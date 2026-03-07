"""
知识库搜索工具
基于构建的知识库索引，提供快速搜索功能
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class KnowledgeSearcher:
    """知识库搜索器"""
    
    def __init__(self, index_path: str = "assets/knowledge_index.json"):
        self.index_path = Path(index_path)
        self.index = None
        self.load_index()
    
    def load_index(self):
        """加载知识库索引"""
        if not self.index_path.exists():
            raise FileNotFoundError(f"知识库索引文件不存在: {self.index_path}")
        
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键词搜索"""
        if not self.index:
            return []
        
        keyword = keyword.lower()
        results = []
        
        # 搜索快速索引
        if keyword in self.index.get('quick_search', {}):
            file_paths = self.index['quick_search'][keyword]
            for file_path in file_paths:
                file_info = self.index['files'].get(file_path)
                if file_info:
                    results.append(file_info)
        
        return results
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """根据分类搜索"""
        if not self.index:
            return []
        
        results = []
        categories = self.index.get('categories', {})
        
        if category in categories:
            results = categories[category]
        
        return results
    
    def search_files(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """综合搜索（搜索文件名和内容）"""
        if not self.index:
            return []
        
        query = query.lower()
        results = []
        scored_results = []
        
        # 遍历所有文件
        for file_path, file_info in self.index.get('files', {}).items():
            score = 0
            
            # 文件名匹配
            if query in file_info['name'].lower():
                score += 10
            
            # 关键词匹配
            for keyword in file_info.get('keywords', []):
                if query in keyword.lower():
                    score += 5
                    break
            
            # 分类匹配
            if query in file_info['category'].lower():
                score += 3
            
            if score > 0:
                scored_results.append((score, file_info))
        
        # 按分数排序
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前N个结果
        results = [item[1] for item in scored_results[:max_results]]
        
        return results
    
    def get_file_content(self, file_path: str, max_chars: int = 10000) -> Optional[str]:
        """获取文件内容"""
        base_path = Path("assets")
        full_path = base_path / file_path
        
        if not full_path.exists():
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n... (内容过长，已截断) ..."
            
            return content
        except Exception as e:
            return f"无法读取文件: {str(e)}"
    
    def search_css_selector_rules(self) -> str:
        """搜索CSS选择器相关规则"""
        # 搜索CSS选择器文件
        css_files = self.search_by_category('css选择器')
        
        if not css_files:
            # 尝试搜索关键词
            css_files = self.search_by_keyword('@text')
            css_files = [f for f in css_files if 'css' in f['name'].lower() or '选择器' in f['name'].lower()]
        
        if not css_files:
            return "未找到CSS选择器相关规则"
        
        # 获取第一个CSS文件的内容
        css_file = css_files[0]
        content = self.get_file_content(css_file['path'], max_chars=20000)
        
        return f"文件: {css_file['name']}\n路径: {css_file['path']}\n\n{content}"
    
    def search_real_book_sources(self) -> List[Dict[str, Any]]:
        """搜索真实书源示例"""
        # 搜索真实书源分析文件
        real_sources = self.search_by_category('真实书源分析')
        
        if not real_sources:
            # 尝试搜索其他相关文件
            real_sources = self.search_files('真实书源', max_results=5)
        
        return real_sources
    
    def search_book_source_templates(self) -> List[Dict[str, Any]]:
        """搜索书源模板"""
        templates = self.search_by_category('书源模板')
        
        if not templates:
            templates = self.search_files('模板', max_results=5)
        
        return templates

# 创建全局搜索器实例
_searcher = None

def get_searcher() -> KnowledgeSearcher:
    """获取搜索器实例"""
    global _searcher
    if _searcher is None:
        _searcher = KnowledgeSearcher()
    return _searcher
