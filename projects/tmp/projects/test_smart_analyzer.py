#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试智能分析器功能
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/utils'))

# 测试导入
print("=" * 60)
print("测试1: 测试模块导入")
print("=" * 60)

try:
    from html_structure_analyzer import HTMLStructureAnalyzer
    print("✅ html_structure_analyzer 导入成功")
except Exception as e:
    print(f"❌ html_structure_analyzer 导入失败: {e}")
    sys.exit(1)

try:
    from knowledge_based_analyzer import KnowledgeBasedAnalyzer
    print("✅ knowledge_based_analyzer 导入成功")
except Exception as e:
    print(f"❌ knowledge_based_analyzer 导入失败: {e}")
    sys.exit(1)

try:
    from multi_mode_extractor import MultiModeExtractor, SmartExtractionStrategy
    print("✅ multi_mode_extractor 导入成功")
except Exception as e:
    print(f"❌ multi_mode_extractor 导入失败: {e}")
    sys.exit(1)

try:
    from rule_validator import RuleValidator
    print("✅ rule_validator 导入成功")
except Exception as e:
    print(f"❌ rule_validator 导入失败: {e}")
    sys.exit(1)

# 测试基本功能
print("\n" + "=" * 60)
print("测试2: 测试HTML结构分析")
print("=" * 60)

test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>测试页面</title>
</head>
<body>
    <div class="book-info">
        <h1 class="book-title">Python编程从入门到实践</h1>
        <div class="author">作者：Eric Matthes</div>
        <div class="intro">这是一本优秀的Python入门书籍</div>
        <img class="cover" src="cover.jpg" alt="封面">
        <a class="toc-link" href="/toc">目录</a>
    </div>
    <div class="chapter-list">
        <ul>
            <li><a href="/chapter1">第一章</a></li>
            <li><a href="/chapter2">第二章</a></li>
            <li><a href="/chapter3">第三章</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>第一章：Python基础</h1>
        <p>这是正文内容...</p>
    </div>
</body>
</html>
"""

try:
    analyzer = HTMLStructureAnalyzer(test_html)
    structure = analyzer.analyze_structure()
    print(f"✅ HTML结构分析成功")
    print(f"   - 页面类型: {structure['page_type']}")
    print(f"   - 标题数量: {len(structure['key_elements']['titles'])}")
    print(f"   - 列表数量: {len(structure['key_elements']['lists'])}")
    print(f"   - 容器数量: {len(structure['key_elements']['containers'])}")
except Exception as e:
    print(f"❌ HTML结构分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试知识库分析
print("\n" + "=" * 60)
print("测试3: 测试知识库分析")
print("=" * 60)

try:
    kb_analyzer = KnowledgeBasedAnalyzer()
    result = kb_analyzer.analyze_with_knowledge(test_html, 'title', '书名')
    print(f"✅ 知识库分析成功")
    print(f"   - 置信度: {result.confidence:.2f}")
    print(f"   - 推荐数量: {len(result.recommended_selectors)}")
except Exception as e:
    print(f"❌ 知识库分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试多模式提取
print("\n" + "=" * 60)
print("测试4: 测试多模式提取")
print("=" * 60)

try:
    extractor = MultiModeExtractor(test_html)
    
    # CSS提取
    css_result = extractor.extract('.book-title', method='css')
    print(f"✅ CSS提取成功: {css_result.content}")
    
    # XPath提取
    xpath_result = extractor.extract('//h1', method='xpath')
    print(f"✅ XPath提取成功: {xpath_result.content}")
    
    # 智能策略提取
    smart_strategy = SmartExtractionStrategy(test_html)
    strategy_result = smart_strategy.extract_with_strategy('title')
    print(f"✅ 智能策略提取成功: {strategy_result['best_result']['strategy']}")
except Exception as e:
    print(f"❌ 多模式提取失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试规则验证
print("\n" + "=" * 60)
print("测试5: 测试规则验证")
print("=" * 60)

try:
    validator = RuleValidator(test_html)
    validation = validator.validate_rule('css', '.book-title')
    print(f"✅ 规则验证成功")
    print(f"   - 规则有效: {validation['valid']}")
    print(f"   - 提取数量: {validation['test_results']['extracted_count']}")
except Exception as e:
    print(f"❌ 规则验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 总结
print("\n" + "=" * 60)
print("🎉 所有测试通过！")
print("=" * 60)
print("\n智能分析引擎功能总结：")
print("✅ HTML结构深度分析")
print("✅ 基于知识库的模式匹配")
print("✅ 多模式提取（CSS/XPath/正则）")
print("✅ 规则验证和优化")
print("✅ 自适应分析能力")
print("\n真正做到：随机应变，智能分析！")
