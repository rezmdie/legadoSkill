"""
MCP Server Core Implementation
健壮、高性能且完全模块化的模型上下文协议（MCP）服务器实现
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from datetime import datetime
import aiohttp
from aiohttp import web, WSMsgType

from .config_loader import ConfigLoader, get_config_loader
from .system_prompt_injector import SystemPromptInjector, get_prompt_injector
from .tool_registry import ToolRegistry, get_tool_registry, ToolDefinition
from .protocol import JSONRPCProtocolHandler, get_protocol_handler, JSONRPCRequest, JSONRPCResponse
from .async_manager import AsyncTaskManager, get_async_manager
from .logger import get_logger, setup_logging
from .exceptions import MCPError, InternalError, InitializationError
from .adapters import PythonToolAdapter, GoogleAPIAdapter
from .discovery import ToolDiscovery, get_tool_discovery, DiscoveryConfig


class MCPServer:
    """MCP服务器核心类"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        prompt_path: Optional[str] = None
    ):
        """初始化MCP服务器
        
        Args:
            config_path: 配置文件路径
            prompt_path: 系统提示词文件路径
        """
        # 初始化各个组件
        self.config_loader = get_config_loader(config_path)
        self.prompt_injector = get_prompt_injector(prompt_path)
        self.tool_registry = get_tool_registry()
        self.protocol_handler = get_protocol_handler()
        self.async_manager = get_async_manager()
        self.tool_discovery = get_tool_discovery()
        
        self.logger = get_logger("mcp_server")
        
        # 服务器状态
        self._initialized = False
        self._running = False
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        
        # WebSocket连接
        self._websocket_connections: List[web.WebSocketResponse] = []
        
        # 注册MCP协议方法
        self._register_mcp_methods()
    
    def _register_mcp_methods(self):
        """注册MCP协议方法"""
        # 初始化方法
        self.protocol_handler.register_handler("initialize", self._handle_initialize)
        self.protocol_handler.register_handler("initialized", self._handle_initialized)
        
        # 工具方法
        self.protocol_handler.register_handler("tools/list", self._handle_tools_list)
        self.protocol_handler.register_handler("tools/call", self._handle_tools_call)
        self.protocol_handler.register_handler("tools/cancel", self._handle_tools_cancel)
        
        # 资源方法
        self.protocol_handler.register_handler("resources/list", self._handle_resources_list)
        self.protocol_handler.register_handler("resources/read", self._handle_resources_read)
        
        # 提示词方法
        self.protocol_handler.register_handler("prompts/list", self._handle_prompts_list)
        self.protocol_handler.register_handler("prompts/get", self._handle_prompts_get)
        
        # 服务器方法
        self.protocol_handler.register_handler("ping", self._handle_ping)
        self.protocol_handler.register_handler("shutdown", self._handle_shutdown)
    
    async def initialize(self):
        """初始化服务器"""
        if self._initialized:
            return
        
        self.logger.info("Initializing MCP server...")
        
        try:
            # 加载配置
            config = await self.config_loader.load()
            
            # 设置日志
            setup_logging(
                log_dir=config.logging.log_dir,
                level=getattr(logging, config.logging.level),
                json_format=config.logging.json_format
            )
            
            # 加载系统提示词
            await self.prompt_injector.load()
            
            # 启动异步任务管理器
            await self.async_manager.start()
            
            # 初始化工具注册表
            await self.tool_registry.initialize()
            
            # 注册适配器
            await self._register_adapters(config)
            
            # 发现工具
            await self._discover_tools(config)
            
            # 注册内置工具
            await self._register_builtin_tools()
            
            self._initialized = True
            self.logger.info("MCP server initialized successfully")
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize MCP server: {e}")
            raise InitializationError("MCPServer", str(e))
    
    async def _register_adapters(self, config):
        """注册适配器
        
        Args:
            config: 服务器配置
        """
        # 注册Python适配器
        python_config = self.config_loader.get_adapter_config("python")
        if python_config and python_config.enabled:
            python_adapter = PythonToolAdapter(
                name="python",
                config=python_config.config
            )
            self.tool_registry.register_adapter(python_adapter)
            self.logger.info("Python adapter registered")
        
        # 注册Google API适配器
        google_config = self.config_loader.get_adapter_config("google")
        if google_config and google_config.enabled:
            google_adapter = GoogleAPIAdapter(
                name="google",
                config=google_config.config
            )
            self.tool_registry.register_adapter(google_adapter)
            self.logger.info("Google API adapter registered")
    
    async def _discover_tools(self, config):
        """发现工具
        
        Args:
            config: 服务器配置
        """
        # 配置发现路径
        discovery_paths = [
            "assets/projects_new_extracted/src",
            "tools",
            "adapters"
        ]
        
        discovery_config = DiscoveryConfig(
            paths=discovery_paths,
            recursive=True,
            auto_register=True
        )
        
        # 发现工具
        discovered_tools = await self.tool_discovery.discover()
        self.logger.info(f"Discovered {len(discovered_tools)} tools")
    
    async def _register_builtin_tools(self):
        """注册内置工具"""
        # 服务器信息工具
        await self.tool_registry.register(
            definition=ToolDefinition(
                metadata=self._create_tool_metadata(
                    name="server.info",
                    description="Get server information",
                    category="server",
                    tags=["server", "info"]
                )
            ),
            handler=self._builtin_server_info
        )
        
        # 工具列表工具
        await self.tool_registry.register(
            definition=ToolDefinition(
                metadata=self._create_tool_metadata(
                    name="server.tools",
                    description="List available tools",
                    category="server",
                    tags=["server", "tools"]
                )
            ),
            handler=self._builtin_server_tools
        )
        
        # 配置工具
        await self.tool_registry.register(
            definition=ToolDefinition(
                metadata=self._create_tool_metadata(
                    name="server.config",
                    description="Get server configuration",
                    category="server",
                    tags=["server", "config"]
                )
            ),
            handler=self._builtin_server_config
        )
    
    def _create_tool_metadata(self, **kwargs) -> Any:
        """创建工具元数据
        
        Args:
            **kwargs: 元数据参数
            
        Returns:
            工具元数据对象
        """
        from .tool_registry import ToolMetadata
        return ToolMetadata(
            version="1.0.0",
            author="MCP Server",
            timeout=30.0,
            **kwargs
        )
    
    async def _builtin_server_info(self) -> Dict[str, Any]:
        """内置工具：获取服务器信息"""
        return {
            "name": "MCP Server",
            "version": "1.0.0",
            "initialized": self._initialized,
            "running": self._running,
            "tools_count": len(self.tool_registry.list_tools()),
            "connections": len(self._websocket_connections)
        }
    
    async def _builtin_server_tools(self) -> List[Dict[str, Any]]:
        """内置工具：列出可用工具"""
        tools = self.tool_registry.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.metadata.category,
                "tags": tool.metadata.tags
            }
            for tool in tools
        ]
    
    async def _builtin_server_config(self) -> Dict[str, Any]:
        """内置工具：获取服务器配置"""
        return self.config_loader.to_dict()
    
    async def start(self, host: Optional[str] = None, port: Optional[int] = None):
        """启动服务器
        
        Args:
            host: 主机地址
            port: 端口号
        """
        if self._running:
            self.logger.warning("Server is already running")
            return
        
        # 确保已初始化
        if not self._initialized:
            await self.initialize()
        
        # 获取配置
        config = self.config_loader.get()
        server_host = host or config.server.host
        server_port = port or config.server.port
        
        # 创建应用
        self._app = web.Application()
        self._app.add_routes([
            web.get('/', self._handle_http),
            web.post('/', self._handle_http),
            web.get('/ws', self._handle_websocket),
            web.get('/health', self._handle_health),
            web.get('/metrics', self._handle_metrics)
        ])
        
        # 配置CORS
        if config.server.enable_cors:
            self._setup_cors(config.server.cors_origins)
        
        # 创建运行器
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        
        # 创建站点
        self._site = web.TCPSite(self._runner, server_host, server_port)
        await self._site.start()
        
        self._running = True
        self.logger.info(f"MCP server started on {server_host}:{server_port}")
    
    def _setup_cors(self, origins: List[str]):
        """设置CORS
        
        Args:
            origins: 允许的源列表
        """
        async def cors_middleware(request, handler):
            response = await handler(request)
            origin = request.headers.get('Origin', '*')
            
            if '*' in origins or origin in origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            return response
        
        self._app.middlewares.append(cors_middleware)
    
    async def stop(self):
        """停止服务器"""
        if not self._running:
            return
        
        self.logger.info("Stopping MCP server...")
        
        # 关闭WebSocket连接
        for ws in self._websocket_connections:
            await ws.close()
        self._websocket_connections.clear()
        
        # 停止站点
        if self._site:
            await self._site.stop()
            self._site = None
        
        # 清理运行器
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
        
        # 停止异步任务管理器
        await self.async_manager.stop()
        
        # 关闭工具注册表
        await self.tool_registry.shutdown()
        
        self._running = False
        self.logger.info("MCP server stopped")
    
    async def _handle_http(self, request: web.Request) -> web.Response:
        """处理HTTP请求
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 读取请求体
            if request.method == 'POST':
                body = await request.read()
            else:
                body = b'{"method":"ping"}'
            
            # 处理JSON-RPC请求
            response = await self.protocol_handler.handle_request(body)
            
            # 返回响应
            return web.json_response(
                response.to_dict(),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            self.logger.exception(f"Error handling HTTP request: {e}")
            error_response = JSONRPCResponse(error=InternalError(str(e)).to_dict())
            return web.json_response(error_response.to_dict(), status=500)
    
    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """处理WebSocket连接
        
        Args:
            request: HTTP请求
            
        Returns:
            WebSocket响应
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self._websocket_connections.append(ws)
        self.logger.info(f"WebSocket connection established: {request.remote}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # 处理JSON-RPC请求
                    response = await self.protocol_handler.handle_request(msg.data)
                    
                    # 发送响应
                    await ws.send_str(json.dumps(response.to_dict()))
                    
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {ws.exception()}")
                    
        except Exception as e:
            self.logger.exception(f"Error handling WebSocket: {e}")
            
        finally:
            self._websocket_connections.remove(ws)
            self.logger.info(f"WebSocket connection closed: {request.remote}")
        
        return ws
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """处理健康检查请求
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        return web.json_response({
            "status": "healthy" if self._running else "stopped",
            "initialized": self._initialized,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_metrics(self, request: web.Request) -> web.Response:
        """处理指标请求
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        return web.json_response({
            "server": {
                "initialized": self._initialized,
                "running": self._running,
                "connections": len(self._websocket_connections)
            },
            "tasks": self.async_manager.get_stats(),
            "tools": self.tool_registry.get_all_stats()
        })
    
    # MCP协议方法处理器
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理initialize请求"""
        config = self.config_loader.get()
        system_prompt = self.prompt_injector.get()
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": "MCP Server",
                "version": "1.0.0"
            },
            "systemPrompt": self.prompt_injector.format_for_injection() if system_prompt else None
        }
    
    async def _handle_initialized(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理initialized通知"""
        return {}
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理tools/list请求"""
        tools = self.tool_registry.list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            param.name: {
                                "type": param.type,
                                "description": param.description
                            }
                            for param in tool.parameters
                        },
                        "required": [
                            param.name for param in tool.parameters if param.required
                        ]
                    }
                }
                for tool in tools
            ]
        }
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理tools/call请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # 执行工具
        result = await self.tool_registry.execute(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False)
                }
            ]
        }
    
    async def _handle_tools_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理tools/cancel请求"""
        # 实现工具取消逻辑
        return {"success": True}
    
    async def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理resources/list请求"""
        return {"resources": []}
    
    async def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理resources/read请求"""
        return {"contents": []}
    
    async def _handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理prompts/list请求"""
        return {"prompts": []}
    
    async def _handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理prompts/get请求"""
        return {"messages": []}
    
    async def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理ping请求"""
        return {}
    
    async def _handle_shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理shutdown请求"""
        asyncio.create_task(self.stop())
        return {}
    
    async def run_forever(self, host: Optional[str] = None, port: Optional[int] = None):
        """永久运行服务器
        
        Args:
            host: 主机地址
            port: 端口号
        """
        await self.start(host, port)
        
        try:
            # 保持运行
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.stop()
