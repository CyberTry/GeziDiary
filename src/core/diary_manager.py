"""
日记文件管理模块
================
负责日记文件的创建、读取、保存和删除操作。
日记按年月日格式组织存储：
    存储路径/年/月/YYYY-MM-DD.md

例如：
    ~/Documents/GeziDiary/2024/01/2024-01-15.md
"""

import os
import re
from pathlib import Path
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict


class DiaryManager:
    """
    日记管理器类
    
    负责管理日记文件的所有操作，包括：
    - 获取日记文件路径
    - 读取日记内容
    - 保存日记内容
    - 删除日记文件
    - 获取日记统计信息
    """
    
    def __init__(self, base_path: str):
        """
        初始化日记管理器
        
        Args:
            base_path: 日记文件的根存储路径
        """
        self.base_path = Path(base_path)
        # 确保根目录存在
        self._ensure_directory(self.base_path)
    
    def _ensure_directory(self, path: Path):
        """
        确保目录存在，不存在则创建
        
        Args:
            path: 要检查的目录路径
        """
        path.mkdir(parents=True, exist_ok=True)
    
    def _get_diary_path(self, year: int, month: int, day: int) -> Path:
        """
        根据日期获取日记文件的完整路径
        
        路径格式：base_path/年/月/YYYY-MM-DD.md
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            
        Returns:
            Path: 日记文件的完整路径
        """
        # 格式化年月，确保月份是两位数（01-12）
        month_str = f"{month:02d}"
        day_str = f"{day:02d}"
        
        # 构建目录路径：base_path/年/月/
        dir_path = self.base_path / str(year) / month_str
        
        # 确保目录存在
        self._ensure_directory(dir_path)
        
        # 返回完整文件路径
        return dir_path / f"{year}-{month_str}-{day_str}.md"
    
    def get_diary_by_date(self, target_date: date) -> Path:
        """
        根据date对象获取日记文件路径
        
        Args:
            target_date: 目标日期
            
        Returns:
            Path: 日记文件路径
        """
        return self._get_diary_path(target_date.year, target_date.month, target_date.day)
    
    def diary_exists(self, target_date: date) -> bool:
        """
        检查指定日期的日记是否存在
        
        Args:
            target_date: 要检查的日期
            
        Returns:
            bool: 日记是否存在
        """
        return self.get_diary_by_date(target_date).exists()
    
    def read_diary(self, target_date: date) -> str:
        """
        读取指定日期的日记内容
        
        Args:
            target_date: 要读取的日期
            
        Returns:
            str: 日记内容，如果文件不存在返回空字符串
        """
        file_path = self.get_diary_by_date(target_date)
        
        # 检查文件是否存在
        if not file_path.exists():
            return ""
        
        try:
            # 以UTF-8编码读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # 读取失败时打印错误并返回空字符串
            print(f"读取日记失败 {file_path}: {e}")
            return ""
    
    def save_diary(self, target_date: date, content: str) -> bool:
        """
        保存日记内容到指定日期
        
        Args:
            target_date: 日记日期
            content: 日记内容（Markdown格式）
            
        Returns:
            bool: 保存是否成功
        """
        file_path = self.get_diary_by_date(target_date)
        
        try:
            # 以UTF-8编码写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            # 保存失败时打印错误
            print(f"保存日记失败 {file_path}: {e}")
            return False
    
    def delete_diary(self, target_date: date) -> bool:
        """
        删除指定日期的日记
        
        Args:
            target_date: 要删除的日记日期
            
        Returns:
            bool: 删除是否成功
        """
        file_path = self.get_diary_by_date(target_date)
        
        # 检查文件是否存在
        if not file_path.exists():
            return False
        
        try:
            # 删除文件
            file_path.unlink()
            return True
        except Exception as e:
            # 删除失败时打印错误
            print(f"删除日记失败 {file_path}: {e}")
            return False
    
    def get_word_count(self, target_date: date) -> int:
        """
        获取指定日期日记的字数统计
        
        统计规则：
        - 中文字符：每个字符算1个字
        - 英文单词：按空格分隔
        
        Args:
            target_date: 日记日期
            
        Returns:
            int: 字数统计
        """
        content = self.read_diary(target_date)
        
        if not content:
            return 0
        
        # 统计中文字符数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        
        # 统计英文单词数（去除Markdown标记后统计）
        # 移除Markdown标记符号
        clean_content = re.sub(r'[#*_`\[\]()]', ' ', content)
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', clean_content))
        
        # 总字数 = 中文字符数 + 英文单词数
        return chinese_chars + english_words
    
    def get_all_diaries(self, year: Optional[int] = None, month: Optional[int] = None) -> List[Tuple[date, Path]]:
        """
        获取所有日记文件列表
        
        Args:
            year: 可选，筛选特定年份
            month: 可选，筛选特定月份
            
        Returns:
            List[Tuple[date, Path]]: 日记列表，每项为 (日期, 文件路径) 元组
        """
        diaries = []
        
        # 构建搜索路径
        search_path = self.base_path
        if year:
            search_path = search_path / str(year)
            if month:
                search_path = search_path / f"{month:02d}"
        
        # 如果路径不存在，返回空列表
        if not search_path.exists():
            return diaries
        
        # 遍历目录查找所有.md文件
        for md_file in search_path.rglob("*.md"):
            # 从文件名解析日期
            try:
                # 文件名格式：YYYY-MM-DD.md
                date_str = md_file.stem  # 获取不带扩展名的文件名
                file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                diaries.append((file_date, md_file))
            except ValueError:
                # 文件名格式不符合，跳过
                continue
        
        # 按日期排序（最新的在前）
        diaries.sort(key=lambda x: x[0], reverse=True)
        
        return diaries
    
    def get_yearly_stats(self, year: int) -> Dict[date, int]:
        """
        获取指定年份的每日字数统计
        
        用于生成日历热力图的数据。
        
        Args:
            year: 年份
            
        Returns:
            Dict[date, int]: 日期到字数的映射字典
        """
        stats = {}
        
        # 获取该年份的所有日记
        diaries = self.get_all_diaries(year=year)
        
        for file_date, file_path in diaries:
            # 读取内容并统计字数
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 统计中文字符
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
                # 统计英文单词
                clean_content = re.sub(r'[#*_`\[\]()]', ' ', content)
                english_words = len(re.findall(r'[a-zA-Z]+', clean_content))
                
                stats[file_date] = chinese_chars + english_words
            except Exception:
                stats[file_date] = 0
        
        return stats
    
    def get_date_range(self) -> Tuple[Optional[date], Optional[date]]:
        """
        获取日记的日期范围
        
        Returns:
            Tuple[Optional[date], Optional[date]]: (最早日期, 最晚日期)
        """
        diaries = self.get_all_diaries()
        
        if not diaries:
            return None, None
        
        # 列表已按日期降序排列
        latest_date = diaries[0][0]
        earliest_date = diaries[-1][0]
        
        return earliest_date, latest_date
