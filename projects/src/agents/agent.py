"""
Legado书源驯兽师智能体
帮助用户编写、调试和优化Legado书源规则
"""

import os
import json
import sys
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入系统提示词模块
from utils.system_prompt import get_system_prompt

# 确保tools目录在Python路径中
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

tools_path = os.path.join(workspace_path, "src", "tools")
if tools_path not in sys.path:
    sys.path.insert(0, tools_path)

# 添加utils目录到Python路径（用于智能分析器）
utils_path = os.path.join(workspace_path, "src", "utils")
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# 导入工具
from tools.legado_debug_tools import debug_book_source
from tools.book_source_editor import (
    edit_book_source,
    export_book_source,
    validate_book_source,
    save_to_knowledge
)
from tools.element_picker_guide import (
    element_picker_guide,
    generate_selector_suggestions,
    browser_debug_helper
)
from tools.book_source_html_editor import generate_html_editor

# 智能分析工具
from tools.smart_web_analyzer import (
    smart_analyze_website,
    smart_build_search_request,
    smart_fetch_list
)
from tools.web_fetch_tool import (
    fetch_web_page,
    extract_elements,
    analyze_search_structure
)

# 智能页面分析工具
from tools.smart_bookinfo_analyzer import analyze_book_info_page
from tools.smart_toc_analyzer import analyze_toc_page
from tools.smart_content_analyzer import analyze_content_page
from tools.smart_full_analyzer import (
    analyze_complete_book_source,
    analyze_book_structure
)

# 知识库工具
from tools.knowledge_tools import (
    learn_knowledge_base,
    search_knowledge,
    get_book_source_examples,
    check_knowledge_status
)

# 知识库索引工具（新增 - 快速搜索所有知识文件，防止内容截断）
from tools.knowledge_index_tool import (
    search_knowledge_index,
    get_css_selector_rules,
    get_real_book_source_examples,
    get_book_source_templates,
    list_all_knowledge_files,
    read_file_paginated,
    get_file_summary
)

# 真实网页验证工具（新增 - 强制真实模式）
from tools.selector_validator import (
    validate_selector_on_real_web,
    extract_from_real_web
)

# 人工干预工具（新增 - 允许用户手动干预）
from tools.user_intervention import (
    manual_intervention_mode,
    inject_custom_js,
    correct_selector,
    manual_define_rule,
    provide_html_sample,
    save_experience,
    record_solution
)

# 协同编辑和验证工具（新增）
from tools.collaborative_edit import (
    validate_correction,
    test_manual_rule,
    analyze_user_html,
    debug_manual_intervention
)

# 知识库审查工具（新增 - 审查知识库内容）
from tools.knowledge_auditor import (
    audit_knowledge_base,
    get_saved_html,
    list_saved_htmls
)

# 智能请求工具（新增 - 支持各种HTTP方法）
from tools.smart_fetcher import (
    smart_fetch_html,
    get_full_html,
    test_request_method
)

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_agent(ctx=None):
    """
    构建Legado书源驯兽师智能体
    
    Returns:
        Agent实例
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    # 读取系统提示词（使用统一的系统提示词模块）
    system_prompt = get_system_prompt()
    
    # 如果系统提示词为空，使用配置文件中的sp字段作为回退
    if not system_prompt:
        system_prompt = cfg.get("sp", "你是一个有帮助的助手。")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # 构建工具列表（按优先级排序）
    tools = [
        # 智能请求工具（最高优先级 - 获取真实HTML）
        smart_fetch_html,
        get_full_html,
        test_request_method,
        # 知识库工具（高优先级 - 真正学会知识）
        learn_knowledge_base,
        check_knowledge_status,
        search_knowledge,
        get_book_source_examples,
        # 知识库索引工具（高优先级 - 快速搜索所有知识文件，防止内容截断）
        search_knowledge_index,
        get_css_selector_rules,
        get_real_book_source_examples,
        get_book_source_templates,
        list_all_knowledge_files,
        read_file_paginated,
        get_file_summary,
        # 知识库审查工具（高优先级 - 审查知识库是否适用于真实HTML）
        audit_knowledge_base,
        get_saved_html,
        list_saved_htmls,
        # 人工干预工具（高优先级 - 当AI无法处理时，用户可以手动干预）
        manual_intervention_mode,
        correct_selector,
        manual_define_rule,
        inject_custom_js,
        provide_html_sample,
        # 验证工具（中高优先级 - 验证用户的修正）
        validate_correction,
        test_manual_rule,
        analyze_user_html,
        # 真实网页验证工具（中优先级 - 强制真实模式）
        validate_selector_on_real_web,
        extract_from_real_web,
        # 综合分析工具（中优先级）
        analyze_complete_book_source,
        analyze_book_structure,
        # 智能页面分析工具（中优先级 - 已更新为严格真实模式 + HTML保存 + 知识库审查）
        analyze_book_info_page,
        analyze_toc_page,
        analyze_content_page,
        # 智能分析工具（中优先级）
        smart_analyze_website,
        smart_build_search_request,
        smart_fetch_list,
        fetch_web_page,
        extract_elements,
        analyze_search_structure,
        # 选择器生成
        generate_selector_suggestions,
        # 书源编辑
        edit_book_source,
        generate_html_editor,
        element_picker_guide,
        # 导出和验证
        export_book_source,
        validate_book_source,
        save_to_knowledge,
        # 经验保存（低优先级 - 成功后保存）
        save_experience,
        record_solution,
        debug_manual_intervention,
        # 调试器（谨慎使用）
        debug_book_source,
        browser_debug_helper
    ]
    
    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
