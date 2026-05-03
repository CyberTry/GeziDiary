#!/bin/bash

echo "=========================================="
echo "   GeziDiary - 桌面日记应用"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

echo "[1/3] 检查依赖..."

# 检查并安装依赖
pip3 install -q PyQt6==6.6.1 PyQt6-Qt6==6.6.1 PyQt6-sip==13.6.0 PyQt6-WebEngine==6.6.0 markdown==3.5.2 python-dateutil==2.8.2 PyYAML==6.0.1

echo "[2/3] 启动应用程序..."
echo ""

# 启动应用
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 应用程序异常退出"
    read -p "按回车键继续..."
fi
