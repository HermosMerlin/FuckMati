@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo    C Helper 诊断工具
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] 虚拟环境不存在，请先运行 run.bat 初始化
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [INFO] 正在运行诊断测试...
echo.

.venv\Scripts\python diagnose.py
