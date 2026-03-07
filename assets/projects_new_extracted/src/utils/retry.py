#!/usr/bin/env python3
"""
重试机制模块
提供异步和同步的重试装饰器
"""
import asyncio
import time
from typing import Callable, TypeVar, Any, Optional, List, Type
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryError(Exception):
    """重试失败异常"""
    pass


async def retry_async(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Optional[List[Type[Exception]]] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None
) -> T:
    """
    异步重试函数
    
    Args:
        func: 要重试的异步函数
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 退避因子（每次重试延迟时间乘以这个因子）
        exceptions: 需要重试的异常类型列表（None 表示所有异常）
        on_retry: 重试时的回调函数
    
    Returns:
        函数执行结果
    
    Raises:
        RetryError: 所有重试都失败时抛出
    """
    if exceptions is None:
        exceptions = [Exception]
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except tuple(exceptions) as e:
            last_exception = e
            
            if attempt < max_retries:
                wait_time = delay * (backoff ** attempt)
                logger.warning(
                    f"重试 {attempt + 1}/{max_retries}: {func.__name__} 失败，"
                    f"等待 {wait_time:.2f} 秒后重试。错误: {e}"
                )
                
                if on_retry:
                    on_retry(attempt + 1, e)
                
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"重试失败: {func.__name__} 在 {max_retries} 次重试后仍然失败。"
                    f"最后错误: {e}"
                )
                raise RetryError(
                    f"函数 {func.__name__} 在 {max_retries} 次重试后仍然失败"
                ) from e


def retry_sync(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Optional[List[Type[Exception]]] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None
) -> T:
    """
    同步重试函数
    
    Args:
        func: 要重试的同步函数
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 退避因子
        exceptions: 需要重试的异常类型列表
        on_retry: 重试时的回调函数
    
    Returns:
        函数执行结果
    
    Raises:
        RetryError: 所有重试都失败时抛出
    """
    if exceptions is None:
        exceptions = [Exception]
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except tuple(exceptions) as e:
            last_exception = e
            
            if attempt < max_retries:
                wait_time = delay * (backoff ** attempt)
                logger.warning(
                    f"重试 {attempt + 1}/{max_retries}: {func.__name__} 失败，"
                    f"等待 {wait_time:.2f} 秒后重试。错误: {e}"
                )
                
                if on_retry:
                    on_retry(attempt + 1, e)
                
                time.sleep(wait_time)
            else:
                logger.error(
                    f"重试失败: {func.__name__} 在 {max_retries} 次重试后仍然失败。"
                    f"最后错误: {e}"
                )
                raise RetryError(
                    f"函数 {func.__name__} 在 {max_retries} 次重试后仍然失败"
                ) from e


def async_retry_decorator(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Optional[List[Type[Exception]]] = None
):
    """
    异步重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 退避因子
        exceptions: 需要重试的异常类型列表
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions
            )
        return wrapper
    return decorator


def sync_retry_decorator(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Optional[List[Type[Exception]]] = None
):
    """
    同步重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 退避因子
        exceptions: 需要重试的异常类型列表
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return retry_sync(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions
            )
        return wrapper
    return decorator


# 便捷装饰器别名
retry = sync_retry_decorator
aretry = async_retry_decorator
