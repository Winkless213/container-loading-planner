from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BrowserSmokeContractTest(unittest.TestCase):
    def test_browser_smoke_covers_core_workbench_flow(self):
        text = (ROOT / "browser_smoke.py").read_text(encoding="utf-8")

        self.assertIn("sync_playwright", text)
        self.assertIn("#btn-sample", text)
        self.assertIn("#btn-calc", text)
        self.assertIn(".svg-item", text)
        self.assertIn("#stats .stat", text)
        self.assertIn("#split-left", text)
        self.assertIn("#split-center-tools", text)
        self.assertIn("#split-center-bottom", text)
        self.assertIn("container-pack-layout-v1", text)

    def test_preflight_exposes_browser_smoke_gate(self):
        text = (ROOT / "preflight.py").read_text(encoding="utf-8")

        self.assertIn("--browser-smoke", text)
        self.assertIn("run_browser_smoke", text)
        self.assertIn("browser_smoke.py", text)


if __name__ == "__main__":
    unittest.main()
