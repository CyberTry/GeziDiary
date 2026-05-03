# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
主窗口模块

功能：创建应用程序主窗口，采用底部导航栏切换页面设计
"""

from datetime import date, datetime
from typing import Optional

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame,
    QTextEdit, QPlainTextEdit, QMessageBox, QFileDialog,
    QToolBar, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont

# ============================================
# 本地模块导入
# ============================================
from core.config import ConfigManager
from core.diary_manager import DiaryManager, DiaryEntry
from core.markdown_processor import MarkdownProcessor

from ui.heatmap_calendar import HeatmapCalendar
from ui.markdown_editor import MarkdownEditor
from ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """
    应用程序主窗口类
    
    采用底部导航栏设计，包含三个页面：
    - 编辑页面：Markdown编辑和预览
    - 日历页面：热力图日历
    - 设置页面：应用设置
    
    Attributes:
        config (ConfigManager): 配置管理器
        diary_manager (DiaryManager): 日记管理器
        current_entry (DiaryEntry): 当前编辑的日记条目
    """
    
    def __init__(self, config: ConfigManager):
        """
        初始化主窗口
        
        Args:
            config: 配置管理器实例
        """
        super().__init__()
        
        # ============================================
        # 初始化核心组件
        # ============================================
        self.config = config
        self.diary_manager = DiaryManager(config.get_storage_path())
        self.markdown_processor = MarkdownProcessor()
        self.current_entry: Optional[DiaryEntry] = None
        
        # ============================================
        # 初始化UI
        # ============================================
        self._setup_window()
        self._create_pages()
        self._create_bottom_navigation()
        
        # ============================================
        # 加载初始数据
        # ============================================
        self.load_entry(date.today())
    
    def _setup_window(self):
        """
        设置窗口基本属性
        """
        self.setWindowTitle('鸽子日记 - GeziDiary')
        
        # 设置窗口尺寸
        width = self.config.get('window_width', 1200)
        height = self.config.get('window_height', 800)
        self.resize(width, height)
        
        # 窗口居中
        self._center_window()
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def _center_window(self):
        """
        将窗口居中显示
        """
        screen = self.screen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def _create_pages(self):
        """
        创建三个主要页面
        """
        # 创建堆叠窗口部件用于页面切换
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # ============================================
        # 页面1：编辑页面
        # ============================================
        self.edit_page = self._create_edit_page()
        self.stacked_widget.addWidget(self.edit_page)
        
        # ============================================
        # 页面2：日历页面
        # ============================================
        self.calendar_page = self._create_calendar_page()
        self.stacked_widget.addWidget(self.calendar_page)
        
        # ============================================
        # 页面3：设置页面
        # ============================================
        self.settings_page = self._create_settings_page()
        self.stacked_widget.addWidget(self.settings_page)
    
    def _create_edit_page(self) -> QWidget:
        """
        创建编辑页面
        
        包含：
        - 顶部Markdown工具栏
        - 左侧代码编辑区
        - 右侧预览区
        
        Returns:
            QWidget: 编辑页面
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ============================================
        # 顶部工具栏
        # ============================================
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
                spacing: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QToolButton:hover {
                background-color: #f0f0f0;
                border-color: #d0d0d0;
            }
        """)
        
        # 粗体按钮
        bold_btn = QPushButton('𝐁 粗体')
        bold_btn.setToolTip('Ctrl+B')
        bold_btn.clicked.connect(lambda: self._insert_markdown('**', '**'))
        toolbar.addWidget(bold_btn)
        
        # 斜体按钮
        italic_btn = QPushButton('𝐼 斜体')
        italic_btn.setToolTip('Ctrl+I')
        italic_btn.clicked.connect(lambda: self._insert_markdown('*', '*'))
        toolbar.addWidget(italic_btn)
        
        # 标题按钮
        h1_btn = QPushButton('H1')
        h1_btn.clicked.connect(lambda: self._insert_markdown('# ', ''))
        toolbar.addWidget(h1_btn)
        
        h2_btn = QPushButton('H2')
        h2_btn.clicked.connect(lambda: self._insert_markdown('## ', ''))
        toolbar.addWidget(h2_btn)
        
        h3_btn = QPushButton('H3')
        h3_btn.clicked.connect(lambda: self._insert_markdown('### ', ''))
        toolbar.addWidget(h3_btn)
        
        toolbar.addSeparator()
        
        # 代码块按钮
        code_btn = QPushButton('❖ 代码')
        code_btn.clicked.connect(lambda: self._insert_markdown('```\n', '\n```'))
        toolbar.addWidget(code_btn)
        
        # 引用按钮
        quote_btn = QPushButton('❝ 引用')
        quote_btn.clicked.connect(lambda: self._insert_markdown('> ', ''))
        toolbar.addWidget(quote_btn)
        
        # 列表按钮
        ul_btn = QPushButton('☰ 列表')
        ul_btn.clicked.connect(lambda: self._insert_markdown('- ', ''))
        toolbar.addWidget(ul_btn)
        
        toolbar.addSeparator()
        
        # 链接按钮
        link_btn = QPushButton('🔗 链接')
        link_btn.clicked.connect(lambda: self._insert_markdown('[', '](url)'))
        toolbar.addWidget(link_btn)
        
        # 图片按钮
        img_btn = QPushButton('🖼 图片')
        img_btn.clicked.connect(lambda: self._insert_markdown('![', '](image.png)'))
        toolbar.addWidget(img_btn)
        
        toolbar.addSeparator()
        
        # 分隔线按钮
        hr_btn = QPushButton('— 分隔线')
        hr_btn.clicked.connect(lambda: self._insert_markdown('\n---\n', ''))
        toolbar.addWidget(hr_btn)
        
        layout.addWidget(toolbar)
        
        # ============================================
        # 编辑和预览分割区
        # ============================================
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧编辑器
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(10, 10, 5, 10)
        
        editor_label = QLabel('📝 Markdown 编辑')
        editor_label.setFont(QFont('Microsoft YaHei', 11, QFont.Weight.Bold))
        editor_layout.addWidget(editor_label)
        
        self.code_editor = QPlainTextEdit()
        self.code_editor.setFont(QFont('Consolas', 12))
        self.code_editor.setPlaceholderText('在这里开始写日记...\n\n支持 Markdown 语法')
        self.code_editor.textChanged.connect(self._on_content_changed)
        editor_layout.addWidget(self.code_editor)
        
        splitter.addWidget(editor_container)
        
        # 右侧预览
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(5, 10, 10, 10)
        
        preview_label = QLabel('👁 实时预览')
        preview_label.setFont(QFont('Microsoft YaHei', 11, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont('Microsoft YaHei', 11))
        preview_layout.addWidget(self.preview)
        
        splitter.addWidget(preview_container)
        
        # 设置分割比例
        splitter.setSizes([600, 600])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter, 1)
        
        # 底部状态栏
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.date_label = QLabel()
        self.date_label.setFont(QFont('Microsoft YaHei', 10))
        status_layout.addWidget(self.date_label)
        
        status_layout.addStretch()
        
        self.char_count_label = QLabel('0 字符')
        self.char_count_label.setFont(QFont('Microsoft YaHei', 10))
        status_layout.addWidget(self.char_count_label)
        
        layout.addLayout(status_layout)
        
        return page
    
    def _create_calendar_page(self) -> QWidget:
        """
        创建日历页面
        
        包含热力图日历，点击日期切换到该日日记
        
        Returns:
            QWidget: 日历页面
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel('📅 日记日历')
        title.setFont(QFont('Microsoft YaHei', 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明文字
        hint = QLabel('点击日期查看或编辑当天的日记')
        hint.setFont(QFont('Microsoft YaHei', 10))
        hint.setStyleSheet('color: #666;')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        
        # 热力图日历
        self.heatmap = HeatmapCalendar()
        self.heatmap.date_selected.connect(self._on_date_selected_from_calendar)
        layout.addWidget(self.heatmap, 1)
        
        # 刷新按钮
        refresh_btn = QPushButton('🔄 刷新数据')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_btn.clicked.connect(self._refresh_heatmap)
        layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return page
    
    def _create_settings_page(self) -> QWidget:
        """
        创建设置页面
        
        Returns:
            QWidget: 设置页面
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel('⚙️ 设置')
        title.setFont(QFont('Microsoft YaHei', 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 设置内容容器
        settings_container = QWidget()
        settings_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(20)
        
        # 存储路径设置
        path_group = self._create_setting_group('存储设置')
        path_layout = QHBoxLayout()
        
        path_label = QLabel('日记存储路径:')
        path_label.setFont(QFont('Microsoft YaHei', 11))
        path_layout.addWidget(path_label)
        
        self.path_display = QLabel()
        self.path_display.setFont(QFont('Consolas', 10))
        self.path_display.setStyleSheet('color: #666; padding: 5px; background: #f5f5f5; border-radius: 4px;')
        path_layout.addWidget(self.path_display, 1)
        
        change_path_btn = QPushButton('更改')
        change_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        change_path_btn.clicked.connect(self._change_storage_path)
        path_layout.addWidget(change_path_btn)
        
        path_group.layout().addLayout(path_layout)
        settings_layout.addWidget(path_group)
        
        # 编辑器设置
        editor_group = self._create_setting_group('编辑器设置')
        editor_layout = QFormLayout()
        
        # 字体大小
        font_layout = QHBoxLayout()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.config.get('editor_font_size', 12))
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        font_layout.addWidget(self.font_size_spin)
        font_layout.addStretch()
        editor_layout.addRow('编辑器字体大小:', font_layout)
        
        # 自动保存
        auto_save_layout = QHBoxLayout()
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(0, 300)
        self.auto_save_spin.setValue(self.config.get('auto_save_interval', 30))
        self.auto_save_spin.setSuffix(' 秒')
        self.auto_save_spin.setSpecialValueText('禁用')
        auto_save_layout.addWidget(self.auto_save_spin)
        auto_save_layout.addStretch()
        editor_layout.addRow('自动保存间隔:', auto_save_layout)
        
        editor_group.layout().addLayout(editor_layout)
        settings_layout.addWidget(editor_group)
        
        # 关于信息
        about_group = self._create_setting_group('关于')
        about_layout = QVBoxLayout()
        
        app_name = QLabel('鸽子日记 GeziDiary')
        app_name.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        about_layout.addWidget(app_name)
        
        version = QLabel('版本: 1.0.0')
        version.setStyleSheet('color: #666;')
        about_layout.addWidget(version)
        
        desc = QLabel('一款简洁优雅的Markdown日记应用')
        desc.setStyleSheet('color: #666;')
        desc.setWordWrap(True)
        about_layout.addWidget(desc)
        
        about_group.layout().addLayout(about_layout)
        settings_layout.addWidget(about_group)
        
        settings_layout.addStretch()
        settings_layout.addWidget(self._create_save_settings_button())
        
        layout.addWidget(settings_container, 1)
        
        return page
    
    def _create_setting_group(self, title: str) -> QFrame:
        """
        创建设置分组框
        
        Args:
            title: 分组标题
        
        Returns:
            QFrame: 分组框
        """
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        return group
    
    def _create_save_settings_button(self) -> QPushButton:
        """
        创建保存设置按钮
        
        Returns:
            QPushButton: 保存按钮
        """
        btn = QPushButton('💾 保存设置')
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn.clicked.connect(self._save_settings)
        return btn
    
    def _create_bottom_navigation(self):
        """
        创建底部导航栏
        """
        # 创建底部导航容器
        nav_container = QWidget()
        nav_container.setFixedHeight(60)
        nav_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-top: 1px solid #e0e0e0;
            }
        """)
        
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(20, 5, 20, 5)
        nav_layout.setSpacing(20)
        
        # 编辑按钮
        self.edit_btn = self._create_nav_button('📝', '编辑', 0)
        nav_layout.addWidget(self.edit_btn)
        
        # 日历按钮
        self.calendar_btn = self._create_nav_button('📅', '日历', 1)
        nav_layout.addWidget(self.calendar_btn)
        
        nav_layout.addStretch()
        
        # 设置按钮
        self.settings_btn = self._create_nav_button('⚙️', '设置', 2)
        nav_layout.addWidget(self.settings_btn)
        
        # 将导航栏添加到主窗口
        self.setMenuWidget(nav_container)
        
        # 默认选中编辑页面
        self._switch_page(0)
    
    def _create_nav_button(self, icon: str, text: str, page_index: int) -> QPushButton:
        """
        创建导航按钮
        
        Args:
            icon: 图标
            text: 文字
            page_index: 页面索引
        
        Returns:
            QPushButton: 导航按钮
        """
        btn = QPushButton(f'{icon} {text}')
        btn.setCheckable(True)
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 5px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #333;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
                border-color: #1976D2;
            }
        """)
        btn.clicked.connect(lambda: self._switch_page(page_index))
        return btn
    
    def _switch_page(self, index: int):
        """
        切换页面
        
        Args:
            index: 页面索引
        """
        # 切换堆叠窗口
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮状态
        self.edit_btn.setChecked(index == 0)
        self.calendar_btn.setChecked(index == 1)
        self.settings_btn.setChecked(index == 2)
        
        # 特殊处理
        if index == 1:  # 日历页面
            self._refresh_heatmap()
        elif index == 2:  # 设置页面
            self._load_settings()
    
    # ============================================
    # 编辑页面功能
    # ============================================
    
    def _insert_markdown(self, prefix: str, suffix: str):
        """
        插入Markdown标记
        
        Args:
            prefix: 前缀
            suffix: 后缀
        """
        cursor = self.code_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            # 有选中文本，包裹选中文本
            new_text = prefix + selected_text + suffix
            cursor.insertText(new_text)
        else:
            # 无选中文本，插入标记并将光标移到中间
            cursor.insertText(prefix + suffix)
            # 移动光标到中间
            pos = cursor.position() - len(suffix)
            cursor.setPosition(pos)
            self.code_editor.setTextCursor(cursor)
        
        self.code_editor.setFocus()
    
    def _on_content_changed(self):
        """
        处理内容变化
        """
        # 更新预览
        content = self.code_editor.toPlainText()
        html = self.markdown_processor.to_html_with_style(content)
        self.preview.setHtml(html)
        
        # 更新字符数
        self.char_count_label.setText(f'{len(content)} 字符')
    
    # ============================================
    # 日历页面功能
    # ============================================
    
    def _refresh_heatmap(self):
        """
        刷新热力图数据
        """
        current_year = date.today().year
        year_data = {}
        
        entries = self.diary_manager.get_entries_by_year(current_year)
        for entry in entries:
            year_data[entry.date] = entry.char_count
        
        self.heatmap.set_year_data(current_year, year_data)
    
    def _on_date_selected_from_calendar(self, selected_date: date):
        """
        处理从日历选择日期
        
        Args:
            selected_date: 选中的日期
        """
        # 保存当前日记
        self._save_current_entry()
        
        # 加载选中的日记
        self.load_entry(selected_date)
        
        # 切换到编辑页面
        self._switch_page(0)
    
    # ============================================
    # 设置页面功能
    # ============================================
    
    def _load_settings(self):
        """
        加载设置到UI
        """
        # 存储路径
        self.path_display.setText(self.config.get_storage_path())
        
        # 字体大小
        self.font_size_spin.setValue(self.config.get('editor_font_size', 12))
        
        # 自动保存
        self.auto_save_spin.setValue(self.config.get('auto_save_interval', 30))
    
    def _change_storage_path(self):
        """
        更改存储路径
        """
        new_path = QFileDialog.getExistingDirectory(
            self,
            '选择日记存储路径',
            self.config.get_storage_path()
        )
        
        if new_path:
            self.path_display.setText(new_path)
    
    def _on_font_size_changed(self, size: int):
        """
        处理字体大小变化
        
        Args:
            size: 字体大小
        """
        font = self.code_editor.font()
        font.setPointSize(size)
        self.code_editor.setFont(font)
    
    def _save_settings(self):
        """
        保存设置
        """
        # 存储路径
        new_path = self.path_display.text()
        if new_path and new_path != self.config.get_storage_path():
            self.config.set_storage_path(new_path)
            self.diary_manager = DiaryManager(new_path)
            self.load_entry(date.today())
        
        # 字体大小
        self.config.set('editor_font_size', self.font_size_spin.value())
        
        # 自动保存
        self.config.set('auto_save_interval', self.auto_save_spin.value())
        
        # 保存配置
        self.config.save()
        
        QMessageBox.information(self, '保存成功', '设置已保存！')
    
    # ============================================
    # 日记管理功能
    # ============================================
    
    def load_entry(self, entry_date: date):
        """
        加载指定日期的日记
        
        Args:
            entry_date: 要加载的日期
        """
        # 保存当前日记
        if self.current_entry:
            self._save_current_entry()
        
        # 加载日记
        self.current_entry = self.diary_manager.load_entry(entry_date)
        
        # 更新编辑器
        self.code_editor.setPlainText(self.current_entry.content)
        
        # 更新日期标签
        self.date_label.setText(self.current_entry.get_formatted_date())
        
        # 更新窗口标题
        self.setWindowTitle(f'鸽子日记 - {self.current_entry.get_formatted_date()}')
    
    def _save_current_entry(self):
        """
        保存当前日记
        """
        if not self.current_entry:
            return
        
        # 获取内容
        content = self.code_editor.toPlainText()
        self.current_entry.update_content(content)
        
        # 保存
        if not self.current_entry.is_empty():
            self.diary_manager.save_entry(self.current_entry)
    
    # ============================================
    # 窗口事件
    # ============================================
    
    def closeEvent(self, event):
        """
        处理窗口关闭事件
        """
        # 保存当前日记
        self._save_current_entry()
        
        # 保存窗口设置
        self.config.set('window_width', self.width())
        self.config.set('window_height', self.height())
        self.config.set('window_x', self.x())
        self.config.set('window_y', self.y())
        self.config.save()
        
        event.accept()


# 导入缺失的模块
from PyQt6.QtWidgets import QFormLayout, QSpinBox
