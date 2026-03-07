"""
知识库索引工具 - 防止内容被截断的版本

提供快速搜索知识库、获取CSS选择器规则、获取真实书源示例等功能
所有工具都支持分页和分段，防止内容被截断
"""

import os
import json
from langchain.tools import tool
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Optional
from utils.content_splitter import get_content_splitter, get_knowledge_index_searcher


@tool
def search_knowledge_index(query: str, category: str = "", limit: int = 10, runtime=None) -> str:
    """
    搜索知识库索引（快速搜索）
    
    Args:
        query: 搜索关键词
        category: 可选，限定分类（如"CSS选择器"、"书源规则"、"书源模板"等）
        limit: 最大返回结果数（默认10）
    
    Returns:
        搜索结果（包含文件路径、分类、大小、关键词等信息）
    
    Example:
        search_knowledge_index("CSS选择器")
        search_knowledge_index("POST请求", category="书源规则")
    """
    ctx = runtime.context if runtime else new_context(method="search_knowledge_index")
    
    try:
        searcher = get_knowledge_index_searcher()
        results = searcher.search(query, category, limit)
        
        if not results:
            return f"未找到与\"{query}\"相关的知识库文件。\n\n提示：\n- 尝试使用更通用的关键词\n- 检查拼写是否正确\n- 查看所有知识库文件：list_all_knowledge_files()"
        
        output = f"找到 {len(results)} 个相关文件：\n\n"
        
        for i, file in enumerate(results, 1):
            output += f"{i}. {file.get('name', '未知文件名')}\n"
            output += f"   路径: {file.get('path', '未知路径')}\n"
            output += f"   分类: {file.get('category', '未分类')}\n"
            output += f"   大小: {file.get('size', 0)} bytes\n"
            output += f"   关键词: {', '.join(file.get('keywords', []))}\n\n"
        
        output += "\n提示：使用 get_css_selector_rules() 获取完整规则"
        
        return output
    except Exception as e:
        return f"搜索知识库索引时出错: {str(e)}"


@tool
def get_css_selector_rules(page: int = 1, runtime=None) -> str:
    """
    获取完整的CSS选择器规则（支持分页，防止内容被截断）
    
    Args:
        page: 页码（从1开始，默认第1页）
    
    Returns:
        指定页的CSS选择器规则内容
    
    Example:
        get_css_selector_rules()  # 获取第1页
        get_css_selector_rules(page=2)  # 获取第2页
    """
    ctx = runtime.context if runtime else new_context(method="get_css_selector_rules")
    
    try:
        splitter = get_content_splitter()
        chunk = splitter.read_file_paginated('assets/css选择器规则.txt', page)
        
        if chunk['total_chunks'] == 0:
            return "CSS选择器规则文件不存在或为空。"
        
        output = splitter.format_file_page_output(chunk, "CSS选择器规则")
        
        # 添加使用提示
        if not chunk.get('has_next', False):
            output += "\n\n[CSS选择器规则已全部显示完毕]\n"
            output += "\n常用提取类型：\n"
            output += "- @text: 提取纯文本内容\n"
            output += "- @html: 提取完整HTML结构\n"
            output += "- @href: 提取链接地址\n"
            output += "- @src: 提取图片地址\n"
            output += "- @ownText: 提取元素自身文本\n"
            output += "- @textNode: 提取文本节点\n"
        
        return output
    except FileNotFoundError:
        return "CSS选择器规则文件不存在，请确保 assets/css选择器规则.txt 文件存在。"
    except ValueError as e:
        return f"页码错误: {str(e)}\n\n总页数: 请先调用 get_css_selector_rules(page=1) 查看总页数"
    except Exception as e:
        return f"获取CSS选择器规则时出错: {str(e)}"


