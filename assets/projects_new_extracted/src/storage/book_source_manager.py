"""
Legado书源存储管理器
用于管理本地存储的书源
"""

import os
import json
import sqlite3
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# 获取工作区路径
WORKSPACE_PATH = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
DATA_DIR = os.path.join(WORKSPACE_PATH, "data")
BOOK_SOURCE_DIR = os.path.join(DATA_DIR, "book_sources")
DB_PATH = os.path.join(DATA_DIR, "book_sources.db")


class BookSourceManager:
    """书源存储管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self._ensure_directories()
        self._init_database()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(BOOK_SOURCE_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建书源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_source_url TEXT UNIQUE NOT NULL,
                book_source_name TEXT,
                book_source_group TEXT,
                category TEXT,
                file_path TEXT,
                created_at TEXT,
                updated_at TEXT,
                last_sync_time TEXT,
                enabled INTEGER DEFAULT 1,
                metadata TEXT
            )
        ''')
        
        # 创建同步日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_url TEXT,
                category TEXT,
                action TEXT,
                count INTEGER,
                status TEXT,
                error_message TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_source(self, source: dict, category: str = "书源") -> bool:
        """
        添加书源到数据库
        
        参数:
            source: 书源数据
            category: 分类名称
        
        返回:
            是否成功
        """
        try:
            book_source_url = source.get("bookSourceUrl", "")
            if not book_source_url:
                return False
            
            # 生成文件路径
            file_hash = hashlib.md5(book_source_url.encode('utf-8')).hexdigest()
            file_path = os.path.join(BOOK_SOURCE_DIR, category, f"{file_hash}.json")
            
            # 保存文件
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(source, f, ensure_ascii=False, indent=2)
            
            # 更新数据库
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO book_sources 
                (book_source_url, book_source_name, book_source_group, category, file_path, 
                 created_at, updated_at, last_sync_time, enabled, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ''', (
                book_source_url,
                source.get("bookSourceName", ""),
                source.get("bookSourceGroup", ""),
                category,
                file_path,
                now,
                now,
                now,
                json.dumps(source, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"添加书源失败: {e}")
            return False
    
    def get_source(self, book_source_url: str) -> Optional[dict]:
        """
        获取书源
        
        参数:
            book_source_url: 书源URL
        
        返回:
            书源数据
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metadata, file_path FROM book_sources 
                WHERE book_source_url = ? AND enabled = 1
            ''', (book_source_url,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                metadata, file_path = row
                if metadata:
                    return json.loads(metadata)
                elif file_path and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"获取书源失败: {e}")
            return None
    
    def list_sources(self, category: str = None, enabled: bool = True) -> List[dict]:
        """
        列出书源
        
        参数:
            category: 分类名称（可选）
            enabled: 是否只显示启用的书源
        
        返回:
            书源列表
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT book_source_url, book_source_name, book_source_group, 
                           category, enabled, updated_at
                    FROM book_sources 
                    WHERE category = ? AND enabled = ?
                    ORDER BY updated_at DESC
                ''', (category, 1 if enabled else 0))
            else:
                cursor.execute('''
                    SELECT book_source_url, book_source_name, book_source_group, 
                           category, enabled, updated_at
                    FROM book_sources 
                    WHERE enabled = ?
                    ORDER BY category, updated_at DESC
                ''', (1 if enabled else 0,))
            
            rows = cursor.fetchall()
            conn.close()
            
            sources = []
            for row in rows:
                sources.append({
                    "bookSourceUrl": row[0],
                    "bookSourceName": row[1],
                    "bookSourceGroup": row[2],
                    "category": row[3],
                    "enabled": bool(row[4]),
                    "updatedAt": row[5]
                })
            
            return sources
            
        except Exception as e:
            print(f"列出书源失败: {e}")
            return []
    
    def delete_source(self, book_source_url: str) -> bool:
        """
        删除书源
        
        参数:
            book_source_url: 书源URL
        
        返回:
            是否成功
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 获取文件路径
            cursor.execute('SELECT file_path FROM book_sources WHERE book_source_url = ?', (book_source_url,))
            row = cursor.fetchone()
            
            if row:
                file_path = row[0]
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            
            # 删除数据库记录
            cursor.execute('DELETE FROM book_sources WHERE book_source_url = ?', (book_source_url,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"删除书源失败: {e}")
            return False
    
    def update_source(self, book_source_url: str, source: dict) -> bool:
        """
        更新书源
        
        参数:
            book_source_url: 书源URL
            source: 新的书源数据
        
        返回:
            是否成功
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE book_sources 
                SET book_source_name = ?, book_source_group = ?, updated_at = ?, metadata = ?
                WHERE book_source_url = ?
            ''', (
                source.get("bookSourceName", ""),
                source.get("bookSourceGroup", ""),
                now,
                json.dumps(source, ensure_ascii=False),
                book_source_url
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"更新书源失败: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """
        获取统计信息
        
        返回:
            统计信息字典
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 总书源数
            cursor.execute('SELECT COUNT(*) FROM book_sources WHERE enabled = 1')
            total_count = cursor.fetchone()[0]
            
            # 按分类统计
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM book_sources 
                WHERE enabled = 1 
                GROUP BY category
                ORDER BY count DESC
            ''')
            category_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 最近同步时间
            cursor.execute('''
                SELECT MAX(last_sync_time) FROM book_sources
            ''')
            last_sync = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "totalCount": total_count,
                "categoryStats": category_stats,
                "lastSyncTime": last_sync,
                "storagePath": BOOK_SOURCE_DIR,
                "databasePath": DB_PATH
            }
            
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {
                "totalCount": 0,
                "categoryStats": {},
                "lastSyncTime": None,
                "storagePath": BOOK_SOURCE_DIR,
                "databasePath": DB_PATH
            }
    
    def log_sync(self, subscription_url: str, category: str, action: str, 
                 count: int, status: str, error_message: str = None):
        """
        记录同步日志
        
        参数:
            subscription_url: 订阅源URL
            category: 分类
            action: 操作类型
            count: 数量
            status: 状态
            error_message: 错误信息
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO sync_logs 
                (subscription_url, category, action, count, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (subscription_url, category, action, count, status, error_message, now))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"记录同步日志失败: {e}")
    
    def get_sync_logs(self, limit: int = 100) -> List[dict]:
        """
        获取同步日志
        
        参数:
            limit: 返回数量限制
        
        返回:
            日志列表
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT subscription_url, category, action, count, status, 
                       error_message, created_at
                FROM sync_logs 
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            logs = []
            for row in rows:
                logs.append({
                    "subscriptionUrl": row[0],
                    "category": row[1],
                    "action": row[2],
                    "count": row[3],
                    "status": row[4],
                    "errorMessage": row[5],
                    "createdAt": row[6]
                })
            
            return logs
            
        except Exception as e:
            print(f"获取同步日志失败: {e}")
            return []


# 全局实例
_manager = None


def get_manager() -> BookSourceManager:
    """获取书源管理器实例"""
    global _manager
    if _manager is None:
        _manager = BookSourceManager()
    return _manager
