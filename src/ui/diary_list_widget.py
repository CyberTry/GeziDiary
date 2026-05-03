"""
日记列表组件
============
显示日记列表，支持快速导航

特性：
- 按日期倒序排列
- 显示字数统计
- 点击快速跳转
- 滚动加载更多
"""

from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget,
    QVBoxLayout, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor

from datetime import date


class DiaryListItem(QWidget):
    """
    自定义日记列表项
    
    显示日记日期和字数信息
    """
    
    def __init__(self, diary_date, word_count, parent=None):
        """
        初始化列表项
        
        Args:
            diary_date: 日记日期
            word_count: 字数统计
            parent: 父部件
        """
        super().__init__(parent)
        
        self.diary_date = diary_date
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 日期显示
        date_layout = QVBoxLayout()
        date_layout.setSpacing(2)
        
        # 日期（日）
        day_label = QLabel(str(diary_date.day))
        day_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #24292e;
        """)
        date_layout.addWidget(day_label)
        
        # 月份和星期
        month_names = ['', '1月', '2月', '3月', '4月', '5月', '6月',
                       '7月', '8月', '9月', '10月', '11月', '12月']
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        month_week_label = QLabel(
            f"{diary_date.year}年{month_names[diary_date.month]} {weekday_names[diary_date.weekday()]}"
        )
        month_week_label.setStyleSheet("""
            font-size: 11px;
            color: #586069;
        """)
        date_layout.addWidget(month_week_label)
        
        layout.addLayout(date_layout)
        layout.addStretch()
        
        # 字数统计
        word_count_label = QLabel(f"{word_count} 字")
        word_count_label.setStyleSheet("""
            font-size: 12px;
            color: #28a745;
            font-weight: 500;
        """)
        layout.addWidget(word_count_label)


class DiaryListWidget(QListWidget):
    """
    日记列表组件
    
    显示所有日记的列表，支持快速选择
    
    Signals:
        diary_selected: 当用户选择某个日记时发出
    """
    
    # 自定义信号：日记被选择
    diary_selected = pyqtSignal(date)
    
    def __init__(self, parent=None):
        """
        初始化日记列表
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 存储日期到列表项的映射
        self.date_to_item = {}
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 设置样式
        self.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                outline: none;
            }
            
            QListWidget::item {
                border-bottom: 1px solid #e1e4e8;
                background-color: transparent;
            }
            
            QListWidget::item:selected {
                background-color: #f1f8ff;
                border-left: 3px solid #0366d6;
            }
            
            QListWidget::item:hover {
                background-color: #f6f8fa;
            }
            
            QListWidget::item:selected:hover {
                background-color: #f1f8ff;
            }
        """)
        
        # 设置选择模式
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # 连接选择信号
        self.itemClicked.connect(self._on_item_clicked)
    
    def set_diaries(self, diaries):
        """
        设置日记列表数据
        
        Args:
            diaries: 日记信息列表，每项包含date和word_count
        """
        # 清空现有内容
        self.clear()
        self.date_to_item.clear()
        
        # 添加日记项
        for diary in diaries:
            diary_date = diary['date']
            word_count = diary['word_count']
            
            # 创建自定义部件
            item_widget = DiaryListItem(diary_date, word_count)
            
            # 创建列表项
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, diary_date)
            
            # 添加到列表
            self.addItem(list_item)
            self.setItemWidget(list_item, item_widget)
            
            # 保存映射
            self.date_to_item[diary_date] = list_item
    
    def select_diary(self, diary_date):
        """
        选择指定日期的日记
        
        Args:
            diary_date: 要选择的日期
        """
        if diary_date in self.date_to_item:
            item = self.date_to_item[diary_date]
            self.setCurrentItem(item)
            self.scrollToItem(item)
    
    def _on_item_clicked(self, item):
        """
        列表项点击事件处理
        
        Args:
            item: 被点击的列表项
        """
        # 获取日期数据
        diary_date = item.data(Qt.ItemDataRole.UserRole)
        
        if diary_date:
            # 发出信号
            self.diary_selected.emit(diary_date)
    
    def add_diary(self, diary_date, word_count):
        """
        添加单个日记到列表
        
        Args:
            diary_date: 日记日期
            word_count: 字数统计
        """
        # 检查是否已存在
        if diary_date in self.date_to_item:
            return
        
        # 创建自定义部件
        item_widget = DiaryListItem(diary_date, word_count)
        
        # 创建列表项
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        list_item.setData(Qt.ItemDataRole.UserRole, diary_date)
        
        # 插入到列表开头（最新的在前）
        self.insertItem(0, list_item)
        self.setItemWidget(list_item, item_widget)
        
        # 保存映射
        self.date_to_item[diary_date] = list_item
    
    def update_diary(self, diary_date, word_count):
        """
        更新日记的字数显示
        
        Args:
            diary_date: 日记日期
            word_count: 新的字数统计
        """
        if diary_date in self.date_to_item:
            item = self.date_to_item[diary_date]
            
            # 创建新的部件
            item_widget = DiaryListItem(diary_date, word_count)
            self.setItemWidget(item, item_widget)
    
    def remove_diary(self, diary_date):
        """
        从列表中移除日记
        
        Args:
            diary_date: 要移除的日记日期
        """
        if diary_date in self.date_to_item:
            item = self.date_to_item[diary_date]
            row = self.row(item)
            self.takeItem(row)
            del self.date_to_item[diary_date]
