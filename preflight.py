from __future__ import annotations

import argparse
import base64
import io
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_FILES = [
    "app.py",
    "_frontend.py",
    "_packer.py",
    "_validator.py",
    "_visualizer.py",
    "browser_smoke.py",
    "text_quality.py",
]


def _run_step(name: str, args: list[str]) -> None:
    print(f"[preflight] {name}")
    subprocess.run(args, cwd=ROOT, check=True)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _open_xlsx_from_base64(payload: str) -> zipfile.ZipFile:
    data = base64.b64decode(payload)
    return zipfile.ZipFile(io.BytesIO(data))


def compile_sources() -> None:
    _run_step("compile Python sources", [sys.executable, "-m", "py_compile", *SOURCE_FILES])


def run_tests() -> None:
    _run_step("run unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def run_text_quality() -> None:
    _run_step("check text encoding quality", [sys.executable, str(ROOT / "text_quality.py")])


def run_browser_smoke() -> None:
    _run_step("run browser UI smoke", [sys.executable, str(ROOT / "browser_smoke.py")])


def api_smoke(*, strict_render: bool = False) -> None:
    print("[preflight] API smoke")
    from fastapi.testclient import TestClient

    import app

    client = TestClient(app.app)
    index = client.get("/")
    _assert(index.status_code == 200, "index page did not return HTTP 200")
    _assert("charset=utf-8" in index.headers.get("content-type", "").lower(), "index page is not served as UTF-8")
    _assert("装柜工作台" in index.text, "index page title is missing")

    manifest = "型号,长,宽,高,重,箱,规则\nSMOKE,100,80,60,20,2,叠\n".encode("utf-8")
    imported = client.post(
        "/api/import_manifest",
        files={"file": ("smoke.csv", manifest, "text/csv")},
    )
    _assert(imported.status_code == 200, f"manifest import failed: {imported.text}")
    imported_data = imported.json()
    _assert(len(imported_data["skus"]) == 1, "manifest import did not return one SKU")

    pack_payload = {
        "container_type": "20GP",
        "pack_mode": "auto",
        "skus": [
            {
                "model": "SMOKE",
                "length": 100,
                "width": 80,
                "height": 60,
                "weight": 20,
                "qty": 2,
            }
        ],
    }
    packed = client.post("/api/pack", json=pack_payload)
    _assert(packed.status_code == 200, f"pack API failed: {packed.text}")
    packed_data = packed.json()
    render_error = packed_data.get("render_error")
    if render_error:
        if strict_render:
            raise AssertionError(f"PNG renderer failed: {render_error}")
        print(f"[preflight] warning: PNG renderer unavailable: {render_error}")
    else:
        _assert(packed_data.get("png_base64"), "pack API did not return a PNG payload")
    _assert(len(packed_data["placements"]) == 2, "pack API did not place both smoke cartons")
    _assert(not [i for i in packed_data["validation"] if i["severity"] == "error"], "pack API returned validation errors")

    validate_payload = {
        "container_type": "20GP",
        "skus": pack_payload["skus"],
        "placements": packed_data["placements"],
    }
    validated = client.post("/api/validate_plan", json=validate_payload)
    _assert(validated.status_code == 200, f"validate API failed: {validated.text}")
    _assert(not [i for i in validated.json()["validation"] if i["severity"] == "error"], "validate API returned errors")

    template = client.get("/api/import_template")
    _assert(template.status_code == 200, f"template API failed: {template.text}")
    with _open_xlsx_from_base64(template.json()["xlsx_base64"]) as zf:
        names = set(zf.namelist())
        _assert("xl/workbook.xml" in names, "template workbook is missing xl/workbook.xml")

    workbook_payload = {
        **validate_payload,
        "project_info": {
            "name": "Smoke Plan",
            "containerNo": "SMOKE-001",
            "revision": "R1",
            "preparedBy": "Preflight",
            "reviewedBy": "Preflight",
            "confirmedBy": "Preflight",
        },
        "activity_log": [{"time": "2026-06-30T00:00:00Z", "action": "preflight", "detail": "smoke"}],
        "manual_touched": True,
    }
    workbook = client.post("/api/export_workbook", json=workbook_payload)
    _assert(workbook.status_code == 200, f"workbook export failed: {workbook.text}")
    with _open_xlsx_from_base64(workbook.json()["xlsx_base64"]) as zf:
        names = set(zf.namelist())
        _assert("xl/workbook.xml" in names, "export workbook is missing xl/workbook.xml")
        _assert("xl/worksheets/sheet1.xml" in names, "export workbook is missing sheet1.xml")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run product preflight checks for Container Pack App.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest discovery.")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip API smoke checks.")
    parser.add_argument("--strict-render", action="store_true", help="Fail if PNG rendering dependencies are unavailable.")
    parser.add_argument("--browser-smoke", action="store_true", help="Run a real-browser UI smoke check with Playwright.")
    args = parser.parse_args()

    try:
        compile_sources()
        run_text_quality()
        if not args.skip_tests:
            run_tests()
        if not args.skip_smoke:
            api_smoke(strict_render=args.strict_render)
        if args.browser_smoke:
            run_browser_smoke()
    except (AssertionError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"[preflight] FAILED: {exc}", file=sys.stderr)
        return 1

    print("[preflight] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
