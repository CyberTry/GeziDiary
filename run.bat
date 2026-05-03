@echo off
chcp 65001 >nul
REM ============================================
REM GeziDiary - 鸽子日记
REM Windows启动脚本
REM ============================================

echo.
echo ============================================
echo    GeziDiary - 鸽子日记
echo ============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [检查] 正在检查依赖...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [启动] 正在启动鸽子日记...
echo.

REM 启动应用
python main.py

REM 如果应用异常退出，暂停显示错误
if errorlevel 1 (
    echo.
    echo [错误] 应用异常退出
    pause
)
