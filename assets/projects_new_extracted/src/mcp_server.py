#!/usr/bin/env python3
"""
标准MCP服务器实现
将Legado书源驯兽师的功能暴露为MCP协议服务
"""
import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional
import logging

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))

# 设置环境变量以禁用日志
os.environ['MCP_MODE'] = 'true'
os.environ['COZE_LOG_LEVEL'] = 'CRITICAL'

# 禁用所有日志输出
logging.disable(logging.CRITICAL)

# ============================================================
# 🚨 系统提示词加载 - 必须第一时间读取
# ============================================================
# 导入统一的系统提示词模块
from utils.system_prompt import get_system_prompt, is_system_prompt_loaded

# 获取系统提示词
SYSTEM_PROMPT = get_system_prompt()

if is_system_prompt_loaded():
    print(f"✅ 系统提示词已加载: {len(SYSTEM_PROMPT)} 字符", file=sys.stderr)
else:
    print(f"⚠️ 系统提示词未能加载", file=sys.stderr)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolResult,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
)

# 导入工具 - 使用正确的导入路径
from tools.smart_full_analyzer import analyze_complete_book_source
from tools.smart_web_analyzer import smart_analyze_website
from tools.smart_fetcher import smart_fetch_html
from tools.legado_debug_tools import debug_book_source
from tools.book_source_editor import edit_book_source
from tools.selector_validator import validate_selector_on_real_web
from tools.knowledge_tools import search_knowledge
from tools.element_picker_guide import element_picker_guide

# 导入新增的高级工具
from tools.collaborative_edit import validate_correction, test_manual_rule, analyze_user_html
from tools.user_intervention import (
    manual_intervention_mode, inject_custom_js, correct_selector,
    manual_define_rule, provide_html_sample, save_experience, record_solution
)
from tools.book_source_html_editor import generate_html_editor
from tools.knowledge_auditor import audit_knowledge_base, get_saved_html, list_saved_htmls
from tools.knowledge_index_tool import (
    search_knowledge_index, get_css_selector_rules, get_real_book_source_examples,
    get_book_source_templates, list_all_knowledge_files, read_file_paginated, get_file_summary
)

# 导入知识库初始化模块
from utils.knowledge_initializer import (
    initialize_knowledge_base,
    is_knowledge_initialized,
    get_learning_stats,
    search_knowledge as search_knowledge_base,
    get_knowledge_learner
)

# 创建MCP服务器实例
app = Server("legado-book-source-tamer")


