"""
测试 Legado 源码搜索功能
验证知识库查询工具能否正确搜索 legado/ 源码
"""

import os
import sys
import io

# 设置 UTF-8 输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置环境变量
os.environ["COZE_WORKSPACE_PATH"] = os.getcwd()

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from tools.knowledge_tools import _lightweight_search

def test_legado_source_search():
    """测试 Legado 源码搜索"""
    print("=" * 80)
    print("测试 Legado 源码搜索功能")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        {
            "name": "搜索 BookSource 类",
            "query": "BookSource",
            "description": "搜索书源相关的类定义"
        },
        {
            "name": "搜索 AnalyzeRule",
            "query": "AnalyzeRule",
            "description": "搜索规则分析相关代码"
        },
        {
            "name": "搜索 CSS 选择器",
            "query": "css selector",
            "description": "搜索 CSS 选择器相关代码"
        },
        {
            "name": "搜索 XPath",
            "query": "xpath",
            "description": "搜索 XPath 相关代码"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"查询: {test_case['query']}")
        print("=" * 80)
        
        try:
            result = _lightweight_search(test_case['query'], limit=3)
            print(result)
            print(f"\n✅ 测试 {i} 完成")
        except Exception as e:
            print(f"\n❌ 测试 {i} 失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("所有测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_legado_source_search()
