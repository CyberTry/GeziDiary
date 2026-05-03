@echo off
chcp 65001 >nul
REM ============================================
REM GeziDiary - 鸽子日记
REM Windows打包脚本
REM 使用PyInstaller打包为独立可执行文件
REM ============================================

echo.
echo ============================================
echo    GeziDiary - 打包工具
echo ============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

REM 检查PyInstaller是否安装
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装PyInstaller...
    pip install pyinstaller
)

REM 清理旧的构建文件
echo [清理] 正在清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM 执行打包
echo [打包] 正在打包应用程序...
echo.

pyinstaller ^
    --name="GeziDiary" ^
    --windowed ^
    --onefile ^
    --clean ^
    --noconfirm ^
    --add-data "src;src" ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=markdown.extensions.fenced_code ^
    --hidden-import=markdown.extensions.tables ^
    --hidden-import=markdown.extensions.nl2br ^
    main.py

REM 检查打包结果
if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

REM 复制额外文件到dist目录
echo [复制] 正在复制额外文件...
if exist README.md copy README.md dist\
if exist LICENSE copy LICENSE dist\

REM 创建启动脚本
echo [创建] 正在创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo start "" "%%~dp0GeziDiary.exe"
) > dist\启动鸽子日记.bat

echo.
echo ============================================
echo [成功] 打包完成！
echo ============================================
echo.
echo 可执行文件位置: dist\GeziDiary.exe
echo.
pause
