# -*- coding: utf-8 -*-
"""
装柜模拟器 — 本地 Web App（含报价单图片识别）
=============================================
双击 exe → 自动打开浏览器 → 上传报价单图片自动识别填表 → 计算装柜方案 → 下载三视图 PNG。
关闭黑色控制台窗口即退出。
"""
from __future__ import annotations
import csv
import base64, io, json, os, re, socket, sys, tempfile, threading, time, zipfile
import urllib.request, urllib.error
import webbrowser
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ConfigDict, ValidationError
import uvicorn

from _packer import SKU, CONTAINERS, PlacedItem, _orientations, smart_pack, recommend_best_container
from _validator import EPS, _support_area, issues_to_dicts, validate_plan

# ── DashScope 配置 ──
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "").strip()
QWEN_MODEL = os.environ.get("QWEN_VL_MODEL", "qwen3.6-plus")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DASHSCOPE_TIMEOUT = 180  # Qwen 处理大图可能要 90s+

MAX_SKUS = 200
MAX_QTY_PER_SKU = 1000
MAX_TOTAL_CARTONS = 2000
MAX_DIM_CM = 1500
MAX_WEIGHT_KG = 30000
MAX_TOTAL_WEIGHT_KG = 1000000
MAX_IMPORT_BYTES = 5_000_000

