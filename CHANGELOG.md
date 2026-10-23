# Changelog

## 1.0.1

- Installer now ships `docs/DEVELOPMENT.md` alongside `docs/USAGE.md`, so README links work from the installed folder.

## 1.0.0

- First public release with a Windows installer (Inno Setup), installed per user without a separate Python.
- Added `--self-test`: starts the local server, requests the index page, and checks that the render chain is bundled; writes `%TEMP%\ContainerPack-self-test.log`. The installer runs it after copying files.
- Added `installer/ContainerPack.iss`; creates Start menu shortcuts, an uninstaller, and an optional desktop shortcut.
- README rewritten for public readers; the workbench operation manual moved to `docs/USAGE.md` and the productization log to `docs/DEVELOPMENT.md`.
- Added MIT license and third-party notices.

## 0.45.0

- Added browser-local auto draft persistence for the workbench.
- Users can restore the latest local draft after a refresh or accidental close, or clear the saved draft without clearing the current page.
- Manual project save/open and auto draft now share the same project payload path.
- Browser smoke now verifies that auto draft storage is written after sample packing.

## 0.44.0

- Added `text_quality.py` to scan project text files for common mojibake and non-UTF-8 content.
- Preflight now runs the text-quality gate before tests and API smoke checks.
- Browser smoke now also checks rendered page text for mojibake.
- Added regression coverage for the mojibake detector.

## 0.43.0

- Added `browser_smoke.py` as a real-browser UI smoke test.
- The smoke flow starts a local app server when needed, opens Chromium, fills sample cargo, runs auto packing, verifies rendered cargo and stats, drags workbench splitters, and checks layout persistence.
- Added optional `preflight.py --browser-smoke` integration for stricter release checks.
- Added `requirements-dev.txt` for browser-test dependencies without expanding normal runtime requirements.

## 0.42.0

- Added horizontal resize handles inside the center workbench.
- Users can now drag the toolbar/canvas and canvas/stats boundaries to tune the main editing area.
- Center toolbar and stats heights are saved with the existing browser-local layout memory and reset by the reset layout button.
- Updated page contract coverage and usage docs for the expanded resizable layout.

## 0.41.0

- Added quick-fix actions to the validation issue panel.
- Issue cards can now locate the affected carton and offer targeted repairs for collision, out-of-bounds, door-reserve, unsupported, non-stackable-support, and top-load issues.
- Quick fixes preserve undo history, activity logging, selection focus, and validation refresh.
- Added page contract coverage for the new issue quick-fix controls.

## 0.40.0

- Added an internal CAD placement clipboard for copying selected cargo layouts.
- Users can paste copied placement patterns from the inspector or with `Ctrl+V`; `Ctrl+C` copies the current selection.
- Pasted cartons receive fresh instance IDs and are limited by the remaining quantity in the cargo manifest.
- The paste workflow selects the newly created cartons so users can immediately drag, nudge, lock, or paste again.
- Added page contract coverage for the copy/paste placement controls and keyboard shortcuts.

## 0.39.0

- Added CAD multi-select tools for snapping selected cargo to the container head and centerline.
- Added numeric X/Y spacing distribution so selected cargo can be arranged with a specific edge-to-edge gap.
- Numeric spacing now warns instead of applying a distorted layout when the requested group span exceeds the container interior.
- Updated page contract coverage for the new multi-select arrangement controls.

## 0.38.0

- Added draggable workbench splitters so users can resize the cargo list, canvas, and right-side review area.
- Added per-panel height resizing for the left and right sidebars, with browser-local layout memory and a reset layout button.
- Added custom view presets that save the current view direction, layer filter, highlight mode, and zoom window.
- Project files now save as version 9 to preserve custom view presets alongside measurement annotations.
- Added page contract coverage for resizable workbench controls and the version 9 project schema.

## 0.37.0

