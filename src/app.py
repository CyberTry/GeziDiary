"""
应用主入口模块
==============
负责初始化应用程序和主窗口
"""

import sys
import os

# 导入PyQt6相关类
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineCore import QWebEngineProfile

# 导入主窗口类
from src.ui.main_window import MainWindow

# 导入配置管理器
from src.core.config import ConfigManager


def setup_application():
    """
    配置应用程序全局设置
    
    设置包括：
    - 高DPI支持
    - 应用程序样式
    - 全局字体
    """
    # 启用高DPI支持，确保在高分辨率屏幕上显示清晰
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


def load_stylesheet(app):
    """
    加载应用程序样式表
    
    Args:
        app: QApplication实例
    """
    # 定义现代扁平化风格的样式表
    stylesheet = """
    /* ==================== 全局样式 ==================== */
    
    /* 主窗口背景 */
    QMainWindow {
        background-color: #f6f8fa;
    }
    
    /* 侧边栏样式 */
    QWidget#sidebar {
        background-color: #ffffff;
        border-right: 1px solid #e1e4e8;
    }
    
    /* 按钮基础样式 */
    QPushButton {
        background-color: #2ea44f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #2c974b;
    }
    
    QPushButton:pressed {
        background-color: #298e46;
    }
    
    QPushButton:disabled {
        background-color: #94d3a2;
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* 次要按钮样式 */
    QPushButton#secondary {
        background-color: #f6f8fa;
        color: #24292e;
        border: 1px solid #e1e4e8;
    }
    
    QPushButton#secondary:hover {
        background-color: #f3f4f6;
    }
    
    /* 输入框样式 */
    QLineEdit, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 14px;
        color: #24292e;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border-color: #2ea44f;
    }
    
    /* 标签样式 */
    QLabel {
        color: #24292e;
        font-size: 14px;
    }
    
    QLabel#title {
        font-size: 20px;
        font-weight: 600;
        color: #24292e;
    }
    
    QLabel#subtitle {
        font-size: 16px;
        font-weight: 500;
        color: #586069;
    }
    
    /* 日历控件样式 */
    QCalendarWidget {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
    }
    
    QCalendarWidget QToolButton {
        background-color: transparent;
        color: #24292e;
        font-weight: 500;
    }
    
    QCalendarWidget QMenu {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
    }
    
    QCalendarWidget QSpinBox {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
    }
    
    /* 滚动条样式 */
    QScrollBar:vertical {
        background-color: #f6f8fa;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c6cbd1;
        border-radius: 6px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #959da5;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* 列表样式 */
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        outline: none;
    }
    
    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #e1e4e8;
    }
    
    QListWidget::item:selected {
        background-color: #f1f8ff;
        color: #24292e;
    }
    
    QListWidget::item:hover {
        background-color: #f6f8fa;
    }
    
    /* 对话框样式 */
    QDialog {
        background-color: #ffffff;
    }
    
    /* 分组框样式 */
    QGroupBox {
        font-weight: 600;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 16px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #586069;
    }
    
    /* 菜单样式 */
    QMenuBar {
        background-color: #ffffff;
        border-bottom: 1px solid #e1e4e8;
    }
    
    QMenuBar::item:selected {
        background-color: #f6f8fa;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
    }
    
    QMenu::item:selected {
        background-color: #f1f8ff;
    }
    """
    
    # 应用样式表
    app.setStyleSheet(stylesheet)


def main():
    """
    应用程序主入口函数
    
    初始化并启动整个应用程序
    """
    # 配置应用程序
    setup_application()
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("GeziDiary")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("鸽子工作室")
    
    # 加载样式表
    load_stylesheet(app)
    
    # 初始化配置管理器
    config = ConfigManager()
    
    # 创建并显示主窗口
    window = MainWindow(config)
    window.show()
    
    # 进入应用程序主循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