# 强制 DashScope 直连(绕开 VPN / HTTP_PROXY), 阿里国内 API 不能走代理
_no_proxy_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def _post_dashscope(payload_bytes: bytes) -> dict:
    if not DASHSCOPE_API_KEY:
        raise HTTPException(503, "未配置 DASHSCOPE_API_KEY，图片/文字识别功能已禁用。请配置环境变量后重启。")
    req = urllib.request.Request(DASHSCOPE_URL, data=payload_bytes, headers={
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    })
    t0 = time.time()
    try:
        with _no_proxy_opener.open(req, timeout=DASHSCOPE_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"[Qwen] {QWEN_MODEL} 响应耗时 {time.time()-t0:.1f}s")
        return data
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        raise HTTPException(502, f"Qwen API 错误 {e.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise HTTPException(504, f"Qwen 请求超时/网络错误: {e}")

app = FastAPI(title="装柜模拟器")

# ── 数据模型 ──
class SKUPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    model: str = Field(..., min_length=1, max_length=80)
    name: str = ""
    length: float = Field(..., gt=0, le=MAX_DIM_CM)
    width: float = Field(..., gt=0, le=MAX_DIM_CM)
    height: float = Field(..., gt=0, le=MAX_DIM_CM)
    weight: float = Field(..., gt=0, le=MAX_WEIGHT_KG)
    qty: int = Field(..., gt=0, le=MAX_QTY_PER_SKU)
    upright_only: bool = True
    allow_stack: bool = True
    flat_stack: bool = False
    supplier: str = Field("", max_length=80)
    arrival_order: int = Field(1, ge=1, le=99)
    max_top_load_kg: float = Field(0, ge=0, le=MAX_TOTAL_WEIGHT_KG)

class PackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skus: list[SKUPayload] = Field(..., min_length=1, max_length=MAX_SKUS)
    container_type: str = Field(..., pattern=r"^(20GP|40GP|40HQ|45HQ)$")
    pack_mode: str = Field("auto", pattern=r"^(auto|compact|grouped)$")
    door_reserve_cm: float = Field(0, ge=0, le=600)
    max_segment_weight_kg: float = Field(0, ge=0, le=MAX_TOTAL_WEIGHT_KG)

class ExtractedSKUPayload(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    model: str = Field("", max_length=80)
    length: float = Field(0, ge=0, le=MAX_DIM_CM)
    width: float = Field(0, ge=0, le=MAX_DIM_CM)
    height: float = Field(0, ge=0, le=MAX_DIM_CM)
    weight: float = Field(0, ge=0, le=MAX_WEIGHT_KG)
    qty: int = Field(0, ge=0, le=MAX_QTY_PER_SKU)
    stack_mode: str = Field("full", pattern=r"^(full|flat|none)$")
    upright_only: bool = True
    supplier: str = Field("", max_length=80)
    arrival_order: int = Field(1, ge=1, le=99)
    max_top_load_kg: float = Field(0, ge=0, le=MAX_TOTAL_WEIGHT_KG)
    note: str = Field("", max_length=500)

class PlacementPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku_model: str = Field(..., min_length=1, max_length=80)
    instance_id: int = Field(..., ge=1)
    x: float = Field(..., ge=0)
    y: float = Field(..., ge=0)
    z: float = Field(..., ge=0)
    length: float = Field(..., gt=0, le=MAX_DIM_CM)
    width: float = Field(..., gt=0, le=MAX_DIM_CM)
    height: float = Field(..., gt=0, le=MAX_DIM_CM)
    weight: float = Field(..., gt=0, le=MAX_WEIGHT_KG)
    color: str = Field("#777777", max_length=32)
    rotated: bool = False
    locked: bool = False

class ValidatePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skus: list[SKUPayload] = Field(..., min_length=1, max_length=MAX_SKUS)
    container_type: str = Field(..., pattern=r"^(20GP|40GP|40HQ|45HQ)$")
    placements: list[PlacementPayload] = Field(..., max_length=MAX_TOTAL_CARTONS)
    door_reserve_cm: float = Field(0, ge=0, le=600)
    max_segment_weight_kg: float = Field(0, ge=0, le=MAX_TOTAL_WEIGHT_KG)

class RepackUnlockedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skus: list[SKUPayload] = Field(..., min_length=1, max_length=MAX_SKUS)
    container_type: str = Field(..., pattern=r"^(20GP|40GP|40HQ|45HQ)$")
    locked_placements: list[PlacementPayload] = Field(default_factory=list, max_length=MAX_TOTAL_CARTONS)
    door_reserve_cm: float = Field(0, ge=0, le=600)
    max_segment_weight_kg: float = Field(0, ge=0, le=MAX_TOTAL_WEIGHT_KG)

class ProjectInfoPayload(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    name: str = Field("", max_length=120)
    containerNo: str = Field("", max_length=120)
    revision: str = Field("R1", max_length=40)
    preparedBy: str = Field("", max_length=80)
    reviewedBy: str = Field("", max_length=80)
    confirmedBy: str = Field("", max_length=80)
    note: str = Field("", max_length=500)

class ActivityPayload(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    time: str = Field("", max_length=80)
    action: str = Field("", max_length=80)
    detail: str = Field("", max_length=300)

class ExportWorkbookRequest(ValidatePlanRequest):
    project_info: ProjectInfoPayload = Field(default_factory=ProjectInfoPayload)
    activity_log: list[ActivityPayload] = Field(default_factory=list, max_length=200)
    manual_touched: bool = False

def _to_skus(payload):
    return [SKU(model=p.model, name=p.name or p.model,
                length=p.length, width=p.width, height=p.height,
                weight=p.weight, qty=p.qty,
                upright_only=p.upright_only, allow_stack=p.allow_stack,
                flat_stack=p.flat_stack,
                supplier=p.supplier, arrival_order=p.arrival_order,
                max_top_load_kg=p.max_top_load_kg) for p in payload]

def _ensure_pack_size(skus: list[SKU]):
    total = sum(s.qty for s in skus)
    if total > MAX_TOTAL_CARTONS:
        raise HTTPException(422, f"总箱数 {total} 超过上限 {MAX_TOTAL_CARTONS}，请拆分方案或降低粒度。")

def _normalize_extracted_skus(raw, source_label: str = "Qwen 返回"):
    if not isinstance(raw, list):
        raw = [raw]
    if len(raw) > MAX_SKUS:
        raise HTTPException(422, f"{source_label}包含 {len(raw)} 行，超过上限 {MAX_SKUS}。")
    normalized = []
    try:
        for item in raw:
            normalized.append(ExtractedSKUPayload.model_validate(item).model_dump())
    except ValidationError as e:
        raise HTTPException(422, f"{source_label}的字段格式不符合要求，请重试或手工校对。\n" + str(e))
    return normalized

_IMPORT_HEADER_ALIASES = {
    "model": ("型号", "sku", "model", "货号", "品名", "产品型号", "物料编码", "item", "itemno"),
    "supplier": ("厂家", "供应商", "supplier", "vendor", "factory", "工厂"),
    "arrival_order": ("序", "顺序", "到货序", "order", "arrivalorder"),
    "length": ("长", "长度", "length", "l", "外箱长"),
    "width": ("宽", "宽度", "width", "w", "外箱宽"),
    "height": ("高", "高度", "height", "h", "外箱高"),
    "weight": ("重", "重量", "单重", "单箱重", "weight", "kg", "grossweight", "cartonweight"),
    "max_top_load_kg": ("上压", "上压限重", "承重", "最大上压", "topload", "maxtopload"),
    "qty": ("箱", "箱数", "数量", "总箱数", "qty", "quantity", "cartons", "ctns", "ctn"),
    "stack_mode": ("规则", "堆叠", "堆码", "stack", "stackmode", "堆叠方式"),
    "side_allowed": ("侧放", "可侧放", "side", "sideallowed"),
    "note": ("备注", "note", "说明"),
}

_FULLWIDTH_TRANS = str.maketrans({
    "０": "0", "１": "1", "２": "2", "３": "3", "４": "4",
    "５": "5", "６": "6", "７": "7", "８": "8", "９": "9",
    "．": ".", "，": ",", "（": "(", "）": ")", "：": ":",
})

def _normalize_import_text(value) -> str:
    return str(value or "").strip().translate(_FULLWIDTH_TRANS)

def _import_header_key(value) -> str:
    text = _normalize_import_text(value).lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("厘米", "").replace("公斤", "")
    text = text.replace("cm", "").replace("kg", "")
    return re.sub(r"[\s_\-./\\:：]+", "", text)

def _canonical_import_header(value) -> str | None:
    key = _import_header_key(value)
    if not key:
        return None
    for field, aliases in _IMPORT_HEADER_ALIASES.items():
        if key in {_import_header_key(alias) for alias in aliases}:
            return field
    return None

def _build_import_header_map(row: list[str]) -> dict[str, int]:
    mapping = {}
    for idx, value in enumerate(row):
        field = _canonical_import_header(value)
        if field and field not in mapping:
            mapping[field] = idx
    return mapping

def _find_import_header(rows: list[list[str]]) -> tuple[int, dict[str, int]]:
    required = {"model", "length", "width", "height", "weight", "qty"}
    best_idx, best_map, best_score = -1, {}, -1
    for idx, row in enumerate(rows[:20]):
        mapping = _build_import_header_map(row)
        score = len(required & set(mapping))
        if "model" in mapping and score > best_score:
            best_idx, best_map, best_score = idx, mapping, score
    if best_score >= 4:
        return best_idx, best_map
    raise HTTPException(422, "未识别到清单表头。请至少包含：型号/SKU、长、宽、高、重量、箱数。")

def _parse_import_number(value):
    text = _normalize_import_text(value)
    if not text:
        return None
    text = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))

def _parse_import_qty(value):
    number = _parse_import_number(value)
    if number is None:
        return None
    return int(round(number))

def _parse_import_stack_mode(value) -> str:
    text = _normalize_import_text(value).lower()
    if not text:
        return "full"
    if any(token in text for token in ("flat", "平台", "平", "木箱", "设备")):
        return "flat"
    if any(token in text for token in ("none", "no", "禁", "不可", "不叠", "不能叠", "易碎")):
        return "none"
    return "full"

def _parse_import_side_allowed(value) -> bool:
    text = _normalize_import_text(value).lower()
    if not text:
        return False
    if any(token in text for token in ("否", "不可", "不能", "no", "false", "0")):
        return False
    return any(token in text for token in ("是", "可", "允许", "yes", "true", "1", "side", "侧"))

def _decode_import_text(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(422, "无法识别清单文件编码，请另存为 UTF-8 CSV 后再导入。")

def _read_import_csv_rows(content: bytes) -> list[list[str]]:
    text = _decode_import_text(content)
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;，")
    except csv.Error:
        dialect = csv.excel_tab if sample.count("\t") > sample.count(",") else csv.excel
    return [[_normalize_import_text(cell) for cell in row] for row in csv.reader(io.StringIO(text), dialect)]

def _xlsx_col_number(ref: str) -> int:
    letters = "".join(ch for ch in str(ref or "") if ch.isalpha()).upper()
    result = 0
    for ch in letters:
        result = result * 26 + ord(ch) - 64
    return result

def _read_import_xlsx_rows(content: bytes) -> list[list[str]]:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = set(zf.namelist())
            sheet_names = sorted(name for name in names if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
            if not sheet_names:
                raise HTTPException(422, "未在 Excel 文件中找到工作表。")
            ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
            shared = []
            if "xl/sharedStrings.xml" in names:
                root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
                for item in root.findall(f".//{ns}si"):
                    shared.append("".join(t.text or "" for t in item.findall(f".//{ns}t")))
            root = ET.fromstring(zf.read(sheet_names[0]))
    except zipfile.BadZipFile:
        raise HTTPException(422, "Excel 文件无法打开，请确认是 .xlsx 格式。")
    rows = []
    for row in root.findall(f".//{ns}sheetData/{ns}row"):
        cells = []
        for cell in row.findall(f"{ns}c"):
            col = _xlsx_col_number(cell.attrib.get("r")) or len(cells) + 1
            while len(cells) < col:
                cells.append("")
            cell_type = cell.attrib.get("t", "")
            if cell_type == "inlineStr":
                value = "".join(t.text or "" for t in cell.findall(f".//{ns}t"))
            else:
                node = cell.find(f"{ns}v")
                value = node.text if node is not None and node.text is not None else ""
                if cell_type == "s" and value:
                    idx = int(float(value))
                    value = shared[idx] if 0 <= idx < len(shared) else ""
            cells[col - 1] = _normalize_import_text(value)
        if any(cells):
            rows.append(cells)
    return rows

def _parse_manifest_rows(rows: list[list[str]], source: str) -> dict:
    rows = [row for row in rows if any(str(cell).strip() for cell in row)]
    if not rows:
        raise HTTPException(422, "清单文件为空。")
    header_idx, mapping = _find_import_header(rows)
    required = ("model", "length", "width", "height", "weight", "qty")
    issues = []
    parsed = []

    def cell(row, field):
        idx = mapping.get(field)
        if idx is None or idx >= len(row):
            return ""
        return row[idx]

    for row_no, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
        if not any(str(cell_value).strip() for cell_value in row):
            continue
        first_text = "".join(str(cell_value) for cell_value in row[:2])
        if any(token in first_text for token in ("合计", "总计", "total", "Total")):
            continue
        missing = [field for field in required if not cell(row, field)]
        if missing:
            issues.append({"row": row_no, "severity": "error", "message": "缺少必填字段：" + "、".join(missing)})
            continue
        numbers = {field: _parse_import_number(cell(row, field)) for field in ("length", "width", "height", "weight")}
        qty = _parse_import_qty(cell(row, "qty"))
        invalid = [field for field, value in numbers.items() if value is None or value <= 0]
        if qty is None or qty <= 0:
            invalid.append("qty")
        if invalid:
            issues.append({"row": row_no, "severity": "error", "message": "数字格式无效：" + "、".join(invalid)})
            continue
        arrival_order = _parse_import_qty(cell(row, "arrival_order")) or 1
        stack_mode = _parse_import_stack_mode(cell(row, "stack_mode"))
        side_allowed = _parse_import_side_allowed(cell(row, "side_allowed")) or _parse_import_side_allowed(cell(row, "stack_mode"))
        raw_item = {
            "model": cell(row, "model"),
            "length": numbers["length"],
            "width": numbers["width"],
            "height": numbers["height"],
            "weight": numbers["weight"],
            "qty": qty,
            "stack_mode": stack_mode,
            "upright_only": not side_allowed,
            "supplier": cell(row, "supplier"),
            "arrival_order": max(1, min(99, arrival_order)),
            "max_top_load_kg": _parse_import_number(cell(row, "max_top_load_kg")) or 0,
            "note": cell(row, "note"),
        }
        try:
            parsed.append(ExtractedSKUPayload.model_validate(raw_item).model_dump())
        except ValidationError as e:
            issues.append({"row": row_no, "severity": "error", "message": "字段超出允许范围：" + str(e).splitlines()[0]})
    if len(parsed) > MAX_SKUS:
        raise HTTPException(422, f"清单有效行 {len(parsed)} 超过上限 {MAX_SKUS}，请拆分导入。")
    duplicates = [model for model, count in Counter(item["model"] for item in parsed).items() if count > 1]
    for model in duplicates[:10]:
        issues.append({"row": 0, "severity": "warning", "message": f"型号 {model} 出现多行，系统会按多行 SKU 追加，请确认是否需要合并。"})
    return {
        "skus": parsed,
        "issues": issues,
        "summary": {
            "source": source,
            "total_rows": max(0, len(rows) - header_idx - 1),
            "imported_rows": len(parsed),
            "error_count": sum(1 for item in issues if item["severity"] == "error"),
            "warning_count": sum(1 for item in issues if item["severity"] == "warning"),
        },
    }

def _parse_manifest_file_bytes(filename: str, content: bytes) -> dict:
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(413, "清单文件太大，请控制在 5MB 以内。")
    lower = (filename or "").lower()
    if lower.endswith(".xlsx") or content[:2] == b"PK":
        rows = _read_import_xlsx_rows(content)
    elif lower.endswith(".xls"):
        raise HTTPException(422, "暂不支持旧版 .xls，请另存为 .xlsx 或 CSV 后导入。")
    else:
        rows = _read_import_csv_rows(content)
    return _parse_manifest_rows(rows, filename or "清单文件")

def _manifest_template_rows() -> list[tuple[str, list[list]]]:
    headers = ["型号", "厂家", "序", "长(cm)", "宽(cm)", "高(cm)", "重(kg)", "上压(kg)", "箱数", "规则", "侧放", "备注"]
    cargo = [headers]
    cargo.extend([["", "", "", "", "", "", "", "", "", "", "", ""] for _ in range(20)])
    help_rows = [
        ["字段", "是否必填", "填写示例", "说明"],
        ["型号", "是", "SKU-A", "货号、型号或品名，不能留空。"],
        ["厂家", "否", "供应商A", "用于按供应商高亮和交接。"],
        ["序", "否", "1", "到货或装柜优先顺序，默认 1。"],
        ["长(cm)", "是", "120", "外箱长度，单位 cm；如果原表是 mm 请除以 10。"],
        ["宽(cm)", "是", "80", "外箱宽度，单位 cm。"],
        ["高(cm)", "是", "60", "外箱高度，单位 cm。"],
        ["重(kg)", "是", "25", "单箱重量，单位 kg，不是总重量。"],
        ["上压(kg)", "否", "120", "该 SKU 单箱最多承受的上方累计重量；0 或留空表示不限制。"],
        ["箱数", "是", "10", "总箱数 cartons，不是每箱件数。"],
        ["规则", "否", "叠 / 平 / 禁", "叠=普通可叠；平=自身单层但顶部可作平台；禁=不可堆叠。"],
        ["侧放", "否", "是 / 否", "是否允许旋转侧放；默认否。"],
        ["备注", "否", "60x25=1500kg", "写单位换算、总重反推或人工确认依据。"],
    ]
    examples = [
        headers,
        ["SKU-A", "供应商A", 1, 120, 80, 60, 25, 120, 10, "叠", "是", "规则纸箱，可侧放"],
        ["SKU-B", "供应商B", 2, 160, 90, 75, 80, 0, 4, "平", "否", "木箱设备，顶部可加垫板"],
        ["SKU-C", "供应商C", 3, 60, 50, 45, 12, 0, 20, "禁", "否", "易碎件，不可堆叠"],
    ]
    return [("货物清单", cargo), ("字段说明", help_rows), ("填写示例", examples)]

def _render_loading_plan(*args, **kwargs):
    try:
        from _visualizer import render_loading_plan
    except ModuleNotFoundError as e:
        raise HTTPException(500, f"缺少渲染依赖: {e.name}。请先安装 requirements.txt。")
    return render_loading_plan(*args, **kwargs)

def _placements_from_payload(payload: list[PlacementPayload]) -> list[PlacedItem]:
    return [PlacedItem(**p.model_dump(exclude={"locked"})) for p in payload]

def _unfitted_from_placements(skus: list[SKU], placed: list[PlacedItem]) -> list[tuple[str, int]]:
    placed_counts = Counter(p.sku_model for p in placed)
    result = []
    for sku in skus:
        missing = max(0, sku.qty - placed_counts.get(sku.model, 0))
        if missing:
            result.append((sku.model, missing))
    return result

def _weight_segments(placed: list[PlacedItem], spec: dict, segment_count: int = 6) -> list[dict]:
    L = spec["L"]
    if segment_count <= 0 or L <= EPS:
        return []
    segment_len = L / segment_count
    weights = [0.0 for _ in range(segment_count)]
    for p in placed:
        center = p.x + p.length / 2
        idx = int(center / segment_len) if segment_len > EPS else 0
        idx = max(0, min(segment_count - 1, idx))
        weights[idx] += p.weight
    return [
        {
            "from_cm": round(i * segment_len, 1),
            "to_cm": round((i + 1) * segment_len, 1),
            "weight_kg": round(weight, 0),
        }
        for i, weight in enumerate(weights)
    ]

def _stats_for_plan(
    skus: list[SKU],
    placed: list[PlacedItem],
    unfitted: list[tuple[str, int]],
    spec: dict,
    container_type: str,
    pack_mode_requested: str,
    pack_mode_used: str,
    door_reserve_cm: float = 0,
    max_segment_weight_kg: float = 0,
) -> dict:
    door_reserve_cm = max(0.0, float(door_reserve_cm or 0))
    usable_l = max(0.0, spec["L"] - door_reserve_cm)
    cbm_cap = spec["L"] * spec["W"] * spec["H"] / 1e6
    cbm_usable_cap = usable_l * spec["W"] * spec["H"] / 1e6
    cbm_used = sum(p.length * p.width * p.height for p in placed) / 1e6
    w_total = sum(p.weight for p in placed)
    center_x = sum((p.x + p.length / 2) * p.weight for p in placed) / w_total if w_total else 0
    center_y = sum((p.y + p.width / 2) * p.weight for p in placed) / w_total if w_total else 0
    front_weight = sum(p.weight for p in placed if p.x + p.length / 2 <= spec["L"] / 2)
    rear_weight = w_total - front_weight
    left_weight = sum(p.weight for p in placed if p.y + p.width / 2 <= spec["W"] / 2)
    right_weight = w_total - left_weight
    weight_segments = _weight_segments(placed, spec)
    max_segment_weight = max((s["weight_kg"] for s in weight_segments), default=0)
    max_segment_weight_kg = max(0.0, float(max_segment_weight_kg or 0))
    return {
        "container_name": spec["name"],
        "container_type": container_type,
        "door_reserve_cm": round(door_reserve_cm, 1),
        "usable_length_cm": round(usable_l, 1),
        "placed_count": len(placed),
        "total_count": sum(s.qty for s in skus),
        "unfitted": [{"model": m, "count": c} for m, c in unfitted],
        "cbm_used": round(cbm_used, 2),
        "cbm_capacity": round(cbm_cap, 2),
        "cbm_usable_capacity": round(cbm_usable_cap, 2),
        "cbm_util_pct": round(cbm_used / cbm_cap * 100, 1) if cbm_cap else 0,
        "cbm_usable_util_pct": round(cbm_used / cbm_usable_cap * 100, 1) if cbm_usable_cap else 0,
        "weight_total_kg": round(w_total, 0),
        "weight_max_kg": spec["max_kg"],
        "weight_util_pct": round(w_total / spec["max_kg"] * 100, 1) if spec["max_kg"] else 0,
        "center_x_cm": round(center_x, 1),
        "center_x_pct": round(center_x / spec["L"] * 100, 1) if spec["L"] else 0,
        "center_y_cm": round(center_y, 1),
        "center_y_pct": round(center_y / spec["W"] * 100, 1) if spec["W"] else 0,
        "front_weight_kg": round(front_weight, 0),
        "rear_weight_kg": round(rear_weight, 0),
        "left_weight_kg": round(left_weight, 0),
        "right_weight_kg": round(right_weight, 0),
        "weight_segments": weight_segments,
        "max_segment_weight_kg": max_segment_weight,
        "max_segment_limit_kg": round(max_segment_weight_kg, 0),
        "pack_mode_requested": pack_mode_requested,
        "pack_mode_used": pack_mode_used,
    }

def _archive_missing(info: ProjectInfoPayload) -> list[str]:
    fields = [
        ("方案名", info.name),
        ("柜号/车号", info.containerNo),
        ("方案版本", info.revision),
        ("制单人", info.preparedBy),
        ("复核人", info.reviewedBy),
        ("现场确认人", info.confirmedBy),
    ]
    return [label for label, value in fields if not str(value or "").strip()]

def _safety_summary_for_export(
    stats: dict,
    validation: list[dict],
    placed: list[PlacedItem],
    info: ProjectInfoPayload,
    manual_touched: bool,
    locked_count: int = 0,
) -> dict:
    errors = sum(1 for item in validation if item.get("severity") == "error")
    warnings = sum(1 for item in validation if item.get("severity") == "warning")
    missing = sum(item.get("count", 0) for item in stats.get("unfitted", []))
    if not placed:
        return {"label": "待生成", "detail": "先生成装柜方案，再进入安全复核。", "reasons": ["尚未生成装柜初稿"]}
    blockers = []
    if errors:
        blockers.append(f"{errors} 个错误未处理")
    if missing:
        blockers.append(f"{missing} 箱未放入方案")
    if blockers:
        return {"label": "不可交付", "detail": "；".join(blockers), "reasons": blockers}
    reviews = []
    if warnings:
        reviews.append(f"{warnings} 个警告需复核")
    if not manual_touched and not locked_count:
        reviews.append("尚未人工复核或锁定关键区域")
    archive_missing = _archive_missing(info)
    if archive_missing:
        reviews.append("归档信息缺少：" + "、".join(archive_missing))
    if reviews:
        return {"label": "需复核", "detail": "；".join(reviews), "reasons": reviews}
    return {
        "label": "可交付",
        "detail": "清单已完整入柜，规则校验通过，归档信息齐全。",
        "reasons": ["清单已完整入柜", "规则校验通过", "归档信息齐全"],
    }

def _xlsx_col(col: int) -> str:
    label = ""
    while col:
        col, rem = divmod(col - 1, 26)
        label = chr(65 + rem) + label
    return label or "A"

def _xlsx_cell(row: int, col: int, value, style: int | None = None) -> str:
    ref = f"{_xlsx_col(col)}{row}"
    style_attr = f' s="{style}"' if style is not None else ""
    if value is None:
        return f'<c r="{ref}"{style_attr}/>'
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"{style_attr}><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"{style_attr}><v>{value}</v></c>'
    text = xml_escape(str(value))
    return f'<c r="{ref}" t="inlineStr"{style_attr}><is><t>{text}</t></is></c>'

def _sheet_xml(rows: list[list], freeze_header: bool = True) -> str:
    row_count = max(1, len(rows))
    col_count = max(1, max((len(r) for r in rows), default=1))
    col_widths = []
    for idx in range(col_count):
        width = 10
        for row in rows:
            if idx < len(row):
                width = max(width, min(42, int(len(str(row[idx])) * 1.15) + 3))
        col_widths.append(width)
    cols = "".join(
        f'<col min="{i+1}" max="{i+1}" width="{width}" customWidth="1"/>'
        for i, width in enumerate(col_widths)
    )
    sheet_views = ""
    if freeze_header and len(rows) > 1:
        sheet_views = (
            '<sheetViews><sheetView workbookViewId="0">'
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
            '</sheetView></sheetViews>'
        )
    sheet_rows = []
    for r_idx, row in enumerate(rows, start=1):
        cells = "".join(
            _xlsx_cell(r_idx, c_idx, value, 1 if r_idx == 1 else None)
            for c_idx, value in enumerate(row, start=1)
        )
        sheet_rows.append(f'<row r="{r_idx}">{cells}</row>')
    dimension = f"A1:{_xlsx_col(col_count)}{row_count}"
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="{dimension}"/>{sheet_views}<cols>{cols}</cols>'
        f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        '</worksheet>'
    )

def _build_xlsx(sheets: list[tuple[str, list[list]]]) -> bytes:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    safe_sheets = []
    used_names = set()
    for idx, (name, rows) in enumerate(sheets, start=1):
        clean = re.sub(r"[\[\]\:\*\?\/\\]", " ", str(name)).strip()[:31] or f"Sheet{idx}"
        base, suffix = clean, 1
        while clean in used_names:
            tail = f" {suffix}"
            clean = (base[:31-len(tail)] + tail).strip()
            suffix += 1
        used_names.add(clean)
        safe_sheets.append((clean, rows))

    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    for idx in range(1, len(safe_sheets) + 1):
        content_types.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    content_types.append("</Types>")

    workbook_sheets = "".join(
        f'<sheet name="{xml_escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, (name, _) in enumerate(safe_sheets, start=1)
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{workbook_sheets}</sheets></workbook>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )
    workbook_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for idx in range(1, len(safe_sheets) + 1):
        workbook_rels.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        )
    workbook_rels.append(
        f'<Relationship Id="rId{len(safe_sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    workbook_rels.append("</Relationships>")
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )
    app_props = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>Container Pack App</Application></Properties>'
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:creator>Container Pack App</dc:creator>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>'
        '</cp:coreProperties>'
    )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "".join(content_types))
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", "".join(workbook_rels))
        zf.writestr("xl/styles.xml", styles)
        zf.writestr("docProps/app.xml", app_props)
        zf.writestr("docProps/core.xml", core)
        for idx, (_, rows) in enumerate(safe_sheets, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", _sheet_xml(rows))
    return output.getvalue()

def _workbook_rows(
    req: ExportWorkbookRequest,
    skus: list[SKU],
    placed: list[PlacedItem],
    validation: list[dict],
    stats: dict,
    safety: dict,
) -> list[tuple[str, list[list]]]:
    info = req.project_info
    locked_by_key = {(p.sku_model, p.instance_id): p.locked for p in req.placements}
    summary = [
        ["字段", "值"],
        ["安全结论", safety["label"]],
        ["结论说明", safety["detail"]],
        ["方案名", info.name],
        ["方案版本", info.revision],
        ["柜号/车号", info.containerNo],
        ["制单人", info.preparedBy],
        ["复核人", info.reviewedBy],
        ["现场确认人", info.confirmedBy],
        ["备注", info.note],
        ["柜型", req.container_type],
        ["柜型名称", stats.get("container_name", "")],
        ["箱数", f"{stats.get('placed_count', 0)} / {stats.get('total_count', 0)}"],
        ["未放箱数", sum(item.get("count", 0) for item in stats.get("unfitted", []))],
        ["空间利用率(%)", stats.get("cbm_util_pct", 0)],
        ["总体积(m³)", stats.get("cbm_used", 0)],
        ["总重量(kg)", stats.get("weight_total_kg", 0)],
        ["限重(kg)", stats.get("weight_max_kg", 0)],
        ["重心X(cm)", stats.get("center_x_cm", 0)],
        ["重心Y(cm)", stats.get("center_y_cm", 0)],
        ["前/后重量(kg)", f"{stats.get('front_weight_kg', 0)} / {stats.get('rear_weight_kg', 0)}"],
        ["左/右重量(kg)", f"{stats.get('left_weight_kg', 0)} / {stats.get('right_weight_kg', 0)}"],
        ["门口预留(cm)", stats.get("door_reserve_cm", 0)],
        ["分段限重(kg)", stats.get("max_segment_limit_kg", 0)],
    ]
    summary.extend([["复核要点", reason] for reason in safety.get("reasons", [])])

    cargo = [["SKU", "名称", "厂家", "到货序", "长(cm)", "宽(cm)", "高(cm)", "单箱重(kg)", "上压限重(kg)", "箱数", "规则"]]
    for sku in skus:
        if sku.flat_stack:
            rule = "顶部平台"
        elif sku.allow_stack:
            rule = "可堆叠"
        else:
            rule = "不可堆叠"
        cargo.append([
            sku.model, sku.name, sku.supplier, sku.arrival_order,
            sku.length, sku.width, sku.height, sku.weight,
            sku.max_top_load_kg, sku.qty, rule,
        ])

    placements = [["顺序", "SKU", "箱号", "X(cm)", "Y(cm)", "Z(cm)", "长(cm)", "宽(cm)", "高(cm)", "重量(kg)", "旋转", "锁定"]]
    for idx, p in enumerate(placed, start=1):
        placements.append([
            idx, p.sku_model, p.instance_id, p.x, p.y, p.z,
            p.length, p.width, p.height, p.weight,
            "是" if p.rotated else "否",
            "是" if locked_by_key.get((p.sku_model, p.instance_id), False) else "否",
        ])

    issues = [["级别", "代码", "对象", "箱号", "说明"]]
    for item in validation:
        issues.append([
            item.get("severity", ""),
            item.get("code", ""),
            item.get("item", ""),
            item.get("instance_id", ""),
            item.get("message", ""),
        ])
    if len(issues) == 1:
        issues.append(["", "", "", "", "无"])

    segments = [["段", "X起点(cm)", "X终点(cm)", "重量(kg)", "限重(kg)"]]
    for idx, seg in enumerate(stats.get("weight_segments", []), start=1):
        segments.append([
            idx,
            seg.get("from_cm", 0),
            seg.get("to_cm", 0),
            seg.get("weight_kg", 0),
            stats.get("max_segment_limit_kg", 0),
        ])

    activity = [["时间", "动作", "说明"]]
    for item in req.activity_log[-200:]:
        activity.append([item.time, item.action, item.detail])
    if len(activity) == 1:
        activity.append(["", "", "无"])

    unfitted = [["SKU", "未放箱数"]]
    for item in stats.get("unfitted", []):
        unfitted.append([item.get("model", ""), item.get("count", 0)])
    if len(unfitted) == 1:
        unfitted.append(["", 0])

    return [
        ("摘要", summary),
        ("货物清单", cargo),
        ("装柜坐标", placements),
        ("校验问题", issues),
        ("分段重量", segments),
        ("未放货物", unfitted),
        ("操作记录", activity),
    ]

def _packing_spec(spec: dict, door_reserve_cm: float) -> dict:
    packing_spec = dict(spec)
    reserve = max(0.0, float(door_reserve_cm or 0))
    packing_spec["L"] = max(0.0, spec["L"] - reserve)
    return packing_spec

def _copy_sku_with_qty(sku: SKU, qty: int) -> SKU:
    return SKU(
        model=sku.model,
        name=sku.name,
        length=sku.length,
        width=sku.width,
        height=sku.height,
        weight=sku.weight,
        qty=qty,
        upright_only=sku.upright_only,
        allow_stack=sku.allow_stack,
        flat_stack=sku.flat_stack,
        supplier=sku.supplier,
        arrival_order=sku.arrival_order,
        max_top_load_kg=sku.max_top_load_kg,
    )

def _overlaps(a: PlacedItem, b: PlacedItem) -> bool:
    return (
        a.x < b.x + b.length - EPS and b.x < a.x + a.length - EPS
        and a.y < b.y + b.width - EPS and b.y < a.y + a.width - EPS
        and a.z < b.z + b.height - EPS and b.z < a.z + a.height - EPS
    )

def _can_place_candidate(
    candidate: PlacedItem,
    placed: list[PlacedItem],
    skus_by_model: dict[str, SKU],
    spec: dict,
    total_weight: float,
) -> bool:
    if total_weight + candidate.weight > spec["max_kg"] + EPS:
        return False
    if (
        candidate.x < -EPS or candidate.y < -EPS or candidate.z < -EPS
        or candidate.x + candidate.length > spec["L"] + EPS
        or candidate.y + candidate.width > spec["W"] + EPS
        or candidate.z + candidate.height > spec["H"] + EPS
    ):
        return False
    if any(_overlaps(candidate, p) for p in placed):
        return False

    sku = skus_by_model[candidate.sku_model]
    if (sku.flat_stack or not sku.allow_stack) and candidate.z > EPS:
        return False
    if candidate.z > EPS:
        footprint = candidate.length * candidate.width
        if _support_area(candidate, placed) + EPS < footprint:
            return False
        for lower in placed:
            if abs(lower.z + lower.height - candidate.z) > EPS:
                continue
            x_overlap = max(0, min(candidate.x + candidate.length, lower.x + lower.length) - max(candidate.x, lower.x))
            y_overlap = max(0, min(candidate.y + candidate.width, lower.y + lower.width) - max(candidate.y, lower.y))
            if x_overlap * y_overlap <= EPS:
                continue
            lower_sku = skus_by_model.get(lower.sku_model)
            if lower_sku and not lower_sku.allow_stack and not lower_sku.flat_stack:
                return False
    top_load_issues = validate_plan(
        placed + [candidate],
        list(skus_by_model.values()),
        spec,
        check_collisions=False,
    )
    if any(issue.code == "top_load_exceeded" for issue in top_load_issues):
        return False
    return True

def _candidate_points(placed: list[PlacedItem], spec: dict, dl: float, dw: float, dh: float):
    xs = {0.0}
    ys = {0.0}
    points = {(0.0, 0.0, 0.0)}
    for p in placed:
        xs.update({p.x, p.x + p.length, p.x - dl, p.x + p.length - dl})
        ys.update({p.y, p.y + p.width, p.y - dw, p.y + p.width - dw})
        z = p.z + p.height
        for x in (p.x, p.x + p.length - dl, p.x + p.length):
            for y in (p.y, p.y + p.width - dw, p.y + p.width):
                points.add((x, y, z))

    floor_product = len(xs) * len(ys)
    if floor_product <= 8000:
        for x in xs:
            for y in ys:
                points.add((x, y, 0.0))
    else:
        for p in placed:
            points.update({
                (p.x + p.length, p.y, 0.0),
                (p.x, p.y + p.width, 0.0),
                (p.x + p.length, p.y + p.width, 0.0),
            })

    filtered = []
    for x, y, z in points:
        if x >= -EPS and y >= -EPS and z >= -EPS and x + dl <= spec["L"] + EPS and y + dw <= spec["W"] + EPS and z + dh <= spec["H"] + EPS:
            filtered.append((max(0.0, x), max(0.0, y), max(0.0, z)))
    return sorted(set(filtered), key=lambda p: (p[2], p[0], p[1]))

def _find_repack_position(
    sku: SKU,
    instance_id: int,
    placed: list[PlacedItem],
    spec: dict,
    skus_by_model: dict[str, SKU],
    total_weight: float,
    color: str,
) -> PlacedItem | None:
    for dl, dw, dh, rotated in _orientations(sku.length, sku.width, sku.height, sku.upright_only):
        for x, y, z in _candidate_points(placed, spec, dl, dw, dh):
            candidate = PlacedItem(sku.model, instance_id, x, y, z, dl, dw, dh, sku.weight, color, rotated)
            if _can_place_candidate(candidate, placed, skus_by_model, spec, total_weight):
                return candidate
    return None

def _repack_unlocked_plan(skus: list[SKU], spec: dict, locked: list[PlacedItem]):
    palette = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6",
               "#1ABC9C", "#E67E22", "#34495E", "#16A085", "#D35400"]
    color_map = {s.model: palette[i % len(palette)] for i, s in enumerate(skus)}
    for p in locked:
        color_map[p.sku_model] = p.color or color_map.get(p.sku_model, "#777777")

    skus_by_model = {s.model: s for s in skus}
    locked_counts = Counter(p.sku_model for p in locked)
    instance_counters = Counter()
    for p in locked:
        instance_counters[p.sku_model] = max(instance_counters[p.sku_model], p.instance_id)

    remaining = []
    for sku in skus:
        qty = max(0, sku.qty - locked_counts.get(sku.model, 0))
        if qty:
            remaining.append(_copy_sku_with_qty(sku, qty))

    remaining.sort(key=lambda s: (0 if s.flat_stack else 1, -(s.length * s.width * s.height), s.model))
    placed = list(locked)
    total_weight = sum(p.weight for p in placed)
    unfitted = []

    for sku in remaining:
        count = 0
        for _ in range(sku.qty):
            instance_counters[sku.model] += 1
            candidate = _find_repack_position(
                sku,
                instance_counters[sku.model],
                placed,
                spec,
                skus_by_model,
                total_weight,
                color_map.get(sku.model, "#777777"),
            )
            if candidate is None:
                instance_counters[sku.model] -= 1
                break
            placed.append(candidate)
            total_weight += candidate.weight
            count += 1
        if count < sku.qty:
            unfitted.append((sku.model, sku.qty - count))

    return placed, unfitted

