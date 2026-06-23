@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ==========================================
echo    C Helper Launcher
echo ==========================================

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found, initializing...
    uv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Is uv installed?
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    uv pip install -e ".[dev]"
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Environment ready
) else (
    call .venv\Scripts\activate.bat
)

if not exist "config.json" (
    echo [INFO] config.json not found, will auto-generate on first run.
    echo [INFO] After startup, edit config.json to fill in your api_key,
    echo [INFO] then right-click the tray icon and select "强制重置为空闲".
)

echo [INFO] Starting C Helper...
echo [INFO] Press Ctrl+Alt+G to trigger, right-click tray icon to exit
echo.

.venv\Scripts\python -m c_helper.main
set EXITCODE=%errorlevel%

echo.
echo [INFO] Program exited with code: %EXITCODE%
if %EXITCODE% neq 0 (
    echo [ERROR] Abnormal exit. Check error message above.
)
pause
endlocal
