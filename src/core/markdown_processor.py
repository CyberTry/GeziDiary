# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
Markdown处理模块

功能：将Markdown文本转换为HTML，支持代码高亮
"""

import re
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class MarkdownProcessor:
    """
    Markdown处理器类
    
    负责将Markdown文本转换为HTML，支持语法高亮和自定义样式
    
    Attributes:
        md (markdown.Markdown): Markdown解析器实例
    
    使用示例：
        >>> processor = MarkdownProcessor()
        >>> html = processor.to_html('# 标题\\n\\n正文内容')
    """
    
    def __init__(self):
        """
        初始化Markdown处理器
        
        配置Markdown扩展和选项
        """
        # ============================================
        # 配置Markdown扩展
        # ============================================
        self.md = markdown.Markdown(
            extensions=[
                # 代码块语法高亮
                'fenced_code',
                # 表格支持
                'tables',
                # 自动转换URL为链接
                'nl2br',
                # 删除线 ~~text~~
                'sane_lists',
            ],
            # 启用扩展配置
            extension_configs={
                'fenced_code': {
                    'lang_prefix': 'language-',
                }
            }
        )
    
    def to_html(self, text: str) -> str:
        """
        将Markdown文本转换为HTML
        
        Args:
            text: Markdown格式的文本
        
        Returns:
            str: 转换后的HTML字符串
        
        注意：
            每次转换前会重置解析器状态，避免多次转换时的状态污染
        """
        if not text:
            return ''
        
        # 重置解析器状态（重要：避免多次转换时的累积问题）
        self.md.reset()
        
        # 转换Markdown为HTML
        html = self.md.convert(text)
        
        # 包装在article标签中，便于样式控制
        return f'<article class="markdown-body">{html}</article>'
    
    def to_html_with_style(self, text: str, theme: str = 'light') -> str:
        """
        将Markdown转换为带样式的完整HTML文档
        
        Args:
            text: Markdown格式的文本
            theme: 主题样式（'light' 或 'dark'）
        
        Returns:
            str: 完整的HTML文档字符串
        """
        # 转换Markdown内容
        content = self.to_html(text)
        
        # 获取CSS样式
        css = self._get_css(theme)
        
        # 组装完整HTML文档
        html_doc = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {css}
    </style>
</head>
<body>
    {content}
</body>
</html>'''
        
        return html_doc
    
    def _get_css(self, theme: str = 'light') -> str:
        """
        获取Markdown渲染的CSS样式
        
        Args:
            theme: 主题样式
        
        Returns:
            str: CSS样式字符串
        """
        # 基础样式（适用于两种主题）
        base_css = '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
                         "Microsoft YaHei", "PingFang SC", sans-serif;
            font-size: 14px;
            line-height: 1.8;
            padding: 20px;
        }
        
        .markdown-body {
            max-width: 100%;
        }
        
        /* 标题样式 */
        .markdown-body h1,
        .markdown-body h2,
        .markdown-body h3,
        .markdown-body h4,
        .markdown-body h5,
        .markdown-body h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        
        .markdown-body h1 {
            font-size: 2em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid;
        }
        
        .markdown-body h2 {
            font-size: 1.5em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid;
        }
        
        .markdown-body h3 {
            font-size: 1.25em;
        }
        
        .markdown-body h4 {
            font-size: 1em;
        }
        
        /* 段落和文本 */
        .markdown-body p {
            margin-bottom: 16px;
        }
        
        .markdown-body a {
            text-decoration: none;
        }
        
        .markdown-body a:hover {
            text-decoration: underline;
        }
        
        /* 列表 */
        .markdown-body ul,
        .markdown-body ol {
            margin-bottom: 16px;
            padding-left: 2em;
        }
        
        .markdown-body li {
            margin-bottom: 4px;
        }
        
        /* 代码 */
        .markdown-body code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", 
                         Menlo, Courier, monospace;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 85%;
        }
        
        .markdown-body pre {
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            border-radius: 6px;
            margin-bottom: 16px;
        }
        
        .markdown-body pre code {
            padding: 0;
            background: transparent;
            font-size: 100%;
        }
        
        /* 引用块 */
        .markdown-body blockquote {
            padding: 0 1em;
            border-left: 0.25em solid;
            margin-bottom: 16px;
        }
        
        /* 表格 */
        .markdown-body table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        
        .markdown-body th,
        .markdown-body td {
            padding: 6px 13px;
            border: 1px solid;
        }
        
        .markdown-body th {
            font-weight: 600;
        }
        
        /* 分隔线 */
        .markdown-body hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            border: 0;
        }
        
        /* 图片 */
        .markdown-body img {
            max-width: 100%;
            height: auto;
        }
        '''
        
        # 亮色主题
        light_theme = '''
        body {
            background-color: #ffffff;
            color: #24292e;
        }
        
        .markdown-body h1,
        .markdown-body h2 {
            border-bottom-color: #eaecef;
        }
        
        .markdown-body a {
            color: #0366d6;
        }
        
        .markdown-body code {
            background-color: rgba(27, 31, 35, 0.05);
        }
        
        .markdown-body pre {
            background-color: #f6f8fa;
        }
        
        .markdown-body blockquote {
            color: #6a737d;
            border-left-color: #dfe2e5;
        }
        
        .markdown-body th,
        .markdown-body td {
            border-color: #dfe2e5;
        }
        
        .markdown-body th {
            background-color: #f6f8fa;
        }
        
        .markdown-body hr {
            background-color: #e1e4e8;
        }
        '''
        
        # 暗色主题
        dark_theme = '''
        body {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        .markdown-body h1,
        .markdown-body h2 {
            border-bottom-color: #21262d;
        }
        
        .markdown-body a {
            color: #58a6ff;
        }
        
        .markdown-body code {
            background-color: rgba(110, 118, 129, 0.4);
        }
        
        .markdown-body pre {
            background-color: #161b22;
        }
        
        .markdown-body blockquote {
            color: #8b949e;
            border-left-color: #3b434b;
        }
        
        .markdown-body th,
        .markdown-body td {
            border-color: #30363d;
        }
        
        .markdown-body th {
            background-color: #161b22;
        }
        
        .markdown-body hr {
            background-color: #30363d;
        }
        '''
        
        # 根据主题选择样式
        theme_css = dark_theme if theme == 'dark' else light_theme
        
        return base_css + theme_css
    
    def extract_plain_text(self, markdown_text: str) -> str:
        """
        从Markdown文本中提取纯文本（去除所有标记）
        
        Args:
            markdown_text: Markdown格式的文本
        
        Returns:
            str: 纯文本内容
        """
        if not markdown_text:
            return ''
        
        text = markdown_text
        
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # 移除行内代码
        text = re.sub(r'`[^`]*`', '', text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除Markdown标题标记
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
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
        
        # 移除水平线
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
        
        # 规范化空白字符
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        
        return text
