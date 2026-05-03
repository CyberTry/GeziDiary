#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
主程序入口文件

功能：启动桌面日记应用程序
作者：鸽子工作室
版本：1.0.0
"""

import sys
import os

# ============================================
# 路径配置 - 确保能正确导入本地模块
# ============================================

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将src目录添加到Python路径，用于导入本地模块
sys.path.insert(0, os.path.join(current_dir, 'src'))

# ============================================
# 导入应用主类
# ============================================
from app import DiaryApplication


def main():
    """
    应用程序主入口函数
    
    功能：
        1. 创建日记应用实例
        2. 启动应用程序主循环
        3. 处理程序退出
    
    Returns:
        int: 程序退出码，0表示正常退出
    """
    # 创建应用实例
    app = DiaryApplication()
    
    # 启动应用程序并返回退出码
    # exec()进入Qt事件循环，等待用户交互
    exit_code = app.exec()
    
    return exit_code


# ============================================
# 程序入口点
# ============================================
if __name__ == '__main__':
    # 调用主函数并传递退出码给系统
    sys.exit(main())
