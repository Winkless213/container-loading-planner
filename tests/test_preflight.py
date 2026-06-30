import unittest

import preflight


class PreflightTest(unittest.TestCase):
    def test_api_smoke_passes(self):
        preflight.api_smoke()


if __name__ == "__main__":
    unittest.main()
