#!/bin/bash
# ============================================
# GeziDiary - 鸽子日记
# Linux/macOS 启动脚本
# ============================================

echo ""
echo "============================================"
echo "   GeziDiary - 鸽子日记"
echo "============================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

# 检查依赖是否安装
echo "[检查] 正在检查依赖..."
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "[安装] 正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo "[启动] 正在启动鸽子日记..."
echo ""

# 启动应用
python3 main.py

# 如果应用异常退出
if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 应用异常退出"
    read -p "按回车键继续..."
fi
