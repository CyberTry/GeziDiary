"""
Markdown编辑器组件
==================
提供Markdown编辑和实时预览功能的自定义组件。
包含编辑区和预览区两个面板，支持同步滚动。
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, 
    QSplitter, QFrame, QLabel, QToolBar, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

from ..core.markdown_processor import MarkdownProcessor


class MarkdownEditor(QWidget):
    """
    Markdown编辑器组件
    
    提供双栏布局：左侧编辑区，右侧预览区。
    支持实时预览、工具栏快捷操作等功能。
    
    Signals:
        content_changed: 当内容发生变化时发射
        save_requested: 当用户请求保存时发射
    """
    
    # 定义信号
    content_changed = pyqtSignal()  # 内容变化信号
    save_requested = pyqtSignal()   # 保存请求信号
    
    def __init__(self, parent=None):
        """
        初始化Markdown编辑器
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        # 创建Markdown处理器
        self.md_processor = MarkdownProcessor()
        
        # 当前编辑的文件路径（用于标题显示等）
        self.current_file = None
        
        # 标记是否有未保存的更改
        self._is_modified = False
        
        # 初始化UI
        self._init_ui()
        
        # 设置自动预览定时器（延迟预览，避免频繁刷新）
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)  # 单次触发
        self.preview_timer.timeout.connect(self._update_preview)
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建工具栏
        self._create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 创建分割器（用于调整编辑区和预览区宽度）
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建编辑区
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("在此输入Markdown内容...")
        self.editor.textChanged.connect(self._on_text_changed)
        
        # 设置编辑器字体
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        
        # 创建预览区
        self.preview = QWebEngineView()
        self.preview.setHtml(self._get_empty_preview())
        
        # 将编辑区和预览区添加到分割器
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        
        # 设置分割比例（默认各占50%）
        self.splitter.setSizes([500, 500])
        
        # 将分割器添加到布局
        layout.addWidget(self.splitter)
        
        # 创建状态栏
        self._create_statusbar()
        layout.addWidget(self.statusbar)
    
    def _create_toolbar(self):
        """
        创建工具栏
        
        提供常用的Markdown格式快捷按钮。
        """
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)
        
        # 标题按钮
        btn_h1 = QPushButton("H1")
        btn_h1.setFixedSize(40, 28)
        btn_h1.setToolTip("一级标题 (# )")
        btn_h1.clicked.connect(lambda: self._insert_prefix("# "))
        
        btn_h2 = QPushButton("H2")
        btn_h2.setFixedSize(40, 28)
        btn_h2.setToolTip("二级标题 (## )")
        btn_h2.clicked.connect(lambda: self._insert_prefix("## "))
        
        btn_h3 = QPushButton("H3")
        btn_h3.setFixedSize(40, 28)
        btn_h3.setToolTip("三级标题 (### )")
        btn_h3.clicked.connect(lambda: self._insert_prefix("### "))
        
        # 格式按钮
        btn_bold = QPushButton("B")
        btn_bold.setFixedSize(32, 28)
        btn_bold.setToolTip("粗体 (**text**)")
        btn_bold.setStyleSheet("font-weight: bold;")
        btn_bold.clicked.connect(lambda: self._wrap_selection("**", "**"))
        
        btn_italic = QPushButton("I")
        btn_italic.setFixedSize(32, 28)
        btn_italic.setToolTip("斜体 (*text*)")
        btn_italic.setStyleSheet("font-style: italic;")
        btn_italic.clicked.connect(lambda: self._wrap_selection("*", "*"))
        
        btn_code = QPushButton("</>")
        btn_code.setFixedSize(40, 28)
        btn_code.setToolTip("行内代码 (`code`)")
        btn_code.clicked.connect(lambda: self._wrap_selection("`", "`"))
        
        btn_link = QPushButton("🔗")
        btn_link.setFixedSize(32, 28)
        btn_link.setToolTip("链接 ([text](url))")
        btn_link.clicked.connect(self._insert_link)
        
        btn_list = QPushButton("☰")
        btn_list.setFixedSize(32, 28)
        btn_list.setToolTip("无序列表 (- )")
        btn_list.clicked.connect(lambda: self._insert_prefix("- "))
        
        btn_quote = QPushButton('"')
        btn_quote.setFixedSize(32, 28)
        btn_quote.setToolTip("引用 (> )")
        btn_quote.clicked.connect(lambda: self._insert_prefix("> "))
        
        # 添加按钮到工具栏
        toolbar_layout.addWidget(btn_h1)
        toolbar_layout.addWidget(btn_h2)
        toolbar_layout.addWidget(btn_h3)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(btn_bold)
        toolbar_layout.addWidget(btn_italic)
        toolbar_layout.addWidget(btn_code)
        toolbar_layout.addWidget(btn_link)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(btn_list)
        toolbar_layout.addWidget(btn_quote)
        toolbar_layout.addStretch()
        
        # 保存按钮
        btn_save = QPushButton("💾 保存")
        btn_save.setFixedSize(80, 28)
        btn_save.clicked.connect(self.save_requested.emit)
        toolbar_layout.addWidget(btn_save)
    
    def _create_statusbar(self):
        """
        创建状态栏
        
        显示字数统计等信息。
        """
        self.statusbar = QFrame()
        self.statusbar.setFixedHeight(30)
        status_layout = QHBoxLayout(self.statusbar)
        status_layout.setContentsMargins(10, 2, 10, 2)
        
        # 字数统计标签
        self.word_count_label = QLabel("字数: 0")
        status_layout.addWidget(self.word_count_label)
        
        status_layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)
    
    def _get_empty_preview(self) -> str:
        """
        获取空预览页面的HTML
        
        Returns:
            str: 空预览页面的HTML
        """
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    color: #999;
                }
            </style>
        </head>
        <body>
            <p>预览区域</p>
        </body>
        </html>
        """
    
    def _on_text_changed(self):
        """
        文本变化时的处理函数
        """
        # 标记为已修改
        self._is_modified = True
        
        # 更新字数统计
        self._update_word_count()
        
        # 发射内容变化信号
        self.content_changed.emit()
        
        # 延迟更新预览（避免频繁刷新）
        self.preview_timer.stop()
        self.preview_timer.start(500)  # 500ms后更新
    
    def _update_preview(self):
        """
        更新预览区域
        """
        text = self.editor.toPlainText()
        html = self.md_processor.to_html(text)
        self.preview.setHtml(html)
    
    def _update_word_count(self):
        """
        更新字数统计
        """
        text = self.editor.toPlainText()
        plain_text = self.md_processor.get_plain_text(text)
        
        # 统计中文字符
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', plain_text))
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', plain_text))
        total = chinese_chars + english_words
        
        self.word_count_label.setText(f"字数: {total}")
    
    def _insert_prefix(self, prefix: str):
        """
        在当前行插入前缀
        
        Args:
            prefix: 要插入的前缀字符串
        """
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.StartOfLine)
        cursor.insertText(prefix)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
    
    def _wrap_selection(self, prefix: str, suffix: str):
        """
        用前缀和后缀包裹选中的文本
        
        Args:
            prefix: 前缀字符串
            suffix: 后缀字符串
        """
        cursor = self.editor.textCursor()
        
        if cursor.hasSelection():
            # 有选中文本，包裹它
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        else:
            # 无选中文本，插入占位符并选中
            cursor.insertText(f"{prefix}文本{suffix}")
            # 选中"文本"两个字
            cursor.movePosition(cursor.MoveOperation.PreviousCharacter, cursor.MoveMode.MoveAnchor, 2)
            cursor.movePosition(cursor.MoveOperation.PreviousCharacter, cursor.MoveMode.KeepAnchor, 2)
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
    
    def _insert_link(self):
        """
        插入链接
        """
        cursor = self.editor.textCursor()
        
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"[{selected_text}](url)")
        else:
            cursor.insertText("[链接文本](url)")
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
    
    def get_content(self) -> str:
        """
        获取编辑器内容
        
        Returns:
            str: Markdown文本内容
        """
        return self.editor.toPlainText()
    
    def set_content(self, content: str):
        """
        设置编辑器内容
        
        Args:
            content: Markdown文本内容
        """
        self.editor.setPlainText(content)
        self._update_preview()
        self._update_word_count()
        self._is_modified = False
    
    def is_modified(self) -> bool:
        """
        检查是否有未保存的更改
        
        Returns:
            bool: 是否有未保存的更改
        """
        return self._is_modified
    
    def set_modified(self, modified: bool):
        """
        设置修改状态
        
        Args:
            modified: 修改状态
        """
        self._is_modified = modified
        if modified:
            self.status_label.setText("已修改")
        else:
            self.status_label.setText("已保存")
    
    def clear(self):
        """
        清空编辑器内容
        """
        self.editor.clear()
        self.preview.setHtml(self._get_empty_preview())
        self._is_modified = False
        self.word_count_label.setText("字数: 0")