- Added current-layer repacking from the CAD toolbar.
- The workbench can now repack only the selected Z layer on its existing plane while temporarily fixing every other layer.
- Same-layer repacking skips candidate positions that do not have full bottom support.
- Current-layer repacking preserves original locked states after the repack completes and keeps the layer filter active for review.
- Repacking a layer with cargo above it now requires confirmation because support relationships must be reviewed afterward.
- Added regression coverage for layer repack controls and locked layer preservation.

## 0.36.0

- Added a right-side measurement annotation panel for saved CAD measurement lines.
- Saved measurements can now be named, annotated with notes, focused in the canvas, and deleted one by one.
- HTML reports now include measurement names and notes.
- Project files now save as version 8 to preserve measurement annotation metadata.
- Added a page contract test for the measurement annotation panel and version 8 project schema.

## 0.35.0

- Added saved CAD measurement annotations on top of the temporary measurement tool.
- Saved measurement annotations are drawn on the workbench, persisted in `.cpack` project files, and included in HTML reports.
- Fixed the center CAD toolbar wrapping so overflowing controls remain clickable instead of overlapping the top toolbar.
- Project files now save as version 7 to preserve measurement annotations.
- Added a page contract test for saved measurement controls and rendering support.

## 0.34.0

- Added temporary CAD dimension overlays for selected cartons and selected groups.
- Top view shows length/width dimensions, while side view shows length/height dimensions.
- Official report snapshots now clear temporary selection and dimension overlays before embedding SVGs.
- Added a page contract test for dimension overlay support.

## 0.33.0

- Added CAD-style multi-select distribution and edge-snapping tools.
- Multi-select inspector now supports equal spacing on X/Y plus snap left, snap right, and snap to door-side safe line.
- Distribution and snap actions preserve undo history, activity logging, and validation refresh.
- Added a page contract test for the new distribution controls.

## 0.32.0

- Added `preflight.py` as a repeatable product self-check command.
- Preflight covers source compilation, unit tests, homepage UTF-8, manifest import, packing, validation, template export, and workbook export smoke checks.
- Added `--strict-render` mode to fail when PNG rendering dependencies are unavailable.
- Windows packaging now runs strict preflight before building the exe.
- Added a regression test for the preflight API smoke path.

## 0.31.0

- Added quick view presets for bottom layer, top layer, and door-side focus.
- View presets update the active view, layer filter, and canvas zoom without changing cargo placement data.
- Preset changes are recorded in the activity log for handoff traceability.
- Added a page contract test for the preset controls.

## 0.30.0

- Added current-layer operations to the CAD workbench.
- Users can select, lock, or unlock all currently visible layer items from the top canvas toolbar.
- Layer lock operations record activity, mark the plan as manually reviewed, and keep undo history.
- Added a page contract test for the layer operation controls.

## 0.29.0

- Added a cargo import preview panel before rows are appended to the workbench.
- Import preview now shows sample valid rows plus error and warning messages.
- Users can confirm appending valid rows or cancel the preview without changing the cargo table.
- Added a page contract test to protect the import preview controls.

## 0.28.0

- Added a downloadable `.xlsx` cargo manifest template.
- The template includes a blank cargo sheet, field documentation, and a separate example sheet so example rows are not imported by accident.
- Added frontend "下载模板" action and backend `/api/import_template`.
- Added a regression test to verify the template is a valid workbook and imports as an empty manifest.

## 0.27.0

- Added cargo manifest import for CSV, TXT, TSV, and `.xlsx` files.
- Import parsing now recognizes common Chinese and English headers for SKU, supplier, arrival order, dimensions, weight, quantity, top-load limit, stack rule, side-placement allowance, and notes.
- Invalid manifest rows are reported without being appended to the cargo table.
- The workbench now has a "导入清单" action with import feedback and operation logging.
- Added regression tests for Chinese CSV import, `.xlsx` import, and invalid row handling.

## 0.26.0