# ── 装柜计算 ──
@app.get("/", response_class=HTMLResponse)
def index():
    from _frontend import INDEX_HTML as html
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")

@app.post("/api/pack")
def api_pack(req: PackRequest):
    skus = _to_skus(req.skus)
    _ensure_pack_size(skus)
    spec = CONTAINERS[req.container_type]
    packing_spec = _packing_spec(spec, req.door_reserve_cm)
    # 确定实际使用的模式 (auto 会根据利用率自动切换)
    actual_mode = req.pack_mode
    if req.pack_mode == "auto":
        # 预跑 compact 看利用率, 决定用哪个
        pre_placed, pre_unfitted = smart_pack(skus, packing_spec, pack_mode="compact")
        cbm_cap = packing_spec["L"] * packing_spec["W"] * packing_spec["H"]
        cbm_used = sum(p.length * p.width * p.height for p in pre_placed)
        util = cbm_used / cbm_cap if cbm_cap > 0 else 0
        suppliers = {(s.supplier or "") for s in skus}
        suppliers.discard("")
        if len(suppliers) >= 2 and util < 0.75 and not pre_unfitted:
            actual_mode = "grouped"
            placed, unfitted = smart_pack(skus, packing_spec, pack_mode="grouped")
        else:
            actual_mode = "compact"
            placed, unfitted = pre_placed, pre_unfitted
    else:
        placed, unfitted = smart_pack(skus, packing_spec, pack_mode=req.pack_mode)
    png_bytes = b""
    render_error = None
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False); tmp.close()
    try:
        try:
            _render_loading_plan(placed, unfitted, spec, tmp.name,
                                 title=f"{spec['name']} ({req.container_type}) 装柜方案")
            png_bytes = Path(tmp.name).read_bytes()
        except HTTPException as e:
            render_error = e.detail
    finally:
        try: os.unlink(tmp.name)
        except OSError: pass
    validation = issues_to_dicts(validate_plan(
        placed,
        skus,
        spec,
        door_reserve_cm=req.door_reserve_cm,
        max_segment_weight_kg=req.max_segment_weight_kg,
    ))
    return {
        "png_base64": base64.b64encode(png_bytes).decode(),
        "render_error": render_error,
        "placements": [p.to_dict() for p in placed],
        "validation": validation,
        "stats": _stats_for_plan(
            skus, placed, unfitted, spec, req.container_type,
            req.pack_mode, actual_mode, req.door_reserve_cm, req.max_segment_weight_kg
        ),
    }

