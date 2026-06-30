from __future__ import annotations

import argparse
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from text_quality import find_mojibake_in_text, format_issues


ROOT = Path(__file__).resolve().parent
EXPECTED_TITLE = "\u88c5\u67dc\u5de5\u4f5c\u53f0"
LAYOUT_KEY = "container-pack-layout-v1"
DRAFT_KEY = "container-pack-autodraft-v1"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http(url: str, timeout_s: float = 12) -> None:
    deadline = time.monotonic() + timeout_s
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError) as exc:
            last_error = exc
        time.sleep(0.15)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _start_local_server(port: int):
    import app
    import uvicorn

    config = uvicorn.Config(
        app.app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="browser-smoke-server", daemon=True)
    thread.start()
    return server, thread


def _px(value: str) -> float:
    return float((value or "0").strip().removesuffix("px") or 0)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _css_var(page: Any, name: str) -> float:
    raw = page.evaluate(
        "name => getComputedStyle(document.documentElement).getPropertyValue(name).trim()",
        name,
    )
    return _px(raw)


def _drag(page: Any, selector: str, *, dx: float = 0, dy: float = 0) -> None:
    box = page.locator(selector).bounding_box()
    _assert(bool(box), f"Missing draggable handle: {selector}")
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + dx, y + dy, steps=6)
    page.mouse.up()


def run_browser_smoke(
    base_url: str,
    *,
    headed: bool = False,
    timeout_ms: int = 30_000,
    screenshot: Path | None = None,
) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Playwright is required. Install it with: "
            "py -3.13 -m pip install playwright && py -3.13 -m playwright install chromium"
        ) from exc

    with sync_playwright() as play:
        try:
            browser = play.chromium.launch(headless=not headed)
        except Exception as exc:
            if "Executable doesn't exist" in str(exc) or "playwright install" in str(exc):
                raise RuntimeError(
                    "Playwright Chromium is missing. Install it with: "
                    "py -3.13 -m playwright install chromium"
                ) from exc
            raise

        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
        )
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        try:
            page.goto(base_url, wait_until="networkidle")
            _assert(page.title() == EXPECTED_TITLE, f"Unexpected page title: {page.title()!r}")
            text_issues = find_mojibake_in_text("browser", page.locator("body").inner_text())
            _assert(not text_issues, "Rendered page contains mojibake:\n" + format_issues(text_issues))

            page.locator("#btn-sample").click()
            page.wait_for_function("() => document.querySelectorAll('#items-body tr').length >= 4")

            page.locator("#btn-calc").click()
            page.wait_for_function("() => !document.querySelector('#btn-calc')?.disabled")
            page.wait_for_function("() => document.querySelectorAll('.svg-item').length > 0")
            page.wait_for_function("() => document.querySelectorAll('#stats .stat').length >= 6")
            page.wait_for_function(
                f"() => JSON.parse(localStorage.getItem('{DRAFT_KEY}') || 'null')?.data?.placements?.length > 0"
            )
            _assert(page.locator("#btn-restore-draft").is_enabled(), "Restore draft button did not enable")

            for selector in (
                "#split-left",
                "#split-right",
                "#split-center-tools",
                "#split-center-bottom",
                ".panel-resizer",
            ):
                _assert(page.locator(selector).count() > 0, f"Missing selector: {selector}")

            left_before = _css_var(page, "--left-w")
            strip_before = _css_var(page, "--strip-h")
            bottom_before = _css_var(page, "--bottom-h")

            _drag(page, "#split-left", dx=24)
            page.wait_for_function(
                "before => parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--left-w')) > before",
                arg=left_before,
            )

            _drag(page, "#split-center-tools", dy=24)
            page.wait_for_function(
                "before => parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--strip-h')) > before",
                arg=strip_before,
            )

            _drag(page, "#split-center-bottom", dy=-24)
            page.wait_for_function(
                "before => parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--bottom-h')) > before",
                arg=bottom_before,
            )

            saved = page.evaluate(
                f"() => JSON.parse(localStorage.getItem('{LAYOUT_KEY}') || '{{}}')"
            )
            for key in ("left", "strip", "bottom"):
                _assert(key in saved, f"Layout state did not save {key!r}")

            if screenshot:
                screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot), full_page=True)

            page.locator("#btn-reset-layout").click()
            page.wait_for_function(
                f"() => !localStorage.getItem('{LAYOUT_KEY}')"
            )
        finally:
            context.close()
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real-browser UI smoke test.")
    parser.add_argument("--url", help="Existing Container Pack App URL to test.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible window.")
    parser.add_argument("--timeout-ms", type=int, default=30_000, help="Per-action Playwright timeout.")
    parser.add_argument("--screenshot", type=Path, help="Optional screenshot path to write after the smoke flow passes.")
    args = parser.parse_args()

    server = None
    thread = None
    if args.url:
        base_url = args.url.rstrip("/") + "/"
    else:
        port = _free_port()
        base_url = f"http://127.0.0.1:{port}/"
        server, thread = _start_local_server(port)

    try:
        _wait_for_http(base_url)
        run_browser_smoke(
            base_url,
            headed=args.headed,
            timeout_ms=args.timeout_ms,
            screenshot=args.screenshot,
        )
    except Exception as exc:
        print(f"[browser-smoke] FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        if server is not None:
            server.should_exit = True
        if thread is not None:
            thread.join(timeout=5)

    print(f"[browser-smoke] OK: {base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