- Added Excel workbook export from the workbench.
- Added `/api/export_workbook`, returning a valid `.xlsx` package with summary, cargo, placement, validation, weight segment, unfitted, and activity sheets.
- Excel exports now preserve project metadata, safety conclusion, locked placement state, and operation records.
- Added a backend contract test that opens the generated workbook as an OOXML zip package.

## 0.25.0

- Added project revision, reviewer, and on-site confirmer fields to project metadata.
- Safety summaries now keep plans in "needs review" when key handoff metadata is missing.
- HTML reports now include revision and sign-off fields in the project information section.
- Project files now save as version 6 to preserve the expanded handoff metadata.

## 0.24.0

- Added a safety summary that classifies plans as deliverable, needs review, or not deliverable.
- The workbench stats now show the safety conclusion before utilization and weight metrics.
- HTML reports now include the safety conclusion and review points near the top.
- Report export activity records now include the safety conclusion at export time.

## 0.23.0

- Added a right-side activity log panel for workflow and manual-edit traceability.
- Logged automatic packing, drag edits, coordinate edits, rotation, lock toggles, deletion, nudges, alignment, unlocked repacking, validation, exports, save/open, clear, and recognized input appends.
- Project files now save as version 5 and preserve the latest 200 activity records.
- HTML reports now include the latest activity records after the workflow section.

## 0.22.0

- Explicitly serve the workbench HTML as `text/html; charset=utf-8`.
- Added UTF-8 source headers to Python files that contain Chinese UI copy.
- Added `.editorconfig` to keep project files opened and saved as UTF-8.
- Added a regression test for the index page charset and UTF-8 title bytes.

## 0.21.0

- Added SKU-level `max_top_load_kg` for maximum allowed top load per carton.
- Validation now reports `top_load_exceeded` when cumulative load transmitted from upper cartons exceeds a lower carton's SKU limit.
- Local unlocked repacking rejects candidates that would violate top-load limits.
- Workbench cargo rows now include an "上压" field, and HTML reports include SKU top-load limits.
- Project files now save as version 4 to preserve the expanded cargo-row schema.
- Added regression tests for top-load validation and API contract handling.

## 0.20.0

- Added configurable segment weight limits across six container-length segments.
- `/api/pack`, `/api/validate_plan`, `/api/render_plan`, and `/api/repack_unlocked` now accept `max_segment_weight_kg`.
- Validation now reports `segment_overweight` when any segment exceeds the configured limit.
- Workbench project files now preserve the segment weight limit.
- Workbench stats and HTML reports display the segment limit when configured.
- Added regression tests for segment overweight validation and API contract handling.

## 0.19.0

- Added a CAD-style measurement mode in the workbench canvas.
- Measurement mode draws a temporary distance line and reports total distance plus X/Y or X/Z deltas.
- Added `M` as a keyboard shortcut for measurement mode and Esc to exit.
- Official HTML report snapshots omit temporary measurement overlays.

## 0.18.0

- Added report-export preflight confirmation for unresolved errors, review warnings, or missing handoff metadata.
- Report export can still proceed after explicit human confirmation, preserving operator control.

## 0.17.0

- Added CAD-style edge snapping while dragging placements.
- Dragging now keeps a 5 cm grid feel but precisely snaps near container walls, floor/top edges, and visible carton edges.
- Added snap guide lines in the SVG workbench.
- Updated the center toolbar hint to describe snapping behavior.
- Placement inspector fields now show zero coordinates as `0` instead of blank values.

## 0.16.0

- Added a workflow status panel for list readiness, draft generation, manual review, validation, and handoff readiness.
- Manual placement edits now mark the plan as manually reviewed/adjusted.
- Project files now preserve the manual review marker.
- HTML reports now include workflow status for handoff review.

## 0.15.0

- Added project metadata fields for plan name, container/truck number, prepared-by, and notes.
- Project files now preserve project metadata.
- HTML reports now use the plan name as the report title when provided.
- HTML reports now include a project information section for handoff and archiving.

## 0.2.0

