#!/usr/bin/env python3
"""
工具调用追踪模块
记录和追踪所有工具的调用历史
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class ToolTracker:
    """工具调用追踪器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化追踪器
        
        Args:
            max_history: 最大历史记录数
        """
        self.call_history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self._current_call: Optional[Dict[str, Any]] = None
    
    def start_call(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        开始记录工具调用
        
        Args:
            tool_name: 工具名称
            args: 工具参数
        
        Returns:
            调用ID
        """
        call_id = f"{tool_name}_{int(time.time() * 1000)}"
        self._current_call = {
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "args": args,
            "start_time": time.time(),
            "status": "running"
        }
        return call_id
    
    def end_call(self, call_id: str, result: Any, error: Optional[Exception] = None):
        """
        结束记录工具调用
        
        Args:
            call_id: 调用ID
            result: 调用结果
            error: 错误信息（如果有）
        """
        if self._current_call and self._current_call.get("call_id") == call_id:
            self._current_call["end_time"] = time.time()
            self._current_call["duration"] = (
                self._current_call["end_time"] - self._current_call["start_time"]
            )
            self._current_call["result"] = result
            self._current_call["error"] = str(error) if error else None
            self._current_call["status"] = "error" if error else "success"
            
            # 添加到历史记录
            self.call_history.append(self._current_call)
            
            # 限制历史记录数量
            if len(self.call_history) > self.max_history:
                self.call_history = self.call_history[-self.max_history:]
            
            self._current_call = None
    
    def track_call(self, tool_name: str, args: Dict[str, Any], result: Any, duration: float):
        """
        一次性记录工具调用（简化版）
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            result: 调用结果
            duration: 调用耗时（秒）
        """
        self.call_history.append({
            "call_id": f"{tool_name}_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "args": args,
            "result": result,
            "duration": duration,
            "status": "success"
        })
        
        # 限制历史记录数量
        if len(self.call_history) > self.max_history:
            self.call_history = self.call_history[-self.max_history:]
    
    def get_history(self, tool_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取调用历史
        
        Args:
            tool_name: 工具名称（可选，如果指定则只返回该工具的历史）
            limit: 返回的最大记录数
        
        Returns:
            调用历史列表
        """
        history = self.call_history
        
        if tool_name:
            history = [c for c in history if c["tool_name"] == tool_name]
        
        return history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取调用统计信息
        
        Returns:
            统计信息字典
        """
        if not self.call_history:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "average_duration": 0,
                "tool_counts": {}
            }
        
        successful = [c for c in self.call_history if c["status"] == "success"]
        failed = [c for c in self.call_history if c["status"] == "error"]
        
        tool_counts = {}
        for call in self.call_history:
            tool_name = call["tool_name"]
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        total_duration = sum(c.get("duration", 0) for c in successful)
        avg_duration = total_duration / len(successful) if successful else 0
        
        return {
            "total_calls": len(self.call_history),
            "successful_calls": len(successful),
            "failed_calls": len(failed),
            "average_duration": avg_duration,
            "tool_counts": tool_counts
        }
    
    def clear_history(self):
        """清除所有历史记录"""
        self.call_history = []
    
    def export_history(self, tool_name: Optional[str] = None) -> str:
        """
        导出调用历史为JSON字符串
        
        Args:
            tool_name: 工具名称（可选）
        
        Returns:
            JSON字符串
        """
        history = self.get_history(tool_name)
        return json.dumps(history, ensure_ascii=False, indent=2)


# 全局追踪器实例
_global_tracker: Optional[ToolTracker] = None


def get_tool_tracker() -> ToolTracker:
    """
    获取全局工具追踪器实例
    
    Returns:
        ToolTracker 实例
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ToolTracker()
    return _global_tracker


def track_tool_call(tool_name: str, args: Dict[str, Any], result: Any, duration: float):
    """
    便捷函数：记录工具调用
    
    Args:
        tool_name: 工具名称
        args: 工具参数
        result: 调用结果
        duration: 调用耗时（秒）
    """
    tracker = get_tool_tracker()
    tracker.track_call(tool_name, args, result, duration)
