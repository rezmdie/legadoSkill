"""
知识应用引擎
将学到的知识应用到实际分析中
支持智能匹配、知识推荐、规则生成
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from knowledge_learner import KnowledgeLearner, KnowledgeEntry


@dataclass
class KnowledgeApplication:
    """知识应用结果"""
    applied_knowledge: List[KnowledgeEntry]
    reasoning: str
    recommendations: List[Dict[str, Any]]
    confidence: float
    source_files: List[str]


class KnowledgeApplier:
    """知识应用引擎"""
    
    def __init__(self, learner: KnowledgeLearner):
        self.learner = learner
        self.application_history = []
    
    def apply_knowledge_to_html(
        self,
        html: str,
        element_type: str,
        context: Optional[Dict] = None
    ) -> KnowledgeApplication:
        """
        将知识应用到HTML分析
        
        Args:
            html: HTML内容
            element_type: 元素类型 (title, author, content, list等)
            context: 上下文信息
        
        Returns:
            知识应用结果
        """
        context = context or {}
        
        # 1. 获取相似选择器
        similar_selectors = self.learner.get_similar_selectors(html, limit=10)
        
        # 2. 搜索相关知识
        related_knowledge = self._search_related_knowledge(
            element_type,
            html,
            context
        )
        
        # 3. 分析HTML结构
        html_analysis = self._analyze_html_structure(html)
        
        # 4. 应用知识生成建议
        recommendations = self._generate_recommendations(
            similar_selectors,
            related_knowledge,
            html_analysis,
            element_type
        )
        
        # 5. 生成推理过程
        reasoning = self._generate_reasoning(
            similar_selectors,
            related_knowledge,
            html_analysis,
            element_type
        )
        
        # 6. 计算置信度
        confidence = self._calculate_confidence(
            recommendations,
            related_knowledge
        )
        
        # 7. 收集源文件
        source_files = list({
            entry.source_file
            for entry in related_knowledge
        })
        
        # 创建应用结果
        application = KnowledgeApplication(
            applied_knowledge=related_knowledge,
            reasoning=reasoning,
            recommendations=recommendations,
            confidence=confidence,
            source_files=source_files
        )
        
        # 记录应用历史
        self.application_history.append({
            'html_length': len(html),
            'element_type': element_type,
            'applied_count': len(related_knowledge),
            'confidence': confidence
        })
        
        return application
    
    def _search_related_knowledge(
        self,
        element_type: str,
        html: str,
        context: Dict
    ) -> List[KnowledgeEntry]:
        """搜索相关知识"""
        related = []
        
        # 搜索关键词
        keywords = [
            element_type,
            context.get('query', ''),
            context.get('field', '')
        ]
        
        # 按类别搜索
        category_map = {
            'title': 'bookinfo',
            'author': 'bookinfo',
            'cover': 'bookinfo',
            'intro': 'bookinfo',
            'list': 'toc',
            'content': 'content',
            'chapter': 'toc'
        }
        
        category = category_map.get(element_type, 'general')
        
        # 搜索知识库
        for keyword in keywords:
            if keyword:
                results = self.learner.search_knowledge(
                    keyword,
                    category=category,
                    limit=5
                )
                
                for result in results:
                    if result not in related:
                        related.append(result)
        
        # 限制数量
        return related[:10]
    
    def _analyze_html_structure(self, html: str) -> Dict[str, Any]:
        """分析HTML结构"""
        analysis = {
            'classes': set(),
            'ids': set(),
            'tags': set(),
            'structures': []
        }
        
        # 提取class
        class_matches = re.findall(r'class=["\']([^"\']+)["\']', html)
        analysis['classes'].update(class_matches)
        
        # 提取id
        id_matches = re.findall(r'id=["\']([^"\']+)["\']', html)
        analysis['ids'].update(id_matches)
        
        # 提取标签
        tag_matches = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)\s', html)
        analysis['tags'].update(tag_matches)
        
        # 分析常见结构
        structure_patterns = [
            (r'<div[^>]*class=["\'][^"\']*?book[^"\']*?["\']', 'book container'),
            (r'<div[^>]*class=["\'][^"\']*?chapter[^"\']*?["\']', 'chapter container'),
            (r'<div[^>]*class=["\'][^"\']*?content[^"\']*?["\']', 'content container'),
            (r'<ul[^>]*>', 'list structure'),
            (r'<li[^>]*>', 'list item')
        ]
        
        for pattern, structure_name in structure_patterns:
            if re.search(pattern, html):
                analysis['structures'].append(structure_name)
        
        return {
            'classes': list(analysis['classes']),
            'ids': list(analysis['ids']),
            'tags': list(analysis['tags']),
            'structures': analysis['structures']
        }
    
    def _generate_recommendations(
        self,
        similar_selectors: List[Dict],
        related_knowledge: List[KnowledgeEntry],
        html_analysis: Dict,
        element_type: str
    ) -> List[Dict[str, Any]]:
        """生成推荐"""
        recommendations = []
        
        # 1. 基于相似选择器的推荐
        for similar in similar_selectors[:5]:
            recommendations.append({
                'type': 'similar_selector',
                'selector': similar['selector'],
                'source': similar['source'],
                'title': similar['title'],
                'confidence': similar['confidence'],
                'examples': similar['examples'],
                'reason': f'与知识库中的{similar["source"]}相似'
            })
        
        # 2. 基于知识的推荐
        for entry in related_knowledge[:3]:
            if entry.type == 'pattern':
                recommendations.append({
                    'type': 'knowledge_pattern',
                    'selector': entry.content,
                    'source': entry.source_file,
                    'title': entry.title,
                    'confidence': entry.confidence,
                    'examples': entry.examples,
                    'reason': f'来自{entry.source_file}的已知模式'
                })
            elif entry.type == 'explanation':
                recommendations.append({
                    'type': 'knowledge_guide',
                    'content': entry.content[:200],
                    'source': entry.source_file,
                    'title': entry.title,
                    'reason': f'{entry.source_file}中的相关说明'
                })
        
        # 3. 基于HTML结构的推荐
        for class_name in html_analysis['classes']:
            if any(keyword in class_name.lower() for keyword in [element_type, 'book', 'chapter']):
                selector = f".{class_name}"
                recommendations.append({
                    'type': 'html_structure',
                    'selector': selector,
                    'confidence': 0.7,
                    'reason': f'HTML中包含相关class: {class_name}'
                })
        
        # 限制数量并排序
        recommendations.sort(key=lambda x: x.get('confidence', 0.5), reverse=True)
        
        return recommendations[:10]
    
    def _generate_reasoning(
        self,
        similar_selectors: List[Dict],
        related_knowledge: List[KnowledgeEntry],
        html_analysis: Dict,
        element_type: str
    ) -> str:
        """生成推理过程"""
        reasoning_parts = []
        
        reasoning_parts.append(f"🧠 知识应用推理过程")
        reasoning_parts.append("=" * 60)
        
        # 1. 分析目标
        reasoning_parts.append(f"\n📌 分析目标: {element_type}")
        
        # 2. HTML结构分析
        reasoning_parts.append(f"\n🔍 HTML结构分析:")
        reasoning_parts.append(f"   - 发现的Class: {', '.join(html_analysis['classes'][:5])}")
        reasoning_parts.append(f"   - 发现的ID: {', '.join(html_analysis['ids'][:5])}")
        reasoning_parts.append(f"   - 结构特征: {', '.join(html_analysis['structures'][:5])}")
        
        # 3. 知识匹配
        reasoning_parts.append(f"\n📚 知识匹配结果:")
        if similar_selectors:
            reasoning_parts.append(f"   - 找到 {len(similar_selectors)} 个相似选择器")
            for similar in similar_selectors[:3]:
                reasoning_parts.append(f"     • {similar['selector']} (来源: {similar['source']})")
        else:
            reasoning_parts.append(f"   - 未找到相似选择器")
        
        if related_knowledge:
            reasoning_parts.append(f"   - 找到 {len(related_knowledge)} 条相关知识")
            for entry in related_knowledge[:3]:
                reasoning_parts.append(f"     • {entry.title} (来源: {entry.source_file})")
        else:
            reasoning_parts.append(f"   - 未找到相关知识")
        
        # 4. 推荐依据
        reasoning_parts.append(f"\n✅ 推荐依据:")
        
        # 统计推荐类型
        rec_types = {}
        if similar_selectors:
            rec_types['相似选择器'] = len(similar_selectors)
        if related_knowledge:
            rec_types['知识库'] = len(related_knowledge)
        
        for rec_type, count in rec_types.items():
            reasoning_parts.append(f"   - {rec_type}: {count}条")
        
        # 5. 置信度评估
        reasoning_parts.append(f"\n📊 置信度评估:")
        if similar_selectors or related_knowledge:
            reasoning_parts.append(f"   - 基于知识匹配: 高")
            reasoning_parts.append(f"   - 参考源文件: {len(set(e.source_file for e in related_knowledge))}个")
        else:
            reasoning_parts.append(f"   - 基于知识匹配: 低")
            reasoning_parts.append(f"   - 建议: 使用通用分析策略")
        
        return '\n'.join(reasoning_parts)
    
    def _calculate_confidence(
        self,
        recommendations: List[Dict],
        related_knowledge: List[KnowledgeEntry]
    ) -> float:
        """计算置信度"""
        if not recommendations and not related_knowledge:
            return 0.3
        
        confidence = 0.5
        
        # 相似选择器加分
        similar_count = sum(
            1 for rec in recommendations
            if rec.get('type') == 'similar_selector'
        )
        confidence += min(similar_count * 0.1, 0.3)
        
        # 知识库条目加分
        if related_knowledge:
            confidence += 0.2
            
            # 模式条目加分更多
            pattern_count = sum(
                1 for entry in related_knowledge
                if entry.type == 'pattern'
            )
            confidence += min(pattern_count * 0.1, 0.2)
        
        return min(confidence, 1.0)
    
    def generate_rule_with_knowledge(
        self,
        element_type: str,
        selector: str,
        html: str
    ) -> Dict[str, Any]:
        """使用知识生成规则"""
        # 应用知识
        application = self.apply_knowledge_to_html(html, element_type)
        
        # 查找最佳匹配
        best_match = None
        best_score = 0
        
        for entry in application.applied_knowledge:
            if entry.type == 'pattern':
                score = entry.confidence
                if selector in entry.content:
                    score += 0.3
                if score > best_score:
                    best_score = score
                    best_match = entry
        
        # 生成规则建议
        rule = {
            'selector': selector,
            'knowledge_based': best_match is not None,
            'reference_source': best_match.source_file if best_match else None,
            'confidence': best_score if best_match else 0.5,
            'recommendations': []
        }
        
        # 添加推荐
        if best_match and best_match.examples:
            rule['recommendations'].extend(best_match.examples[:3])
        
        # 添加通用建议
        if element_type in ['author', 'intro']:
            if not any('@text##' in r for r in rule['recommendations']):
                # 添加替换规则建议
                if element_type == 'author':
                    rule['recommendations'].append('@text##^(作者|Writer|By)[:：]\\s*##')
        
        return rule
    
    def validate_knowledge_application(
        self,
        selector: str,
        html: str,
        expected_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证知识应用效果"""
        # 应用知识
        application = self.apply_knowledge_to_html(html, 'general')
        
        validation = {
            'selector': selector,
            'has_knowledge_support': len(application.applied_knowledge) > 0,
            'knowledge_sources': [e.source_file for e in application.applied_knowledge],
            'confidence': application.confidence,
            'recommendations_count': len(application.recommendations),
            'valid': True,
            'issues': []
        }
        
        # 检查是否有知识支持
        if not validation['has_knowledge_support']:
            validation['issues'].append({
                'type': 'warning',
                'message': '没有找到相关知识支持',
                'suggestion': '建议使用通用分析策略或添加到知识库'
            })
            validation['confidence'] *= 0.8
        
        # 检查置信度
        if validation['confidence'] < 0.6:
            validation['issues'].append({
                'type': 'warning',
                'message': f'置信度较低 ({validation["confidence"]:.2f})',
                'suggestion': '建议验证选择器或寻找更相似的知识'
            })
            validation['valid'] = False
        
        return validation
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """获取学习摘要"""
        stats = self.learner.learning_stats
        
        return {
            'total_files': stats['total_files'],
            'learned_entries': stats['learned_entries'],
            'book_sources': stats['book_sources'],
            'patterns': stats['patterns'],
            'selectors': stats['selectors'],
            'application_count': len(self.application_history),
            'avg_confidence': sum(
                app['confidence'] for app in self.application_history
            ) / max(len(self.application_history), 1),
            'top_knowledge_sources': self._get_top_knowledge_sources()
        }
    
    def _get_top_knowledge_sources(self) -> List[Dict[str, Any]]:
        """获取最常用的知识源"""
        source_counts = {}
        
        for entry in self.learner.knowledge_entries.values():
            source = entry.source_file
            source_counts[source] = source_counts.get(source, 0) + 1
        
        sorted_sources = sorted(
            source_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'source': source, 'count': count}
            for source, count in sorted_sources[:10]
        ]
