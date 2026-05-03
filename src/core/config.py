# -*- coding: utf-8 -*-
"""
GeziDiary - 鸽子日记
配置管理模块

功能：管理应用程序配置，包括存储路径、界面设置等
配置文件保存为JSON格式
"""

import os
import json
from pathlib import Path


class ConfigManager:
    """
    配置管理器类
    
    负责加载、保存和管理应用程序配置
    配置存储在用户目录下的JSON文件中
    
    Attributes:
        config_file (str): 配置文件路径
        config (dict): 配置数据字典
        default_config (dict): 默认配置
    
    使用示例：
        >>> config = ConfigManager()
        >>> storage_path = config.get('storage_path')
        >>> config.set('theme', 'dark')
        >>> config.save()
    """
    
    # ============================================
    # 默认配置常量
    # ============================================
    DEFAULT_CONFIG = {
        # 日记存储路径（默认在用户文档目录下）
        'storage_path': '',
        # 界面主题（light/dark/auto）
        'theme': 'light',
        # 编辑器字体大小
        'editor_font_size': 14,
        # 预览字体大小
        'preview_font_size': 14,
        # 自动保存间隔（秒，0表示禁用）
        'auto_save_interval': 30,
        # 窗口尺寸
        'window_width': 1200,
        'window_height': 800,
        # 窗口位置（-1表示居中）
        'window_x': -1,
        'window_y': -1,
        # 侧边栏宽度
        'sidebar_width': 280,
        # 编辑器/预览分割比例
        'editor_split_ratio': 0.5,
    }
    
    def __init__(self):
        """
        初始化配置管理器
        
        功能：
            1. 确定配置文件路径
            2. 加载现有配置或创建默认配置
        """
        # ============================================
        # 设置配置文件路径
        # ============================================
        # 获取应用数据目录（跨平台兼容）
        # Windows: %APPDATA%/GeziDiary
        # macOS: ~/Library/Application Support/GeziDiary
        # Linux: ~/.config/GeziDiary
        self.app_dir = self._get_app_data_dir()
        
        # 确保应用数据目录存在
        os.makedirs(self.app_dir, exist_ok=True)
        
        # 配置文件完整路径
        self.config_file = os.path.join(self.app_dir, 'config.json')
        
        # ============================================
        # 加载配置
        # ============================================
        # 先复制默认配置
        self.config = self.DEFAULT_CONFIG.copy()
        
        # 从文件加载配置并合并
        self._load_config()
        
        # 如果存储路径为空，设置默认路径
        if not self.config.get('storage_path'):
            self.config['storage_path'] = self._get_default_storage_path()
    
    def _get_app_data_dir(self) -> str:
        """
        获取应用数据目录路径
        
        根据操作系统返回合适的应用数据目录
        
        Returns:
            str: 应用数据目录的绝对路径
        """
        # 获取用户主目录
        home = Path.home()
        
        # 根据操作系统选择合适的路径
        if os.name == 'nt':  # Windows
            # 使用APPDATA环境变量，如果不存在则使用用户目录
            app_data = os.environ.get('APPDATA', str(home))
            return os.path.join(app_data, 'GeziDiary')
        elif os.name == 'posix':
            # 检查是否为macOS
            if os.uname().sysname == 'Darwin':
                return str(home / 'Library' / 'Application Support' / 'GeziDiary')
            else:  # Linux
                config_dir = os.environ.get('XDG_CONFIG_HOME', str(home / '.config'))
                return os.path.join(config_dir, 'GeziDiary')
        else:
            # 其他系统使用用户目录
            return str(home / '.gezidiary')
    
    def _get_default_storage_path(self) -> str:
        """
        获取默认日记存储路径
        
        Returns:
            str: 默认存储路径
        """
        # 默认存储在用户文档目录下的GeziDiary文件夹
        documents = Path.home() / 'Documents'
        
        # 如果Documents目录不存在，使用用户主目录
        if not documents.exists():
            documents = Path.home()
        
        return str(documents / 'GeziDiary' / 'Diaries')
    
    def _load_config(self):
        """
        从配置文件加载配置
        
        如果配置文件不存在或损坏，使用默认配置
        """
        # 检查配置文件是否存在
        if not os.path.exists(self.config_file):
            # 配置文件不存在，使用默认配置
            return
        
        try:
            # 打开并读取配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # 合并加载的配置到默认配置
            # 这样新增的配置项也能被正确处理
            self.config.update(loaded_config)
            
        except json.JSONDecodeError:
            # JSON解析错误，配置文件损坏
            # 保留默认配置，将在下次保存时覆盖损坏的文件
            pass
        except Exception:
            # 其他错误，同样使用默认配置
            pass
    
    def save(self):
        """
        保存配置到文件
        
        将当前配置持久化到JSON文件
        """
        try:
            # 以UTF-8编码写入JSON文件
            # indent=4使JSON文件可读性更好
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            # 保存失败时打印错误（在生产环境可能需要更优雅的处理）
            print(f"保存配置失败: {e}")
    
    def get(self, key: str, default=None):
        """
        获取配置项的值
        
        Args:
            key: 配置项名称
            default: 默认值（如果配置项不存在）
        
        Returns:
            配置项的值，如果不存在则返回default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """
        设置配置项的值
        
        Args:
            key: 配置项名称
            value: 配置项值
        """
        self.config[key] = value
    
    def get_storage_path(self) -> str:
        """
        获取日记存储路径
        
        Returns:
            str: 日记存储目录的绝对路径
        """
        path = self.get('storage_path')
        
        # 确保存储目录存在
        if path and not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception:
                pass
        
        return path
    
    def set_storage_path(self, path: str):
        """
        设置日记存储路径
        
        Args:
            path: 新的存储路径
        """
        # 规范化路径（转换为绝对路径）
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # 确保目录存在
        os.makedirs(abs_path, exist_ok=True)
        
        # 更新配置
        self.set('storage_path', abs_path)
