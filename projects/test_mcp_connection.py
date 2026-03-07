#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP服务器连接和工具调用
"""
import asyncio
import json
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """测试MCP服务器"""
    print("=" * 60)
    print("MCP服务器连接测试")
    print("=" * 60)
    
    # 配置服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_server.py"],
        env=None
    )
    
    try:
        # 连接到MCP服务器
        print("\n1. 连接到MCP服务器...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化会话
                await session.initialize()
                print("[OK] 连接成功!")
                
                # 列出所有工具
                print("\n2. 获取可用工具列表...")
                tools_result = await session.list_tools()
                print(f"[OK] 找到 {len(tools_result.tools)} 个工具:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description[:60]}...")
                
                # 测试 get_element_picker_guide 工具（最简单的工具）
                print("\n3. 测试工具调用: get_element_picker_guide")
                result = await session.call_tool(
                    "get_element_picker_guide",
                    arguments={"selector_type": "css"}
                )
                print("[OK] 工具调用成功!")
                print(f"返回内容长度: {len(str(result.content))} 字符")
                
                # 测试 search_knowledge 工具
                print("\n4. 测试工具调用: search_knowledge")
                result = await session.call_tool(
                    "search_knowledge",
                    arguments={"query": "CSS选择器", "top_k": 3}
                )
                print("[OK] 工具调用成功!")
                print(f"返回内容长度: {len(str(result.content))} 字符")
                
                # 列出提示模板
                print("\n5. 获取提示模板列表...")
                prompts_result = await session.list_prompts()
                print(f"[OK] 找到 {len(prompts_result.prompts)} 个提示模板:")
                for prompt in prompts_result.prompts:
                    print(f"  - {prompt.name}: {prompt.description}")
                
                print("\n" + "=" * 60)
                print("[SUCCESS] 所有测试通过! MCP服务器运行正常")
                print("=" * 60)
                
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
