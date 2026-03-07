"""
Legado书源调试工具
提供给智能体使用的调试工具

该模块提供了两个主要的工具函数：
1. debug_book_source() - 调试书源规则
2. test_legado_rule() - 测试单个规则

使用方法:
    from tools.legado_debug_tools import debug_book_source, test_legado_rule

    # 调试书源
    result = debug_book_source(book_source_json, keyword="斗破苍穹")

    # 测试单个规则
    result = test_legado_rule(html_content, rule=".title@text")
"""

from typing import Dict, Any, Optional
import json
import logging
from tools.book_source_debugger import BookSourceDebugger

logger = logging.getLogger(__name__)


# 全局调试器实例
_debugger_instance = None


def debug_book_source(book_source_json: str, keyword: str = "斗破苍穹", test_type: str = "full") -> Dict[str, Any]:
    """
    调试书源规则

    Args:
        book_source_json: 书源JSON字符串
        keyword: 测试关键词
        test_type: 测试类型
            - "full": 完整测试（搜索、书籍信息、目录、正文）
            - "search": 只测试搜索
            - "bookInfo": 只测试书籍信息
            - "toc": 只测试目录
            - "content": 只测试正文

    Returns:
        调试结果字典
    """
    global _debugger_instance

    # 初始化调试器
    if _debugger_instance is None:
        _debugger_instance = BookSourceDebugger()

    try:
        # 加载书源
        book_source = _debugger_instance.load_book_source(book_source_json)
        if not book_source:
            return {
                "success": False,
                "error": "加载书源失败"
            }

        result = {
            "success": True,
            "bookSourceName": book_source.get("bookSourceName", "未知"),
            "testType": test_type,
            "keyword": keyword,
            "results": {}
        }

        # 根据测试类型执行不同的测试
        if test_type == "full":
            result["results"] = _debugger_instance.run_full_test(book_source_json, keyword)
        elif test_type == "search":
            result["results"] = _debugger_instance.test_search(book_source, keyword)
        elif test_type == "bookInfo":
            # 需要提供书籍URL
            if keyword.startswith("http"):
                result["results"] = _debugger_instance.test_book_info(book_source, keyword)
            else:
                # 先搜索，然后使用第一个结果
                search_result = _debugger_instance.test_search(book_source, keyword)
                if search_result.get("results") and search_result["results"][0].get("bookUrl"):
                    book_url = search_result["results"][0]["bookUrl"]
                    base_url = book_source.get("bookSourceUrl", "")
                    if not book_url.startswith("http"):
                        book_url = f"{base_url.rstrip('/')}/{book_url.lstrip('/')}"
                    result["results"] = _debugger_instance.test_book_info(book_source, book_url)
                else:
                    result["success"] = False
                    result["error"] = "未找到书籍，无法测试书籍信息"
        elif test_type == "toc":
            # 需要提供目录URL
            if keyword.startswith("http"):
                result["results"] = _debugger_instance.test_toc(book_source, keyword)
            else:
                result["success"] = False
                result["error"] = "需要提供目录URL"
        elif test_type == "content":
            # 需要提供章节URL
            if keyword.startswith("http"):
                result["results"] = _debugger_instance.test_content(book_source, keyword)
            else:
                result["success"] = False
                result["error"] = "需要提供章节URL"
        else:
            result["success"] = False
            result["error"] = f"不支持的测试类型: {test_type}"

        return result

    except Exception as e:
        logger.error(f"调试书源失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def test_legado_rule(html_content: str, rule: str, base_url: str = "") -> Dict[str, Any]:
    """
    测试单个Legado规则

    Args:
        html_content: HTML内容
        rule: 规则字符串（如 ".title@text", "text.下一章@href"）
        base_url: 基础URL

    Returns:
        测试结果
    """
    try:
        from tools.legado_debugger import LegadoDebugger

        debugger = LegadoDebugger(html_content, base_url)

        # 判断是获取单个值还是列表
        # 简单判断：如果选择器匹配多个元素，可能是列表
        if '@' not in rule:
            return {
                "success": False,
                "error": "规则格式不正确，缺少@分隔符"
            }

        # 尝试获取单个值
        single_result = debugger.get_string(rule)

        # 尝试获取列表
        list_result = debugger.get_string_list(rule)

        return {
            "success": True,
            "rule": rule,
            "singleResult": single_result,
            "listResult": list_result if len(list_result) > 1 else [],
            "isList": len(list_result) > 1
        }

    except Exception as e:
        logger.error(f"测试规则失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def format_debug_result(result: Dict[str, Any]) -> str:
    """
    格式化调试结果为可读字符串

    Args:
        result: 调试结果字典

    Returns:
        格式化的字符串
    """
    if not result.get("success"):
        return f"[ERROR] 调试失败: {result.get('error', '未知错误')}"

    output = []

    # 基本信息
    output.append(f"[OK] 书源名称: {result.get('bookSourceName', '未知')}")
    output.append(f"[NOTE] 测试类型: {result.get('testType', '未知')}")
    if result.get('keyword'):
        output.append(f"[SEARCH] 关键词: {result.get('keyword')}")
    output.append("")

    # 测试结果
    test_results = result.get("results", {})

    # 搜索结果
    if "results" in test_results:
        output.append("📚 搜索结果:")
        for book in test_results["results"][:3]:  # 只显示前3个
            output.append(f"  - {book.get('name', '未知')} ({book.get('author', '未知作者')})")
            if book.get("bookUrl"):
                output.append(f"    URL: {book['bookUrl']}")
        output.append("")

    # 书籍信息
    if "name" in test_results:
        output.append("📖 书籍信息:")
        output.append(f"  书名: {test_results.get('name')}")
        output.append(f"  作者: {test_results.get('author')}")
        if test_results.get("kind"):
            output.append(f"  分类: {test_results.get('kind')}")
        if test_results.get("lastChapter"):
            output.append(f"  最新章节: {test_results.get('lastChapter')}")
        output.append("")

    # 目录
    if "chapters" in test_results:
        output.append(f"📑 目录 (前5章):")
        for chapter in test_results["chapters"][:5]:
            output.append(f"  - {chapter.get('name', '未知章节')}")
        output.append("")

    # 正文
    if "text" in test_results:
        output.append("[DOC] 正文内容:")
        text = test_results.get("text", "")
        preview = text[:200] + "..." if len(text) > 200 else text
        output.append(f"  {preview}")
        output.append(f"  (长度: {len(text)} 字符)")
        if test_results.get("nextUrl"):
            output.append(f"  下一页URL: {test_results.get('nextUrl')}")
        output.append("")

    return "\n".join(output)


def quick_test(html_content: str, rule: str) -> str:
    """
    快速测试规则并返回格式化结果

    Args:
        html_content: HTML内容
        rule: 规则字符串

    Returns:
        格式化的测试结果
    """
    result = test_legado_rule(html_content, rule)

    if not result.get("success"):
        return f"[ERROR] 测试失败: {result.get('error', '未知错误')}"

    output = []
    output.append(f"[OK] 规则: {rule}")
    output.append(f"[NOTE] 单个结果: {result['singleResult']}")

    if result["isList"]:
        output.append(f"[INFO] 列表结果 ({len(result['listResult'])} 项):")
        for i, item in enumerate(result["listResult"][:5], 1):
            preview = item[:50] + "..." if len(item) > 50 else item
            output.append(f"  {i}. {preview}")
        if len(result["listResult"]) > 5:
            output.append(f"  ... (还有 {len(result['listResult']) - 5} 项)")

    return "\n".join(output)


# 导出工具函数
__all__ = [
    "debug_book_source",
    "test_legado_rule",
    "format_debug_result",
    "quick_test"
]
