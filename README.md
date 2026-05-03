功能特性：
Markdown编辑：支持实时预览、工具栏快捷操作
日历热力图：类似GitHub的贡献图，展示每日写作量
文件组织：按 年/月/YYYY-MM-DD.md 格式存储
自定义路径：可在设置中修改存储位置
现代UI：扁平化设计，支持浅色主题
自动保存：定时自动保存功能
GeziDiary/
├── main.py                  # 程序入口
├── requirements.txt         # 依赖清单
├── start.bat               # Windows启动脚本
├── start.sh                # Linux/Mac启动脚本
└── src/
    ├── __init__.py
    ├── app.py              # 应用初始化
    ├── core/               # 核心模块
    │   ├── __init__.py
    │   ├── config.py       # 配置管理（YAML格式）
    │   ├── diary_manager.py # 日记文件管理
    │   └── markdown_processor.py # Markdown解析
    ├── ui/                 # UI模块
    │   ├── __init__.py
    │   ├── main_window.py  # 主窗口
    │   ├── markdown_editor.py # Markdown编辑器
    │   ├── heatmap_calendar.py # 日历热力图
    │   └── settings_dialog.py # 设置对话框
    └── utils/              # 工具模块
        ├── __init__.py
        └── helpers.py      # 辅助函数