@app.post("/api/validate_plan")
def api_validate_plan(req: ValidatePlanRequest):
    skus = _to_skus(req.skus)
    _ensure_pack_size(skus)
    spec = CONTAINERS[req.container_type]
    placed = _placements_from_payload(req.placements)
    return {"validation": issues_to_dicts(validate_plan(
        placed,
        skus,
        spec,
        door_reserve_cm=req.door_reserve_cm,
        max_segment_weight_kg=req.max_segment_weight_kg,
    ))}

@app.post("/api/render_plan")
def api_render_plan(req: ValidatePlanRequest):
    skus = _to_skus(req.skus)
    _ensure_pack_size(skus)
    spec = CONTAINERS[req.container_type]
    placed = _placements_from_payload(req.placements)
    unfitted = _unfitted_from_placements(skus, placed)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False); tmp.close()
    try:
        _render_loading_plan(placed, unfitted, spec, tmp.name,
                             title=f"{spec['name']} ({req.container_type}) 人工调整方案")
        png_bytes = Path(tmp.name).read_bytes()
    finally:
        try: os.unlink(tmp.name)
        except OSError: pass
    return {
        "png_base64": base64.b64encode(png_bytes).decode(),
        "validation": issues_to_dicts(validate_plan(
            placed,
            skus,
            spec,
            door_reserve_cm=req.door_reserve_cm,
            max_segment_weight_kg=req.max_segment_weight_kg,
        )),
        "stats": _stats_for_plan(
            skus, placed, unfitted, spec, req.container_type,
            "manual", "manual", req.door_reserve_cm, req.max_segment_weight_kg
        ),
    }

