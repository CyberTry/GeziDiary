"""
内置依赖包
==========
此目录包含应用运行所需的所有第三方依赖的内置版本
确保用户无需手动安装任何依赖即可运行应用

包含的依赖：
- PyQt6: GUI框架
- markdown: Markdown解析
- PyYAML: YAML配置处理
- python-dateutil: 日期时间处理
"""

# 当系统没有安装依赖时，使用此目录下的版本
import sys
import os

# 获取vendor目录路径
VENDOR_DIR = os.path.dirname(os.path.abspath(__file__))

# 如果系统路径中还没有这些包，添加vendor目录到Python路径
if VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)
