"""
统计信息组件
============
显示日记统计信息

显示内容：
- 总日记数
- 总字数
- 平均字数
- 连续写作天数
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    """
    统计卡片
    
    显示单个统计项的数值和标签
    """
    
    def __init__(self, title, value="0", parent=None):
        """
        初始化统计卡片
        
        Args:
            title: 统计项名称
            value: 统计值
            parent: 父部件
        """
        super().__init__(parent)
        
        # 设置样式
        self.setStyleSheet("""
            StatCard {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        # 数值标签
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #24292e;
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # 标题标签
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            color: #586069;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
    
    def set_value(self, value):
        """
        设置统计值
        
        Args:
            value: 新的统计值
        """
        self.value_label.setText(str(value))


class StatsWidget(QWidget):
    """
    统计信息组件
    
    显示日记的各项统计数据
    """
    
    def __init__(self, parent=None):
        """
        初始化统计组件
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("📈 统计信息")
        title.setObjectName("subtitle")
        layout.addWidget(title)
        
        # 统计卡片网格
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # 创建统计卡片
        self.total_diaries_card = StatCard("总日记数", "0")
        grid.addWidget(self.total_diaries_card, 0, 0)
        
        self.total_words_card = StatCard("总字数", "0")
        grid.addWidget(self.total_words_card, 0, 1)
        
        self.avg_words_card = StatCard("平均字数", "0")
        grid.addWidget(self.avg_words_card, 1, 0)
        
        self.streak_card = StatCard("连续天数", "0")
        grid.addWidget(self.streak_card, 1, 1)
        
        layout.addLayout(grid)
        
        # 最长连续记录
        self.longest_streak_label = QLabel("最长连续: 0 天")
        self.longest_streak_label.setStyleSheet("""
            font-size: 12px;
            color: #28a745;
            font-weight: 500;
            padding: 8px;
            background-color: #f6f8fa;
            border-radius: 4px;
        """)
        self.longest_streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.longest_streak_label)
        
        # 最高记录
        self.max_record_label = QLabel("单篇最高: 0 字")
        self.max_record_label.setStyleSheet("""
            font-size: 12px;
            color: #0366d6;
            font-weight: 500;
            padding: 8px;
            background-color: #f6f8fa;
            border-radius: 4px;
        """)
        self.max_record_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.max_record_label)
    
    def update_stats(self, stats):
        """
        更新统计数据
        
        Args:
            stats: 统计信息字典，包含：
                - total_diaries: 总日记数
                - total_words: 总字数
                - avg_words: 平均字数
                - streak_days: 当前连续天数
                - longest_streak: 最长连续天数
                - max_words: 单篇最高字数
                - max_words_date: 最高字数日期
        """
        # 更新卡片
        self.total_diaries_card.set_value(stats.get('total_diaries', 0))
        self.total_words_card.set_value(self._format_number(
            stats.get('total_words', 0)
        ))
        self.avg_words_card.set_value(stats.get('avg_words', 0))
        self.streak_card.set_value(stats.get('streak_days', 0))
        
        # 更新最长连续记录
        longest_streak = stats.get('longest_streak', 0)
        self.longest_streak_label.setText(f"🏆 最长连续: {longest_streak} 天")
        
        # 更新最高记录
        max_words = stats.get('max_words', 0)
        max_date = stats.get('max_words_date')
        if max_date:
            date_str = max_date.strftime("%m月%d日")
            self.max_record_label.setText(
                f"📝 单篇最高: {max_words} 字 ({date_str})"
            )
        else:
            self.max_record_label.setText(f"📝 单篇最高: {max_words} 字")
    
    def _format_number(self, num):
        """
        格式化数字显示
        
        大于1000的数字显示为x.xk格式
        
        Args:
            num: 要格式化的数字
            
        Returns:
            格式化后的字符串
        """
        if num >= 10000:
            return f"{num / 10000:.1f}w"
        elif num >= 1000:
            return f"{num / 1000:.1f}k"
        else:
            return str(num)
