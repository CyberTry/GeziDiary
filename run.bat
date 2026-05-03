@echo off
chcp 65001 >nul
echo ==========================================
echo    GeziDiary - 桌面日记应用
echo    鸽子工作室出品
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python版本:
python --version
echo.

REM 检查依赖是否已安装
echo [信息] 检查依赖...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装依赖，请稍候...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [信息] 依赖检查完成
echo.
echo [信息] 启动 GeziDiary...
echo.

REM 启动应用
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 应用启动失败
    pause
)
