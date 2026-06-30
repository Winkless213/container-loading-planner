import base64
import io
import unittest
import zipfile

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app


class AppContractTest(unittest.TestCase):
    def test_index_serves_utf8_html(self):
        response = TestClient(app.app).get("/")

        self.assertEqual(200, response.status_code)
        self.assertIn("charset=utf-8", response.headers["content-type"].lower())
        self.assertIn("\u88c5\u67dc\u5de5\u4f5c\u53f0".encode("utf-8"), response.content)

    def test_index_contains_import_preview_controls(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("导入预览", text)
        self.assertIn("追加有效行", text)
        self.assertIn("取消预览", text)

    def test_index_contains_layer_operation_controls(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("选本层", text)
        self.assertIn("锁本层", text)
        self.assertIn("解本层", text)
        self.assertIn("重排本层", text)
        self.assertIn("repackCurrentLayer", text)
        self.assertIn("repackLayerPlane", text)
        self.assertIn("必须复核校验结果", text)

    def test_index_contains_view_preset_controls(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("底层", text)
        self.assertIn("上层", text)
        self.assertIn("门口", text)
        self.assertIn("btn-save-view", text)
        self.assertIn("view-preset-list", text)
        self.assertIn("customViewPresets", text)
        self.assertIn("applyCustomViewPreset", text)

    def test_index_contains_resizable_workbench_layout(self):
        text = TestClient(app.app).get("/").text

        self.assertIn('id="split-left"', text)
        self.assertIn('id="split-right"', text)
        self.assertIn("btn-reset-layout", text)
        self.assertIn("container-pack-layout-v1", text)
        self.assertIn("startColumnResize", text)
        self.assertIn("startPanelResize", text)
        self.assertIn("startCenterResize", text)
        self.assertIn("panel-resizer", text)
        self.assertIn('id="split-center-tools"', text)
        self.assertIn('id="split-center-bottom"', text)
        self.assertIn("--strip-h", text)
        self.assertIn("--bottom-h", text)

    def test_index_contains_auto_draft_recovery(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("btn-restore-draft", text)
        self.assertIn("btn-clear-draft", text)
        self.assertIn("container-pack-autodraft-v1", text)
        self.assertIn("projectPayload", text)
        self.assertIn("saveAutoDraftNow", text)
        self.assertIn("restoreAutoDraft", text)
        self.assertIn("clearAutoDraft", text)
        self.assertIn("beforeunload", text)

    def test_index_uses_bounded_wrapping_canvas_toolbar(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("grid-template-rows:var(--strip-h,110px) 6px minmax(180px,1fr) 6px var(--bottom-h,128px)", text)
        self.assertIn("max-height:230px", text)
        self.assertIn("align-content:flex-start", text)

    def test_index_contains_distribution_controls(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("等距 X", text)
        self.assertIn("等距 Y", text)
        self.assertIn("贴左", text)
        self.assertIn("贴右", text)
        self.assertIn("贴柜头", text)
        self.assertIn("贴门口", text)
        self.assertIn("贴中线", text)
        self.assertIn("X 间距(cm)", text)
        self.assertIn("Y 间距(cm)", text)
        self.assertIn("按间距 X", text)
        self.assertIn("按间距 Y", text)
        self.assertIn("distributeSelectionByGap", text)
        self.assertIn("复制摆放", text)
        self.assertIn("粘贴摆放", text)
        self.assertIn("placementClipboard", text)
        self.assertIn("copyPlacementSelection", text)
        self.assertIn("pastePlacementClipboard", text)
        self.assertIn('key.toLowerCase()==="c"', text)
        self.assertIn('key.toLowerCase()==="v"', text)

    def test_index_contains_dimension_overlay_support(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("svg-dim-label", text)
        self.assertIn("renderSelectionDimensions", text)

    def test_index_contains_issue_quick_fix_actions(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("issue-actions", text)
        self.assertIn("issueFixKinds", text)
        self.assertIn("fixIssue", text)
        self.assertIn("快速修复", text)
        self.assertIn("移出门口", text)
        self.assertIn("拉回柜内", text)
        self.assertIn("前移 5cm", text)
        self.assertIn("后移 5cm", text)
        self.assertIn("落地", text)

    def test_index_contains_saved_measurement_support(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("保存测距", text)
        self.assertIn("清除标注", text)
        self.assertIn("savedMeasurements", text)
        self.assertIn("svg-saved-measure-label", text)

    def test_index_contains_measurement_annotation_panel_and_version_schema(self):
        text = TestClient(app.app).get("/").text

        self.assertIn("measurement-list", text)
        self.assertIn("标注名", text)
        self.assertIn("备注", text)
        self.assertIn("normalizedMeasurements", text)
        self.assertIn("version:9", text)
        self.assertIn("normalizedViewPresets(d.customViewPresets)", text)

    def test_extracted_skus_are_normalized_and_limited(self):
        data = app._normalize_extracted_skus({
            "model": "A",
            "length": "10",
            "width": 20,
            "height": 30,
            "weight": 4,
            "qty": 5,
            "stack_mode": "flat",
            "note": "checked",
            "ignored": "value",
        })
        self.assertEqual("A", data[0]["model"])
        self.assertEqual(10.0, data[0]["length"])
        self.assertEqual("flat", data[0]["stack_mode"])
        self.assertNotIn("ignored", data[0])

    def test_extracted_skus_reject_unknown_stack_mode(self):
        with self.assertRaises(HTTPException):
            app._normalize_extracted_skus({"model": "A", "stack_mode": "maybe"})

    def test_import_manifest_csv_maps_chinese_headers(self):
        content = (
            "型号,厂家,序,长,宽,高,重,上压,箱,规则,侧放\n"
            "SKU-A,工厂一,2,120cm,80,60,25kg,50,10,平,是\n"
        ).encode("gb18030")

        data = app._parse_manifest_file_bytes("清单.csv", content)
        sku = data["skus"][0]

        self.assertEqual(1, len(data["skus"]))
        self.assertEqual("SKU-A", sku["model"])
        self.assertEqual("工厂一", sku["supplier"])
        self.assertEqual(2, sku["arrival_order"])
        self.assertEqual(120.0, sku["length"])
        self.assertEqual(50.0, sku["max_top_load_kg"])
        self.assertEqual(10, sku["qty"])
        self.assertEqual("flat", sku["stack_mode"])
        self.assertFalse(sku["upright_only"])
        self.assertEqual(0, data["summary"]["error_count"])

    def test_import_manifest_xlsx_reads_first_sheet(self):
        workbook = app._build_xlsx([("清单", [
            ["SKU", "Length", "Width", "Height", "Weight", "Qty"],
            ["SKU-B", 100, 90, 70, 30, 5],
        ])])

        data = app._parse_manifest_file_bytes("manifest.xlsx", workbook)

        self.assertEqual(1, len(data["skus"]))
        self.assertEqual("SKU-B", data["skus"][0]["model"])
        self.assertEqual(5, data["skus"][0]["qty"])

    def test_import_template_is_valid_xlsx_and_imports_empty(self):
        response = app.api_import_template()
        workbook = base64.b64decode(response["xlsx_base64"])

        self.assertTrue(response["filename"].endswith(".xlsx"))
        with zipfile.ZipFile(io.BytesIO(workbook)) as zf:
            workbook_xml = zf.read("xl/workbook.xml").decode("utf-8")
        self.assertIn("货物清单", workbook_xml)
        self.assertIn("字段说明", workbook_xml)
        self.assertIn("填写示例", workbook_xml)

        parsed = app._parse_manifest_file_bytes(response["filename"], workbook)
        self.assertEqual([], parsed["skus"])
        self.assertEqual(0, parsed["summary"]["error_count"])

    def test_import_manifest_reports_invalid_rows_without_importing_them(self):
        content = "型号,长,宽,高,重,箱\nSKU-B,100,,70,30,5\n".encode("utf-8")

        data = app._parse_manifest_file_bytes("bad.csv", content)

        self.assertEqual([], data["skus"])
        self.assertEqual(1, data["summary"]["error_count"])
        self.assertIn("缺少必填字段", data["issues"][0]["message"])

    def test_pack_request_rejects_extreme_quantity(self):
        with self.assertRaises(ValidationError):
            app.PackRequest.model_validate({
                "container_type": "40HQ",
                "skus": [{
                    "model": "A",
                    "length": 10,
                    "width": 10,
                    "height": 10,
                    "weight": 1,
                    "qty": app.MAX_QTY_PER_SKU + 1,
                }],
            })

    def test_total_carton_limit_is_enforced(self):
        skus = [
            app.SKU("A", "A", 10, 10, 10, 1, app.MAX_TOTAL_CARTONS),
            app.SKU("B", "B", 10, 10, 10, 1, 1),
        ]
        with self.assertRaises(HTTPException):
            app._ensure_pack_size(skus)

    def test_pack_returns_layout_even_when_png_renderer_is_missing(self):
        old_renderer = app._render_loading_plan

        def missing_renderer(*args, **kwargs):
            raise HTTPException(500, "missing renderer")

        app._render_loading_plan = missing_renderer
        try:
            req = app.PackRequest.model_validate({
                "container_type": "20GP",
                "skus": [{
                    "model": "A",
                    "length": 100,
                    "width": 100,
                    "height": 100,
                    "weight": 10,
                    "qty": 1,
                }],
            })
            data = app.api_pack(req)
        finally:
            app._render_loading_plan = old_renderer

        self.assertEqual("missing renderer", data["render_error"])
        self.assertEqual(1, len(data["placements"]))
        self.assertEqual([], data["validation"])

    def test_pack_respects_door_reserve(self):
        req = app.PackRequest.model_validate({
            "container_type": "20GP",
            "door_reserve_cm": 300,
            "skus": [{
                "model": "A",
                "length": 180,
                "width": 100,
                "height": 80,
                "weight": 100,
                "qty": 1,
            }],
        })
        data = app.api_pack(req)
        usable_length = app.CONTAINERS["20GP"]["L"] - 300

        self.assertEqual(300, data["stats"]["door_reserve_cm"])
        self.assertEqual([], [i for i in data["validation"] if i["code"] == "door_reserve_occupied"])
        self.assertTrue(all(p["x"] + p["length"] <= usable_length + app.EPS for p in data["placements"]))

    def test_stats_include_weight_segments(self):
        spec = {"L": 600, "W": 200, "H": 200, "max_kg": 1000, "name": "test"}
        placed = [
            app.PlacedItem("A", 1, 0, 0, 0, 50, 50, 50, 100, "#000", False),
            app.PlacedItem("A", 2, 520, 0, 0, 50, 50, 50, 200, "#000", False),
        ]
        stats = app._stats_for_plan(
            [app.SKU("A", "A", 50, 50, 50, 100, 2)],
            placed,
            [],
            spec,
            "TEST",
            "manual",
            "manual",
        )

        self.assertEqual(6, len(stats["weight_segments"]))
        self.assertEqual(100, stats["weight_segments"][0]["weight_kg"])
        self.assertEqual(200, stats["weight_segments"][-1]["weight_kg"])
        self.assertEqual(200, stats["max_segment_weight_kg"])
        self.assertEqual(300, stats["left_weight_kg"])
        self.assertEqual(0, stats["right_weight_kg"])
        self.assertIn("center_y_pct", stats)

    def test_validate_plan_applies_segment_weight_limit(self):
        req = app.ValidatePlanRequest.model_validate({
            "container_type": "20GP",
            "max_segment_weight_kg": 50,
            "skus": [{
                "model": "A",
                "length": 100,
                "width": 100,
                "height": 50,
                "weight": 80,
                "qty": 1,
            }],
            "placements": [{
                "sku_model": "A",
                "instance_id": 1,
                "x": 0,
                "y": 0,
                "z": 0,
                "length": 100,
                "width": 100,
                "height": 50,
                "weight": 80,
                "color": "#000000",
                "rotated": False,
            }],
        })
        data = app.api_validate_plan(req)
        self.assertIn("segment_overweight", {issue["code"] for issue in data["validation"]})

    def test_validate_plan_applies_sku_top_load_limit(self):
        req = app.ValidatePlanRequest.model_validate({
            "container_type": "20GP",
            "skus": [
                {
                    "model": "BASE",
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 20,
                    "qty": 1,
                    "max_top_load_kg": 50,
                },
                {
                    "model": "TOP",
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 80,
                    "qty": 1,
                },
            ],
            "placements": [
                {
                    "sku_model": "BASE",
                    "instance_id": 1,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 20,
                    "color": "#000000",
                    "rotated": False,
                },
                {
                    "sku_model": "TOP",
                    "instance_id": 1,
                    "x": 0,
                    "y": 0,
                    "z": 50,
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 80,
                    "color": "#111111",
                    "rotated": False,
                },
            ],
        })
        data = app.api_validate_plan(req)
        self.assertIn("top_load_exceeded", {issue["code"] for issue in data["validation"]})

    def test_repack_unlocked_keeps_locked_items_and_places_remaining(self):
        req = app.RepackUnlockedRequest.model_validate({
            "container_type": "20GP",
            "skus": [{
                "model": "A",
                "length": 100,
                "width": 100,
                "height": 50,
                "weight": 10,
                "qty": 2,
            }],
            "locked_placements": [{
                "sku_model": "A",
                "instance_id": 1,
                "x": 0,
                "y": 0,
                "z": 0,
                "length": 100,
                "width": 100,
                "height": 50,
                "weight": 10,
                "color": "#123456",
                "rotated": False,
            }],
        })
        data = app.api_repack_unlocked(req)
        self.assertEqual(2, len(data["placements"]))
        self.assertTrue(data["placements"][0]["locked"])
        self.assertFalse(data["placements"][1]["locked"])
        self.assertEqual([], [i for i in data["validation"] if i["severity"] == "error"])

    def test_repack_unlocked_preserves_locked_layer_positions(self):
        req = app.RepackUnlockedRequest.model_validate({
            "container_type": "20GP",
            "skus": [{
                "model": "A",
                "length": 100,
                "width": 100,
                "height": 50,
                "weight": 10,
                "qty": 3,
            }],
            "locked_placements": [
                {
                    "sku_model": "A",
                    "instance_id": 1,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 10,
                    "color": "#123456",
                    "rotated": False,
                },
                {
                    "sku_model": "A",
                    "instance_id": 2,
                    "x": 120,
                    "y": 0,
                    "z": 50,
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 10,
                    "color": "#123456",
                    "rotated": False,
                },
            ],
        })
        data = app.api_repack_unlocked(req)
        locked = {
            item["instance_id"]: item
            for item in data["placements"]
            if item["locked"]
        }

        self.assertEqual({1, 2}, set(locked))
        self.assertEqual((0, 0, 0), (locked[1]["x"], locked[1]["y"], locked[1]["z"]))
        self.assertEqual((120, 0, 50), (locked[2]["x"], locked[2]["y"], locked[2]["z"]))

    def test_repack_unlocked_reports_over_locked_counts(self):
        req = app.RepackUnlockedRequest.model_validate({
            "container_type": "20GP",
            "skus": [{
                "model": "A",
                "length": 100,
                "width": 100,
                "height": 50,
                "weight": 10,
                "qty": 1,
            }],
            "locked_placements": [
                {
                    "sku_model": "A",
                    "instance_id": 1,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 10,
                    "color": "#123456",
                    "rotated": False,
                },
                {
                    "sku_model": "A",
                    "instance_id": 2,
                    "x": 100,
                    "y": 0,
                    "z": 0,
                    "length": 100,
                    "width": 100,
                    "height": 50,
                    "weight": 10,
                    "color": "#123456",
                    "rotated": False,
                },
            ],
        })
        data = app.api_repack_unlocked(req)
        self.assertIn("over_placed", {i["code"] for i in data["validation"]})

    def test_export_workbook_returns_valid_xlsx_package(self):
        req = app.ExportWorkbookRequest.model_validate({
            "container_type": "20GP",
            "project_info": {
                "name": "测试方案",
                "containerNo": "CONT-001",
                "revision": "R1",
                "preparedBy": "Alice",
                "reviewedBy": "Bob",
                "confirmedBy": "Chen",
                "note": "交付测试",
            },
            "manual_touched": True,
            "activity_log": [{"time": "2026-06-29T10:00:00Z", "action": "导出", "detail": "测试记录"}],
            "skus": [{
                "model": "SKU-1",
                "length": 100,
                "width": 80,
                "height": 60,
                "weight": 25,
                "qty": 1,
            }],
            "placements": [{
                "sku_model": "SKU-1",
                "instance_id": 1,
                "x": 0,
                "y": 0,
                "z": 0,
                "length": 100,
                "width": 80,
                "height": 60,
                "weight": 25,
                "color": "#123456",
                "rotated": False,
                "locked": True,
            }],
        })
        data = app.api_export_workbook(req)
        workbook = base64.b64decode(data["xlsx_base64"])

        self.assertTrue(data["filename"].endswith(".xlsx"))
        self.assertEqual("可交付", data["safety"]["label"])
        self.assertEqual([], [i for i in data["validation"] if i["severity"] == "error"])
        with zipfile.ZipFile(io.BytesIO(workbook)) as zf:
            names = set(zf.namelist())
            self.assertIn("xl/workbook.xml", names)
            self.assertIn("xl/worksheets/sheet1.xml", names)
            self.assertIn("xl/worksheets/sheet7.xml", names)
            workbook_xml = zf.read("xl/workbook.xml").decode("utf-8")
            xml = "\n".join(
                zf.read(name).decode("utf-8")
                for name in names
                if name.startswith("xl/worksheets/")
            )
        self.assertIn("装柜坐标", workbook_xml)
        for expected in ("安全结论", "测试方案", "SKU-1", "导出", "是"):
            self.assertIn(expected, xml)


if __name__ == "__main__":
    unittest.main()