- Reworked the app into a local container loading workbench.
- Added editable placement data returned from `/api/pack`.
- Added `/api/validate_plan` for manual layout validation.
- Added `/api/render_plan` for exporting adjusted layouts.
- Added `_validator.py` with checks for bounds, collisions, support, weight, and non-stackable supports.
- Fixed flat-stack platform support so partially filled footprints no longer create floating space.
- Removed the hardcoded DashScope API key fallback.
- Added input and extraction schema limits.
- Moved the new frontend into `_frontend.py`.
- Added unit tests for packer regressions, validation rules, and API contracts.

## 0.3.0

- Added multi-select, box select, batch move, batch rotate, batch lock, and keyboard nudging.
- Added quantity validation for unknown, over-placed, and missing SKUs.
- Added partial repacking with `/api/repack_unlocked`.
- Added the "重排未锁定" workflow in the workbench.
- Added CSV placement-detail export.
- Added HTML loading-plan report export.
- Added SKU/supplier highlighting in the workbench canvas.
- Added multi-selection alignment tools: align X, align Y, and set Z to floor.

## 0.4.0

- Added a door-reserve rule that reduces auto-pack usable length and flags manual placements in the reserved door zone.
- Added door-reserve support to `/api/pack`, `/api/validate_plan`, `/api/render_plan`, and `/api/repack_unlocked`.
- Added reserve-zone visualization in the SVG top/side workbench.
- Added center-of-gravity X, front/rear weight stats, and a weight-balance warning.
- Added door reserve, center-of-gravity, and front/rear weight to HTML reports.
- Fixed 1280px workbench layout clipping by restructuring the top action bar and constraining the center canvas column.
- Added regression tests for door reserve, balance warnings, and pack API reserve behavior.

## 0.5.0

- Added CAD-style canvas view controls: zoom in, zoom out, fit to container, and zoom percentage.
- Added mouse-wheel zoom centered on the pointer.
- Added Alt-drag canvas panning without moving placed cartons.
- Added SVG rulers for top and side views.
- Added live coordinate readout for X/Y in top view and X/Z in side view.
- Reworked the center tool strip into a wrapped two-line toolbar to avoid clipping and right-panel overlap.

## 0.6.0

- Added canvas issue highlighting for validation findings that can be mapped to a specific carton.
- Error cartons now render with a red stroke and warning cartons with a yellow stroke.
- Added SVG hover titles on issue cartons with the validation message.

## 0.7.0

- Added lightweight live drag feedback for collisions while moving cartons.
- Added live drag feedback when a carton enters the configured door-reserve zone.
- Kept backend validation as the final source of truth after drop.

## 0.8.0

- Added drag delta readout while moving cartons.
- Top view shows ΔX/ΔY and side view shows ΔX/ΔZ.

## 0.9.0

- Embedded the current SVG loading plan in HTML reports.
- Added report-side SVG styling for containers, cartons, reserve zones, rulers, and issue highlights.

## 0.10.0

- Added loading-sequence playback controls in the workbench.
- Added previous/next/all controls and a step slider for showing the first N cartons.
- Added a step stat card for current playback progress.
- Added loading order to CSV exports and HTML report placement details.

## 0.11.0

- Added staged loading snapshots to HTML reports.
- Reports now include 25%, 50%, 75%, and 100% loading views when placements exist.
- Report export now serializes the full loading plan even if the workbench is currently in sequence playback mode.

## 0.12.0

- Added six-segment weight distribution stats along the container length.
- Added max segment weight to the workbench stats.
- Added segment weight rows to HTML reports.

## 0.13.0

- Added lateral center-of-gravity stats.
- Added left/right half-container weight stats to the workbench and HTML report.
- Added lateral weight-balance validation warnings.

## 0.14.0

- Added Z-layer filtering in the workbench canvas.
- Added a layer selector that lists available placement heights.
- Added layer status to the stats bar.
- Project files now preserve the current layer filter.
- HTML report export restores all layers before serializing official plan snapshots.
