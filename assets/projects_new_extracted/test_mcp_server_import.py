"""
测试MCP服务器
"""
import sys
import os
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置环境变量
os.environ['MCP_MODE'] = 'true'
os.environ['COZE_LOG_LEVEL'] = 'CRITICAL'

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在导入MCP服务器模块...")
    from src.mcp_server import app, TOOLS
    
    print("[OK] MCP服务器模块导入成功")
    print(f"[OK] 服务器名称: {app.name}")
    print(f"[OK] 可用工具数量: {len(TOOLS)}")
    print("\n可用工具列表:")
    for i, tool in enumerate(TOOLS, 1):
        print(f"  {i}. {tool.name} - {tool.description}")
    
    print("\n[OK] MCP服务器配置正确，可以启动")
    print("\n使用方法:")
    print("  在Kilo中重新加载MCP服务器即可使用")
    
except Exception as e:
    print(f"[ERROR] 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
