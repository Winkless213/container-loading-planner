# 装柜工作台

外贸出货前的集装箱装柜规划工具：录入货物清单，算法生成装柜初稿，人工在画布上复核调整，后端按装柜规则校验，最后导出给仓库和现场使用的方案报告。在外贸公司实际业务中使用，Windows 下打包为单文件 exe。

![装柜工作台界面](docs/screenshot.png)

## 功能亮点

- **排柜算法**：启发式三维排柜，枚举 6 种摆放方向（限直立货物只允许水平旋转），沿柜长推进并利用箱顶平台和末列空位回填；多厂家货物在紧凑排法利用率偏低时自动改为按厂家分区。可锁定已摆好的部分，只重排剩余货物。
- **规则校验**：越界、碰撞、门口预留区、底面支撑（按接触面积计算，防止悬空）、不可堆叠、单箱累计上压、柜长 6 段分段限重、重心偏载、漏放／多放。问题在画布上高亮，并对碰撞、越界、悬空等给出一键修复。
- **人工复核**：2D 画布支持缩放、吸附、测距、多选对齐、按层过滤、按装柜顺序回放；左右栏和工具栏可拖拽调宽，布局在本机记忆。
- **交付**：保存／打开 `.cpack` 项目文件、浏览器自动草稿、操作记录留痕；导出 PNG、CSV、7 个工作表的 Excel 和 HTML 方案报告，报告带安全结论与复核要点。
- **AI 识别清单**：报价单截图或文字交给通义千问视觉模型识别成货物清单，结果先做结构校验再进表格。

技术栈：Python / FastAPI / Pydantic / 原生 JavaScript + SVG / Matplotlib / 通义千问 Qwen-VL / Playwright / PyInstaller

## 环境要求

- Windows 10/11（安装包为 Windows x64；源码也可在其他系统上跑）
- Python 3.11–3.13：打包时不要用预览版或过新的版本，`matplotlib` 可能没有可用 wheel
- AI 识别需要 DashScope API Key；未配置时识别功能禁用，手工填表、自动排柜、人工调整和校验仍可使用

## 安装与运行

### 安装包（Windows）

从 [Releases](../../releases/latest) 下载 `Container-Loading-Planner-Setup-1.0.1.exe` 安装，安装器会创建开始菜单和桌面快捷方式，装完即可使用，不需要另外安装 Python。

启动后会自动打开浏览器进入工作台；关闭控制台窗口即退出程序。安装器在安装后会执行一次隐藏自检，失败时提示查看 `%TEMP%\ContainerPack-self-test.log`。

### 从源码运行

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 app.py
```

启动后访问控制台显示的本地地址，通常是 `http://127.0.0.1:17283/`。端口被占用时会自动顺延。

## 使用流程

导入清单（或下载模板填写）→ 自动排柜 → 在画布上复核调整 → 规则校验 → 导出报告。

画布快捷键、面板分隔条、视图预设、测距、多选整理、导出选项等逐项说明见 [docs/USAGE.md](docs/USAGE.md)。

## AI 识别清单

识别依赖 DashScope，API Key 只从环境变量读取，不写入源码：

```powershell
$env:DASHSCOPE_API_KEY="你的 key"
$env:QWEN_VL_MODEL="qwen3.6-plus"   # 可选，默认 qwen3.6-plus
python app.py
```

## 核心文件

```text
app.py          FastAPI 接口、启动逻辑、AI 识别接口
_frontend.py    装柜工作台前端
_packer.py      装柜算法
_validator.py   方案校验器
_visualizer.py  PNG 三视图渲染
tests/          回归测试
build.bat       Windows 单 exe 打包脚本
docs/           截图、操作手册、开发记录
```

## 打包

```powershell
.\build.bat
```

打包脚本会检查 Python 版本、安装依赖、运行严格自检，然后生成 `dist\ContainerPack.exe`。

安装包用 Inno Setup 构建，脚本在 `installer/ContainerPack.iss`，输出到 `work\release\installer\`。

## 验证

```powershell
py -3.13 preflight.py --strict-render
py -3.13 -m unittest discover -s tests
py -3.13 browser_smoke.py
```

`preflight.py` 会编译源码、检查文本编码、跑单测和接口冒烟；加 `--browser-smoke` 会在真实 Chromium 里填示例、自动排柜并检查布局记忆。`ContainerPack.exe --self-test` 是安装包自检入口，不需要浏览器。

## 文档

- [docs/USAGE.md](docs/USAGE.md)：工作台逐项操作说明
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)：产品化过程记录
- [CHANGELOG.md](CHANGELOG.md)：版本变更

## 许可证

MIT，见 [LICENSE](LICENSE)。第三方依赖许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