# 定义所有可用的工具
TOOLS = [
    Tool(
        name="create_book_source",
        description="为指定网站创建Legado书源。自动分析网站结构，生成完整的书源JSON配置。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "目标网站URL，例如：https://www.example.com"
                },
                "source_name": {
                    "type": "string",
                    "description": "书源名称（可选）"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="analyze_website",
        description="智能分析网站结构，识别搜索页、列表页、详情页、目录页和内容页的关键元素。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要分析的网站URL"
                },
                "page_type": {
                    "type": "string",
                    "enum": ["search", "list", "detail", "toc", "content", "all"],
                    "description": "页面类型：search(搜索页), list(列表页), detail(详情页), toc(目录页), content(内容页), all(全部分析)"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="fetch_html",
        description="智能获取网页HTML内容，支持GET/POST请求、自定义headers、cookies等。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "目标URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "description": "HTTP方法，默认GET"
                },
                "headers": {
                    "type": "object",
                    "description": "自定义HTTP headers"
                },
                "data": {
                    "type": "object",
                    "description": "POST请求的数据"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="debug_book_source",
        description="调试书源规则，测试搜索、列表、详情、目录、内容等规则是否正确。",
        inputSchema={
            "type": "object",
            "properties": {
                "book_source_json": {
                    "type": "string",
                    "description": "书源JSON字符串"
                },
                "test_url": {
                    "type": "string",
                    "description": "测试URL"
                },
                "rule_type": {
                    "type": "string",
                    "enum": ["search", "bookList", "bookInfo", "tocUrl", "chapterList", "content"],
                    "description": "要测试的规则类型"
                }
            },
            "required": ["book_source_json", "test_url", "rule_type"]
        }
    ),
    Tool(
        name="edit_book_source",
        description="编辑和修改书源配置，支持修改规则、添加字段、调整参数等。",
        inputSchema={
            "type": "object",
            "properties": {
                "book_source_json": {
                    "type": "string",
                    "description": "原始书源JSON字符串"
                },
                "modifications": {
                    "type": "object",
                    "description": "要修改的内容，键为字段路径，值为新值"
                }
            },
            "required": ["book_source_json", "modifications"]
        }
    ),
    Tool(
        name="validate_selector",
        description="验证CSS选择器或XPath表达式是否正确，测试能否提取到目标内容。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "测试URL"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS选择器或XPath表达式"
                },
                "selector_type": {
                    "type": "string",
                    "enum": ["css", "xpath", "json"],
                    "description": "选择器类型"
                }
            },
            "required": ["url", "selector"]
        }
    ),
    Tool(
        name="search_knowledge",
        description="搜索Legado书源开发知识库，获取相关文档和示例。知识库包含24.93MB的文档，167个文件。",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认5"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_element_picker_guide",
        description="获取元素选择器使用指南，包括CSS选择器、XPath、JSONPath等的使用方法。",
        inputSchema={
            "type": "object",
            "properties": {
                "selector_type": {
                    "type": "string",
                    "enum": ["css", "xpath", "json", "all"],
                    "description": "选择器类型"
                }
            },
            "required": []
        }
    ),
    # 协同编辑工具
    Tool(
        name="validate_correction",
        description="验证用户修正的选择器是否正确，在真实网页上测试选择器能否提取到目标内容。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "目标网页URL"},
                "selector": {"type": "string", "description": "用户修正后的选择器"},
                "field_name": {"type": "string", "description": "字段名称"}
            },
            "required": ["url", "selector", "field_name"]
        }
    ),
    Tool(
        name="test_manual_rule",
        description="测试手动定义的规则，在真实网页上测试规则中的所有选择器是否正确。",
        inputSchema={
            "type": "object",
            "properties": {
                "rule_name": {"type": "string", "description": "规则名称"},
                "rule_content": {"type": "string", "description": "规则内容（JSON格式）"},
                "test_url": {"type": "string", "description": "测试网页URL"}
            },
            "required": ["rule_name", "rule_content", "test_url"]
        }
    ),
    Tool(
        name="analyze_user_html",
        description="分析用户提供的HTML样本，推荐选择器。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "网页URL"},
                "html_content": {"type": "string", "description": "HTML源代码"},
                "field_name": {"type": "string", "description": "要提取的字段（可选）"}
            },
            "required": ["url", "html_content"]
        }
    ),
    # 人工干预工具
    Tool(
        name="manual_intervention_mode",
        description="启动人工干预模式，当AI遇到复杂情况无法处理时使用。",
        inputSchema={
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "启动人工干预的原因"},
                "ai_suggestion": {"type": "string", "description": "AI的初步建议（可选）"}
            },
            "required": ["reason"]
        }
    ),
    Tool(
        name="inject_custom_js",
        description="注入自定义JavaScript代码，用于处理复杂的JS逻辑。",
        inputSchema={
            "type": "object",
            "properties": {
                "js_code": {"type": "string", "description": "JavaScript代码"},
                "description": {"type": "string", "description": "代码说明"}
            },
            "required": ["js_code"]
        }
    ),
    Tool(
        name="correct_selector",
        description="修正选择器，当AI识别的选择器不正确时手动修正。",
        inputSchema={
            "type": "object",
            "properties": {
                "field_name": {"type": "string", "description": "字段名称"},
                "original_selector": {"type": "string", "description": "AI原来识别的选择器"},
                "corrected_selector": {"type": "string", "description": "修正后的选择器"},
                "reason": {"type": "string", "description": "修正原因"}
            },
            "required": ["field_name", "original_selector", "corrected_selector", "reason"]
        }
    ),
    Tool(
        name="manual_define_rule",
        description="手动定义规则，当AI生成的规则不符合预期时使用。",
        inputSchema={
            "type": "object",
            "properties": {
                "rule_name": {"type": "string", "description": "规则名称"},
                "rule_content": {"type": "string", "description": "规则内容（JSON格式）"},
                "rule_type": {"type": "string", "description": "规则类型"},
                "description": {"type": "string", "description": "规则说明"}
            },
            "required": ["rule_name", "rule_content"]
        }
    ),
    Tool(
        name="provide_html_sample",
        description="提供HTML样本，当AI无法访问网页时手动提供HTML。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "网页URL"},
                "html_content": {"type": "string", "description": "HTML源代码"},
                "field_name": {"type": "string", "description": "要提取的字段（可选）"}
            },
            "required": ["url", "html_content"]
        }
    ),
    Tool(
        name="save_experience",
        description="保存经验到知识库，成功解决问题后保存经验供下次学习。",
        inputSchema={
            "type": "object",
            "properties": {
                "experience_type": {"type": "string", "description": "经验类型"},
                "problem": {"type": "string", "description": "问题描述"},
                "solution": {"type": "string", "description": "解决方案"},
                "tags": {"type": "string", "description": "标签（逗号分隔）"}
            },
            "required": ["experience_type", "problem", "solution"]
        }
    ),
    Tool(
        name="record_solution",
        description="记录解决方案，记录针对特定网站的解决方案。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "网站URL"},
                "problem": {"type": "string", "description": "问题描述"},
                "solution": {"type": "string", "description": "解决方案"},
                "rule_snippet": {"type": "string", "description": "规则片段（可选）"}
            },
            "required": ["url", "problem", "solution"]
        }
    ),
    # HTML编辑器工具
    Tool(
        name="generate_html_editor",
        description="生成可视化HTML书源编辑器，在浏览器中编辑书源。",
        inputSchema={
            "type": "object",
            "properties": {
                "book_source_json": {"type": "string", "description": "书源JSON字符串（可选，用于预填充）"}
            },
            "required": []
        }
    ),
    # 知识库审查工具
    Tool(
        name="audit_knowledge_base",
        description="审查知识库，验证知识库内容是否适用于真实HTML。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "网页URL"},
                "html": {"type": "string", "description": "HTML内容（可选）"},
                "categories": {"type": "string", "description": "要审查的类别（逗号分隔）"}
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="get_saved_html",
        description="获取已保存的HTML，获取之前永久保存的HTML源代码。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "网页URL"}
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="list_saved_htmls",
        description="列出所有已保存的HTML文件。",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # 知识库索引工具
    Tool(
        name="search_knowledge_index",
        description="搜索知识库索引，快速搜索知识库文件。",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "category": {"type": "string", "description": "限定分类（可选）"},
                "limit": {"type": "integer", "description": "最大返回结果数（默认10）"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_css_selector_rules",
        description="获取CSS选择器规则（支持分页，防止内容被截断）。",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {"type": "integer", "description": "页码（从1开始，默认第1页）"}
            },
            "required": []
        }
    ),
    Tool(
        name="get_real_book_source_examples",
        description="获取真实书源示例（支持分段，防止内容被截断）。",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "最多返回的示例数量（默认5个）"}
            },
            "required": []
        }
    ),
    Tool(
        name="get_book_source_templates",
        description="获取书源模板（支持分段，防止内容被截断）。",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "最多返回的模板数量（默认3个）"}
            },
            "required": []
        }
    ),
    Tool(
        name="list_all_knowledge_files",
        description="列出所有知识库文件（支持分类筛选）。",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "限定分类（可选）"},
                "show_size": {"type": "boolean", "description": "是否显示文件大小（默认True）"}
            },
            "required": []
        }
    ),
    Tool(
        name="read_file_paginated",
        description="分页读取文件（防止内容被截断）。",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径（相对于assets目录）"},
                "page": {"type": "integer", "description": "页码（从1开始，默认第1页）"}
            },
            "required": ["file_path"]
        }
    ),
    Tool(
        name="get_file_summary",
        description="获取文件摘要信息（大小、行数、页数等）。",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径（相对于assets目录）"}
            },
            "required": ["file_path"]
        }
    )
]


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """调用工具"""
    import time
    from utils.tool_tracker import track_tool_call
    
    start_time = time.time()
    
    try:
        # 🚨 确保知识库已初始化
        if not is_knowledge_initialized():
            print("⚠️ 知识库未初始化，正在初始化...", file=sys.stderr)
            initialize_knowledge_base()
        
        result = None
        
        # 在调用分析工具前，先检查知识库并提供相关知识
        knowledge_context = ""
        
        # 添加系统提示词上下文（仅在创建书源时）
        system_context = ""
        if name == "create_book_source" and SYSTEM_PROMPT:
            system_context = f"""
## 🚨 系统核心规则（必须遵守）

以下是系统提示词的关键要点，所有操作都必须严格遵守：

### 📋 工作流程（三阶段）
1. **第一阶段：收集信息**
   - 调用 search_knowledge 查询知识库
   - 调用 smart_fetch_html 获取真实HTML
   - 分析HTML结构
   - 记录所有信息

2. **第二阶段：严格审查**
   - 根据知识库、真实HTML和真实模板编写规则
   - 验证规则语法
   - 处理特殊情况

3. **第三阶段：创建书源**
   - 一次性调用 edit_book_source
   - 输出完整JSON

### ⚠️ 核心约束
- ❌ 禁止使用 `prevContentUrl` 字段
- ❌ 禁止使用 `:contains()` 伪类选择器
- ❌ 禁止使用 `:first-child/:last-child`，应使用数字索引（.0, .-1）
- ✅ 必须先查询知识库再编写规则
- ✅ 必须获取真实HTML再编写规则
- ✅ 必须参考真实书源模板

完整系统提示词已加载，共 {len(SYSTEM_PROMPT)} 字符。

---
"""
        
        if name == "create_book_source":
            # 🚨 第一阶段：收集信息（严格按照系统提示词）
            # 必须先调用知识库查询工具（第一步）
            knowledge_context = ""
            
            # 1. 调用search_knowledge查询CSS选择器规则（使用知识库初始化模块）
            try:
                css_results = search_knowledge_base("CSS选择器格式 提取类型 @text @html @ownText @textNode @href @src", limit=3)
                if css_results:
                    knowledge_context += f"## 📚 CSS选择器规则（第一步）\n\n"
                    for i, result in enumerate(css_results, 1):
                        knowledge_context += f"{i}. {result.title}\n"
                        knowledge_context += f"   来源: {result.source_file}\n"
                        knowledge_context += f"   内容: {result.content[:200]}...\n\n"
                else:
                    knowledge_context += "⚠️ CSS选择器规则查询失败\n\n"
            except Exception as e:
                knowledge_context += f"⚠️ CSS选择器规则查询失败: {e}\n\n"
            
            # 2. 调用get_real_book_source_examples查询真实书源示例（第二步）
            try:
                examples_result = await get_real_book_source_examples.ainvoke({"limit": 3})
                if examples_result and not examples_result.startswith("[ERROR]"):
                    knowledge_context += f"## 📚 真实书源示例（第二步）\n\n{examples_result}\n\n---\n"
            except Exception as e:
                knowledge_context += "⚠️ 真实书源示例查询失败\n\n"
            
            # 3. 调用get_book_source_templates查询书源模板（第三步）
            try:
                templates_result = await get_book_source_templates.ainvoke({"limit": 3})
                if templates_result and not templates_result.startswith("[ERROR]"):
                    knowledge_context += f"## 📚 书源模板（第三步）\n\n{templates_result}\n\n---\n"
            except Exception as e:
                knowledge_context += "⚠️ 书源模板查询失败\n\n"
            
            # 4. 调用get_css_selector_rules获取完整规则（第四步）
            try:
                rules_result = await get_css_selector_rules.ainvoke({"page": 1})
                if rules_result and not rules_result.startswith("[ERROR]"):
                    knowledge_context += f"## 📚 CSS选择器完整规则（第四步）\n\n{rules_result}\n\n---\n"
            except Exception as e:
                knowledge_context += "⚠️ CSS选择器规则查询失败\n\n"
            
            # 5. 调用search_knowledge查询134个真实书源分析结果（第五步）
            try:
                analysis_results = search_knowledge_base("134个真实书源分析 常用选择器 提取类型 正则模式", limit=3)
                if analysis_results:
                    knowledge_context += f"## 📚 134个真实书源分析结果（第五步）\n\n"
                    for i, result in enumerate(analysis_results, 1):
                        knowledge_context += f"{i}. {result.title}\n"
                        knowledge_context += f"   来源: {result.source_file}\n"
                        knowledge_context += f"   内容: {result.content[:200]}...\n\n"
                else:
                    knowledge_context += "⚠️ 134个真实书源分析结果查询失败\n\n"
            except Exception as e:
                knowledge_context += f"⚠️ 134个真实书源分析结果查询失败: {e}\n\n"
        
        # 直接调用对应的工具函数
        if name == "create_book_source":
            # 使用完整分析工具创建书源
            result = await analyze_complete_book_source.ainvoke({
                "url": arguments.get("url"),
                "source_name": arguments.get("source_name", "")
            })
        
        elif name == "analyze_website":
            # 使用智能网站分析工具
            result = await smart_analyze_website.ainvoke({
                "url": arguments.get("url"),
                "page_type": arguments.get("page_type", "all")
            })
        
        elif name == "fetch_html":
            # 使用智能获取工具
            # 将对象转换为JSON字符串
            headers = arguments.get("headers", {})
            data = arguments.get("data", {})
            result = await smart_fetch_html.ainvoke({
                "url": arguments.get("url"),
                "method": arguments.get("method", "GET"),
                "headers": json.dumps(headers) if headers else "",
                "data": json.dumps(data) if data else ""
            })
        
        elif name == "debug_book_source":
            # 使用调试工具
            result = await debug_book_source.ainvoke({
                "book_source_json": arguments.get("book_source_json"),
                "test_url": arguments.get("test_url"),
                "rule_type": arguments.get("rule_type")
            })
        
        elif name == "edit_book_source":
            # 使用编辑工具
            result = await edit_book_source.ainvoke({
                "book_source_json": arguments.get("book_source_json"),
                "modifications": arguments.get("modifications", {})
            })
        
        elif name == "validate_selector":
            # 使用选择器验证工具
            result = await validate_selector_on_real_web.ainvoke({
                "url": arguments.get("url"),
                "selector": arguments.get("selector"),
                "selector_type": arguments.get("selector_type", "css")
            })
        
        elif name == "search_knowledge":
            # 使用知识库搜索工具
            result = await search_knowledge.ainvoke({
                "query": arguments.get("query"),
                "top_k": arguments.get("top_k", 5)
            })
        
        elif name == "get_element_picker_guide":
            # 使用元素选择器指南工具
            result = await element_picker_guide.ainvoke({
                "selector_type": arguments.get("selector_type", "all")
            })
        
        # 协同编辑工具
        elif name == "validate_correction":
            result = validate_correction(
                url=arguments.get("url"),
                selector=arguments.get("selector"),
                field_name=arguments.get("field_name")
            )
        
        elif name == "test_manual_rule":
            result = test_manual_rule(
                rule_name=arguments.get("rule_name"),
                rule_content=arguments.get("rule_content"),
                test_url=arguments.get("test_url")
            )
        
        elif name == "analyze_user_html":
            result = analyze_user_html(
                url=arguments.get("url"),
                html_content=arguments.get("html_content"),
                field_name=arguments.get("field_name", "")
            )
        
        # 人工干预工具
        elif name == "manual_intervention_mode":
            result = manual_intervention_mode(
                reason=arguments.get("reason"),
                ai_suggestion=arguments.get("ai_suggestion", "")
            )
        
        elif name == "inject_custom_js":
            result = inject_custom_js(
                js_code=arguments.get("js_code"),
                description=arguments.get("description", "")
            )
        
        elif name == "correct_selector":
            result = correct_selector(
                field_name=arguments.get("field_name"),
                original_selector=arguments.get("original_selector"),
                corrected_selector=arguments.get("corrected_selector"),
                reason=arguments.get("reason")
            )
        
        elif name == "manual_define_rule":
            result = manual_define_rule(
                rule_name=arguments.get("rule_name"),
                rule_content=arguments.get("rule_content"),
                rule_type=arguments.get("rule_type", "ruleBookInfo"),
                description=arguments.get("description", "")
            )
        
        elif name == "provide_html_sample":
            result = provide_html_sample(
                url=arguments.get("url"),
                html_content=arguments.get("html_content"),
                field_name=arguments.get("field_name", "")
            )
        
        elif name == "save_experience":
            result = save_experience(
                experience_type=arguments.get("experience_type"),
                problem=arguments.get("problem"),
                solution=arguments.get("solution"),
                tags=arguments.get("tags", "")
            )
        
        elif name == "record_solution":
            result = record_solution(
                url=arguments.get("url"),
                problem=arguments.get("problem"),
                solution=arguments.get("solution"),
                rule_snippet=arguments.get("rule_snippet", "")
            )
        
        # HTML编辑器工具
        elif name == "generate_html_editor":
            result = generate_html_editor(
                book_source_json=arguments.get("book_source_json", "")
            )
        
        # 知识库审查工具
        elif name == "audit_knowledge_base":
            result = audit_knowledge_base(
                url=arguments.get("url"),
                html=arguments.get("html", ""),
                categories=arguments.get("categories", "")
            )
        
        elif name == "get_saved_html":
            result = get_saved_html(
                url=arguments.get("url")
            )
        
        elif name == "list_saved_htmls":
            result = list_saved_htmls()
        
        # 知识库索引工具
        elif name == "search_knowledge_index":
            result = search_knowledge_index(
                query=arguments.get("query"),
                category=arguments.get("category", ""),
                limit=arguments.get("limit", 10)
            )
        
        elif name == "get_css_selector_rules":
            result = get_css_selector_rules(
                page=arguments.get("page", 1)
            )
        
        elif name == "get_real_book_source_examples":
            result = get_real_book_source_examples(
                limit=arguments.get("limit", 5)
            )
        
        elif name == "get_book_source_templates":
            result = get_book_source_templates(
                limit=arguments.get("limit", 3)
            )
        
        elif name == "list_all_knowledge_files":
            result = list_all_knowledge_files(
                category=arguments.get("category", ""),
                show_size=arguments.get("show_size", True)
            )
        
        elif name == "read_file_paginated":
            result = read_file_paginated(
                file_path=arguments.get("file_path"),
                page=arguments.get("page", 1)
            )
        
        elif name == "get_file_summary":
            result = get_file_summary(
                file_path=arguments.get("file_path")
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"未知工具: {name}")],
                isError=True
            )
        
        # 格式化返回结果
        if isinstance(result, dict):
            result_text = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            result_text = str(result)
        
        # 将系统上下文和知识库上下文添加到结果前面
        final_result = system_context + knowledge_context + result_text
        
        # 记录工具调用
        duration = time.time() - start_time
        track_tool_call(name, arguments, result_text, duration)
        
        return CallToolResult(
            content=[TextContent(type="text", text=final_result)],
            isError=False
        )
    
    except Exception as e:
        error_msg = f"工具调用失败: {str(e)}"
        import traceback
        error_msg += f"\n{traceback.format_exc()}"
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )


