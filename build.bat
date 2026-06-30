@echo off
chcp 65001 >nul
REM Container Loading Simulator - Windows Build Script (English only to avoid encoding issues)

echo.
echo [0/4] Checking Python version...
python -c "import sys; v=sys.version_info[:2]; print(f'Python {sys.version.split()[0]}'); raise SystemExit(0 if (3,11) <= v <= (3,13) else 1)"
if errorlevel 1 ( echo Build requires Python 3.11-3.13. Do not use preview/future Python builds for packaging. & pause & exit /b 1 )

echo.
echo [1/4] Installing PyInstaller and dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt
if errorlevel 1 ( echo Install failed. Check Python and network. & pause & exit /b 1 )

echo.
echo [2/4] Running preflight checks...
python preflight.py --strict-render
if errorlevel 1 ( echo Preflight failed. Fix checks before packaging. & pause & exit /b 1 )

echo.
echo [3/4] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ContainerPack.spec del /q ContainerPack.spec

echo.
echo [4/4] Building exe (takes 2-5 minutes, please wait)...
pyinstaller --onefile --name ContainerPack --collect-all matplotlib --collect-submodules uvicorn --collect-submodules fastapi --hidden-import _frontend --hidden-import uvicorn.logging --hidden-import uvicorn.loops.auto --hidden-import uvicorn.loops.asyncio --hidden-import uvicorn.protocols.http.auto --hidden-import uvicorn.protocols.http.h11_impl --hidden-import uvicorn.protocols.websockets.auto --hidden-import uvicorn.protocols.websockets.wsproto_impl --hidden-import uvicorn.lifespan.on --add-data "_packer.py;." --add-data "_visualizer.py;." app.py
if errorlevel 1 ( echo Build failed. & pause & exit /b 1 )

echo.
echo ==============================================================
echo  Build complete!
echo  Output file: dist\ContainerPack.exe
echo  You can rename it to anything you want (e.g. zhuanggui.exe).
echo  Double-click the exe to run, browser will open automatically.
echo ==============================================================
echo.
pause
