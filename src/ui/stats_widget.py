# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
统计信息部件模块

功能：展示日记统计信息，如总篇数、总字数、连续天数等
"""

from datetime import date
from typing import Dict, Optional

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class StatCard(QFrame):
    """
    统计卡片部件
    
    显示单个统计项的卡片样式组件
    
    Attributes:
        title_label (QLabel): 标题标签
        value_label (QLabel): 数值标签
    """
    
    def __init__(self, title: str, value: str = '0', parent=None):
        """
        初始化统计卡片
        
        Args:
            title: 统计项标题
            value: 统计数值
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 设置样式
        # ============================================
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            StatCard {
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        # ============================================
        # 创建布局
        # ============================================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont('Microsoft YaHei', 9))
        self.title_label.setStyleSheet('color: #6e7781;')
        layout.addWidget(self.title_label)
        
        # 数值
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet('color: #24292f;')
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        """
        设置统计数值
        
        Args:
            value: 新的数值
        """
        self.value_label.setText(value)


class StatsWidget(QWidget):
    """
    统计信息部件
    
    展示日记的各种统计信息
    
    Attributes:
        stats (Dict): 统计数据字典
    """
    
    def __init__(self, parent=None):
        """
        初始化统计信息部件
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 初始化属性
        # ============================================
        self.stats: Dict = {}
        
        # ============================================
        # 设置UI
        # ============================================
        self._setup_ui()
    
    def _setup_ui(self):
        """
        设置UI布局
        """
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # ============================================
        # 标题
        # ============================================
        title_label = QLabel('统计信息')
        title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # ============================================
        # 统计卡片网格
        # ============================================
        cards_layout = QGridLayout()
        cards_layout.setSpacing(10)
        
        # 总篇数
        self.entries_card = StatCard('总篇数', '0')
        cards_layout.addWidget(self.entries_card, 0, 0)
        
        # 总字符数
        self.chars_card = StatCard('总字符数', '0')
        cards_layout.addWidget(self.chars_card, 0, 1)
        
        # 连续天数
        self.streak_card = StatCard('连续天数', '0')
        cards_layout.addWidget(self.streak_card, 1, 0)
        
        # 平均字符数
        self.avg_card = StatCard('平均字符数', '0')
        cards_layout.addWidget(self.avg_card, 1, 1)
        
        layout.addLayout(cards_layout)
        
        # ============================================
        # 详细信息
        # ============================================
        self.details_label = QLabel('开始写日记吧！')
        self.details_label.setFont(QFont('Microsoft YaHei', 9))
        self.details_label.setStyleSheet('color: #6e7781;')
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)
        
        # 添加弹性空间
        layout.addStretch()
    
    def update_stats(self, stats: Dict):
        """
        更新统计信息
        
        Args:
            stats: 统计数据字典，包含以下键：
                - total_entries: 总篇数
                - total_chars: 总字符数
                - total_words: 总词数
                - avg_chars: 平均字符数
                - current_streak: 连续天数
                - first_entry: 第一篇日记日期
                - last_entry: 最后一篇日记日期
        """
        self.stats = stats
        
        # ============================================
        # 更新卡片数值
        # ============================================
        
        # 总篇数
        total_entries = stats.get('total_entries', 0)
        self.entries_card.set_value(self._format_number(total_entries))
        
        # 总字符数
        total_chars = stats.get('total_chars', 0)
        self.chars_card.set_value(self._format_number(total_chars))
        
        # 连续天数
        streak = stats.get('current_streak', 0)
        self.streak_card.set_value(self._format_number(streak))
        
        # 平均字符数
        avg_chars = stats.get('avg_chars', 0)
        self.avg_card.set_value(self._format_number(avg_chars))
        
        # ============================================
        # 更新详细信息
        # ============================================
        self._update_details()
    
    def _update_details(self):
        """
        更新详细信息文本
        """
        total_entries = self.stats.get('total_entries', 0)
        
        if total_entries == 0:
            self.details_label.setText('开始写日记吧！')
            return
        
        # 构建详细信息文本
        details_parts = []
        
        # 第一篇日记日期
        first_entry = self.stats.get('first_entry')
        if first_entry:
            details_parts.append(f"第一篇: {first_entry.strftime('%Y-%m-%d')}")
        
        # 最后一篇日记日期
        last_entry = self.stats.get('last_entry')
        if last_entry:
            details_parts.append(f"最近: {last_entry.strftime('%Y-%m-%d')}")
        
        # 总词数
        total_words = self.stats.get('total_words', 0)
        if total_words > 0:
            details_parts.append(f"总词数: {self._format_number(total_words)}")
        
        # 设置文本
        self.details_label.setText('  |  '.join(details_parts))
    
    def _format_number(self, num: int) -> str:
        """
        格式化数字显示
        
        大数字使用K/M缩写
        
        Args:
            num: 要格式化的数字
        
        Returns:
            str: 格式化后的字符串
        """
        if num >= 1000000:
            return f'{num / 1000000:.1f}M'
        elif num >= 1000:
            return f'{num / 1000:.1f}K'
        else:
            return str(num)
    
    def get_stats(self) -> Dict:
        """
        获取当前统计数据
        
        Returns:
            Dict: 统计数据字典
        """
        return self.stats.copy()
