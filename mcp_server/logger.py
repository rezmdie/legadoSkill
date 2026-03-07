"""
MCP Server Logging Module
提供结构化、高性能的日志记录功能
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import traceback


class MCPLogger:
    """MCP服务器日志记录器"""
    
    _instances: Dict[str, 'MCPLogger'] = {}
    
    def __new__(cls, name: str = "mcp_server", *args, **kwargs):
        """单例模式，确保每个名称只有一个logger实例"""
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
        return cls._instances[name]
    
    def __init__(
        self,
        name: str = "mcp_server",
        log_dir: Optional[str] = None,
        level: int = logging.INFO,
        console_output: bool = True,
        file_output: bool = True,
        json_format: bool = False,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
            level: 日志级别
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            json_format: 是否使用JSON格式
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
        """
        if hasattr(self, '_initialized'):
            return
        
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()
        
        self.json_format = json_format
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        
        # 创建日志目录
        if file_output:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置格式化器
        formatter = self._get_formatter()
        
        # 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 文件处理器
        if file_output:
            # 主日志文件
            main_log_file = self.log_dir / f"{name}.log"
            file_handler = RotatingFileHandler(
                main_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # 错误日志文件
            error_log_file = self.log_dir / f"{name}_error.log"
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
        
        self._initialized = True
    
    def _get_formatter(self) -> logging.Formatter:
        """获取日志格式化器"""
        if self.json_format:
            return JSONFormatter()
        else:
            return logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def debug(self, message: str, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """记录一般信息"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """记录错误信息"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message, extra=kwargs)
    
    def log_tool_call(self, tool_name: str, params: Dict[str, Any], result: Any = None, error: Optional[str] = None):
        """记录工具调用"""
        log_data = {
            "event": "tool_call",
            "tool": tool_name,
            "params": params,
            "timestamp": datetime.utcnow().isoformat()
        }
        if result is not None:
            log_data["result"] = result
        if error:
            log_data["error"] = error
            self.error(f"Tool call failed: {tool_name}", **log_data)
        else:
            self.info(f"Tool called: {tool_name}", **log_data)
    
    def log_request(self, request_id: str, method: str, params: Optional[Dict] = None):
        """记录请求"""
        self.info(
            f"Request received: {method}",
            request_id=request_id,
            method=method,
            params=params
        )
    
    def log_response(self, request_id: str, success: bool, duration_ms: float):
        """记录响应"""
        self.info(
            f"Response sent: {request_id}",
            request_id=request_id,
            success=success,
            duration_ms=duration_ms
        )


class JSONFormatter(logging.Formatter):
    """JSON格式化器，用于结构化日志"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加额外字段
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str = "mcp_server", **kwargs) -> MCPLogger:
    """获取日志记录器实例
    
    Args:
        name: 日志记录器名称
        **kwargs: 传递给MCPLogger的参数
        
    Returns:
        MCPLogger实例
    """
    return MCPLogger(name, **kwargs)


def setup_logging(
    log_dir: str = "logs",
    level: int = logging.INFO,
    json_format: bool = False,
    **kwargs
) -> None:
    """设置全局日志配置
    
    Args:
        log_dir: 日志目录
        level: 日志级别
        json_format: 是否使用JSON格式
        **kwargs: 其他配置参数
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    
    # 创建日志目录
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 设置格式化器
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    main_log_file = Path(log_dir) / "mcp_server.log"
    file_handler = RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