@app.post("/api/export_workbook")
def api_export_workbook(req: ExportWorkbookRequest):
    skus = _to_skus(req.skus)
    _ensure_pack_size(skus)
    spec = CONTAINERS[req.container_type]
    placed = _placements_from_payload(req.placements)
    unfitted = _unfitted_from_placements(skus, placed)
    validation = issues_to_dicts(validate_plan(
        placed,
        skus,
        spec,
        door_reserve_cm=req.door_reserve_cm,
        max_segment_weight_kg=req.max_segment_weight_kg,
    ))
    stats = _stats_for_plan(
        skus, placed, unfitted, spec, req.container_type,
        "manual", "manual", req.door_reserve_cm, req.max_segment_weight_kg
    )
    locked_count = sum(1 for p in req.placements if p.locked)
    safety = _safety_summary_for_export(stats, validation, placed, req.project_info, req.manual_touched, locked_count)
    workbook = _build_xlsx(_workbook_rows(req, skus, placed, validation, stats, safety))
    safe_name = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", req.project_info.name or req.container_type).strip("_")
    filename = f"装柜工作簿_{safe_name or req.container_type}_{time.strftime('%Y%m%d_%H%M')}.xlsx"
    return {
        "xlsx_base64": base64.b64encode(workbook).decode(),
        "filename": filename,
        "validation": validation,
        "stats": stats,
        "safety": safety,
    }

