# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
工具函数模块

功能：提供各种辅助函数
"""

import os
import re
from datetime import date, datetime
from typing import Optional


def format_date_cn(d: date) -> str:
    """
    格式化日期为中文格式
    
    Args:
        d: 日期对象
    
    Returns:
        str: 格式为"YYYY年MM月DD日 星期X"的字符串
    """
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[d.weekday()]
    return f"{d.year}年{d.month:02d}月{d.day:02d}日 星期{weekday}"


def format_date_short(d: date) -> str:
    """
    格式化日期为简短格式
    
    Args:
        d: 日期对象
    
    Returns:
        str: 格式为"YYYY-MM-DD"的字符串
    """
    return d.strftime('%Y-%m-%d')


def parse_date(date_str: str) -> Optional[date]:
    """
    解析日期字符串
    
    支持格式：YYYY-MM-DD, YYYY/MM/DD, YYYY年MM月DD日
    
    Args:
        date_str: 日期字符串
    
    Returns:
        date: 解析成功返回date对象，失败返回None
    """
    # 定义支持的格式
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y年%m月%d日',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


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


def ensure_dir(path: str) -> bool:
    """
    确保目录存在，不存在则创建
    
    Args:
        path: 目录路径
    
    Returns:
        bool: 成功返回True
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_size(path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        path: 文件路径
    
    Returns:
        int: 文件大小，文件不存在返回0
    """
    try:
        return os.path.getsize(path)
    except Exception:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 字节数
    
    Returns:
        str: 格式化后的字符串（如：1.5 KB）
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀字符串
    
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def count_chinese_chars(text: str) -> int:
    """
    统计中文字符数量
    
    Args:
        text: 文本
    
    Returns:
        int: 中文字符数
    """
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def count_words(text: str) -> int:
    """
    统计词数（中文+英文）
    
    Args:
        text: 文本
    
    Returns:
        int: 词数
    """
    # 中文字符
    chinese = count_chinese_chars(text)
    # 英文单词
    english = len(re.findall(r'[a-zA-Z]+', text))
    
    return chinese + english


def strip_markdown(text: str) -> str:
    """
    移除Markdown标记，提取纯文本
    
    Args:
        text: Markdown文本
    
    Returns:
        str: 纯文本
    """
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # 移除行内代码
    text = re.sub(r'`[^`]*`', '', text)
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除标题标记
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # 移除粗体和斜体标记
    text = re.sub(r'\*\*?|\_\_?', '', text)
    
    # 移除链接标记，保留文本
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)
    
    # 移除图片标记
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    
    # 移除引用标记
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # 移除列表标记
    text = re.sub(r'^[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 规范化空白字符
    text = re.sub(r'\n+', '\n', text)
    text = text.strip()
    
    return text


def get_summary(text: str, max_length: int = 100) -> str:
    """
    获取文本摘要
    
    Args:
        text: 原始文本
        max_length: 最大长度
    
    Returns:
        str: 文本摘要
    """
    # 移除Markdown标记
    plain_text = strip_markdown(text)
    
    # 截断到指定长度
    return truncate_text(plain_text, max_length)
