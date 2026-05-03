# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
设置对话框模块

功能：提供应用程序设置界面
"""

import os

# ============================================
# PyQt6 导入
# ============================================
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QSpinBox, QComboBox, QGroupBox, QFormLayout,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# ============================================
# 本地模块导入
# ============================================
from core.config import ConfigManager


class SettingsDialog(QDialog):
    """
    设置对话框类
    
    提供应用程序设置界面，包括存储路径、界面设置等
    
    Attributes:
        config (ConfigManager): 配置管理器
    """
    
    def __init__(self, config: ConfigManager, parent=None):
        """
        初始化设置对话框
        
        Args:
            config: 配置管理器实例
            parent: 父部件
        """
        super().__init__(parent)
        
        self.config = config
        
        # ============================================
        # 设置对话框属性
        # ============================================
        self.setWindowTitle('设置')
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # ============================================
        # 设置UI
        # ============================================
        self._setup_ui()
        
        # ============================================
        # 加载当前设置
        # ============================================
        self._load_settings()
    
    def _setup_ui(self):
        """
        设置UI布局
        """
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ============================================
        # 存储设置组
        # ============================================
        storage_group = QGroupBox('存储设置')
        storage_group.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        
        storage_layout = QFormLayout(storage_group)
        storage_layout.setSpacing(10)
        
        # 存储路径
        path_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText('选择日记存储路径')
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self._on_browse_path)
        path_layout.addWidget(browse_btn)
        
        storage_layout.addRow('存储路径:', path_layout)
        
        # 路径说明
        path_hint = QLabel('日记将按年月日格式保存到此路径')
        path_hint.setFont(QFont('Microsoft YaHei', 8))
        path_hint.setStyleSheet('color: #6e7781;')
        storage_layout.addRow('', path_hint)
        
        layout.addWidget(storage_group)
        
        # ============================================
        # 编辑器设置组
        # ============================================
        editor_group = QGroupBox('编辑器设置')
        editor_group.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        
        editor_layout = QFormLayout(editor_group)
        editor_layout.setSpacing(10)
        
        # 编辑器字体大小
        self.editor_font_spin = QSpinBox()
        self.editor_font_spin.setRange(8, 24)
        self.editor_font_spin.setSuffix(' pt')
        editor_layout.addRow('编辑器字体大小:', self.editor_font_spin)
        
        # 预览字体大小
        self.preview_font_spin = QSpinBox()
        self.preview_font_spin.setRange(8, 24)
        self.preview_font_spin.setSuffix(' pt')
        editor_layout.addRow('预览字体大小:', self.preview_font_spin)
        
        # 自动保存间隔
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(0, 300)
        self.auto_save_spin.setSuffix(' 秒')
        self.auto_save_spin.setSpecialValueText('禁用')
        auto_save_hint = QLabel('设置为0禁用自动保存')
        auto_save_hint.setFont(QFont('Microsoft YaHei', 8))
        auto_save_hint.setStyleSheet('color: #6e7781;')
        editor_layout.addRow('自动保存间隔:', self.auto_save_spin)
        editor_layout.addRow('', auto_save_hint)
        
        layout.addWidget(editor_group)
        
        # ============================================
        # 界面设置组
        # ============================================
        ui_group = QGroupBox('界面设置')
        ui_group.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        
        ui_layout = QFormLayout(ui_group)
        ui_layout.setSpacing(10)
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItem('浅色', 'light')
        self.theme_combo.addItem('深色', 'dark')
        self.theme_combo.addItem('跟随系统', 'auto')
        ui_layout.addRow('主题:', self.theme_combo)
        
        layout.addWidget(ui_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        # ============================================
        # 按钮区域
        # ============================================
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_settings(self):
        """
        加载当前设置到UI
        """
        # 存储路径
        storage_path = self.config.get_storage_path()
        self.path_edit.setText(storage_path)
        
        # 编辑器字体大小
        editor_font = self.config.get('editor_font_size', 14)
        self.editor_font_spin.setValue(editor_font)
        
        # 预览字体大小
        preview_font = self.config.get('preview_font_size', 14)
        self.preview_font_spin.setValue(preview_font)
        
        # 自动保存间隔
        auto_save = self.config.get('auto_save_interval', 30)
        self.auto_save_spin.setValue(auto_save)
        
        # 主题
        theme = self.config.get('theme', 'light')
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
    
    def _on_browse_path(self):
        """
        处理浏览路径按钮点击
        """
        # 获取当前路径
        current_path = self.path_edit.text()
        
        # 打开文件夹选择对话框
        path = QFileDialog.getExistingDirectory(
            self,
            '选择日记存储路径',
            current_path if current_path else os.path.expanduser('~')
        )
        
        # 如果选择了路径，更新输入框
        if path:
            self.path_edit.setText(path)
    
    def _on_accept(self):
        """
        处理确定按钮点击
        
        保存设置到配置
        """
        # ============================================
        # 验证并保存设置
        # ============================================
        
        # 存储路径
        new_path = self.path_edit.text().strip()
        if new_path:
            # 检查路径是否存在或可创建
            try:
                os.makedirs(new_path, exist_ok=True)
                self.config.set_storage_path(new_path)
            except Exception as e:
                QMessageBox.warning(self, '错误', f'无法设置存储路径: {e}')
                return
        
        # 编辑器字体大小
        self.config.set('editor_font_size', self.editor_font_spin.value())
        
        # 预览字体大小
        self.config.set('preview_font_size', self.preview_font_spin.value())
        
        # 自动保存间隔
        self.config.set('auto_save_interval', self.auto_save_spin.value())
        
        # 主题
        self.config.set('theme', self.theme_combo.currentData())
        
        # 保存配置
        self.config.save()
        
        # 接受对话框
        self.accept()
