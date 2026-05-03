# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
应用程序主类

功能：管理应用生命周期、初始化配置、创建主窗口
"""

import sys
import os

# ============================================
# PyQt6 导入 - GUI框架
# ============================================
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase

# ============================================
# 本地模块导入
# ============================================
from core.config import ConfigManager
from ui.main_window import MainWindow


class DiaryApplication(QApplication):
    """
    日记应用程序主类
    
    继承自QApplication，管理整个应用的生命周期
    负责初始化配置、加载字体、创建主窗口
    
    Attributes:
        config (ConfigManager): 配置管理器实例
        main_window (MainWindow): 主窗口实例
    """
    
    def __init__(self):
        """
        初始化应用程序
        
        功能：
            1. 初始化父类QApplication
            2. 设置应用属性（高DPI支持等）
            3. 加载配置
            4. 初始化UI
        """
        # 初始化父类，传递命令行参数
        super().__init__(sys.argv)
        
        # ============================================
        # 应用基本设置
        # ============================================
        # 设置应用名称（用于窗口标题、任务栏显示等）
        self.setApplicationName('GeziDiary')
        # 设置应用显示名称（中文名）
        self.setApplicationDisplayName('鸽子日记')
        # 设置应用版本
        self.setApplicationVersion('1.0.0')
        
        # ============================================
        # 高DPI支持设置 (PyQt6默认启用高DPI支持)
        # ============================================
        # PyQt6 默认启用高DPI支持，无需手动设置AA_EnableHighDpiScaling
        # 设置DPI缩放策略
        self.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # ============================================
        # 初始化配置管理器
        # ============================================
        # ConfigManager会加载或创建默认配置
        self.config = ConfigManager()
        
        # ============================================
        # 设置全局字体
        # ============================================
        self._setup_fonts()
        
        # ============================================
        # 创建并显示主窗口
        # ============================================
        self.main_window = MainWindow(self.config)
        self.main_window.show()
    
    def _setup_fonts(self):
        """
        设置应用程序全局字体
        
        功能：
            1. 尝试加载系统默认中文字体
            2. 设置全局字体大小
            3. 确保中文显示正常
        """
        # 优先使用的中文字体列表（按优先级排序）
        # 这些字体在Windows和macOS上通常都有
        preferred_fonts = [
            'Microsoft YaHei',      # 微软雅黑（Windows首选）
            'PingFang SC',          # 苹方（macOS首选）
            'Source Han Sans SC',   # 思源黑体
            'Noto Sans CJK SC',     # Noto中文
            'WenQuanYi Micro Hei',  # 文泉驿（Linux）
            'SimHei',               # 黑体（备用）
        ]
        
        # 获取系统所有可用字体族（PyQt6使用静态方法）
        available_families = QFontDatabase.families()
        
        # 选择第一个可用的中文字体
        selected_font = None
        for font_name in preferred_fonts:
            if font_name in available_families:
                selected_font = font_name
                break
        
        # 如果没有找到首选字体，使用系统默认字体
        if not selected_font:
            selected_font = self.font().family()
        
        # 创建字体对象并设置属性
        font = QFont(selected_font)
        # 设置字体大小（9pt是标准大小）
        font.setPointSize(9)
        # 设置字体权重为正常（PyQt6使用枚举）
        font.setWeight(QFont.Weight.Normal)
        
        # 应用全局字体
        self.setFont(font)
    
    def exec(self):
        """
        启动应用程序事件循环
        
        Returns:
            int: 应用程序退出码
        """
        # 调用父类的exec方法进入事件循环
        return super().exec()
