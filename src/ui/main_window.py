"""
主窗口模块
==========
应用程序的主窗口，整合所有UI组件：
- 左侧边栏：日历热力图、日期选择
- 中间区域：Markdown编辑器
- 顶部工具栏：常用操作按钮
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QCalendarWidget, QPushButton, QLabel,
    QMessageBox, QFileDialog, QFrame, QScrollArea,
    QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon

from datetime import date, datetime

from ..core.config import ConfigManager
from ..core.diary_manager import DiaryManager
from .markdown_editor import MarkdownEditor
from .heatmap_calendar import HeatmapCalendar
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """
    应用程序主窗口
    
    整合所有功能模块，提供完整的日记编辑体验。
    """
    
    def __init__(self, config: ConfigManager):
        """
        初始化主窗口
        
        Args:
            config: 配置管理器实例
        """
        super().__init__()
        
        # 保存配置管理器
        self.config = config
        
        # 创建日记管理器
        self.diary_manager = DiaryManager(config.get_diary_path())
        
        # 当前选中的日期
        self.current_date = date.today()
        
        # 是否有未保存的更改
        self._has_unsaved_changes = False
        
        # 初始化UI
        self._init_ui()
        
        # 加载今天的日记
        self._load_diary(self.current_date)
        
        # 设置窗口标题和大小
        self.setWindowTitle("GeziDiary - 桌面日记")
        self.resize(
            config.get('window_width', 1200),
            config.get('window_height', 800)
        )
        
        # 设置窗口最小大小
        self.setMinimumSize(900, 600)
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ===== 左侧边栏 =====
        sidebar = self._create_sidebar()
        splitter.addWidget(sidebar)
        
        # ===== 编辑器区域 =====
        self.editor = MarkdownEditor()
        self.editor.content_changed.connect(self._on_content_changed)
        self.editor.save_requested.connect(self._save_current_diary)
        splitter.addWidget(self.editor)
        
        # 设置分割比例
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建状态栏
        self._create_status_bar()
        
        # 创建自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        interval = self.config.get('auto_save_interval', 30) * 1000  # 转换为毫秒
        self.auto_save_timer.start(interval)
    
    def _create_sidebar(self) -> QWidget:
        """
        创建左侧边栏
        
        Returns:
            QWidget: 边栏组件
        """
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # ===== 日期选择器 =====
        date_group = QFrame()
        date_layout = QVBoxLayout(date_group)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        # 日期选择器标题
        date_title = QLabel("选择日期")
        date_title.setObjectName("subtitle")
        date_layout.addWidget(date_title)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.clicked.connect(self._on_calendar_clicked)
        date_layout.addWidget(self.calendar)
        
        # 今天按钮
        btn_today = QPushButton("📅 今天")
        btn_today.clicked.connect(self._go_to_today)
        date_layout.addWidget(btn_today)
        
        layout.addWidget(date_group)
        
        # ===== 热力图 =====
        heatmap_group = QFrame()
        heatmap_layout = QVBoxLayout(heatmap_group)
        heatmap_layout.setContentsMargins(0, 0, 0, 0)
        
        # 热力图标题
        heatmap_title = QLabel("写作热力图")
        heatmap_title.setObjectName("subtitle")
        heatmap_layout.addWidget(heatmap_title)
        
        # 创建热力图
        self.heatmap = HeatmapCalendar()
        self.heatmap.set_data_callback(self._get_heatmap_data)
        self.heatmap.date_selected.connect(self._on_heatmap_date_selected)
        heatmap_layout.addWidget(self.heatmap)
        
        # 年份切换按钮
        year_layout = QHBoxLayout()
        btn_prev_year = QPushButton("◀")
        btn_prev_year.setFixedWidth(40)
        btn_prev_year.clicked.connect(self.heatmap.previous_year)
        
        btn_next_year = QPushButton("▶")
        btn_next_year.setFixedWidth(40)
        btn_next_year.clicked.connect(self.heatmap.next_year)
        
        year_layout.addWidget(btn_prev_year)
        year_layout.addStretch()
        year_layout.addWidget(btn_next_year)
        heatmap_layout.addLayout(year_layout)
        
        layout.addWidget(heatmap_group)
        
        layout.addStretch()
        
        return sidebar
    
    def _create_menu_bar(self):
        """
        创建菜单栏
        """
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        # 新建日记
        new_action = QAction("新建", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._go_to_today)
        file_menu.addAction(new_action)
        
        # 保存
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_current_diary)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 导出
        export_action = QAction("导出...", self)
        export_action.triggered.connect(self._export_diary)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        
        # 设置
        settings_action = QAction("设置...", self)
        settings_action.triggered.connect(self._open_settings)
        edit_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 当前日期标签
        self.date_label = QLabel()
        self.status_bar.addWidget(self.date_label)
        
        # 存储路径标签
        path_label = QLabel(f"存储: {self.config.get_diary_path()}")
        path_label.setStyleSheet("color: #586069;")
        self.status_bar.addPermanentWidget(path_label)
    
    def _get_heatmap_data(self, year: int) -> dict:
        """
        获取热力图数据
        
        Args:
            year: 年份
            
        Returns:
            dict: 日期到字数的映射
        """
        return self.diary_manager.get_yearly_stats(year)
    
    def _on_calendar_clicked(self, qdate: QDate):
        """
        日历点击事件处理
        
        Args:
            qdate: 选中的日期
        """
        selected_date = date(qdate.year(), qdate.month(), qdate.day())
        self._load_diary(selected_date)
    
    def _on_heatmap_date_selected(self, selected_date: date):
        """
        热力图日期选择事件处理
        
        Args:
            selected_date: 选中的日期
        """
        # 更新日历显示
        self.calendar.setSelectedDate(
            QDate(selected_date.year, selected_date.month, selected_date.day)
        )
        self._load_diary(selected_date)
    
    def _load_diary(self, target_date: date):
        """
        加载指定日期的日记
        
        Args:
            target_date: 目标日期
        """
        # 检查是否有未保存的更改
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "未保存的更改",
                "当前日记有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._save_current_diary()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # 更新当前日期
        self.current_date = target_date
        
        # 更新日期标签
        date_str = target_date.strftime("%Y年%m月%d日")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][target_date.weekday()]
        self.date_label.setText(f"当前: {date_str} {weekday}")
        
        # 读取日记内容
        content = self.diary_manager.read_diary(target_date)
        
        # 设置到编辑器
        self.editor.set_content(content)
        self._has_unsaved_changes = False
        
        # 添加到最近日记
        self.config.add_recent_diary(target_date.strftime("%Y-%m-%d"))
    
    def _save_current_diary(self):
        """
        保存当前日记
        """
        content = self.editor.get_content()
        
        # 如果内容为空，询问是否删除
        if not content.strip():
            if self.diary_manager.diary_exists(self.current_date):
                reply = QMessageBox.question(
                    self,
                    "删除日记",
                    "日记内容为空，是否删除该日记文件？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.diary_manager.delete_diary(self.current_date)
                    self._has_unsaved_changes = False
                    self.editor.set_modified(False)
                    # 更新热力图
                    self.heatmap.set_cell_data(self.current_date, 0)
            return
        
        # 保存日记
        if self.diary_manager.save_diary(self.current_date, content):
            self._has_unsaved_changes = False
            self.editor.set_modified(False)
            self.status_bar.showMessage("保存成功", 2000)
            
            # 更新热力图
            word_count = self.diary_manager.get_word_count(self.current_date)
            self.heatmap.set_cell_data(self.current_date, word_count)
        else:
            QMessageBox.critical(self, "错误", "保存失败，请检查存储路径")
    
    def _auto_save(self):
        """
        自动保存
        """
        if self._has_unsaved_changes:
            self._save_current_diary()
    
    def _on_content_changed(self):
        """
        内容变化事件处理
        """
        self._has_unsaved_changes = True
    
    def _go_to_today(self):
        """
        跳转到今天
        """
        today = date.today()
        self.calendar.setSelectedDate(QDate(today.year, today.month, today.day))
        self._load_diary(today)
    
    def _export_diary(self):
        """
        导出日记
        """
        # 获取当前内容
        content = self.editor.get_content()
        if not content:
            QMessageBox.information(self, "提示", "当前日记为空，无需导出")
            return
        
        # 选择导出路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日记",
            f"diary_{self.current_date.strftime('%Y%m%d')}.md",
            "Markdown文件 (*.md);;文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "成功", "导出成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _open_settings(self):
        """
        打开设置对话框
        """
        old_path = self.config.get_diary_path()
        
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            new_path = dialog.get_new_path()
            
            # 如果路径改变，更新日记管理器
            if new_path != old_path:
                self.diary_manager = DiaryManager(new_path)
                self._load_diary(self.current_date)
                
                # 更新状态栏
                self.status_bar.clearMessage()
                path_label = QLabel(f"存储: {new_path}")
                path_label.setStyleSheet("color: #586069;")
                self.status_bar.addPermanentWidget(path_label)
                
                # 重新加载热力图
                self.heatmap.load_year(self.heatmap.get_current_year())
    
    def _show_about(self):
        """
        显示关于对话框
        """
        QMessageBox.about(
            self,
            "关于 GeziDiary",
            """
            <h2>GeziDiary 1.0.0</h2>
            <p>一款简洁优雅的桌面日记应用</p>
            <p>功能特性：</p>
            <ul>
                <li>Markdown编辑与实时预览</li>
                <li>GitHub风格日历热力图</li>
                <li>按年月日自动组织文件</li>
                <li>自定义存储路径</li>
            </ul>
            <p>作者：鸽子工作室</p>
            """
        )
    
    def closeEvent(self, event):
        """
        窗口关闭事件处理
        
        Args:
            event: 关闭事件
        """
        # 检查是否有未保存的更改
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "未保存的更改",
                "当前日记有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._save_current_diary()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # 保存窗口大小
        self.config.set('window_width', self.width())
        self.config.set('window_height', self.height())
        
        event.accept()
