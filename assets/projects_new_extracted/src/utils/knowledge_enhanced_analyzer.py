"""
知识增强分析器
深度集成学习到的知识，真正做到"学会知识"并正确应用
"""

import os
from typing import Dict, List, Any, Optional
from .knowledge_learner import KnowledgeLearner, KnowledgeEntry
from .knowledge_applier import KnowledgeApplier, KnowledgeApplication
from .knowledge_based_analyzer import KnowledgeBasedAnalyzer, AnalysisResult


class KnowledgeEnhancedAnalyzer:
    """知识增强分析器"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        
        # 延迟初始化 - 不在构造时创建重量级对象
        self._learner = None
        self._applier = None
        self._base_analyzer = None
        
        # 是否已学习
        self.is_learned = False
    
    @property
    def learner(self):
        """懒加载知识学习引擎"""
        if self._learner is None:
            self._learner = KnowledgeLearner(self.assets_path)
        return self._learner
    
    @property
    def applier(self):
        """获取知识应用引擎"""
        return self._applier
    
    @applier.setter
    def applier(self, value):
        self._applier = value
    
    @property
    def base_analyzer(self):
        """懒加载基础分析器"""
        if self._base_analyzer is None:
            self._base_analyzer = KnowledgeBasedAnalyzer(self.assets_path)
        return self._base_analyzer
    
    def learn_knowledge(self, force: bool = False) -> Dict[str, Any]:
        """
        学习知识库
        
        Args:
            force: 是否强制重新学习
        
        Returns:
            学习统计
        """
        if not self.is_learned or force:
            print("\n" + "=" * 60)
            print("🎓 启动知识学习引擎...")
            print("=" * 60)
            
            stats = self.learner.learn_all()
            
            # 初始化应用引擎
            self.applier = KnowledgeApplier(self.learner)
            
            self.is_learned = True
            
            return stats
        else:
            return self.learner.learning_stats
    
    def analyze_with_learned_knowledge(
        self,
        html: str,
        element_type: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        使用学到的知识进行分析
        
        Args:
            html: HTML内容
            element_type: 元素类型
            context: 上下文信息
        
        Returns:
            分析结果，包含知识应用详情
        """
        # 确保已学习
        if not self.is_learned:
            self.learn_knowledge()
        
        # 应用知识
        application = self.applier.apply_knowledge_to_html(
            html,
            element_type,
            context or {}
        )
        
        # 基础分析
        base_result = self.base_analyzer.analyze_with_knowledge(
            html,
            element_type,
            context.get('query', '') if context else ''
        )
        
        # 合并结果
        enhanced_result = {
            'element_type': element_type,
            'base_analysis': base_result,
            'knowledge_application': application,
            'recommended_selectors': self._merge_recommendations(
                base_result,
                application
            ),
            'confidence': self._calculate_enhanced_confidence(
                base_result,
                application
            ),
            'knowledge_sources': application.source_files,
            'applied_knowledge_count': len(application.applied_knowledge),
            'reasoning': self._generate_enhanced_reasoning(
                base_result,
                application
            ),
            'warnings': self._merge_warnings(
                base_result,
                application
            )
        }
        
        return enhanced_result
    
    def _merge_recommendations(
        self,
        base_result: AnalysisResult,
        application: KnowledgeApplication
    ) -> List[Dict[str, Any]]:
        """合并推荐结果"""
        merged = []
        
        # 添加基础推荐
        for rec in base_result.recommended_selectors:
            rec['source'] = 'base_analysis'
            merged.append(rec)
        
        # 添加知识推荐
        for rec in application.recommendations:
            if rec.get('selector'):
                # 检查是否已存在
                exists = any(
                    m.get('selector') == rec['selector']
                    for m in merged
                )
                if not exists:
                    rec['source'] = 'knowledge'
                    merged.append(rec)
        
        # 按置信度排序
        merged.sort(key=lambda x: x.get('confidence', 0.5), reverse=True)
        
        return merged[:10]
    
    def _calculate_enhanced_confidence(
        self,
        base_result: AnalysisResult,
        application: KnowledgeApplication
    ) -> float:
        """计算增强置信度"""
        base_conf = base_result.confidence
        knowledge_conf = application.confidence
        
        # 加权平均
        if len(application.applied_knowledge) > 0:
            # 有知识支持时，知识置信度权重更高
            enhanced = (base_conf * 0.3) + (knowledge_conf * 0.7)
        else:
            # 无知识支持时，基础分析权重更高
            enhanced = (base_conf * 0.7) + (knowledge_conf * 0.3)
        
        return min(enhanced, 1.0)
    
    def _generate_enhanced_reasoning(
        self,
        base_result: AnalysisResult,
        application: KnowledgeApplication
    ) -> str:
        """生成增强推理过程"""
        reasoning_parts = []
        
        reasoning_parts.append("🧠 知识增强分析推理过程")
        reasoning_parts.append("=" * 60)
        
        # 基础分析
        reasoning_parts.append("\n📊 基础分析:")
        reasoning_parts.append(base_result.reasoning)
        
        # 知识应用
        reasoning_parts.append("\n📚 知识应用:")
        reasoning_parts.append(application.reasoning)
        
        # 知识源
        if application.source_files:
            reasoning_parts.append("\n📖 引用的知识源:")
            for source in set(application.source_files):
                reasoning_parts.append(f"   • {source}")
        
        # 应用统计
        reasoning_parts.append(f"\n📈 应用统计:")
        reasoning_parts.append(f"   - 应用的知识条目: {len(application.applied_knowledge)}")
        reasoning_parts.append(f"   - 生成的推荐: {len(application.recommendations)}")
        reasoning_parts.append(f"   - 基础置信度: {base_result.confidence:.2f}")
        reasoning_parts.append(f"   - 知识置信度: {application.confidence:.2f}")
        reasoning_parts.append(f"   - 增强置信度: {self._calculate_enhanced_confidence(base_result, application):.2f}")
        
        # 学习状态
        if self.is_learned:
            stats = self.learner.learning_stats
            reasoning_parts.append(f"\n📚 知识库状态:")
            reasoning_parts.append(f"   - 已学习文件: {stats['total_files']}")
            reasoning_parts.append(f"   - 知识条目: {stats['learned_entries']}")
            reasoning_parts.append(f"   - 书源数量: {stats['book_sources']}")
            reasoning_parts.append(f"   - 模式数量: {stats['patterns']}")
        
        return '\n'.join(reasoning_parts)
    
    def _merge_warnings(
        self,
        base_result: AnalysisResult,
        application: KnowledgeApplication
    ) -> List[str]:
        """合并警告信息"""
        warnings = []
        
        # 基础警告
        warnings.extend(base_result.warnings)
        
        # 知识应用警告
        if not application.applied_knowledge:
            warnings.append("⚠️  未找到相关知识支持，建议添加到知识库")
        
        if application.confidence < 0.6:
            warnings.append(f"⚠️  知识应用置信度较低 ({application.confidence:.2f})")
        
        return warnings
    
    def get_knowledge_by_query(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """根据查询获取知识"""
        if not self.is_learned:
            self.learn_knowledge()
        
        results = self.learner.search_knowledge(query, limit=limit)
        
        return [
            {
                'id': entry.id,
                'title': entry.title,
                'type': entry.type,
                'category': entry.category,
                'source': entry.source_file,
                'content': entry.content[:200],
                'tags': entry.tags,
                'examples': entry.examples,
                'confidence': entry.confidence
            }
            for entry in results
        ]
    
    def get_book_source_examples(
        self,
        element_type: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """获取书源示例"""
        if not self.is_learned:
            self.learn_knowledge()
        
        examples = []
        
        for book_source in list(self.learner.book_sources.values())[:limit]:
            patterns = book_source.patterns.get(element_type, [])
            
            if patterns:
                examples.append({
                    'source_name': book_source.source_name,
                    'source_url': book_source.source_url,
                    'patterns': patterns[:3],
                    'tags': book_source.tags
                })
        
        return examples
    
    def validate_selector_with_knowledge(
        self,
        selector: str,
        html: str,
        element_type: str
    ) -> Dict[str, Any]:
        """使用知识验证选择器"""
        if not self.is_learned:
            self.learn_knowledge()
        
        # 基础验证
        validation = self.applier.validate_knowledge_application(
            selector,
            html
        )
        
        # 查找相似知识
        similar = self.learner.get_similar_selectors(html, limit=5)
        
        # 检查是否匹配已知模式
        matched_patterns = []
        for entry in self.learner.knowledge_entries.values():
            if entry.type == 'pattern' and selector in entry.content:
                matched_patterns.append({
                    'source': entry.source_file,
                    'title': entry.title,
                    'confidence': entry.confidence
                })
        
        validation.update({
            'matched_patterns': matched_patterns,
            'similar_selectors': similar,
            'element_type': element_type
        })
        
        # 重新计算有效性
        if matched_patterns:
            validation['has_knowledge_support'] = True
            validation['confidence'] = min(validation['confidence'] + 0.2, 1.0)
        
        return validation
    
    def get_learning_status(self) -> Dict[str, Any]:
        """获取学习状态"""
        if self.is_learned and self._learner is not None:
            return {
                'is_learned': True,
                'learning_stats': self._learner.learning_stats,
                'knowledge_count': len(self._learner.knowledge_entries),
                'book_source_count': len(self._learner.book_sources),
                'pattern_count': len(self._learner.patterns)
            }
        return {
            'is_learned': False,
            'learning_stats': {},
            'knowledge_count': 0,
            'book_source_count': 0,
            'pattern_count': 0
        }


# 全局实例
_global_analyzer = None


def get_global_analyzer(assets_path: str = "assets") -> KnowledgeEnhancedAnalyzer:
    """获取全局分析器实例"""
    global _global_analyzer
    
    if _global_analyzer is None:
        _global_analyzer = KnowledgeEnhancedAnalyzer(assets_path)
    
    return _global_analyzer
