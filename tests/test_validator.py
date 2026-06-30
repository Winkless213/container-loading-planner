import unittest

from _packer import PlacedItem, SKU
from _validator import validate_plan


SPEC = {"L": 200, "W": 200, "H": 200, "max_kg": 1000, "name": "test"}


def item(model, instance_id, x, y, z, length=100, width=100, height=50, weight=10):
    return PlacedItem(model, instance_id, x, y, z, length, width, height, weight, "#000", False)


class ValidatorTest(unittest.TestCase):
    def test_detects_out_of_bounds(self):
        issues = validate_plan(
            [item("A", 1, 150, 0, 0, length=100)],
            [SKU("A", "A", 100, 100, 50, 10, 1)],
            SPEC,
        )
        self.assertIn("out_of_bounds", {issue.code for issue in issues})

    def test_detects_collision(self):
        issues = validate_plan(
            [item("A", 1, 0, 0, 0), item("B", 1, 50, 0, 0)],
            [SKU("A", "A", 100, 100, 50, 10, 1), SKU("B", "B", 100, 100, 50, 10, 1)],
            SPEC,
        )
        self.assertIn("collision", {issue.code for issue in issues})

    def test_detects_unsupported_upper_item(self):
        issues = validate_plan(
            [item("BASE", 1, 0, 0, 0), item("TOP", 1, 0, 100, 50)],
            [SKU("BASE", "BASE", 100, 100, 50, 10, 1), SKU("TOP", "TOP", 100, 100, 50, 10, 1)],
            SPEC,
        )
        self.assertIn("unsupported", {issue.code for issue in issues})

    def test_detects_non_stackable_support(self):
        issues = validate_plan(
            [item("BASE", 1, 0, 0, 0), item("TOP", 1, 0, 0, 50)],
            [
                SKU("BASE", "BASE", 100, 100, 50, 10, 1, allow_stack=False),
                SKU("TOP", "TOP", 100, 100, 50, 10, 1),
            ],
            SPEC,
        )
        self.assertIn("non_stackable_support", {issue.code for issue in issues})

    def test_accepts_fully_supported_upper_item(self):
        issues = validate_plan(
            [item("BASE", 1, 0, 0, 0), item("TOP", 1, 0, 0, 50)],
            [SKU("BASE", "BASE", 100, 100, 50, 10, 1), SKU("TOP", "TOP", 100, 100, 50, 10, 1)],
            SPEC,
        )
        self.assertEqual([], [issue for issue in issues if issue.severity == "error"])

    def test_detects_missing_and_over_placed_counts(self):
        issues = validate_plan(
            [item("A", 1, 0, 0, 0), item("A", 2, 100, 0, 0)],
            [SKU("A", "A", 100, 100, 50, 10, 1), SKU("B", "B", 100, 100, 50, 10, 1)],
            SPEC,
        )
        codes = {issue.code for issue in issues}
        self.assertIn("over_placed", codes)
        self.assertIn("missing_items", codes)

    def test_detects_door_reserve_occupied(self):
        issues = validate_plan(
            [item("A", 1, 130, 0, 0, length=60)],
            [SKU("A", "A", 60, 100, 50, 10, 1)],
            SPEC,
            door_reserve_cm=40,
        )
        self.assertIn("door_reserve_occupied", {issue.code for issue in issues})

    def test_warns_when_meaningful_weight_is_unbalanced(self):
        issues = validate_plan(
            [item("A", 1, 0, 0, 0, length=50, weight=300)],
            [SKU("A", "A", 50, 100, 50, 300, 1)],
            SPEC,
        )
        self.assertIn("weight_balance", {issue.code for issue in issues})

    def test_warns_when_lateral_weight_is_unbalanced(self):
        issues = validate_plan(
            [item("A", 1, 75, 0, 0, length=50, width=50, weight=300)],
            [SKU("A", "A", 50, 50, 50, 300, 1)],
            SPEC,
        )
        self.assertIn("lateral_weight_balance", {issue.code for issue in issues})

    def test_detects_segment_overweight(self):
        issues = validate_plan(
            [item("A", 1, 0, 0, 0, length=50, weight=220)],
            [SKU("A", "A", 50, 100, 50, 220, 1)],
            {**SPEC, "L": 600},
            max_segment_weight_kg=200,
        )
        self.assertIn("segment_overweight", {issue.code for issue in issues})

    def test_detects_top_load_exceeded(self):
        issues = validate_plan(
            [
                item("BASE", 1, 0, 0, 0, length=100, width=100, height=50, weight=20),
                item("TOP", 1, 0, 0, 50, length=100, width=100, height=50, weight=80),
            ],
            [
                SKU("BASE", "BASE", 100, 100, 50, 20, 1, max_top_load_kg=50),
                SKU("TOP", "TOP", 100, 100, 50, 80, 1),
            ],
            SPEC,
        )
        self.assertIn("top_load_exceeded", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
