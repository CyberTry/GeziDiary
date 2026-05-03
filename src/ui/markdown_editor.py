# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
Markdown编辑器模块

功能：提供Markdown编辑和实时预览功能
"""

from typing import Optional

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QPlainTextEdit, QLabel, QLineEdit,
    QPushButton, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QFont, QTextCharFormat, QColor, QSyntaxHighlighter,
    QTextDocument, QKeyEvent, QAction
)

# ============================================
# 本地模块导入
# ============================================
from core.markdown_processor import MarkdownProcessor


class MarkdownHighlighter(QSyntaxHighlighter):
    """
    Markdown语法高亮器
    
    为Markdown编辑器提供语法高亮功能
    
    Attributes:
        highlighting_rules (list): 高亮规则列表
    """
    
    def __init__(self, parent=None):
        """
        初始化语法高亮器
        
        Args:
            parent: 父文档
        """
        super().__init__(parent)
        
        # ============================================
        # 定义高亮规则
        # ============================================
        self.highlighting_rules = []
        
        # 标题样式（# ## ### 等）
        header_format = QTextCharFormat()
        header_format.setForeground(QColor('#22863a'))
        header_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'^#{1,6}\s.*$', header_format))
        
        # 粗体 **text** 或 __text__
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'\*\*[^*]+\*\*', bold_format))
        self.highlighting_rules.append((r'__[^_]+__', bold_format))
        
        # 斜体 *text* 或 _text_
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*[^*]+\*', italic_format))
        self.highlighting_rules.append((r'_[^_]+_', italic_format))
        
        # 行内代码 `code`
        code_format = QTextCharFormat()
        code_format.setForeground(QColor('#032f62'))
        code_format.setBackground(QColor('#f6f8fa'))
        code_format.setFontFamily('Consolas, monospace')
        self.highlighting_rules.append((r'`[^`]+`', code_format))
        
        # 链接 [text](url)
        link_format = QTextCharFormat()
        link_format.setForeground(QColor('#0366d6'))
        self.highlighting_rules.append((r'\[([^\]]+)\]\([^)]+\)', link_format))
        
        # 图片 ![alt](url)
        image_format = QTextCharFormat()
        image_format.setForeground(QColor('#6f42c1'))
        self.highlighting_rules.append((r'!\[([^\]]*)\]\([^)]+\)', image_format))
        
        # 引用 > text
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor('#6a737d'))
        self.highlighting_rules.append((r'^>\s.*$', quote_format))
        
        # 列表项 - * + 1.
        list_format = QTextCharFormat()
        list_format.setForeground(QColor('#22863a'))
        self.highlighting_rules.append((r'^[\*\-\+]\s', list_format))
        self.highlighting_rules.append((r'^\d+\.\s', list_format))
        
        # 代码块 ```
        code_block_format = QTextCharFormat()
        code_block_format.setForeground(QColor('#032f62'))
        code_block_format.setBackground(QColor('#f6f8fa'))
        self.highlighting_rules.append((r'^```[\s\S]*?```$', code_block_format))
    
    def highlightBlock(self, text: str):
        """
        高亮文本块
        
        Args:
            text: 要处理的文本行
        """
        import re
        
        # 应用每条高亮规则
        for pattern, format_obj in self.highlighting_rules:
            expression = re.compile(pattern, re.MULTILINE)
            for match in expression.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format_obj)


class MarkdownTextEdit(QPlainTextEdit):
    """
    Markdown文本编辑器
    
    支持语法高亮的纯文本编辑器
    
    Signals:
        content_changed: 内容变化时发射
        save_requested: 请求保存时发射（Ctrl+S）
    """
    
    content_changed = pyqtSignal()
    save_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化编辑器
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 设置编辑器属性
        # ============================================
        # 设置字体
        font = QFont('Consolas', 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 启用自动换行
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # 设置Tab宽度
        self.setTabStopDistance(40)
        
        # ============================================
        # 设置语法高亮
        # ============================================
        self.highlighter = MarkdownHighlighter(self.document())
        
        # ============================================
        # 连接信号
        # ============================================
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """
        处理文本变化
        """
        self.content_changed.emit()
    
    def keyPressEvent(self, event: QKeyEvent):
        """
        处理按键事件
        
        Args:
            event: 按键事件
        """
        # Ctrl+S 保存
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.save_requested.emit()
            return
        
        # Tab键插入空格
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText('    ')
            return
        
        # 处理其他按键
        super().keyPressEvent(event)
    
    def insert_markdown(self, markdown_text: str):
        """
        插入Markdown文本
        
        Args:
            markdown_text: Markdown文本
        """
        self.insertPlainText(markdown_text)


class MarkdownEditor(QWidget):
    """
    Markdown编辑器部件
    
    整合编辑器和预览功能
    
    Attributes:
        markdown_processor (MarkdownProcessor): Markdown处理器
        is_modified (bool): 内容是否被修改
    
    Signals:
        content_changed: 内容变化时发射
        save_requested: 请求保存时发射
    """
    
    content_changed = pyqtSignal()
    save_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化Markdown编辑器
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # ============================================
        # 初始化属性
        # ============================================
        self.markdown_processor = MarkdownProcessor()
        self._is_modified = False
        self._content = ''
        
        # ============================================
        # 设置UI
        # ============================================
        self._setup_ui()
        
        # ============================================
        # 设置预览更新定时器
        # ============================================
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)
    
    def _setup_ui(self):
        """
        设置UI布局
        """
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ============================================
        # 创建分割器（编辑 | 预览）
        # ============================================
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # ============================================
        # 编辑器区域
        # ============================================
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(10, 10, 10, 10)
        editor_layout.setSpacing(5)
        
        # 编辑器标签
        editor_label = QLabel('编辑')
        editor_label.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        editor_layout.addWidget(editor_label)
        
        # Markdown编辑器
        self.text_edit = MarkdownTextEdit()
        self.text_edit.content_changed.connect(self._on_content_changed)
        self.text_edit.save_requested.connect(self.save_requested.emit)
        editor_layout.addWidget(self.text_edit)
        
        self.splitter.addWidget(editor_container)
        
        # ============================================
        # 预览区域
        # ============================================
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        preview_layout.setSpacing(5)
        
        # 预览标签
        preview_label = QLabel('预览')
        preview_label.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        # 预览控件（使用QTextEdit显示HTML）
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont('Microsoft YaHei', 10))
        preview_layout.addWidget(self.preview)
        
        self.splitter.addWidget(preview_container)
        
        # ============================================
        # 设置分割比例
        # ============================================
        self.splitter.setSizes([500, 500])
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
    
    def _on_content_changed(self):
        """
        处理内容变化
        """
        # 标记为已修改
        self._is_modified = True
        
        # 发射内容变化信号
        self.content_changed.emit()
        
        # 延迟更新预览（避免频繁刷新）
        self.preview_timer.stop()
        self.preview_timer.start(500)  # 500ms后更新
    
    def _update_preview(self):
        """
        更新预览
        """
        # 获取编辑器内容
        markdown_text = self.text_edit.toPlainText()
        
        # 转换为HTML
        html = self.markdown_processor.to_html_with_style(markdown_text)
        
        # 更新预览
        self.preview.setHtml(html)
    
    def set_content(self, content: str):
        """
        设置编辑器内容
        
        Args:
            content: Markdown内容
        """
        # 保存内容
        self._content = content
        self._is_modified = False
        
        # 设置编辑器文本
        self.text_edit.setPlainText(content)
        
        # 更新预览
        self._update_preview()
    
    def get_content(self) -> str:
        """
        获取编辑器内容
        
        Returns:
            str: Markdown内容
        """
        return self.text_edit.toPlainText()
    
    def is_modified(self) -> bool:
        """
        检查内容是否被修改
        
        Returns:
            bool: 如果被修改返回True
        """
        return self._is_modified
    
    def set_modified(self, modified: bool):
        """
        设置修改状态
        
        Args:
            modified: 修改状态
        """
        self._is_modified = modified
    
    def undo(self):
        """
        撤销操作
        """
        self.text_edit.undo()
    
    def redo(self):
        """
        重做操作
        """
        self.text_edit.redo()
    
    def set_preview_visible(self, visible: bool):
        """
        设置预览区域可见性
        
        Args:
            visible: 是否可见
        """
        # 获取预览容器的索引（在splitter中的位置）
        index = 1  # 预览在右侧
        
        if visible:
            self.splitter.widget(index).show()
            # 恢复分割比例
            self.splitter.setSizes([500, 500])
        else:
            self.splitter.widget(index).hide()
    
    def show_find_dialog(self):
        """
        显示查找对话框
        """
        dialog = FindDialog(self.text_edit, self)
        dialog.exec()


class FindDialog(QDialog):
    """
    查找对话框
    
    提供文本查找功能
    """
    
    def __init__(self, text_edit: MarkdownTextEdit, parent=None):
        """
        初始化查找对话框
        
        Args:
            text_edit: 要查找的文本编辑器
            parent: 父部件
        """
        super().__init__(parent)
        
        self.text_edit = text_edit
        
        # 设置对话框属性
        self.setWindowTitle('查找')
        self.setFixedSize(300, 120)
        
        # 创建布局
        layout = QGridLayout(self)
        
        # 查找输入框
        layout.addWidget(QLabel('查找内容:'), 0, 0)
        self.find_input = QLineEdit()
        layout.addWidget(self.find_input, 0, 1)
        
        # 查找按钮
        find_btn = QPushButton('查找下一个')
        find_btn.clicked.connect(self.find_next)
        layout.addWidget(find_btn, 1, 1)
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, 2, 1)
    
    def find_next(self):
        """
        查找下一个匹配项
        """
        text = self.find_input.text()
        if text:
            # 使用QTextDocument查找
            document = self.text_edit.document()
            cursor = self.text_edit.textCursor()
            
            # 从当前位置开始查找
            found = document.find(text, cursor)
            
            if found.isNull():
                # 没找到，从头开始
                cursor.movePosition(cursor.MoveOperation.Start)
                found = document.find(text, cursor)
            
            if not found.isNull():
                # 选中找到的文本
                self.text_edit.setTextCursor(found)
