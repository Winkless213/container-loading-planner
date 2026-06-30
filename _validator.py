# -*- coding: utf-8 -*-
"""
Plan validation for container loading layouts.

The packer proposes placements; this module decides whether a layout is
physically usable enough to hand to a human for review or manual editing.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from collections import Counter

from _packer import PlacedItem, SKU

EPS = 1e-6


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    item: str | None = None
    instance_id: int | None = None

    def to_dict(self):
        return asdict(self)


def _overlap_1d(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def _overlap_volume(a: PlacedItem, b: PlacedItem) -> float:
    return (
        _overlap_1d(a.x, a.x + a.length, b.x, b.x + b.length)
        * _overlap_1d(a.y, a.y + a.width, b.y, b.y + b.width)
        * _overlap_1d(a.z, a.z + a.height, b.z, b.z + b.height)
    )


def _rect_union_area(rects: list[tuple[float, float, float, float]]) -> float:
    """Return union area for axis-aligned rectangles."""
    xs = sorted({x for r in rects for x in (r[0], r[2])})
    if len(xs) < 2:
        return 0.0

    area = 0.0
    for left, right in zip(xs, xs[1:]):
        if right - left <= EPS:
            continue
        intervals = []
        for x0, y0, x1, y1 in rects:
            if x0 < right - EPS and x1 > left + EPS:
                intervals.append((y0, y1))
        if not intervals:
            continue
        intervals.sort()
        covered = 0.0
        cur0, cur1 = intervals[0]
        for y0, y1 in intervals[1:]:
            if y0 <= cur1 + EPS:
                cur1 = max(cur1, y1)
            else:
                covered += cur1 - cur0
                cur0, cur1 = y0, y1
        covered += cur1 - cur0
        area += (right - left) * covered
    return area


def _support_area(item: PlacedItem, placed: list[PlacedItem]) -> float:
    rects = []
    for lower in placed:
        if lower is item:
            continue
        lower_top = lower.z + lower.height
        if abs(lower_top - item.z) > EPS:
            continue
        x0 = max(item.x, lower.x)
        y0 = max(item.y, lower.y)
        x1 = min(item.x + item.length, lower.x + lower.length)
        y1 = min(item.y + item.width, lower.y + lower.width)
        if x1 - x0 > EPS and y1 - y0 > EPS:
            rects.append((x0, y0, x1, y1))
    return _rect_union_area(rects)


def _weight_segments(
    placed: list[PlacedItem],
    container_length: float,
    segment_count: int = 6,
) -> list[tuple[int, float, float, float]]:
    if segment_count <= 0 or container_length <= EPS:
        return []
    segment_len = container_length / segment_count
    weights = [0.0 for _ in range(segment_count)]
    for p in placed:
        center = p.x + p.length / 2
        idx = int(center / segment_len) if segment_len > EPS else 0
        idx = max(0, min(segment_count - 1, idx))
        weights[idx] += p.weight
    return [
        (i + 1, i * segment_len, (i + 1) * segment_len, weight)
        for i, weight in enumerate(weights)
    ]


def _top_loads_by_index(placed: list[PlacedItem]) -> list[float]:
    loads = [0.0 for _ in placed]
    order = sorted(range(len(placed)), key=lambda i: placed[i].z, reverse=True)
    for upper_idx in order:
        upper = placed[upper_idx]
        if upper.z <= EPS:
            continue
        footprint = upper.length * upper.width
        if footprint <= EPS:
            continue
        gross_load = upper.weight + loads[upper_idx]
        for lower_idx, lower in enumerate(placed):
            if lower_idx == upper_idx:
                continue
            if abs(lower.z + lower.height - upper.z) > EPS:
                continue
            overlap_area = (
                _overlap_1d(upper.x, upper.x + upper.length, lower.x, lower.x + lower.length)
                * _overlap_1d(upper.y, upper.y + upper.width, lower.y, lower.y + lower.width)
            )
            if overlap_area > EPS:
                loads[lower_idx] += gross_load * overlap_area / footprint
    return loads


def validate_plan(
    placed: list[PlacedItem],
    skus: list[SKU],
    container_spec: dict,
    *,
    check_collisions: bool = True,
    door_reserve_cm: float = 0,
    balance_warn_pct: float = 12,
    max_segment_weight_kg: float = 0,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sku_by_model = {s.model: s for s in skus}
    required_counts = {s.model: s.qty for s in skus}
    placed_counts = Counter(p.sku_model for p in placed)
    L, W, H = container_spec["L"], container_spec["W"], container_spec["H"]
    door_reserve_cm = max(0.0, float(door_reserve_cm or 0))
    usable_l = max(0.0, L - door_reserve_cm)
    max_kg = container_spec["max_kg"]

    total_weight = sum(p.weight for p in placed)
    if total_weight > max_kg + EPS:
        issues.append(ValidationIssue(
            "error",
            "overweight",
            f"总重量 {total_weight:.0f} kg 超过限重 {max_kg:.0f} kg。",
        ))

    max_segment_weight_kg = max(0.0, float(max_segment_weight_kg or 0))
    if max_segment_weight_kg > EPS:
        for idx, start, end, weight in _weight_segments(placed, L):
            if weight > max_segment_weight_kg + EPS:
                issues.append(ValidationIssue(
                    "error",
                    "segment_overweight",
                    f"第 {idx} 段({start:.0f}-{end:.0f} cm)重量 {weight:.0f} kg 超过分段限值 {max_segment_weight_kg:.0f} kg。",
                ))

    for model, count in placed_counts.items():
        if model not in required_counts:
            issues.append(ValidationIssue(
                "error",
                "unknown_sku",
                f"方案中存在货物清单外的 SKU: {model}。",
                model,
            ))
        elif count > required_counts[model]:
            issues.append(ValidationIssue(
                "error",
                "over_placed",
                f"{model} 计划放置 {count} 箱，超过清单数量 {required_counts[model]} 箱。",
                model,
            ))

    for model, required in required_counts.items():
        count = placed_counts.get(model, 0)
        if count < required:
            issues.append(ValidationIssue(
                "warning",
                "missing_items",
                f"{model} 还有 {required - count} 箱未放入方案。",
                model,
            ))

    top_loads = _top_loads_by_index(placed)
    for idx, load in enumerate(top_loads):
        if load <= EPS:
            continue
        p = placed[idx]
        sku = sku_by_model.get(p.sku_model)
        limit = max(0.0, float(getattr(sku, "max_top_load_kg", 0) or 0)) if sku else 0.0
        if limit > EPS and load > limit + EPS:
            issues.append(ValidationIssue(
                "error",
                "top_load_exceeded",
                f"{p.sku_model} 第 {p.instance_id} 箱承受上压 {load:.0f} kg，超过该 SKU 单箱上压限值 {limit:.0f} kg。",
                p.sku_model,
                p.instance_id,
            ))

    for p in placed:
        if (
            p.x < -EPS or p.y < -EPS or p.z < -EPS
            or p.x + p.length > L + EPS
            or p.y + p.width > W + EPS
            or p.z + p.height > H + EPS
        ):
            issues.append(ValidationIssue(
                "error",
                "out_of_bounds",
                "货物超出集装箱内部边界。",
                p.sku_model,
                p.instance_id,
            ))

        if door_reserve_cm > EPS and p.x + p.length > usable_l + EPS:
            issues.append(ValidationIssue(
                "error",
                "door_reserve_occupied",
                f"货物进入柜门侧 {door_reserve_cm:.0f} cm 预留区，请前移或减少预留。",
                p.sku_model,
                p.instance_id,
            ))

        sku = sku_by_model.get(p.sku_model)
        if sku and sku.upright_only:
            upright = (
                abs(p.height - sku.height) <= EPS
                and (
                    (abs(p.length - sku.length) <= EPS and abs(p.width - sku.width) <= EPS)
                    or (abs(p.length - sku.width) <= EPS and abs(p.width - sku.length) <= EPS)
                )
            )
            if not upright:
                issues.append(ValidationIssue(
                    "error",
                    "bad_orientation",
                    "货物要求直立，但当前摆放改变了高度方向。",
                    p.sku_model,
                    p.instance_id,
                ))

        if p.z > EPS:
            footprint = p.length * p.width
            supported = _support_area(p, placed)
            if supported + EPS < footprint:
                issues.append(ValidationIssue(
                    "error",
                    "unsupported",
                    f"上层货物底面支撑不足，支撑面积 {supported:.0f}/{footprint:.0f} cm²。",
                    p.sku_model,
                    p.instance_id,
                ))

    if check_collisions:
        for i, a in enumerate(placed):
            for b in placed[i + 1:]:
                if _overlap_volume(a, b) > EPS:
                    issues.append(ValidationIssue(
                        "error",
                        "collision",
                        f"{a.sku_model} 与 {b.sku_model} 发生空间重叠。",
                        a.sku_model,
                        a.instance_id,
                    ))
                    break

    for upper in placed:
        if upper.z <= EPS:
            continue
        for lower in placed:
            if lower is upper:
                continue
            if abs(lower.z + lower.height - upper.z) > EPS:
                continue
            overlap_area = (
                _overlap_1d(upper.x, upper.x + upper.length, lower.x, lower.x + lower.length)
                * _overlap_1d(upper.y, upper.y + upper.width, lower.y, lower.y + lower.width)
            )
            if overlap_area <= EPS:
                continue
            lower_sku = sku_by_model.get(lower.sku_model)
            if lower_sku and not lower_sku.allow_stack and not lower_sku.flat_stack:
                issues.append(ValidationIssue(
                    "error",
                    "non_stackable_support",
                    f"{upper.sku_model} 压在不可堆叠货物 {lower.sku_model} 上。",
                    upper.sku_model,
                    upper.instance_id,
                ))

    if (
        placed
        and total_weight > max_kg * 0.2
        and L > EPS
        and balance_warn_pct > 0
    ):
        center_x = sum((p.x + p.length / 2) * p.weight for p in placed) / total_weight
        center_pct = center_x / L * 100
        if abs(center_pct - 50) > balance_warn_pct:
            issues.append(ValidationIssue(
                "warning",
                "weight_balance",
                f"整柜重心位于柜长 {center_pct:.1f}% 处，偏离中部较多，请复核轴荷/偏载风险。",
            ))
        if W > EPS:
            center_y = sum((p.y + p.width / 2) * p.weight for p in placed) / total_weight
            center_y_pct = center_y / W * 100
            if abs(center_y_pct - 50) > balance_warn_pct:
                issues.append(ValidationIssue(
                    "warning",
                    "lateral_weight_balance",
                    f"整柜横向重心位于柜宽 {center_y_pct:.1f}% 处，左右偏载较明显，请复核装车稳定性。",
                ))

    return issues


def issues_to_dicts(issues: list[ValidationIssue]) -> list[dict]:
    return [issue.to_dict() for issue in issues]
