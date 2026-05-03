"""
GeziDiary - 桌面日记应用
=======================
一个支持Markdown编辑和GitHub风格日历热力图的现代日记应用。

功能特性：
- Markdown编辑与实时预览
- GitHub风格日历热力图展示每日文本量
- 按年月日格式保存日记文件
- 自定义存储路径
- 内置所有依赖，无需手动配置
- 现代扁平化UI设计

作者：鸽子工作室
版本：1.0.0
"""

import sys
import os

# 添加项目根目录到Python路径，确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主应用程序入口
from src.app import main

if __name__ == "__main__":
    # 程序入口点
    main()
