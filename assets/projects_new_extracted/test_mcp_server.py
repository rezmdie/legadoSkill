#!/usr/bin/env python
"""
MCP服务器测试脚本
捕获所有输出，用于调试MCP服务器启动问题
"""
import sys
import os
import subprocess
import time

print("=" * 60)
print("MCP服务器测试脚本")
print("=" * 60)
print()

# 设置环境变量
env = os.environ.copy()
env['MCP_MODE'] = 'true'
env['COZE_LOG_LEVEL'] = 'CRITICAL'
env['PYTHONPATH'] = '.'
env['COZE_WORKSPACE_PATH'] = '.'

print("环境变量:")
for key, value in env.items():
    if key in ['MCP_MODE', 'COZE_LOG_LEVEL', 'PYTHONPATH', 'COZE_WORKSPACE_PATH']:
        print(f"  {key}={value}")
print()

print("启动MCP服务器...")
print("=" * 60)
print()

# 启动服务器
process = subprocess.Popen(
    [sys.executable, "start_mcp_server.py"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    universal_newlines=True
)

print("服务器已启动，PID:", process.pid)
print("等待服务器启动...")
print("=" * 60)
print()

# 读取输出
try:
    # 等待5秒让服务器启动
    time.sleep(5)
    
    # 检查进程是否还在运行
    if process.poll() is None:
        print("[成功] 服务器正在运行中...")
        print("[提示] 按 Ctrl+C 停止服务器")
        
        # 持续读取输出
        while True:
            output = process.stdout.readline()
            if output:
                print(output, end='')
                sys.stdout.flush()
            
            error = process.stderr.readline()
            if error:
                print("[STDERR]", error, end='')
                sys.stdout.flush()
            
            if process.poll() is not None:
                break
    else:
        print("[错误] 服务器启动失败！")
        print()
        print("STDOUT:")
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout)
        print()
        print("STDERR:")
        if stderr:
            print(stderr)
        print()
        print("返回码:", process.returncode)
        
except KeyboardInterrupt:
    print("\n\n收到中断信号，正在停止服务器...")
    process.terminate()
    process.wait()
    print("服务器已停止")

print()
print("=" * 60)
print("服务器已退出，返回码:", process.returncode)
print("=" * 60)
