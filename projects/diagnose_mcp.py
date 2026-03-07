#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器诊断工具
检查MCP服务器是否能正常启动
"""
import sys
import os
import subprocess
import json

print("=" * 60)
print("MCP服务器诊断工具")
print("=" * 60)

# 1. 检查Python版本
print("\n1. 检查Python版本...")
print(f"   Python版本: {sys.version}")
print(f"   Python路径: {sys.executable}")

# 2. 检查工作目录
print("\n2. 检查工作目录...")
cwd = os.getcwd()
print(f"   当前目录: {cwd}")

# 3. 检查MCP服务器文件
print("\n3. 检查MCP服务器文件...")
mcp_server_path = os.path.join(cwd, "src", "mcp_server.py")
if os.path.exists(mcp_server_path):
    print(f"   [OK] 找到MCP服务器: {mcp_server_path}")
else:
    print(f"   [ERROR] 未找到MCP服务器: {mcp_server_path}")
    sys.exit(1)

# 4. 检查依赖
print("\n4. 检查依赖...")
try:
    import mcp
    print(f"   [OK] mcp模块已安装")
except ImportError:
    print(f"   [ERROR] mcp模块未安装，请运行: pip install mcp")
    sys.exit(1)

try:
    from langchain_core.tools import tool
    print(f"   [OK] langchain_core已安装")
except ImportError:
    print(f"   [ERROR] langchain_core未安装")
    sys.exit(1)

# 5. 检查MCP配置文件
print("\n5. 检查MCP配置文件...")
mcp_config_path = os.path.join(cwd, ".kilocode", "mcp.json")
if os.path.exists(mcp_config_path):
    print(f"   [OK] 找到配置文件: {mcp_config_path}")
    with open(mcp_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        print(f"   配置内容:")
        print(f"   {json.dumps(config, indent=2, ensure_ascii=False)}")
else:
    print(f"   [ERROR] 未找到配置文件: {mcp_config_path}")

# 6. 尝试启动MCP服务器（测试模式）
print("\n6. 测试MCP服务器启动...")
print("   提示: 按Ctrl+C停止测试")
print("   如果看到服务器输出，说明启动成功")
print("-" * 60)

try:
    # 启动服务器进程
    process = subprocess.Popen(
        [sys.executable, mcp_server_path],
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "MCP_MODE": "true", "COZE_LOG_LEVEL": "CRITICAL"}
    )
    
    # 等待一小段时间看是否有错误
    import time
    time.sleep(2)
    
    if process.poll() is None:
        print("   [OK] MCP服务器进程正在运行")
        print("   进程ID:", process.pid)
        process.terminate()
        process.wait()
    else:
        print("   [ERROR] MCP服务器启动失败")
        stdout, stderr = process.communicate()
        if stderr:
            print("   错误信息:")
            print(stderr.decode('utf-8', errors='ignore'))
        sys.exit(1)
        
except Exception as e:
    print(f"   [ERROR] 启动测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] 所有诊断检查通过!")
print("=" * 60)
print("\n下一步:")
print("1. 在Kilo IDE中点击'刷新 MCP 服务器'")
print("2. 或者重启Kilo IDE")
print("3. 检查MCP服务器是否显示为'Connected'")
