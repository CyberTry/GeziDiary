"""
Markdown处理模块
================
负责Markdown文本的解析和HTML渲染。
使用Python的markdown库进行解析，并添加了一些扩展以支持更多功能。
"""

import markdown
import re


class MarkdownProcessor:
    """
    Markdown处理器类
    
    负责将Markdown文本转换为HTML，支持以下扩展：
    - 代码高亮
    - 表格
    - 任务列表
    - 自动链接
    - 删除线
    """
    
    def __init__(self):
        """
        初始化Markdown处理器
        
        配置Markdown解析器的扩展和选项。
        """
        # 配置Markdown扩展
        self.extensions = [
            # 代码块扩展，支持```代码块```
            'fenced_code',
            # 表格扩展
            'tables',
            # 自动检测URL并转换为链接
            'autolink',
            # 删除线支持 ~~删除线~~
            'sane_lists',
            # 任务列表支持 - [ ] 和 - [x]
            'toc',  # 目录生成
        ]
        
        # 创建Markdown实例
        self.md = markdown.Markdown(
            extensions=self.extensions,
            extension_configs={
                'toc': {
                    'permalink': True,  # 为标题添加锚点链接
                }
            }
        )
    
    def to_html(self, text: str) -> str:
        """
        将Markdown文本转换为HTML
        
        Args:
            text: Markdown格式的文本
            
        Returns:
            str: 转换后的HTML文本
        """
        if not text:
            return ""
        
        # 重置Markdown实例（清除之前的状态）
        self.md.reset()
        
        # 转换Markdown为HTML
        html = self.md.convert(text)
        
        # 包装在完整的HTML文档中，添加样式
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                /* 基础样式 */
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #24292e;
                    padding: 20px;
                    max-width: 100%;
                    margin: 0;
                }}
                
                /* 标题样式 */
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                    color: #24292e;
                }}
                h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
                h3 {{ font-size: 1.25em; }}
                h4 {{ font-size: 1em; }}
                
                /* 段落和文本样式 */
                p {{
                    margin-top: 0;
                    margin-bottom: 16px;
                }}
                
                /* 链接样式 */
                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                
                /* 代码样式 */
                code {{
                    background-color: rgba(27,31,35,.05);
                    border-radius: 3px;
                    font-size: 85%;
                    margin: 0;
                    padding: .2em .4em;
                    font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                }}
                
                pre {{
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    font-size: 85%;
                    line-height: 1.45;
                    overflow: auto;
                    padding: 16px;
                }}
                
                pre code {{
                    background-color: transparent;
                    border: 0;
                    display: inline;
                    line-height: inherit;
                    margin: 0;
                    overflow: visible;
                    padding: 0;
                    word-wrap: normal;
                }}
                
                /* 列表样式 */
                ul, ol {{
                    margin-top: 0;
                    margin-bottom: 16px;
                    padding-left: 2em;
                }}
                
                li + li {{
                    margin-top: .25em;
                }}
                
                /* 任务列表样式 */
                ul.contains-task-list {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                
                .task-list-item {{
                    display: flex;
                    align-items: flex-start;
                }}
                
                .task-list-item-checkbox {{
                    margin-right: 8px;
                    margin-top: 5px;
                }}
                
                /* 表格样式 */
                table {{
                    border-collapse: collapse;
                    border-spacing: 0;
                    display: block;
                    overflow: auto;
                    width: 100%;
                    margin-bottom: 16px;
                }}
                
                table th {{
                    font-weight: 600;
                    background-color: #f6f8fa;
                }}
                
                table th, table td {{
                    border: 1px solid #dfe2e5;
                    padding: 6px 13px;
                }}
                
                table tr:nth-child(2n) {{
                    background-color: #f6f8fa;
                }}
                
                /* 引用块样式 */
                blockquote {{
                    border-left: .25em solid #dfe2e5;
                    color: #6a737d;
                    padding: 0 1em;
                    margin: 0 0 16px 0;
                }}
                
                blockquote > :first-child {{
                    margin-top: 0;
                }}
                
                blockquote > :last-child {{
                    margin-bottom: 0;
                }}
                
                /* 水平分割线 */
                hr {{
                    background-color: #e1e4e8;
                    border: 0;
                    height: .25em;
                    margin: 24px 0;
                    padding: 0;
                }}
                
                /* 图片样式 */
                img {{
                    max-width: 100%;
                    box-sizing: border-box;
                    background-color: #fff;
                }}
                
                /* 删除线样式 */
                del {{
                    color: #6a737d;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return styled_html
    
    def get_plain_text(self, text: str) -> str:
        """
        从Markdown文本中提取纯文本（去除所有标记）
        
        用于字数统计等功能。
        
        Args:
            text: Markdown格式的文本
            
        Returns:
            str: 纯文本内容
        """
        if not text:
            return ""
        
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        # 移除行内代码
        text = re.sub(r'`[^`]*`', '', text)
        # 移除链接，保留文本 [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除图片 ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        # 移除标题标记 #
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        # 移除强调标记 * 和 _
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)
        # 移除删除线
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除列表标记
        text = re.sub(r'^[\s]*[-*+]\s', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s', '', text, flags=re.MULTILINE)
        # 移除任务列表标记
        text = re.sub(r'^[\s]*[-*]\s*\[[ x]\]\s', '', text, flags=re.MULTILINE)
        
        return text.strip()
