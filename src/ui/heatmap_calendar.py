# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
热力图日历模块

功能：展示类似GitHub贡献图的日历热力图，显示每日文本量
"""

from datetime import date, timedelta
from typing import Dict, Optional

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QToolTip, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QFont, QMouseEvent


class HeatmapCell(QFrame):
    """
    热力图单元格类
    
    表示单日的热力图单元格，根据文本量显示不同颜色深度
    
    Attributes:
        cell_date (date): 单元格代表的日期
        value (int): 该日期的文本量（字符数）
        is_selected (bool): 是否被选中
        is_today (bool): 是否是今天
    
    Signals:
        clicked: 点击时发射，传递日期
    """
    
    # 自定义信号：点击时发射
    clicked = pyqtSignal(date)
    
    # ============================================
    # 颜色配置（GitHub风格）
    # ============================================
    # 亮色主题颜色
    LIGHT_COLORS = {
        0: '#ebedf0',      # 无数据 - 浅灰
        1: '#9be9a8',      # 少量 - 浅绿
        2: '#40c463',      # 中等 - 中绿
        3: '#30a14e',      # 较多 - 深绿
        4: '#216e39',      # 大量 - 最深绿
    }
    
    # 暗色主题颜色
    DARK_COLORS = {
        0: '#161b22',      # 无数据 - 深灰
        1: '#0e4429',      # 少量 - 暗绿
        2: '#006d32',      # 中等 - 中绿
        3: '#26a641',      # 较多 - 亮绿
        4: '#39d353',      # 大量 - 最亮绿
    }
    
    # 选中状态边框颜色
    SELECTED_BORDER = '#0969da'
    TODAY_BORDER = '#f0883e'
    
    def __init__(self, cell_date: date, parent=None):
        """
        初始化热力图单元格
        
        Args:
            cell_date: 单元格代表的日期
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 初始化属性
        # ============================================
        self.cell_date = cell_date
        self.value = 0
        self.is_selected = False
        self.is_today = (cell_date == date.today())
        self.level = 0  # 热力等级 0-4
        
        # ============================================
        # 设置UI
        # ============================================
        self._setup_ui()
    
    def _setup_ui(self):
        """
        设置单元格UI
        """
        # 固定大小
        self.setFixedSize(14, 14)
        
        # 设置边框样式
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        
        # 启用鼠标跟踪（用于显示提示）
        self.setMouseTracking(True)
        
        # 设置圆角
        self.setStyleSheet("""
            HeatmapCell {
                border-radius: 2px;
                border: 1px solid transparent;
            }
        """)
        
        # 更新颜色
        self._update_color()
    
    def set_value(self, value: int):
        """
        设置单元格的值（字符数）
        
        Args:
            value: 字符数
        """
        self.value = value
        
        # 计算热力等级
        if value == 0:
            self.level = 0
        elif value < 100:
            self.level = 1
        elif value < 500:
            self.level = 2
        elif value < 1000:
            self.level = 3
        else:
            self.level = 4
        
        # 更新颜色
        self._update_color()
    
    def set_selected(self, selected: bool):
        """
        设置选中状态
        
        Args:
            selected: 是否选中
        """
        self.is_selected = selected
        self._update_color()
    
    def _update_color(self):
        """
        更新单元格颜色
        
        根据热力等级和选中状态设置背景色
        """
        # 获取当前等级颜色（使用亮色主题）
        color = self.LIGHT_COLORS.get(self.level, self.LIGHT_COLORS[0])
        
        # 确定边框颜色
        if self.is_selected:
            border_color = self.SELECTED_BORDER
            border_width = 2
        elif self.is_today:
            border_color = self.TODAY_BORDER
            border_width = 2
        else:
            border_color = 'rgba(27, 31, 35, 0.06)'
            border_width = 1
        
        # 应用样式
        self.setStyleSheet(f"""
            HeatmapCell {{
                background-color: {color};
                border: {border_width}px solid {border_color};
                border-radius: 2px;
            }}
            HeatmapCell:hover {{
                border: 2px solid {self.SELECTED_BORDER};
            }}
        """)
    
    def enterEvent(self, event):
        """
        鼠标进入事件
        
        显示工具提示
        """
        # 格式化日期
        date_str = self.cell_date.strftime('%Y年%m月%d日')
        weekday = ['一', '二', '三', '四', '五', '六', '日'][self.cell_date.weekday()]
        
        # 格式化文本量
        if self.value == 0:
            value_str = '无日记'
        else:
            value_str = f'{self.value} 字符'
        
        # 设置工具提示
        tooltip = f"{date_str} 星期{weekday}\n{value_str}"
        self.setToolTip(tooltip)
        
        super().enterEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """
        鼠标点击事件
        
        发射clicked信号
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.cell_date)
        
        super().mousePressEvent(event)


class HeatmapCalendar(QWidget):
    """
    热力图日历部件类
    
    展示全年或指定时间范围的GitHub风格热力图
    
    Attributes:
        year (int): 当前显示的年份
        data (Dict[date, int]): 日期到字符数的映射
        selected_date (date): 当前选中的日期
        cells (Dict[date, HeatmapCell]): 日期到单元格的映射
    
    Signals:
        date_selected: 选择日期时发射
    """
    
    # 自定义信号：选择日期时发射
    date_selected = pyqtSignal(date)
    
    def __init__(self, parent=None):
        """
        初始化热力图日历
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 初始化属性
        # ============================================
        self.year = date.today().year
        self.data: Dict[date, int] = {}
        self.selected_date: Optional[date] = None
        self.cells: Dict[date, HeatmapCell] = {}
        
        # ============================================
        # 设置UI
        # ============================================
        self._setup_ui()
        
        # 初始化为当前年份
        self.set_year(self.year)
    
    def _setup_ui(self):
        """
        设置UI布局
        """
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ============================================
        # 标题区域
        # ============================================
        header_layout = QHBoxLayout()
        
        # 年份标签
        self.year_label = QLabel(str(self.year))
        self.year_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.year_label)
        
        header_layout.addStretch()
        
        # 图例
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(4)
        
        legend_label = QLabel('少')
        legend_label.setFont(QFont("Microsoft YaHei", 9))
        legend_layout.addWidget(legend_label)
        
        # 图例颜色块
        for level in range(5):
            legend_cell = QFrame()
            legend_cell.setFixedSize(12, 12)
            color = HeatmapCell.LIGHT_COLORS[level]
            legend_cell.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: 1px solid rgba(27, 31, 35, 0.06);
                    border-radius: 2px;
                }}
            """)
            legend_layout.addWidget(legend_cell)
        
        legend_label2 = QLabel('多')
        legend_label2.setFont(QFont("Microsoft YaHei", 9))
        legend_layout.addWidget(legend_label2)
        
        header_layout.addLayout(legend_layout)
        
        layout.addLayout(header_layout)
        
        # ============================================
        # 热力图网格
        # ============================================
        # 创建滚动区域容器
        self.heatmap_container = QWidget()
        self.heatmap_layout = QHBoxLayout(self.heatmap_container)
        self.heatmap_layout.setContentsMargins(0, 0, 0, 0)
        self.heatmap_layout.setSpacing(8)
        
        layout.addWidget(self.heatmap_container)
        
        # 初始化热力图网格
        self._create_heatmap_grid()
    
    def _create_heatmap_grid(self):
        """
        创建热力图网格
        
        按照GitHub贡献图的布局：
        - 每列代表一周（7天）
        - 每行代表星期几
        - 从左到右显示全年
        """
        # 清除旧的内容
        # 先保存布局中的所有部件，然后删除
        while self.heatmap_layout.count():
            item = self.heatmap_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.cells.clear()
        
        # ============================================
        # 创建星期标签列
        # ============================================
        weekday_widget = QWidget()
        weekday_layout = QVBoxLayout(weekday_widget)
        weekday_layout.setContentsMargins(0, 20, 4, 0)
        weekday_layout.setSpacing(2)
        
        # 星期标签（只显示部分）
        weekdays = ['', '周一', '', '周三', '', '周五', '']
        for day in weekdays:
            label = QLabel(day)
            label.setFont(QFont("Microsoft YaHei", 8))
            label.setFixedSize(28, 14)
            weekday_layout.addWidget(label)
        
        self.heatmap_layout.addWidget(weekday_widget)
        
        # ============================================
        # 计算日期范围
        # ============================================
        # 从该年第一天开始
        year_start = date(self.year, 1, 1)
        # 到该年最后一天
        year_end = date(self.year, 12, 31)
        
        # 调整到第一个星期日（或周一，根据喜好）
        # GitHub风格：从周日开始
        first_day = year_start - timedelta(days=year_start.weekday() + 1)
        if first_day.year < self.year:
            first_day = year_start
        
        # ============================================
        # 创建月份标签和热力图
        # ============================================
        current_date = first_day
        current_month = 0
        
        # 按月分组创建
        while current_date <= year_end:
            # 创建月份容器
            month_widget = QWidget()
            month_layout = QVBoxLayout(month_widget)
            month_layout.setContentsMargins(0, 0, 0, 0)
            month_layout.setSpacing(4)
            
            # 月份标签
            if current_date.month != current_month:
                month_label = QLabel(f"{current_date.month}月")
                month_label.setFont(QFont("Microsoft YaHei", 9))
                month_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                month_layout.addWidget(month_label)
                current_month = current_date.month
            else:
                month_layout.addWidget(QLabel())  # 占位
            
            # 创建该月的周网格
            month_grid = QGridLayout()
            month_grid.setContentsMargins(0, 0, 0, 0)
            month_grid.setSpacing(2)
            
            col = 0
            while current_date <= year_end and current_date.month == current_month:
                # 创建7天的列
                for row in range(7):
                    if current_date > year_end:
                        break
                    
                    # 创建单元格
                    cell = HeatmapCell(current_date)
                    cell.clicked.connect(self._on_cell_clicked)
                    
                    # 保存到映射
                    self.cells[current_date] = cell
                    
                    # 添加到网格
                    month_grid.addWidget(cell, row, col)
                    
                    # 下一天
                    current_date += timedelta(days=1)
                
                col += 1
            
            month_layout.addLayout(month_grid)
            self.heatmap_layout.addWidget(month_widget)
        
        # 添加弹性空间
        self.heatmap_layout.addStretch()
        
        # 更新数据
        self._update_cells()
    
    def _update_cells(self):
        """
        更新所有单元格的数据
        """
        for cell_date, cell in self.cells.items():
            # 获取该日期的字符数
            value = self.data.get(cell_date, 0)
            cell.set_value(value)
            
            # 更新选中状态
            cell.set_selected(cell_date == self.selected_date)
    
    def _on_cell_clicked(self, clicked_date: date):
        """
        处理单元格点击
        
        Args:
            clicked_date: 点击的日期
        """
        # 更新选中日期
        self.set_selected_date(clicked_date)
        
        # 发射信号
        self.date_selected.emit(clicked_date)
    
    def set_year(self, year: int):
        """
        设置显示的年份
        
        Args:
            year: 年份
        """
        self.year = year
        self.year_label.setText(str(year))
        
        # 重新创建网格
        self._create_heatmap_grid()
    
    def set_year_data(self, year: int, data: Dict[date, int]):
        """
        设置年份数据
        
        Args:
            year: 年份
            data: 日期到字符数的映射
        """
        self.year = year
        self.data = data
        
        # 更新年份标签
        self.year_label.setText(str(year))
        
        # 如果年份变化，重新创建网格
        if self.year != year or not self.cells:
            self._create_heatmap_grid()
        else:
            # 只更新数据
            self._update_cells()
    
    def set_selected_date(self, selected_date: date):
        """
        设置选中的日期
        
        Args:
            selected_date: 选中的日期
        """
        # 清除之前的选中状态
        if self.selected_date and self.selected_date in self.cells:
            self.cells[self.selected_date].set_selected(False)
        
        # 设置新的选中日期
        self.selected_date = selected_date
        
        # 更新新日期的选中状态
        if selected_date in self.cells:
            self.cells[selected_date].set_selected(True)
        
        # 如果选中的日期不在当前年份，切换年份
        if selected_date.year != self.year:
            self.set_year(selected_date.year)
            # 重新设置选中（因为网格重建了）
            if selected_date in self.cells:
                self.cells[selected_date].set_selected(True)
    
    def update_date_value(self, entry_date: date, value: int):
        """
        更新指定日期的值
        
        Args:
            entry_date: 日期
            value: 新的字符数
        """
        # 更新数据
        self.data[entry_date] = value
        
        # 如果该日期在当前显示的网格中，更新单元格
        if entry_date in self.cells:
            self.cells[entry_date].set_value(value)
