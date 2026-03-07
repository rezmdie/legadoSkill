#!/usr/bin/env python3
"""
会话管理模块
提供会话创建、获取、更新和清理功能
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    def __init__(self, session_timeout: timedelta = timedelta(hours=1)):
        """
        初始化会话管理器
        
        Args:
            session_timeout: 会话超时时间
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout
        self._lock = threading.Lock()
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """
        创建会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话数据字典
        """
        with self._lock:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "context": {},
                "metadata": {}
            }
            logger.info(f"创建会话: {session_id}")
            return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话数据字典，如果不存在返回 None
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session["last_accessed"] = datetime.now()
            return session
    
    def update_session(self, session_id: str, context: Dict[str, Any]) -> bool:
        """
        更新会话上下文
        
        Args:
            session_id: 会话ID
            context: 要更新的上下文数据
        
        Returns:
            True 如果更新成功，False 如果会话不存在
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session["context"].update(context)
                session["last_accessed"] = datetime.now()
                return True
            return False
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话上下文
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话上下文字典，如果不存在返回 None
        """
        session = self.get_session(session_id)
        if session:
            return session.get("context")
        return None
    
    def set_session_context(self, session_id: str, key: str, value: Any) -> bool:
        """
        设置会话上下文中的单个值
        
        Args:
            session_id: 会话ID
            key: 键
            value: 值
        
        Returns:
            True 如果设置成功，False 如果会话不存在
        """
        session = self.get_session(session_id)
        if session:
            session["context"][key] = value
            return True
        return False
    
    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话元数据
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话元数据字典，如果不存在返回 None
        """
        session = self.get_session(session_id)
        if session:
            return session.get("metadata")
        return None
    
    def set_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """
        设置会话元数据
        
        Args:
            session_id: 会话ID
            metadata: 元数据
        
        Returns:
            True 如果设置成功，False 如果会话不存在
        """
        session = self.get_session(session_id)
        if session:
            session["metadata"].update(metadata)
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            True 如果删除成功，False 如果会话不存在
        """
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"删除会话: {session_id}")
                return True
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            清理的会话数量
        """
        with self._lock:
            now = datetime.now()
            expired = [
                sid for sid, session in self.sessions.items()
                if now - session["last_accessed"] > self.session_timeout
            ]
            
            for sid in expired:
                del self.sessions[sid]
                logger.info(f"清理过期会话: {sid}")
            
            return len(expired)
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有会话
        
        Returns:
            所有会话字典
        """
        with self._lock:
            return dict(self.sessions)
    
    def get_session_count(self) -> int:
        """
        获取会话数量
        
        Returns:
            会话数量
        """
        with self._lock:
            return len(self.sessions)
    
    def is_session_valid(self, session_id: str) -> bool:
        """
        检查会话是否有效
        
        Args:
            session_id: 会话ID
        
        Returns:
            True 如果会话有效，False 否则
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        now = datetime.now()
        return now - session["last_accessed"] <= self.session_timeout


# 全局会话管理器实例
_global_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    获取全局会话管理器实例
    
    Returns:
        SessionManager 实例
    """
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = SessionManager()
    return _global_session_manager
