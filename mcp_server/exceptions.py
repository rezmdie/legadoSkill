"""
MCP Server Exception Handling Module
定义所有自定义异常类，提供完善的错误处理机制
"""

from typing import Optional, Any, Dict
import json


class MCPError(Exception):
    """MCP服务器基础异常类"""
    
    def __init__(self, message: str, code: int = -32603, data: Optional[Any] = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为JSON-RPC错误格式"""
        error_dict = {
            "code": self.code,
            "message": self.message
        }
        if self.data is not None:
            error_dict["data"] = self.data
        return error_dict


class ParseError(MCPError):
    """JSON解析错误"""
    
    def __init__(self, message: str = "Invalid JSON", data: Optional[Any] = None):
        super().__init__(message, code=-32700, data=data)


class InvalidRequestError(MCPError):
    """无效请求错误"""
    
    def __init__(self, message: str = "Invalid Request", data: Optional[Any] = None):
        super().__init__(message, code=-32600, data=data)


class MethodNotFoundError(MCPError):
    """方法未找到错误"""
    
    def __init__(self, method: str, data: Optional[Any] = None):
        message = f"Method not found: {method}"
        super().__init__(message, code=-32601, data=data)


class InvalidParamsError(MCPError):
    """无效参数错误"""
    
    def __init__(self, message: str = "Invalid params", data: Optional[Any] = None):
        super().__init__(message, code=-32602, data=data)


class InternalError(MCPError):
    """内部错误"""
    
    def __init__(self, message: str = "Internal error", data: Optional[Any] = None):
        super().__init__(message, code=-32603, data=data)


class ConfigError(MCPError):
    """配置加载错误"""
    
    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(message, code=-32000, data=data)


class ToolNotFoundError(MCPError):
    """工具未找到错误"""
    
    def __init__(self, tool_name: str, data: Optional[Any] = None):
        message = f"Tool not found: {tool_name}"
        super().__init__(message, code=-32001, data=data)


class ToolExecutionError(MCPError):
    """工具执行错误"""
    
    def __init__(self, tool_name: str, message: str, data: Optional[Any] = None):
        full_message = f"Tool execution failed [{tool_name}]: {message}"
        super().__init__(full_message, code=-32002, data=data)


class AdapterError(MCPError):
    """适配器错误"""
    
    def __init__(self, adapter_name: str, message: str, data: Optional[Any] = None):
        full_message = f"Adapter error [{adapter_name}]: {message}"
        super().__init__(full_message, code=-32003, data=data)


class ConnectionError(MCPError):
    """连接错误"""
    
    def __init__(self, service: str, message: str, data: Optional[Any] = None):
        full_message = f"Connection error [{service}]: {message}"
        super().__init__(full_message, code=-32004, data=data)


class TimeoutError(MCPError):
    """超时错误"""
    
    def __init__(self, operation: str, timeout: float, data: Optional[Any] = None):
        message = f"Operation timeout [{operation}]: {timeout}s"
        super().__init__(message, code=-32005, data=data)


class ValidationError(MCPError):
    """验证错误"""
    
    def __init__(self, field: str, message: str, data: Optional[Any] = None):
        full_message = f"Validation error [{field}]: {message}"
        super().__init__(full_message, code=-32006, data=data)


class RateLimitError(MCPError):
    """速率限制错误"""
    
    def __init__(self, service: str, limit: int, data: Optional[Any] = None):
        message = f"Rate limit exceeded [{service}]: {limit} requests"
        super().__init__(message, code=-32007, data=data)


class AuthenticationError(MCPError):
    """认证错误"""
    
    def __init__(self, service: str, message: str = "Authentication failed", data: Optional[Any] = None):
        full_message = f"Authentication error [{service}]: {message}"
        super().__init__(full_message, code=-32008, data=data)


class InitializationError(MCPError):
    """初始化错误"""
    
    def __init__(self, component: str, message: str, data: Optional[Any] = None):
        full_message = f"Initialization error [{component}]: {message}"
        super().__init__(full_message, code=-32009, data=data)
