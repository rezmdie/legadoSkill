"""
MCP Server Tool Registry Module
提供高度可扩展的工具注册、发现和管理机制
"""

import asyncio
import inspect
from typing import Dict, List, Optional, Callable, Any, Type, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import json

from .exceptions import ToolNotFoundError, ToolExecutionError, ValidationError
from .logger import get_logger


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    pattern: Optional[str] = None


@dataclass
class ToolMetadata:
    """工具元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    timeout: float = 30.0
    retry_count: int = 3
    rate_limit: Optional[int] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ToolDefinition:
    """工具定义"""
    metadata: ToolMetadata
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def description(self) -> str:
        return self.metadata.description
    
    @property
    def enabled(self) -> bool:
        return self.metadata.enabled


class ToolAdapter(ABC):
    """工具适配器抽象基类"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """初始化适配器
        
        Args:
            name: 适配器名称
            config: 适配器配置
        """
        self.name = name
        self.config = config or {}
        self.logger = get_logger(f"adapter.{name}")
        self._initialized = False
    
    @abstractmethod
    async def initialize(self):
        """初始化适配器"""
        pass
    
    @abstractmethod
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            工具执行结果
        """
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[ToolDefinition]:
        """列出适配器支持的所有工具
        
        Returns:
            工具定义列表
        """
        pass
    
    @abstractmethod
    async def shutdown(self):
        """关闭适配器"""
        pass
    
    @property
    def initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized


