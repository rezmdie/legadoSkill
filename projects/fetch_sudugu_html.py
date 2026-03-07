#!/usr/bin/env python3
"""
获取 sudugu.org 首页HTML
"""
import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.smart_fetcher import smart_fetch_html

async def main():
    """获取HTML"""
    print("=" * 60)
    print("获取 https://www.sudugu.org 首页HTML")
    print("=" * 60)
    print()
    
    try:
        # 获取HTML
        print("[*] 正在获取...")
        result = await smart_fetch_html.ainvoke({
            "url": "https://www.sudugu.org",
            "method": "GET",
            "headers": "",
            "data": ""
        })
        
        # 保存结果
        with open("sudugu_html.txt", 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("[OK] HTML已保存到: sudugu_html.txt")
        
    except Exception as e:
        print(f"[ERROR] 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