@app.list_prompts()
async def list_prompts() -> List[Prompt]:
    """列出所有可用的提示模板"""
    return [
        Prompt(
            name="create_book_source",
            description="创建书源的完整工作流程提示",
            arguments=[
                PromptArgument(
                    name="url",
                    description="目标网站URL",
                    required=True
                )
            ]
        ),
        Prompt(
            name="debug_book_source",
            description="调试书源的提示模板",
            arguments=[
                PromptArgument(
                    name="book_source",
                    description="书源JSON",
                    required=True
                ),
                PromptArgument(
                    name="issue",
                    description="遇到的问题",
                    required=True
                )
            ]
        )
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
    """获取提示模板"""
    if name == "create_book_source":
        url = arguments.get("url", "")
        return GetPromptResult(
            description="创建书源的完整工作流程",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""我需要为网站 {url} 创建一个Legado书源。

请按照以下步骤进行：

1. 首先使用 fetch_html 工具获取网站首页HTML
2. 使用 analyze_website 工具分析网站结构
3. 根据分析结果，使用 create_book_source 工具生成书源
4. 使用 debug_book_source 工具测试书源规则
5. 如果有问题，使用 edit_book_source 工具修改
6. 最终输出完整的书源JSON

请开始执行。"""
                    )
                )
            ]
        )
    
    elif name == "debug_book_source":
        book_source = arguments.get("book_source", "")
        issue = arguments.get("issue", "")
        return GetPromptResult(
            description="调试书源问题",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""我的书源遇到了问题：{issue}

书源配置：
{book_source}

请帮我：
1. 使用 debug_book_source 工具测试相关规则
2. 使用 validate_selector 工具验证选择器
3. 使用 search_knowledge 工具查找相关文档
4. 提供修复建议
5. 使用 edit_book_source 工具修复问题

请开始诊断。"""
                    )
                )
            ]
        )
    
    else:
        raise ValueError(f"未知提示模板: {name}")


