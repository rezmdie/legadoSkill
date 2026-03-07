#!/usr/bin/env python
"""
MCP服务器启动脚本
禁用日志输出，确保只输出JSON格式的响应
"""
import sys
import os
import logging

# 设置MCP模式环境变量
os.environ['MCP_MODE'] = 'true'
os.environ['COZE_LOG_LEVEL'] = 'CRITICAL'

# 创建日志目录（防止coze_coding_utils报错）
# coze_coding_utils使用硬编码的Linux路径 /tmp/app/work/logs/bypass
# 在Windows上需要创建这个路径
try:
    os.makedirs('/tmp/app/work/logs/bypass', exist_ok=True)
except Exception:
    # 如果无法创建/tmp路径，尝试创建相对路径
    try:
        os.makedirs('tmp/app/work/logs/bypass', exist_ok=True)
    except Exception:
        pass

# 禁用所有日志
logging.disable(logging.CRITICAL)

# 导入uvicorn并启动服务器
if __name__ == "__main__":
    import uvicorn
    # 使用quiet模式启动
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        log_level="critical",
        access_log=False,
        use_colors=False,
        reload=False
    )
