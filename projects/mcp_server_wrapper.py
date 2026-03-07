#!/usr/bin/env python
"""
MCP服务器包装器
将FastAPI应用包装为MCP服务器
"""
import sys
import os
import json
import asyncio
import logging
from typing import Any, Dict, Optional

# 禁用所有日志
logging.disable(logging.CRITICAL)

# 设置环境变量
os.environ['MCP_MODE'] = 'true'
os.environ['COZE_LOG_LEVEL'] = 'CRITICAL'

# 创建日志目录
try:
    os.makedirs('/tmp/app/work/logs/bypass', exist_ok=True)
except Exception:
    try:
        os.makedirs('tmp/app/work/logs/bypass', exist_ok=True)
    except Exception:
        pass

# 导入FastAPI应用
sys.path.insert(0, '.')
from src.main import app

# MCP协议实现
class MCPServer:
    def __init__(self):
        self.tools = self._get_tools()
    
    def _get_tools(self) -> list:
        """获取可用的工具列表"""
        return [
            {
                "name": "smart_fetch_html",
                "description": "智能获取网页HTML，支持GET/POST等各种请求方法",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "请求URL"},
                        "method": {"type": "string", "description": "HTTP方法（默认GET）"},
                        "params": {"type": "string", "description": "URL参数（JSON字符串）"},
                        "data": {"type": "string", "description": "请求体（JSON字符串）"},
                        "headers": {"type": "string", "description": "自定义headers（JSON字符串）"},
                        "cookies": {"type": "string", "description": "Cookies（JSON字符串）"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_full_html",
                "description": "获取网页完整HTML源代码",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "请求URL"},
                        "method": {"type": "string", "description": "HTTP方法（默认GET）"},
                        "params": {"type": "string", "description": "URL参数（JSON字符串）"},
                        "data": {"type": "string", "description": "请求体（JSON字符串）"},
                        "headers": {"type": "string", "description": "自定义headers（JSON字符串）"},
                        "cookies": {"type": "string", "description": "Cookies（JSON字符串）"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "search_knowledge",
                "description": "搜索知识库，查询CSS选择器、书源规则等知识",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "category": {"type": "string", "description": "知识类别（可选）"},
                        "limit": {"type": "integer", "description": "返回结果数量（默认5）"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "smart_web_analyzer",
                "description": "智能分析网站整体结构",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "html": {"type": "string", "description": "HTML内容"},
                        "page_type": {"type": "string", "description": "页面类型（search、list、detail、toc、content等）"}
                    },
                    "required": ["html"]
                }
            },
            {
                "name": "edit_book_source",
                "description": "编辑书源，生成完整的书源JSON",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "complete_source": {"type": "string", "description": "完整书源JSON字符串"}
                    },
                    "required": ["complete_source"]
                }
            },
            {
                "name": "debug_book_source",
                "description": "调试书源，诊断问题并提供修复方案",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "book_source_json": {"type": "string", "description": "书源JSON字符串"},
                        "keyword": {"type": "string", "description": "搜索关键词"},
                        "test_type": {"type": "string", "description": "测试类型（search/book_info/toc/content/full）"}
                    },
                    "required": ["book_source_json"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "legado-book-source-tamer",
                    "version": "1.0.0"
                }
            }
        
        elif method == "tools/list":
            return {
                "tools": self.tools
            }
        
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})
            
            # 调用FastAPI的/run端点
            from httpx import AsyncClient
            async with AsyncClient() as client:
                response = await client.post(
                    "http://localhost:5000/run",
                    json=arguments,
                    timeout=300.0
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(response.json(), ensure_ascii=False, indent=2)
                        }
                    ]
                }
        
        return {
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }

async def main():
    """MCP服务器主函数"""
    import uvicorn
    
    # 启动FastAPI服务器
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="critical",
        access_log=False,
        use_colors=False
    )
    
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
