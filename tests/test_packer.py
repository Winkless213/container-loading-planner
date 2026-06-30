import unittest

from _packer import CONTAINERS, SKU, smart_pack
from _validator import validate_plan


class PackerRegressionTest(unittest.TestCase):
    def test_sample_load_is_valid(self):
        skus = [
            SKU("CSL-160", "CSL-160", 58, 45, 55, 22, 75, True, True, False, "A厂", 1),
            SKU("CC-65A", "CC-65A", 50, 40, 35, 15, 74, True, True, False, "A厂", 1),
            SKU("M-MOTOR", "M-MOTOR", 60, 60, 80, 25, 12, True, False, True, "B机械厂", 2),
            SKU("T-50L", "T-50L", 55, 55, 85, 70, 30, True, False, False, "C灭菌", 3),
        ]
        placed, unfitted = smart_pack(skus, CONTAINERS["40HQ"], pack_mode="auto")
        self.assertEqual([], unfitted)
        self.assertEqual(sum(s.qty for s in skus), len(placed))
        self.assertEqual([], [issue.to_dict() for issue in validate_plan(placed, skus, CONTAINERS["40HQ"])])

    def test_flat_stack_platform_does_not_create_floating_space(self):
        spec = {"L": 200, "W": 200, "H": 200, "max_kg": 10000, "name": "demo"}
        skus = [
            SKU("BASE", "BASE", 100, 100, 50, 1, 1, True, False, True),
            SKU("TOP", "TOP", 100, 100, 20, 1, 2, True, True, False),
        ]
        placed, unfitted = smart_pack(skus, spec, pack_mode="compact")
        self.assertEqual([], unfitted)
        self.assertEqual([], [issue.to_dict() for issue in validate_plan(placed, skus, spec)])


if __name__ == "__main__":
    unittest.main()