@app.post("/api/repack_unlocked")
def api_repack_unlocked(req: RepackUnlockedRequest):
    skus = _to_skus(req.skus)
    _ensure_pack_size(skus)
    spec = CONTAINERS[req.container_type]
    packing_spec = _packing_spec(spec, req.door_reserve_cm)
    locked = _placements_from_payload(req.locked_placements)
    placed, unfitted = _repack_unlocked_plan(skus, packing_spec, locked)
    validation = issues_to_dicts(validate_plan(
        placed,
        skus,
        spec,
        door_reserve_cm=req.door_reserve_cm,
        max_segment_weight_kg=req.max_segment_weight_kg,
    ))
    locked_ids = {(p.sku_model, p.instance_id) for p in locked}
    placements = []
    for p in placed:
        d = p.to_dict()
        d["locked"] = (p.sku_model, p.instance_id) in locked_ids
        placements.append(d)
    return {
        "placements": placements,
        "validation": validation,
        "stats": _stats_for_plan(
            skus, placed, unfitted, spec, req.container_type,
            "partial", "partial", req.door_reserve_cm, req.max_segment_weight_kg
        ),
    }

# ── 图片识别（qwen3.6-plus）──
EXTRACT_PROMPT = """你是装柜助手。请从这张 packing list / 报价单图片中提取所有货物信息。

【关键: 中文报价单列名歧义处理】
包装单列名经常不规范, 常见陷阱:
- "装箱量" 通常指"每箱装 N 件", 不是箱数本身
- "件数" 经常指"箱数"(cartons), 不是 pieces
- "总数量" 通常指 pieces 总数 = 箱数 × 每箱件数
- "箱数" 才明确指 cartons
- "重量" 一般是单箱重(kg/carton), 但可能是单件重
- "总重量" 是所有箱子加起来的总重

你必须用算术做交叉验证(这是唯一可靠的判断方式):
- 必须满足: qty(箱数) × weight(单箱重) ≈ 总重量
- 如果图上只有 "总重量" 和 "重量" 两列, 可以反推: qty = 总重量 / 重量
- 如果图上有多个可能的"箱数"列, 优先选使算术成立的那个
- 在 note 里写清楚你的判断依据, 比如 "依据总重 1920 / 单箱重 32 推得 60 箱"

返回严格 JSON 数组(不要 markdown 代码块), 每个对象:
- model: string, 型号/货号/品名
- length: number, 外箱长(cm)
- width: number, 外箱宽(cm)
- height: number, 外箱高(cm)
- weight: number, 单箱重量(kg)
- qty: number, 总箱数 (cartons 数, 不是 pieces 数)
- stack_mode: string, 堆叠方式: "full"=普通可堆叠纸箱 / "flat"=机械设备或木箱(自己只能单层但顶部可加垫板再叠其他货) / "none"=易碎或精密不可叠
- upright_only: boolean, 必须直立(精密/医疗=true, 规则纸箱=false)
- supplier: string, 厂家/供应商名 (如图中有标注则提取, 没有则填空字符串)
- note: string, **必填**: 写你的推理依据(单位转换/算术验证/歧义判断), 例如 "60×32=1920 kg 验证通过" 或 "单重由总重 1920/箱数 60 推得 32kg"; 完全确定无歧义时可留空

规则:
1. 单位统一 cm/kg, 图上 m 要乘100, mm 要除10
2. 无法判断的字段填0, note里说明
3. 跳过表头/合计/说明行
4. 严禁编造数据

只输出 JSON 数组。"""

