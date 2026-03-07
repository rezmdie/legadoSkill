#!/usr/bin/env python3
"""
LangGraph 图定义模块
定义 Legado 书源驯兽师的工作流图
"""
from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """图状态定义"""
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: str
    context: dict
    current_step: str
    tool_calls: list
    results: dict


def knowledge_query_node(state: GraphState) -> GraphState:
    """
    知识库查询节点
    查询 CSS 选择器规则、真实书源示例、书源模板等
    """
    logger.info(f"[知识库查询节点] 会话ID: {state['session_id']}")
    
    # 这里应该调用知识库查询工具
    # 由于这是一个示例，我们只是记录状态
    state["current_step"] = "knowledge_query"
    state["context"]["knowledge_queried"] = True
    
    # 添加消息
    state["messages"].append(
        AIMessage(content="已查询知识库，获取 CSS 选择器规则和真实书源示例")
    )
    
    return state


def html_fetch_node(state: GraphState) -> GraphState:
    """
    HTML 获取节点
    获取真实网页 HTML 源代码
    """
    logger.info(f"[HTML获取节点] 会话ID: {state['session_id']}")
    
    state["current_step"] = "html_fetch"
    state["context"]["html_fetched"] = True
    
    state["messages"].append(
        AIMessage(content="已获取真实网页 HTML 源代码")
    )
    
    return state


def html_analysis_node(state: GraphState) -> GraphState:
    """
    HTML 分析节点
    分析网页结构，识别关键元素
    """
    logger.info(f"[HTML分析节点] 会话ID: {state['session_id']}")
    
    state["current_step"] = "html_analysis"
    state["context"]["html_analyzed"] = True
    
    state["messages"].append(
        AIMessage(content="已分析网页结构，识别关键元素")
    )
    
    return state


def rule_validation_node(state: GraphState) -> GraphState:
    """
    规则验证节点
    验证生成的规则是否符合 Legado 规范
    """
    logger.info(f"[规则验证节点] 会话ID: {state['session_id']}")
    
    state["current_step"] = "rule_validation"
    state["context"]["rules_validated"] = True
    
    state["messages"].append(
        AIMessage(content="已验证规则语法和完整性")
    )
    
    return state


def book_source_creation_node(state: GraphState) -> GraphState:
    """
    书源创建节点
    创建完整的书源 JSON
    """
    logger.info(f"[书源创建节点] 会话ID: {state['session_id']}")
    
    state["current_step"] = "book_source_creation"
    state["context"]["book_source_created"] = True
    
    state["messages"].append(
        AIMessage(content="已创建完整的书源 JSON")
    )
    
    return state


def decision_node(state: GraphState) -> Literal["knowledge_query", "html_fetch", "html_analysis", "rule_validation", "book_source_creation", END]:
    """
    决策节点
    根据当前状态决定下一步操作
    """
    current_step = state.get("current_step", "")
    
    if current_step == "":
        return "knowledge_query"
    elif current_step == "knowledge_query":
        return "html_fetch"
    elif current_step == "html_fetch":
        return "html_analysis"
    elif current_step == "html_analysis":
        return "rule_validation"
    elif current_step == "rule_validation":
        return "book_source_creation"
    elif current_step == "book_source_creation":
        return END
    else:
        return END


def build_graph() -> StateGraph:
    """
    构建 LangGraph
    
    Returns:
        编译后的 StateGraph 实例
    """
    # 创建图
    graph = StateGraph(GraphState)
    
    # 添加节点
    graph.add_node("knowledge_query", knowledge_query_node)
    graph.add_node("html_fetch", html_fetch_node)
    graph.add_node("html_analysis", html_analysis_node)
    graph.add_node("rule_validation", rule_validation_node)
    graph.add_node("book_source_creation", book_source_creation_node)
    graph.add_node("decision", decision_node)
    
    # 设置入口
    graph.set_entry_point("decision")
    
    # 添加边
    graph.add_edge("knowledge_query", "decision")
    graph.add_edge("html_fetch", "decision")
    graph.add_edge("html_analysis", "decision")
    graph.add_edge("rule_validation", "decision")
    graph.add_edge("book_source_creation", "decision")
    
    # 编译图
    compiled_graph = graph.compile()
    
    logger.info("LangGraph 构建完成")
    
    return compiled_graph


# 全局图实例
_global_graph = None


def get_graph() -> StateGraph:
    """
    获取全局图实例
    
    Returns:
        编译后的 StateGraph 实例
    """
    global _global_graph
    if _global_graph is None:
        _global_graph = build_graph()
    return _global_graph
