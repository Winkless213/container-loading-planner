# -*- coding: utf-8 -*-
"""
核心装柜算法（与独立工具共用）
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import ceil
from typing import Literal

CONTAINERS = {
    "20GP": {"L": 589,  "W": 235, "H": 239, "max_kg": 21700, "name": "20尺普柜"},
    "40GP": {"L": 1203, "W": 235, "H": 239, "max_kg": 26500, "name": "40尺普柜"},
    "40HQ": {"L": 1205, "W": 235, "H": 269, "max_kg": 25000, "name": "40尺高柜"},
    "45HQ": {"L": 1358, "W": 235, "H": 269, "max_kg": 27600, "name": "45尺高柜"},
}


@dataclass
class SKU:
    model: str
    name: str
    length: float
    width: float
    height: float
    weight: float
    qty: int
    upright_only: bool = True
    allow_stack: bool = True
    flat_stack: bool = False  # 平铺可叠: 自己单层放(不叠自己), 但顶部允许其他货物堆叠(如机械+垫板)
    supplier: str = ""  # 厂家名 (空=未分组)
    arrival_order: int = 1  # 到货顺序, 数值越小越早到 → 越靠柜尾; 越大越晚到 → 越靠柜门
    max_top_load_kg: float = 0  # 0=不限制; >0 表示该 SKU 单箱允许承受的最大上压重量


@dataclass
class PlacedItem:
    sku_model: str
    instance_id: int
    x: float; y: float; z: float
    length: float; width: float; height: float
    weight: float; color: str; rotated: bool

    def to_dict(self):
        return asdict(self)


def _orientations(l, w, h, upright_only):
    if upright_only:
        return [(l, w, h, False), (w, l, h, True)]
    from itertools import permutations
    seen = set(); result = []
    for p in permutations([l, w, h]):
        if p not in seen:
            seen.add(p); result.append((*p, p != (l, w, h)))
    return result


def _best_grid(item_dims, avail_dims, n_target, upright_only, allow_stack):
    l, w, h = item_dims; L, W, H = avail_dims
    best = None
    for dl, dw, dh, rotated in _orientations(l, w, h, upright_only):
        if dl > L or dw > W or dh > H:
            continue
        nx_max = int(L // dl); ny_max = int(W // dw)
        nz_max = int(H // dh) if allow_stack else 1
        if nx_max * ny_max * nz_max == 0:
            continue
        n = min(n_target, nx_max * ny_max * nz_max)
        per_xslice = ny_max * nz_max
        length_used = ceil(n / per_xslice) * dl
        score = (n, -length_used)
        if best is None or score > best[0]:
            best = (score, (dl, dw, dh, rotated), (nx_max, ny_max, nz_max), n)
    return best[1:] if best else None


def smart_pack(skus: list[SKU], container_spec: dict, pack_mode: str = "auto"):
    """装柜算法调度器。

    pack_mode:
      - "compact":  紧凑模式, 不考虑厂家, 空间利用率最高
      - "grouped":  按 supplier 分组, 沿 X 轴分区 (arrival_order 小=柜尾, 大=柜门)
      - "auto":     先试 compact, 利用率 < 75% 就切 grouped (default)

    支持三种堆叠模式:
    - allow_stack=True, flat_stack=False: 可堆叠 (纸箱)
    - allow_stack=False, flat_stack=True: 平铺可叠 (机械设备 + 垫板在其上)
    - allow_stack=False, flat_stack=False: 完全不叠 (易碎品)
    """
    # 全局颜色: 按原始 SKU 顺序 + 型号去重, 保证跨模式颜色一致
    palette = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6",
               "#1ABC9C", "#E67E22", "#34495E", "#16A085", "#D35400"]
    color_map = {}
    for idx, s in enumerate(skus):
        if s.model not in color_map:
            color_map[s.model] = palette[len(color_map) % len(palette)]

    if pack_mode == "compact":
        return _pack_compact(skus, container_spec, color_map)
    if pack_mode == "grouped":
        return _pack_grouped(skus, container_spec, color_map)
    # auto
    placed, unfitted = _pack_compact(skus, container_spec, color_map)
    L, W, H = container_spec["L"], container_spec["W"], container_spec["H"]
    cbm_cap = L * W * H
    cbm_used = sum(p.length * p.width * p.height for p in placed)
    util = cbm_used / cbm_cap if cbm_cap > 0 else 0
    # 有多个厂家且空间有余 → 切分厂家模式
    suppliers = {(getattr(s, "supplier", "") or "") for s in skus}
    suppliers.discard("")
    if len(suppliers) >= 2 and util < 0.75 and not unfitted:
        return _pack_grouped(skus, container_spec, color_map)
    return placed, unfitted


def _pack_grouped(skus: list[SKU], container_spec: dict, color_map: dict | None = None):
    """分厂家模式 (简化策略):
    - flat_stack 货物(机械)优先放底层, 按 arrival_order+supplier 排序
    - 其他货物按 (arrival_order, supplier) 分组, 每组内按体积降序
    - 所有货物排好顺序后, 交给 _pack_compact 沿 X 轴依次放置
    - 效果: 机械在柜尾底部, 各厂家货物沿 X 轴依次分布, arrival_order 小的靠柜尾
    - 不强制分区的严格边界, 但视觉上同一厂家货物自然聚在一起
    - 机械上方空间会被后续厂家的可叠货利用 (通过 _pack_compact 内置的 platform 逻辑)
    """
    # 排序: flat_stack 货物全局优先 (它们没法用平台, 必须先抢地板),
    # 全局 flat 内部按 (arrival_order, 有厂家在前/无厂家在后, supplier名, -vol)
    # 这样保证用户设置的"第一家"(有厂家名的) 会先放到柜尾, 无厂家的散货放在后面
    def _sort_key(sku):
        is_flat = getattr(sku, "flat_stack", False)
        vol = sku.length * sku.width * sku.height * sku.qty
        has_supplier = 0 if sku.supplier else 1  # 有厂家=0(先放), 无厂家=1(后放)
        return (
            0 if is_flat else 1,       # 全局 flat-first
            sku.arrival_order or 1,
            has_supplier,
            sku.supplier or "",
            -vol,
        )

    sorted_skus = sorted(skus, key=_sort_key)

    # 直接交给 _pack_compact, 但需要让 _pack_compact 按输入顺序放置, 不重排
    # 现有 _pack_compact 内部会按 (flat优先, 体积降序) 排序, 这会破坏 supplier 分组
    # 所以需要加一个 "保持输入顺序" 的开关
    return _pack_compact(sorted_skus, container_spec, color_map, preserve_order=True)


def _pack_compact(skus: list[SKU], container_spec: dict, color_map: dict | None = None, preserve_order: bool = False):
    """紧凑装柜算法 (原 smart_pack 主体)。
    color_map: 可选的 {sku_model: hex_color} 映射, 用于跨调用保持颜色一致
    preserve_order: True 时按输入顺序放置 (分厂家模式用), False 时内部排序优化 (默认)
    """
    L, W, H = container_spec["L"], container_spec["W"], container_spec["H"]
    max_kg = container_spec["max_kg"]

    palette = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6",
               "#1ABC9C", "#E67E22", "#34495E", "#16A085", "#D35400"]

    if preserve_order:
        # 保持输入顺序, 不重排 (分厂家模式用)
        sku_order = list(enumerate(skus))
    else:
        # Sort: flat_stack 优先 (先放机械设备给出平台), 再按体积降序
        def _priority(sku):
            is_flat = getattr(sku, "flat_stack", False)
            vol = sku.length * sku.width * sku.height * sku.qty
            return (0 if is_flat else 1, -vol)

        sku_order = sorted(enumerate(skus), key=lambda t: _priority(t[1]))

    placed = []; unfitted = []
    total_weight = 0.0; x_cursor = 0.0
    last_leftover = None
    # 平台信息: 由 flat_stack 货物放置后产生的可堆叠顶面
    # 每个 platform: {x, y, dx, dy, z_top, used_x}
    platforms = []

    for orig_idx, sku in sku_order:
        color = (color_map or {}).get(sku.model) or palette[orig_idx % len(palette)]
        qty = sku.qty; count = 0
        is_flat = getattr(sku, "flat_stack", False)
        # flat_stack 物品本身强制单层放置, 内部 allow_stack 取 False
        eff_allow_stack = sku.allow_stack and not is_flat

        # 回填上一组末列空位 (仅限 cursor 放置延续)
        # preserve_order=True (分厂家模式) 时禁用回填, 避免打破厂家分组
        if last_leftover is not None and not preserve_order:
            ll_dl, ll_dw, ll_dh, _ = last_leftover["dims"]
            matches_direct = (sku.length == ll_dl and sku.width == ll_dw and sku.height == ll_dh)
            matches_rotated = (sku.width == ll_dl and sku.length == ll_dw and sku.height == ll_dh)
            if matches_direct or matches_rotated:
                for cx, cy, cz in list(last_leftover["empty_cells"]):
                    if count >= qty or total_weight + sku.weight > max_kg:
                        break
                    placed.append(PlacedItem(
                        sku.model, count + 1, cx, cy, cz,
                        ll_dl, ll_dw, ll_dh, sku.weight, color, matches_rotated,
                    ))
                    last_leftover["empty_cells"].remove((cx, cy, cz))
                    total_weight += sku.weight; count += 1
                if not last_leftover["empty_cells"]:
                    last_leftover = None

        # 迭代放置: 
        #   - 紧凑模式 (preserve_order=False): 平台优先, 地板兜底 (高利用率)
        #   - 分厂家模式 (preserve_order=True): 地板优先, 平台仅当地板满后兜底
        #     这样避免当前 SKU 跳到前面其他厂家创造的平台上, 保持厂家分组聚集
        while count < qty:
            remaining = qty - count
            placement = None

            def _try_platform(same_supplier_only=False):
                if not (sku.allow_stack and not is_flat):
                    return None
                best_plat = None
                for plat in platforms:
                    if same_supplier_only and plat.get("supplier", "") != (sku.supplier or ""):
                        continue
                    remain_x = plat["dx"] - plat["used_x"]
                    if remain_x <= 0: continue
                    avail = (remain_x, plat["dy"], H - plat["z_top"])
                    if avail[0] <= 0 or avail[1] <= 0 or avail[2] <= 0: continue
                    g = _best_grid((sku.length, sku.width, sku.height), avail,
                                   remaining, sku.upright_only, eff_allow_stack)
                    if g is None: continue
                    (dl, dw, dh, rotated), (nx_max, ny_max, nz_max), n_actual = g
                    if best_plat is None or n_actual > best_plat["n"]:
                        best_plat = {"type": "platform", "platform": plat,
                                     "start_x": plat["x"] + plat["used_x"],
                                     "start_y": plat["y"], "start_z": plat["z_top"],
                                     "dims": (dl, dw, dh, rotated),
                                     "grid": (nx_max, ny_max, nz_max), "n": n_actual}
                return best_plat if best_plat and best_plat["n"] > 0 else None

            def _try_cursor():
                if L - x_cursor <= 0:
                    return None
                avail = (L - x_cursor, W, H)
                g = _best_grid((sku.length, sku.width, sku.height), avail,
                               remaining, sku.upright_only, eff_allow_stack)
                if g is None: return None
                (dl, dw, dh, rotated), (nx_max, ny_max, nz_max), n_actual = g
                return {"type": "cursor",
                        "start_x": x_cursor, "start_y": 0, "start_z": 0,
                        "dims": (dl, dw, dh, rotated),
                        "grid": (nx_max, ny_max, nz_max), "n": n_actual}

            if preserve_order:
                # 分厂家模式: 地板优先 (保持厂家聚集), 平台兜底 (不浪费机器顶部空间)
                # flat 货物全局排在前面, 已经抢到地板; 可叠货物按厂家用地板, 满了就上平台
                placement = _try_cursor() or _try_platform(same_supplier_only=False)
            else:
                # 紧凑模式: 平台优先 > 地板 (最大化空间利用率)
                placement = _try_platform(same_supplier_only=False) or _try_cursor()

            if placement is None:
                break  # 平台和地板都放不下, 跳出迭代

            # 应用重量限制
            n_actual = placement["n"]
            weight_cap = int((max_kg - total_weight) / sku.weight) if sku.weight > 0 else n_actual
            n_actual = min(n_actual, weight_cap)
            if n_actual <= 0:
                break  # 超重, 整个 SKU 后续都不能放

            (dl, dw, dh, rotated) = placement["dims"]
            (nx_max, ny_max, nz_max) = placement["grid"]
            sx, sy, sz = placement["start_x"], placement["start_y"], placement["start_z"]

            per_xslice = ny_max * nz_max
            nx_used = ceil(n_actual / per_xslice)

            placed_here = 0; last_col_used = []
            new_platforms = []
            for ix in range(nx_used):
                col_x = sx + ix * dl
                for iz in range(nz_max):
                    for iy in range(ny_max):
                        if placed_here >= n_actual: break
                        px, py, pz = col_x, sy + iy*dw, sz + iz*dh
                        placed_item = PlacedItem(
                            sku.model, count + 1,
                            px, py, pz,
                            dl, dw, dh, sku.weight, color, rotated,
                        )
                        placed.append(placed_item)
                        count += 1; placed_here += 1
                        if ix == nx_used - 1:
                            last_col_used.append((px, py, pz))
                        if is_flat and placement["type"] == "cursor":
                            # A flat-stack item only supports the footprint it actually occupies.
                            # Treating a partially filled grid as one large platform creates
                            # floating placements over empty air.
                            new_platforms.append({
                                "x": px, "y": py,
                                "dx": dl, "dy": dw,
                                "z_top": pz + dh, "used_x": 0,
                                "supplier": sku.supplier or "",
                            })

            total_weight += placed_here * sku.weight

            # 更新 cursor / 平台使用量
            if placement["type"] == "cursor":
                x_cursor += nx_used * dl
                # leftover 记录(仅 cursor)
                last_col_x = x_cursor - dl
                all_cells = [(last_col_x, iy*dw, iz*dh)
                             for iz in range(nz_max) for iy in range(ny_max)]
                empty_cells = [c for c in all_cells if c not in last_col_used]
                last_leftover = {"dims": (dl, dw, dh, rotated),
                                 "empty_cells": empty_cells} if empty_cells else None
                # flat_stack 放置后产生平台
                if new_platforms:
                    platforms.extend(new_platforms)
            else:
                placement["platform"]["used_x"] += nx_used * dl
                last_leftover = None

            # 如果这次没全放下就继续循环尝试下一个位置
            if placed_here == 0:
                break  # 防死循环

        if count < qty:
            unfitted.append((sku.model, qty - count))

    return placed, unfitted


def recommend_best_container(skus: list[SKU]) -> dict:
    """推荐最优柜型，返回详细对比"""
    results = {}
    for ctype, spec in CONTAINERS.items():
        placed, unfitted = smart_pack(skus, spec)
        total_cbm = sum(p.length*p.width*p.height for p in placed) / 1_000_000
        total_w = sum(p.weight for p in placed)
        results[ctype] = {
            "container_type": ctype,
            "container_name": spec["name"],
            "n_placed": len(placed),
            "n_unfitted": sum(c for _, c in unfitted),
            "cbm_used": round(total_cbm, 2),
            "cbm_capacity": round(spec["L"]*spec["W"]*spec["H"]/1_000_000, 2),
            "cbm_utilization": round(total_cbm / (spec["L"]*spec["W"]*spec["H"]/1_000_000) * 100, 1),
            "weight_total": round(total_w, 0),
            "weight_utilization": round(total_w / spec["max_kg"] * 100, 1),
            "unfitted_detail": [{"model": m, "count": c} for m, c in unfitted],
        }

    # 推荐逻辑
    fit_all = {k: v for k, v in results.items() if v["n_unfitted"] == 0}
    total_cbm = sum(s.length*s.width*s.height*s.qty for s in skus) / 1_000_000

    if not fit_all:
        recommendation = {
            "recommended": None,
            "reason": "所有标准柜型都装不下，需拆单分柜或考虑 45HQ 加高柜。",
            "suggest_lcl": False,
        }
    else:
        # 最小的能装下的柜
        smallest = min(fit_all.items(), key=lambda x: x[1]["cbm_capacity"])
        ctype, stats = smallest

        if stats["cbm_utilization"] < 25:
            recommendation = {
                "recommended": ctype,
                "reason": (f"总货量 {total_cbm:.2f} CBM 偏少，最小可用柜型 {stats['container_name']} "
                          f"利用率仅 {stats['cbm_utilization']}%，建议走拼箱（LCL）更划算。"),
                "suggest_lcl": True,
            }
        elif stats["cbm_utilization"] < 50:
            recommendation = {
                "recommended": ctype,
                "reason": (f"推荐 {stats['container_name']} ({ctype})，利用率 {stats['cbm_utilization']}%（偏低）。"
                          f"如不急发可凑单提升利用率。"),
                "suggest_lcl": False,
            }
        else:
            recommendation = {
                "recommended": ctype,
                "reason": f"推荐 {stats['container_name']} ({ctype})，利用率 {stats['cbm_utilization']}%。",
                "suggest_lcl": False,
            }

    return {
        "summary": {
            "total_skus": len(skus),
            "total_cartons": sum(s.qty for s in skus),
            "total_cbm": round(total_cbm, 2),
            "total_weight_kg": round(sum(s.weight*s.qty for s in skus), 0),
        },
        "containers": results,
        "recommendation": recommendation,
    }
