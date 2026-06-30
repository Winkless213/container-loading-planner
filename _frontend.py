# -*- coding: utf-8 -*-

INDEX_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>装柜工作台</title>
<style>
:root{
  --bg:#11151a;--panel:#171d24;--panel-2:#1f2730;--panel-3:#26313b;
  --ink:#ecf2f8;--ink-2:#b8c3ce;--muted:#7f8d9a;--line:#34414d;
  --accent:#41b6e6;--accent-2:#f59e0b;--ok:#4ade80;--warn:#fbbf24;--err:#fb7185;
  --grid:#27313a;--shadow:0 18px 48px rgba(0,0,0,.28);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);font:13px/1.45 "Segoe UI","Microsoft YaHei",Arial,sans-serif;overflow:hidden}
button,input,select,textarea{font:inherit}
button{border:1px solid var(--line);background:var(--panel-2);color:var(--ink);border-radius:6px;padding:7px 10px;cursor:pointer;white-space:nowrap}
button:hover{border-color:var(--accent);background:#22313c}
button:disabled{opacity:.45;cursor:not-allowed}
button.primary{background:var(--accent);border-color:var(--accent);color:#06131a;font-weight:700}
button.ghost{background:transparent}
button.danger{border-color:#5d2c38;color:#ffc7d1}
input,select{width:100%;border:1px solid var(--line);border-radius:5px;background:#0f1419;color:var(--ink);padding:7px 8px;outline:none}
input:focus,select:focus{border-color:var(--accent)}
.app{display:grid;grid-template-rows:74px 1fr;height:100%}
.topbar{display:grid;grid-template-columns:auto minmax(0,1fr);grid-template-rows:28px 34px;align-items:center;gap:4px 14px;padding:6px 14px;border-bottom:1px solid var(--line);background:#0d1116}
.brand{display:flex;align-items:center;gap:12px;font-weight:800;letter-spacing:.02em}
.brand::before{content:"";width:24px;height:16px;border:2px solid var(--accent);box-shadow:inset 9px 0 0 rgba(65,182,230,.25)}
.toolbar{grid-column:1/-1;display:flex;align-items:center;gap:8px;min-width:0;overflow-x:auto;padding-bottom:2px}
.status{color:var(--muted);min-width:0;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.status.ok{color:var(--ok)}.status.warn{color:var(--warn)}.status.err{color:var(--err)}
.shell{display:grid;grid-template-columns:var(--left-w,520px) 6px minmax(360px,1fr) 6px var(--right-w,320px);min-height:0}
.left,.right{background:var(--panel);overflow:auto;min-width:0}
.left{border-right:1px solid var(--line)}
.right{border-left:1px solid var(--line)}
.splitter.vertical{position:relative;background:#101820;border-left:1px solid #0b1015;border-right:1px solid var(--line);cursor:col-resize;touch-action:none}
.splitter.vertical::after{content:"";position:absolute;inset:0 2px;border-radius:4px;background:rgba(65,182,230,.25);opacity:0;transition:opacity .12s}
.splitter.vertical:hover::after,.splitter.vertical.active::after{opacity:1}
.splitter.horizontal{position:relative;background:#101820;border-top:1px solid #0b1015;border-bottom:1px solid var(--line);cursor:row-resize;touch-action:none}
.splitter.horizontal::after{content:"";position:absolute;left:50%;top:50%;width:38px;height:4px;transform:translate(-50%,-50%);border-top:1px solid rgba(65,182,230,.65);border-bottom:1px solid rgba(65,182,230,.45);opacity:0;transition:opacity .12s}
.splitter.horizontal:hover::after,.splitter.horizontal.active::after{opacity:1}
.resizing-x,.resizing-y{user-select:none}
.resizing-x{cursor:col-resize}.resizing-y{cursor:row-resize}
.center{display:grid;grid-template-rows:var(--strip-h,110px) 6px minmax(180px,1fr) 6px var(--bottom-h,128px);min-width:0;overflow:hidden;background:linear-gradient(180deg,#111820,#0f1419)}
.strip{display:flex;align-items:center;align-content:flex-start;flex-wrap:wrap;gap:7px;min-width:0;width:100%;max-height:230px;overflow:auto;padding:7px 10px;border-bottom:1px solid var(--line);background:#121921}
.strip button{flex:0 0 auto}
.strip .grow{display:none}
.strip select{width:auto;flex:0 0 150px;min-width:130px;padding:6px 8px}
.strip .hint{flex:1 1 220px;min-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.zoom-label{flex:0 0 auto;color:var(--ink-2);font-family:Consolas,monospace;border:1px solid var(--line);border-radius:5px;padding:6px 8px;background:#0f1419}
.step-range{flex:1 1 150px;min-width:120px;accent-color:var(--accent);padding:0}
.step-label{flex:0 0 auto;color:var(--ink-2);font-family:Consolas,monospace;border:1px solid var(--line);border-radius:5px;padding:6px 8px;background:#0f1419}
.panel{position:relative;border-bottom:1px solid var(--line);padding:13px;min-height:90px}
.panel.resizable-panel{overflow:auto;padding-bottom:22px}
.panel-resizer{position:sticky;bottom:-13px;height:13px;margin:10px -13px -22px;border-top:1px solid var(--line);background:#101820;cursor:row-resize;touch-action:none}
.panel-resizer::after{content:"";position:absolute;left:50%;top:4px;width:34px;height:4px;transform:translateX(-50%);border-top:1px solid rgba(65,182,230,.65);border-bottom:1px solid rgba(65,182,230,.45)}
.panel-resizer:hover,.panel-resizer.active{background:#132533}
.panel h2{margin:0 0 10px;color:var(--ink-2);font-size:11px;text-transform:uppercase;letter-spacing:.16em}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.chip{min-height:54px;text-align:left}
.chip strong{display:block;font-size:14px}
.chip span{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.chip.active{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
.workflow{display:grid;gap:6px}
.flow-step{display:grid;grid-template-columns:18px 1fr;gap:8px;align-items:start;border:1px solid var(--line);border-radius:8px;background:#101820;padding:8px}
.flow-dot{width:9px;height:9px;border-radius:50%;margin-top:5px;background:var(--muted);box-shadow:0 0 0 4px rgba(127,141,154,.08)}
.flow-step b{display:block;font-size:12px}
.flow-step span{display:block;color:var(--muted);font-size:11px;margin-top:2px}
.flow-step.done{border-color:#275d3f}.flow-step.done .flow-dot{background:var(--ok);box-shadow:0 0 0 4px rgba(74,222,128,.12)}
.flow-step.warn{border-color:#645019}.flow-step.warn .flow-dot{background:var(--warn);box-shadow:0 0 0 4px rgba(251,191,36,.12)}
.flow-step.bad{border-color:#65313c}.flow-step.bad .flow-dot{background:var(--err);box-shadow:0 0 0 4px rgba(251,113,133,.12)}
.flow-step.wait{opacity:.68}
.activity-list{display:grid;gap:7px}
.activity-item{position:relative;border:1px solid var(--line);border-left-color:var(--accent);border-radius:8px;background:#101820;padding:8px 8px 8px 10px}
.activity-item b{display:block;font-size:12px}
.activity-item span{display:block;color:var(--muted);font-size:11px;margin-top:2px}
.activity-item::before{content:"";position:absolute;left:-4px;top:12px;width:7px;height:7px;border-radius:50%;background:var(--accent)}
.measure-list{display:grid;gap:8px}
.measure-card{border:1px solid var(--line);border-radius:8px;background:#101820;padding:8px}
.measure-card .measure-meta{color:var(--muted);font-size:11px;margin:5px 0 7px}
.measure-card label{display:block;color:var(--muted);font-size:10px;margin:6px 0 3px}
.measure-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}
.measure-actions button{padding:5px 8px;font-size:12px}
.preset-list{display:grid;gap:8px}
.preset-card{border:1px solid var(--line);border-radius:8px;background:#101820;padding:8px}
.preset-card .preset-meta{color:var(--muted);font-size:11px;margin:5px 0 7px}
.preset-card label{display:block;color:var(--muted);font-size:10px;margin:6px 0 3px}
.preset-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}
.preset-actions button{padding:5px 8px;font-size:12px}
.hint{color:var(--muted);font-size:12px;margin-top:8px}
.import-preview{display:none;margin-top:10px;border:1px solid var(--line);border-radius:8px;background:#101820;padding:10px}
.import-preview.show{display:block}
.import-preview-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}
.import-preview-head b{font-size:12px;color:var(--ink-2)}
.import-preview-summary{color:var(--muted);font-size:11px}
.import-preview .table-wrap{max-height:180px}
.import-preview table{min-width:560px}
.import-issues{display:grid;gap:5px;margin-top:8px}
.import-issue{border:1px solid var(--line);border-radius:6px;padding:6px 7px;color:var(--muted);font-size:11px;background:#0f1419}
.import-issue.error{border-color:#63313c;color:#ffc7d1}
.import-issue.warning{border-color:#604b1d;color:#ffe8a3}
.drop{position:relative;border:1px dashed var(--line);border-radius:8px;padding:14px;color:var(--ink-2);background:#111820;text-align:center}
.drop.drag{border-color:var(--accent);background:#102332}
.drop input{position:absolute;inset:0;opacity:0;cursor:pointer}
.table-wrap{border:1px solid var(--line);border-radius:8px;overflow:auto;background:#0f1419}
.table-wrap table{min-width:680px}
table{width:100%;border-collapse:collapse;table-layout:fixed}
th{background:#151c23;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.08em;text-align:left;padding:7px 4px;border-bottom:1px solid var(--line)}
td{padding:3px;border-bottom:1px solid #202932;vertical-align:middle}
td input{padding:6px 3px;border-color:transparent;background:transparent}
td input:focus{background:#111f2a;border-color:var(--accent)}
.row-actions{display:flex;gap:2px}
.mini{padding:5px 5px;font-size:11px}
.mode-on{border-color:var(--accent);color:var(--accent)}
.mode-flat.mode-on{border-color:var(--accent-2);color:var(--accent-2)}
.mode-none.mode-on{border-color:var(--err);color:var(--err)}
.canvas-wrap{position:relative;min-width:0;min-height:0;width:100%;overflow:hidden}
#plan-svg{width:100%;height:100%;display:block;background:#0b1015;touch-action:none}
.svg-grid{stroke:var(--grid);stroke-width:1}
.svg-container{fill:#0e151b;stroke:#d6e4f0;stroke-width:3}
.svg-item{stroke:#091117;stroke-width:1;cursor:grab}
.svg-item.selected{stroke:#fff;stroke-width:3}
.svg-item.locked{stroke-dasharray:6 4;opacity:.72}
.svg-item.issue-error{stroke:var(--err);stroke-width:4}
.svg-item.issue-warning{stroke:var(--warn);stroke-width:3}
.svg-item.live-error{stroke:#ff2d55;stroke-width:5}
.svg-label{fill:#f8fbff;font-size:12px;font-weight:700;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,.9)}
.svg-floor{stroke:var(--accent-2);stroke-width:2;stroke-dasharray:8 6}
.svg-reserve{fill:rgba(251,113,133,.16);stroke:var(--err);stroke-width:2;stroke-dasharray:10 6;pointer-events:none}
.svg-reserve-label{fill:#ffd7df;font-size:13px;font-weight:800;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,.9)}
.svg-ruler{stroke:#526273;stroke-width:1;pointer-events:none}
.svg-ruler-label{fill:#8fa1b2;font-size:11px;pointer-events:none}
.svg-snap-guide{stroke:var(--accent);stroke-width:2;stroke-dasharray:7 5;pointer-events:none}
.svg-measure{stroke:var(--accent-2);stroke-width:3;stroke-dasharray:9 6;pointer-events:none}
.svg-measure-point{fill:var(--accent-2);stroke:#0b1015;stroke-width:2;pointer-events:none}
.svg-measure-label{fill:#ffe8b0;font-size:13px;font-weight:800;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,.9)}
.svg-saved-measure{stroke:#41b6e6;stroke-width:2;stroke-dasharray:7 5;pointer-events:none}
.svg-saved-measure-point{fill:#41b6e6;stroke:#0b1015;stroke-width:2;pointer-events:none}
.svg-saved-measure-label{fill:#d7f5ff;font-size:12px;font-weight:800;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,.9)}
.svg-dim{stroke:#d8eefb;stroke-width:2;stroke-dasharray:5 4;pointer-events:none}
.svg-dim-tick{stroke:#d8eefb;stroke-width:2;pointer-events:none}
.svg-dim-label{fill:#e8f8ff;font-size:12px;font-weight:800;pointer-events:none;text-shadow:0 1px 3px rgba(0,0,0,.95)}
.svg-select-box{fill:rgba(65,182,230,.16);stroke:var(--accent);stroke-width:2;stroke-dasharray:8 5;pointer-events:none}
.canvas-readout{position:absolute;left:10px;bottom:10px;border:1px solid var(--line);border-radius:6px;background:rgba(15,20,25,.86);color:var(--ink-2);padding:5px 8px;font-family:Consolas,monospace;font-size:12px;pointer-events:none}
.bottom{min-width:0;width:100%;border-top:1px solid var(--line);background:#111820;overflow:auto;padding:10px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(126px,1fr));gap:8px}
.stat{border:1px solid var(--line);border-radius:8px;background:#0f1419;padding:9px}
.stat label{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.1em}
.stat b{display:block;margin-top:3px;font-size:17px}
.stat.safety{grid-column:span 2;border-left:4px solid var(--line)}
.stat.safety b{font-size:20px}
.stat.safety.ok{border-left-color:var(--ok)}
.stat.safety.warn{border-left-color:var(--warn)}
.stat.safety.bad{border-left-color:var(--err)}
.stat.safety.wait{border-left-color:var(--muted)}
.issue{border:1px solid var(--line);border-radius:8px;padding:8px;margin-bottom:7px;background:#111820;cursor:pointer}
.issue.error{border-color:#63313c}.issue.warning{border-color:#604b1d}
.issue code{color:var(--muted)}
.issue-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}
.issue-actions button{padding:5px 8px;font-size:12px}
.empty{color:var(--muted);padding:10px;border:1px dashed var(--line);border-radius:8px}
.fields{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.field label{display:block;color:var(--muted);font-size:11px;margin-bottom:4px}
.button-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.kbd{font-family:Consolas,monospace;border:1px solid var(--line);border-radius:4px;padding:1px 5px;color:var(--ink-2);background:#0f1419}
@media(max-width:1180px){.shell{grid-template-columns:var(--left-w,420px) 6px minmax(360px,1fr)}.right,#split-right{display:none}}
</style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div class="brand">装柜工作台</div>
    <div class="toolbar">
      <button id="btn-undo">撤销</button>
      <button id="btn-redo">重做</button>
      <button id="btn-reset-layout" title="恢复默认栏宽和面板高度">重置布局</button>
      <button id="btn-save">保存项目</button>
      <button id="btn-load">打开项目</button>
      <input id="project-input" type="file" accept=".cpack,.json" hidden>
      <button id="btn-restore-draft" title="恢复本机自动保存的草稿">恢复草稿</button>
      <button id="btn-clear-draft" title="清除本机自动草稿">清草稿</button>
      <button id="btn-render">导出 PNG</button>
      <button id="btn-csv">导出 CSV</button>
      <button id="btn-xlsx">导出 Excel</button>
      <button id="btn-report">导出报告</button>
      <button id="btn-repack">重排未锁定</button>
      <button id="btn-calc" class="primary">自动排柜</button>
    </div>
    <div id="status" class="status">准备就绪</div>
  </header>
  <main class="shell">
    <aside class="left">
      <section class="panel">
        <h2>集装箱</h2>
        <div id="container-grid" class="grid4"></div>
      </section>
      <section class="panel">
        <h2>识别报价单</h2>
        <div id="drop-zone" class="drop">
          <div id="upload-label">拖入图片，或在空白处粘贴文字</div>
          <input id="file-input" type="file" accept="image/*" multiple>
        </div>
        <div class="hint">识别只负责填表，最终方案仍由人工校验确认。</div>
      </section>
      <section class="panel">
        <h2>货物清单</h2>
        <div class="table-wrap">
          <table>
            <thead><tr>
              <th style="width:72px">型号</th><th style="width:50px">厂家</th><th style="width:30px">序</th>
              <th style="width:39px">长</th><th style="width:39px">宽</th><th style="width:39px">高</th>
              <th style="width:44px">重</th><th style="width:46px">上压</th><th style="width:38px">箱</th><th style="width:96px">规则</th><th style="width:22px"></th>
            </tr></thead>
            <tbody id="items-body"></tbody>
          </table>
        </div>
        <div class="button-row">
          <button id="btn-add-row">添加一行</button>
          <button id="btn-import-manifest">导入清单</button>
          <button id="btn-template">下载模板</button>
          <input id="manifest-input" type="file" accept=".csv,.txt,.tsv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" hidden>
          <button id="btn-sample">填入示例</button>
          <button id="btn-clear" class="danger">清空</button>
        </div>
        <div id="import-feedback" class="hint"></div>
        <div id="import-preview" class="import-preview">
          <div class="import-preview-head">
            <b>导入预览</b>
            <span id="import-preview-summary" class="import-preview-summary"></span>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>型号</th><th>厂家</th><th>尺寸(cm)</th><th>重</th><th>箱</th><th>规则</th></tr></thead>
              <tbody id="import-preview-body"></tbody>
            </table>
          </div>
          <div id="import-preview-issues" class="import-issues"></div>
          <div class="button-row">
            <button id="btn-commit-import" class="primary">追加有效行</button>
            <button id="btn-cancel-import">取消预览</button>
          </div>
        </div>
        <div class="hint"><span class="kbd">叠</span> 普通可叠 <span class="kbd">平</span> 顶部可作平台 <span class="kbd">禁</span> 完全不可叠 <span class="kbd">侧</span> 可侧放</div>
      </section>
      <section class="panel">
        <h2>排柜模式</h2>
        <div id="mode-grid" class="grid3"></div>
      </section>
      <section class="panel">
        <h2>专业规则</h2>
        <div class="fields">
          <div class="field">
            <label>门口预留(cm)</label>
            <input id="door-reserve-input" type="number" min="0" max="600" step="5">
          </div>
          <div class="field">
            <label>分段限重(kg)</label>
            <input id="segment-limit-input" type="number" min="0" max="1000000" step="100">
          </div>
        </div>
        <div class="hint">预留区位于柜门侧；分段限重按柜长 6 段粗分，0 表示不限制。</div>
      </section>
      <section class="panel">
        <h2>方案信息</h2>
        <div class="fields">
          <div class="field"><label>方案名</label><input id="project-name-input" type="text"></div>
          <div class="field"><label>柜号/车号</label><input id="container-no-input" type="text"></div>
          <div class="field"><label>方案版本</label><input id="project-revision-input" type="text"></div>
          <div class="field"><label>制单人</label><input id="prepared-by-input" type="text"></div>
          <div class="field"><label>复核人</label><input id="reviewed-by-input" type="text"></div>
          <div class="field"><label>现场确认</label><input id="confirmed-by-input" type="text"></div>
          <div class="field"><label>备注</label><input id="project-note-input" type="text"></div>
        </div>
      </section>
    </aside>
    <div id="split-left" class="splitter vertical" title="拖动调整左侧栏宽度"></div>
    <section class="center">
      <div class="strip">
        <button id="view-top" class="primary">俯视</button>
        <button id="view-side">侧视</button>
        <button id="btn-validate">重新校验</button>
        <button id="zoom-out" title="缩小">−</button>
        <button id="zoom-in" title="放大">＋</button>
        <button id="zoom-fit" title="适配整柜">适配</button>
        <span id="zoom-label" class="zoom-label">100%</span>
        <button id="btn-view-bottom" title="查看最低 Z 层">底层</button>
        <button id="btn-view-top-layer" title="查看最高 Z 层">上层</button>
        <button id="btn-view-door" title="聚焦柜门侧区域">门口</button>
        <button id="btn-save-view" title="保存当前视图、层和高亮状态">存视图</button>
        <button id="measure-toggle" title="拖拽画布测量距离">测距</button>
        <button id="btn-save-measure" title="保存当前测距线">保存测距</button>
        <button id="btn-clear-measures" title="清除保存的测量标注">清除标注</button>
        <button id="step-toggle" title="按装柜顺序回放">步骤</button>
        <button id="step-prev" title="上一箱">‹</button>
        <button id="step-next" title="下一箱">›</button>
        <button id="step-all" title="显示全部">全部</button>
        <input id="step-range" class="step-range" type="range" min="0" max="0" value="0">
        <span id="step-label" class="step-label">0/0</span>
        <select id="highlight-select" title="高亮显示"></select>
        <select id="layer-select" title="按高度层显示"></select>
        <button id="btn-select-layer" title="选择当前层可见货物">选本层</button>
        <button id="btn-lock-layer" title="锁定当前层可见货物">锁本层</button>
        <button id="btn-unlock-layer" title="解锁当前层可见货物">解本层</button>
        <button id="btn-repack-layer" title="只重排当前层，其他层临时固定">重排本层</button>
        <span class="grow"></span>
        <span class="hint">拖拽移动；测距模式拖线量距离；Alt+拖拽平移。</span>
      </div>
      <div id="split-center-tools" class="splitter horizontal" title="拖动调整工具条高度"></div>
      <div class="canvas-wrap"><svg id="plan-svg" aria-label="装柜编辑画布"></svg><div id="coord-readout" class="canvas-readout">X 0 / Y 0 cm</div></div>
      <div id="split-center-bottom" class="splitter horizontal" title="拖动调整统计栏高度"></div>
      <div class="bottom">
        <div id="stats" class="stats"></div>
      </div>
    </section>
    <div id="split-right" class="splitter vertical" title="拖动调整右侧栏宽度"></div>
    <aside class="right">
      <section class="panel">
        <h2>作业流程</h2>
        <div id="workflow" class="workflow"></div>
        <div class="hint">按清单、初稿、人工复核、规则校验、交付归档推进，避免跳步出报告。</div>
      </section>
      <section class="panel">
        <h2>操作记录</h2>
        <div id="activity-log" class="activity-list"></div>
      </section>
      <section class="panel">
        <h2>测量标注</h2>
        <div id="measurement-list" class="measure-list"></div>
      </section>
      <section class="panel">
        <h2>视图预设</h2>
        <div id="view-preset-list" class="preset-list"></div>
      </section>
      <section class="panel">
        <h2>选中货物</h2>
        <div id="inspector"></div>
      </section>
      <section class="panel">
        <h2>规则校验</h2>
        <div id="issues"></div>
      </section>
    </aside>
  </main>
</div>
<script>
const NS="http://www.w3.org/2000/svg";
const EPS=1e-6;
const CONTAINERS={
  "20GP":{name:"20尺普柜",L:589,W:235,H:239,maxKg:21700,cbm:33},
  "40GP":{name:"40尺普柜",L:1203,W:235,H:239,maxKg:26500,cbm:67},
  "40HQ":{name:"40尺高柜",L:1205,W:235,H:269,maxKg:25000,cbm:76},
  "45HQ":{name:"45尺高柜",L:1358,W:235,H:269,maxKg:27600,cbm:86}
};
const CORDER=["20GP","40GP","40HQ","45HQ"];
const PACK_MODES={
  auto:{name:"自动",desc:"空间紧张时紧凑排柜，空间充裕且多厂家时分区"},
  compact:{name:"紧凑",desc:"优先提高空间利用率"},
  grouped:{name:"分厂家",desc:"按厂家和到货顺序沿柜长分布"}
};
const SAMPLE=[
  {sku:"CSL-160",supplier:"A厂",order:1,L:58,W:45,H:55,kg:22,maxTop:0,qty:75,mode:"full",side:false,note:""},
  {sku:"CC-65A",supplier:"A厂",order:1,L:50,W:40,H:35,kg:15,maxTop:0,qty:74,mode:"full",side:false,note:""},
  {sku:"M-MOTOR",supplier:"B机械厂",order:2,L:60,W:60,H:80,kg:25,maxTop:500,qty:12,mode:"flat",side:false,note:""},
  {sku:"T-50L",supplier:"C灭菌",order:3,L:55,W:55,H:85,kg:70,maxTop:0,qty:30,mode:"none",side:false,note:""}
];
const blank=()=>({sku:"",supplier:"",order:1,L:0,W:0,H:0,kg:0,maxTop:0,qty:0,mode:"full",side:false,note:""});
function projectInfoDefaults(){return {name:"",containerNo:"",revision:"R1",preparedBy:"",reviewedBy:"",confirmedBy:"",note:""}}
function withProjectInfo(info){return {...projectInfoDefaults(),...(info||{})}}
const state={containerKey:"40HQ",packMode:"auto",view:"top",highlight:"all",layerFilter:"all",doorReserve:0,maxSegmentWeight:0,projectInfo:projectInfoDefaults(),manualTouched:false,measureMode:false,measurement:null,savedMeasurements:[],customViewPresets:[],placementClipboard:null,canvasViews:{},sequenceMode:false,sequenceStep:0,items:[blank()],placements:[],selectedIndex:null,selectedIndices:[],selectionBox:null,validation:[],stats:null,lastPng:null,history:[],future:[],activityLog:[],importPreview:null};
const LAYOUT_KEY="container-pack-layout-v1";
const DRAFT_KEY="container-pack-autodraft-v1";
const DRAFT_SAVE_DELAY=650;
const LAYOUT_DEFAULTS={left:520,right:320,strip:110,bottom:128,panels:{}};
let drag=null, validateTimer=null, layoutDrag=null;
let draftTimer=null, draftReady=false, preserveExistingDraft=false;
let layoutState={left:LAYOUT_DEFAULTS.left,right:LAYOUT_DEFAULTS.right,strip:LAYOUT_DEFAULTS.strip,bottom:LAYOUT_DEFAULTS.bottom,panels:{}};

function $(id){return document.getElementById(id)}
function node(tag, cls, text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n}
function svg(tag){return document.createElementNS(NS,tag)}
function clear(n){n.replaceChildren()}
function setStatus(msg,type=""){const s=$("status");s.textContent=msg;s.className="status"+(type?" "+type:"")}
function clamp(v,min,max){return Math.max(min,Math.min(max,v))}
function projectPayload(){
  state.projectInfo=withProjectInfo(state.projectInfo);
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  state.customViewPresets=normalizedViewPresets(state.customViewPresets);
  return {version:9,projectInfo:state.projectInfo,manualTouched:state.manualTouched,containerKey:state.containerKey,packMode:state.packMode,highlight:state.highlight,layerFilter:state.layerFilter,doorReserve:state.doorReserve,maxSegmentWeight:state.maxSegmentWeight,sequenceMode:state.sequenceMode,sequenceStep:state.sequenceStep,items:state.items,placements:state.placements,view:state.view,savedMeasurements:state.savedMeasurements||[],customViewPresets:state.customViewPresets||[],activityLog:state.activityLog||[]};
}
function hasProjectContent(data=projectPayload()){
  const info=withProjectInfo(data.projectInfo);
  const defaultInfo=projectInfoDefaults();
  const hasInfo=Object.keys(defaultInfo).some(k=>String(info[k]||"")!==String(defaultInfo[k]||""));
  const hasItems=(data.items||[]).some(it=>it&&[it.sku,it.supplier,it.note,it.L,it.W,it.H,it.kg,it.qty,it.maxTop].some(v=>String(v||"").trim()&&String(v)!=="0"));
  return hasInfo||hasItems||(data.placements||[]).length||(data.savedMeasurements||[]).length||(data.customViewPresets||[]).length||(+data.doorReserve||0)>0||(+data.maxSegmentWeight||0)>0||data.manualTouched;
}
function draftTimeLabel(iso){
  const d=new Date(iso);
  return Number.isNaN(d.getTime())?"未知时间":d.toLocaleString();
}
function readAutoDraft(){
  try{
    const raw=localStorage.getItem(DRAFT_KEY);if(!raw)return null;
    const draft=JSON.parse(raw);
    if(!draft||!draft.data||!Array.isArray(draft.data.items))return null;
    return draft;
  }catch(e){return null}
}
function updateDraftButtons(){
  const draft=readAutoDraft(), restore=$("btn-restore-draft"), clearBtn=$("btn-clear-draft");
  if(restore){restore.disabled=!draft;restore.title=draft?`恢复本机自动草稿：${draftTimeLabel(draft.savedAt)}`:"暂无本机自动草稿"}
  if(clearBtn){clearBtn.disabled=!draft;clearBtn.title=draft?`清除本机自动草稿：${draftTimeLabel(draft.savedAt)}`:"暂无本机自动草稿"}
}
function saveAutoDraftNow(){
  if(!draftReady)return;
  const data=projectPayload();
  try{
    if(!hasProjectContent(data)){
      if(!preserveExistingDraft)localStorage.removeItem(DRAFT_KEY);
      updateDraftButtons();
      return;
    }
    preserveExistingDraft=false;
    localStorage.setItem(DRAFT_KEY,JSON.stringify({savedAt:new Date().toISOString(),data}));
    updateDraftButtons();
  }catch(e){
    setStatus("自动草稿保存失败，请手动保存项目。","warn");
  }
}
function scheduleAutoDraft(){
  if(!draftReady)return;
  preserveExistingDraft=false;
  clearTimeout(draftTimer);
  draftTimer=setTimeout(saveAutoDraftNow,DRAFT_SAVE_DELAY);
}
function applyProjectData(d,{activity="打开项目",detail="",status="项目已打开。",statusType="ok"}={}){
  state.projectInfo=withProjectInfo(d.projectInfo);
  state.manualTouched=!!d.manualTouched;
  state.containerKey=d.containerKey||"40HQ";
  state.packMode=d.packMode||"auto";
  state.highlight=d.highlight||"all";
  state.layerFilter=d.layerFilter||"all";
  state.doorReserve=clamp(parseFloat(d.doorReserve)||0,0,600);
  state.maxSegmentWeight=clamp(parseFloat(d.maxSegmentWeight)||0,0,1000000);
  state.items=d.items&&d.items.length?d.items:[blank()];
  state.placements=d.placements||[];
  state.view=d.view||"top";
  state.sequenceMode=!!d.sequenceMode;
  state.sequenceStep=parseInt(d.sequenceStep)||state.placements.length;
  state.savedMeasurements=normalizedMeasurements(d.savedMeasurements);
  state.customViewPresets=normalizedViewPresets(d.customViewPresets);
  state.activityLog=Array.isArray(d.activityLog)?d.activityLog.slice(-200):[];
  if(activity)recordActivity(activity,detail||`读取项目文件，版本 ${state.projectInfo.revision||"未填"}`);
  syncSequenceStep();state.canvasViews={};setSelection([]);state.history=[];state.future=[];
  renderAll();validatePlan();setStatus(status,statusType);
}
function restoreAutoDraft(){
  const draft=readAutoDraft();
  if(!draft){setStatus("暂无本机自动草稿。","warn");updateDraftButtons();return}
  if(hasProjectContent()&&!confirm("当前页面已有内容，确定用本机自动草稿覆盖？"))return;
  applyProjectData(draft.data,{activity:"恢复草稿",detail:`自动保存于 ${draftTimeLabel(draft.savedAt)}`,status:"已恢复本机自动草稿。"});
  preserveExistingDraft=false;
  saveAutoDraftNow();
}
function clearAutoDraft(){
  const draft=readAutoDraft();
  if(!draft){setStatus("暂无本机自动草稿。","warn");updateDraftButtons();return}
  if(!confirm("确定清除本机自动草稿？当前页面内容不会被清空。"))return;
  localStorage.removeItem(DRAFT_KEY);preserveExistingDraft=false;updateDraftButtons();setStatus("本机自动草稿已清除。","ok");
}
function initAutoDraft(){
  updateDraftButtons();
  const draft=readAutoDraft();
  if(draft&&!hasProjectContent()){
    if(confirm(`发现本机自动草稿（${draftTimeLabel(draft.savedAt)}），是否恢复？`)){
      applyProjectData(draft.data,{activity:"恢复草稿",detail:`自动保存于 ${draftTimeLabel(draft.savedAt)}`,status:"已恢复本机自动草稿。"});
    }else{
      preserveExistingDraft=true;
      setStatus("已保留本机自动草稿，可稍后点击“恢复草稿”。","warn");
    }
  }
  draftReady=true;
  updateDraftButtons();
  window.addEventListener("beforeunload",saveAutoDraftNow);
}
function defaultLayoutState(){return {left:LAYOUT_DEFAULTS.left,right:LAYOUT_DEFAULTS.right,strip:LAYOUT_DEFAULTS.strip,bottom:LAYOUT_DEFAULTS.bottom,panels:{}}}
function loadLayoutState(){
  try{
    const raw=localStorage.getItem(LAYOUT_KEY);if(!raw)return defaultLayoutState();
    const saved=JSON.parse(raw)||{};
    return {
      left:clamp(parseFloat(saved.left)||LAYOUT_DEFAULTS.left,340,780),
      right:clamp(parseFloat(saved.right)||LAYOUT_DEFAULTS.right,260,620),
      strip:clamp(parseFloat(saved.strip)||LAYOUT_DEFAULTS.strip,48,230),
      bottom:clamp(parseFloat(saved.bottom)||LAYOUT_DEFAULTS.bottom,72,320),
      panels:{...(saved.panels||{})}
    };
  }catch(e){return defaultLayoutState()}
}
function saveLayoutState(){try{localStorage.setItem(LAYOUT_KEY,JSON.stringify(layoutState))}catch(e){}}
function rightPaneHidden(){const n=$("split-right");return !n||getComputedStyle(n).display==="none"}
function columnMax(side){
  const shell=document.querySelector(".shell"), total=shell?shell.getBoundingClientRect().width:window.innerWidth;
  const minCenter=360, gutters=rightPaneHidden()?6:12, other=side==="left"?(rightPaneHidden()?0:layoutState.right):layoutState.left;
  return Math.max(side==="left"?340:260,total-other-gutters-minCenter);
}
function panelMaxHeight(){return Math.max(140,window.innerHeight-120)}
function centerHeight(){const center=document.querySelector(".center");return center?center.getBoundingClientRect().height:Math.max(320,window.innerHeight-74)}
function centerMaxStrip(){return Math.max(48,Math.min(230,centerHeight()-(layoutState.bottom||LAYOUT_DEFAULTS.bottom)-12-180))}
function centerMaxBottom(){return Math.max(72,centerHeight()-(layoutState.strip||LAYOUT_DEFAULTS.strip)-12-180)}
function applyLayoutState(){
  layoutState.left=clamp(layoutState.left,340,columnMax("left"));
  layoutState.right=clamp(layoutState.right,260,columnMax("right"));
  layoutState.strip=clamp(layoutState.strip||LAYOUT_DEFAULTS.strip,48,centerMaxStrip());
  layoutState.bottom=clamp(layoutState.bottom||LAYOUT_DEFAULTS.bottom,72,centerMaxBottom());
  document.documentElement.style.setProperty("--left-w",`${layoutState.left}px`);
  document.documentElement.style.setProperty("--right-w",`${layoutState.right}px`);
  document.documentElement.style.setProperty("--strip-h",`${layoutState.strip}px`);
  document.documentElement.style.setProperty("--bottom-h",`${layoutState.bottom}px`);
  document.querySelectorAll(".left .panel,.right .panel").forEach(panel=>{
    const id=panel.dataset.panelId, raw=id&&layoutState.panels?layoutState.panels[id]:0;
    if(raw)panel.style.height=`${clamp(parseFloat(raw)||0,90,panelMaxHeight())}px`;
  });
}
function ensurePanelResizers(){
  ["left","right"].forEach(side=>{
    document.querySelectorAll(`.${side} .panel`).forEach((panel,idx)=>{
      panel.dataset.panelId=`${side}-${idx}`;
      panel.classList.add("resizable-panel");
      if(panel.querySelector(".panel-resizer"))return;
      const handle=node("div","panel-resizer");
      handle.title="拖动调整本面板高度";
      handle.addEventListener("pointerdown",evt=>startPanelResize(evt,panel));
      panel.appendChild(handle);
    });
  });
}
function startColumnResize(evt,side){
  if(evt.button!==0)return;
  evt.preventDefault();
  layoutDrag={type:"column",side,startX:evt.clientX,startLeft:layoutState.left,startRight:layoutState.right,handle:evt.currentTarget};
  evt.currentTarget.classList.add("active");
  document.body.classList.add("resizing-x");
  try{evt.currentTarget.setPointerCapture(evt.pointerId)}catch(e){}
}
function startPanelResize(evt,panel){
  if(evt.button!==0)return;
  evt.preventDefault();evt.stopPropagation();
  layoutDrag={type:"panel",panel,id:panel.dataset.panelId,startY:evt.clientY,startH:panel.getBoundingClientRect().height,handle:evt.currentTarget};
  evt.currentTarget.classList.add("active");
  document.body.classList.add("resizing-y");
  try{evt.currentTarget.setPointerCapture(evt.pointerId)}catch(e){}
}
function startCenterResize(evt,section){
  if(evt.button!==0)return;
  evt.preventDefault();evt.stopPropagation();
  layoutDrag={type:"center",section,startY:evt.clientY,startStrip:layoutState.strip,startBottom:layoutState.bottom,handle:evt.currentTarget};
  evt.currentTarget.classList.add("active");
  document.body.classList.add("resizing-y");
  try{evt.currentTarget.setPointerCapture(evt.pointerId)}catch(e){}
}
function onLayoutPointerMove(evt){
  if(!layoutDrag)return;
  evt.preventDefault();
  if(layoutDrag.type==="column"){
    if(layoutDrag.side==="left")layoutState.left=clamp(layoutDrag.startLeft+evt.clientX-layoutDrag.startX,340,columnMax("left"));
    else layoutState.right=clamp(layoutDrag.startRight-(evt.clientX-layoutDrag.startX),260,columnMax("right"));
    applyLayoutState();
    return;
  }
  if(layoutDrag.type==="panel"){
    const h=clamp(layoutDrag.startH+evt.clientY-layoutDrag.startY,90,panelMaxHeight());
    layoutDrag.panel.style.height=`${h}px`;
    layoutState.panels[layoutDrag.id]=Math.round(h);
    return;
  }
  if(layoutDrag.type==="center"){
    const dy=evt.clientY-layoutDrag.startY;
    if(layoutDrag.section==="strip")layoutState.strip=Math.round(clamp(layoutDrag.startStrip+dy,48,centerMaxStrip()));
    if(layoutDrag.section==="bottom")layoutState.bottom=Math.round(clamp(layoutDrag.startBottom-dy,72,centerMaxBottom()));
    applyLayoutState();
  }
}
function endLayoutResize(){
  if(!layoutDrag)return;
  if(layoutDrag.handle)layoutDrag.handle.classList.remove("active");
  document.body.classList.remove("resizing-x","resizing-y");
  saveLayoutState();
  layoutDrag=null;
}
function resetWorkbenchLayout(){
  layoutState=defaultLayoutState();
  try{localStorage.removeItem(LAYOUT_KEY)}catch(e){}
  document.querySelectorAll(".left .panel,.right .panel").forEach(panel=>{panel.style.height=""});
  applyLayoutState();
  setStatus("布局已恢复默认。","ok");
}
function initWorkbenchLayout(){
  layoutState=loadLayoutState();
  ensurePanelResizers();
  applyLayoutState();
  $("split-left").addEventListener("pointerdown",evt=>startColumnResize(evt,"left"));
  $("split-right").addEventListener("pointerdown",evt=>startColumnResize(evt,"right"));
  $("split-center-tools").addEventListener("pointerdown",evt=>startCenterResize(evt,"strip"));
  $("split-center-bottom").addEventListener("pointerdown",evt=>startCenterResize(evt,"bottom"));
  document.addEventListener("pointermove",onLayoutPointerMove);
  document.addEventListener("pointerup",endLayoutResize);
  window.addEventListener("resize",applyLayoutState);
}
function snap(v){return Math.round(v/5)*5}
function selectedIndices(){return [...new Set((state.selectedIndices||[]).filter(i=>Number.isInteger(i)&&i>=0&&i<state.placements.length))]}
function isSelected(idx){return selectedIndices().includes(idx)}
function setSelection(indices,primary=null){const clean=[...new Set(indices.filter(i=>Number.isInteger(i)&&i>=0&&i<state.placements.length))];state.selectedIndices=clean;state.selectedIndex=primary!=null&&clean.includes(primary)?primary:(clean.length?clean[clean.length-1]:null)}
function selected(){return Number.isInteger(state.selectedIndex)?state.placements[state.selectedIndex]:null}
function selectedPlacements(){return selectedIndices().map(i=>state.placements[i]).filter(Boolean)}
function snapshot(){return JSON.stringify(state.placements)}
function pushHistory(before){const after=snapshot();if(before&&before!==after){state.history.push(before);if(state.history.length>80)state.history.shift();state.future=[]}}
function restore(s){state.placements=JSON.parse(s);setSelection([]);renderAll();validatePlan()}
function sequenceLimit(){
  return state.sequenceMode?clamp(parseInt(state.sequenceStep)||0,0,state.placements.length):state.placements.length;
}
function placementLayer(p){return Math.round((+p.z||0)/5)*5}
function availableLayers(){
  return [...new Set(state.placements.map(placementLayer))].sort((a,b)=>a-b);
}
function matchesLayerFilter(p){
  return state.layerFilter==="all"||placementLayer(p)===parseFloat(state.layerFilter);
}
function visiblePlacementEntries(){
  const limit=sequenceLimit();
  return state.placements.map((p,idx)=>({p,idx})).filter(({p,idx})=>idx<limit&&matchesLayerFilter(p));
}
function syncSequenceStep(){
  state.sequenceStep=clamp(parseInt(state.sequenceStep)||0,0,state.placements.length);
  if(!state.sequenceMode)state.sequenceStep=state.placements.length;
}
function setSequenceStep(value){
  state.sequenceMode=true;
  state.sequenceStep=clamp(parseInt(value)||0,0,state.placements.length);
  if(state.selectedIndex!=null&&state.selectedIndex>=sequenceLimit())setSelection([]);
  renderAll();
}
function showAllSteps(){
  state.sequenceMode=false;
  state.sequenceStep=state.placements.length;
  renderAll();
}
function viewDimY(c){return state.view==="side"?c.H:c.W}
function canvasKey(){return `${state.containerKey}:${state.view}`}
function baseViewBox(){
  const c=CONTAINERS[state.containerKey], pad=50, dimY=viewDimY(c);
  return {x:-pad,y:-pad,w:c.L+pad*2,h:dimY+pad*2};
}
function currentViewBox(){
  const key=canvasKey();
  if(!state.canvasViews[key])state.canvasViews[key]=baseViewBox();
  return state.canvasViews[key];
}
function setViewBox(vb){
  state.canvasViews[canvasKey()]={x:vb.x,y:vb.y,w:vb.w,h:vb.h};
}
function cleanViewBox(vb){
  const base=baseViewBox(), src=vb||base;
  return {x:+src.x||base.x,y:+src.y||base.y,w:clamp(+src.w||base.w,80,base.w*3),h:clamp(+src.h||base.h,80,base.h*3)};
}
function resetCanvasView({render=true}={}){
  setViewBox(baseViewBox());
  if(render)renderCanvas();
}
function zoomPct(){
  const base=baseViewBox(), vb=currentViewBox();
  return Math.round(base.w/vb.w*100);
}
function zoomCanvas(factor, anchor=null){
  const vb=currentViewBox(), base=baseViewBox();
  const minW=base.w/8, maxW=base.w*3;
  const nextW=clamp(vb.w/factor,minW,maxW);
  const ratio=nextW/vb.w, nextH=vb.h*ratio;
  const a=anchor||{x:vb.x+vb.w/2,y:vb.y+vb.h/2};
  setViewBox({x:a.x-(a.x-vb.x)*ratio,y:a.y-(a.y-vb.y)*ratio,w:nextW,h:nextH});
  renderCanvas();
}
function viewBoxForEntries(entries, margin=70){
  const c=CONTAINERS[state.containerKey], dimY=viewDimY(c);
  if(!entries.length)return baseViewBox();
  const rects=entries.map(({p})=>rectForView(p,c));
  const x0=Math.min(...rects.map(r=>r.x)), y0=Math.min(...rects.map(r=>r.y));
  const x1=Math.max(...rects.map(r=>r.x+r.w)), y1=Math.max(...rects.map(r=>r.y+r.h));
  return {
    x:clamp(x0-margin,-margin,c.L+margin),
    y:clamp(y0-margin,-margin,dimY+margin),
    w:Math.max(220,x1-x0+margin*2),
    h:Math.max(160,y1-y0+margin*2)
  };
}
function applyViewPreset(kind){
  if(!state.placements.length){setStatus("还没有方案可切换视图预设。","warn");return}
  state.measureMode=false;state.measurement=null;state.sequenceMode=false;state.sequenceStep=state.placements.length;setSelection([]);
  const c=CONTAINERS[state.containerKey], layers=availableLayers();
  if(kind==="bottom"||kind==="top"){
    const layer=kind==="bottom"?layers[0]:layers[layers.length-1];
    state.view="top";
    state.layerFilter=String(layer);
    const entries=state.placements.map((p,idx)=>({p,idx})).filter(({p})=>placementLayer(p)===layer);
    setViewBox(viewBoxForEntries(entries));
    const label=kind==="bottom"?"底层":"上层";
    recordActivity("视图预设",`${label} Z=${layer} cm`);
    renderAll();
    setStatus(`已切换到${label}视图：Z=${layer} cm。`,"ok");
    return;
  }
  if(kind==="door"){
    state.view="top";
    state.layerFilter="all";
    const pad=50, reserve=clamp(+state.doorReserve||0,0,c.L);
    const focusW=clamp(Math.max(reserve, c.L*0.25), 220, c.L);
    setViewBox({x:Math.max(-pad,c.L-focusW-pad),y:-pad,w:focusW+pad*2,h:c.W+pad*2});
    recordActivity("视图预设",reserve?`门口区域，预留 ${reserve} cm`:"门口区域");
    renderAll();
    setStatus(reserve?`已聚焦门口预留区 ${reserve} cm。`:"已聚焦门口侧区域。","ok");
  }
}
function viewPresetDefaultName(idx){return `视图 ${idx+1}`}
function normalizedViewPresets(list){
  return (Array.isArray(list)?list:[]).filter(p=>p&&p.containerKey&&["top","side"].includes(p.view)).map((p,idx)=>({
    name:cleanText(p.name,40)||viewPresetDefaultName(idx),
    containerKey:p.containerKey,
    view:p.view,
    layerFilter:p.layerFilter==null?"all":String(p.layerFilter),
    highlight:p.highlight||"all",
    viewBox:p.viewBox?{x:+p.viewBox.x||0,y:+p.viewBox.y||0,w:+p.viewBox.w||0,h:+p.viewBox.h||0}:null,
    createdAt:p.createdAt||""
  })).slice(-30);
}
function viewPresetName(p,idx){return cleanText(p&&p.name,40)||viewPresetDefaultName(idx)}
function saveCustomViewPreset(){
  state.customViewPresets=normalizedViewPresets(state.customViewPresets);
  const idx=state.customViewPresets.length, vb=currentViewBox();
  state.customViewPresets.push({
    name:viewPresetDefaultName(idx),
    containerKey:state.containerKey,
    view:state.view,
    layerFilter:state.layerFilter||"all",
    highlight:state.highlight||"all",
    viewBox:{x:vb.x,y:vb.y,w:vb.w,h:vb.h},
    createdAt:new Date().toISOString()
  });
  if(state.customViewPresets.length>30)state.customViewPresets=state.customViewPresets.slice(-30);
  recordActivity("保存视图",viewPresetDefaultName(idx),{render:true});
  renderViewPresetList();
  setStatus("当前视图已保存为预设。","ok");
}
function updateViewPreset(idx,patch){
  state.customViewPresets=normalizedViewPresets(state.customViewPresets);
  const p=state.customViewPresets[idx];if(!p)return;
  state.customViewPresets[idx]={...p,...patch,name:cleanText(patch.name??p.name,40)||viewPresetDefaultName(idx)};
}
function applyCustomViewPreset(idx){
  state.customViewPresets=normalizedViewPresets(state.customViewPresets);
  const p=state.customViewPresets[idx];if(!p)return;
  if(p.containerKey!==state.containerKey){setStatus(`该视图属于 ${p.containerKey}，请先切换柜型。`,"warn");return}
  state.measureMode=false;state.measurement=null;state.sequenceMode=false;state.sequenceStep=state.placements.length;setSelection([]);
  state.view=p.view;state.layerFilter=p.layerFilter||"all";state.highlight=p.highlight||"all";setViewBox(cleanViewBox(p.viewBox));
  recordActivity("应用视图",viewPresetName(p,idx),{render:true});
  renderAll();
  setStatus(`已应用视图预设：${viewPresetName(p,idx)}`,"ok");
}
function deleteViewPreset(idx){
  state.customViewPresets=normalizedViewPresets(state.customViewPresets);
  const p=state.customViewPresets[idx];if(!p)return;
  const name=viewPresetName(p,idx);
  state.customViewPresets.splice(idx,1);
  recordActivity("删除视图",name,{render:true});
  renderAll();
  setStatus(`已删除视图预设：${name}`,"ok");
}
function updateZoomLabel(){
  const z=$("zoom-label");if(z)z.textContent=`${zoomPct()}%`;
}
function updateCoordReadout(pt){
  const readout=$("coord-readout");if(!readout||!pt)return;
  const c=CONTAINERS[state.containerKey];
  const x=clamp(pt.x,0,c.L);
  if(state.view==="side"){
    const z=clamp(c.H-pt.y,0,c.H);
    readout.textContent=`X ${Math.round(x)} / Z ${Math.round(z)} cm`;
  }else{
    const y=clamp(pt.y,0,c.W);
    readout.textContent=`X ${Math.round(x)} / Y ${Math.round(y)} cm`;
  }
}
function updateDragReadout(dx,dy){
  const readout=$("coord-readout");if(!readout)return;
  if(state.view==="side"){
    readout.textContent=`ΔX ${Math.round(dx)} / ΔZ ${Math.round(-dy)} cm`;
  }else{
    readout.textContent=`ΔX ${Math.round(dx)} / ΔY ${Math.round(dy)} cm`;
  }
}
function clampCanvasPoint(pt){
  const c=CONTAINERS[state.containerKey], dimY=viewDimY(c);
  return {x:clamp(pt.x,0,c.L),y:clamp(pt.y,0,dimY)};
}
function measurementSummary(m=state.measurement, view=state.view){
  if(!m||m.view!==view)return null;
  const dx=m.x1-m.x0;
  const dv=view==="side"?-(m.y1-m.y0):(m.y1-m.y0);
  return {distance:Math.hypot(dx,dv),dx,dv,label:view==="side"?"Z":"Y"};
}
function measurementDefaultName(idx){return `M${idx+1}`}
function cleanText(value,max=80){return String(value||"").trim().slice(0,max)}
function measurementName(m,idx){return cleanText(m&&m.name,40)||measurementDefaultName(idx)}
function measurementNote(m){return cleanText(m&&m.note,140)}
function normalizedMeasurements(list){
  return (Array.isArray(list)?list:[]).filter(m=>m&&["top","side"].includes(m.view)).map((m,idx)=>({
    view:m.view,
    x0:+m.x0||0,y0:+m.y0||0,x1:+m.x1||0,y1:+m.y1||0,
    name:cleanText(m.name,40)||measurementDefaultName(idx),
    note:cleanText(m.note,140),
    createdAt:m.createdAt||""
  })).slice(-40);
}
function updateMeasureReadout(){
  const readout=$("coord-readout"), s=measurementSummary();if(!readout||!s)return;
  readout.textContent=`距离 ${Math.round(s.distance)} cm · ΔX ${Math.round(s.dx)} / Δ${s.label} ${Math.round(s.dv)} cm`;
}
function clearMeasurement(){
  state.measurement=null;
  drag=null;
}
function saveMeasurement(){
  const s=measurementSummary();
  if(!state.measurement||!s||s.distance<1){setStatus("先拖拽一条有效测距线。","warn");return}
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  const idx=state.savedMeasurements.length;
  state.savedMeasurements.push({...state.measurement,name:measurementDefaultName(idx),note:"",createdAt:new Date().toISOString()});
  if(state.savedMeasurements.length>40)state.savedMeasurements=state.savedMeasurements.slice(-40);
  recordActivity("保存测距",`${Math.round(s.distance)} cm，ΔX ${Math.round(s.dx)} / Δ${s.label} ${Math.round(s.dv)} cm`,{render:true});
  clearMeasurement();
  renderAll();
  setStatus("测距标注已保存。","ok");
}
function clearSavedMeasurements(){
  const count=(state.savedMeasurements||[]).length;
  if(!count){setStatus("没有已保存的测距标注。","warn");return}
  state.savedMeasurements=[];
  recordActivity("清除测距",`${count} 条标注`,{render:true});
  renderAll();
  setStatus(`已清除 ${count} 条测距标注。`,"ok");
}
function updateSavedMeasurement(idx,patch){
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  const m=state.savedMeasurements[idx];if(!m)return;
  state.savedMeasurements[idx]={...m,...patch,name:cleanText(patch.name??m.name,40)||measurementDefaultName(idx),note:cleanText(patch.note??m.note,140)};
  renderCanvas();
}
function deleteSavedMeasurement(idx){
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  const m=state.savedMeasurements[idx];if(!m)return;
  const name=measurementName(m,idx);
  state.savedMeasurements.splice(idx,1);
  recordActivity("删除测距",name,{render:true});
  renderAll();
  setStatus(`已删除测量标注：${name}`,"ok");
}
function focusSavedMeasurement(idx){
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  const m=state.savedMeasurements[idx];if(!m)return;
  state.measureMode=false;state.measurement=null;state.view=m.view;state.layerFilter="all";setSelection([]);
  const c=CONTAINERS[state.containerKey], dimY=viewDimY(c), pad=80;
  const x0=Math.min(m.x0,m.x1), x1=Math.max(m.x0,m.x1), y0=Math.min(m.y0,m.y1), y1=Math.max(m.y0,m.y1);
  setViewBox({x:clamp(x0-pad,-pad,c.L+pad),y:clamp(y0-pad,-pad,dimY+pad),w:Math.max(260,x1-x0+pad*2),h:Math.max(180,y1-y0+pad*2)});
  renderAll();
  setStatus(`已定位测量标注：${measurementName(m,idx)}`,"ok");
}
function toggleMeasureMode(force=null){
  state.measureMode=force==null?!state.measureMode:!!force;
  if(!state.measureMode)clearMeasurement();
  setSelection([]);
  renderAll();
  setStatus(state.measureMode?"测距模式：在画布上拖拽一条测量线，Esc 退出。":"已退出测距模式。",state.measureMode?"ok":"");
}

function validItems(){return state.items.filter(it=>it.sku&&it.L>0&&it.W>0&&it.H>0&&it.kg>0&&it.qty>0)}
function skuPayload(){
  return validItems().map(it=>({
    model:it.sku,name:it.sku,length:+it.L,width:+it.W,height:+it.H,weight:+it.kg,qty:parseInt(it.qty)||0,
    upright_only:!it.side,allow_stack:it.mode==="full",flat_stack:it.mode==="flat",
    supplier:it.supplier||"",arrival_order:parseInt(it.order)||1,max_top_load_kg:+it.maxTop||0
  }))
}
function placementPayload(items=state.placements){
  return items.map(p=>({
    sku_model:p.sku_model,instance_id:p.instance_id,x:+p.x,y:+p.y,z:+p.z,
    length:+p.length,width:+p.width,height:+p.height,weight:+p.weight,
    color:p.color||"#777777",rotated:!!p.rotated,locked:!!p.locked
  }))
}
function rulesPayload(){
  return {door_reserve_cm:+state.doorReserve||0,max_segment_weight_kg:+state.maxSegmentWeight||0}
}
function updateLocalStats(){
  const c=CONTAINERS[state.containerKey], placed=state.placements;
  const cbmCap=c.L*c.W*c.H/1e6, cbm=placed.reduce((a,p)=>a+p.length*p.width*p.height,0)/1e6;
  const weight=placed.reduce((a,p)=>a+p.weight,0);
  const centerX=weight?placed.reduce((a,p)=>a+(p.x+p.length/2)*p.weight,0)/weight:0;
  const centerY=weight?placed.reduce((a,p)=>a+(p.y+p.width/2)*p.weight,0)/weight:0;
  const frontWeight=placed.reduce((a,p)=>a+((p.x+p.length/2)<=c.L/2?p.weight:0),0);
  const rearWeight=weight-frontWeight;
  const leftWeight=placed.reduce((a,p)=>a+((p.y+p.width/2)<=c.W/2?p.weight:0),0);
  const rightWeight=weight-leftWeight;
  const segmentCount=6, segLen=c.L/segmentCount, segmentWeights=Array(segmentCount).fill(0);
  placed.forEach(p=>{const idx=clamp(Math.floor((p.x+p.length/2)/segLen),0,segmentCount-1);segmentWeights[idx]+=p.weight});
  const weightSegments=segmentWeights.map((w,i)=>({from_cm:+(i*segLen).toFixed(1),to_cm:+((i+1)*segLen).toFixed(1),weight_kg:Math.round(w)}));
  const counts={}; placed.forEach(p=>counts[p.sku_model]=(counts[p.sku_model]||0)+1);
  const total=validItems().reduce((a,it)=>a+(parseInt(it.qty)||0),0);
  const unfitted=validItems().map(it=>({model:it.sku,count:Math.max(0,(parseInt(it.qty)||0)-(counts[it.sku]||0))})).filter(x=>x.count>0);
  state.stats={placed_count:placed.length,total_count:total,door_reserve_cm:+state.doorReserve||0,usable_length_cm:Math.max(0,c.L-(+state.doorReserve||0)),cbm_used:+cbm.toFixed(2),cbm_capacity:+cbmCap.toFixed(2),cbm_util_pct:+(cbm/cbmCap*100).toFixed(1),weight_total_kg:Math.round(weight),weight_max_kg:c.maxKg,weight_util_pct:+(weight/c.maxKg*100).toFixed(1),center_x_cm:+centerX.toFixed(1),center_x_pct:+(centerX/c.L*100).toFixed(1),center_y_cm:+centerY.toFixed(1),center_y_pct:+(centerY/c.W*100).toFixed(1),front_weight_kg:Math.round(frontWeight),rear_weight_kg:Math.round(rearWeight),left_weight_kg:Math.round(leftWeight),right_weight_kg:Math.round(rightWeight),weight_segments:weightSegments,max_segment_weight_kg:Math.max(0,...weightSegments.map(s=>s.weight_kg)),max_segment_limit_kg:+state.maxSegmentWeight||0,unfitted};
}

function renderContainers(){
  const root=$("container-grid");clear(root);
  CORDER.forEach(k=>{const c=CONTAINERS[k],b=node("button","chip"+(state.containerKey===k?" active":""));
    const s=node("strong","",k), d=node("span","",`${(c.L/100).toFixed(2)}×${(c.W/100).toFixed(2)}×${(c.H/100).toFixed(2)} m`), cap=node("span","",`${c.cbm} m³ · ${(c.maxKg/1000).toFixed(1)} t`);
    b.append(s,d,cap);b.onclick=()=>{state.containerKey=k;state.canvasViews={};renderAll();validatePlan()};root.appendChild(b);
  });
}
function renderModes(){
  const root=$("mode-grid");clear(root);
  Object.entries(PACK_MODES).forEach(([k,m])=>{const b=node("button","chip"+(state.packMode===k?" active":""));
    b.append(node("strong","",m.name),node("span","",m.desc));b.onclick=()=>{state.packMode=k;renderModes()};root.appendChild(b);
  });
}
function renderRules(){
  const reserve=$("door-reserve-input");if(!reserve)return;
  if(document.activeElement!==reserve)reserve.value=state.doorReserve||"";
  reserve.oninput=()=>{
    state.doorReserve=clamp(parseFloat(reserve.value)||0,0,600);
    renderCanvas();renderStats();validatePlan();
    scheduleAutoDraft();
  };
  const segment=$("segment-limit-input");if(!segment)return;
  if(document.activeElement!==segment)segment.value=state.maxSegmentWeight||"";
  segment.oninput=()=>{
    state.maxSegmentWeight=clamp(parseFloat(segment.value)||0,0,1000000);
    renderStats();validatePlan();
    scheduleAutoDraft();
  };
}
function renderProjectInfo(){
  state.projectInfo=withProjectInfo(state.projectInfo);
  const map=[
    ["project-name-input","name"],
    ["container-no-input","containerNo"],
    ["project-revision-input","revision"],
    ["prepared-by-input","preparedBy"],
    ["reviewed-by-input","reviewedBy"],
    ["confirmed-by-input","confirmedBy"],
    ["project-note-input","note"],
  ];
  map.forEach(([id,key])=>{
    const el=$(id);if(!el)return;
    if(document.activeElement!==el)el.value=state.projectInfo[key]||"";
    el.oninput=()=>{state.projectInfo[key]=el.value;renderWorkflow();renderStats();scheduleAutoDraft()};
  });
}
function projectArchiveMissing(){
  const info=withProjectInfo(state.projectInfo);
  return [
    ["方案名",info.name],
    ["柜号/车号",info.containerNo],
    ["方案版本",info.revision],
    ["制单人",info.preparedBy],
    ["复核人",info.reviewedBy],
    ["现场确认人",info.confirmedBy],
  ].filter(([,value])=>!String(value||"").trim()).map(([label])=>label);
}
function workflowSteps(){
  const items=validItems(), totalQty=items.reduce((a,it)=>a+(parseInt(it.qty)||0),0);
  const hasPlan=state.placements.length>0, locked=state.placements.filter(p=>p.locked).length;
  const errors=(state.validation||[]).filter(i=>i.severity==="error").length;
  const warnings=(state.validation||[]).filter(i=>i.severity==="warning").length;
  const archiveMissing=projectArchiveMissing(), archiveReady=!archiveMissing.length;
  return [
    {status:items.length?"done":"warn",title:"1. 清单有效",detail:items.length?`${items.length} 个 SKU / ${totalQty} 箱`:"先填写型号、尺寸、重量和箱数"},
    {status:hasPlan?"done":"wait",title:"2. 生成初稿",detail:hasPlan?`${state.placements.length} 箱已入柜`:"点击自动排柜生成初稿"},
    {status:!hasPlan?"wait":(state.manualTouched||locked?"done":"warn"),title:"3. 人工复核",detail:!hasPlan?"待生成方案":(state.manualTouched||locked?`已人工调整或锁定 ${locked} 箱`:"建议拖拽检查、锁定关键区域或精改坐标")},
    {status:!hasPlan?"wait":(errors?"bad":warnings?"warn":"done"),title:"4. 规则校验",detail:!hasPlan?"待生成方案":errors?`${errors} 个错误需处理`:warnings?`${warnings} 个警告需复核`:"校验通过，可进入交付"},
    {status:!hasPlan?"wait":(errors?"bad":archiveReady?"done":"warn"),title:"5. 交付归档",detail:!hasPlan?"待生成方案":errors?"修完错误后再导出":archiveReady?"方案信息齐，可保存/导出":`待补：${archiveMissing.join("、")}`},
  ];
}
function safetySummary(){
  const s=state.stats||{}, hasPlan=state.placements.length>0;
  const errors=(state.validation||[]).filter(i=>i.severity==="error").length;
  const warnings=(state.validation||[]).filter(i=>i.severity==="warning").length;
  const missing=(s.unfitted||[]).reduce((a,u)=>a+(u.count||0),0);
  const locked=state.placements.filter(p=>p.locked).length;
  const archiveMissing=projectArchiveMissing();
  if(!hasPlan)return {level:"wait",label:"待生成",detail:"先生成装柜方案，再进入安全复核。",reasons:["尚未生成装柜初稿"]};
  const blockers=[];
  if(errors)blockers.push(`${errors} 个错误未处理`);
  if(missing)blockers.push(`${missing} 箱未放入方案`);
  if(blockers.length)return {level:"bad",label:"不可交付",detail:blockers.join("；"),reasons:blockers};
  const reviews=[];
  if(warnings)reviews.push(`${warnings} 个警告需复核`);
  if(!(state.manualTouched||locked))reviews.push("尚未人工复核或锁定关键区域");
  if(archiveMissing.length)reviews.push(`归档信息缺少：${archiveMissing.join("、")}`);
  if(reviews.length)return {level:"warn",label:"需复核",detail:reviews.join("；"),reasons:reviews};
  return {level:"ok",label:"可交付",detail:"清单已完整入柜，规则校验通过，归档信息齐全。",reasons:["清单已完整入柜","规则校验通过","归档信息齐全"]};
}
function renderWorkflow(){
  const root=$("workflow");if(!root)return;clear(root);
  workflowSteps().forEach(step=>{
    const box=node("div","flow-step "+step.status);
    box.append(node("div","flow-dot"),node("div",""));
    box.lastChild.append(node("b","",step.title),node("span","",step.detail));
    root.appendChild(box);
  });
}
function activityTimeLabel(iso){
  const d=new Date(iso);
  if(Number.isNaN(d.getTime()))return "";
  return d.toLocaleString();
}
function recordActivity(action,detail="",opts={}){
  state.activityLog=Array.isArray(state.activityLog)?state.activityLog:[];
  state.activityLog.push({time:new Date().toISOString(),action:String(action||"操作"),detail:String(detail||"")});
  if(state.activityLog.length>200)state.activityLog=state.activityLog.slice(-200);
  if(opts.render)renderActivityLog();
  scheduleAutoDraft();
}
function renderActivityLog(){
  const root=$("activity-log");if(!root)return;clear(root);
  const items=(state.activityLog||[]).slice(-8).reverse();
  if(!items.length){root.appendChild(node("div","empty","还没有操作记录。生成、调整、校验和导出会显示在这里。"));return}
  items.forEach(item=>{
    const box=node("div","activity-item");
    box.append(node("b","",item.action||"操作"));
    box.append(node("span","",activityTimeLabel(item.time)));
    if(item.detail)box.append(node("span","",item.detail));
    root.appendChild(box);
  });
}
function renderMeasurementList(){
  const root=$("measurement-list");if(!root)return;clear(root);
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  if(!state.savedMeasurements.length){root.appendChild(node("div","empty","还没有测量标注。先打开测距，在画布上拖线后保存。"));return}
  state.savedMeasurements.forEach((m,idx)=>{
    const s=measurementSummary(m,m.view), box=node("div","measure-card");
    const title=node("b","",measurementName(m,idx));
    box.append(title);
    box.append(node("div","measure-meta",`${m.view==="side"?"侧视":"俯视"} · ${s?Math.round(s.distance):0} cm · ΔX ${s?Math.round(s.dx):0} / Δ${s?s.label:"Y"} ${s?Math.round(s.dv):0} cm`));
    const nameLabel=node("label","", "标注名"), nameInput=input(m.name||measurementDefaultName(idx),v=>updateSavedMeasurement(idx,{name:v}));
    nameInput.maxLength=40;
    const syncTitle=nameInput.oninput;
    nameInput.oninput=()=>{syncTitle();title.textContent=measurementName(state.savedMeasurements[idx],idx)};
    nameInput.onchange=nameInput.oninput;
    const noteLabel=node("label","", "备注"), noteInput=input(m.note||"",v=>updateSavedMeasurement(idx,{note:v}));
    noteInput.maxLength=140;noteInput.placeholder="例如：门口预留宽度、重货区边界";
    const actions=node("div","measure-actions");
    const focusBtn=node("button","", "定位");focusBtn.onclick=()=>focusSavedMeasurement(idx);
    const delBtn=node("button","danger", "删除");delBtn.onclick=()=>deleteSavedMeasurement(idx);
    actions.append(focusBtn,delBtn);
    box.append(nameLabel,nameInput,noteLabel,noteInput,actions);
    root.appendChild(box);
  });
}
function renderViewPresetList(){
  const root=$("view-preset-list");if(!root)return;clear(root);
  state.customViewPresets=normalizedViewPresets(state.customViewPresets);
  if(!state.customViewPresets.length){root.appendChild(node("div","empty","还没有自定义视图。调整缩放、层或高亮后，点上方“存视图”。"));return}
  state.customViewPresets.forEach((p,idx)=>{
    const box=node("div","preset-card"), title=node("b","",viewPresetName(p,idx));
    box.append(title);
    box.append(node("div","preset-meta",`${p.containerKey} · ${p.view==="side"?"侧视":"俯视"} · ${p.layerFilter==="all"?"全部层":`Z=${p.layerFilter} cm`} · ${p.highlight==="all"?"全部高亮":p.highlight.replace("sku:","SKU ").replace("supplier:","厂家 ")}`));
    const nameLabel=node("label","", "预设名"), nameInput=input(p.name||viewPresetDefaultName(idx),v=>{updateViewPreset(idx,{name:v});title.textContent=viewPresetName(state.customViewPresets[idx],idx)});
    nameInput.maxLength=40;
    const actions=node("div","preset-actions");
    const applyBtn=node("button","", "应用");applyBtn.onclick=()=>applyCustomViewPreset(idx);
    const delBtn=node("button","danger", "删除");delBtn.onclick=()=>deleteViewPreset(idx);
    actions.append(applyBtn,delBtn);
    box.append(nameLabel,nameInput,actions);
    root.appendChild(box);
  });
}
function renderHighlightPicker(){
  const sel=$("highlight-select");if(!sel)return;
  const current=state.highlight||"all";clear(sel);
  const all=node("option");all.value="all";all.textContent="高亮：全部";sel.appendChild(all);
  [...new Set(validItems().map(it=>it.sku).filter(Boolean))].forEach(sku=>{const o=node("option");o.value="sku:"+sku;o.textContent="SKU："+sku;sel.appendChild(o)});
  [...new Set(validItems().map(it=>it.supplier).filter(Boolean))].forEach(supplier=>{const o=node("option");o.value="supplier:"+supplier;o.textContent="厂家："+supplier;sel.appendChild(o)});
  sel.value=[...sel.options].some(o=>o.value===current)?current:"all";
  state.highlight=sel.value;
  sel.onchange=()=>{state.highlight=sel.value;renderCanvas()};
}
function renderLayerPicker(){
  const sel=$("layer-select");if(!sel)return;
  const current=state.layerFilter||"all";clear(sel);
  const all=node("option");all.value="all";all.textContent="层：全部";sel.appendChild(all);
  availableLayers().forEach(z=>{const o=node("option");o.value=String(z);o.textContent=`Z=${z} cm`;sel.appendChild(o)});
  sel.value=[...sel.options].some(o=>o.value===current)?current:"all";
  state.layerFilter=sel.value;
  sel.onchange=()=>{state.layerFilter=sel.value;if(state.selectedIndex!=null&&!visiblePlacementEntries().some(e=>e.idx===state.selectedIndex))setSelection([]);renderAll()};
}
function layerActionTargets(){
  return visiblePlacementEntries().map(e=>e.idx);
}
function selectCurrentLayer(){
  const targets=layerActionTargets();
  if(!targets.length){setStatus("当前层没有可选择的货物。","warn");return}
  setSelection(targets,targets[targets.length-1]);
  recordActivity("选择当前层",`${targets.length} 箱`,{render:true});
  renderAll();
  setStatus(`已选择当前层 ${targets.length} 箱。`,"ok");
}
function setCurrentLayerLock(locked){
  const targets=layerActionTargets();
  if(!targets.length){setStatus("当前层没有可处理的货物。","warn");return}
  const before=snapshot();
  let changed=0;
  targets.forEach(idx=>{
    const p=state.placements[idx];
    if(p&&p.locked!==locked){p.locked=locked;changed++}
  });
  if(!changed){setStatus(locked?"当前层已全部锁定。":"当前层已全部解锁。","warn");return}
  state.manualTouched=true;
  pushHistory(before);
  setSelection(targets,targets[targets.length-1]);
  recordActivity(locked?"锁定当前层":"解锁当前层",`${changed} / ${targets.length} 箱`,{render:true});
  renderAll();
  validatePlan();
  setStatus(locked?`已锁定当前层 ${changed} 箱。`:`已解锁当前层 ${changed} 箱。`,"ok");
}
function renderSequenceControls(){
  syncSequenceStep();
  const total=state.placements.length, shown=sequenceLimit();
  const toggle=$("step-toggle"), prev=$("step-prev"), next=$("step-next"), all=$("step-all"), range=$("step-range"), label=$("step-label");
  if(!toggle||!range||!label)return;
  toggle.className=state.sequenceMode?"primary":"";
  toggle.disabled=!total;
  prev.disabled=!total||shown<=0;
  next.disabled=!total||shown>=total;
  all.disabled=!total||!state.sequenceMode;
  range.max=String(total);
  range.value=String(shown);
  range.disabled=!total;
  label.textContent=`${shown}/${total}`;
  toggle.onclick=()=>{state.sequenceMode=!state.sequenceMode;state.sequenceStep=state.sequenceMode?Math.min(Math.max(sequenceLimit(),1),total):total;renderAll()};
  prev.onclick=()=>setSequenceStep(shown-1);
  next.onclick=()=>setSequenceStep(shown+1);
  all.onclick=showAllSteps;
  range.oninput=()=>setSequenceStep(range.value);
}
function renderToolButtons(){
  const measure=$("measure-toggle");if(measure)measure.className=state.measureMode?"primary":"";
  const saveMeasure=$("btn-save-measure");if(saveMeasure)saveMeasure.disabled=!measurementSummary();
  const clearMeasures=$("btn-clear-measures");if(clearMeasures)clearMeasures.disabled=!(state.savedMeasurements||[]).length;
  ["btn-select-layer","btn-lock-layer","btn-unlock-layer"].forEach(id=>{const b=$(id);if(b)b.disabled=!visiblePlacementEntries().length});
  const repackLayer=$("btn-repack-layer");if(repackLayer)repackLayer.disabled=state.layerFilter==="all"||!visiblePlacementEntries().some(({p})=>!p.locked);
  ["btn-view-bottom","btn-view-top-layer","btn-view-door"].forEach(id=>{const b=$(id);if(b)b.disabled=!state.placements.length});
}
function input(value,onchange,type="text",opts={}){
  const i=node("input");i.type=type;i.value=value===0?"":(value??"");
  if(value===0&&opts.showZero)i.value="0";
  const commit=()=>{onchange(i.value);renderWorkflow();scheduleAutoDraft()};
  i.oninput=commit;i.onchange=commit;
  return i;
}
function modeButton(label,mode,it){const b=node("button","mini "+(it.mode===mode?"mode-on ":"")+(mode==="flat"?"mode-flat":mode==="none"?"mode-none":""),label);b.onclick=()=>{it.mode=mode;renderItems()};return b}
function renderItems(){
  const body=$("items-body");clear(body);
  state.items.forEach((it,idx)=>{
    const tr=node("tr");
    const cells=[
      input(it.sku,v=>it.sku=v),input(it.supplier,v=>it.supplier=v),input(it.order,v=>it.order=Math.max(1,parseInt(v)||1),"number"),
      input(it.L,v=>it.L=parseFloat(v)||0,"number"),input(it.W,v=>it.W=parseFloat(v)||0,"number"),input(it.H,v=>it.H=parseFloat(v)||0,"number"),
      input(it.kg,v=>it.kg=parseFloat(v)||0,"number"),input(it.maxTop,v=>it.maxTop=parseFloat(v)||0,"number"),input(it.qty,v=>it.qty=parseInt(v)||0,"number")
    ];
    cells.forEach(c=>{const td=node("td");td.appendChild(c);tr.appendChild(td)});
    const rules=node("td"), r=node("div","row-actions");
    r.append(modeButton("叠","full",it),modeButton("平","flat",it),modeButton("禁","none",it));
    const side=node("button","mini"+(it.side?" mode-on":""),"侧");side.onclick=()=>{it.side=!it.side;renderItems()};r.appendChild(side);rules.appendChild(r);tr.appendChild(rules);
    const del=node("td"), db=node("button","mini danger","×");db.onclick=()=>{state.items.splice(idx,1);if(!state.items.length)state.items=[blank()];renderItems()};del.appendChild(db);tr.appendChild(del);
    body.appendChild(tr);
    if(it.note){const nr=node("tr"), td=node("td");td.colSpan=11;td.className="hint";td.textContent=it.note;nr.appendChild(td);body.appendChild(nr)}
  });
  renderHighlightPicker();
  scheduleAutoDraft();
}
function stackModeText(mode){
  return mode==="flat"?"平":mode==="none"?"禁":"叠";
}
function renderImportPreview(){
  const wrap=$("import-preview"), body=$("import-preview-body"), issuesRoot=$("import-preview-issues"), summaryEl=$("import-preview-summary");
  if(!wrap||!body||!issuesRoot||!summaryEl)return;
  clear(body);clear(issuesRoot);
  const data=state.importPreview;
  if(!data){wrap.classList.remove("show");summaryEl.textContent="";return}
  const rows=data.skus||[], issues=data.issues||[], s=data.summary||{};
  wrap.classList.add("show");
  summaryEl.textContent=`有效 ${s.imported_rows||rows.length} 行 / 错误 ${s.error_count||0} / 警告 ${s.warning_count||0}`;
  rows.slice(0,8).forEach(sku=>{
    const tr=node("tr");
    [
      sku.model||"",
      sku.supplier||"",
      `${sku.length||0}×${sku.width||0}×${sku.height||0}`,
      sku.weight||0,
      sku.qty||0,
      stackModeText(sku.stack_mode)
    ].forEach(value=>{const td=node("td","",value);tr.appendChild(td)});
    body.appendChild(tr);
  });
  if(rows.length>8){const tr=node("tr"), td=node("td","hint",`还有 ${rows.length-8} 行未显示，确认后会一并追加。`);td.colSpan=6;tr.appendChild(td);body.appendChild(tr)}
  if(!rows.length){const tr=node("tr"), td=node("td","hint","没有可追加的有效行。");td.colSpan=6;tr.appendChild(td);body.appendChild(tr)}
  issues.slice(0,8).forEach(issue=>{
    issuesRoot.appendChild(node("div","import-issue "+(issue.severity||"warning"),`${issue.row?`第 ${issue.row} 行`:"提示"}：${issue.message}`));
  });
  if(issues.length>8)issuesRoot.appendChild(node("div","import-issue",`还有 ${issues.length-8} 个问题未显示。`));
}
function renderStats(){
  updateLocalStats();
  const s=state.stats, root=$("stats");clear(root);
  const safety=safetySummary(), safetyBox=node("div","stat safety "+safety.level);
  safetyBox.append(node("label","","安全结论"),node("b","",safety.label),node("div","hint",safety.detail));
  root.appendChild(safetyBox);
  [
    ["空间利用率",`${s.cbm_util_pct}%`,`${s.cbm_used}/${s.cbm_capacity} m³`],
    ["总重量",`${s.weight_total_kg.toLocaleString()} kg`,`限重 ${s.weight_max_kg.toLocaleString()} kg`],
    ["箱数",`${s.placed_count}/${s.total_count}`,"已放/总箱数"],
    ["步骤",`${sequenceLimit()}/${s.placed_count}`,state.sequenceMode?"当前回放进度":"显示全部"],
    ["层",state.layerFilter==="all"?"全部":`Z=${state.layerFilter} cm`,`${visiblePlacementEntries().length} 箱可见`],
    ["未放",`${s.unfitted.reduce((a,u)=>a+u.count,0)}`,"删除或未装箱数"],
    ["重心 X",`${s.center_x_pct||0}%`,`${s.center_x_cm||0} cm 距柜头`],
    ["前/后重",`${(s.front_weight_kg||0).toLocaleString()} / ${(s.rear_weight_kg||0).toLocaleString()} kg`,`门口预留 ${s.door_reserve_cm||0} cm`],
    ["左/右重",`${(s.left_weight_kg||0).toLocaleString()} / ${(s.right_weight_kg||0).toLocaleString()} kg`,`横向重心 ${s.center_y_pct||0}%`],
    ["最重分段",`${(s.max_segment_weight_kg||0).toLocaleString()} kg`,(s.max_segment_limit_kg||0)>0?`限 ${(s.max_segment_limit_kg||0).toLocaleString()} kg`:"按柜长 6 段粗分"],
  ].forEach(([a,b,c])=>{
    const box=node("div","stat");box.append(node("label","",a),node("b","",b),node("div","hint",c));root.appendChild(box);
  });
}
function issueTargetIndex(issue){
  return state.placements.findIndex(p=>p.sku_model===issue.item&&(!issue.instance_id||p.instance_id===issue.instance_id));
}
function focusIssue(issue){
  const idx=issueTargetIndex(issue);
  if(idx>=0){setSelection([idx],idx);renderAll();return true}
  return false;
}
function fixIssue(issue,kind){
  const idx=issueTargetIndex(issue);
  if(idx<0){setStatus("该问题没有可直接定位的箱体。","warn");return}
  const p=state.placements[idx], c=CONTAINERS[state.containerKey], reserve=clamp(+state.doorReserve||0,0,c.L);
  if(p.locked){setStatus("该箱已锁定，请先解锁后再快速修复。","warn");return}
  const before=snapshot();
  if(kind==="forward")p.x-=5;
  if(kind==="back")p.x+=5;
  if(kind==="left")p.y-=5;
  if(kind==="right")p.y+=5;
  if(kind==="door")p.x=c.L-reserve-p.length;
  if(kind==="bounds")clampPlacement(p);
  if(kind==="floor")p.z=0;
  clampPlacement(p);
  if(before===snapshot()){setStatus("快速修复没有改变该箱位置。","warn");return}
  state.manualTouched=true;pushHistory(before);setSelection([idx],idx);renderAll();
  const labels={forward:"前移 5cm",back:"后移 5cm",left:"左移 5cm",right:"右移 5cm",door:"移出门口",bounds:"拉回柜内",floor:"落地"};
  recordActivity("快速修复",`${p.sku_model} #${p.instance_id} ${labels[kind]||kind}`,{render:true});
  validatePlan();
}
function issueFixKinds(issue){
  if(!issue||!issue.item)return [];
  if(issue.code==="door_reserve_occupied")return [["移出门口","door"],["前移 5cm","forward"]];
  if(issue.code==="out_of_bounds")return [["拉回柜内","bounds"]];
  if(issue.code==="unsupported"||issue.code==="non_stackable_support"||issue.code==="top_load_exceeded")return [["落地","floor"]];
  if(issue.code==="collision")return [["前移 5cm","forward"],["后移 5cm","back"],["左移 5cm","left"],["右移 5cm","right"]];
  return [];
}
function renderIssues(){
  const root=$("issues");clear(root);
  if(!state.validation.length){root.appendChild(node("div","empty","没有发现错误。人工调整后仍建议导出前重新校验。"));return}
  state.validation.forEach(issue=>{const box=node("div","issue "+issue.severity);
    const title=node("div","",issue.message);const code=node("code","",issue.code);
    box.append(title,code);box.onclick=()=>focusIssue(issue);
    const actions=node("div","issue-actions");
    if(issueTargetIndex(issue)>=0){
      const locate=node("button","","定位");locate.onclick=e=>{e.stopPropagation();focusIssue(issue)};actions.appendChild(locate);
    }
    issueFixKinds(issue).forEach(([label,kind])=>{
      const b=node("button","",label);b.onclick=e=>{e.stopPropagation();fixIssue(issue,kind)};actions.appendChild(b);
    });
    if(actions.childNodes.length)box.appendChild(actions);
    root.appendChild(box);
  });
}
function rectForView(p,c){
  if(state.view==="side")return {x:p.x,y:c.H-(p.z+p.height),w:p.length,h:p.height};
  return {x:p.x,y:p.y,w:p.length,h:p.width};
}
function placementMatchesHighlight(p){
  if(!state.highlight||state.highlight==="all")return true;
  if(state.highlight.startsWith("sku:"))return p.sku_model===state.highlight.slice(4);
  if(state.highlight.startsWith("supplier:")){
    const supplier=state.items.find(it=>it.sku===p.sku_model)?.supplier||"";
    return supplier===state.highlight.slice(9);
  }
  return true;
}
function issuesForPlacement(p){
  return (state.validation||[]).filter(i=>i.item===p.sku_model&&(!i.instance_id||i.instance_id===p.instance_id));
}
function issueClassForPlacement(p){
  const issues=issuesForPlacement(p);
  if(issues.some(i=>i.severity==="error"))return " issue-error";
  if(issues.some(i=>i.severity==="warning"))return " issue-warning";
  return "";
}
function overlap1d(a0,a1,b0,b1){return Math.max(0,Math.min(a1,b1)-Math.max(a0,b0))}
function placementsOverlap(a,b){
  return overlap1d(a.x,a.x+a.length,b.x,b.x+b.length)>0
    && overlap1d(a.y,a.y+a.width,b.y,b.y+b.width)>0
    && overlap1d(a.z,a.z+a.height,b.z,b.z+b.height)>0;
}
function rectUnionArea(rects){
  const xs=[...new Set(rects.flatMap(r=>[r[0],r[2]]))].sort((a,b)=>a-b);
  let area=0;
  for(let i=0;i<xs.length-1;i++){
    const left=xs[i], right=xs[i+1];if(right-left<=EPS)continue;
    const intervals=rects.filter(r=>r[0]<right-EPS&&r[2]>left+EPS).map(r=>[r[1],r[3]]).sort((a,b)=>a[0]-b[0]);
    if(!intervals.length)continue;
    let [cur0,cur1]=intervals[0], covered=0;
    intervals.slice(1).forEach(([y0,y1])=>{if(y0<=cur1+EPS){cur1=Math.max(cur1,y1)}else{covered+=cur1-cur0;cur0=y0;cur1=y1}});
    covered+=cur1-cur0;area+=(right-left)*covered;
  }
  return area;
}
function supportArea(candidate,placed){
  const rects=[];
  placed.forEach(lower=>{
    if(Math.abs(lower.z+lower.height-candidate.z)>EPS)return;
    const x0=Math.max(candidate.x,lower.x), y0=Math.max(candidate.y,lower.y);
    const x1=Math.min(candidate.x+candidate.length,lower.x+lower.length), y1=Math.min(candidate.y+candidate.width,lower.y+lower.width);
    if(x1-x0>EPS&&y1-y0>EPS)rects.push([x0,y0,x1,y1]);
  });
  return rectUnionArea(rects);
}
function placementKey(p){return `${p.sku_model}#${p.instance_id}`}
function canPlaceLayerCandidate(candidate,placed,c){
  const reserve=clamp(+state.doorReserve||0,0,c.L);
  if(candidate.x<-EPS||candidate.y<-EPS||candidate.z<-EPS)return false;
  if(candidate.x+candidate.length>c.L-reserve+EPS||candidate.y+candidate.width>c.W+EPS||candidate.z+candidate.height>c.H+EPS)return false;
  if(candidate.z>EPS&&supportArea(candidate,placed)+EPS<candidate.length*candidate.width)return false;
  return !placed.some(other=>placementsOverlap(candidate,other));
}
function layerCandidatePoints(item,placed,c,targetLayer){
  const reserve=clamp(+state.doorReserve||0,0,c.L), maxX=Math.max(0,c.L-reserve-item.length), maxY=Math.max(0,c.W-item.width);
  const xs=new Set([0,maxX]), ys=new Set([0,maxY]);
  placed.forEach(other=>{
    if(overlap1d(targetLayer,targetLayer+item.height,other.z,other.z+other.height)<=0)return;
    [other.x,other.x+other.length,other.x-item.length,other.x+other.length-item.length].forEach(x=>xs.add(clamp(snap(x),0,maxX)));
    [other.y,other.y+other.width,other.y-item.width,other.y+other.width-item.width].forEach(y=>ys.add(clamp(snap(y),0,maxY)));
  });
  const points=[];
  xs.forEach(x=>ys.forEach(y=>points.push({x,y})));
  return points.sort((a,b)=>a.x-b.x||a.y-b.y);
}
function repackLayerPlane(targetLayer,movableEntries){
  const c=CONTAINERS[state.containerKey], moving=new Set(movableEntries.map(e=>e.idx));
  const next=state.placements.map(p=>({...p}));
  const placed=next.filter((_,idx)=>!moving.has(idx));
  let moved=0, failed=0;
  movableEntries.map(({p,idx})=>({idx,p:{...p,z:targetLayer}}))
    .sort((a,b)=>b.p.length*b.p.width*b.p.height-a.p.length*a.p.width*a.p.height||a.idx-b.idx)
    .forEach(({idx,p})=>{
      let chosen=null;
      for(const pt of layerCandidatePoints(p,placed,c,targetLayer)){
        const candidate={...p,x:pt.x,y:pt.y,z:targetLayer};
        if(canPlaceLayerCandidate(candidate,placed,c)){chosen=candidate;break}
      }
      if(!chosen){chosen={...p};failed++}
      if(Math.abs(chosen.x-next[idx].x)>EPS||Math.abs(chosen.y-next[idx].y)>EPS||Math.abs(chosen.z-next[idx].z)>EPS)moved++;
      next[idx]=chosen;placed.push(chosen);
    });
  return {placements:next,moved,failed};
}
function violatesDoorReserve(p){
  const c=CONTAINERS[state.containerKey], reserve=+state.doorReserve||0;
  return reserve>0&&p.x+p.length>c.L-reserve;
}
function liveIssueClassForPlacement(p,idx){
  if(!drag||drag.type!=="move"||!drag.indices.includes(idx))return "";
  if(violatesDoorReserve(p))return " live-error";
  if(state.placements.some((other,j)=>j!==idx&&placementsOverlap(p,other)))return " live-error";
  return "";
}
function viewAxisBounds(p){
  if(state.view==="side")return {x0:p.x,x1:p.x+p.length,v0:p.z,v1:p.z+p.height};
  return {x0:p.x,x1:p.x+p.length,v0:p.y,v1:p.y+p.width};
}
function snapOffset(edges,targets,delta,tolerance=10){
  let best=0, bestAbs=tolerance+1, bestTarget=null;
  edges.forEach(edge=>targets.forEach(target=>{
    const offset=target-(edge+delta), abs=Math.abs(offset);
    if(abs<bestAbs&&abs<=tolerance){best=offset;bestAbs=abs;bestTarget=target}
  }));
  return {offset:best,target:bestTarget};
}
function snapDragDelta(rawDx,rawDy){
  if(!drag||drag.type!=="move")return {dx:rawDx,dy:rawDy,guides:[]};
  const c=CONTAINERS[state.containerKey], maxV=state.view==="side"?c.H:c.W;
  const moving=new Set(drag.indices), bounds=drag.positions.map(pos=>{
    const p=state.placements[pos.i];if(!p)return null;
    const copy={...p,x:pos.x,y:pos.y,z:pos.z};
    return viewAxisBounds(copy);
  }).filter(Boolean);
  if(!bounds.length)return {dx:rawDx,dy:rawDy,guides:[]};
  let dx=snap(rawDx), dv=snap(state.view==="side"?-rawDy:rawDy);
  const group={x0:Math.min(...bounds.map(b=>b.x0)),x1:Math.max(...bounds.map(b=>b.x1)),v0:Math.min(...bounds.map(b=>b.v0)),v1:Math.max(...bounds.map(b=>b.v1))};
  const xTargets=[0,c.L], vTargets=[0,maxV];
  visiblePlacementEntries().forEach(({p,idx})=>{
    if(moving.has(idx))return;
    const b=viewAxisBounds(p);
    xTargets.push(b.x0,b.x1);vTargets.push(b.v0,b.v1);
  });
  const xSnap=snapOffset([group.x0,group.x1],xTargets,dx);
  const vSnap=snapOffset([group.v0,group.v1],vTargets,dv);
  dx+=xSnap.offset;dv+=vSnap.offset;
  const guides=[];
  if(xSnap.target!=null)guides.push({axis:"x",value:xSnap.target});
  if(vSnap.target!=null)guides.push({axis:"v",value:vSnap.target});
  return {dx,dy:state.view==="side"?-dv:dv,guides};
}
function renderSnapGuides(root,c,dimY){
  const guides=(drag&&drag.type==="move"&&drag.guides)||[];
  guides.forEach(g=>{
    const line=svg("line");line.setAttribute("class","svg-snap-guide");
    if(g.axis==="x"){
      line.setAttribute("x1",g.value);line.setAttribute("x2",g.value);line.setAttribute("y1",0);line.setAttribute("y2",dimY);
    }else{
      const y=state.view==="side"?c.H-g.value:g.value;
      line.setAttribute("x1",0);line.setAttribute("x2",c.L);line.setAttribute("y1",y);line.setAttribute("y2",y);
    }
    root.appendChild(line);
  });
}
function renderMeasurement(root){
  const m=state.measurement, s=measurementSummary(m);if(!m||!s)return;
  const line=svg("line");line.setAttribute("x1",m.x0);line.setAttribute("y1",m.y0);line.setAttribute("x2",m.x1);line.setAttribute("y2",m.y1);line.setAttribute("class","svg-measure");root.appendChild(line);
  [[m.x0,m.y0],[m.x1,m.y1]].forEach(([x,y])=>{const p=svg("circle");p.setAttribute("cx",x);p.setAttribute("cy",y);p.setAttribute("r",5);p.setAttribute("class","svg-measure-point");root.appendChild(p)});
  const label=svg("text");label.setAttribute("x",(m.x0+m.x1)/2+8);label.setAttribute("y",(m.y0+m.y1)/2-8);label.setAttribute("class","svg-measure-label");
  label.textContent=`${Math.round(s.distance)} cm · ΔX ${Math.round(s.dx)} / Δ${s.label} ${Math.round(s.dv)}`;
  root.appendChild(label);
}
function renderSavedMeasurements(root){
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  (state.savedMeasurements||[]).filter(m=>m.view===state.view).forEach((m,idx)=>{
    const s=measurementSummary(m);if(!s)return;
    const line=svg("line");line.setAttribute("x1",m.x0);line.setAttribute("y1",m.y0);line.setAttribute("x2",m.x1);line.setAttribute("y2",m.y1);line.setAttribute("class","svg-saved-measure");root.appendChild(line);
    [[m.x0,m.y0],[m.x1,m.y1]].forEach(([x,y])=>{const p=svg("circle");p.setAttribute("cx",x);p.setAttribute("cy",y);p.setAttribute("r",4);p.setAttribute("class","svg-saved-measure-point");root.appendChild(p)});
    const label=svg("text");label.setAttribute("x",(m.x0+m.x1)/2+8);label.setAttribute("y",(m.y0+m.y1)/2+16);label.setAttribute("class","svg-saved-measure-label");
    label.textContent=`${measurementName(m,idx)} ${Math.round(s.distance)} cm`;
    root.appendChild(label);
  });
}
function appendDimLine(root,x1,y1,x2,y2,label,vertical=false){
  const line=svg("line");line.setAttribute("x1",x1);line.setAttribute("y1",y1);line.setAttribute("x2",x2);line.setAttribute("y2",y2);line.setAttribute("class","svg-dim");root.appendChild(line);
  const ticks=vertical?[[x1-6,y1,x1+6,y1],[x2-6,y2,x2+6,y2]]:[[x1,y1-6,x1,y1+6],[x2,y2-6,x2,y2+6]];
  ticks.forEach(([a,b,c,d])=>{const tick=svg("line");tick.setAttribute("x1",a);tick.setAttribute("y1",b);tick.setAttribute("x2",c);tick.setAttribute("y2",d);tick.setAttribute("class","svg-dim-tick");root.appendChild(tick)});
  const text=svg("text");text.setAttribute("x",(x1+x2)/2+4);text.setAttribute("y",(y1+y2)/2-6);text.setAttribute("class","svg-dim-label");text.textContent=label;root.appendChild(text);
}
function renderSelectionDimensions(root,c){
  const entries=selectedIndices().map(idx=>({idx,p:state.placements[idx]})).filter(({p,idx})=>p&&idx<sequenceLimit()&&matchesLayerFilter(p));
  if(!entries.length)return;
  const rects=entries.map(({p})=>rectForView(p,c));
  const x0=Math.min(...rects.map(r=>r.x)), y0=Math.min(...rects.map(r=>r.y));
  const x1=Math.max(...rects.map(r=>r.x+r.w)), y1=Math.max(...rects.map(r=>r.y+r.h));
  const width=Math.round(x1-x0), height=Math.round(y1-y0);
  const xLabel=entries.length===1?`L ${width} cm`:`X ${width} cm`;
  const yLabel=entries.length===1?(state.view==="side"?`H ${height} cm`:`W ${height} cm`):(state.view==="side"?`Z ${height} cm`:`Y ${height} cm`);
  appendDimLine(root,x0,y1+16,x1,y1+16,xLabel,false);
  appendDimLine(root,x1+16,y0,x1+16,y1,yLabel,true);
}
function addRulers(root,c,dimY){
  for(let x=0;x<=c.L;x+=200){
    const tick=svg("line");tick.setAttribute("x1",x);tick.setAttribute("x2",x);tick.setAttribute("y1",-14);tick.setAttribute("y2",0);tick.setAttribute("class","svg-ruler");root.appendChild(tick);
    const label=svg("text");label.setAttribute("x",x+4);label.setAttribute("y",-18);label.setAttribute("class","svg-ruler-label");label.textContent=`X ${x}`;root.appendChild(label);
  }
  const step=state.view==="side"?50:50;
  for(let y=0;y<=dimY;y+=step){
    const tick=svg("line");tick.setAttribute("x1",-14);tick.setAttribute("x2",0);tick.setAttribute("y1",y);tick.setAttribute("y2",y);tick.setAttribute("class","svg-ruler");root.appendChild(tick);
    const label=svg("text");label.setAttribute("x",-46);label.setAttribute("y",y+4);label.setAttribute("class","svg-ruler-label");
    label.textContent=state.view==="side"?`Z ${Math.max(0,c.H-y)}`:`Y ${y}`;
    root.appendChild(label);
  }
}
function renderCanvas(){
  const c=CONTAINERS[state.containerKey], root=$("plan-svg");root.replaceChildren();
  const dimY=viewDimY(c), vb=currentViewBox();
  root.setAttribute("viewBox",`${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  addRulers(root,c,dimY);
  for(let x=0;x<=c.L;x+=100){const l=svg("line");l.setAttribute("x1",x);l.setAttribute("x2",x);l.setAttribute("y1",0);l.setAttribute("y2",dimY);l.setAttribute("class","svg-grid");root.appendChild(l)}
  for(let y=0;y<=dimY;y+=50){const l=svg("line");l.setAttribute("x1",0);l.setAttribute("x2",c.L);l.setAttribute("y1",y);l.setAttribute("y2",y);l.setAttribute("class","svg-grid");root.appendChild(l)}
  const cr=svg("rect");cr.setAttribute("x",0);cr.setAttribute("y",0);cr.setAttribute("width",c.L);cr.setAttribute("height",dimY);cr.setAttribute("class","svg-container");root.appendChild(cr);
  const reserve=clamp(+state.doorReserve||0,0,c.L);
  if(reserve>0){
    const rz=svg("rect");rz.setAttribute("x",c.L-reserve);rz.setAttribute("y",0);rz.setAttribute("width",reserve);rz.setAttribute("height",dimY);rz.setAttribute("class","svg-reserve");root.appendChild(rz);
    if(reserve>70){const rt=svg("text");rt.setAttribute("x",c.L-reserve+8);rt.setAttribute("y",22);rt.setAttribute("class","svg-reserve-label");rt.textContent="门口预留";root.appendChild(rt)}
  }
  if(state.view==="side"){const floor=svg("line");floor.setAttribute("x1",0);floor.setAttribute("x2",c.L);floor.setAttribute("y1",c.H);floor.setAttribute("y2",c.H);floor.setAttribute("class","svg-floor");root.appendChild(floor)}
  renderSnapGuides(root,c,dimY);
  renderSavedMeasurements(root);
  visiblePlacementEntries().forEach(({p,idx})=>{
    const r=rectForView(p,c), g=svg("g");g.dataset.idx=idx;
    if(!placementMatchesHighlight(p)&&!isSelected(idx))g.setAttribute("opacity",".18");
    const itemIssues=issuesForPlacement(p);
    const box=svg("rect");box.setAttribute("x",r.x);box.setAttribute("y",r.y);box.setAttribute("width",Math.max(0,r.w));box.setAttribute("height",Math.max(0,r.h));box.setAttribute("fill",p.color||"#777");box.setAttribute("class","svg-item"+issueClassForPlacement(p)+liveIssueClassForPlacement(p,idx)+(isSelected(idx)?" selected":"")+(p.locked?" locked":""));
    if(itemIssues.length){const title=svg("title");title.textContent=itemIssues.map(i=>i.message).join(" / ");box.appendChild(title)}
    g.appendChild(box);
    if(r.w>42&&r.h>18){const t=svg("text");t.setAttribute("x",r.x+5);t.setAttribute("y",r.y+14);t.setAttribute("class","svg-label");t.textContent=p.sku_model;g.appendChild(t)}
    root.appendChild(g);
  });
  if(state.selectionBox){
    const b=state.selectionBox, x=Math.min(b.x0,b.x1), y=Math.min(b.y0,b.y1), w=Math.abs(b.x1-b.x0), h=Math.abs(b.y1-b.y0);
    const sr=svg("rect");sr.setAttribute("x",x);sr.setAttribute("y",y);sr.setAttribute("width",w);sr.setAttribute("height",h);sr.setAttribute("class","svg-select-box");root.appendChild(sr);
  }
  renderSelectionDimensions(root,c);
  renderMeasurement(root);
  $("view-top").className=state.view==="top"?"primary":"";
  $("view-side").className=state.view==="side"?"primary":"";
  updateZoomLabel();
}
function numberField(label,field,p){
  const wrap=node("div","field"), lab=node("label","",label), i=input(p[field],v=>{const next=parseFloat(v)||0;if(p[field]===next)return;const before=snapshot();p[field]=next;clampPlacement(p);state.manualTouched=true;pushHistory(before);renderAll();recordActivity("精改坐标",`${p.sku_model} #${p.instance_id} ${field.toUpperCase()}=${p[field]}`,{render:true});validatePlan()},"number",{showZero:true});
  i.dataset.field=field;
  wrap.append(lab,i);return wrap;
}
function applyToSelection(mutator,{validate=true,activity=null}={}){
  const indices=selectedIndices();if(!indices.length)return;
  const before=snapshot();
  indices.forEach(i=>{const p=state.placements[i];if(p)mutator(p,i)});
  if(before===snapshot())return;
  state.manualTouched=true;pushHistory(before);renderAll();if(activity)recordActivity(activity.action,activity.detail,{render:true});if(validate)validatePlan();
}
function placementCountsBySku(){
  const counts={};state.placements.forEach(p=>{counts[p.sku_model]=(counts[p.sku_model]||0)+1});return counts;
}
function usedInstanceIdsBySku(){
  const ids={};
  state.placements.forEach(p=>{
    if(!ids[p.sku_model])ids[p.sku_model]=new Set();
    ids[p.sku_model].add(parseInt(p.instance_id)||0);
  });
  return ids;
}
function nextInstanceIdForSku(sku,ids){
  if(!ids[sku])ids[sku]=new Set();
  let id=1;while(ids[sku].has(id))id++;
  ids[sku].add(id);return id;
}
function canPastePlacementClipboard(){
  return !!(state.placementClipboard&&Array.isArray(state.placementClipboard.items)&&state.placementClipboard.items.length);
}
function copyPlacementSelection(){
  const entries=selectedIndices().map(i=>state.placements[i]).filter(Boolean);
  if(!entries.length){setStatus("先选择要复制的箱体。","warn");return}
  const origin={
    x:Math.min(...entries.map(p=>+p.x||0)),
    y:Math.min(...entries.map(p=>+p.y||0)),
    z:Math.min(...entries.map(p=>+p.z||0))
  };
  state.placementClipboard={
    copiedAt:new Date().toISOString(),
    view:state.view,
    origin,
    pasteCount:0,
    items:entries.map(p=>({
      sku_model:p.sku_model,relX:(+p.x||0)-origin.x,relY:(+p.y||0)-origin.y,relZ:(+p.z||0)-origin.z,
      length:+p.length||0,width:+p.width||0,height:+p.height||0,weight:+p.weight||0,
      color:p.color||"#777777",rotated:!!p.rotated
    }))
  };
  recordActivity("复制摆放",`${entries.length} 箱`,{render:true});
  renderInspector();
  setStatus(`已复制 ${entries.length} 箱摆放模式。`,"ok");
}
function pastePlacementClipboard(){
  const clip=state.placementClipboard;
  if(!canPastePlacementClipboard()){setStatus("还没有复制的摆放模式。","warn");return}
  const skuMap={};validItems().forEach(it=>skuMap[it.sku]=it);
  const counts=placementCountsBySku(), ids=usedInstanceIdsBySku();
  const before=snapshot(), created=[], skipped=[];
  const pasteNo=(parseInt(clip.pasteCount)||0)+1, offset=20*pasteNo;
  clip.items.forEach(item=>{
    const sku=skuMap[item.sku_model];
    if(!sku){skipped.push(item.sku_model);return}
    const limit=parseInt(sku.qty)||0;
    if((counts[item.sku_model]||0)>=limit){skipped.push(item.sku_model);return}
    const p={
      sku_model:item.sku_model,
      instance_id:nextInstanceIdForSku(item.sku_model,ids),
      x:(clip.origin.x||0)+item.relX+offset,
      y:(clip.origin.y||0)+item.relY,
      z:(clip.origin.z||0)+item.relZ,
      length:item.length,width:item.width,height:item.height,weight:item.weight,
      color:item.color||"#777777",rotated:!!item.rotated,locked:false
    };
    if(state.view==="side")p.z+=offset;else p.y+=offset;
    clampPlacement(p);
    state.placements.push(p);
    created.push(state.placements.length-1);
    counts[item.sku_model]=(counts[item.sku_model]||0)+1;
  });
  if(!created.length){setStatus("清单没有剩余箱数可粘贴。","warn");return}
  clip.pasteCount=pasteNo;
  state.manualTouched=true;state.sequenceMode=false;state.sequenceStep=state.placements.length;
  pushHistory(before);setSelection(created,created[created.length-1]);renderAll();
  const skipText=skipped.length?`，跳过 ${skipped.length} 箱`:"";
  recordActivity("粘贴摆放",`新增 ${created.length} 箱${skipText}`,{render:true});
  validatePlan();
  setStatus(`已粘贴 ${created.length} 箱摆放模式${skipText}。`,skipped.length?"warn":"ok");
}
function appendClipboardActions(root){
  const row=node("div","button-row");
  const copy=node("button","","复制摆放");copy.disabled=!selectedIndices().length;copy.onclick=copyPlacementSelection;
  const paste=node("button","",canPastePlacementClipboard()?`粘贴摆放(${state.placementClipboard.items.length})`:"粘贴摆放");
  paste.disabled=!canPastePlacementClipboard();paste.onclick=pastePlacementClipboard;
  row.append(copy,paste);root.appendChild(row);
}
function rotateSelection(){
  const count=selectedPlacements().filter(p=>!p.locked).length;
  applyToSelection(p=>{if(p.locked)return;[p.length,p.width]=[p.width,p.length];p.rotated=!p.rotated;clampPlacement(p)},{activity:{action:"旋转货物",detail:`${count} 箱`}});
}
function toggleLockSelection(){
  const count=selectedIndices().length;
  applyToSelection(p=>{p.locked=!p.locked},{validate:false,activity:{action:"切换锁定",detail:`${count} 箱`}});
}
function deleteSelection(){
  const indices=selectedIndices();if(!indices.length)return;
  const count=indices.length;
  const before=snapshot();
  indices.sort((a,b)=>b-a).forEach(i=>state.placements.splice(i,1));
  syncSequenceStep();
  state.manualTouched=true;setSelection([]);pushHistory(before);renderAll();recordActivity("删除货物",`${count} 箱`,{render:true});validatePlan();
}
function nudgeSelection(dx,dy,dz){
  const count=selectedPlacements().filter(p=>!p.locked).length;
  applyToSelection(p=>{if(p.locked)return;p.x+=dx;p.y+=dy;p.z+=dz;clampPlacement(p)},{activity:{action:"微调货物",detail:`${count} 箱，ΔX ${dx} / ΔY ${dy} / ΔZ ${dz} cm`}});
}
function alignSelection(axis){
  const items=selectedPlacements().filter(p=>!p.locked);if(!items.length)return;
  const target=axis==="z"?0:Math.min(...items.map(p=>p[axis]));
  applyToSelection(p=>{if(p.locked)return;p[axis]=target;clampPlacement(p)},{activity:{action:"对齐货物",detail:`${items.length} 箱，对齐 ${axis.toUpperCase()}`}});
}
function distributeSelection(axis){
  const indices=selectedIndices().filter(i=>!state.placements[i]?.locked);
  if(indices.length<3){setStatus("等距分布至少需要选择 3 箱未锁定货物。","warn");return}
  const sizeField=axis==="x"?"length":"width";
  const sorted=indices.map(i=>({i,p:state.placements[i]})).sort((a,b)=>(a.p[axis]+a.p[sizeField]/2)-(b.p[axis]+b.p[sizeField]/2));
  const first=sorted[0], last=sorted[sorted.length-1];
  const start=first.p[axis]+first.p[sizeField]/2, end=last.p[axis]+last.p[sizeField]/2;
  if(Math.abs(end-start)<1){setStatus("所选货物中心点重合，无法等距分布。","warn");return}
  const before=snapshot(), step=(end-start)/(sorted.length-1);
  sorted.forEach((item,idx)=>{
    const targetCenter=start+step*idx;
    item.p[axis]=targetCenter-item.p[sizeField]/2;
    clampPlacement(item.p);
  });
  if(before===snapshot())return;
  state.manualTouched=true;pushHistory(before);renderAll();recordActivity("等距分布",`${sorted.length} 箱，沿 ${axis.toUpperCase()} 轴`,{render:true});validatePlan();
}
function distributeSelectionByGap(axis,gapValue){
  const gap=snap(Math.max(0,parseFloat(gapValue)||0));
  const indices=selectedIndices().filter(i=>!state.placements[i]?.locked);
  if(indices.length<2){setStatus("按间距分布至少需要选择 2 箱未锁定货物。","warn");return}
  const c=CONTAINERS[state.containerKey], sizeField=axis==="x"?"length":"width", limit=axis==="x"?c.L:c.W;
  const sorted=indices.map(i=>({i,p:state.placements[i]})).sort((a,b)=>a.p[axis]-b.p[axis]||a.i-b.i);
  const total=sorted.reduce((sum,item)=>sum+(+item.p[sizeField]||0),0)+gap*(sorted.length-1);
  if(total>limit+EPS){setStatus(`间距 ${gap} cm 后总宽度 ${Math.round(total)} cm，已超过柜内 ${axis.toUpperCase()} 方向 ${limit} cm。`,"warn");return}
  let cursor=clamp(sorted[0].p[axis],0,Math.max(0,limit-total));
  const before=snapshot();
  sorted.forEach(item=>{
    item.p[axis]=cursor;
    cursor+=item.p[sizeField]+gap;
    clampPlacement(item.p);
  });
  if(before===snapshot())return;
  state.manualTouched=true;pushHistory(before);renderAll();recordActivity("按间距分布",`${sorted.length} 箱，${axis.toUpperCase()} 间距 ${gap} cm`,{render:true});validatePlan();
}
function snapSelection(edge){
  const c=CONTAINERS[state.containerKey], reserve=clamp(+state.doorReserve||0,0,c.L);
  const items=selectedPlacements().filter(p=>!p.locked);if(!items.length)return;
  const labels={left:"贴左",right:"贴右",head:"贴柜头",door:"贴门口",centerY:"贴中线"};
  applyToSelection(p=>{
    if(p.locked)return;
    if(edge==="left")p.y=0;
    if(edge==="right")p.y=c.W-p.width;
    if(edge==="head")p.x=0;
    if(edge==="door")p.x=c.L-reserve-p.length;
    if(edge==="centerY")p.y=(c.W-p.width)/2;
    clampPlacement(p);
  },{activity:{action:"贴边整理",detail:`${items.length} 箱，${labels[edge]||edge}`}});
}
function renderInspector(){
  const root=$("inspector");clear(root);const p=selected(), indices=selectedIndices();
  if(!p){root.appendChild(node("div","empty","单击选择；Ctrl/Shift 加选；空白处拖拽框选；方向键微调。"));appendClipboardActions(root);return}
  if(indices.length>1){
    const locked=indices.filter(i=>state.placements[i]?.locked).length;
    root.append(node("div","hint",`已选择 ${indices.length} 箱 · ${locked} 箱锁定`));
    const row=node("div","button-row");
    const rotate=node("button","primary","批量旋转");rotate.onclick=rotateSelection;
    const lock=node("button","","切换锁定");lock.onclick=toggleLockSelection;
    const del=node("button","danger","删除所选");del.onclick=deleteSelection;
    row.append(rotate,lock,del);root.appendChild(row);
    appendClipboardActions(root);
    const move=node("div","button-row");
    [["←",[-5,0,0]],["→",[5,0,0]],["↑",state.view==="side"?[0,0,5]:[0,-5,0]],["↓",state.view==="side"?[0,0,-5]:[0,5,0]]].forEach(([label,d])=>{const b=node("button","",label+" 5cm");b.onclick=()=>nudgeSelection(...d);move.appendChild(b)});
    root.appendChild(move);
    const align=node("div","button-row");
    [["对齐 X","x"],["对齐 Y","y"],["落地 Z","z"]].forEach(([label,axis])=>{const b=node("button","",label);b.onclick=()=>alignSelection(axis);align.appendChild(b)});
    root.appendChild(align);
    const distribute=node("div","button-row");
    [["等距 X","x"],["等距 Y","y"],["贴左","left"],["贴右","right"],["贴门口","door"]].forEach(([label,action])=>{
      const b=node("button","",label);
      b.onclick=()=>action==="x"||action==="y"?distributeSelection(action):snapSelection(action);
      distribute.appendChild(b);
    });
    root.appendChild(distribute);
    const snapMore=node("div","button-row");
    [["贴柜头","head"],["贴中线","centerY"]].forEach(([label,edge])=>{
      const b=node("button","",label);b.onclick=()=>snapSelection(edge);snapMore.appendChild(b);
    });
    root.appendChild(snapMore);
    const gapFields=node("div","fields");
    const gapX=node("div","field"), gapXLabel=node("label","","X 间距(cm)"), gapXInput=node("input");
    gapXInput.type="number";gapXInput.min="0";gapXInput.step="5";gapXInput.placeholder="例如 10";
    gapX.append(gapXLabel,gapXInput);
    const gapY=node("div","field"), gapYLabel=node("label","","Y 间距(cm)"), gapYInput=node("input");
    gapYInput.type="number";gapYInput.min="0";gapYInput.step="5";gapYInput.placeholder="例如 5";
    gapY.append(gapYLabel,gapYInput);
    gapFields.append(gapX,gapY);root.appendChild(gapFields);
    const gapActions=node("div","button-row");
    const gapXBtn=node("button","","按间距 X");gapXBtn.onclick=()=>distributeSelectionByGap("x",gapXInput.value);
    const gapYBtn=node("button","","按间距 Y");gapYBtn.onclick=()=>distributeSelectionByGap("y",gapYInput.value);
    gapActions.append(gapXBtn,gapYBtn);root.appendChild(gapActions);
    root.append(node("div","hint","按住 Shift 使用方向键每次移动 20cm。侧视图的 ↑/↓ 调整高度。"));
    return;
  }
  root.append(node("div","hint",`${p.sku_model} / 第 ${p.instance_id} 箱`));
  const fields=node("div","fields");["x","y","z","length","width","height"].forEach(f=>fields.appendChild(numberField(f.toUpperCase(),f,p)));root.appendChild(fields);
  const row=node("div","button-row");
  const rotate=node("button","primary","旋转 90°");rotate.onclick=rotateSelection;
  const lock=node("button","",p.locked?"解除锁定":"锁定");lock.onclick=toggleLockSelection;
  const del=node("button","danger","移除选中");del.onclick=deleteSelection;
  row.append(rotate,lock,del);root.appendChild(row);
  appendClipboardActions(root);
}
function renderAll(){renderContainers();renderModes();renderRules();renderProjectInfo();renderItems();renderImportPreview();renderHighlightPicker();renderLayerPicker();renderSequenceControls();renderToolButtons();renderCanvas();renderStats();renderIssues();renderInspector();renderWorkflow();renderActivityLog();renderMeasurementList();renderViewPresetList();$("btn-undo").disabled=!state.history.length;$("btn-redo").disabled=!state.future.length;updateDraftButtons();scheduleAutoDraft()}
function clampPlacement(p,{grid=true}={}){
  const c=CONTAINERS[state.containerKey];
  const norm=v=>grid?snap(v):v;
  p.x=clamp(norm(p.x),0,Math.max(0,c.L-p.length));p.y=clamp(norm(p.y),0,Math.max(0,c.W-p.width));p.z=clamp(norm(p.z),0,Math.max(0,c.H-p.height));
}
function svgPoint(evt){const s=$("plan-svg"),pt=s.createSVGPoint();pt.x=evt.clientX;pt.y=evt.clientY;return pt.matrixTransform(s.getScreenCTM().inverse())}
function rectsIntersect(a,b){return a.x < b.x+b.w && b.x < a.x+a.w && a.y < b.y+b.h && b.y < a.y+a.h}
function indicesInBox(box){
  const c=CONTAINERS[state.containerKey], r={x:Math.min(box.x0,box.x1),y:Math.min(box.y0,box.y1),w:Math.abs(box.x1-box.x0),h:Math.abs(box.y1-box.y0)};
  return visiblePlacementEntries().map(({p,idx})=>({idx,rp:rectForView(p,c)})).filter(x=>rectsIntersect(x.rp,r)).map(x=>x.idx);
}

$("plan-svg").addEventListener("pointerdown",evt=>{
  const target=evt.target.closest("[data-idx]"), pt=svgPoint(evt);
  if(evt.altKey||evt.button===1){
    drag={type:"pan",startClient:{x:evt.clientX,y:evt.clientY},viewBox:{...currentViewBox()}};
    $("plan-svg").setPointerCapture(evt.pointerId);
    return;
  }
  if(state.measureMode){
    const p=clampCanvasPoint(pt);
    state.measurement={view:state.view,x0:p.x,y0:p.y,x1:p.x,y1:p.y};
    drag={type:"measure",start:p};
    updateMeasureReadout();
    renderCanvas();$("plan-svg").setPointerCapture(evt.pointerId);return;
  }
  if(!target){
    const base=(evt.ctrlKey||evt.shiftKey)?selectedIndices():[];
    state.selectionBox={x0:pt.x,y0:pt.y,x1:pt.x,y1:pt.y};
    if(!base.length)setSelection([]);
    drag={type:"box",start:pt,base,additive:evt.ctrlKey||evt.shiftKey};
    renderCanvas();$("plan-svg").setPointerCapture(evt.pointerId);return;
  }
  const idx=parseInt(target.dataset.idx), current=selectedIndices();
  if(evt.ctrlKey||evt.shiftKey){
    const next=current.includes(idx)?current.filter(i=>i!==idx):current.concat(idx);
    setSelection(next,idx);
  }else if(!current.includes(idx)){
    setSelection([idx],idx);
  }else{
    setSelection(current,idx);
  }
  renderAll();
  const moving=selectedIndices().filter(i=>!state.placements[i]?.locked);
  if(!moving.length)return;
  drag={type:"move",indices:moving,start:pt,before:snapshot(),positions:moving.map(i=>({i,x:state.placements[i].x,y:state.placements[i].y,z:state.placements[i].z}))};
  $("plan-svg").setPointerCapture(evt.pointerId);
});
$("plan-svg").addEventListener("pointermove",evt=>{
  const pt=svgPoint(evt);updateCoordReadout(pt);
  if(!drag)return;
  if(drag.type==="pan"){
    const rect=$("plan-svg").getBoundingClientRect();
    const dx=(evt.clientX-drag.startClient.x)*drag.viewBox.w/rect.width;
    const dy=(evt.clientY-drag.startClient.y)*drag.viewBox.h/rect.height;
    setViewBox({...drag.viewBox,x:drag.viewBox.x-dx,y:drag.viewBox.y-dy});
    renderCanvas();
    return;
  }
  const dx=pt.x-drag.start.x,dy=pt.y-drag.start.y;
  if(drag.type==="measure"){
    const p=clampCanvasPoint(pt);
    state.measurement={view:state.view,x0:drag.start.x,y0:drag.start.y,x1:p.x,y1:p.y};
    updateMeasureReadout();
    renderCanvas();return;
  }
  if(drag.type==="box"){
    state.selectionBox={x0:drag.start.x,y0:drag.start.y,x1:pt.x,y1:pt.y};
    const inside=indicesInBox(state.selectionBox);
    setSelection(drag.additive?[...drag.base,...inside]:inside,inside.length?inside[inside.length-1]:null);
    renderCanvas();renderInspector();return;
  }
  const snapped=snapDragDelta(dx,dy);
  drag.guides=snapped.guides;
  drag.positions.forEach(pos=>{const p=state.placements[pos.i];if(!p)return;if(state.view==="side"){p.x=pos.x+snapped.dx;p.z=pos.z-snapped.dy}else{p.x=pos.x+snapped.dx;p.y=pos.y+snapped.dy}clampPlacement(p,{grid:false})});
  updateDragReadout(snapped.dx,snapped.dy);
  renderCanvas();renderStats();renderInspector();
});
$("plan-svg").addEventListener("pointerup",evt=>{
  if(!drag)return;
  const wasMove=drag.type==="move", wasMeasure=drag.type==="measure", before=drag.before, movedCount=drag.indices?drag.indices.length:0;
  drag=null;state.selectionBox=null;
  if(wasMove&&before!==snapshot()){state.manualTouched=true;pushHistory(before);recordActivity("拖拽调整",`${movedCount} 箱`);validatePlan()}
  if(wasMeasure)updateMeasureReadout();
  renderAll();try{$("plan-svg").releasePointerCapture(evt.pointerId)}catch(e){}
});
$("plan-svg").addEventListener("wheel",evt=>{
  evt.preventDefault();
  const pt=svgPoint(evt);
  zoomCanvas(evt.deltaY<0?1.15:1/1.15,pt);
  updateCoordReadout(pt);
},{passive:false});

async function apiJSON(url,payload){
  const resp=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  if(!resp.ok)throw new Error(await resp.text());return await resp.json();
}
async function calculate(){
  const skus=skuPayload();if(!skus.length){setStatus("请至少填写一件有效货物。","warn");return}
  setStatus("正在自动排柜...");$("btn-calc").disabled=true;
  try{
    const data=await apiJSON("/api/pack",{container_type:state.containerKey,pack_mode:state.packMode,skus,...rulesPayload()});
    state.placements=(data.placements||[]).map(p=>({...p,locked:false}));state.manualTouched=false;state.sequenceMode=false;state.sequenceStep=state.placements.length;state.layerFilter="all";state.validation=data.validation||[];state.stats=data.stats;state.lastPng=data.png_base64;setSelection([]);state.history=[];state.future=[];
    recordActivity("自动排柜",`${state.placements.length} 箱，${state.validation.length} 个问题`);
    renderAll();setStatus(`已生成方案：${state.placements.length} 箱，${state.validation.length} 个问题。`,state.validation.length?"warn":"ok");
  }catch(e){setStatus("自动排柜失败："+(e.message||e),"err")}finally{$("btn-calc").disabled=false}
}
async function repackUnlocked(){
  const skus=skuPayload();if(!skus.length){setStatus("请至少填写一件有效货物。","warn");return}
  const before=snapshot(), locked=state.placements.filter(p=>p.locked);
  setStatus(locked.length?`正在保留 ${locked.length} 箱并重排剩余货物...`:"正在重排全部未锁定货物...");
  $("btn-repack").disabled=true;
  try{
    const data=await apiJSON("/api/repack_unlocked",{container_type:state.containerKey,skus,locked_placements:placementPayload(locked),...rulesPayload()});
    state.placements=(data.placements||[]).map(p=>({...p,locked:!!p.locked}));
    state.sequenceMode=false;state.sequenceStep=state.placements.length;state.layerFilter="all";
    state.validation=data.validation||[];state.stats=data.stats;setSelection([]);pushHistory(before);recordActivity("重排未锁定",`保留 ${locked.length} 箱，当前 ${state.placements.length} 箱，${state.validation.length} 个问题`);renderAll();
    setStatus(`已重排：保留 ${locked.length} 箱，当前 ${state.placements.length} 箱，${state.validation.length} 个问题。`,state.validation.length?"warn":"ok");
  }catch(e){setStatus("重排失败："+(e.message||e),"err")}finally{$("btn-repack").disabled=false}
}
async function repackCurrentLayer(){
  const skus=skuPayload();if(!skus.length){setStatus("请至少填写一件有效货物。","warn");return}
  if(state.layerFilter==="all"){setStatus("请先在“层”下拉框选择一个具体 Z 层。","warn");return}
  const targetLayer=parseFloat(state.layerFilter);
  const layerEntries=state.placements.map((p,idx)=>({p,idx})).filter(({p})=>placementLayer(p)===targetLayer);
  const movable=layerEntries.filter(({p})=>!p.locked);
  if(!movable.length){setStatus("当前层没有未锁定货物可重排。","warn");return}
  const hasUpper=state.placements.some(p=>placementLayer(p)>targetLayer);
  if(hasUpper&&!confirm(`当前 Z=${targetLayer} cm 层上方还有货物。只重排本层可能改变上层支撑关系，重排后必须复核校验结果。仍继续？`)){
    setStatus("已取消重排当前层。","warn");return;
  }
  const before=snapshot();
  const fixedCount=state.placements.length-movable.length;
  const btn=$("btn-repack-layer");if(btn)btn.disabled=true;
  setStatus(`正在只重排 Z=${targetLayer} cm 当前层，其他 ${fixedCount} 箱临时固定...`);
  try{
    const result=repackLayerPlane(targetLayer,movable);
    state.placements=result.placements;
    state.manualTouched=true;
    state.sequenceMode=false;state.sequenceStep=state.placements.length;state.layerFilter=String(targetLayer);
    setSelection(movable.map(e=>e.idx),movable[movable.length-1].idx);pushHistory(before);
    recordActivity("重排当前层",`Z=${targetLayer} cm，重排 ${movable.length} 箱，移动 ${result.moved} 箱，临时固定 ${fixedCount} 箱`);
    renderAll();
    validatePlan();
    setStatus(`已重排当前层 Z=${targetLayer} cm：${movable.length} 箱${result.failed?`，${result.failed} 箱保留原位`:""}，正在校验。`,result.failed?"warn":"ok");
  }catch(e){setStatus("重排当前层失败："+(e.message||e),"err")}finally{if(btn)btn.disabled=false}
}
async function validatePlan(activity=null){
  clearTimeout(validateTimer);validateTimer=setTimeout(async()=>{
    if(!state.placements.length){state.validation=[];renderIssues();if(activity)recordActivity(activity.action,"无方案可校验",{render:true});return}
    try{const data=await apiJSON("/api/validate_plan",{container_type:state.containerKey,skus:skuPayload(),placements:placementPayload(),...rulesPayload()});state.validation=data.validation||[];renderIssues();renderCanvas();if(activity)recordActivity(activity.action,state.validation.length?`${state.validation.length} 个问题`:"校验通过",{render:true});setStatus(state.validation.length?`校验发现 ${state.validation.length} 个问题。`:"校验通过。",state.validation.length?"warn":"ok")}
    catch(e){setStatus("校验失败："+(e.message||e),"err")}
  },180);
}
async function exportPNG(){
  if(!state.placements.length){setStatus("没有可导出的方案。","warn");return}
  setStatus("正在渲染 PNG...");
  try{
    const data=await apiJSON("/api/render_plan",{container_type:state.containerKey,skus:skuPayload(),placements:placementPayload(),...rulesPayload()});
    state.validation=data.validation||[];state.stats=data.stats;recordActivity("导出 PNG",`${state.placements.length} 箱，${state.validation.length} 个问题`);renderAll();downloadBase64(data.png_base64,`装柜方案_${state.containerKey}_${stamp()}.png`);setStatus("PNG 已生成。",state.validation.length?"warn":"ok");
  }catch(e){setStatus("导出失败："+(e.message||e),"err")}
}
function stamp(){return new Date().toISOString().replace(/[:.]/g,"-").slice(0,16)}
function downloadBase64(b64,name){const a=node("a");a.download=name;a.href="data:image/png;base64,"+b64;a.click()}
function downloadBase64File(b64,name,type="application/octet-stream"){const a=node("a");a.download=name;a.href=`data:${type};base64,${b64}`;a.click()}
function downloadText(text,name,type="text/plain;charset=utf-8"){
  const a=node("a");a.download=name;a.href=URL.createObjectURL(new Blob([text],{type}));a.click();URL.revokeObjectURL(a.href);
}
function csvCell(value){
  const s=String(value??"");
  return /[",\r\n]/.test(s)?`"${s.replace(/"/g,'""')}"`:s;
}
function exportCSV(){
  if(!state.placements.length){setStatus("没有可导出的装柜明细。","warn");return}
  const rows=[["装柜顺序","SKU","箱号","X(cm)","Y(cm)","Z(cm)","长(cm)","宽(cm)","高(cm)","重量(kg)","是否旋转","是否锁定"]];
  state.placements.forEach((p,idx)=>rows.push([idx+1,p.sku_model,p.instance_id,p.x,p.y,p.z,p.length,p.width,p.height,p.weight,p.rotated?"是":"否",p.locked?"是":"否"]));
  downloadText("\ufeff"+rows.map(r=>r.map(csvCell).join(",")).join("\r\n"),`装柜明细_${state.containerKey}_${stamp()}.csv`,"text/csv;charset=utf-8");
  recordActivity("导出 CSV",`${state.placements.length} 箱`,{render:true});
  setStatus("CSV 明细已生成。","ok");
}
async function exportWorkbook(){
  if(!state.placements.length){setStatus("没有可导出的 Excel 工作簿。","warn");return}
  setStatus("正在生成 Excel 工作簿...");
  try{
    const data=await apiJSON("/api/export_workbook",{
      container_type:state.containerKey,
      skus:skuPayload(),
      placements:placementPayload(),
      project_info:withProjectInfo(state.projectInfo),
      activity_log:state.activityLog||[],
      manual_touched:!!state.manualTouched,
      ...rulesPayload()
    });
    state.validation=data.validation||[];
    state.stats=data.stats;
    recordActivity("导出 Excel",`${state.placements.length} 箱，${state.validation.length} 个问题`,{render:true});
    renderAll();
    downloadBase64File(
      data.xlsx_base64,
      data.filename||`装柜工作簿_${state.containerKey}_${stamp()}.xlsx`,
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    setStatus("Excel 工作簿已生成。",state.validation.length?"warn":"ok");
  }catch(e){setStatus("导出 Excel 失败："+(e.message||e),"err")}
}
function escapeHTML(value){return String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]))}
function currentPlanSVG(){
  const source=$("plan-svg");if(!source)return "";
  const clone=source.cloneNode(true);
  clone.setAttribute("xmlns",NS);
  clone.removeAttribute("aria-label");
  return new XMLSerializer().serializeToString(clone);
}
function planSVGForLimit(limit){
  const oldMode=state.sequenceMode, oldStep=state.sequenceStep, oldLayer=state.layerFilter, oldMeasureMode=state.measureMode, oldMeasurement=state.measurement, oldSelectedIndex=state.selectedIndex, oldSelectedIndices=[...(state.selectedIndices||[])];
  state.sequenceMode=true;
  state.sequenceStep=clamp(parseInt(limit)||0,0,state.placements.length);
  state.layerFilter="all";
  state.measureMode=false;
  state.measurement=null;
  state.selectedIndex=null;
  state.selectedIndices=[];
  renderCanvas();
  const svgText=currentPlanSVG();
  state.sequenceMode=oldMode;
  state.sequenceStep=oldStep;
  state.layerFilter=oldLayer;
  state.measureMode=oldMeasureMode;
  state.measurement=oldMeasurement;
  state.selectedIndex=oldSelectedIndex;
  state.selectedIndices=oldSelectedIndices;
  renderCanvas();
  return svgText;
}
function fullPlanSVG(){
  return planSVGForLimit(state.placements.length);
}
function stepSnapshotsHTML(){
  const total=state.placements.length;if(!total)return "";
  const steps=[Math.ceil(total*.25),Math.ceil(total*.5),Math.ceil(total*.75),total]
    .filter((v,i,a)=>v>0&&a.indexOf(v)===i);
  return `<h2>装柜步骤快照</h2><div class="stepshots">${steps.map(n=>`<div class="step-shot"><b>第 ${n} / ${total} 箱</b>${planSVGForLimit(n)}</div>`).join("")}</div>`;
}
function confirmReportPreflight(){
  const items=workflowSteps().filter(step=>["bad","warn"].includes(step.status));
  if(!items.length)return true;
  const lines=items.map(step=>`${step.title}：${step.detail}`).join("\n");
  return confirm(`当前方案还有需要复核的事项：\n\n${lines}\n\n仍然导出报告？`);
}
function exportReport(){
  if(!state.placements.length){setStatus("没有可导出的方案报告。","warn");return}
  if(!confirmReportPreflight()){setStatus("已取消导出报告。","warn");return}
  updateLocalStats();
  const safety=safetySummary();
  recordActivity("导出报告",`${safety.label}，${state.placements.length} 箱，${(state.validation||[]).length} 个问题`,{render:true});
  const info=withProjectInfo(state.projectInfo), reportTitle=info.name||"装柜方案报告";
  const infoRows=[
    ["方案名",info.name],
    ["柜号/车号",info.containerNo],
    ["方案版本",info.revision],
    ["制单人",info.preparedBy],
    ["复核人",info.reviewedBy],
    ["现场确认人",info.confirmedBy],
    ["备注",info.note],
  ].filter(([,v])=>String(v||"").trim()).map(([k,v])=>`<tr><th>${escapeHTML(k)}</th><td>${escapeHTML(v)}</td></tr>`).join("");
  const workflowLabel={done:"完成",warn:"待复核",bad:"需处理",wait:"待开始"};
  const workflowRows=workflowSteps().map(step=>`<tr><td>${escapeHTML(step.title)}</td><td>${escapeHTML(workflowLabel[step.status]||step.status)}</td><td>${escapeHTML(step.detail)}</td></tr>`).join("");
  const safetyRows=safety.reasons.map(reason=>`<tr><td>${escapeHTML(reason)}</td></tr>`).join("");
  const safetySection=`<h2>安全结论</h2><table class="meta"><tbody><tr><th>结论</th><td><b>${escapeHTML(safety.label)}</b></td></tr><tr><th>说明</th><td>${escapeHTML(safety.detail)}</td></tr></tbody></table><table><thead><tr><th>复核要点</th></tr></thead><tbody>${safetyRows}</tbody></table>`;
  const activityRows=(state.activityLog||[]).length?(state.activityLog||[]).slice(-40).map(item=>`<tr><td>${escapeHTML(activityTimeLabel(item.time))}</td><td>${escapeHTML(item.action)}</td><td>${escapeHTML(item.detail)}</td></tr>`).join(""):`<tr><td colspan="3">无</td></tr>`;
  const activitySection=`<h2>操作记录</h2><table><thead><tr><th>时间</th><th>动作</th><th>说明</th></tr></thead><tbody>${activityRows}</tbody></table>`;
  state.savedMeasurements=normalizedMeasurements(state.savedMeasurements);
  const measurementRows=(state.savedMeasurements||[]).length?(state.savedMeasurements||[]).map((m,idx)=>{const ms=measurementSummary(m,m.view);return `<tr><td>${escapeHTML(measurementName(m,idx))}</td><td>${escapeHTML(m.view==="side"?"侧视":"俯视")}</td><td>${escapeHTML(ms?Math.round(ms.distance):0)} cm</td><td>ΔX ${escapeHTML(ms?Math.round(ms.dx):0)} / Δ${escapeHTML(ms?ms.label:"Y")} ${escapeHTML(ms?Math.round(ms.dv):0)} cm</td><td>${escapeHTML(measurementNote(m))}</td></tr>`}).join(""):`<tr><td colspan="5">无</td></tr>`;
  const measurementSection=`<h2>测量标注</h2><table><thead><tr><th>标注</th><th>视图</th><th>距离</th><th>分量</th><th>备注</th></tr></thead><tbody>${measurementRows}</tbody></table>`;
  const s=state.stats, c=CONTAINERS[state.containerKey], issueRows=state.validation.length?state.validation.map(i=>`<tr><td>${escapeHTML(i.severity)}</td><td>${escapeHTML(i.code)}</td><td>${escapeHTML(i.item||"")}</td><td>${escapeHTML(i.message)}</td></tr>`).join(""):`<tr><td colspan="4">无</td></tr>`;
  const segmentLimitText=(s.max_segment_limit_kg||0)>0?`限值 ${s.max_segment_limit_kg} kg`:"按柜长 6 段粗分";
  const skuRows=validItems().map(it=>`<tr><td>${escapeHTML(it.sku)}</td><td>${escapeHTML(it.supplier)}</td><td>${escapeHTML(it.L)}×${escapeHTML(it.W)}×${escapeHTML(it.H)}</td><td>${escapeHTML(it.kg)}</td><td>${escapeHTML(it.maxTop||0)}</td><td>${escapeHTML(it.qty)}</td><td>${escapeHTML(it.mode)}</td></tr>`).join("");
  const segmentRows=(s.weight_segments||[]).map((seg,idx)=>`<tr><td>${idx+1}</td><td>${escapeHTML(seg.from_cm)} - ${escapeHTML(seg.to_cm)}</td><td>${escapeHTML(seg.weight_kg)} kg</td></tr>`).join("");
  const placementRows=state.placements.map((p,idx)=>`<tr><td>${idx+1}</td><td>${escapeHTML(p.sku_model)}</td><td>${escapeHTML(p.instance_id)}</td><td>${escapeHTML(p.x)}, ${escapeHTML(p.y)}, ${escapeHTML(p.z)}</td><td>${escapeHTML(p.length)}×${escapeHTML(p.width)}×${escapeHTML(p.height)}</td><td>${escapeHTML(p.weight)}</td><td>${p.locked?"是":"否"}</td></tr>`).join("");
  let html=`<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>${escapeHTML(reportTitle)}</title><style>body{font-family:"Segoe UI","Microsoft YaHei",sans-serif;margin:32px;color:#111}h1{margin:0 0 8px}h2{margin-top:26px;border-bottom:1px solid #ddd;padding-bottom:6px}table{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}th,td{border:1px solid #ddd;padding:7px;text-align:left}th{background:#f3f4f6}.meta{max-width:720px}.meta th{width:120px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0}.stat{border:1px solid #ddd;padding:12px}.stat b{font-size:20px;display:block}.muted{color:#666}.plan{border:1px solid #ddd;background:#0b1015;margin-top:10px;overflow:auto}.plan svg{width:100%;height:360px;display:block}.stepshots{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.step-shot{border:1px solid #ddd;background:#0b1015;padding:8px}.step-shot b{display:block;color:#333;background:#f3f4f6;margin:-8px -8px 8px;padding:6px}.step-shot svg{width:100%;height:210px;display:block}.svg-grid{stroke:#27313a;stroke-width:1}.svg-container{fill:#0e151b;stroke:#d6e4f0;stroke-width:3}.svg-item{stroke:#091117;stroke-width:1}.svg-item.selected{stroke:#fff;stroke-width:3}.svg-item.locked{stroke-dasharray:6 4;opacity:.72}.svg-item.issue-error{stroke:#fb7185;stroke-width:4}.svg-item.issue-warning{stroke:#fbbf24;stroke-width:3}.svg-label{fill:#f8fbff;font-size:12px;font-weight:700}.svg-floor{stroke:#f59e0b;stroke-width:2;stroke-dasharray:8 6}.svg-reserve{fill:rgba(251,113,133,.16);stroke:#fb7185;stroke-width:2;stroke-dasharray:10 6}.svg-reserve-label{fill:#ffd7df;font-size:13px;font-weight:800}.svg-ruler{stroke:#526273;stroke-width:1}.svg-ruler-label{fill:#8fa1b2;font-size:11px}.svg-saved-measure{stroke:#41b6e6;stroke-width:2;stroke-dasharray:7 5}.svg-saved-measure-point{fill:#41b6e6;stroke:#0b1015;stroke-width:2}.svg-saved-measure-label{fill:#d7f5ff;font-size:12px;font-weight:800}.svg-select-box{display:none}</style></head><body><h1>${escapeHTML(reportTitle)}</h1><div class="muted">生成时间：${escapeHTML(new Date().toLocaleString())}</div>${infoRows?`<h2>方案信息</h2><table class="meta"><tbody>${infoRows}</tbody></table>`:""}<h2>作业流程</h2><table><thead><tr><th>步骤</th><th>状态</th><th>说明</th></tr></thead><tbody>${workflowRows}</tbody></table><div class="stats"><div class="stat">柜型<b>${escapeHTML(state.containerKey)}</b><span>${escapeHTML(c.name)}</span></div><div class="stat">空间利用率<b>${escapeHTML(s.cbm_util_pct)}%</b><span>${escapeHTML(s.cbm_used)} / ${escapeHTML(s.cbm_capacity)} m³</span></div><div class="stat">总重量<b>${escapeHTML(s.weight_total_kg)} kg</b><span>限重 ${escapeHTML(s.weight_max_kg)} kg</span></div><div class="stat">箱数<b>${escapeHTML(s.placed_count)} / ${escapeHTML(s.total_count)}</b><span>未放 ${escapeHTML(s.unfitted.reduce((a,u)=>a+u.count,0))}</span></div><div class="stat">门口预留<b>${escapeHTML(s.door_reserve_cm||0)} cm</b><span>可用柜长 ${escapeHTML(s.usable_length_cm||c.L)} cm</span></div><div class="stat">重心 X<b>${escapeHTML(s.center_x_pct||0)}%</b><span>${escapeHTML(s.center_x_cm||0)} cm 距柜头</span></div><div class="stat">前/后重<b>${escapeHTML(s.front_weight_kg||0)} / ${escapeHTML(s.rear_weight_kg||0)} kg</b><span>按柜长中线粗分</span></div><div class="stat">左/右重<b>${escapeHTML(s.left_weight_kg||0)} / ${escapeHTML(s.right_weight_kg||0)} kg</b><span>横向重心 ${escapeHTML(s.center_y_pct||0)}%</span></div><div class="stat">最重分段<b>${escapeHTML(s.max_segment_weight_kg||0)} kg</b><span>${escapeHTML(segmentLimitText)}</span></div></div><h2>装柜示意图</h2><div class="muted">装柜明细中的“装柜顺序”可用于现场逐箱回放和复核。</div><div class="plan">${fullPlanSVG()}</div>${stepSnapshotsHTML()}<h2>分段重量</h2><table><thead><tr><th>段</th><th>X 范围(cm)</th><th>重量</th></tr></thead><tbody>${segmentRows}</tbody></table><h2>货物清单</h2><table><thead><tr><th>SKU</th><th>厂家</th><th>尺寸(cm)</th><th>单箱重</th><th>上压限重</th><th>箱数</th><th>规则</th></tr></thead><tbody>${skuRows}</tbody></table><h2>校验结果</h2><table><thead><tr><th>级别</th><th>代码</th><th>对象</th><th>说明</th></tr></thead><tbody>${issueRows}</tbody></table><h2>装柜明细</h2><table><thead><tr><th>顺序</th><th>SKU</th><th>箱号</th><th>坐标 X,Y,Z</th><th>尺寸(cm)</th><th>重量</th><th>锁定</th></tr></thead><tbody>${placementRows}</tbody></table></body></html>`;
  html=html.replace(`<h2>作业流程</h2>`,`${safetySection}<h2>作业流程</h2>`);
  html=html.replace(`</tbody></table><div class="stats">`,`</tbody></table>${activitySection}${measurementSection}<div class="stats">`);
  downloadText(html,`装柜报告_${state.containerKey}_${stamp()}.html`,"text/html;charset=utf-8");
  setStatus("HTML 报告已生成。","ok");
}
function saveProject(){
  recordActivity("保存项目",`导出 .cpack 项目文件，版本 ${state.projectInfo.revision||"未填"}`,{render:true});
  const data=projectPayload();
  const a=node("a");a.download=`装柜项目_${stamp()}.cpack`;a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));a.click();URL.revokeObjectURL(a.href)
}
function loadProjectFile(file){const r=new FileReader();r.onload=()=>{try{const d=JSON.parse(r.result);applyProjectData(d,{activity:"打开项目",detail:`读取项目文件，版本 ${withProjectInfo(d.projectInfo).revision||"未填"}`,status:"项目已打开。"})}catch(e){setStatus("项目文件无法解析。","err")}};r.readAsText(file)}
function appendSkus(skus,action="识别入表"){state.items=state.items.filter(it=>it.sku||it.L||it.W||it.H||it.qty);skus.forEach(s=>{let mode=s.stack_mode||"full";state.items.push({sku:s.model||"",supplier:s.supplier||"",order:parseInt(s.arrival_order||s.order)||1,L:s.length||0,W:s.width||0,H:s.height||0,kg:s.weight||0,maxTop:s.max_top_load_kg||0,qty:s.qty||0,mode,side:s.upright_only===false,note:s.note||""})});if(!state.items.length)state.items=[blank()];recordActivity(action,`追加 ${skus.length} 行`,{render:true});renderItems();setStatus(`已追加 ${skus.length} 行识别结果。`,"ok")}
function importIssueLines(issues,limit=5){return (issues||[]).slice(0,limit).map(i=>`${i.row?`第 ${i.row} 行`:"提示"}：${i.message}`).join("\n")}
function showImportFeedback(data){
  const box=$("import-feedback");if(!box)return;
  const s=data.summary||{}, issues=data.issues||[];
  const head=`上次导入：有效 ${s.imported_rows||0} 行，错误 ${s.error_count||0} 个，警告 ${s.warning_count||0} 个。`;
  const detail=importIssueLines(issues,3).replace(/\n/g,"；");
  box.textContent=detail?`${head} ${detail}`:head;
}
async function importManifestFile(file){
  if(!file)return;
  setStatus("正在解析清单...");
  try{
    const form=new FormData();form.append("file",file);
    const resp=await fetch("/api/import_manifest",{method:"POST",body:form});
    if(!resp.ok)throw new Error(await resp.text());
    const data=await resp.json(), issues=data.issues||[], summary=data.summary||{};
    state.importPreview=data;
    showImportFeedback(data);
    renderImportPreview();
    if(!data.skus||!data.skus.length){setStatus("清单没有可导入的有效行，请查看预览问题。","warn");return}
    setStatus(`清单预览已生成：有效 ${summary.imported_rows||data.skus.length} 行，请确认追加。`,issues.length?"warn":"ok");
  }catch(e){setStatus("导入清单失败："+(e.message||e),"err")}
}
function commitImportPreview(){
  const data=state.importPreview;
  if(!data||!data.skus||!data.skus.length){setStatus("没有可追加的清单预览。","warn");return}
  appendSkus(data.skus,"确认导入清单");
  showImportFeedback(data);
  state.importPreview=null;
  renderImportPreview();
  setStatus(`已追加 ${data.skus.length} 行清单。`,(data.issues||[]).length?"warn":"ok");
}
function cancelImportPreview(){
  state.importPreview=null;
  renderImportPreview();
  setStatus("已取消清单导入预览。","warn");
}
async function downloadManifestTemplate(){
  setStatus("正在生成清单模板...");
  try{
    const resp=await fetch("/api/import_template");
    if(!resp.ok)throw new Error(await resp.text());
    const data=await resp.json();
    downloadBase64File(
      data.xlsx_base64,
      data.filename||`货物清单导入模板_${stamp().slice(0,10)}.xlsx`,
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    recordActivity("下载模板","货物清单导入模板",{render:true});
    setStatus("清单模板已生成。","ok");
  }catch(e){setStatus("下载模板失败："+(e.message||e),"err")}
}
const queue=[];let processing=false;
function enqueue(item){queue.push(item);processQueue()}
async function processQueue(){if(processing)return;processing=true;while(queue.length){const q=queue.shift();try{setStatus(q.type==="file"?"正在识别图片...":"正在识别文字...");if(q.type==="file"){const form=new FormData();form.append("file",q.data);const resp=await fetch("/api/extract",{method:"POST",body:form});if(!resp.ok)throw new Error(await resp.text());appendSkus((await resp.json()).skus||[])}else{const data=await apiJSON("/api/extract_text",{text:q.data});appendSkus(data.skus||[])}}catch(e){setStatus("识别失败："+(e.message||e),"err")}}processing=false}

$("btn-calc").onclick=calculate;$("btn-repack").onclick=repackUnlocked;$("btn-render").onclick=exportPNG;$("btn-csv").onclick=exportCSV;$("btn-xlsx").onclick=exportWorkbook;$("btn-report").onclick=exportReport;$("btn-save").onclick=saveProject;$("btn-load").onclick=()=>$("project-input").click();$("btn-restore-draft").onclick=restoreAutoDraft;$("btn-clear-draft").onclick=clearAutoDraft;$("btn-reset-layout").onclick=resetWorkbenchLayout;
$("project-input").onchange=()=>{const f=$("project-input").files[0];if(f)loadProjectFile(f);$("project-input").value=""};
$("btn-add-row").onclick=()=>{state.items.push(blank());renderItems()};
$("btn-import-manifest").onclick=()=>$("manifest-input").click();
$("manifest-input").onchange=()=>{const f=$("manifest-input").files[0];if(f)importManifestFile(f);$("manifest-input").value=""};
$("btn-template").onclick=downloadManifestTemplate;
$("btn-commit-import").onclick=commitImportPreview;
$("btn-cancel-import").onclick=cancelImportPreview;
$("btn-sample").onclick=()=>{state.items=JSON.parse(JSON.stringify(SAMPLE));recordActivity("填入示例",`${state.items.length} 行货物`,{render:true});renderItems();setStatus("示例已填入。","ok")};
$("btn-clear").onclick=()=>{if(!confirm("确定清空货物和当前方案？"))return;state.projectInfo=projectInfoDefaults();state.manualTouched=false;state.measurement=null;state.savedMeasurements=[];state.customViewPresets=[];state.placementClipboard=null;state.measureMode=false;state.maxSegmentWeight=0;state.items=[blank()];state.placements=[];state.sequenceMode=false;state.sequenceStep=0;state.layerFilter="all";state.validation=[];state.history=[];state.future=[];state.activityLog=[];state.importPreview=null;recordActivity("清空项目","已清空货物和当前方案");setSelection([]);renderAll()};
$("btn-undo").onclick=()=>{if(!state.history.length)return;state.future.push(snapshot());restore(state.history.pop());recordActivity("撤销调整","回退上一步布局",{render:true})};
$("btn-redo").onclick=()=>{if(!state.future.length)return;state.history.push(snapshot());restore(state.future.pop());recordActivity("重做调整","恢复下一步布局",{render:true})};
$("btn-validate").onclick=()=>validatePlan({action:"重新校验"});
$("btn-select-layer").onclick=selectCurrentLayer;
$("btn-lock-layer").onclick=()=>setCurrentLayerLock(true);
$("btn-unlock-layer").onclick=()=>setCurrentLayerLock(false);
$("btn-repack-layer").onclick=repackCurrentLayer;
$("measure-toggle").onclick=()=>toggleMeasureMode();
$("zoom-in").onclick=()=>zoomCanvas(1.2);
$("zoom-out").onclick=()=>zoomCanvas(1/1.2);
$("zoom-fit").onclick=()=>resetCanvasView();
$("btn-view-bottom").onclick=()=>applyViewPreset("bottom");
$("btn-view-top-layer").onclick=()=>applyViewPreset("top");
$("btn-view-door").onclick=()=>applyViewPreset("door");
$("btn-save-view").onclick=saveCustomViewPreset;
$("btn-save-measure").onclick=saveMeasurement;
$("btn-clear-measures").onclick=clearSavedMeasurements;
$("view-top").onclick=()=>{state.view="top";state.measurement=null;renderAll()};
$("view-side").onclick=()=>{state.view="side";state.measurement=null;renderAll()};
const dz=$("drop-zone"),fi=$("file-input");
dz.addEventListener("dragover",e=>{e.preventDefault();dz.classList.add("drag")});
dz.addEventListener("dragleave",()=>dz.classList.remove("drag"));
dz.addEventListener("drop",e=>{e.preventDefault();dz.classList.remove("drag");for(const f of e.dataTransfer.files)enqueue({type:"file",data:f})});
fi.onchange=()=>{for(const f of fi.files)enqueue({type:"file",data:f});fi.value=""};
document.addEventListener("paste",e=>{const tag=e.target&&e.target.tagName;if(tag==="INPUT"||tag==="TEXTAREA")return;let hasImage=false;for(const item of e.clipboardData.items){if(item.type.startsWith("image/")){hasImage=true;e.preventDefault();enqueue({type:"file",data:item.getAsFile()})}}if(!hasImage){const text=e.clipboardData.getData("text");if(text&&text.trim().length>5){e.preventDefault();enqueue({type:"text",data:text})}}});
document.addEventListener("keydown",e=>{
  const tag=e.target&&e.target.tagName;if(tag==="INPUT"||tag==="TEXTAREA")return;
  if(e.key==="Escape"&&(state.measureMode||state.measurement)){toggleMeasureMode(false);e.preventDefault();return}
  if(e.ctrlKey&&e.key.toLowerCase()==="c"){copyPlacementSelection();e.preventDefault();return}
  if(e.ctrlKey&&e.key.toLowerCase()==="v"&&canPastePlacementClipboard()){pastePlacementClipboard();e.preventDefault();return}
  if(e.ctrlKey&&e.key.toLowerCase()==="z"){$("btn-undo").click();e.preventDefault();return}
  if(e.ctrlKey&&e.key.toLowerCase()==="y"){$("btn-redo").click();e.preventDefault();return}
  if(e.key.toLowerCase()==="m"){toggleMeasureMode();e.preventDefault();return}
  if(e.key==="Delete"||e.key==="Backspace"){deleteSelection();e.preventDefault();return}
  if(e.key.toLowerCase()==="r"){rotateSelection();e.preventDefault();return}
  if(e.key.toLowerCase()==="l"){toggleLockSelection();e.preventDefault();return}
  const step=e.shiftKey?20:5;
  if(e.key==="ArrowLeft"){nudgeSelection(-step,0,0);e.preventDefault();return}
  if(e.key==="ArrowRight"){nudgeSelection(step,0,0);e.preventDefault();return}
  if(e.key==="ArrowUp"){state.view==="side"?nudgeSelection(0,0,step):nudgeSelection(0,-step,0);e.preventDefault();return}
  if(e.key==="ArrowDown"){state.view==="side"?nudgeSelection(0,0,-step):nudgeSelection(0,step,0);e.preventDefault();return}
});
initWorkbenchLayout();
renderAll();
initAutoDraft();
</script>
</body>
</html>'''
