"""
知识库搜索工具
用于搜索Legado书源相关的知识库内容
"""

import os
import json
import re
from langchain.tools import tool, ToolRuntime


@tool
def search_knowledge(query: str, top_k: int = 3, runtime: ToolRuntime = None) -> str:
    """
    搜索Legado书源知识库

    Args:
        query: 搜索查询文本
        top_k: 返回结果数量，默认为3

    Returns:
        搜索结果字符串
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        assets_path = os.path.join(workspace_path, "assets")

        # 知识库文件列表
        knowledge_files = [
            "legado_knowledge_base.md",
            "css选择器规则.txt",
            "书源规则：从入门到入土.md"
        ]

        results = []

        # 搜索每个知识库文件
        for filename in knowledge_files:
            file_path = os.path.join(assets_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 搜索包含查询关键词的段落
                paragraphs = content.split('\n\n')
                matches = []

                for para in paragraphs:
                    if query.lower() in para.lower():
                        matches.append(para.strip())

                if matches:
                    results.append(f"\n## 来自 {filename}\n\n")
                    # 限制返回结果数量
                    for match in matches[:top_k]:
                        results.append(match + "\n\n")

        if results:
            return "".join(results)
        else:
            # 如果没有找到匹配，返回知识库概览
            overview = f"""未找到关于"{query}"的具体内容。

以下是可用的知识库文件：

1. **legado_knowledge_base.md** - 核心数据结构和规则定义
   - BookSource类结构
   - CSS选择器规则
   - JSOUP Default语法
   - 正则表达式规则

2. **css选择器规则.txt** - CSS选择器语法详解
   - 提取类型：@text, @html, @ownText, @textNode
   - 属性提取：@href, @src, @属性名
   - 正则表达式：##正则表达式##替换内容

3. **书源规则：从入门到入土.md** - 完整规则说明
   - 语法说明
   - 特殊规则
   - 实战案例

请尝试搜索更具体的关键词，如：
- "CSS选择器"
- "searchUrl"
- "ruleSearch"
- "@text"
"""
            return overview

    except Exception as e:
        return f"搜索知识库时发生错误：{str(e)}"
