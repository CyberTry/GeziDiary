#!/bin/bash

# ==========================================
#    GeziDiary - 桌面日记应用
#    鸽子工作室出品
# ==========================================

echo "=========================================="
echo "   GeziDiary - 桌面日记应用"
echo "   鸽子工作室出品"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8或更高版本"
    echo "Ubuntu/Debian: sudo apt-get install python3"
    echo "macOS: brew install python3"
    exit 1
fi

echo "[信息] Python版本:"
python3 --version
echo ""

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未检测到pip3，请先安装pip"
    echo "Ubuntu/Debian: sudo apt-get install python3-pip"
    exit 1
fi

# 检查依赖是否已安装
echo "[信息] 检查依赖..."
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "[信息] 正在安装依赖，请稍候..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo "[信息] 依赖检查完成"
echo ""
echo "[信息] 启动 GeziDiary..."
echo ""

# 启动应用
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 应用启动失败"
    read -p "按回车键退出..."
fi
