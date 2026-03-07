"""
MCP Server Configuration Loader Module
动态配置管理模块，从.kilocode/mcp.json文件中深度解析并加载设置
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from copy import deepcopy

from .exceptions import ConfigError
from .logger import get_logger


@dataclass
class ToolConfig:
    """工具配置"""
    name: str
    enabled: bool = True
    adapter: str = "python"
    config: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    retry_count: int = 3
    rate_limit: Optional[int] = None


@dataclass
class AdapterConfig:
    """适配器配置"""
    name: str
    type: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    max_concurrent: int = 10


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "127.0.0.1"
    port: int = 8080
    max_connections: int = 100
    request_timeout: float = 60.0
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    log_dir: str = "logs"
    console_output: bool = True
    file_output: bool = True
    json_format: bool = False
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class MCPConfig:
    """MCP服务器完整配置"""
    server: ServerConfig = field(default_factory=ServerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    tools: List[ToolConfig] = field(default_factory=list)
    adapters: List[AdapterConfig] = field(default_factory=list)
    system_prompt_path: str = "config/system/prompt.md"
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为.kilocode/mcp.json
        """
        self.config_path = Path(config_path) if config_path else Path(".kilocode/mcp.json")
        self.config: Optional[MCPConfig] = None
        self.logger = get_logger("config_loader")
        self._watchers: List[asyncio.Task] = []
        self._callbacks: List[callable] = []
    
    async def load(self) -> MCPConfig:
        """加载配置文件
        
        Returns:
            MCPConfig实例
            
        Raises:
            ConfigError: 配置文件不存在或格式错误
        """
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
                self.config = MCPConfig()
                return self.config
            
            self.logger.info(f"Loading config from: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
            
            # 解析配置
            self.config = self._parse_config(raw_config)
            
            self.logger.info("Config loaded successfully")
            return self.config
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")
    
    def _parse_config(self, raw_config: Dict[str, Any]) -> MCPConfig:
        """解析原始配置为MCPConfig对象
        
        Args:
            raw_config: 原始配置字典
            
        Returns:
            MCPConfig实例
        """
        config = MCPConfig()
        
        # 解析服务器配置
        if "server" in raw_config:
            server_config = raw_config["server"]
            config.server = ServerConfig(
                host=server_config.get("host", "127.0.0.1"),
                port=server_config.get("port", 8080),
                max_connections=server_config.get("max_connections", 100),
                request_timeout=server_config.get("request_timeout", 60.0),
                enable_cors=server_config.get("enable_cors", True),
                cors_origins=server_config.get("cors_origins", ["*"])
            )
        
        # 解析日志配置
        if "logging" in raw_config:
            logging_config = raw_config["logging"]
            config.logging = LoggingConfig(
                level=logging_config.get("level", "INFO"),
                log_dir=logging_config.get("log_dir", "logs"),
                console_output=logging_config.get("console_output", True),
                file_output=logging_config.get("file_output", True),
                json_format=logging_config.get("json_format", False),
                max_bytes=logging_config.get("max_bytes", 10485760),
                backup_count=logging_config.get("backup_count", 5)
            )
        
        # 解析工具配置
        if "tools" in raw_config:
            config.tools = [
                ToolConfig(
                    name=tool.get("name", ""),
                    enabled=tool.get("enabled", True),
                    adapter=tool.get("adapter", "python"),
                    config=tool.get("config", {}),
                    timeout=tool.get("timeout", 30.0),
                    retry_count=tool.get("retry_count", 3),
                    rate_limit=tool.get("rate_limit")
                )
                for tool in raw_config["tools"]
            ]
        
        # 解析适配器配置
        if "adapters" in raw_config:
            config.adapters = [
                AdapterConfig(
                    name=adapter.get("name", ""),
                    type=adapter.get("type", ""),
                    enabled=adapter.get("enabled", True),
                    config=adapter.get("config", {}),
                    max_concurrent=adapter.get("max_concurrent", 10)
                )
                for adapter in raw_config["adapters"]
            ]
        
        # 解析系统提示词路径
        if "system_prompt_path" in raw_config:
            config.system_prompt_path = raw_config["system_prompt_path"]
        
        # 解析自定义设置
        if "custom_settings" in raw_config:
            config.custom_settings = raw_config["custom_settings"]
        
        return config
    
    async def reload(self) -> MCPConfig:
        """重新加载配置文件
        
        Returns:
            重新加载的MCPConfig实例
        """
        self.logger.info("Reloading config...")
        old_config = self.config
        self.config = await self.load()
        
        # 触发回调
        for callback in self._callbacks:
            try:
                await callback(old_config, self.config)
            except Exception as e:
                self.logger.error(f"Config reload callback failed: {e}")
        
        return self.config
    
    def get(self) -> Optional[MCPConfig]:
        """获取当前配置
        
        Returns:
            当前MCPConfig实例，如果未加载则返回None
        """
        return self.config
    
    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """获取指定工具的配置
        
        Args:
            tool_name: 工具名称
            
        Returns:
            ToolConfig实例，如果未找到则返回None
        """
        if not self.config:
            return None
        
        for tool in self.config.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_adapter_config(self, adapter_name: str) -> Optional[AdapterConfig]:
        """获取指定适配器的配置
        
        Args:
            adapter_name: 适配器名称
            
        Returns:
            AdapterConfig实例，如果未找到则返回None
        """
        if not self.config:
            return None
        
        for adapter in self.config.adapters:
            if adapter.name == adapter_name:
                return adapter
        return None
    
    def get_enabled_tools(self) -> List[ToolConfig]:
        """获取所有启用的工具配置
        
        Returns:
            启用的ToolConfig列表
        """
        if not self.config:
            return []
        
        return [tool for tool in self.config.tools if tool.enabled]
    
    def get_enabled_adapters(self) -> List[AdapterConfig]:
        """获取所有启用的适配器配置
        
        Returns:
            启用的AdapterConfig列表
        """
        if not self.config:
            return []
        
        return [adapter for adapter in self.config.adapters if adapter.enabled]
    
    def add_reload_callback(self, callback: callable):
        """添加配置重载回调
        
        Args:
            callback: 回调函数，接收(old_config, new_config)参数
        """
        self._callbacks.append(callback)
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典
        
        Returns:
            配置字典
        """
        if not self.config:
            return {}
        
        return {
            "server": asdict(self.config.server),
            "logging": asdict(self.config.logging),
            "tools": [asdict(tool) for tool in self.config.tools],
            "adapters": [asdict(adapter) for adapter in self.config.adapters],
            "system_prompt_path": self.config.system_prompt_path,
            "custom_settings": self.config.custom_settings
        }
    
    async def save(self, config: Optional[MCPConfig] = None):
        """保存配置到文件
        
        Args:
            config: 要保存的配置，如果为None则保存当前配置
        """
        config_to_save = config or self.config
        if not config_to_save:
            raise ConfigError("No config to save")
        
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典
            config_dict = {
                "server": asdict(config_to_save.server),
                "logging": asdict(config_to_save.logging),
                "tools": [asdict(tool) for tool in config_to_save.tools],
                "adapters": [asdict(adapter) for adapter in config_to_save.adapters],
                "system_prompt_path": config_to_save.system_prompt_path,
                "custom_settings": config_to_save.custom_settings
            }
            
            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Config saved to: {self.config_path}")
            
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")


# 全局配置加载器实例
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """获取全局配置加载器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigLoader实例
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader
