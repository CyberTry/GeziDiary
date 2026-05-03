# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
主窗口模块

功能：创建应用程序主窗口，整合所有UI组件
"""

from datetime import date, datetime
from typing import Optional

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QIcon

# ============================================
# 本地模块导入
# ============================================
from core.config import ConfigManager
from core.diary_manager import DiaryManager, DiaryEntry
from core.markdown_processor import MarkdownProcessor

from ui.diary_list_widget import DiaryListWidget
from ui.heatmap_calendar import HeatmapCalendar
from ui.markdown_editor import MarkdownEditor
from ui.stats_widget import StatsWidget
from ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """
    应用程序主窗口类
    
    整合所有UI组件，提供完整的日记编辑和管理功能
    
    Attributes:
        config (ConfigManager): 配置管理器
        diary_manager (DiaryManager): 日记管理器
        markdown_processor (MarkdownProcessor): Markdown处理器
        current_entry (DiaryEntry): 当前编辑的日记条目
        auto_save_timer (QTimer): 自动保存定时器
    
    Signals:
        entry_saved: 日记保存时发射，传递日期参数
    """
    
    # 自定义信号：日记保存时发射
    entry_saved = pyqtSignal(date)
    
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
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        self._setup_auto_save()
        
        # ============================================
        # 加载初始数据
        # ============================================
        # 默认加载今天的日记
        self.load_entry(date.today())
        self._update_stats()
    
    def _setup_window(self):
        """
        设置窗口基本属性
        
        包括标题、尺寸、位置等
        """
        # 设置窗口标题
        self.setWindowTitle('鸽子日记 - GeziDiary')
        
        # 设置窗口尺寸
        width = self.config.get('window_width', 1200)
        height = self.config.get('window_height', 800)
        self.resize(width, height)
        
        # 设置窗口位置
        x = self.config.get('window_x', -1)
        y = self.config.get('window_y', -1)
        if x >= 0 and y >= 0:
            self.move(x, y)
        else:
            # 窗口居中显示
            self._center_window()
    
    def _center_window(self):
        """
        将窗口居中显示
        """
        # 获取屏幕几何信息
        screen = self.screen().geometry()
        # 获取窗口尺寸
        size = self.geometry()
        
        # 计算居中位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        
        self.move(x, y)
    
    def _create_menu_bar(self):
        """
        创建菜单栏
        
        包含文件、编辑、视图、设置等菜单
        """
        # 创建菜单栏
        menubar = self.menuBar()
        
        # ============================================
        # 文件菜单
        # ============================================
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建日记
        new_action = QAction('新建(&N)', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_entry)
        file_menu.addAction(new_action)
        
        # 保存
        save_action = QAction('保存(&S)', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&Q)', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ============================================
        # 编辑菜单
        # ============================================
        edit_menu = menubar.addMenu('编辑(&E)')
        
        # 撤销
        undo_action = QAction('撤销(&U)', self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(undo_action)
        
        # 重做
        redo_action = QAction('重做(&R)', self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # 查找
        find_action = QAction('查找(&F)', self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._on_find)
        edit_menu.addAction(find_action)
        
        # ============================================
        # 视图菜单
        # ============================================
        view_menu = menubar.addMenu('视图(&V)')
        
        # 切换预览
        self.preview_action = QAction('显示预览(&P)', self)
        self.preview_action.setCheckable(True)
        self.preview_action.setChecked(True)
        self.preview_action.triggered.connect(self._on_toggle_preview)
        view_menu.addAction(self.preview_action)
        
        # ============================================
        # 设置菜单
        # ============================================
        settings_menu = menubar.addMenu('设置(&S)')
        
        # 首选项
        prefs_action = QAction('首选项(&P)...', self)
        prefs_action.triggered.connect(self._on_settings)
        settings_menu.addAction(prefs_action)
    
    def _create_central_widget(self):
        """
        创建中央部件
        
        整合左侧边栏（日历、列表）和右侧编辑区
        """
        # ============================================
        # 创建主分割器
        # ============================================
        # 主分割器：左侧边栏 | 右侧编辑区
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # ============================================
        # 创建左侧边栏
        # ============================================
        self.sidebar = self._create_sidebar()
        self.main_splitter.addWidget(self.sidebar)
        
        # ============================================
        # 创建右侧编辑区
        # ============================================
        self.editor_widget = self._create_editor_widget()
        self.main_splitter.addWidget(self.editor_widget)
        
        # ============================================
        # 设置分割比例
        # ============================================
        sidebar_width = self.config.get('sidebar_width', 280)
        total_width = self.width()
        self.main_splitter.setSizes([sidebar_width, total_width - sidebar_width])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
    
    def _create_sidebar(self) -> QWidget:
        """
        创建左侧边栏
        
        包含热力图日历、日记列表和统计信息
        
        Returns:
            QWidget: 侧边栏部件
        """
        # 创建侧边栏容器
        sidebar = QWidget()
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(400)
        
        # 布局
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # ============================================
        # 热力图日历
        # ============================================
        self.heatmap = HeatmapCalendar()
        # 连接日期选择信号
        self.heatmap.date_selected.connect(self._on_date_selected_from_heatmap)
        layout.addWidget(self.heatmap)
        
        # ============================================
        # 日记列表
        # ============================================
        self.diary_list = DiaryListWidget()
        # 连接日记选择信号
        self.diary_list.entry_selected.connect(self._on_entry_selected_from_list)
        layout.addWidget(self.diary_list, 1)  # 占据剩余空间
        
        # ============================================
        # 统计信息
        # ============================================
        self.stats_widget = StatsWidget()
        layout.addWidget(self.stats_widget)
        
        return sidebar
    
    def _create_editor_widget(self) -> QWidget:
        """
        创建右侧编辑区
        
        包含Markdown编辑器和预览
        
        Returns:
            QWidget: 编辑区部件
        """
        # 创建编辑区容器
        widget = QWidget()
        
        # 布局
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ============================================
        # Markdown编辑器
        # ============================================
        self.editor = MarkdownEditor()
        
        # 连接编辑器信号
        self.editor.content_changed.connect(self._on_content_changed)
        self.editor.save_requested.connect(self._on_save)
        
        layout.addWidget(self.editor)
        
        return widget
    
    def _create_status_bar(self):
        """
        创建状态栏
        
        显示当前日期、字符数等信息
        """
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # 状态标签
        self.status_label = self.statusbar.showMessage('就绪')
        
        # 字符数标签
        self.char_count_label = self.statusbar.showMessage('字符数: 0')
    
    def _setup_auto_save(self):
        """
        设置自动保存
        
        根据配置定期自动保存日记
        """
        # 创建定时器
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self._auto_save)
        
        # 获取自动保存间隔（秒）
        interval = self.config.get('auto_save_interval', 30)
        
        # 如果间隔大于0，启动定时器
        if interval > 0:
            self.auto_save_timer.start(interval * 1000)  # 转换为毫秒
    
    # ============================================
    # 数据加载和保存方法
    # ============================================
    
    def load_entry(self, entry_date: date):
        """
        加载指定日期的日记
        
        Args:
            entry_date: 要加载的日期
        """
        # 从管理器加载日记
        self.current_entry = self.diary_manager.load_entry(entry_date)
        
        # 更新编辑器内容
        self.editor.set_content(self.current_entry.content)
        
        # 更新窗口标题
        self._update_window_title()
        
        # 更新状态栏
        self._update_status_bar()
        
        # 更新热力图选中状态
        self.heatmap.set_selected_date(entry_date)
        
        # 更新日记列表选中状态
        self.diary_list.set_selected_date(entry_date)
    
    def save_current_entry(self) -> bool:
        """
        保存当前日记
        
        Returns:
            bool: 保存成功返回True
        """
        if not self.current_entry:
            return False
        
        # 获取编辑器内容
        content = self.editor.get_content()
        
        # 更新日记内容
        self.current_entry.update_content(content)
        
        # 保存到文件
        success = self.diary_manager.save_entry(self.current_entry)
        
        if success:
            # 发射保存信号
            self.entry_saved.emit(self.current_entry.date)
            
            # 更新UI
            self._update_window_title()
            self._update_status_bar()
            
            # 更新热力图数据
            self._refresh_heatmap()
            
            # 更新日记列表
            self._refresh_diary_list()
            
            # 更新统计
            self._update_stats()
            
            # 显示保存成功提示
            self.statusbar.showMessage('已保存', 2000)
        
        return success
    
    def _auto_save(self):
        """
        自动保存当前日记
        
        仅在内容有变化时保存
        """
        if self.current_entry and self.editor.is_modified():
            self.save_current_entry()
    
    # ============================================
    # UI更新方法
    # ============================================
    
    def _update_window_title(self):
        """
        更新窗口标题
        
        显示当前日期和修改状态
        """
        if self.current_entry:
            date_str = self.current_entry.get_formatted_date()
            modified = '*' if self.editor.is_modified() else ''
            self.setWindowTitle(f'{modified}鸽子日记 - {date_str}')
    
    def _update_status_bar(self):
        """
        更新状态栏信息
        """
        if self.current_entry:
            # 更新字符数
            char_count = len(self.editor.get_content())
            self.statusbar.showMessage(f'字符数: {char_count}')
    
    def _refresh_heatmap(self):
        """
        刷新热力图数据
        """
        # 获取当前年份的所有日记数据
        current_year = date.today().year
        year_data = {}
        
        # 获取该年份的所有日记
        entries = self.diary_manager.get_entries_by_year(current_year)
        
        for entry in entries:
            # 使用字符数作为热力值
            year_data[entry.date] = entry.char_count
        
        # 更新热力图
        self.heatmap.set_year_data(current_year, year_data)
    
    def _refresh_diary_list(self):
        """
        刷新日记列表
        """
        # 获取当前月份的所有日记
        today = date.today()
        entries = self.diary_manager.get_entries_by_month(today.year, today.month)
        
        # 更新列表（只显示非空日记）
        non_empty_entries = [e for e in entries if not e.is_empty()]
        self.diary_list.set_entries(non_empty_entries)
    
    def _update_stats(self):
        """
        更新统计信息
        """
        stats = self.diary_manager.get_stats()
        self.stats_widget.update_stats(stats)
    
    # ============================================
    # 事件处理槽函数
    # ============================================
    
    def _on_date_selected_from_heatmap(self, selected_date: date):
        """
        处理从热力图选择日期
        
        Args:
            selected_date: 选中的日期
        """
        # 先保存当前日记
        if self.editor.is_modified():
            self.save_current_entry()
        
        # 加载选中的日记
        self.load_entry(selected_date)
    
    def _on_entry_selected_from_list(self, entry_date: date):
        """
        处理从列表选择日记
        
        Args:
            entry_date: 选中的日记日期
        """
        # 先保存当前日记
        if self.editor.is_modified():
            self.save_current_entry()
        
        # 加载选中的日记
        self.load_entry(entry_date)
    
    def _on_content_changed(self):
        """
        处理编辑器内容变化
        """
        # 更新窗口标题（显示修改标记）
        self._update_window_title()
        
        # 更新状态栏
        self._update_status_bar()
    
    def _on_new_entry(self):
        """
        处理新建日记
        """
        # 保存当前日记
        if self.editor.is_modified():
            self.save_current_entry()
        
        # 加载今天的日记
        self.load_entry(date.today())
    
    def _on_save(self):
        """
        处理保存操作
        """
        self.save_current_entry()
    
    def _on_undo(self):
        """
        处理撤销操作
        """
        self.editor.undo()
    
    def _on_redo(self):
        """
        处理重做操作
        """
        self.editor.redo()
    
    def _on_find(self):
        """
        处理查找操作
        """
        self.editor.show_find_dialog()
    
    def _on_toggle_preview(self, checked: bool):
        """
        处理预览显示切换
        
        Args:
            checked: 是否显示预览
        """
        self.editor.set_preview_visible(checked)
    
    def _on_settings(self):
        """
        处理设置操作
        """
        # 创建设置对话框
        dialog = SettingsDialog(self.config, self)
        
        # 显示对话框
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            # 应用新设置
            self._apply_settings()
    
    def _apply_settings(self):
        """
        应用设置更改
        """
        # 更新存储路径
        new_path = self.config.get_storage_path()
        if new_path != self.diary_manager.storage_path:
            self.diary_manager = DiaryManager(new_path)
            self.load_entry(date.today())
        
        # 更新自动保存间隔
        interval = self.config.get('auto_save_interval', 30)
        if interval > 0:
            self.auto_save_timer.start(interval * 1000)
        else:
            self.auto_save_timer.stop()
        
        # 刷新UI
        self._refresh_heatmap()
        self._refresh_diary_list()
    
    # ============================================
    # 窗口事件重写
    # ============================================
    
    def closeEvent(self, event):
        """
        处理窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        # 保存当前日记
        if self.editor.is_modified():
            self.save_current_entry()
        
        # 保存窗口位置和尺寸
        self.config.set('window_width', self.width())
        self.config.set('window_height', self.height())
        self.config.set('window_x', self.x())
        self.config.set('window_y', self.y())
        
        # 保存侧边栏宽度
        sizes = self.main_splitter.sizes()
        if len(sizes) >= 2:
            self.config.set('sidebar_width', sizes[0])
        
        # 保存配置
        self.config.save()
        
        # 接受关闭事件
        event.accept()
    
    def showEvent(self, event):
        """
        处理窗口显示事件
        
        Args:
            event: 显示事件
        """
        super().showEvent(event)
        
        # 窗口显示后刷新数据
        self._refresh_heatmap()
        self._refresh_diary_list()
