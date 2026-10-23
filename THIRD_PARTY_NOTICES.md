# 第三方依赖许可

本项目以 MIT 许可发布。打包产物中包含以下第三方组件，各自保留原有许可：

| 组件 | 许可 | 用途 |
|---|---|---|
| [FastAPI](https://github.com/fastapi/fastapi) | MIT | HTTP 接口 |
| [Starlette](https://github.com/encode/starlette) | BSD-3-Clause | ASGI 框架 |
| [Uvicorn](https://github.com/encode/uvicorn) | BSD-3-Clause | ASGI 服务器 |
| [Pydantic](https://github.com/pydantic/pydantic) | MIT | 请求/响应模型 |
| [python-multipart](https://github.com/Kludex/python-multipart) | Apache-2.0 | 表单与文件上传解析 |
| [Matplotlib](https://github.com/matplotlib/matplotlib) | PSF-based（BSD 兼容） | PNG 三视图渲染 |
| [NumPy](https://github.com/numpy/numpy) | BSD-3-Clause | Matplotlib 依赖 |
| [Pillow](https://github.com/python-pillow/Pillow) | MIT-CMU | Matplotlib 依赖 |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | GPL-2.0-or-later，附 bootloader 例外 | 打包为单文件 exe |

PyInstaller 的 bootloader 例外允许把打包产物按任意许可分发；打包产物本身不因此变成 GPL。

前端为仓库内手写的 HTML/CSS/JavaScript，未引入第三方前端框架。