async def main():
    """启动MCP服务器"""
    # 设置 UTF-8 编码输出（解决 Windows 控制台编码问题）
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 🚨 启动前再次确认系统提示词已加载
    if not is_system_prompt_loaded():
        print("⚠️ 系统提示词未加载", file=sys.stderr)
    
    if is_system_prompt_loaded():
        print(f"✅ MCP服务器启动 - 系统提示词已就绪 ({len(SYSTEM_PROMPT)} 字符)", file=sys.stderr)
    else:
        print("❌ 警告：系统提示词未能加载！", file=sys.stderr)
    
    # 🧠 初始化知识库（重要！）
    print("🧠 正在初始化知识库...", file=sys.stderr)
    knowledge_stats = initialize_knowledge_base()
    
    if 'error' in knowledge_stats:
        print(f"❌ 知识库初始化失败: {knowledge_stats['error']}", file=sys.stderr)
    else:
        print(f"✅ 知识库初始化成功！", file=sys.stderr)
        print(f"   - 处理文件: {knowledge_stats.get('total_files', 0)}", file=sys.stderr)
        print(f"   - 学习条目: {knowledge_stats.get('learned_entries', 0)}", file=sys.stderr)
        print(f"   - 书源数量: {knowledge_stats.get('book_sources', 0)}", file=sys.stderr)
        print(f"   - 模式数量: {knowledge_stats.get('patterns', 0)}", file=sys.stderr)
        print(f"   - 选择器数量: {knowledge_stats.get('selectors', 0)}", file=sys.stderr)
    
    # 使用stdio传输
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
