#!/usr/bin/env python3
"""
系统提示词统一管理模块
提供系统提示词的加载和缓存功能
"""
import os
import sys
from typing import Optional

# 全局变量：缓存系统提示词
_SYSTEM_PROMPT: Optional[str] = None

# 系统提示词文件路径
SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), 
    '..', '..', 
    'config', 
    'system_prompt.md'
)


def load_system_prompt(force_reload: bool = False) -> str:
    """
    加载系统提示词
    
    Args:
        force_reload: 是否强制重新加载（忽略缓存）
    
    Returns:
        系统提示词内容（如果加载失败返回空字符串）
    """
    global _SYSTEM_PROMPT
    
    # 如果已加载且不强制重新加载，直接返回缓存
    if _SYSTEM_PROMPT is not None and not force_reload:
        return _SYSTEM_PROMPT
    
    try:
        if os.path.exists(SYSTEM_PROMPT_PATH):
            with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
                _SYSTEM_PROMPT = f.read()
            
            print(f"✅ 系统提示词已加载: {len(_SYSTEM_PROMPT)} 字符", file=sys.stderr)
            return _SYSTEM_PROMPT
        else:
            print(f"⚠️ 系统提示词文件不存在: {SYSTEM_PROMPT_PATH}", file=sys.stderr)
            return ""
    except Exception as e:
        print(f"❌ 加载系统提示词失败: {e}", file=sys.stderr)
        return ""


def get_system_prompt() -> str:
    """
    获取系统提示词（使用缓存）
    
    Returns:
        系统提示词内容
    """
    return load_system_prompt()


def is_system_prompt_loaded() -> bool:
    """
    检查系统提示词是否已加载
    
    Returns:
        True 如果已加载，False 否则
    """
    return _SYSTEM_PROMPT is not None


def clear_system_prompt_cache():
    """清除系统提示词缓存"""
    global _SYSTEM_PROMPT
    _SYSTEM_PROMPT = None


def get_system_prompt_path() -> str:
    """
    获取系统提示词文件路径
    
    Returns:
        系统提示词文件路径
    """
    return SYSTEM_PROMPT_PATH


# 模块加载时自动加载系统提示词
load_system_prompt()
