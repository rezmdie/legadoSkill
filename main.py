#!/usr/bin/env python3
"""
MCP Server Main Entry Point
模型上下文协议（MCP）服务器主入口文件
"""

import asyncio
import argparse
import signal
import sys
from pathlib import Path

from mcp_server import MCPServer
from mcp_server.logger import get_logger, setup_logging


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="MCP Server - Model Context Protocol Server")
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Server host address (default: from config or 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port (default: from config or 8080)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file (default: .kilocode/mcp.json)"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Path to system prompt file (default: config/system/prompt.md)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Log level (default: from config or INFO)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=None,
        help="Log directory (default: logs)"
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Enable JSON format logging"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="MCP Server 1.0.0"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = args.log_level or "INFO"
    log_dir = args.log_dir or "logs"
    
    setup_logging(
        log_dir=log_dir,
        level=getattr(logging, log_level),
        json_format=args.json_logs
    )
    
    logger = get_logger("main")
    logger.info("Starting MCP Server...")
    
    # 创建服务器实例
    server = MCPServer(
        config_path=args.config,
        prompt_path=args.prompt
    )
    
    # 设置信号处理
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: signal_handler())
    
    try:
        # 运行服务器
        await server.run_forever(
            host=args.host,
            port=args.port
        )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("MCP Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
