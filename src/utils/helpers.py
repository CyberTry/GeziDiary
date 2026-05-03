"""
辅助工具函数
============
提供各种实用的辅助函数。
"""

import re
from datetime import date


def format_date(target_date: date, format_str: str = "%Y年%m月%d日") -> str:
    """
    格式化日期
    
    Args:
        target_date: 要格式化的日期
        format_str: 格式字符串，默认为 "%Y年%m月%d日"
        
    Returns:
        str: 格式化后的日期字符串
    """
    return target_date.strftime(format_str)


def get_word_count_text(text: str) -> tuple:
    """
    统计文本字数
    
    统计规则：
    - 中文字符：每个字符算1个字
    - 英文单词：按空格分隔，每个单词算1个字
    
    Args:
        text: 要统计的文本
        
    Returns:
        tuple: (中文字符数, 英文单词数, 总字数)
    """
    if not text:
        return 0, 0, 0
    
    # 统计中文字符数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # 统计英文单词数
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    
    # 总字数
    total = chinese_chars + english_words
    
    return chinese_chars, english_words, total


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # Windows非法字符: < > : " / \ | ? *
    illegal_chars = r'[<>:"/\\|?*]'
    return re.sub(illegal_chars, '_', filename)