@app.post("/api/import_manifest")
async def api_import_manifest(file: UploadFile = File(...)):
    content = await file.read()
    return _parse_manifest_file_bytes(file.filename or "", content)

@app.get("/api/import_template")
def api_import_template():
    workbook = _build_xlsx(_manifest_template_rows())
    filename = f"货物清单导入模板_{time.strftime('%Y%m%d')}.xlsx"
    return {
        "xlsx_base64": base64.b64encode(workbook).decode(),
        "filename": filename,
    }

@app.post("/api/extract")
async def api_extract(file: UploadFile = File(...)):
    img_bytes = await file.read()
    if len(img_bytes) > 10_000_000:
        raise HTTPException(413, "图片太大，请控制在 10MB 以内")
    mime = file.content_type or "image/jpeg"
    b64_img = base64.b64encode(img_bytes).decode()
    body = json.dumps({
        "model": QWEN_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_img}"}},
            {"type": "text", "text": EXTRACT_PROMPT},
        ]}],
        "max_tokens": 4096,
        "enable_thinking": False,  # 关思考链, 结构化提取不需要
    }).encode("utf-8")
    data = _post_dashscope(body)
    raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        skus = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(422, f"Qwen 返回无法解析为 JSON，请重试。原始:\n{raw[:500]}")
    return {"skus": _normalize_extracted_skus(skus), "model_used": QWEN_MODEL}