@tool
def get_real_book_source_examples(limit: int = 5, runtime=None) -> str:
    """
    获取真实书源示例（支持分段，防止内容被截断）
    
    Args:
        limit: 最多返回的示例数量（默认5个）
    
    Returns:
        真实书源示例JSON
    
    Example:
        get_real_book_source_examples()
        get_real_book_source_examples(limit=10)
    """
    ctx = runtime.context if runtime else new_context(method="get_real_book_source_examples")
    
    try:
        file_path = 'assets/真实书源模板库.txt'
        
        if not os.path.exists(file_path):
            return "真实书源模板库文件不存在，请确保 assets/真实书源模板库.txt 文件存在。"
        
        splitter = get_content_splitter()
        summary = splitter.get_file_summary(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分段输出
        chunks = splitter.output_in_chunks(content)
        
        if not chunks:
            return "真实书源模板库文件为空。"
        
        output = f"真实书源模板库（共{summary['total_pages']}页，{summary['size']} bytes）：\n\n"
        output += chunks[0]['content']  # 只返回第一段
        
        if len(chunks) > 1:
            output += f"\n\n[内容未完，共{len(chunks)}部分，当前显示第1部分]\n"
            output += "提示：完整内容请直接读取 assets/真实书源模板库.txt 文件"
        
        return output
    except Exception as e:
        return f"获取真实书源示例时出错: {str(e)}"


@tool
def get_book_source_templates(limit: int = 3, runtime=None) -> str:
    """
    获取书源模板（支持分段，防止内容被截断）
    
    Args:
        limit: 最多返回的模板数量（默认3个）
    
    Returns:
        书源模板示例
    
    Example:
        get_book_source_templates()
        get_book_source_templates(limit=5)
    """
    ctx = runtime.context if runtime else new_context(method="get_book_source_templates")
    
    try:
        # 搜索书源模板相关的文件
        searcher = get_knowledge_index_searcher()
        results = searcher.search("书源模板", category="书源模板", limit=limit)
        
        if not results:
            return "未找到书源模板文件。"
        
        output = f"找到 {len(results)} 个书源模板文件：\n\n"
        
        for i, file in enumerate(results, 1):
            output += f"{i}. {file.get('name', '未知文件名')}\n"
            output += f"   路径: {file.get('path', '未知路径')}\n"
            output += f"   大小: {file.get('size', 0)} bytes\n\n"
        
        output += "\n提示：使用 get_real_book_source_examples() 获取具体的模板内容"
        
        return output
    except Exception as e:
        return f"获取书源模板时出错: {str(e)}"


@tool
def list_all_knowledge_files(category: str = "", show_size: bool = True, runtime=None) -> str:
    """
    列出所有知识库文件（支持分类筛选）
    
    Args:
        category: 可选，限定分类（如"CSS选择器"、"书源规则"等）
        show_size: 是否显示文件大小（默认True）
    
    Returns:
        所有知识库文件的列表
    
    Example:
        list_all_knowledge_files()  # 列出所有文件
        list_all_knowledge_files(category="CSS选择器")  # 只列出CSS选择器相关的文件
    """
    ctx = runtime.context if runtime else new_context(method="list_all_knowledge_files")
    
    try:
        searcher = get_knowledge_index_searcher()
        summary = searcher.get_summary()
        
        if category:
            files = searcher.get_files_by_category(category)
        else:
            # 获取所有文件
            files = []
            categories = searcher.get_categories()
            for cat_name in categories.keys():
                files.extend(searcher.get_files_by_category(cat_name))
        
        if not files:
            if category:
                return f"未找到分类为\"{category}\"的文件。\n\n可用分类：\n" + "\n".join(
                    f"- {cat}" for cat in searcher.get_categories().keys()
                )
            else:
                return "知识库中没有文件。"
        
        output = ""
        
        # 显示摘要
        if not category:
            output += f"知识库摘要：\n"
            output += f"- 总文件数: {summary.get('total_files', 0)}\n"
            metadata = searcher.index.get('metadata', {})
            output += f"- 总大小: {metadata.get('total_size_kb', 0) / 1024:.2f} MB\n"
            output += f"- 分类数: {summary.get('categories_count', 0)}\n\n"
        
        # 显示分类统计
        if not category:
            output += "分类统计：\n"
            categories = searcher.get_categories()
            for cat_name, cat_info in categories.items():
                output += f"- {cat_name}: {cat_info.get('count', 0)} 个文件, {cat_info.get('size', 0) / 1024:.2f} KB\n"
            output += "\n"
        
        # 显示文件列表
        output += f"文件列表（共{len(files)}个文件）：\n\n"
        
        for i, file in enumerate(files, 1):
            output += f"{i}. {file.get('name', '未知文件名')}\n"
            output += f"   路径: {file.get('path', '未知路径')}\n"
            if show_size:
                size = file.get('size', 0)
                output += f"   大小: {size} bytes ({size / 1024:.2f} KB)\n"
            output += f"   分类: {file.get('category', '未分类')}\n"
            output += f"   关键词: {', '.join(file.get('keywords', []))}\n\n"
        
        # 标注核心文件
        if not category:
            output += "\n【核心文件】（推荐优先阅读）：\n"
            core_files = [
                "css选择器规则.txt",
                "书源规则：从入门到入土.md",
                "真实书源模板库.txt",
                "真实书源高级功能分析.md",
                "书源输出模板_严格模式.md",
                "Legado书源开发_长记忆系统.md"
            ]
            for core_file in core_files:
                for file in files:
                    if file.get('name', '') == core_file:
                        size = file.get('size', 0)
                        output += f"- {core_file} ({size / 1024:.2f} KB)\n"
                        break
        
        return output
    except Exception as e:
        return f"列出知识库文件时出错: {str(e)}"


@tool
def read_file_paginated(file_path: str, page: int = 1, runtime=None) -> str:
    """
    分页读取文件（防止内容被截断）
    
    Args:
        file_path: 文件路径（相对于assets目录）
        page: 页码（从1开始，默认第1页）
    
    Returns:
        指定页的文件内容
    
    Example:
        read_file_paginated("css选择器规则.txt", page=1)
        read_file_paginated("书源规则：从入门到入土.md", page=2)
    """
    ctx = runtime.context if runtime else new_context(method="read_file_paginated")
    
    try:
        # 如果路径不以assets开头，自动添加
        if not file_path.startswith('assets/'):
            full_path = f'assets/{file_path}'
        else:
            full_path = file_path
        
        splitter = get_content_splitter()
        chunk = splitter.read_file_paginated(full_path, page)
        
        if chunk['total_chunks'] == 0:
            return f"文件不存在或为空: {file_path}"
        
        return splitter.format_file_page_output(chunk, os.path.basename(file_path))
    except FileNotFoundError:
        return f"文件不存在: {file_path}\n\n提示：\n- 检查文件路径是否正确\n- 使用 list_all_knowledge_files() 查看可用文件"
    except ValueError as e:
        return f"页码错误: {str(e)}\n\n总页数: 请先调用 read_file_paginated(\"{file_path}\", page=1) 查看总页数"
    except Exception as e:
        return f"读取文件时出错: {str(e)}"


@tool
def get_file_summary(file_path: str, runtime=None) -> str:
    """
    获取文件摘要信息
    
    Args:
        file_path: 文件路径（相对于assets目录）
    
    Returns:
        文件摘要信息（大小、行数、页数等）
    
    Example:
        get_file_summary("css选择器规则.txt")
    """
    ctx = runtime.context if runtime else new_context(method="get_file_summary")
    
    try:
        # 如果路径不以assets开头，自动添加
        if not file_path.startswith('assets/'):
            full_path = f'assets/{file_path}'
        else:
            full_path = file_path
        
        splitter = get_content_splitter()
        summary = splitter.get_file_summary(full_path)
        
        output = f"文件摘要信息：\n\n"
        output += f"文件名: {summary['name']}\n"
        output += f"路径: {summary['path']}\n"
        output += f"大小: {summary['size']} bytes ({summary['size'] / 1024:.2f} KB)\n"
        output += f"总行数: {summary['total_lines']}\n"
        output += f"总页数: {summary['total_pages']}（每页200行）\n"
        output += f"编码: {summary['encoding']}\n"
        
        return output
    except FileNotFoundError:
        return f"文件不存在: {file_path}"
    except Exception as e:
        return f"获取文件摘要时出错: {str(e)}"


# 导出所有工具
TOOLS = [
    search_knowledge_index,
    get_css_selector_rules,
    get_real_book_source_examples,
    get_book_source_templates,
    list_all_knowledge_files,
    read_file_paginated,
    get_file_summary,
]
