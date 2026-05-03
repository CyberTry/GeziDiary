# GeziDiary - 鸽子日记

一款简洁优雅的桌面日记应用，支持Markdown编辑和GitHub风格的热力图展示。

## 功能特性

- **Markdown编辑**：支持完整的Markdown语法，实时预览
- **热力图日历**：类似GitHub贡献图的日历热力图，直观展示每日写作量
- **文件管理**：按年月日格式自动组织日记文件
- **自定义存储**：可自定义日记存储路径
- **现代UI**：扁平化设计风格，支持高DPI显示
- **自动保存**：支持定时自动保存，防止数据丢失
- **统计信息**：实时显示写作统计，包括总篇数、总字数、连续天数等

## 系统要求

- Windows 10/11、macOS 10.14+ 或 Linux
- Python 3.8+（运行源码）

## 快速开始

### 方法一：使用可执行文件（推荐）

1. 下载最新版本的 `GeziDiary.exe`
2. 双击运行即可

### 方法二：运行源码

1. 克隆或下载源码
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用：
   ```bash
   # Windows
   run.bat
   
   # Linux/macOS
   ./run.sh
   ```

## 文件结构

```
GeziDiary/
├── main.py                 # 程序入口
├── requirements.txt        # Python依赖
├── src/
│   ├── app.py             # 应用主类
│   ├── core/              # 核心功能模块
│   │   ├── config.py      # 配置管理
│   │   ├── diary_manager.py   # 日记管理
│   │   └── markdown_processor.py  # Markdown处理
│   ├── ui/                # 用户界面模块
│   │   ├── main_window.py     # 主窗口
│   │   ├── heatmap_calendar.py    # 热力图日历
│   │   ├── markdown_editor.py     # Markdown编辑器
│   │   ├── diary_list_widget.py   # 日记列表
│   │   ├── stats_widget.py        # 统计信息
│   │   └── settings_dialog.py     # 设置对话框
│   └── utils/             # 工具函数
└── run.bat / run.sh       # 启动脚本
```

## 日记存储格式

日记按以下目录结构存储：

```
存储路径/
├── 2024/
│   ├── 01/
│   │   ├── 01.md
│   │   ├── 02.md
│   │   └── ...
│   ├── 02/
│   └── ...
└── 2025/
    └── ...
```

每篇日记以 `.md` 文件格式保存，可直接用任何文本编辑器打开。

## 打包发布

使用 PyInstaller 打包为独立可执行文件：

```bash
# Windows
package.bat

# 或手动执行
pyinstaller --name="GeziDiary" --windowed --onefile main.py
```

打包后的可执行文件位于 `dist/GeziDiary.exe`。

## 开发团队

**鸽子工作室**

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-01-XX)

- 初始版本发布
- 支持Markdown编辑和实时预览
- 实现GitHub风格热力图日历
- 支持自定义存储路径
- 添加写作统计功能
