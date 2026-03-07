"""
MCP Server Tool Discovery Module
实现工具发现机制，支持动态注册和发现各类工具适配器
"""

import asyncio
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass, field
import importlib.util
import sys

from .tool_registry import ToolAdapter, ToolDefinition, ToolMetadata, ToolParameter
from .exceptions import AdapterError
from .logger import get_logger


@dataclass
class DiscoveryConfig:
    """发现配置"""
    paths: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=lambda: ["*.py", "tool_*.py", "*_tool.py"])
    recursive: bool = True
    auto_register: bool = True
    exclude_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "*.pyc", "test_*"])


@dataclass
class DiscoveredTool:
    """发现的工具"""
    name: str
    module_path: str
    function_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    parameters: List[ToolParameter] = field(default_factory=list)
    enabled: bool = True


class ToolDiscovery:
    """工具发现器"""
    
    def __init__(self, config: Optional[DiscoveryConfig] = None):
        """初始化工具发现器
        
        Args:
            config: 发现配置
        """
        self.config = config or DiscoveryConfig()
        self.logger = get_logger("tool_discovery")
        self._discovered_tools: Dict[str, DiscoveredTool] = {}
        self._loaded_modules: Dict[str, Any] = {}
        self._adapters: Dict[str, Type[ToolAdapter]] = {}
    
    async def discover(self) -> List[DiscoveredTool]:
        """发现工具
        
        Returns:
            发现的工具列表
        """
        self.logger.info("Starting tool discovery...")
        
        # 发现Python工具
        await self._discover_python_tools()
        
        # 发现适配器
        await self._discover_adapters()
        
        self.logger.info(f"Discovery completed: {len(self._discovered_tools)} tools found")
        return list(self._discovered_tools.values())
    
    async def _discover_python_tools(self):
        """发现Python工具"""
        for path_str in self.config.paths:
            path = Path(path_str)
            
            if not path.exists():
                self.logger.warning(f"Discovery path not found: {path}")
                continue
            
            if path.is_file() and path.suffix == ".py":
                # 单个文件
                await self._discover_tools_from_file(path)
            elif path.is_dir():
                # 目录
                await self._discover_tools_from_directory(path)
    
    async def _discover_tools_from_directory(self, directory: Path):
        """从目录发现工具
        
        Args:
            directory: 目录路径
        """
        self.logger.debug(f"Scanning directory: {directory}")
        
        # 查找匹配的文件
        files = []
        if self.config.recursive:
            for pattern in self.config.patterns:
                files.extend(directory.rglob(pattern))
        else:
            for pattern in self.config.patterns:
                files.extend(directory.glob(pattern))
        
        # 过滤排除的文件
        for exclude_pattern in self.config.exclude_patterns:
            files = [f for f in files if not f.match(exclude_pattern)]
        
        # 处理每个文件
        for file_path in files:
            try:
                await self._discover_tools_from_file(file_path)
            except Exception as e:
                self.logger.error(f"Failed to discover tools from {file_path}: {e}")
    
    async def _discover_tools_from_file(self, file_path: Path):
        """从文件发现工具
        
        Args:
            file_path: 文件路径
        """
        self.logger.debug(f"Scanning file: {file_path}")
        
        # 加载模块
        module = await self._load_module_from_file(file_path)
        if module is None:
            return
        
        # 查找工具函数
        for name, obj in inspect.getmembers(module):
            # 检查是否为函数
            if inspect.isfunction(obj) and not name.startswith("_"):
                await self._process_function(name, obj, file_path)
            
            # 检查是否为类
            elif inspect.isclass(obj) and not name.startswith("_"):
                await self._process_class(name, obj, file_path)
    
    async def _load_module_from_file(self, file_path: Path) -> Optional[Any]:
        """从文件加载模块
        
        Args:
            file_path: 文件路径
            
        Returns:
            模块对象，如果加载失败则返回None
        """
        try:
            # 生成模块名
            module_name = file_path.stem
            
            # 检查是否已加载
            if module_name in self._loaded_modules:
                return self._loaded_modules[module_name]
            
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                self.logger.warning(f"Failed to load module from {file_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._loaded_modules[module_name] = module
            return module
            
        except Exception as e:
            self.logger.error(f"Failed to load module from {file_path}: {e}")
            return None
    
    async def _process_function(self, name: str, func: Callable, file_path: Path):
        """处理函数
        
        Args:
            name: 函数名
            func: 函数对象
            file_path: 文件路径
        """
        # 检查是否有工具装饰器
        if hasattr(func, '_is_tool'):
            tool_name = getattr(func, '_tool_name', name)
            tool_description = getattr(func, '_tool_description', func.__doc__ or f"Tool: {name}")
            tool_category = getattr(func, '_tool_category', "general")
            tool_tags = getattr(func, '_tool_tags', [])
            
            # 解析参数
            parameters = self._parse_function_parameters(func)
            
            # 创建发现的工具
            discovered_tool = DiscoveredTool(
                name=tool_name,
                module_path=str(file_path),
                function_name=name,
                metadata={
                    "description": tool_description,
                    "category": tool_category,
                    "tags": tool_tags,
                    "author": getattr(func, '_tool_author', "Unknown"),
                    "version": getattr(func, '_tool_version', "1.0.0")
                },
                parameters=parameters
            )
            
            self._discovered_tools[tool_name] = discovered_tool
            self.logger.debug(f"Discovered tool function: {tool_name}")
    
    async def _process_class(self, name: str, cls: Type, file_path: Path):
        """处理类
        
        Args:
            name: 类名
            cls: 类对象
            file_path: 文件路径
        """
        # 检查是否为ToolAdapter子类
        if issubclass(cls, ToolAdapter) and cls != ToolAdapter:
            adapter_name = getattr(cls, '_adapter_name', name.lower())
            self._adapters[adapter_name] = cls
            self.logger.debug(f"Discovered adapter: {adapter_name}")
        
        # 查找类方法
        for method_name, method in inspect.getmembers(cls, inspect.isfunction):
            if not method_name.startswith("_") and hasattr(method, '_is_tool'):
                tool_name = f"{name}.{method_name}"
                tool_description = getattr(method, '_tool_description', method.__doc__ or f"Tool: {tool_name}")
                tool_category = getattr(method, '_tool_category', "general")
                tool_tags = getattr(method, '_tool_tags', [])
                
                # 解析参数
                parameters = self._parse_function_parameters(method)
                
                # 创建发现的工具
                discovered_tool = DiscoveredTool(
                    name=tool_name,
                    module_path=str(file_path),
                    function_name=method_name,
                    metadata={
                        "description": tool_description,
                        "category": tool_category,
                        "tags": tool_tags,
                        "class_name": name,
                        "author": getattr(method, '_tool_author', "Unknown"),
                        "version": getattr(method, '_tool_version', "1.0.0")
                    },
                    parameters=parameters
                )
                
                self._discovered_tools[tool_name] = discovered_tool
                self.logger.debug(f"Discovered tool method: {tool_name}")
    
    async def _discover_adapters(self):
        """发现适配器"""
        # 从配置路径发现适配器
        for path_str in self.config.paths:
            path = Path(path_str)
            
            if path.is_dir():
                await self._discover_adapters_from_directory(path)
    
    async def _discover_adapters_from_directory(self, directory: Path):
        """从目录发现适配器
        
        Args:
            directory: 目录路径
        """
        # 查找适配器文件
        adapter_files = list(directory.glob("*adapter*.py"))
        
        for file_path in adapter_files:
            try:
                module = await self._load_module_from_file(file_path)
                if module is None:
                    continue
                
                # 查找适配器类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, ToolAdapter) and 
                        obj != ToolAdapter and
                        not name.startswith("_")):
                        
                        adapter_name = getattr(obj, '_adapter_name', name.lower())
                        self._adapters[adapter_name] = obj
                        self.logger.debug(f"Discovered adapter: {adapter_name}")
                        
            except Exception as e:
                self.logger.error(f"Failed to discover adapters from {file_path}: {e}")
    
    def _parse_function_parameters(self, func: Callable) -> List[ToolParameter]:
        """解析函数参数
        
        Args:
            func: 函数对象
            
        Returns:
            参数定义列表
        """
        parameters = []
        sig = inspect.signature(func)
        
        for name, param in sig.parameters.items():
            # 跳过self参数
            if name == "self":
                continue
            
            # 确定参数类型
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                annotation = param.annotation
                if annotation == int:
                    param_type = "integer"
                elif annotation == float:
                    param_type = "number"
                elif annotation == bool:
                    param_type = "boolean"
                elif annotation == list:
                    param_type = "array"
                elif annotation == dict:
                    param_type = "object"
            
            # 确定是否必需
            required = param.default == inspect.Parameter.empty
            
            # 创建参数定义
            tool_param = ToolParameter(
                name=name,
                type=param_type,
                description=f"Parameter: {name}",
                required=required,
                default=param.default if param.default != inspect.Parameter.empty else None
            )
            
            parameters.append(tool_param)
        
        return parameters
    
    def get_discovered_tools(self) -> List[DiscoveredTool]:
        """获取所有发现的工具
        
        Returns:
            发现的工具列表
        """
        return list(self._discovered_tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[DiscoveredTool]:
        """获取指定的工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            发现的工具，如果未找到则返回None
        """
        return self._discovered_tools.get(tool_name)
    
    def get_adapters(self) -> Dict[str, Type[ToolAdapter]]:
        """获取所有发现的适配器
        
        Returns:
            适配器字典，键为适配器名称
        """
        return self._adapters.copy()
    
    def get_adapter(self, adapter_name: str) -> Optional[Type[ToolAdapter]]:
        """获取指定的适配器
        
        Args:
            adapter_name: 适配器名称
            
        Returns:
            适配器类，如果未找到则返回None
        """
        return self._adapters.get(adapter_name)
    
    def enable_tool(self, tool_name: str):
        """启用工具
        
        Args:
            tool_name: 工具名称
        """
        if tool_name in self._discovered_tools:
            self._discovered_tools[tool_name].enabled = True
    
    def disable_tool(self, tool_name: str):
        """禁用工具
        
        Args:
            tool_name: 工具名称
        """
        if tool_name in self._discovered_tools:
            self._discovered_tools[tool_name].enabled = False
    
    def clear(self):
        """清除所有发现的工具和适配器"""
        self._discovered_tools.clear()
        self._adapters.clear()


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: str = "general",
    tags: Optional[List[str]] = None,
    author: str = "Unknown",
    version: str = "1.0.0"
):
    """工具装饰器，用于标记函数为工具
    
    Args:
        name: 工具名称
        description: 工具描述
        category: 工具分类
        tags: 工具标签
        author: 作者
        version: 版本
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        func._is_tool = True
        func._tool_name = name or func.__name__
        func._tool_description = description or func.__doc__
        func._tool_category = category
        func._tool_tags = tags or []
        func._tool_author = author
        func._tool_version = version
        return func
    
    return decorator


def adapter(name: Optional[str] = None):
    """适配器装饰器，用于标记类为适配器
    
    Args:
        name: 适配器名称
        
    Returns:
        装饰器函数
    """
    def decorator(cls: Type[ToolAdapter]):
        cls._adapter_name = name or cls.__name__.lower()
        return cls
    
    return decorator


# 全局工具发现器实例
_tool_discovery: Optional[ToolDiscovery] = None


def get_tool_discovery(config: Optional[DiscoveryConfig] = None) -> ToolDiscovery:
    """获取全局工具发现器实例
    
    Args:
        config: 发现配置
        
    Returns:
        ToolDiscovery实例
    """
    global _tool_discovery
    if _tool_discovery is None:
        _tool_discovery = ToolDiscovery(config)
    return _tool_discovery
