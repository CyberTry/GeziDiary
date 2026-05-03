# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
日记列表部件模块

功能：展示日记列表，支持按日期浏览
"""

import re
from datetime import date
from typing import List, Optional

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QComboBox,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# ============================================
# 本地模块导入
# ============================================
from core.diary_manager import DiaryEntry


class DiaryListItem(QListWidgetItem):
    """
    日记列表项
    
    自定义列表项，存储日记日期和摘要信息
    
    Attributes:
        entry_date (date): 日记日期
        entry (DiaryEntry): 日记条目
    """
    
    def __init__(self, entry: DiaryEntry):
        """
        初始化列表项
        
        Args:
            entry: 日记条目
        """
        # 生成显示文本
        display_text = self._format_display_text(entry)
        
        super().__init__(display_text)
        
        self.entry_date = entry.date
        self.entry = entry
        
        # 设置工具提示
        self.setToolTip(entry.get_formatted_date())
    
    def _format_display_text(self, entry: DiaryEntry) -> str:
        """
        格式化显示文本
        
        Args:
            entry: 日记条目
        
        Returns:
            str: 格式化的显示文本
        """
        # 日期部分
        date_str = f"{entry.date.month:02d}-{entry.date.day:02d}"
        
        # 提取摘要（前30个字符）
        content = entry.content.strip()
        
        # 移除Markdown标记
        # 移除标题标记
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        # 移除行内代码
        content = re.sub(r'`[^`]*`', '', content)
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        # 移除图片和链接标记
        content = re.sub(r'!\[[^\]]*\]\([^)]+\)', '[图片]', content)
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        # 移除粗体斜体标记
        content = re.sub(r'\*\*?|\_\_?', '', content)
        
        # 获取摘要
        content = content.strip()
        if len(content) > 30:
            summary = content[:30] + '...'
        else:
            summary = content
        
        # 如果没有内容，显示提示
        if not summary:
            summary = '(无内容)'
        
        # 组合显示文本
        return f"{date_str}  {summary}"


class DiaryListWidget(QWidget):
    """
    日记列表部件
    
    展示日记列表，支持月份筛选和日期选择
    
    Attributes:
        entries (List[DiaryEntry]): 当前显示的日记列表
        selected_date (date): 当前选中的日期
    
    Signals:
        entry_selected: 选择日记时发射，传递日期
    """
    
    # 自定义信号：选择日记时发射
    entry_selected = pyqtSignal(date)
    
    def __init__(self, parent=None):
        """
        初始化日记列表部件
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 初始化属性
        # ============================================
        self.entries: List[DiaryEntry] = []
        self.selected_date: Optional[date] = None
        
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
        title_label = QLabel('日记列表')
        title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # ============================================
        # 筛选区域
        # ============================================
        filter_layout = QHBoxLayout()
        
        # 年份选择
        self.year_combo = QComboBox()
        self.year_combo.setFont(QFont('Microsoft YaHei', 9))
        self.year_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.year_combo)
        
        # 月份选择
        self.month_combo = QComboBox()
        self.month_combo.setFont(QFont('Microsoft YaHei', 9))
        for i in range(1, 13):
            self.month_combo.addItem(f'{i}月', i)
        # 设置当前月份
        current_month = date.today().month
        self.month_combo.setCurrentIndex(current_month - 1)
        self.month_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.month_combo)
        
        layout.addLayout(filter_layout)
        
        # ============================================
        # 日记列表
        # ============================================
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont('Microsoft YaHei', 9))
        self.list_widget.setSpacing(2)
        self.list_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        
        # 设置列表样式
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #d0d7de;
                border-radius: 6px;
                background-color: #ffffff;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #0969da;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f3f4f6;
            }
            QListWidget::item:selected:hover {
                background-color: #0969da;
            }
        """)
        
        # 连接选择信号
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        layout.addWidget(self.list_widget)
        
        # ============================================
        # 统计信息
        # ============================================
        self.stats_label = QLabel('共 0 篇日记')
        self.stats_label.setFont(QFont('Microsoft YaHei', 9))
        self.stats_label.setStyleSheet('color: #6e7781;')
        layout.addWidget(self.stats_label)
    
    def set_entries(self, entries: List[DiaryEntry]):
        """
        设置日记列表
        
        Args:
            entries: 日记条目列表
        """
        self.entries = entries
        self._refresh_list()
        self._update_stats()
    
    def _refresh_list(self):
        """
        刷新列表显示
        """
        # 清空列表
        self.list_widget.clear()
        
        # 按日期倒序排列（最新的在前）
        sorted_entries = sorted(self.entries, key=lambda e: e.date, reverse=True)
        
        # 添加列表项
        for entry in sorted_entries:
            item = DiaryListItem(entry)
            self.list_widget.addItem(item)
            
            # 如果是选中的日期，高亮显示
            if entry.date == self.selected_date:
                item.setSelected(True)
                self.list_widget.scrollToItem(item)
    
    def _update_stats(self):
        """
        更新统计信息
        """
        count = len(self.entries)
        self.stats_label.setText(f'共 {count} 篇日记')
    
    def set_selected_date(self, selected_date: date):
        """
        设置选中的日期
        
        Args:
            selected_date: 选中的日期
        """
        self.selected_date = selected_date
        
        # 更新列表选中状态
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if isinstance(item, DiaryListItem) and item.entry_date == selected_date:
                item.setSelected(True)
                self.list_widget.scrollToItem(item)
                break
        else:
            # 如果没找到，清除选中
            self.list_widget.clearSelection()
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """
        处理列表项点击
        
        Args:
            item: 点击的列表项
        """
        if isinstance(item, DiaryListItem):
            self.selected_date = item.entry_date
            self.entry_selected.emit(item.entry_date)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """
        处理列表项双击
        
        Args:
            item: 双击的列表项
        """
        # 双击与单击相同处理
        self._on_item_clicked(item)
    
    def _on_filter_changed(self):
        """
        处理筛选条件变化
        
        这里可以实现按年月筛选功能
        """
        # 获取选中的年月
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        
        # 发射筛选信号（由父组件处理）
        # 这里可以添加筛选逻辑
        pass
    
    def update_year_combo(self, years: List[int]):
        """
        更新年份选择框
        
        Args:
            years: 可用年份列表
        """
        # 保存当前选择
        current_year = self.year_combo.currentData()
        
        # 清空并重新填充
        self.year_combo.clear()
        
        for year in sorted(years, reverse=True):
            self.year_combo.addItem(f'{year}年', year)
        
        # 恢复选择或选择当前年份
        if current_year:
            index = self.year_combo.findData(current_year)
            if index >= 0:
                self.year_combo.setCurrentIndex(index)
        else:
            # 选择当前年份
            current_year = date.today().year
            index = self.year_combo.findData(current_year)
            if index >= 0:
                self.year_combo.setCurrentIndex(index)
    
    def add_entry(self, entry: DiaryEntry):
        """
        添加日记到列表
        
        Args:
            entry: 日记条目
        """
        self.entries.append(entry)
        
        # 按日期排序
        self.entries.sort(key=lambda e: e.date, reverse=True)
        
        # 刷新列表
        self._refresh_list()
        self._update_stats()
    
    def remove_entry(self, entry_date: date):
        """
        从列表中移除日记
        
        Args:
            entry_date: 要移除的日记日期
        """
        # 查找并移除
        self.entries = [e for e in self.entries if e.date != entry_date]
        
        # 刷新列表
        self._refresh_list()
        self._update_stats()
