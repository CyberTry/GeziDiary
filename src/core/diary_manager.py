# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
日记管理模块

功能：管理日记文件的创建、读取、保存和删除
日记按年月日格式保存为独立文件
"""

import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Tuple


class DiaryEntry:
    """
    单篇日记条目类
    
    表示一天的日记内容，包含日期、内容、字符数等信息
    
    Attributes:
        date (date): 日记日期
        content (str): 日记内容（Markdown格式）
        char_count (int): 字符数量
        word_count (int): 词数（粗略统计）
        file_path (str): 日记文件路径
    """
    
    def __init__(self, entry_date: date, content: str = '', file_path: str = ''):
        """
        初始化日记条目
        
        Args:
            entry_date: 日记日期
            content: 日记内容
            file_path: 日记文件路径
        """
        self.date = entry_date
        self.content = content
        self.file_path = file_path
        
        # 计算文本统计信息
        self._update_stats()
    
    def _update_stats(self):
        """
        更新文本统计信息
        
        计算字符数和词数
        """
        # 字符数（包含所有字符）
        self.char_count = len(self.content)
        
        # 词数（粗略统计：中文字符 + 英文单词）
        # 中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', self.content))
        # 英文单词（连续的字母序列）
        english_words = len(re.findall(r'[a-zA-Z]+', self.content))
        
        self.word_count = chinese_chars + english_words
    
    def update_content(self, new_content: str):
        """
        更新日记内容
        
        Args:
            new_content: 新的日记内容
        """
        self.content = new_content
        self._update_stats()
    
    def is_empty(self) -> bool:
        """
        检查日记是否为空
        
        Returns:
            bool: 如果内容为空或只有空白字符返回True
        """
        return not self.content or not self.content.strip()
    
    def get_formatted_date(self) -> str:
        """
        获取格式化的日期字符串
        
        Returns:
            str: 格式为"YYYY年MM月DD日 星期X"的字符串
        """
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        weekday = weekdays[self.date.weekday()]
        return f"{self.date.year}年{self.date.month:02d}月{self.date.day:02d}日 星期{weekday}"
    
    def get_short_date(self) -> str:
        """
        获取简短日期字符串
        
        Returns:
            str: 格式为"YYYY-MM-DD"的字符串
        """
        return self.date.strftime('%Y-%m-%d')


class DiaryManager:
    """
    日记管理器类
    
    负责管理所有日记文件的CRUD操作
    日记按年月日格式存储，目录结构：存储路径/年/月/日.md
    
    Attributes:
        storage_path (str): 日记存储根目录
        current_entry (DiaryEntry): 当前打开的日记条目
    """
    
    # 日记文件扩展名
    FILE_EXTENSION = '.md'
    
    def __init__(self, storage_path: str):
        """
        初始化日记管理器
        
        Args:
            storage_path: 日记存储根目录
        """
        self.storage_path = storage_path
        self.current_entry: Optional[DiaryEntry] = None
        
        # 确保存储目录存在
        self._ensure_storage_path()
    
    def _ensure_storage_path(self):
        """
        确保存储路径存在
        
        如果不存在则创建目录
        """
        if self.storage_path and not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path, exist_ok=True)
            except Exception as e:
                raise IOError(f"无法创建存储目录: {e}")
    
    def _get_file_path(self, entry_date: date) -> str:
        """
        根据日期获取日记文件路径
        
        路径格式：存储路径/年/月/日.md
        
        Args:
            entry_date: 日记日期
        
        Returns:
            str: 日记文件的完整路径
        """
        # 构建路径：年/月/日.md
        year_dir = str(entry_date.year)
        month_dir = f"{entry_date.month:02d}"
        day_file = f"{entry_date.day:02d}{self.FILE_EXTENSION}"
        
        return os.path.join(self.storage_path, year_dir, month_dir, day_file)
    
    def _ensure_dir_exists(self, file_path: str):
        """
        确保文件所在目录存在
        
        Args:
            file_path: 文件路径
        """
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    def load_entry(self, entry_date: date) -> DiaryEntry:
        """
        加载指定日期的日记
        
        Args:
            entry_date: 要加载的日期
        
        Returns:
            DiaryEntry: 日记条目对象（如果不存在则返回空内容的条目）
        """
        file_path = self._get_file_path(entry_date)
        
        content = ''
        
        # 如果文件存在，读取内容
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"读取日记文件失败: {e}")
        
        # 创建日记条目对象
        entry = DiaryEntry(entry_date, content, file_path)
        self.current_entry = entry
        
        return entry
    
    def save_entry(self, entry: DiaryEntry) -> bool:
        """
        保存日记条目
        
        Args:
            entry: 要保存的日记条目
        
        Returns:
            bool: 保存成功返回True
        """
        # 如果内容为空，可以选择删除文件
        if entry.is_empty():
            return self.delete_entry(entry.date)
        
        # 确保目录存在
        self._ensure_dir_exists(entry.file_path)
        
        try:
            # 写入文件
            with open(entry.file_path, 'w', encoding='utf-8') as f:
                f.write(entry.content)
            
            # 更新统计信息
            entry._update_stats()
            
            return True
            
        except Exception as e:
            print(f"保存日记失败: {e}")
            return False
    
    def delete_entry(self, entry_date: date) -> bool:
        """
        删除指定日期的日记
        
        Args:
            entry_date: 要删除的日期
        
        Returns:
            bool: 删除成功返回True（文件不存在也返回True）
        """
        file_path = self._get_file_path(entry_date)
        
        # 如果文件存在，删除它
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                
                # 尝试清理空目录
                self._cleanup_empty_dirs(file_path)
                
                return True
            except Exception as e:
                print(f"删除日记失败: {e}")
                return False
        
        return True
    
    def _cleanup_empty_dirs(self, file_path: str):
        """
        清理空目录
        
        删除文件后，如果上级目录为空则一并删除
        
        Args:
            file_path: 被删除的文件路径
        """
        # 从文件所在目录开始向上清理
        current_dir = os.path.dirname(file_path)
        
        while current_dir and current_dir != self.storage_path:
            # 如果目录为空，删除它
            if os.path.exists(current_dir) and not os.listdir(current_dir):
                try:
                    os.rmdir(current_dir)
                except Exception:
                    break
                current_dir = os.path.dirname(current_dir)
            else:
                break
    
    def entry_exists(self, entry_date: date) -> bool:
        """
        检查指定日期的日记是否存在
        
        Args:
            entry_date: 要检查的日期
        
        Returns:
            bool: 日记存在返回True
        """
        file_path = self._get_file_path(entry_date)
        return os.path.exists(file_path)
    
    def get_entry_char_count(self, entry_date: date) -> int:
        """
        获取指定日期日记的字符数
        
        Args:
            entry_date: 日期
        
        Returns:
            int: 字符数（日记不存在返回0）
        """
        if not self.entry_exists(entry_date):
            return 0
        
        entry = self.load_entry(entry_date)
        return entry.char_count
    
    def get_entries_by_month(self, year: int, month: int) -> List[DiaryEntry]:
        """
        获取指定月份的所有日记
        
        Args:
            year: 年份
            month: 月份
        
        Returns:
            List[DiaryEntry]: 该月份的所有日记条目列表
        """
        entries = []
        
        # 构建月份目录路径
        month_dir = os.path.join(self.storage_path, str(year), f"{month:02d}")
        
        # 如果目录不存在，返回空列表
        if not os.path.exists(month_dir):
            return entries
        
        # 遍历目录中的所有.md文件
        for filename in sorted(os.listdir(month_dir)):
            if filename.endswith(self.FILE_EXTENSION):
                try:
                    # 从文件名解析日期
                    day = int(filename[:-len(self.FILE_EXTENSION)])
                    entry_date = date(year, month, day)
                    
                    # 加载日记
                    entry = self.load_entry(entry_date)
                    entries.append(entry)
                    
                except ValueError:
                    # 文件名格式不正确，跳过
                    continue
        
        return entries
    
    def get_entries_by_year(self, year: int) -> List[DiaryEntry]:
        """
        获取指定年份的所有日记
        
        Args:
            year: 年份
        
        Returns:
            List[DiaryEntry]: 该年份的所有日记条目列表
        """
        entries = []
        
        # 构建年份目录路径
        year_dir = os.path.join(self.storage_path, str(year))
        
        # 如果目录不存在，返回空列表
        if not os.path.exists(year_dir):
            return entries
        
        # 遍历所有月份目录
        for month_dir_name in sorted(os.listdir(year_dir)):
            month_dir = os.path.join(year_dir, month_dir_name)
            
            # 确保是目录
            if not os.path.isdir(month_dir):
                continue
            
            try:
                month = int(month_dir_name)
                # 获取该月份的日记
                month_entries = self.get_entries_by_month(year, month)
                entries.extend(month_entries)
            except ValueError:
                continue
        
        # 按日期排序
        entries.sort(key=lambda e: e.date)
        
        return entries
    
    def get_all_entries(self) -> List[DiaryEntry]:
        """
        获取所有日记
        
        Returns:
            List[DiaryEntry]: 所有日记条目列表
        """
        entries = []
        
        # 如果存储路径不存在，返回空列表
        if not os.path.exists(self.storage_path):
            return entries
        
        # 遍历所有年份目录
        for year_dir_name in os.listdir(self.storage_path):
            year_dir = os.path.join(self.storage_path, year_dir_name)
            
            # 确保是目录且名称是数字（年份）
            if not os.path.isdir(year_dir) or not year_dir_name.isdigit():
                continue
            
            try:
                year = int(year_dir_name)
                # 获取该年份的日记
                year_entries = self.get_entries_by_year(year)
                entries.extend(year_entries)
            except ValueError:
                continue
        
        # 按日期排序
        entries.sort(key=lambda e: e.date)
        
        return entries
    
    def get_date_range(self) -> Tuple[Optional[date], Optional[date]]:
        """
        获取日记日期范围
        
        Returns:
            Tuple[date, date]: (最早日期, 最晚日期)，如果没有日记返回(None, None)
        """
        entries = self.get_all_entries()
        
        if not entries:
            return None, None
        
        return entries[0].date, entries[-1].date
    
    def get_stats(self) -> Dict:
        """
        获取日记统计信息
        
        Returns:
            Dict: 包含各种统计信息的字典
        """
        entries = self.get_all_entries()
        
        total_entries = len(entries)
        total_chars = sum(e.char_count for e in entries)
        total_words = sum(e.word_count for e in entries)
        
        # 计算连续写日记天数
        streak = self._calculate_streak(entries)
        
        return {
            'total_entries': total_entries,
            'total_chars': total_chars,
            'total_words': total_words,
            'avg_chars': total_chars // total_entries if total_entries > 0 else 0,
            'current_streak': streak,
            'first_entry': entries[0].date if entries else None,
            'last_entry': entries[-1].date if entries else None,
        }
    
    def _calculate_streak(self, entries: List[DiaryEntry]) -> int:
        """
        计算连续写日记天数
        
        从今天往前数，统计连续有日记的天数
        
        Args:
            entries: 日记条目列表（必须按日期排序）
        
        Returns:
            int: 连续天数
        """
        if not entries:
            return 0
        
        # 获取所有有日记的日期集合
        entry_dates = {e.date for e in entries}
        
        # 从今天开始往前数
        today = date.today()
        streak = 0
        current_date = today
        
        # 检查今天是否有日记，没有则从昨天开始
        while current_date in entry_dates:
            streak += 1
            current_date = date.fromordinal(current_date.toordinal() - 1)
        
        return streak
