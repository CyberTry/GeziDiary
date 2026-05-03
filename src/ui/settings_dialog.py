"""
设置对话框
==========
提供应用程序设置界面，允许用户自定义：
- 日记存储路径
- 编辑器字体大小
- 主题设置
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QSpinBox,
    QComboBox, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt

from ..core.config import ConfigManager


class SettingsDialog(QDialog):
    """
    设置对话框
    
    提供图形界面让用户修改应用程序配置。
    """
    
    def __init__(self, config: ConfigManager, parent=None):
        """
        初始化设置对话框
        
        Args:
            config: 配置管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.config = config
        
        # 设置对话框属性
        self.setWindowTitle("设置")
        self.setFixedSize(500, 350)
        self.setModal(True)  # 设置为模态对话框
        
        # 初始化UI
        self._init_ui()
        
        # 加载当前设置
        self._load_settings()
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== 存储设置组 =====
        storage_group = QGroupBox("存储设置")
        storage_layout = QFormLayout(storage_group)
        
        # 日记路径
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)  # 只读，通过按钮选择
        path_layout.addWidget(self.path_edit)
        
        btn_browse = QPushButton("浏览...")
        btn_browse.setFixedWidth(80)
        btn_browse.clicked.connect(self._browse_path)
        path_layout.addWidget(btn_browse)
        
        storage_layout.addRow("日记存储路径:", path_layout)
        
        layout.addWidget(storage_group)
        
        # ===== 外观设置组 =====
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QFormLayout(appearance_group)
        
        # 编辑器字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 24)
        self.font_size_spin.setSuffix(" px")
        appearance_layout.addRow("编辑器字体大小:", self.font_size_spin)
        
        # 预览字体大小
        self.preview_font_spin = QSpinBox()
        self.preview_font_spin.setRange(10, 24)
        self.preview_font_spin.setSuffix(" px")
        appearance_layout.addRow("预览字体大小:", self.preview_font_spin)
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色", "light")
        self.theme_combo.addItem("深色", "dark")
        appearance_layout.addRow("主题:", self.theme_combo)
        
        layout.addWidget(appearance_group)
        
        # ===== 按钮区域 =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("secondary")
        btn_cancel.setFixedWidth(80)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        # 保存按钮
        btn_save = QPushButton("保存")
        btn_save.setFixedWidth(80)
        btn_save.clicked.connect(self._save_settings)
        button_layout.addWidget(btn_save)
        
        layout.addStretch()
        layout.addLayout(button_layout)
    
    def _load_settings(self):
        """
        加载当前设置到界面
        """
        # 加载日记路径
        diary_path = self.config.get_diary_path()
        self.path_edit.setText(diary_path)
        
        # 加载字体大小
        editor_font_size = self.config.get('editor_font_size', 14)
        self.font_size_spin.setValue(editor_font_size)
        
        preview_font_size = self.config.get('preview_font_size', 14)
        self.preview_font_spin.setValue(preview_font_size)
        
        # 加载主题
        theme = self.config.get('theme', 'light')
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
    
    def _browse_path(self):
        """
        浏览选择存储路径
        """
        current_path = self.path_edit.text()
        
        # 打开文件夹选择对话框
        new_path = QFileDialog.getExistingDirectory(
            self,
            "选择日记存储路径",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        # 如果用户选择了路径，更新显示
        if new_path:
            self.path_edit.setText(new_path)
    
    def _save_settings(self):
        """
        保存设置
        """
        try:
            # 保存日记路径
            new_path = self.path_edit.text()
            if new_path:
                self.config.set_diary_path(new_path)
            
            # 保存字体大小
            self.config.set('editor_font_size', self.font_size_spin.value())
            self.config.set('preview_font_size', self.preview_font_spin.value())
            
            # 保存主题
            theme = self.theme_combo.currentData()
            self.config.set('theme', theme)
            
            # 显示成功提示
            QMessageBox.information(self, "成功", "设置已保存")
            
            # 关闭对话框并返回接受状态
            self.accept()
            
        except Exception as e:
            # 显示错误提示
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def get_new_path(self) -> str:
        """
        获取用户设置的新路径
        
        Returns:
            str: 新的日记存储路径
        """
        return self.path_edit.text()
