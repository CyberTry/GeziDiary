"""
日历热力图组件
==============
类似GitHub贡献图的日历热力图，用于展示每日日记字数。
使用不同深度的绿色表示不同的字数范围。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGridLayout, QFrame, QToolTip, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QColor, QPainter, QBrush, QFont, QMouseEvent

from datetime import date, timedelta
from calendar import monthrange
from typing import Dict, Optional, Callable


class HeatmapCell(QFrame):
    """
    热力图单元格
    
    表示某一天的数据，根据数值显示不同颜色深度。
    """
    
    # 颜色等级定义（从浅到深）
    COLORS = [
        "#ebedf0",  # 等级0: 无数据（浅灰）
        "#9be9a8",  # 等级1: 少量（浅绿）
        "#40c463",  # 等级2: 中等（中绿）
        "#30a14e",  # 等级3: 较多（深绿）
        "#216e39",  # 等级4: 大量（最深绿）
    ]
    
    # 字数阈值定义
    THRESHOLDS = [0, 100, 300, 600, 1000]
    
    clicked = pyqtSignal(date)  # 点击信号
    
    def __init__(self, cell_date: date, word_count: int = 0, parent=None):
        """
        初始化单元格
        
        Args:
            cell_date: 单元格代表的日期
            word_count: 字数统计
            parent: 父组件
        """
        super().__init__(parent)
        
        self.cell_date = cell_date
        self.word_count = word_count
        self.level = self._calculate_level()
        
        # 设置固定大小
        self.setFixedSize(14, 14)
        
        # 设置样式
        self._update_style()
        
        # 启用鼠标跟踪以显示工具提示
        self.setMouseTracking(True)
    
    def _calculate_level(self) -> int:
        """
        根据字数计算颜色等级
        
        Returns:
            int: 颜色等级 (0-4)
        """
        for i, threshold in enumerate(self.THRESHOLDS):
            if self.word_count < threshold:
                return max(0, i - 1)
        return 4
    
    def _update_style(self):
        """
        更新单元格样式
        """
        color = self.COLORS[self.level]
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 2px;
                border: 1px solid rgba(27, 31, 35, 0.06);
            }}
            QFrame:hover {{
                border: 1px solid rgba(27, 31, 35, 0.3);
            }}
        """)
    
    def set_word_count(self, count: int):
        """
        设置字数并更新显示
        
        Args:
            count: 新的字数
        """
        self.word_count = count
        new_level = self._calculate_level()
        if new_level != self.level:
            self.level = new_level
            self._update_style()
    
    def mousePressEvent(self, event: QMouseEvent):
        """
        鼠标点击事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.cell_date)
    
    def enterEvent(self, event):
        """
        鼠标进入事件 - 显示工具提示
        """
        date_str = self.cell_date.strftime("%Y年%m月%d日")
        tooltip = f"{date_str}\n字数: {self.word_count}"
        self.setToolTip(tooltip)


class HeatmapCalendar(QWidget):
    """
    日历热力图组件
    
    显示一整年的日历热力图，类似GitHub的贡献图。
    支持点击日期跳转、月份标签显示等功能。
    
    Signals:
        date_selected: 当用户点击某个日期时发射
    """
    
    date_selected = pyqtSignal(date)  # 日期选择信号
    
    def __init__(self, parent=None):
        """
        初始化日历热力图
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        # 当前显示的年份
        self.current_year = date.today().year
        
        # 存储所有单元格的字典 {date: HeatmapCell}
        self.cells: Dict[date, HeatmapCell] = {}
        
        # 数据获取回调函数
        self.data_callback: Optional[Callable[[int], Dict[date, int]]] = None
        
        # 初始化UI
        self._init_ui()
        
        # 加载当前年份的数据
        self.load_year(self.current_year)
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建标题栏
        header_layout = QHBoxLayout()
        
        # 年份标签
        self.year_label = QLabel(str(self.current_year))
        self.year_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #24292e;")
        header_layout.addWidget(self.year_label)
        
        header_layout.addStretch()
        
        # 图例
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(4)
        
        legend_label = QLabel("少")
        legend_label.setStyleSheet("color: #586069; font-size: 11px;")
        legend_layout.addWidget(legend_label)
        
        # 添加颜色等级示例
        for i, color in enumerate(HeatmapCell.COLORS):
            legend_cell = QFrame()
            legend_cell.setFixedSize(12, 12)
            legend_cell.setStyleSheet(f"""
                background-color: {color};
                border-radius: 2px;
                border: 1px solid rgba(27, 31, 35, 0.06);
            """)
            legend_layout.addWidget(legend_cell)
        
        legend_label2 = QLabel("多")
        legend_label2.setStyleSheet("color: #586069; font-size: 11px;")
        legend_layout.addWidget(legend_label2)
        
        header_layout.addLayout(legend_layout)
        layout.addLayout(header_layout)
        
        # 创建热力图网格容器
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.grid_widget = QWidget()
        self.grid_layout = QHBoxLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.grid_widget)
        layout.addWidget(scroll_area)
        
        # 初始化网格
        self._create_grid()
    
    def _create_grid(self):
        """
        创建热力图网格
        
        按照GitHub风格，每列代表一周，每行代表星期几。
        """
        # 清空现有单元格
        self.cells.clear()
        
        # 清除布局中的所有widget
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建月份标签行
        months_widget = QWidget()
        months_layout = QVBoxLayout(months_widget)
        months_layout.setSpacing(0)
        months_layout.setContentsMargins(0, 0, 0, 0)
        
        # 空白占位（对应星期标签的位置）
        spacer = QLabel()
        spacer.setFixedSize(30, 20)
        months_layout.addWidget(spacer)
        
        # 月份标签容器
        months_row = QWidget()
        months_row_layout = QHBoxLayout(months_row)
        months_row_layout.setSpacing(0)
        months_row_layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算每个月的起始位置
        year_start = date(self.current_year, 1, 1)
        # 找到第一个周日（或该年的第一天）
        first_day = year_start - timedelta(days=year_start.weekday() + 1)
        if first_day.year < self.current_year:
            first_day = year_start
        
        # 添加月份标签
        current_month = 0
        month_names = ["1月", "2月", "3月", "4月", "5月", "6月",
                      "7月", "8月", "9月", "10月", "11月", "12月"]
        
        # 这里简化处理，在网格上方显示月份
        months_layout.addWidget(months_row)
        self.grid_layout.addWidget(months_widget)
        
        # 创建主网格
        grid_container = QWidget()
        grid_container_layout = QHBoxLayout(grid_container)
        grid_container_layout.setSpacing(4)
        grid_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 星期标签
        weekdays_widget = QWidget()
        weekdays_layout = QVBoxLayout(weekdays_widget)
        weekdays_layout.setSpacing(4)
        weekdays_layout.setContentsMargins(0, 0, 5, 0)
        
        weekday_labels = ["", "一", "", "三", "", "五", ""]
        for label_text in weekday_labels:
            label = QLabel(label_text)
            label.setFixedSize(20, 14)
            label.setStyleSheet("color: #586069; font-size: 10px;")
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            weekdays_layout.addWidget(label)
        
        grid_container_layout.addWidget(weekdays_widget)
        
        # 创建日期网格
        self.cells_grid = QGridLayout()
        self.cells_grid.setSpacing(3)
        self.cells_grid.setContentsMargins(0, 0, 0, 0)
        
        # 计算该年的所有日期
        start_date = date(self.current_year, 1, 1)
        end_date = date(self.current_year, 12, 31)
        
        # 从该年第一个周日开始（或该年第一天）
        current_date = start_date - timedelta(days=start_date.weekday() + 1)
        if current_date.year < self.current_year:
            current_date = start_date
        
        col = 0
        while current_date <= end_date:
            for row in range(7):  # 0=周一, 6=周日
                if current_date.year == self.current_year:
                    # 创建单元格
                    cell = HeatmapCell(current_date, 0)
                    cell.clicked.connect(self._on_cell_clicked)
                    self.cells[current_date] = cell
                    self.cells_grid.addWidget(cell, row, col)
                
                current_date += timedelta(days=1)
                if current_date > end_date:
                    break
            
            col += 1
            if current_date > end_date:
                break
        
        grid_widget = QWidget()
        grid_widget.setLayout(self.cells_grid)
        grid_container_layout.addWidget(grid_widget)
        grid_container_layout.addStretch()
        
        self.grid_layout.addWidget(grid_container)
        self.grid_layout.addStretch()
    
    def _on_cell_clicked(self, clicked_date: date):
        """
        单元格点击处理
        
        Args:
            clicked_date: 被点击的日期
        """
        self.date_selected.emit(clicked_date)
    
    def set_data_callback(self, callback: Callable[[int], Dict[date, int]]):
        """
        设置数据获取回调函数
        
        Args:
            callback: 回调函数，接收年份参数，返回日期到字数的映射字典
        """
        self.data_callback = callback
        # 重新加载当前年份数据
        self.load_year(self.current_year)
    
    def load_year(self, year: int):
        """
        加载指定年份的数据
        
        Args:
            year: 年份
        """
        self.current_year = year
        self.year_label.setText(str(year))
        
        # 如果年份改变，需要重新创建网格
        if not self.cells or list(self.cells.keys())[0].year != year:
            self._create_grid()
        
        # 如果有数据回调，获取数据
        if self.data_callback:
            data = self.data_callback(year)
            self.update_data(data)
    
    def update_data(self, data: Dict[date, int]):
        """
        更新热力图数据
        
        Args:
            data: 日期到字数的映射字典
        """
        for cell_date, cell in self.cells.items():
            word_count = data.get(cell_date, 0)
            cell.set_word_count(word_count)
    
    def set_cell_data(self, cell_date: date, word_count: int):
        """
        设置单个单元格的数据
        
        Args:
            cell_date: 日期
            word_count: 字数
        """
        if cell_date in self.cells:
            self.cells[cell_date].set_word_count(word_count)
    
    def get_current_year(self) -> int:
        """
        获取当前显示的年份
        
        Returns:
            int: 当前年份
        """
        return self.current_year
    
    def previous_year(self):
        """
        切换到上一年
        """
        self.load_year(self.current_year - 1)
    
    def next_year(self):
        """
        切换到下一年
        """
        self.load_year(self.current_year + 1)