class ToolWrapper:
    """工具包装器，封装工具执行逻辑"""
    
    def __init__(
        self,
        definition: ToolDefinition,
        handler: Callable,
        adapter: Optional[ToolAdapter] = None
    ):
        """初始化工具包装器
        
        Args:
            definition: 工具定义
            handler: 工具处理函数
            adapter: 工具适配器
        """
        self.definition = definition
        self.handler = handler
        self.adapter = adapter
        self.logger = get_logger(f"tool.{definition.name}")
        self._call_count = 0
        self._last_called: Optional[datetime] = None
        self._error_count = 0
    
    async def execute(self, params: Dict[str, Any]) -> Any:
        """执行工具
        
        Args:
            params: 工具参数
            
        Returns:
            工具执行结果
            
        Raises:
            ToolExecutionError: 工具执行失败
            ValidationError: 参数验证失败
        """
        # 验证参数
        self._validate_params(params)
        
        # 更新调用统计
        self._call_count += 1
        self._last_called = datetime.utcnow()
        
        try:
            # 执行工具
            if self.adapter:
                result = await self.adapter.execute(self.definition.name, params)
            else:
                if inspect.iscoroutinefunction(self.handler):
                    result = await self.handler(**params)
                else:
                    result = self.handler(**params)
            
            self.logger.log_tool_call(self.definition.name, params, result)
            return result
            
        except Exception as e:
            self._error_count += 1
            error_msg = str(e)
            self.logger.log_tool_call(self.definition.name, params, error=error_msg)
            raise ToolExecutionError(self.definition.name, error_msg)
    
    def _validate_params(self, params: Dict[str, Any]):
        """验证工具参数
        
        Args:
            params: 参数字典
            
        Raises:
            ValidationError: 参数验证失败
        """
        # 检查必需参数
        for param in self.definition.parameters:
            if param.required and param.name not in params:
                raise ValidationError(param.name, "Required parameter is missing")
            
            # 类型验证
            if param.name in params:
                value = params[param.name]
                if not self._validate_type(value, param.type):
                    raise ValidationError(param.name, f"Expected type {param.type}, got {type(value).__name__}")
                
                # 枚举验证
                if param.enum and value not in param.enum:
                    raise ValidationError(param.name, f"Value must be one of {param.enum}")
                
                # 范围验证
                if param.min is not None and value < param.min:
                    raise ValidationError(param.name, f"Value must be >= {param.min}")
                
                if param.max is not None and value > param.max:
                    raise ValidationError(param.name, f"Value must be <= {param.max}")
                
                # 模式验证
                if param.pattern and not re.match(param.pattern, str(value)):
                    raise ValidationError(param.name, f"Value does not match pattern {param.pattern}")
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """验证值类型
        
        Args:
            value: 要验证的值
            expected_type: 期望的类型
            
        Returns:
            是否匹配
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # 未知类型，跳过验证
        
        return isinstance(value, expected_python_type)
    
    @property
    def call_count(self) -> int:
        """调用次数"""
        return self._call_count
    
    @property
    def error_count(self) -> int:
        """错误次数"""
        return self._error_count
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self._call_count == 0:
            return 1.0
        return (self._call_count - self._error_count) / self._call_count


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        """初始化工具注册表"""
        self._tools: Dict[str, ToolWrapper] = {}
        self._adapters: Dict[str, ToolAdapter] = {}
        self._categories: Dict[str, List[str]] = {}
        self.logger = get_logger("tool_registry")
        self._initialized = False
    
    async def initialize(self):
        """初始化工具注册表"""
        if self._initialized:
            return
        
        self.logger.info("Initializing tool registry...")
        
        # 初始化所有适配器
        for adapter in self._adapters.values():
            if not adapter.initialized:
                await adapter.initialize()
        
        # 从适配器加载工具
        for adapter in self._adapters.values():
            try:
                tools = await adapter.list_tools()
                for tool_def in tools:
                    await self.register_from_adapter(tool_def, adapter)
            except Exception as e:
                self.logger.error(f"Failed to load tools from adapter {adapter.name}: {e}")
        
        self._initialized = True
        self.logger.info(f"Tool registry initialized with {len(self._tools)} tools")
    
    async def register(
        self,
        definition: ToolDefinition,
        handler: Callable,
        adapter: Optional[ToolAdapter] = None
    ):
        """注册工具
        
        Args:
            definition: 工具定义
            handler: 工具处理函数
            adapter: 工具适配器
        """
        wrapper = ToolWrapper(definition, handler, adapter)
        self._tools[definition.name] = wrapper
        
        # 更新分类索引
        category = definition.metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(definition.name)
        
        self.logger.info(f"Tool registered: {definition.name}")
    
    async def register_from_adapter(
        self,
        definition: ToolDefinition,
        adapter: ToolAdapter
    ):
        """从适配器注册工具
        
        Args:
            definition: 工具定义
            adapter: 工具适配器
        """
        wrapper = ToolWrapper(definition, None, adapter)
        self._tools[definition.name] = wrapper
        
        # 更新分类索引
        category = definition.metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(definition.name)
        
        self.logger.info(f"Tool registered from adapter: {definition.name}")
    
    def register_adapter(self, adapter: ToolAdapter):
        """注册适配器
        
        Args:
            adapter: 工具适配器
        """
        self._adapters[adapter.name] = adapter
        self.logger.info(f"Adapter registered: {adapter.name}")
    
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            工具执行结果
            
        Raises:
            ToolNotFoundError: 工具未找到
        """
        if tool_name not in self._tools:
            raise ToolNotFoundError(tool_name)
        
        wrapper = self._tools[tool_name]
        
        if not wrapper.definition.enabled:
            raise ToolExecutionError(tool_name, "Tool is disabled")
        
        return await wrapper.execute(params)
    
    def get_tool(self, tool_name: str) -> Optional[ToolWrapper]:
        """获取工具包装器
        
        Args:
            tool_name: 工具名称
            
        Returns:
            ToolWrapper实例，如果未找到则返回None
        """
        return self._tools.get(tool_name)
    
    def list_tools(self, category: Optional[str] = None, enabled_only: bool = True) -> List[ToolDefinition]:
        """列出工具
        
        Args:
            category: 工具分类，如果为None则返回所有分类
            enabled_only: 是否只返回启用的工具
            
        Returns:
            工具定义列表
        """
        tools = []
        
        if category:
            tool_names = self._categories.get(category, [])
            for name in tool_names:
                wrapper = self._tools.get(name)
                if wrapper and (not enabled_only or wrapper.definition.enabled):
                    tools.append(wrapper.definition)
        else:
            for wrapper in self._tools.values():
                if not enabled_only or wrapper.definition.enabled:
                    tools.append(wrapper.definition)
        
        return tools
    
    def get_categories(self) -> List[str]:
        """获取所有工具分类
        
        Returns:
            分类列表
        """
        return list(self._categories.keys())
    
    def search_tools(self, query: str) -> List[ToolDefinition]:
        """搜索工具
        
        Args:
            query: 搜索查询
            
        Returns:
            匹配的工具定义列表
        """
        query = query.lower()
        results = []
        
        for wrapper in self._tools.values():
            if not wrapper.definition.enabled:
                continue
            
            # 搜索名称、描述和标签
            if (query in wrapper.definition.name.lower() or
                query in wrapper.definition.description.lower() or
                any(query in tag.lower() for tag in wrapper.definition.metadata.tags)):
                results.append(wrapper.definition)
        
        return results
    
    def enable_tool(self, tool_name: str):
        """启用工具
        
        Args:
            tool_name: 工具名称
        """
        if tool_name in self._tools:
            self._tools[tool_name].definition.metadata.enabled = True
            self.logger.info(f"Tool enabled: {tool_name}")
    
    def disable_tool(self, tool_name: str):
        """禁用工具
        
        Args:
            tool_name: 工具名称
        """
        if tool_name in self._tools:
            self._tools[tool_name].definition.metadata.enabled = False
            self.logger.info(f"Tool disabled: {tool_name}")
    
    def get_tool_stats(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具统计信息
        
        Args:
            tool_name: 工具名称
            
        Returns:
            统计信息字典
        """
        wrapper = self._tools.get(tool_name)
        if not wrapper:
            return None
        
        return {
            "call_count": wrapper.call_count,
            "error_count": wrapper.error_count,
            "success_rate": wrapper.success_rate,
            "last_called": wrapper._last_called.isoformat() if wrapper._last_called else None
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有工具的统计信息
        
        Returns:
            统计信息字典，键为工具名称
        """
        return {
            name: self.get_tool_stats(name)
            for name in self._tools.keys()
        }
    
    async def shutdown(self):
        """关闭工具注册表"""
        self.logger.info("Shutting down tool registry...")
        
        # 关闭所有适配器
        for adapter in self._adapters.values():
            try:
                await adapter.shutdown()
            except Exception as e:
                self.logger.error(f"Failed to shutdown adapter {adapter.name}: {e}")
        
        self._initialized = False


# 全局工具注册表实例
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """获取全局工具注册表实例
    
    Returns:
        ToolRegistry实例
    """
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def tool(
    name: str,
    description: str,
    parameters: Optional[List[ToolParameter]] = None,
    **metadata_kwargs
):
    """工具装饰器，用于快速注册工具
    
    Args:
        name: 工具名称
        description: 工具描述
        parameters: 工具参数列表
        **metadata_kwargs: 其他元数据参数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        # 创建工具定义
        metadata = ToolMetadata(
            name=name,
            description=description,
            **metadata_kwargs
        )
        
        definition = ToolDefinition(
            metadata=metadata,
            parameters=parameters or []
        )
        
        # 注册工具
        registry = get_tool_registry()
        asyncio.create_task(registry.register(definition, func))
        
        return func
    
    return decorator
