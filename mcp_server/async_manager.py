"""
MCP Server Async Task Manager Module
提供高性能的异步任务管理功能，支持并发处理和任务调度
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List, Coroutine
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import heapq

from .exceptions import TimeoutError as MCPTimeoutError
from .logger import get_logger


@dataclass
class AsyncTask:
    """异步任务"""
    id: str
    coro: Coroutine
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout: Optional[float] = None
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: 'AsyncTask') -> bool:
        """用于优先级队列比较"""
        return self.priority < other.priority


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    result: Any = None
    error: Optional[Exception] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(
        self,
        max_concurrent: int = 100,
        default_timeout: float = 60.0,
        enable_priority: bool = True
    ):
        """初始化异步任务管理器
        
        Args:
            max_concurrent: 最大并发任务数
            default_timeout: 默认超时时间（秒）
            enable_priority: 是否启用优先级队列
        """
        self.max_concurrent = max_concurrent
        self.default_timeout = default_timeout
        self.enable_priority = enable_priority
        
        self.logger = get_logger("async_manager")
        
        # 任务存储
        self._pending_tasks: List[AsyncTask] = []
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, TaskResult] = {}
        self._task_futures: Dict[str, asyncio.Future] = {}
        
        # 信号量控制并发
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # 统计信息
        self._stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "timeout_tasks": 0
        }
        
        # 后台任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """启动任务管理器"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("Async task manager started")
    
    async def stop(self):
        """停止任务管理器"""
        if not self._running:
            return
        
        self._running = False
        
        # 取消所有运行中的任务
        for task_id, task in self._running_tasks.items():
            task.cancel()
        
        # 等待所有任务完成
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
        
        # 取消清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Async task manager stopped")
    
    async def submit(
        self,
        coro: Coroutine,
        task_id: Optional[str] = None,
        timeout: Optional[float] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """提交异步任务
        
        Args:
            coro: 协程对象
            task_id: 任务ID，如果为None则自动生成
            timeout: 超时时间（秒）
            priority: 优先级（数字越小优先级越高）
            metadata: 任务元数据
            
        Returns:
            任务ID
        """
        if task_id is None:
            task_id = f"task_{datetime.utcnow().timestamp()}_{len(self._stats)}"
        
        # 创建任务对象
        task = AsyncTask(
            id=task_id,
            coro=coro,
            timeout=timeout or self.default_timeout,
            priority=priority,
            metadata=metadata or {}
        )
        
        # 创建Future用于等待结果
        future = asyncio.Future()
        self._task_futures[task_id] = future
        
        # 添加到待处理队列
        if self.enable_priority:
            heapq.heappush(self._pending_tasks, task)
        else:
            self._pending_tasks.append(task)
        
        # 更新统计
        self._stats["total_tasks"] += 1
        
        # 启动任务处理
        asyncio.create_task(self._process_task(task))
        
        self.logger.debug(f"Task submitted: {task_id}")
        return task_id
    
    async def _process_task(self, task: AsyncTask):
        """处理任务
        
        Args:
            task: 异步任务
        """
        async with self._semaphore:
            start_time = datetime.utcnow()
            
            try:
                # 创建包装任务
                wrapper_task = asyncio.create_task(self._execute_with_timeout(task))
                self._running_tasks[task.id] = wrapper_task
                
                # 等待任务完成
                result = await wrapper_task
                
                # 记录成功结果
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                task_result = TaskResult(
                    task_id=task.id,
                    result=result,
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms
                )
                
                self._completed_tasks[task.id] = task_result
                self._stats["completed_tasks"] += 1
                
                # 设置Future结果
                if task.id in self._task_futures:
                    self._task_futures[task.id].set_result(task_result)
                
                self.logger.debug(f"Task completed: {task.id} ({duration_ms:.2f}ms)")
                
            except asyncio.TimeoutError:
                # 记录超时
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                task_result = TaskResult(
                    task_id=task.id,
                    error=MCPTimeoutError(task.id, task.timeout),
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms
                )
                
                self._completed_tasks[task.id] = task_result
                self._stats["timeout_tasks"] += 1
                
                # 设置Future异常
                if task.id in self._task_futures:
                    self._task_futures[task.id].set_exception(task_result.error)
                
                self.logger.warning(f"Task timeout: {task.id}")
                
            except Exception as e:
                # 记录错误
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                task_result = TaskResult(
                    task_id=task.id,
                    error=e,
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms
                )
                
                self._completed_tasks[task.id] = task_result
                self._stats["failed_tasks"] += 1
                
                # 设置Future异常
                if task.id in self._task_futures:
                    self._task_futures[task.id].set_exception(e)
                
                self.logger.error(f"Task failed: {task.id} - {e}")
                
            finally:
                # 清理
                if task.id in self._running_tasks:
                    del self._running_tasks[task.id]
    
    async def _execute_with_timeout(self, task: AsyncTask) -> Any:
        """执行任务并处理超时
        
        Args:
            task: 异步任务
            
        Returns:
            任务结果
        """
        return await asyncio.wait_for(task.coro, timeout=task.timeout)
    
    async def wait(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 等待超时时间
            
        Returns:
            任务结果
        """
        if task_id not in self._task_futures:
            raise ValueError(f"Task not found: {task_id}")
        
        future = self._task_futures[task_id]
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            raise MCPTimeoutError(f"wait_task:{task_id}", timeout or self.default_timeout)
    
    async def wait_all(self, task_ids: List[str], timeout: Optional[float] = None) -> List[TaskResult]:
        """等待多个任务完成
        
        Args:
            task_ids: 任务ID列表
            timeout: 等待超时时间
            
        Returns:
            任务结果列表
        """
        futures = []
        for task_id in task_ids:
            if task_id in self._task_futures:
                futures.append(self._task_futures[task_id])
        
        if not futures:
            return []
        
        try:
            results = await asyncio.wait_for(asyncio.gather(*futures, return_exceptions=True), timeout=timeout)
            return [r for r in results if isinstance(r, TaskResult)]
        except asyncio.TimeoutError:
            raise MCPTimeoutError("wait_all", timeout or self.default_timeout)
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果（不等待）
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果，如果任务未完成则返回None
        """
        return self._completed_tasks.get(task_id)
    
    def cancel(self, task_id: str) -> bool:
        """取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        # 取消运行中的任务
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            del self._running_tasks[task_id]
            return True
        
        # 从待处理队列中移除
        for i, task in enumerate(self._pending_tasks):
            if task.id == task_id:
                self._pending_tasks.pop(i)
                if self.enable_priority:
                    heapq.heapify(self._pending_tasks)
                return True
        
        return False
    
    def get_status(self, task_id: str) -> Optional[str]:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态：pending, running, completed, failed, timeout
        """
        # 检查待处理队列
        for task in self._pending_tasks:
            if task.id == task_id:
                return "pending"
        
        # 检查运行中的任务
        if task_id in self._running_tasks:
            return "running"
        
        # 检查已完成的任务
        if task_id in self._completed_tasks:
            result = self._completed_tasks[task_id]
            if result.error:
                if isinstance(result.error, MCPTimeoutError):
                    return "timeout"
                return "failed"
            return "completed"
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            **self._stats,
            "pending_tasks": len(self._pending_tasks),
            "running_tasks": len(self._running_tasks),
            "completed_tasks_stored": len(self._completed_tasks)
        }
    
    async def _cleanup_loop(self):
        """清理循环，定期清理已完成的任务"""
        while self._running:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                
                # 清理超过1小时的已完成任务
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                to_remove = []
                
                for task_id, result in self._completed_tasks.items():
                    if result.completed_at and result.completed_at < cutoff_time:
                        to_remove.append(task_id)
                
                for task_id in to_remove:
                    del self._completed_tasks[task_id]
                    if task_id in self._task_futures:
                        del self._task_futures[task_id]
                
                if to_remove:
                    self.logger.debug(f"Cleaned up {len(to_remove)} old task results")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int, time_window: float = 60.0):
        """初始化速率限制器
        
        Args:
            max_requests: 最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取许可，如果超过速率限制则等待"""
        async with self._lock:
            now = datetime.utcnow()
            
            # 移除时间窗口外的请求
            cutoff_time = now - timedelta(seconds=self.time_window)
            self._requests = [r for r in self._requests if r > cutoff_time]
            
            # 检查是否超过限制
            if len(self._requests) >= self.max_requests:
                # 计算需要等待的时间
                oldest_request = self._requests[0]
                wait_time = (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            # 记录请求
            self._requests.append(now)
    
    def get_remaining(self) -> int:
        """获取剩余请求数
        
        Returns:
            剩余请求数
        """
        now = datetime.utcnow()
        cutoff_time = now - timedelta(seconds=self.time_window)
        recent_requests = [r for r in self._requests if r > cutoff_time]
        return self.max_requests - len(recent_requests)


# 全局异步任务管理器实例
_async_manager: Optional[AsyncTaskManager] = None


def get_async_manager(
    max_concurrent: int = 100,
    default_timeout: float = 60.0,
    enable_priority: bool = True
) -> AsyncTaskManager:
    """获取全局异步任务管理器实例
    
    Args:
        max_concurrent: 最大并发任务数
        default_timeout: 默认超时时间
        enable_priority: 是否启用优先级队列
        
    Returns:
        AsyncTaskManager实例
    """
    global _async_manager
    if _async_manager is None:
        _async_manager = AsyncTaskManager(max_concurrent, default_timeout, enable_priority)
    return _async_manager
