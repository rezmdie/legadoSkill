#!/usr/bin/env python3
"""
知识库初始化模块
在MCP服务器启动时自动初始化知识库
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Optional

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
assets_path = os.path.join(project_root, 'assets')

# 导入知识学习引擎
sys.path.insert(0, os.path.join(project_root, 'src', 'utils'))
from knowledge_learner import KnowledgeLearner

logger = logging.getLogger(__name__)

# 全局知识学习器实例
_global_learner: Optional[KnowledgeLearner] = None
_knowledge_initialized = False


def get_assets_path() -> str:
    """
    获取assets目录路径
    
    Returns:
        assets目录路径
    """
    return assets_path


def initialize_knowledge_base(force: bool = False) -> Dict[str, Any]:
    """
    初始化知识库
    
    Args:
        force: 是否强制重新初始化（即使已经初始化过）
    
    Returns:
        学习统计信息
    """
    global _global_learner, _knowledge_initialized
    
    # 如果已经初始化且不强制重新初始化，直接返回
    if _knowledge_initialized and not force:
        if _global_learner:
            return _global_learner.learning_stats
        return {'error': 'Knowledge base marked as initialized but learner is None'}
    
    try:
        logger.info("=" * 60)
        logger.info("🧠 开始初始化知识库...")
        logger.info("=" * 60)
        
        # 创建知识学习器
        _global_learner = KnowledgeLearner(assets_path)
        
        # 学习所有知识
        stats = _global_learner.learn_all()
        
        # 标记为已初始化
        _knowledge_initialized = True
        
        logger.info("=" * 60)
        logger.info("✅ 知识库初始化完成！")
        logger.info("=" * 60)
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ 知识库初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def get_knowledge_learner() -> Optional[KnowledgeLearner]:
    """
    获取全局知识学习器实例
    
    Returns:
        KnowledgeLearner 实例，如果未初始化返回 None
    """
    return _global_learner


def is_knowledge_initialized() -> bool:
    """
    检查知识库是否已初始化
    
    Returns:
        True 如果已初始化，False 否则
    """
    return _knowledge_initialized


def search_knowledge(
    query: str,
    category: Optional[str] = None,
    limit: int = 5
) -> list:
    """
    搜索知识库
    
    Args:
        query: 搜索关键词
        category: 类别过滤（可选）
        limit: 返回结果数量
    
    Returns:
        搜索结果列表
    """
    learner = get_knowledge_learner()
    if not learner:
        logger.warning("知识库未初始化，无法搜索")
        return []
    
    return learner.search_knowledge(query, category=category, limit=limit)


def get_similar_selectors(html: str, limit: int = 10) -> list:
    """
    根据HTML获取相似选择器
    
    Args:
        html: HTML内容
        limit: 返回结果数量
    
    Returns:
        相似选择器列表
    """
    learner = get_knowledge_learner()
    if not learner:
        logger.warning("知识库未初始化，无法获取相似选择器")
        return []
    
    return learner.get_similar_selectors(html, limit=limit)


def get_knowledge_by_tag(tag: str) -> list:
    """
    根据标签获取知识
    
    Args:
        tag: 标签
    
    Returns:
        知识条目列表
    """
    learner = get_knowledge_learner()
    if not learner:
        logger.warning("知识库未初始化，无法获取知识")
        return []
    
    return learner.get_knowledge_by_tag(tag)


def get_learning_stats() -> Dict[str, Any]:
    """
    获取学习统计信息
    
    Returns:
        学习统计信息
    """
    learner = get_knowledge_learner()
    if not learner:
        return {
            'error': 'Knowledge base not initialized',
            'initialized': False
        }
    
    return {
        'initialized': True,
        'stats': learner.learning_stats,
        'knowledge_count': len(learner.knowledge_entries),
        'book_source_count': len(learner.book_sources),
        'pattern_count': len(learner.patterns),
        'selector_count': len(learner.selectors)
    }


def reload_knowledge_base() -> Dict[str, Any]:
    """
    重新加载知识库
    
    Returns:
        学习统计信息
    """
    global _knowledge_initialized
    _knowledge_initialized = False
    return initialize_knowledge_base(force=True)


# 模块加载时自动初始化知识库
def _auto_initialize():
    """模块加载时自动初始化知识库"""
    try:
        # 检查是否在MCP模式下
        if os.environ.get('MCP_MODE') == 'true':
            # 在MCP模式下，延迟初始化（在第一次使用时初始化）
            logger.info("MCP模式：知识库将在首次使用时初始化")
        else:
            # 非MCP模式，立即初始化
            initialize_knowledge_base()
    except Exception as e:
        logger.warning(f"自动初始化知识库失败: {e}")


# 取消自动初始化，改为按需初始化
# _auto_initialize()
