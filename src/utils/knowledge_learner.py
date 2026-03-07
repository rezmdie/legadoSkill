"""
知识学习引擎
读取、解析、学习assets目录下的所有知识资源
将知识结构化存储，支持智能检索和应用
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from bs4 import BeautifulSoup


@dataclass
class KnowledgeEntry:
    """知识条目"""
    id: str
    source_file: str
    type: str  # rule, pattern, example, explanation, technique
    category: str  # css, xpath, regex, bookinfo, toc, content
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)  # 相关知识ID
    confidence: float = 1.0
    usage_count: int = 0
    success_count: int = 0


@dataclass
class BookSourceKnowledge:
    """书源知识"""
    source_name: str
    source_url: str
    rules: Dict[str, str]
    patterns: Dict[str, List[str]]
    techniques: List[str]
    tags: List[str]


class KnowledgeLearner:
    """知识学习引擎"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        self.knowledge_entries: Dict[str, KnowledgeEntry] = {}
        self.book_sources: Dict[str, BookSourceKnowledge] = {}
        self.patterns: Dict[str, List[str]] = {}
        self.selectors: Dict[str, List[str]] = {}
        
        # 学习统计
        self.learning_stats = {
            'total_files': 0,
            'learned_entries': 0,
            'book_sources': 0,
            'patterns': 0,
            'selectors': 0
        }
    
    def learn_all(self) -> Dict[str, Any]:
        """学习所有知识资源"""
        print("=" * 60)
        print("🧠 开始学习知识库...")
        print("=" * 60)
        
        # 1. 学习书源规则文档
        self._learn_rule_documents()
        
        # 2. 学习CSS选择器规则
        self._learn_css_rules()
        
        # 3. 学习书源知识库
        self._learn_book_sources()
        
        # 4. 学习参考文件
        self._learn_reference_files()
        
        # 5. 学习技术文档
        self._learn_technique_docs()
        
        # 6. 构建知识关联
        self._build_knowledge_relations()
        
        # 7. 保存学习结果
        self._save_learning_results()
        
        print("=" * 60)
        print("✅ 知识学习完成！")
        print("=" * 60)
        print(f"📊 学习统计:")
        print(f"   - 处理文件: {self.learning_stats['total_files']}")
        print(f"   - 学习条目: {self.learning_stats['learned_entries']}")
        print(f"   - 书源数量: {self.learning_stats['book_sources']}")
        print(f"   - 模式数量: {self.learning_stats['patterns']}")
        print(f"   - 选择器数量: {self.learning_stats['selectors']}")
        
        return self.learning_stats
    
    def _learn_rule_documents(self):
        """学习书源规则文档"""
        print("\n📚 学习书源规则文档...")
        
        rule_docs = [
            '书源规则：从入门到入土.md',
            'legado_knowledge_base.md',
            '订阅源规则：从入门到再入门 (4).md',
            '订阅源规则帮助.txt'
        ]
        
        for doc_name in rule_docs:
            file_path = os.path.join(self.assets_path, doc_name)
            if os.path.exists(file_path):
                self._parse_rule_document(doc_name, file_path)
                self.learning_stats['total_files'] += 1
    
    def _learn_css_rules(self):
        """学习CSS选择器规则"""
        print("\n🎨 学习CSS选择器规则...")
        
        file_path = os.path.join(self.assets_path, 'css选择器规则.txt')
        if os.path.exists(file_path):
            self._parse_css_rules(file_path)
            self.learning_stats['total_files'] += 1
    
    def _learn_book_sources(self):
        """学习书源知识库"""
        print("\n📖 学习书源知识库...")
        
        kb_path = os.path.join(self.assets_path, 'knowledge_base', 'book_sources')
        if os.path.exists(kb_path):
            for file_name in os.listdir(kb_path):
                if file_name.endswith('.md'):
                    file_path = os.path.join(kb_path, file_name)
                    self._parse_book_source(file_name, file_path)
                    self.learning_stats['book_sources'] += 1
                    self.learning_stats['total_files'] += 1
    
    def _learn_reference_files(self):
        """学习参考文件"""
        print("\n📝 学习参考文件...")
        
        ref_files = [
            '3a.json参考.txt',
            'Legado书源驯兽师加载器.txt',
            'TapManga.json参考.txt',
            'cf登录检测【半自动化】.js参考.txt',
            '喜漫漫画.json参考.txt',
            '霹雳书屋.json参考.txt'
        ]
        
        for ref_file in ref_files:
            file_path = os.path.join(self.assets_path, ref_file)
            if os.path.exists(file_path):
                self._parse_reference_file(ref_file, file_path)
                self.learning_stats['total_files'] += 1
    
    def _learn_technique_docs(self):
        """学习技术文档"""
        print("\n🔧 学习技术文档...")
        
        technique_files = [
            '方法-JS扩展类.md',
            '方法-加密解密.md',
            '方法-登录检查JS.md',
            '阅读js ai提示词文档基本通用(注：我使用的版本为lcy的).txt',
            '阅读教程AI提取精华，人工润色 已矫正过.txt'
        ]
        
        for tech_file in technique_files:
            file_path = os.path.join(self.assets_path, tech_file)
            if os.path.exists(file_path):
                self._parse_technique_doc(tech_file, file_path)
                self.learning_stats['total_files'] += 1
    
    def _parse_rule_document(self, doc_name: str, file_path: str):
        """解析规则文档"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按标题分割内容
        sections = re.split(r'^#+\s+(.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                title = sections[i].strip()
                section_content = sections[i + 1].strip()
                
                if title and section_content:
                    # 创建知识条目
                    entry_id = f"rule_{doc_name}_{i}"
                    entry = KnowledgeEntry(
                        id=entry_id,
                        source_file=doc_name,
                        type='explanation',
                        category='general',
                        title=title,
                        content=section_content,
                        tags=['rule', 'explanation', doc_name.replace('.', '_')]
                    )
                    
                    # 提取代码示例
                    code_blocks = re.findall(r'```(?:json|js|javascript|python)?\n(.*?)```', section_content, re.DOTALL)
                    entry.examples = code_blocks[:5]
                    
                    self.knowledge_entries[entry_id] = entry
                    self.learning_stats['learned_entries'] += 1
    
    def _parse_css_rules(self, file_path: str):
        """解析CSS选择器规则"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按标题分割
        sections = re.split(r'^#+\s+(.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                title = sections[i].strip()
                section_content = sections[i + 1].strip()
                
                if title and section_content:
                    entry_id = f"css_{i}"
                    entry = KnowledgeEntry(
                        id=entry_id,
                        source_file='css选择器规则.txt',
                        type='explanation',
                        category='css',
                        title=title,
                        content=section_content,
                        tags=['css', 'selector', title]
                    )
                    
                    # 提取选择器示例
                    selector_matches = re.findall(r'([.#][a-zA-Z_-][a-zA-Z0-9_-]*)', section_content)
                    entry.examples = selector_matches[:10]
                    
                    self.knowledge_entries[entry_id] = entry
                    self.learning_stats['learned_entries'] += 1
                    
                    # 添加到选择器库
                    for selector in selector_matches:
                        if selector not in self.selectors:
                            self.selectors[selector] = []
                        self.selectors[selector].append(entry_id)
                    
                    self.learning_stats['selectors'] += len(selector_matches)
    
    def _parse_book_source(self, file_name: str, file_path: str):
        """解析书源"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取书源名称和URL
        name_match = re.search(r'sourceName[:：]\s*[\'"](.+?)[\'"]', content)
        url_match = re.search(r'bookSourceUrl[:：]\s*[\'"](.+?)[\'"]', content)
        
        source_name = name_match.group(1) if name_match else file_name.replace('.md', '')
        source_url = url_match.group(1) if url_match else ''
        
        # 提取规则
        rules = {}
        rule_patterns = {
            'searchUrl': r'searchUrl[:：]\s*[\'"](.+?)[\'"]',
            'ruleBookInfo': r'ruleBookInfo[:：]\s*(\{.*?\})',
            'ruleToc': r'ruleToc[:：]\s*(\{.*?\})',
            'ruleContent': r'ruleContent[:：]\s*(\{.*?\})',
        }
        
        for rule_type, pattern in rule_patterns.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                rules[rule_type] = match.group(1)
        
        # 提取选择器模式
        patterns = {}
        selector_pattern = r'[\'"]([.#][a-zA-Z_-][a-zA-Z0-9_\-\[\]="' '"]*)[\'"]'
        
        for rule_type, rule_value in rules.items():
            selectors = re.findall(selector_pattern, rule_value)
            if selectors:
                patterns[rule_type] = selectors
        
        # 创建书源知识
        book_source = BookSourceKnowledge(
            source_name=source_name,
            source_url=source_url,
            rules=rules,
            patterns=patterns,
            techniques=[],
            tags=[source_name.split('_')[0]]
        )
        
        self.book_sources[file_name] = book_source
        
        # 为每个选择器创建知识条目
        for rule_type, selectors in patterns.items():
            for selector in selectors:
                entry_id = f"book_{file_name}_{rule_type}_{selector.replace('.', '_').replace('#', '_')}"
                entry = KnowledgeEntry(
                    id=entry_id,
                    source_file=file_name,
                    type='pattern',
                    category=rule_type.replace('rule', '').lower(),
                    title=f"{source_name} - {rule_type}",
                    content=selector,
                    tags=['book_source', rule_type, source_name],
                    examples=[selector],
                    confidence=0.9
                )
                
                self.knowledge_entries[entry_id] = entry
                self.learning_stats['learned_entries'] += 1
                
                # 添加到模式库
                if selector not in self.patterns:
                    self.patterns[selector] = []
                self.patterns[selector].append(entry_id)
                self.learning_stats['patterns'] += 1
    
    def _parse_reference_file(self, file_name: str, file_path: str):
        """解析参考文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取JSON配置
        json_matches = re.findall(r'\{[^{}]*"[^"]+"\s*:\s*[^{}]+\}', content)
        
        for match in json_matches:
            try:
                config = json.loads(match)
                entry_id = f"ref_{file_name}_{len(self.knowledge_entries)}"
                
                entry = KnowledgeEntry(
                    id=entry_id,
                    source_file=file_name,
                    type='example',
                    category='configuration',
                    title=f"{file_name} 配置示例",
                    content=json.dumps(config, ensure_ascii=False, indent=2),
                    tags=['reference', 'example', file_name],
                    examples=[json.dumps(config, ensure_ascii=False)]
                )
                
                self.knowledge_entries[entry_id] = entry
                self.learning_stats['learned_entries'] += 1
            except:
                continue
    
    def _parse_technique_doc(self, file_name: str, file_path: str):
        """解析技术文档"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按标题分割
        sections = re.split(r'^#+\s+(.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                title = sections[i].strip()
                section_content = sections[i + 1].strip()
                
                if title and section_content:
                    entry_id = f"tech_{file_name}_{i}"
                    entry = KnowledgeEntry(
                        id=entry_id,
                        source_file=file_name,
                        type='technique',
                        category='technique',
                        title=title,
                        content=section_content,
                        tags=['technique', file_name, title]
                    )
                    
                    # 提取代码示例
                    code_blocks = re.findall(r'```(?:js|javascript|python)?\n(.*?)```', section_content, re.DOTALL)
                    entry.examples = code_blocks[:3]
                    
                    self.knowledge_entries[entry_id] = entry
                    self.learning_stats['learned_entries'] += 1
    
    def _build_knowledge_relations(self):
        """构建知识关联"""
        print("\n🔗 构建知识关联...")
        
        # 根据标签关联知识
        for entry_id, entry in self.knowledge_entries.items():
            for tag in entry.tags:
                for other_id, other_entry in self.knowledge_entries.items():
                    if entry_id != other_id and tag in other_entry.tags:
                        if other_id not in entry.related:
                            entry.related.append(other_id)
    
    def _save_learning_results(self):
        """保存学习结果"""
        print("\n💾 保存学习结果...")
        
        # 创建学习统计目录
        stats_dir = os.path.join(self.assets_path, 'knowledge_base', 'learning_stats')
        os.makedirs(stats_dir, exist_ok=True)
        
        # 保存学习统计
        stats_file = os.path.join(stats_dir, 'learning_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'learning_stats': self.learning_stats,
                'knowledge_count': len(self.knowledge_entries),
                'book_source_count': len(self.book_sources),
                'pattern_count': len(self.patterns),
                'selector_count': len(self.selectors)
            }, f, ensure_ascii=False, indent=2)
        
        # 保存知识索引
        index_file = os.path.join(stats_dir, 'knowledge_index.json')
        index = {
            'entries': {
                entry_id: {
                    'id': entry.id,
                    'source_file': entry.source_file,
                    'type': entry.type,
                    'category': entry.category,
                    'title': entry.title,
                    'tags': entry.tags
                }
                for entry_id, entry in self.knowledge_entries.items()
            },
            'book_sources': {
                name: {
                    'source_name': bs.source_name,
                    'source_url': bs.source_url,
                    'tags': bs.tags
                }
                for name, bs in self.book_sources.items()
            },
            'patterns': list(self.patterns.keys()),
            'selectors': list(self.selectors.keys())
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgeEntry]:
        """搜索知识"""
        query_lower = query.lower()
        results = []
        
        for entry in self.knowledge_entries.values():
            # 类别过滤
            if category and entry.category != category:
                continue
            
            # 计算相关性
            score = 0
            
            # 标题匹配
            if query_lower in entry.title.lower():
                score += 3
            
            # 标签匹配
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 2
            
            # 内容匹配
            if query_lower in entry.content.lower():
                score += 1
            
            if score > 0:
                results.append((entry, score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [entry for entry, score in results[:limit]]
    
    def get_similar_selectors(self, html: str, limit: int = 10) -> List[Dict[str, Any]]:
        """根据HTML获取相似选择器"""
        similar = []
        
        # 提取HTML中的class和id
        class_matches = re.findall(r'class=["\']([^"\']+)["\']', html)
        id_matches = re.findall(r'id=["\']([^"\']+)["\']', html)
        
        # 从知识库中查找相似的选择器
        for class_name in class_matches:
            selector = f".{class_name}"
            if selector in self.patterns:
                for entry_id in self.patterns[selector]:
                    entry = self.knowledge_entries.get(entry_id)
                    if entry:
                        similar.append({
                            'selector': selector,
                            'entry_id': entry_id,
                            'source': entry.source_file,
                            'title': entry.title,
                            'confidence': entry.confidence,
                            'examples': entry.examples
                        })
        
        # 按置信度排序
        similar.sort(key=lambda x: x['confidence'], reverse=True)
        
        return similar[:limit]
    
    def get_knowledge_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        """根据标签获取知识"""
        return [
            entry for entry in self.knowledge_entries.values()
            if tag in entry.tags
        ]
