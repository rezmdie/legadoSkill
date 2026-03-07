"""
测试编码检测功能
"""

from src.utils.smart_request import get_smart_request

def test_encoding_detection():
    """测试编码检测功能"""
    
    print("=" * 60)
    print("测试编码检测功能")
    print("=" * 60)
    
    # 测试用例 - 使用 HTTP 避免 SSL 问题
    test_cases = [
        {
            "name": "UTF-8网站（自动检测）",
            "url": "http://httpbin.org/html",
            "method": "GET",
            "charset": None
        },
        {
            "name": "指定GBK编码",
            "url": "http://httpbin.org/html",
            "method": "GET",
            "charset": "gbk"
        },
        {
            "name": "指定UTF-8编码",
            "url": "http://httpbin.org/html",
            "method": "GET",
            "charset": "utf-8"
        }
    ]
    
    requester = get_smart_request()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] {test_case['name']}")
        print("-" * 60)
        
        try:
            result = requester.fetch(
                url=test_case['url'],
                method=test_case['method'],
                charset=test_case['charset'],
                verify_ssl=False
            )
            
            if result['success']:
                print(f"[OK] 请求成功")
                print(f"  - 状态码: {result['status_code']}")
                print(f"  - 检测编码: {result['encoding']}")
                print(f"  - HTML大小: {len(result['html'])} 字符")
                print(f"  - 内容预览: {result['html'][:100]}...")
            else:
                print(f"[FAIL] 请求失败: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"[ERROR] 异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_encoding_detection()
