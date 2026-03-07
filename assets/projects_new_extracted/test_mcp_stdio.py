#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动测试MCP服务器的stdio通信
模拟Kilo IDE的连接过程
"""
import sys
import os
import subprocess
import json
import time

print("=" * 60)
print("MCP服务器stdio通信测试")
print("=" * 60)

# 启动MCP服务器
print("\n启动MCP服务器...")
process = subprocess.Popen(
    [sys.executable, "src/mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=os.getcwd(),
    env={**os.environ, "MCP_MODE": "true", "COZE_LOG_LEVEL": "CRITICAL"},
    text=True,
    bufsize=1
)

print(f"进程ID: {process.pid}")

# 发送初始化请求
print("\n发送初始化请求...")
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

try:
    # 发送请求
    request_str = json.dumps(init_request) + "\n"
    print(f"发送: {request_str.strip()}")
    process.stdin.write(request_str)
    process.stdin.flush()
    
    # 等待响应
    print("\n等待响应...")
    time.sleep(2)
    
    # 读取响应
    if process.poll() is None:
        # 尝试读取stdout
        print("\n尝试读取stdout...")
        try:
            # 设置非阻塞读取
            import select
            if select.select([process.stdout], [], [], 1)[0]:
                response = process.stdout.readline()
                print(f"收到响应: {response}")
            else:
                print("没有收到响应（超时）")
        except:
            print("无法读取响应（可能是Windows平台限制）")
        
        # 检查stderr
        print("\n检查stderr...")
        try:
            if select.select([process.stderr], [], [], 0.1)[0]:
                error = process.stderr.read()
                if error:
                    print(f"错误输出: {error}")
        except:
            pass
            
        print("\n服务器仍在运行，手动终止...")
        process.terminate()
        process.wait(timeout=5)
    else:
        print(f"\n服务器已退出，退出码: {process.returncode}")
        stdout, stderr = process.communicate()
        if stdout:
            print(f"标准输出:\n{stdout}")
        if stderr:
            print(f"错误输出:\n{stderr}")
            
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
    process.terminate()
    process.wait()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
