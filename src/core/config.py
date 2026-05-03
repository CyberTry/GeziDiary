"""
配置管理模块
============
负责应用程序配置的读取、保存和管理

支持的功能：
- 自定义日记存储路径
- 应用设置持久化
- 配置文件的YAML格式存储
"""

import os
import yaml
from pathlib import Path


class ConfigManager:
    """
    配置管理器类
    
    负责管理应用程序的所有配置项，包括：
    - 日记存储路径
    - 界面设置
    - 用户偏好
    
    Attributes:
        config_dir: 配置文件目录路径
        config_file: 配置文件完整路径
        config: 当前配置字典
    """
    
    def __init__(self):
        """
        初始化配置管理器
        
        创建配置目录（如果不存在）并加载现有配置
        """
        # 获取用户主目录，用于存储应用配置
        home_dir = Path.home()
        
        # 设置配置目录路径（使用隐藏文件夹）
        self.config_dir = home_dir / ".gezidiary"
        
        # 设置配置文件路径
        self.config_file = self.config_dir / "config.yaml"
        
        # 默认配置值
        self.default_config = {
            # 日记存储路径，默认为用户文档目录下的GeziDiary文件夹
            "diary_path": str(home_dir / "Documents" / "GeziDiary" / "diaries"),
            
            # 窗口设置
            "window": {
                "width": 1400,
                "height": 900,
                "maximized": False
            },
            
            # 编辑器设置
            "editor": {
                "font_size": 14,
                "tab_size": 4,
                "word_wrap": True,
                "auto_save": True,
                "auto_save_interval": 30  # 秒
            },
            
            # 日历热力图设置
            "heatmap": {
                "color_scheme": "github",  # github, gitlab, orange
                "show_weeks": 53  # 显示多少周的记录
            }
        }
        
        # 当前配置
        self.config = {}
        
        # 初始化配置
        self._init_config()
    
    def _init_config(self):
        """
        初始化配置
        
        创建配置目录，加载或创建配置文件
        """
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置，如果不存在则创建默认配置
        if self.config_file.exists():
            self.load_config()
        else:
            self.config = self.default_config.copy()
            self.save_config()
        
        # 确保日记存储目录存在
        diary_path = Path(self.config["diary_path"])
        diary_path.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """
        从文件加载配置
        
        如果配置文件损坏，使用默认配置
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                
            # 合并加载的配置和默认配置，确保所有必要的键都存在
            self.config = self._merge_config(self.default_config, loaded_config or {})
            
        except Exception as e:
            # 加载失败时使用默认配置
            print(f"加载配置文件失败: {e}，使用默认配置")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """
        保存配置到文件
        
        将当前配置以YAML格式写入配置文件
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def _merge_config(self, default, loaded):
        """
        递归合并配置字典
        
        Args:
            default: 默认配置字典
            loaded: 已加载的配置字典
            
        Returns:
            合并后的配置字典
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 递归合并嵌套字典
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key, default=None):
        """
        获取配置项的值
        
        支持使用点号访问嵌套配置，如 "editor.font_size"
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项的值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        设置配置项的值
        
        支持使用点号设置嵌套配置
        
        Args:
            key: 配置项键名
            value: 要设置的值
        """
        keys = key.split('.')
        config = self.config
        
        # 遍历到倒数第二个键
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置最终值
        config[keys[-1]] = value
        
        # 自动保存配置
        self.save_config()
    
    def get_diary_path(self):
        """
        获取日记存储路径
        
        Returns:
            日记存储目录的Path对象
        """
        return Path(self.config["diary_path"])
    
    def set_diary_path(self, path):
        """
        设置日记存储路径
        
        Args:
            path: 新的存储路径
        """
        # 转换为Path对象并创建目录
        diary_path = Path(path)
        diary_path.mkdir(parents=True, exist_ok=True)
        
        # 更新配置
        self.config["diary_path"] = str(diary_path)
        self.save_config()
    
    def get_editor_font_size(self):
        """
        获取编辑器字体大小
        
        Returns:
            字体大小（像素）
        """
        return self.get("editor.font_size", 14)
    
    def set_editor_font_size(self, size):
        """
        设置编辑器字体大小
        
        Args:
            size: 字体大小
        """
        self.set("editor.font_size", size)
    
    def is_auto_save_enabled(self):
        """
        检查是否启用了自动保存
        
        Returns:
            是否启用自动保存
        """
        return self.get("editor.auto_save", True)
    
    def get_auto_save_interval(self):
        """
        获取自动保存间隔
        
        Returns:
            自动保存间隔（秒）
        """
        return self.get("editor.auto_save_interval", 30)
    
    def get_heatmap_weeks(self):
        """
        获取热力图显示的周数
        
        Returns:
            显示的周数
        """
        return self.get("heatmap.show_weeks", 53)
    
    def get_heatmap_color_scheme(self):
        """
        获取热力图配色方案
        
        Returns:
            配色方案名称
        """
        return self.get("heatmap.color_scheme", "github")
