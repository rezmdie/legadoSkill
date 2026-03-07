#!/usr/bin/env python3
"""
Legado知识库索引系统
自动扫描并索引assets目录下的所有知识文件
"""

import os
import json
from typing import Dict, List, Any
from pathlib import Path

class KnowledgeIndexer:
    """知识库索引器"""
    
    def __init__(self, base_path: str = "/workspace/projects/assets"):
        self.base_path = Path(base_path)
        self.index = {
            "metadata": {
                "version": "1.0",
                "last_updated": "",
                "total_files": 0,
                "total_size": 0
            },
            "categories": {},
            "files": {},
            "quick_search": {}
        }
    
    def scan_directory(self) -> List[Path]:
        """扫描assets目录，返回所有知识文件"""
        knowledge_files = []
        
        # 扫描所有txt和md文件
        for ext in ['*.txt', '*.md']:
            for file_path in self.base_path.rglob(ext):
                # 跳过一些不需要的文件
                if any(skip in str(file_path) for skip in ['.erb', 'node_modules', '.git']):
                    continue
                
                # 只扫描根目录和特定子目录的文件
                relative_path = file_path.relative_to(self.base_path)
                parts = relative_path.parts
                
                # 只扫描根目录文件或knowledge_base目录的文件
                if len(parts) == 1 or parts[0] == 'knowledge_base':
                    knowledge_files.append(file_path)
        
        return sorted(knowledge_files)
    
    def categorize_file(self, file_path: Path) -> str:
        """将文件分类"""
        file_name = file_path.name.lower()
        
        # 根据文件名分类
        if 'css' in file_name or '选择器' in file_name:
            return 'css选择器'
        elif '规则' in file_name or 'rule' in file_name:
            return '书源规则'
        elif '模板' in file_name or 'template' in file_name:
            return '书源模板'
        elif '知识' in file_name or 'knowledge' in file_name:
            return '知识库'
        elif '真实书源' in file_name or '分析' in file_name:
            return '真实书源分析'
        elif 'json' in file_name and '参考' in file_name:
            return 'JSON参考'
        elif 'js' in file_name or 'javascript' in file_name:
            return 'JavaScript'
        else:
            return '其他'
    
    def extract_keywords(self, content: str, max_keywords: int = 50) -> List[str]:
        """从内容中提取关键词"""
        # 简单的关键词提取
        keywords = []
        
        # CSS选择器关键词
        css_keywords = ['@text', '@html', '@ownText', '@textNode', '@href', '@src',
                       'class.', '#id', 'tag.', 'css:', 'nth-child', 'first-child', 'last-child']
        
        # 书源规则关键词
        rule_keywords = ['ruleSearch', 'ruleToc', 'ruleContent', 'ruleBookInfo',
                        'bookList', 'name', 'author', 'intro', 'coverUrl', 'bookUrl',
                        'chapterList', 'chapterName', 'chapterUrl', 'content',
                        'nextContentUrl', 'nextTocUrl']
        
        # 合并关键词
        all_keywords = css_keywords + rule_keywords
        
        for keyword in all_keywords:
            if keyword in content:
                keywords.append(keyword)
                if len(keywords) >= max_keywords:
                    break
        
        return keywords
    
    def index_file(self, file_path: Path) -> Dict[str, Any]:
        """索引单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = file_path.relative_to(self.base_path)
            category = self.categorize_file(file_path)
            keywords = self.extract_keywords(content)
            
            # 计算文件大小（KB）
            file_size = file_path.stat().st_size / 1024
            
            file_info = {
                "path": str(relative_path),
                "absolute_path": str(file_path),
                "name": file_path.name,
                "size_kb": round(file_size, 2),
                "category": category,
                "keywords": keywords,
                "line_count": len(content.split('\n')),
                "preview": content[:500]  # 前500字符预览
            }
            
            return file_info
        
        except Exception as e:
            print(f"❌ 无法索引文件 {file_path}: {e}")
            return None
    
    def build_index(self) -> Dict[str, Any]:
        """构建完整索引"""
        print("🔍 开始扫描assets目录...")
        
        # 扫描所有文件
        files = self.scan_directory()
        print(f"📂 找到 {len(files)} 个知识文件")
        
        # 索引每个文件
        indexed_files = []
        for file_path in files:
            print(f"📄 索引: {file_path.name}")
            file_info = self.index_file(file_path)
            if file_info:
                indexed_files.append(file_info)
        
        # 按分类组织
        categories = {}
        for file_info in indexed_files:
            category = file_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(file_info)
        
        # 构建快速搜索索引
        quick_search = {}
        for file_info in indexed_files:
            for keyword in file_info['keywords']:
                if keyword not in quick_search:
                    quick_search[keyword] = []
                quick_search[keyword].append(file_info['path'])
        
        # 更新元数据
        total_size = sum(f['size_kb'] for f in indexed_files)
        self.index['metadata'].update({
            'last_updated': json.dumps({"timestamp": "auto"}),
            'total_files': len(indexed_files),
            'total_size_kb': round(total_size, 2)
        })
        
        # 保存索引
        self.index['categories'] = categories
        self.index['files'] = {f['path']: f for f in indexed_files}
        self.index['quick_search'] = quick_search
        
        print(f"✅ 索引完成！共 {len(indexed_files)} 个文件")
        return self.index
    
    def save_index(self, output_path: str = "assets/knowledge_index.json"):
        """保存索引到文件"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
        
        print(f"💾 索引已保存到: {output_file}")
    
    def print_summary(self):
        """打印索引摘要"""
        print("\n" + "=" * 80)
        print("📊 知识库索引摘要")
        print("=" * 80)
        print(f"总文件数: {self.index['metadata']['total_files']}")
        print(f"总大小: {self.index['metadata']['total_size_kb']} KB")
        print(f"更新时间: {self.index['metadata']['last_updated']}")
        
        print("\n📁 分类统计:")
        for category, files in self.index['categories'].items():
            print(f"  {category}: {len(files)} 个文件")
        
        print("\n🔑 关键词统计 (Top 20):")
        sorted_keywords = sorted(self.index['quick_search'].items(), 
                                 key=lambda x: len(x[1]), reverse=True)
        for keyword, files in sorted_keywords[:20]:
            print(f"  {keyword}: {len(files)} 个文件")

def main():
    """主函数"""
    indexer = KnowledgeIndexer()
    
    # 构建索引
    indexer.build_index()
    
    # 保存索引
    indexer.save_index()
    
    # 打印摘要
    indexer.print_summary()
    
    return indexer.index

if __name__ == "__main__":
    main()
