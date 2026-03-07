"""
MCP Server Python Tool Adapter Module
支持位于assets/projects_new_extracted/src/的Python工具适配器
"""

import asyncio
import importlib.util
import sys
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from ..tool_registry import ToolAdapter, ToolDefinition, ToolMetadata, ToolParameter
from ..exceptions import AdapterError, ToolExecutionError
from ..logger import get_logger


@dataclass
class PythonToolConfig:
    """Python工具配置"""
    tool_path: str
    module_name: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    timeout: float = 30.0
    sandbox: bool = False


class PythonToolAdapter(ToolAdapter):
    """Python工具适配器"""
    
    def __init__(self, name: str = "python", config: Optional[Dict[str, Any]] = None):
        """初始化Python工具适配器
        
        Args:
            name: 适配器名称
            config: 适配器配置
        """
        super().__init__(name, config)
        self._tools: Dict[str, PythonToolConfig] = {}
        self._loaded_modules: Dict[str, Any] = {}
        self._tool_functions: Dict[str, Callable] = {}
        self._tool_classes: Dict[str, Any] = {}
    
    async def initialize(self):
        """初始化适配器"""
        if self._initialized:
            return
        
        self.logger.info(f"Initializing Python tool adapter: {self.name}")
        
        # 从配置中加载工具
        if "tools" in self.config:
            for tool_config in self.config["tools"]:
                await self.register_tool_from_config(tool_config)
        
        # 自动发现工具
        if "auto_discover" in self.config and self.config["auto_discover"]:
            await self.discover_tools()
        
        self._initialized = True
        self.logger.info(f"Python tool adapter initialized with {len(self._tools)} tools")
    
    async def register_tool_from_config(self, config: Dict[str, Any]):
        """从配置注册工具
        
        Args:
            config: 工具配置字典
        """
        tool_config = PythonToolConfig(
            tool_path=config.get("tool_path", ""),
            module_name=config.get("module_name"),
            function_name=config.get("function_name"),
            class_name=config.get("class_name"),
            timeout=config.get("timeout", 30.0),
            sandbox=config.get("sandbox", False)
        )
        
        tool_name = config.get("name", Path(tool_config.tool_path).stem)
        self._tools[tool_name] = tool_config
        
        # 预加载模块
        await self._load_tool_module(tool_name, tool_config)
        
        self.logger.info(f"Python tool registered: {tool_name}")
    
    async def discover_tools(self):
        """自动发现工具"""
        base_path = self.config.get("base_path", "assets/projects_new_extracted/src")
        base_path = Path(base_path)
        
        if not base_path.exists():
            self.logger.warning(f"Tool discovery path not found: {base_path}")
            return
        
        self.logger.info(f"Discovering Python tools in: {base_path}")
        
        # 递归查找Python文件
        for py_file in base_path.rglob("*.py"):
            # 跳过__init__.py和测试文件
            if py_file.name.startswith("__") or py_file.name.startswith("test_"):
                continue
            
            try:
                # 加载模块并提取函数
                await self._load_tool_from_file(py_file)
            except Exception as e:
                self.logger.error(f"Failed to load tool from {py_file}: {e}")
    
    async def _load_tool_from_file(self, file_path: Path):
        """从文件加载工具
        
        Args:
            file_path: Python文件路径
        """
        # 生成模块名
        module_name = file_path.stem
        
        # 加载模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise AdapterError(self.name, f"Failed to load module from {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        self._loaded_modules[module_name] = module
        
        # 查找可调用函数
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                # 注册为工具
                tool_name = f"{module_name}.{name}"
                self._tool_functions[tool_name] = obj
                
                # 创建工具配置
                self._tools[tool_name] = PythonToolConfig(
                    tool_path=str(file_path),
                    module_name=module_name,
                    function_name=name
                )
                
                self.logger.debug(f"Discovered tool function: {tool_name}")
            
            elif inspect.isclass(obj) and not name.startswith("_"):
                # 查找类方法
                for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                    if not method_name.startswith("_"):
                        tool_name = f"{module_name}.{name}.{method_name}"
                        self._tool_functions[tool_name] = method
                        
                        self._tools[tool_name] = PythonToolConfig(
                            tool_path=str(file_path),
                            module_name=module_name,
                            class_name=name,
                            function_name=method_name
                        )
                        
                        self.logger.debug(f"Discovered tool method: {tool_name}")
    
    async def _load_tool_module(self, tool_name: str, config: PythonToolConfig):
        """加载工具模块
        
        Args:
            tool_name: 工具名称
            config: 工具配置
        """
        try:
            file_path = Path(config.tool_path)
            if not file_path.exists():
                self.logger.warning(f"Tool file not found: {file_path}")
                return
            
            module_name = config.module_name or file_path.stem
            
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise AdapterError(self.name, f"Failed to load module from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._loaded_modules[module_name] = module
            
            # 提取函数或类方法
            if config.class_name:
                cls = getattr(module, config.class_name)
                self._tool_classes[tool_name] = cls
                if config.function_name:
                    method = getattr(cls, config.function_name)
                    self._tool_functions[tool_name] = method
            elif config.function_name:
                func = getattr(module, config.function_name)
                self._tool_functions[tool_name] = func
            
        except Exception as e:
            raise AdapterError(self.name, f"Failed to load tool module: {e}")
    
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self._tools:
            raise ToolExecutionError(tool_name, "Tool not found")
        
        config = self._tools[tool_name]
        
        try:
            # 设置超时
            timeout = config.timeout
            
            # 执行工具
            if tool_name in self._tool_functions:
                func = self._tool_functions[tool_name]
                result = await asyncio.wait_for(self._execute_function(func, params), timeout)
            else:
                raise ToolExecutionError(tool_name, "Tool function not found")
            
            return result
            
        except asyncio.TimeoutError:
            raise ToolExecutionError(tool_name, f"Execution timeout after {timeout}s")
        except Exception as e:
            raise ToolExecutionError(tool_name, str(e))
    
    async def _execute_function(self, func: Callable, params: Dict[str, Any]) -> Any:
        """执行函数
        
        Args:
            func: 函数对象
            params: 参数字典
            
        Returns:
            函数执行结果
        """
        # 检查是否为协程函数
        if inspect.iscoroutinefunction(func):
            return await func(**params)
        else:
            # 在线程池中执行同步函数
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(**params))
    
    async def list_tools(self) -> List[ToolDefinition]:
        """列出适配器支持的所有工具
        
        Returns:
            工具定义列表
        """
        tools = []
        
        for tool_name, config in self._tools.items():
            # 获取函数签名
            func = self._tool_functions.get(tool_name)
            if func is None:
                continue
            
            # 解析参数
            parameters = self._parse_function_parameters(func)
            
            # 创建工具定义
            metadata = ToolMetadata(
                name=tool_name,
                description=func.__doc__ or f"Python tool: {tool_name}",
                version="1.0.0",
                author="Python Adapter",
                category="python",
                tags=["python", "script"],
                timeout=config.timeout
            )
            
            definition = ToolDefinition(
                metadata=metadata,
                parameters=parameters
            )
            
            tools.append(definition)
        
        return tools
    
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
    
    async def shutdown(self):
        """关闭适配器"""
        self.logger.info(f"Shutting down Python tool adapter: {self.name}")
        
        # 清理加载的模块
        for module_name in list(self._loaded_modules.keys()):
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        self._loaded_modules.clear()
        self._tool_functions.clear()
        self._tool_classes.clear()
        self._tools.clear()
        
        self._initialized = False
