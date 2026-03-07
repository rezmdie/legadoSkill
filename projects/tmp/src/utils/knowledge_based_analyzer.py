"""
基于知识库的自适应分析器
根据知识库中的规则和模式，智能分析HTML结构，提供自适应建议
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from html_structure_analyzer import HTMLStructureAnalyzer, ElementInfo


@dataclass
class KnowledgePattern:
    """知识库模式"""
    name: str
    description: str
    selectors: List[str]
    regex_patterns: List[str]
    xpath_patterns: List[str]
    site_types: List[str]
    confidence: float


@dataclass
class AnalysisResult:
    """分析结果"""
    element_type: str
    recommended_selectors: List[Dict[str, Any]]
    alternative_selectors: List[Dict[str, Any]]
    confidence: float
    knowledge_references: List[str]
    reasoning: str
    warnings: List[str]


class KnowledgeBasedAnalyzer:
    """基于知识库的分析器"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        self.patterns = []
        self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """加载知识库"""
        # 加载常见网站结构模式
        pattern_files = [
            'knowledge/common_patterns.json',
            'knowledge/selector_patterns.json',
            'knowledge/regex_patterns.json',
            'knowledge/site_templates.json'
        ]
        
        for file in pattern_files:
            file_path = os.path.join(self.assets_path, file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns.extend(self._parse_patterns(data))
    
    def _parse_patterns(self, data: Dict) -> List[KnowledgePattern]:
        """解析模式数据"""
        patterns = []
        
        for pattern_name, pattern_data in data.items():
            pattern = KnowledgePattern(
                name=pattern_name,
                description=pattern_data.get('description', ''),
                selectors=pattern_data.get('selectors', []),
                regex_patterns=pattern_data.get('regex_patterns', []),
                xpath_patterns=pattern_data.get('xpath_patterns', []),
                site_types=pattern_data.get('site_types', []),
                confidence=pattern_data.get('confidence', 0.7)
            )
            patterns.append(pattern)
        
        return patterns
    
    def analyze_with_knowledge(
        self,
        html: str,
        element_type: str,
        context: str = ""
    ) -> AnalysisResult:
        """基于知识库分析"""
        
        # 1. 分析HTML结构
        structure_analyzer = HTMLStructureAnalyzer(html)
        structure = structure_analyzer.analyze_structure()
        
        # 2. 查询知识库相关模式
        relevant_patterns = self._find_relevant_patterns(element_type, structure, context)
        
        # 3. 生成推荐方案
        recommended = self._generate_recommendations(structure, relevant_patterns, element_type)
        
        # 4. 生成替代方案
        alternatives = self._generate_alternatives(structure, element_type)
        
        # 5. 计算置信度
        confidence = self._calculate_confidence(recommended, relevant_patterns)
        
        # 6. 生成推理过程
        reasoning = self._generate_reasoning(structure, relevant_patterns, recommended)
        
        # 7. 生成警告
        warnings = self._generate_warnings(structure, recommended)
        
        # 8. 知识库引用
        knowledge_refs = [p.name for p in relevant_patterns]
        
        return AnalysisResult(
            element_type=element_type,
            recommended_selectors=recommended,
            alternative_selectors=alternatives,
            confidence=confidence,
            knowledge_references=knowledge_refs,
            reasoning=reasoning,
            warnings=warnings
        )
    
    def _find_relevant_patterns(
        self,
        element_type: str,
        structure: Dict,
        context: str
    ) -> List[KnowledgePattern]:
        """查找相关模式"""
        relevant = []
        
        for pattern in self.patterns:
            score = 0
            
            # 检查元素类型匹配
            if element_type.lower() in pattern.name.lower():
                score += 0.4
            
            # 检查站点类型匹配
            site_type = structure.get('page_type', '')
            if site_type in pattern.site_types:
                score += 0.3
            
            # 检查上下文匹配
            if context and any(kw in pattern.description.lower() for kw in context.lower().split()):
                score += 0.2
            
            # 检查选择器存在性
            if pattern.selectors:
                score += 0.1
            
            if score >= 0.3:
                relevant.append((pattern, score))
        
        # 按分数排序
        relevant.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in relevant[:5]]
    
    def _generate_recommendations(
        self,
        structure: Dict,
        patterns: List[KnowledgePattern],
        element_type: str
    ) -> List[Dict[str, Any]]:
        """生成推荐方案"""
        recommendations = []
        
        key_elements = structure.get('key_elements', {})
        
        # 根据元素类型获取候选元素
        if element_type == 'title':
            candidates = key_elements.get('titles', [])
        elif element_type == 'list':
            candidates = key_elements.get('lists', [])
        elif element_type == 'content':
            candidates = key_elements.get('containers', [])
        elif element_type == 'image':
            candidates = key_elements.get('images', [])
        elif element_type == 'link':
            candidates = key_elements.get('links', [])
        else:
            candidates = []
        
        # 为每个候选生成推荐
        for i, elem_info in enumerate(candidates[:3]):
            recommendation = {
                'selector': elem_info.selector,
                'type': 'css_selector',
                'confidence': elem_info.confidence,
                'sample_text': elem_info.text[:50],
                'xpath': self._selector_to_xpath(elem_info.selector),
                'pattern_reference': patterns[0].name if patterns else 'none',
                'rank': i + 1
            }
            
            # 如果有知识库模式，添加模式建议
            if patterns:
                pattern = patterns[0]
                if pattern.selectors:
                    recommendation['pattern_selector'] = pattern.selectors[0]
                if pattern.regex_patterns:
                    recommendation['pattern_regex'] = pattern.regex_patterns[0]
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_alternatives(
        self,
        structure: Dict,
        element_type: str
    ) -> List[Dict[str, Any]]:
        """生成替代方案"""
        alternatives = []
        
        key_elements = structure.get('key_elements', {})
        
        if element_type == 'list':
            candidates = key_elements.get('lists', [])
            # 为第4-6个候选生成替代方案
            for i, elem_info in enumerate(candidates[3:6]):
                alternatives.append({
                    'selector': elem_info.selector,
                    'type': 'css_selector',
                    'confidence': elem_info.confidence,
                    'reason': '备用选择器'
                })
        
        # 生成基于class和tag的通用选择器
        semantic_regions = structure.get('semantic_regions', [])
        for region in semantic_regions:
            if element_type.lower() in region['type'].lower():
                alternatives.append({
                    'selector': region['selector'],
                    'type': 'semantic_selector',
                    'confidence': 0.6,
                    'reason': '基于语义区域'
                })
        
        return alternatives[:5]
    
    def _calculate_confidence(
        self,
        recommendations: List[Dict],
        patterns: List[KnowledgePattern]
    ) -> float:
        """计算置信度"""
        if not recommendations:
            return 0.0
        
        # 基础置信度（来自HTML分析）
        base_confidence = recommendations[0].get('confidence', 0.5)
        
        # 模式匹配加分
        if patterns:
            base_confidence += patterns[0].confidence * 0.3
        
        # 推荐数量加分
        if len(recommendations) >= 2:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _generate_reasoning(
        self,
        structure: Dict,
        patterns: List[KnowledgePattern],
        recommendations: List[Dict]
    ) -> str:
        """生成推理过程"""
        reasoning_parts = []
        
        # 1. 页面类型分析
        page_type = structure.get('page_type', 'unknown')
        reasoning_parts.append(f"🔍 页面类型识别: {page_type}")
        
        # 2. 知识库匹配
        if patterns:
            reasoning_parts.append(f"📚 知识库匹配: 找到{len(patterns)}个相关模式")
            for pattern in patterns[:2]:
                reasoning_parts.append(f"   - {pattern.name}: {pattern.description}")
        else:
            reasoning_parts.append("⚠️  知识库匹配: 未找到完全匹配的模式")
        
        # 3. 元素识别
        key_elements = structure.get('key_elements', {})
        reasoning_parts.append(f"🎯 关键元素识别:")
        for elem_type, elems in key_elements.items():
            if elems:
                reasoning_parts.append(f"   - {elem_type}: {len(elems)}个候选")
        
        # 4. 推荐依据
        if recommendations:
            top_rec = recommendations[0]
            reasoning_parts.append(f"✅ 推荐依据:")
            reasoning_parts.append(f"   - 主选器: {top_rec['selector']}")
            reasoning_parts.append(f"   - 置信度: {top_rec['confidence']:.2f}")
            if 'pattern_reference' in top_rec:
                reasoning_parts.append(f"   - 参考模式: {top_rec['pattern_reference']}")
        
        # 5. 内容密度分析
        density = structure.get('content_density', {})
        text_ratio = density.get('text_ratio', 0)
        reasoning_parts.append(f"📊 内容密度分析: 文本比例 {text_ratio:.2%}")
        
        return '\n'.join(reasoning_parts)
    
    def _generate_warnings(
        self,
        structure: Dict,
        recommendations: List[Dict]
    ) -> List[str]:
        """生成警告信息"""
        warnings = []
        
        # 检查推荐数量
        if not recommendations:
            warnings.append("⚠️  未能找到合适的推荐选择器，可能需要手动分析")
        
        # 检查置信度
        if recommendations and recommendations[0].get('confidence', 0) < 0.6:
            warnings.append("⚠️  推荐选择器置信度较低，建议验证后再使用")
        
        # 检查内容密度
        density = structure.get('content_density', {})
        link_density = density.get('link_density', 0)
        if link_density > 0.5:
            warnings.append("⚠️  页面链接密度过高，可能影响内容提取准确性")
        
        # 检查导航结构
        nav_structure = structure.get('navigation_structure', {})
        nav_count = nav_structure.get('nav_count', 0)
        if nav_count > 5:
            warnings.append("⚠️  页面导航结构复杂，可能需要更精确的选择器")
        
        return warnings
    
    def _selector_to_xpath(self, css_selector: str) -> str:
        """CSS选择器转XPath（简化版）"""
        # 简化的转换逻辑
        xpath = css_selector
        
        # class转attribute
        xpath = re.sub(r'\.([\w-]+)', r'[@class="\1"]', xpath)
        
        # id转attribute
        xpath = re.sub(r'#([\w-]+)', r'[@id="\1"]', xpath)
        
        # tag保持不变
        xpath = '//' + xpath if not xpath.startswith('/') else xpath
        
        return xpath
    
    def get_knowledge_suggestions(
        self,
        html: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """获取知识库建议"""
        suggestions = []
        
        # 分析HTML结构
        structure_analyzer = HTMLStructureAnalyzer(html)
        structure = structure_analyzer.analyze_structure()
        
        # 根据查询匹配知识库模式
        for pattern in self.patterns:
            relevance = 0
            
            # 关键词匹配
            query_words = query.lower().split()
            pattern_desc = pattern.description.lower()
            pattern_name = pattern.name.lower()
            
            for word in query_words:
                if word in pattern_name:
                    relevance += 0.4
                if word in pattern_desc:
                    relevance += 0.2
            
            if relevance > 0.3:
                suggestions.append({
                    'pattern': pattern.name,
                    'description': pattern.description,
                    'selectors': pattern.selectors,
                    'regex_patterns': pattern.regex_patterns,
                    'xpath_patterns': pattern.xpath_patterns,
                    'relevance': relevance
                })
        
        suggestions.sort(key=lambda x: x['relevance'], reverse=True)
        return suggestions[:5]
