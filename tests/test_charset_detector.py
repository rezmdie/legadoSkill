"""
测试编码检测工具
"""

import sys
import os
import json

# 添加项目路径到 Python 路径
workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

# 添加 src 目录到 Python 路径
src_path = os.path.join(workspace_path, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.tools.charset_detector import (
    detect_from_headers,
    detect_from_meta,
    detect_by_content,
    detect_by_chinese_characters,
    detect_charset,
)


def test_detect_from_headers():
    """测试从 HTTP 响应头检测编码"""
    print("=" * 60)
    print("测试 1: 从 HTTP 响应头检测编码")
    print("=" * 60)

    class MockResponse:
        def __init__(self, headers):
            self.headers = headers

    # 测试用例
    test_cases = [
        ({"Content-Type": "text/html; charset=gbk"}, "gbk"),
        ({"Content-Type": "text/html; charset=UTF-8"}, "utf-8"),
        ({"Content-Type": "text/html; charset=GB2312"}, "gbk"),
        ({"Content-Type": "text/html"}, None),
        ({}, None),
    ]

    for i, (headers, expected) in enumerate(test_cases, 1):
        response = MockResponse(headers)
        result = detect_from_headers(response)
        status = "✓" if result == expected else "✗"
        print(f"{status} 测试用例 {i}: {headers}")
        print(f"   期望: {expected}, 实际: {result}")
        print()

    print()


def test_detect_from_meta():
    """测试从 HTML meta 标签检测编码"""
    print("=" * 60)
    print("测试 2: 从 HTML meta 标签检测编码")
    print("=" * 60)

    # 测试用例
    test_cases = [
        ('<meta charset="gbk">', "gbk"),
        ('<meta charset="utf-8">', "utf-8"),
        ('<meta charset="GB2312">', "gbk"),
        ('<meta http-equiv="Content-Type" content="text/html; charset=gbk">', "gbk"),
        ('<html><head><meta charset="utf-8"></head></html>', "utf-8"),
        ('<html><body>没有 meta 标签</body></html>', None),
    ]

    for i, (html, expected) in enumerate(test_cases, 1):
        result = detect_from_meta(html)
        status = "✓" if result == expected else "✗"
        print(f"{status} 测试用例 {i}: {html[:50]}...")
        print(f"   期望: {expected}, 实际: {result}")
        print()

    print()


def test_detect_by_content():
    """测试通过内容分析检测编码"""
    print("=" * 60)
    print("测试 3: 通过内容分析检测编码 (chardet)")
    print("=" * 60)

    # 测试用例
    test_cases = [
        ("这是一个UTF-8编码的中文内容。", "utf-8"),
        ("<html><head><meta charset='gbk'></head><body>GBK编码内容</body></html>", "gbk"),
    ]

    for i, (text, expected) in enumerate(test_cases, 1):
        charset, confidence = detect_by_content(text)
        print(f"测试用例 {i}: {text[:50]}...")
        print(f"   检测结果: {charset} (置信度: {confidence:.2f})")
        print(f"   期望: {expected}")
        print()

    print()


def test_detect_by_chinese_characters():
    """测试通过中文字符特征检测编码"""
    print("=" * 60)
    print("测试 4: 通过中文字符特征检测编码")
    print("=" * 60)

    # 测试用例
    test_cases = [
        ("这是一个UTF-8编码的中文内容。", "utf-8"),
    ]

    for i, (text, expected) in enumerate(test_cases, 1):
        charset, confidence = detect_by_chinese_characters(text)
        print(f"测试用例 {i}: {text}")
        print(f"   检测结果: {charset} (置信度: {confidence:.2f})")
        print(f"   期望: {expected}")
        print()

    print()


def test_real_url():
    """测试真实网站的编码检测"""
    print("=" * 60)
    print("测试 5: 真实网站编码检测")
    print("=" * 60)

    # 导入工具模块
    from src.tools import charset_detector as cd_module

    # 测试一些真实网站
    test_urls = [
        "https://www.baidu.com",  # 应该是 UTF-8
        # "https://www.69shuba.com",  # 应该是 GBK（可能需要访问）
    ]

    for url in test_urls:
        print(f"检测网站: {url}")
        try:
            result_json = cd_module.detect_charset.invoke({"url": url, "max_retries": 3, "timeout": 10})
            result = json.loads(result_json)
            print(f"  编码: {result['charset']}")
            print(f"  置信度: {result['confidence']:.2f}")
            print(f"  来源: {result['source']}")
            print(f"  详细信息: {result['details']}")
            if result.get('recommendation'):
                print(f"  配置建议: {result['recommendation']}")
        except Exception as e:
            print(f"  检测失败: {e}")
        print()

    print()


def test_detect_from_html():
    """测试从 HTML 内容检测编码"""
    print("=" * 60)
    print("测试 6: 从 HTML 内容检测编码")
    print("=" * 60)

    # 在函数内部导入工具
    from src.tools import charset_detector as cd_module

    # 测试用例
    test_cases = [
        ('<html><head><meta charset="gbk"></head><body>GBK编码的中文内容</body></html>', "gbk"),
        ('<html><head><meta charset="utf-8"></head><body>UTF-8编码的中文内容</body></html>', "utf-8"),
    ]

    for i, (html, expected) in enumerate(test_cases, 1):
        print(f"测试用例 {i}:")
        result_json = cd_module.detect_charset_from_html.invoke({"html_content": html})
        result = json.loads(result_json)
        status = "✓" if result['charset'] == expected else "✗"
        print(f"{status} 期望: {expected}, 实际: {result['charset']}")
        print(f"   置信度: {result['confidence']:.2f}")
        print(f"   来源: {result['source']}")
        print()

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("编码检测工具测试")
    print("=" * 60 + "\n")

    test_detect_from_headers()
    test_detect_from_meta()
    test_detect_by_content()
    test_detect_by_chinese_characters()
    test_detect_from_html()

    # 可选：测试真实网站（需要网络连接）
    try:
        test_real_url()
    except Exception as e:
        print(f"跳过真实网站测试: {e}")

    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)
