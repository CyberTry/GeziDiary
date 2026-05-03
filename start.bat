@echo off
chcp 65001 >nul
echo ==========================================
echo    GeziDiary - 桌面日记应用
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo [1/3] 检查依赖...

REM 检查并安装依赖
pip install -q PyQt6==6.6.1 PyQt6-Qt6==6.6.1 PyQt6-sip==13.6.0 PyQt6-WebEngine==6.6.0 markdown==3.5.2 python-dateutil==2.8.2 PyYAML==6.0.1

echo [2/3] 启动应用程序...
echo.

REM 启动应用
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 应用程序异常退出
    pause
)
