"""
MCP Server JSON-RPC Protocol Handler Module
严格遵循MCP规范进行JSON-RPC双向通信
"""

import json
import uuid
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime

from .exceptions import (
    ParseError, InvalidRequestError, MethodNotFoundError,
    InvalidParamsError, InternalError, MCPError
)
from .logger import get_logger


@dataclass
class JSONRPCRequest:
    """JSON-RPC请求"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    
    def is_notification(self) -> bool:
        """是否为通知（无id）"""
        return self.id is None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.id is not None:
            result["id"] = self.id
        if self.params is not None:
            result["params"] = self.params
        return result


@dataclass
class JSONRPCResponse:
    """JSON-RPC响应"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def is_error(self) -> bool:
        """是否为错误响应"""
        return self.error is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            result["id"] = self.id
        if self.error is not None:
            result["error"] = self.error
        else:
            result["result"] = self.result
        return result


@dataclass
class JSONRPCBatchResponse:
    """JSON-RPC批量响应"""
    responses: List[JSONRPCResponse] = field(default_factory=list)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return [response.to_dict() for response in self.responses]


class JSONRPCProtocolHandler:
    """JSON-RPC协议处理器"""
    
    def __init__(self):
        """初始化协议处理器"""
        self.logger = get_logger("protocol")
        self._handlers: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []
        self._pending_requests: Dict[Union[str, int], asyncio.Future] = {}
    
    def register_handler(self, method: str, handler: Callable):
        """注册方法处理器
        
        Args:
            method: 方法名
            handler: 处理函数
        """
        self._handlers[method] = handler
        self.logger.debug(f"Handler registered: {method}")
    
    def unregister_handler(self, method: str):
        """注销方法处理器
        
        Args:
            method: 方法名
        """
        if method in self._handlers:
            del self._handlers[method]
            self.logger.debug(f"Handler unregistered: {method}")
    
    def add_middleware(self, middleware: Callable):
        """添加中间件
        
        Args:
            middleware: 中间件函数
        """
        self._middleware.append(middleware)
    
    async def handle_request(self, request_data: Union[str, bytes, Dict, List]) -> Union[JSONRPCResponse, JSONRPCBatchResponse]:
        """处理请求
        
        Args:
            request_data: 请求数据，可以是字符串、字节、字典或列表
            
        Returns:
            JSON-RPC响应或批量响应
        """
        try:
            # 解析请求
            if isinstance(request_data, (str, bytes)):
                request_obj = await self._parse_json(request_data)
            else:
                request_obj = request_data
            
            # 处理批量请求
            if isinstance(request_obj, list):
                return await self._handle_batch_request(request_obj)
            
            # 处理单个请求
            return await self._handle_single_request(request_obj)
            
        except json.JSONDecodeError as e:
            return JSONRPCResponse(error=ParseError(str(e)).to_dict())
        except Exception as e:
            self.logger.exception(f"Error handling request: {e}")
            return JSONRPCResponse(error=InternalError(str(e)).to_dict())
    
    async def _parse_json(self, data: Union[str, bytes]) -> Union[Dict, List]:
        """解析JSON数据
        
        Args:
            data: JSON字符串或字节
            
        Returns:
            解析后的对象
            
        Raises:
            json.JSONDecodeError: JSON解析错误
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return json.loads(data)
    
    async def _handle_single_request(self, request_obj: Dict) -> JSONRPCResponse:
        """处理单个请求
        
        Args:
            request_obj: 请求对象
            
        Returns:
            JSON-RPC响应
        """
        # 验证请求格式
        validation_error = self._validate_request(request_obj)
        if validation_error:
            return JSONRPCResponse(
                id=request_obj.get("id"),
                error=validation_error.to_dict()
            )
        
        # 创建请求对象
        request = JSONRPCRequest(
            jsonrpc=request_obj.get("jsonrpc", "2.0"),
            id=request_obj.get("id"),
            method=request_obj.get("method"),
            params=request_obj.get("params")
        )
        
        # 如果是通知，不返回响应
        if request.is_notification():
            asyncio.create_task(self._execute_method(request))
            return JSONRPCResponse()
        
        # 执行方法并返回响应
        try:
            result = await self._execute_method(request)
            return JSONRPCResponse(id=request.id, result=result)
        except MCPError as e:
            return JSONRPCResponse(id=request.id, error=e.to_dict())
        except Exception as e:
            self.logger.exception(f"Error executing method {request.method}: {e}")
            return JSONRPCResponse(id=request.id, error=InternalError(str(e)).to_dict())
    
    async def _handle_batch_request(self, request_list: List) -> JSONRPCBatchResponse:
        """处理批量请求
        
        Args:
            request_list: 请求列表
            
        Returns:
            JSON-RPC批量响应
        """
        if not request_list:
            return JSONRPCBatchResponse()
        
        responses = []
        tasks = []
        
        for request_obj in request_list:
            # 验证请求格式
            validation_error = self._validate_request(request_obj)
            if validation_error:
                if "id" in request_obj:
                    responses.append(JSONRPCResponse(
                        id=request_obj.get("id"),
                        error=validation_error.to_dict()
                    ))
                continue
            
            request = JSONRPCRequest(
                jsonrpc=request_obj.get("jsonrpc", "2.0"),
                id=request_obj.get("id"),
                method=request_obj.get("method"),
                params=request_obj.get("params")
            )
            
            # 如果是通知，不返回响应
            if request.is_notification():
                asyncio.create_task(self._execute_method(request))
                continue
            
            # 添加到任务列表
            tasks.append(self._execute_method_with_response(request))
        
        # 等待所有任务完成
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    responses.append(JSONRPCResponse(error=InternalError(str(result)).to_dict()))
                else:
                    responses.append(result)
        
        return JSONRPCBatchResponse(responses=responses)
    
    async def _execute_method_with_response(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """执行方法并返回响应
        
        Args:
            request: JSON-RPC请求
            
        Returns:
            JSON-RPC响应
        """
        try:
            result = await self._execute_method(request)
            return JSONRPCResponse(id=request.id, result=result)
        except MCPError as e:
            return JSONRPCResponse(id=request.id, error=e.to_dict())
        except Exception as e:
            self.logger.exception(f"Error executing method {request.method}: {e}")
            return JSONRPCResponse(id=request.id, error=InternalError(str(e)).to_dict())
    
    async def _execute_method(self, request: JSONRPCRequest) -> Any:
        """执行方法
        
        Args:
            request: JSON-RPC请求
            
        Returns:
            方法执行结果
            
        Raises:
            MethodNotFoundError: 方法未找到
            InvalidParamsError: 参数无效
        """
        method = request.method
        
        # 检查方法是否存在
        if method not in self._handlers:
            raise MethodNotFoundError(method)
        
        handler = self._handlers[method]
        
        # 执行中间件
        for middleware in self._middleware:
            try:
                result = await middleware(request)
                if result is not None:
                    return result
            except Exception as e:
                self.logger.error(f"Middleware error: {e}")
                raise
        
        # 准备参数
        params = request.params or {}
        
        # 验证参数
        if not isinstance(params, (dict, list)):
            raise InvalidParamsError("Params must be an object or array")
        
        # 执行处理器
        try:
            if asyncio.iscoroutinefunction(handler):
                if isinstance(params, list):
                    result = await handler(*params)
                else:
                    result = await handler(**params)
            else:
                if isinstance(params, list):
                    result = handler(*params)
                else:
                    result = handler(**params)
            
            return result
            
        except TypeError as e:
            raise InvalidParamsError(str(e))
    
    def _validate_request(self, request_obj: Dict) -> Optional[MCPError]:
        """验证请求格式
        
        Args:
            request_obj: 请求对象
            
        Returns:
            验证错误，如果验证通过则返回None
        """
        # 检查是否为字典
        if not isinstance(request_obj, dict):
            return InvalidRequestError("Request must be an object")
        
        # 检查jsonrpc版本
        jsonrpc = request_obj.get("jsonrpc")
        if jsonrpc != "2.0":
            return InvalidRequestError('jsonrpc must be "2.0"')
        
        # 检查方法
        if "method" not in request_obj:
            return InvalidRequestError("method is required")
        
        if not isinstance(request_obj["method"], str):
            return InvalidRequestError("method must be a string")
        
        # 检查参数
        if "params" in request_obj:
            params = request_obj["params"]
            if not isinstance(params, (dict, list)):
                return InvalidRequestError("params must be an object or array")
        
        # 检查id
        if "id" in request_obj:
            req_id = request_obj["id"]
            if not isinstance(req_id, (str, int, type(None))):
                return InvalidRequestError("id must be a string, number, or null")
        
        return None
    
    def create_request(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> JSONRPCRequest:
        """创建JSON-RPC请求
        
        Args:
            method: 方法名
            params: 参数
            request_id: 请求ID，如果为None则自动生成
            
        Returns:
            JSON-RPC请求
        """
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        return JSONRPCRequest(
            method=method,
            params=params,
            id=request_id
        )
    
    def create_response(
        self,
        result: Any = None,
        error: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> JSONRPCResponse:
        """创建JSON-RPC响应
        
        Args:
            result: 结果
            error: 错误
            request_id: 请求ID
            
        Returns:
            JSON-RPC响应
        """
        return JSONRPCResponse(
            id=request_id,
            result=result,
            error=error
        )
    
    def create_error_response(
        self,
        error: MCPError,
        request_id: Optional[Union[str, int]] = None
    ) -> JSONRPCResponse:
        """创建错误响应
        
        Args:
            error: MCP错误
            request_id: 请求ID
            
        Returns:
            JSON-RPC错误响应
        """
        return JSONRPCResponse(
            id=request_id,
            error=error.to_dict()
        )
    
    def serialize_response(self, response: Union[JSONRPCResponse, JSONRPCBatchResponse]) -> str:
        """序列化响应为JSON字符串
        
        Args:
            response: JSON-RPC响应
            
        Returns:
            JSON字符串
        """
        return json.dumps(response.to_dict(), ensure_ascii=False, indent=None)
    
    def serialize_request(self, request: JSONRPCRequest) -> str:
        """序列化请求为JSON字符串
        
        Args:
            request: JSON-RPC请求
            
        Returns:
            JSON字符串
        """
        return json.dumps(request.to_dict(), ensure_ascii=False, indent=None)


# 全局协议处理器实例
_protocol_handler: Optional[JSONRPCProtocolHandler] = None


def get_protocol_handler() -> JSONRPCProtocolHandler:
    """获取全局协议处理器实例
    
    Returns:
        JSONRPCProtocolHandler实例
    """
    global _protocol_handler
    if _protocol_handler is None:
        _protocol_handler = JSONRPCProtocolHandler()
    return _protocol_handler
