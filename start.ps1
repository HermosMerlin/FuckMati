# C Helper 启动脚本 (PowerShell)
# 功能：自动检测环境、安装依赖、启动程序

$ErrorActionPreference = "Stop"
$host.UI.RawUI.WindowTitle = "C Helper"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   C Helper 启动器" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

# 检查 uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] 未找到 uv，请先安装: https://docs.astral.sh/uv/" -ForegroundColor Red
    Read-Host "按 Enter 退出"
    exit 1
}

# 检查虚拟环境
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[INFO] 虚拟环境不存在，正在初始化..." -ForegroundColor Yellow
    uv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 创建虚拟环境失败" -ForegroundColor Red
        Read-Host "按 Enter 退出"
        exit 1
    }
    
    & .venv\Scripts\activate
    uv pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 安装依赖失败" -ForegroundColor Red
        Read-Host "按 Enter 退出"
        exit 1
    }
    Write-Host "[OK] 环境初始化完成" -ForegroundColor Green
} else {
    & .venv\Scripts\activate
}

# 检查配置文件
if (-not (Test-Path "config.json")) {
    Write-Host "[WARN] 未找到 config.json，请配置 API 密钥后再启动" -ForegroundColor Yellow
    Read-Host "按 Enter 退出"
    exit 1
}

Write-Host "[INFO] 正在启动 C Helper..." -ForegroundColor Cyan
Write-Host "[INFO] 按 Ctrl+G 触发，托盘右键可退出" -ForegroundColor Gray
Write-Host ""

try {
    .venv\Scripts\python -m c_helper.main
} catch {
    Write-Host ""
    Write-Host "[ERROR] 程序异常退出: $_" -ForegroundColor Red
    Read-Host "按 Enter 关闭"
}
