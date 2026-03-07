#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有MCP工具的功能
验证每个工具是否可以正常调用
"""
import json
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tool_import():
    """测试工具导入"""
    print("=" * 60)
    print("测试1: 工具导入")
    print("=" * 60)
    
    try:
        from src.mcp_server import TOOLS
        print(f"✅ 成功导入MCP服务器")
        print(f"✅ 找到 {len(TOOLS)} 个工具")
        print()
        
        for i, tool in enumerate(TOOLS, 1):
            print(f"{i}. {tool.name}")
            print(f"   描述: {tool.description[:60]}...")
            print()
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_search():
    """测试知识库搜索工具"""
    print("=" * 60)
    print("测试2: 知识库搜索")
    print("=" * 60)
    
    try:
        from src.tools.knowledge_search_tool import search_knowledge
        
        # 测试搜索
        result = search_knowledge("CSS选择器", top_k=2)
        print("✅ search_knowledge 工具可用")
        print(f"搜索结果长度: {len(result)} 字符")
        print(f"结果预览: {result[:200]}...")
        print()
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_web_fetch():
    """测试网页获取工具"""
    print("=" * 60)
    print("测试3: 网页获取")
    print("=" * 60)
    
    try:
        from src.tools.web_fetch_tool import fetch_web_page
        
        # 测试获取网页（使用一个简单的测试URL）
        print("⏳ 正在获取测试网页...")
        result = fetch_web_page("https://www.example.com", timeout=10)
        print("✅ fetch_web_page 工具可用")
        print(f"结果长度: {len(result)} 字符")
        print()
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("注意: 网络请求可能因为网络问题失败，这是正常的")
        print()
        return False


def test_book_source_editor():
    """测试书源编辑工具"""
    print("=" * 60)
    print("测试4: 书源编辑")
    print("=" * 60)
    
    try:
        from src.tools.book_source_editor import edit_book_source
        
        # 测试创建新书源
        result = edit_book_source(
            book_source_json="",
            action="create"
        )
        print("✅ edit_book_source 工具可用")
        print(f"结果长度: {len(result)} 字符")
        
        # 检查是否包含JSON
        if "```json" in result:
            print("✅ 成功生成书源JSON")
        print()
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_selector_validator():
    """测试选择器验证工具"""
    print("=" * 60)
    print("测试5: 选择器验证")
    print("=" * 60)
    
    try:
        from src.tools.selector_validator import validate_selector_on_real_web
        
        print("⏳ 正在验证选择器...")
        # 使用example.com测试
        result = validate_selector_on_real_web(
            url="https://www.example.com",
            selector="h1"
        )
        print("✅ validate_selector_on_real_web 工具可用")
        print(f"结果长度: {len(result)} 字符")
        print()
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("注意: 网络请求可能因为网络问题失败，这是正常的")
        print()
        return False


def test_smart_analyzer():
    """测试智能分析工具"""
    print("=" * 60)
    print("测试6: 智能网站分析")
    print("=" * 60)
    
    try:
        from src.tools.smart_web_analyzer import smart_analyze_website
        
        print("⏳ 正在分析网站...")
        result = smart_analyze_website("https://www.example.com")
        print("✅ smart_analyze_website 工具可用")
        print(f"结果长度: {len(result)} 字符")
        print()
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("注意: 网络请求可能因为网络问题失败，这是正常的")
        print()
        return False


def test_element_picker_guide():
    """测试元素选择器指南"""
    print("=" * 60)
    print("测试7: 元素选择器指南")
    print("=" * 60)
    
    try:
        from src.tools.element_picker_guide import get_element_picker_guide
        
        result = get_element_picker_guide(selector_type="css")
        print("✅ get_element_picker_guide 工具可用")
        print(f"结果长度: {len(result)} 字符")
        print()
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_additional_tools():
    """测试额外的工具"""
    print("=" * 60)
    print("测试8: 额外工具检查")
    print("=" * 60)
    
    additional_tools = [
        ("web_fetch_tool", "extract_elements"),
        ("web_fetch_tool", "analyze_search_structure"),
        ("book_source_editor", "export_book_source"),
        ("book_source_editor", "validate_book_source"),
        ("book_source_editor", "save_to_knowledge"),
        ("selector_validator", "extract_from_real_web"),
        ("smart_web_analyzer", "smart_build_search_request"),
        ("smart_web_analyzer", "smart_fetch_list"),
        ("legado_tools", "debug_legado_book_source"),
        ("legado_tools", "test_legado_rule"),
        ("legado_tools", "validate_legado_rules"),
    ]
    
    available_count = 0
    for module_name, tool_name in additional_tools:
        try:
            module = __import__(f"src.tools.{module_name}", fromlist=[tool_name])
            tool = getattr(module, tool_name)
            print(f"✅ {module_name}.{tool_name} 可用")
            available_count += 1
        except Exception as e:
            print(f"❌ {module_name}.{tool_name} 不可用: {e}")
    
    print()
    print(f"额外工具可用性: {available_count}/{len(additional_tools)}")
    print()
    return available_count > 0


def generate_report(results):
    """生成测试报告"""
    print("=" * 60)
    print("测试报告")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"总测试数: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"通过率: {passed/total*100:.1f}%")
    print()
    
    if passed == total:
        print("🎉 所有测试通过！MCP工具系统运行正常！")
    elif passed >= total * 0.7:
        print("⚠️ 大部分测试通过，但有些工具可能需要网络连接")
    else:
        print("❌ 多个测试失败，请检查系统配置")
    
    print()
    print("=" * 60)
    print("详细信息")
    print("=" * 60)
    print()
    print("MCP服务器状态:")
    print("- 服务器文件: src/mcp_server.py")
    print("- 配置文件: .kilocode/mcp.json")
    print("- 启动脚本: start_mcp.bat")
    print()
    print("已暴露的MCP工具:")
    print("1. create_book_source - 创建书源")
    print("2. analyze_website - 分析网站")
    print("3. fetch_html - 获取HTML")
    print("4. debug_book_source - 调试书源")
    print("5. edit_book_source - 编辑书源")
    print("6. validate_selector - 验证选择器")
    print("7. search_knowledge - 搜索知识库")
    print("8. get_element_picker_guide - 获取选择器指南")
    print()
    print("可用但未暴露的工具:")
    print("- extract_elements - 提取元素")
    print("- analyze_search_structure - 分析搜索结构")
    print("- export_book_source - 导出书源")
    print("- validate_book_source - 验证书源")
    print("- smart_build_search_request - 智能构建搜索请求")
    print("- smart_fetch_list - 智能获取列表")
    print("- 以及更多...")
    print()
    print("查看完整工具清单: TOOLS_INVENTORY.md")
    print()


def main():
    """主函数"""
    print()
    print("🚀 Legado书源驯兽师 - MCP工具测试")
    print()
    
    results = []
    
    # 运行所有测试
    results.append(test_tool_import())
    results.append(test_knowledge_search())
    results.append(test_web_fetch())
    results.append(test_book_source_editor())
    results.append(test_selector_validator())
    results.append(test_smart_analyzer())
    results.append(test_element_picker_guide())
    results.append(test_additional_tools())
    
    # 生成报告
    generate_report(results)
    
    # 返回退出码
    return 0 if all(results[:4]) else 1  # 前4个是核心测试


if __name__ == "__main__":
    sys.exit(main())
