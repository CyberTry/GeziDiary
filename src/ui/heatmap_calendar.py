# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
热力图日历模块

功能：展示类似GitHub贡献图的日历热力图，显示每日文本量
"""

from datetime import date, timedelta
from typing import Dict, Optional, List
import calendar

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent


class HeatmapCell(QFrame):
    """
    热力图单元格类
    
    表示单日的热力图单元格
    """
    
    clicked = pyqtSignal(date)
    
    # 颜色配置
    COLORS = {
        0: '#ebedf0',
        1: '#9be9a8',
        2: '#40c463',
        3: '#30a14e',
        4: '#216e39',
    }
    
    def __init__(self, cell_date: date, parent=None):
        super().__init__(parent)
        
        self.cell_date = cell_date
        self.value = 0
        self.level = 0
        self.is_today = (cell_date == date.today())
        
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._update_style()
    
    def set_value(self, value: int):
        """设置热力值"""
        self.value = value
        
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
        
        self._update_style()
    
    def _update_style(self):
        """更新样式"""
        color = self.COLORS.get(self.level, self.COLORS[0])
        
        border = '2px solid #f0883e' if self.is_today else '1px solid rgba(27,31,35,0.06)'
        
        self.setStyleSheet(f"""
            HeatmapCell {{
                background-color: {color};
                border: {border};
                border-radius: 3px;
            }}
            HeatmapCell:hover {{
                border: 2px solid #0969da;
            }}
        """)
    
    def enterEvent(self, event):
        """鼠标进入显示提示"""
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        weekday = weekdays[self.cell_date.weekday()]
        date_str = self.cell_date.strftime('%Y年%m月%d日')
        value_str = f'{self.value} 字符' if self.value > 0 else '无日记'
        self.setToolTip(f"{date_str} 星期{weekday}\n{value_str}")
        super().enterEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """点击发射信号"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.cell_date)
        super().mousePressEvent(event)


class MonthWidget(QWidget):
    """月份部件"""
    
    def __init__(self, year: int, month: int, data: Dict[date, int], parent=None):
        super().__init__(parent)
        
        self.year = year
        self.month = month
        self.data = data
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 月份标题
        title = QLabel(f"{self.month}月")
        title.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 星期标题
        weekday_layout = QHBoxLayout()
        weekday_layout.setSpacing(4)
        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        for day in weekdays:
            label = QLabel(day)
            label.setFont(QFont('Microsoft YaHei', 9))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(24, 20)
            weekday_layout.addWidget(label)
        layout.addLayout(weekday_layout)
        
        # 日期网格
        grid = QGridLayout()
        grid.setSpacing(4)
        
        # 获取该月第一天是星期几
        first_day = date(self.year, self.month, 1)
        first_weekday = first_day.weekday()
        first_weekday = (first_weekday + 1) % 7  # 转换为周日开始
        
        # 获取该月天数
        _, days_in_month = calendar.monthrange(self.year, self.month)
        
        # 填充空白
        for i in range(first_weekday):
            spacer = QLabel()
            spacer.setFixedSize(24, 24)
            grid.addWidget(spacer, 0, i)
        
        # 填充日期
        row = 0
        col = first_weekday
        
        for day in range(1, days_in_month + 1):
            cell_date = date(self.year, self.month, day)
            cell = HeatmapCell(cell_date)
            
            # 设置值
            value = self.data.get(cell_date, 0)
            cell.set_value(value)
            
            # 连接信号
            if hasattr(self.parent(), 'date_selected'):
                cell.clicked.connect(self.parent().date_selected)
            
            grid.addWidget(cell, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        layout.addLayout(grid)
        layout.addStretch()


class HeatmapCalendar(QWidget):
    """
    热力图日历部件
    
    展示全年日历热力图
    """
    
    date_selected = pyqtSignal(date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.year = date.today().year
        self.data: Dict[date, int] = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 标题栏
        header = QHBoxLayout()
        
        self.year_label = QLabel(str(self.year))
        self.year_label.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        header.addWidget(self.year_label)
        
        header.addStretch()
        
        # 图例
        legend = QLabel('少  □□□□□  多')
        legend.setFont(QFont('Microsoft YaHei', 10))
        header.addWidget(legend)
        
        layout.addLayout(header)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # 月份容器
        self.months_container = QWidget()
        self.months_layout = QGridLayout(self.months_container)
        self.months_layout.setSpacing(20)
        
        scroll.setWidget(self.months_container)
        layout.addWidget(scroll)
        
        # 初始化月份网格
        self._create_months()
    
    def _create_months(self):
        """创建月份网格"""
        # 清除旧内容
        while self.months_layout.count():
            item = self.months_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建12个月份
        for month in range(1, 13):
            month_widget = MonthWidget(self.year, month, self.data)
            row = (month - 1) // 4
            col = (month - 1) % 4
            self.months_layout.addWidget(month_widget, row, col)
    
    def set_year_data(self, year: int, data: Dict[date, int]):
        """设置年份数据"""
        self.year = year
        self.data = data
        self.year_label.setText(str(year))
        self._create_months()
    
    def set_selected_date(self, selected_date: date):
        """设置选中日期"""
        pass  # 简化版本不需要高亮选中


# 保持向后兼容
HeatmapCell.LIGHT_COLORS = HeatmapCell.COLORS
