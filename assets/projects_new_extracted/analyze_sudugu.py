#!/usr/bin/env python3
"""
分析 sudugu.org 网站结构
"""
import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.smart_web_analyzer import smart_analyze_website

async def main():
    """分析网站"""
    print("=" * 60)
    print("分析 https://www.sudugu.org 网站结构")
    print("=" * 60)
    print()
    
    try:
        # 分析网站
        print("[*] 开始分析...")
        result = await smart_analyze_website.ainvoke({
            "url": "https://www.sudugu.org",
            "page_type": "all"
        })
        
        # 保存结果
        with open("sudugu_analysis.txt", 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("[OK] 分析完成，结果已保存到: sudugu_analysis.txt")
        
    except Exception as e:
        print(f"[ERROR] 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
