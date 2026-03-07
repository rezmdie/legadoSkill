"""
Legado书源调试工具
提供给智能体使用的工具函数

注意：这些工具仅在用户明确要求调试时使用
"""

from langchain.tools import tool, ToolRuntime
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


@tool
def debug_legado_book_source(
    book_source_json: str,
    keyword: str = "斗破苍穹",
    test_type: str = "full"
) -> str:
    """
    调试Legado书源规则

    ⚠️ 注意：仅在用户明确要求调试时使用此工具！

    Args:
        book_source_json: 书源JSON字符串（数组格式）
        keyword: 测试关键词，默认为"斗破苍穹"
        test_type: 测试类型
            - "full": 完整测试（搜索、书籍信息、目录、正文）
            - "search": 只测试搜索
            - "bookInfo": 只测试书籍信息
            - "toc": 只测试目录
            - "content": 只测试正文

    Returns:
        调试结果的详细报告

    Example:
        # 调试书源（完整测试）
        result = debug_legado_book_source(book_source_json, "斗破苍穹", "full")

        # 只测试搜索
        result = debug_legado_book_source(book_source_json, "斗破苍穹", "search")
    """
    try:
        from tools.legado_debug_tools import debug_book_source, format_debug_result

        logger.info(f"开始调试书源，测试类型: {test_type}")

        # 调试书源
        result = debug_book_source(book_source_json, keyword, test_type)

        # 格式化结果
        formatted_result = format_debug_result(result)

        return formatted_result

    except Exception as e:
        error_msg = f"调试书源时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"❌ {error_msg}"


@tool
def test_legado_rule(
    html_content: str,
    rule: str,
    base_url: str = ""
) -> str:
    """
    测试单个Legado规则

    ⚠️ 注意：仅在用户明确要求测试规则时使用此工具！

    Args:
        html_content: HTML内容
        rule: 规则字符串
            - CSS选择器@提取类型: 如 ".title@text", ".link@href"
            - text.文本@属性: 如 "text.下一章@href"
            - 正则替换: 如 ".author@text##.*作者：##"
        base_url: 基础URL，用于处理相对路径

    Returns:
        测试结果

    Example:
        # 测试CSS选择器
        result = test_legado_rule(html_content, ".title@text")

        # 测试text.文本@href格式
        result = test_legado_rule(html_content, "text.下一章@href")

        # 测试正则替换
        result = test_legado_rule(html_content, ".author@text##.*作者：##")
    """
    try:
        from tools.legado_debug_tools import test_legado_rule, quick_test

        logger.info(f"测试规则: {rule}")

        # 测试规则
        result = test_legado_rule(html_content, rule, base_url)

        # 格式化结果
        if not result.get("success"):
            return f"❌ 测试失败: {result.get('error', '未知错误')}"

        formatted_result = []
        formatted_result.append(f"✅ 规则: {rule}")
        formatted_result.append(f"📝 单个结果: {result['singleResult']}")

        if result["isList"]:
            formatted_result.append(f"📋 列表结果 ({len(result['listResult'])} 项):")
            for i, item in enumerate(result["listResult"][:5], 1):
                preview = item[:50] + "..." if len(item) > 50 else item
                formatted_result.append(f"  {i}. {preview}")
            if len(result["listResult"]) > 5:
                formatted_result.append(f"  ... (还有 {len(result['listResult']) - 5} 项)")

        return "\n".join(formatted_result)

    except Exception as e:
        error_msg = f"测试规则时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"❌ {error_msg}"


@tool
def validate_legado_rules(
    book_source_json: str,
    test_url: Optional[str] = None
) -> str:
    """
    验证Legado书源规则的语法正确性

    ⚠️ 注意：仅在用户明确要求验证规则时使用此工具！

    Args:
        book_source_json: 书源JSON字符串（数组格式）
        test_url: 可选的测试URL，用于实际测试规则（不提供则只验证语法）

    Returns:
        验证报告

    Example:
        # 只验证语法
        result = validate_legado_rules(book_source_json)

        # 验证语法并实际测试
        result = validate_legado_rules(book_source_json, "https://example.com")
    """
    try:
        logger.info("开始验证书源规则")

        # 解析JSON
        try:
            sources = json.loads(book_source_json)
            if isinstance(sources, list):
                source = sources[0]
            else:
                source = sources
        except json.JSONDecodeError as e:
            return f"❌ JSON解析失败: {str(e)}"

        # 检查必填字段
        required_fields = ["bookSourceName", "bookSourceUrl", "searchUrl"]
        missing_fields = [f for f in required_fields if f not in source]

        if missing_fields:
            return f"❌ 缺少必填字段: {', '.join(missing_fields)}"

        # 验证规则字段
        report = []
        report.append("✅ 书源基本信息验证通过")
        report.append(f"  书源名称: {source.get('bookSourceName')}")
        report.append(f"  书源地址: {source.get('bookSourceUrl')}")

        # 检查规则字段
        rule_types = ["ruleSearch", "ruleBookInfo", "ruleToc", "ruleContent"]
        for rule_type in rule_types:
            if rule_type in source:
                rule = source[rule_type]
                if isinstance(rule, dict):
                    report.append(f"✅ {rule_type} 存在")
                else:
                    report.append(f"⚠️ {rule_type} 格式不正确，应为对象")

        # 如果提供了测试URL，进行实际测试
        if test_url:
            report.append("\n开始实际测试...")
            try:
                from tools.legado_debug_tools import test_legado_rule

                import requests
                response = requests.get(test_url, timeout=10)
                html = response.text

                # 测试几个典型规则
                test_rules = [
                    ("标题", "h1@text"),
                    ("链接", "a@href"),
                ]

                for name, rule in test_rules:
                    result = test_legado_rule(html, rule)
                    if result.get("success"):
                        report.append(f"✅ {name}规则测试通过: {rule}")
                    else:
                        report.append(f"⚠️ {name}规则测试失败: {rule}")

            except Exception as e:
                report.append(f"⚠️ 实际测试失败: {str(e)}")

        return "\n".join(report)

    except Exception as e:
        error_msg = f"验证规则时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"❌ {error_msg}"


# 导出工具
__all__ = [
    "debug_legado_book_source",
    "test_legado_rule",
    "validate_legado_rules"
]
