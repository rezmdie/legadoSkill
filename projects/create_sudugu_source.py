#!/usr/bin/env python3
"""
直接为 sudugu.org 创建书源
"""
import asyncio
import json
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.smart_full_analyzer import analyze_complete_book_source

async def main():
    """创建书源"""
    print("=" * 60)
    print("为 https://www.sudugu.org 创建书源")
    print("=" * 60)
    print()
    
    try:
        # 调用完整分析工具
        print("[*] 开始分析网站...")
        result = await analyze_complete_book_source.ainvoke({
            "url": "https://www.sudugu.org",
            "source_name": "速读谷"
        })
        
        print("\n" + "=" * 60)
        print("[OK] 分析完成！")
        print("=" * 60)
        print()
        
        # 保存结果（不打印，避免编码问题）
        output_file = "sudugu_book_source.json"
        
        # 尝试从结果中提取JSON
        if isinstance(result, str):
            # 查找JSON代码块
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_str = result[json_start:json_end].strip()
                
                try:
                    book_source = json.loads(json_str)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(book_source, f, ensure_ascii=False, indent=2)
                    print(f"\n[OK] 书源已保存到: {output_file}")
                except json.JSONDecodeError:
                    print("\n[!] 无法解析JSON，保存原始结果")
                    with open(output_file.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                        f.write(result)
            else:
                with open(output_file.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"\n[OK] 结果已保存到: {output_file.replace('.json', '.txt')}")
        
    except Exception as e:
        print(f"\n[ERROR] 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