# ── 文字识别（粘贴文本）──
EXTRACT_TEXT_PROMPT = """你是装柜助手。请从下面的文字信息中提取所有货物(SKU)数据。

【关键: 中文报价单列名歧义处理】
- "装箱量" 通常指"每箱装 N 件", 不是箱数本身
- "件数" 经常指"箱数"(cartons), 不是 pieces
- "总数量" 通常指 pieces 总数 = 箱数 × 每箱件数
- "箱数" 才明确指 cartons
- "重量" 一般是单箱重, 但可能是单件重
- "总重量" 是所有箱子加起来的总重

你必须用算术做交叉验证:
- 必须满足: qty(箱数) × weight(单箱重) ≈ 总重量
- 如果数据不一致, 优先选使算术成立的组合
- 在 note 里写清楚推理依据

返回严格 JSON 数组(不要 markdown 代码块), 每个对象:
- model: string, 型号/货号
- length: number, 外箱长(cm)
- width: number, 外箱宽(cm)
- height: number, 外箱高(cm)
- weight: number, 单箱重量(kg)
- qty: number, 总箱数(cartons 数)
- stack_mode: "full" / "flat" / "none"
- upright_only: boolean
- supplier: string, 厂家/供应商名 (有则提取, 否则填空字符串)
- note: string, 推理依据(单位/算术/歧义), 完全确定时可留空

规则:
1. 单位统一 cm/kg
2. 无法判断填0, note说明
3. 跳过表头/合计行
4. 严禁编造

只输出 JSON 数组。"""

class TextExtractRequest(BaseModel):
    text: str = Field(..., min_length=5)

@app.post("/api/extract_text")
async def api_extract_text(req: TextExtractRequest):
    body = json.dumps({
        "model": QWEN_MODEL,
        "messages": [{"role": "user", "content": EXTRACT_TEXT_PROMPT + "\n\n" + req.text}],
        "max_tokens": 4096,
        "enable_thinking": False,
    }).encode("utf-8")
    data = _post_dashscope(body)
    raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        skus = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(422, f"Qwen 返回无法解析为 JSON，请重试。原始:\n{raw[:500]}")
    return {"skus": _normalize_extracted_skus(skus), "model_used": QWEN_MODEL}

# ── 启动 ──
def _find_free_port(start=17283, n=50):
    for p in range(start, start+n):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try: s.bind(("127.0.0.1", p)); return p
            except OSError: continue
    raise RuntimeError("找不到可用端口")

def main():
    port = _find_free_port()
    url = f"http://127.0.0.1:{port}/"
    def _open():
        time.sleep(1.2)
        try: webbrowser.open(url)
        except: pass
    threading.Thread(target=_open, daemon=True).start()
    print("="*60)
    print("  装柜模拟器已启动")
    print(f"  访问地址: {url}")
    print("  关闭这个黑色窗口即可退出程序")
    print("="*60)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

# ── 安装包自检 ──
def _self_test() -> int:
    """安装后自检：起本地服务、请求首页、确认渲染链路随包；不需要浏览器和手柄。"""
    import traceback
    log_path = Path(tempfile.gettempdir()) / "ContainerPack-self-test.log"
    report = []
    try:
        from _visualizer import render_loading_plan  # noqa: F401  渲染链路必须随包
        port = _find_free_port()
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
        threading.Thread(target=server.run, daemon=True).start()
        deadline, body = time.time() + 40, b""
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as resp:
                    body = resp.read()
                break
            except Exception:
                time.sleep(0.3)
        server.should_exit = True
        ok = b"<html" in body.lower() and len(body) > 5000
        report.append(f"index_bytes={len(body)}")
        report.append("OK" if ok else "FAILED: 首页未正常返回")
        code = 0 if ok else 3
    except Exception:
        report.append(traceback.format_exc())
        code = 3
    log_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return code

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    main()
