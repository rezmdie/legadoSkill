"""
防止内容被截断的工具类

提供文件分页读取、内容分段输出等功能
"""

import os
from typing import List, Dict, Optional
import json


class ContentSplitter:
    """内容分割器，用于处理大文件的分页读取和分段输出"""
    
    def __init__(self, default_chunk_size: int = 200, default_output_size: int = 4000):
        """
        初始化内容分割器
        
        Args:
            default_chunk_size: 默认分页大小（行数）
            default_output_size: 默认输出大小（字符数）
        """
        self.default_chunk_size = default_chunk_size
        self.default_output_size = default_output_size
    
    def read_file_in_chunks(self, file_path: str, chunk_size: Optional[int] = None) -> List[Dict]:
        """
        分页读取文件
        
        Args:
            file_path: 文件路径
            chunk_size: 每页的行数，默认使用 default_chunk_size
        
        Returns:
            分页数据列表，每个元素包含：
            - chunk_id: 页码（从1开始）
            - total_chunks: 总页数
            - lines: 该页的行列表
            - start_line: 起始行号（从1开始）
            - end_line: 结束行号
        """
        if chunk_size is None:
            chunk_size = self.default_chunk_size
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        if total_lines == 0:
            return []
        
        chunks = []
        for start in range(0, total_lines, chunk_size):
            end = min(start + chunk_size, total_lines)
            chunk = lines[start:end]
            chunks.append({
                'chunk_id': start // chunk_size + 1,
                'total_chunks': (total_lines + chunk_size - 1) // chunk_size,
                'lines': chunk,
                'start_line': start + 1,
                'end_line': end,
                'content': ''.join(chunk)
            })
        
        return chunks
    
    def read_file_paginated(self, file_path: str, page: int = 1, chunk_size: Optional[int] = None) -> Dict:
        """
        读取指定页的文件内容
        
        Args:
            file_path: 文件路径
            page: 页码（从1开始）
            chunk_size: 每页的行数，默认使用 default_chunk_size
        
        Returns:
            指定页的数据，包含：
            - chunk_id: 页码
            - total_chunks: 总页数
            - lines: 该页的行列表
            - start_line: 起始行号
            - end_line: 结束行号
            - content: 该页的文本内容
            - has_prev: 是否有上一页
            - has_next: 是否有下一页
        """
        chunks = self.read_file_in_chunks(file_path, chunk_size)
        
        if not chunks:
            return {
                'chunk_id': 0,
                'total_chunks': 0,
                'lines': [],
                'start_line': 0,
                'end_line': 0,
                'content': '',
                'has_prev': False,
                'has_next': False
            }
        
        if page < 1 or page > len(chunks):
            raise ValueError(f"页码超出范围: {page}，总页数: {len(chunks)}")
        
        chunk = chunks[page - 1]
        chunk['has_prev'] = page > 1
        chunk['has_next'] = page < len(chunks)
        
        return chunk
    
    def output_in_chunks(self, content: str, chunk_size: Optional[int] = None) -> List[Dict]:
        """
        将内容分段输出
        
        Args:
            content: 要分割的内容
            chunk_size: 每段的字符数，默认使用 default_output_size
        
        Returns:
            分段数据列表，每个元素包含：
            - chunk_id: 段号（从1开始）
            - total_chunks: 总段数
            - content: 该段的内容
            - is_last: 是否是最后一段
            - start_pos: 起始位置
            - end_pos: 结束位置
        """
        if chunk_size is None:
            chunk_size = self.default_output_size
        
        total_length = len(content)
        if total_length == 0:
            return []
        
        chunks = []
        for start in range(0, total_length, chunk_size):
            end = min(start + chunk_size, total_length)
            chunk = content[start:end]
            chunks.append({
                'chunk_id': start // chunk_size + 1,
                'total_chunks': (total_length + chunk_size - 1) // chunk_size,
                'content': chunk,
                'is_last': end == total_length,
                'start_pos': start,
                'end_pos': end
            })
        
        return chunks
    
    def format_chunk_output(self, chunk: Dict, title: str = "") -> str:
        """
        格式化分段输出
        
        Args:
            chunk: 分段数据
            title: 标题
        
        Returns:
            格式化后的字符串
        """
        output = ""
        if title:
            output += f"{title}\n"
        
        output += f"=== 第{chunk['chunk_id']}/{chunk['total_chunks']}部分 ===\n\n"
        output += chunk['content']
        
        if not chunk.get('is_last', True):
            output += "\n\n[内容未完，回复\"继续\"查看下一部分]\n"
        
        return output
    
    def format_file_page_output(self, chunk: Dict, file_name: str = "") -> str:
        """
        格式化文件分页输出
        
        Args:
            chunk: 分页数据
            file_name: 文件名
        
        Returns:
            格式化后的字符串
        """
        output = ""
        if file_name:
            output += f"文档名称：{file_name}\n"
        
        output += f"总页数：{chunk['total_chunks']}页\n"
        output += f"当前页：第{chunk['chunk_id']}页（行{chunk['start_line']}-{chunk['end_line']}）\n\n"
        output += f"=== 第{chunk['chunk_id']}/{chunk['total_chunks']}页 ===\n\n"
        output += chunk['content']
        
        if chunk.get('has_next', False):
            output += "\n\n[内容未完，回复\"继续\"查看下一页]\n"
        
        return output
    
    def get_file_summary(self, file_path: str) -> Dict:
        """
        获取文件摘要信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件摘要信息，包含：
            - path: 文件路径
            - name: 文件名
            - size: 文件大小（字节）
            - total_lines: 总行数
            - total_pages: 总页数（使用默认分页大小）
            - encoding: 文件编码
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # 检测文件编码
        encoding = 'utf-8'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    f.read()
                encoding = 'gbk'
            except:
                encoding = 'unknown'
        
        # 统计行数
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            total_lines = len(f.readlines())
        
        total_pages = (total_lines + self.default_chunk_size - 1) // self.default_chunk_size
        
        return {
            'path': file_path,
            'name': file_name,
            'size': file_size,
            'total_lines': total_lines,
            'total_pages': total_pages,
            'encoding': encoding
        }


class KnowledgeIndexSearcher:
    """知识库索引搜索器"""
    
    def __init__(self, index_path: str = 'assets/knowledge_index.json'):
        """
        初始化知识库索引搜索器
        
        Args:
            index_path: 索引文件路径
        """
        self.index_path = index_path
        self.index = None
        self._load_index()
    
    def _load_index(self):
        """加载索引文件"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {
                'version': '1.0',
                'total_files': 0,
                'total_size': 0,
                'categories': {},
                'files': []
            }
    
    def search(self, query: str, category: str = "", limit: int = 10) -> List[Dict]:
        """
        搜索知识库索引
        
        Args:
            query: 搜索关键词
            category: 可选，限定分类
            limit: 最大返回结果数
        
        Returns:
            搜索结果列表
        """
        if not self.index:
            return []
        
        results = []
        query_lower = query.lower()
        
        # 遍历所有分类
        categories = self.index.get('categories', {})
        
        for cat_name, files in categories.items():
            # 按分类筛选
            if category and cat_name != category:
                continue
            
            # 确保files是一个列表
            if not isinstance(files, list):
                continue
            
            for file in files:
                # 按关键词匹配
                matched = False
                for keyword in file.get('keywords', []):
                    if query_lower in keyword.lower():
                        matched = True
                        break
                
                # 按文件名匹配
                if not matched and query_lower in file.get('name', '').lower():
                    matched = True
                
                if matched:
                    results.append(file)
        
        return results[:limit]
    
    def get_file_by_path(self, file_path: str) -> Optional[Dict]:
        """
        根据路径获取文件信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件信息，如果不存在则返回None
        """
        if not self.index:
            return None
        
        # 遍历所有分类
        categories = self.index.get('categories', {})
        
        for cat_name, files in categories.items():
            if not isinstance(files, list):
                continue
            
            for file in files:
                if file.get('path', '') == file_path or file.get('absolute_path', '') == file_path:
                    return file
        
        return None
    
    def get_files_by_category(self, category: str) -> List[Dict]:
        """
        获取指定分类的所有文件
        
        Args:
            category: 分类名称
        
        Returns:
            文件列表
        """
        if not self.index:
            return []
        
        files = self.index.get('categories', {}).get(category, [])
        return files if isinstance(files, list) else []
    
    def get_categories(self) -> Dict:
        """
        获取所有分类及其统计信息
        
        Returns:
            分类字典
        """
        if not self.index:
            return {}
        
        categories = {}
        for cat_name, files in self.index.get('categories', {}).items():
            if isinstance(files, list):
                categories[cat_name] = {
                    'count': len(files),
                    'size': sum(f.get('size', 0) for f in files)
                }
        
        return categories
    
    def get_summary(self) -> Dict:
        """
        获取索引摘要信息
        
        Returns:
            摘要信息
        """
        if not self.index:
            return {}
        
        return {
            'version': self.index.get('version', ''),
            'total_files': self.index.get('total_files', 0),
            'total_size': self.index.get('total_size', 0),
            'categories_count': len(self.index.get('categories', {}))
        }


# 全局实例（单例模式）
_content_splitter = None
_knowledge_index_searcher = None


def get_content_splitter() -> ContentSplitter:
    """获取内容分割器实例"""
    global _content_splitter
    if _content_splitter is None:
        _content_splitter = ContentSplitter()
    return _content_splitter


def get_knowledge_index_searcher() -> KnowledgeIndexSearcher:
    """获取知识库索引搜索器实例"""
    global _knowledge_index_searcher
    if _knowledge_index_searcher is None:
        _knowledge_index_searcher = KnowledgeIndexSearcher()
    return _knowledge_index_searcher
