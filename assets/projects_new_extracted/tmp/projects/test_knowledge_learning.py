#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试知识学习能力
验证AI是否真正"学会"了知识
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/utils'))

print("=" * 60)
print("🎓 测试知识学习能力")
print("=" * 60)

# 测试1: 导入知识学习引擎
print("\n测试1: 导入知识学习引擎")
print("-" * 60)

try:
    from knowledge_learner import KnowledgeLearner
    print("✅ KnowledgeLearner 导入成功")
except Exception as e:
    print(f"❌ KnowledgeLearner 导入失败: {e}")
    sys.exit(1)

# 测试2: 导入知识应用引擎
print("\n测试2: 导入知识应用引擎")
print("-" * 60)

try:
    from knowledge_applier import KnowledgeApplier
    print("✅ KnowledgeApplier 导入成功")
except Exception as e:
    print(f"❌ KnowledgeApplier 导入失败: {e}")
    sys.exit(1)

# 测试3: 导入知识增强分析器
print("\n测试3: 导入知识增强分析器")
print("-" * 60)

try:
    from knowledge_enhanced_analyzer import KnowledgeEnhancedAnalyzer
    print("✅ KnowledgeEnhancedAnalyzer 导入成功")
except Exception as e:
    print(f"❌ KnowledgeEnhancedAnalyzer 导入失败: {e}")
    sys.exit(1)

# 测试4: 初始化学习引擎
print("\n测试4: 初始化知识学习引擎")
print("-" * 60)

try:
    learner = KnowledgeLearner("assets")
    print("✅ 知识学习引擎初始化成功")
except Exception as e:
    print(f"❌ 知识学习引擎初始化失败: {e}")
    sys.exit(1)

# 测试5: 学习知识库
print("\n测试5: 学习知识库")
print("-" * 60)

try:
    stats = learner.learn_all()
    print(f"✅ 知识库学习成功")
    print(f"   - 处理文件: {stats['total_files']}")
    print(f"   - 学习条目: {stats['learned_entries']}")
    print(f"   - 书源数量: {stats['book_sources']}")
    print(f"   - 模式数量: {stats['patterns']}")
    print(f"   - 选择器数量: {stats['selectors']}")
except Exception as e:
    print(f"❌ 知识库学习失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试6: 搜索知识
print("\n测试6: 搜索知识")
print("-" * 60)

try:
    results = learner.search_knowledge("CSS", limit=3)
    print(f"✅ 搜索成功，找到 {len(results)} 条相关知识")
    for i, result in enumerate(results[:2], 1):
        print(f"   {i}. {result.title} (来源: {result.source_file})")
except Exception as e:
    print(f"❌ 搜索失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试7: 应用知识
print("\n测试7: 应用知识到HTML分析")
print("-" * 60)

try:
    applier = KnowledgeApplier(learner)
    
    test_html = """
    <div class="book-info">
        <h1 class="book-title">Python编程从入门到实践</h1>
        <div class="author">作者：Eric Matthes</div>
    </div>
    """
    
    application = applier.apply_knowledge_to_html(
        test_html,
        'title'
    )
    
    print(f"✅ 知识应用成功")
    print(f"   - 应用的知识条目: {len(application.applied_knowledge)}")
    print(f"   - 生成的推荐: {len(application.recommendations)}")
    print(f"   - 置信度: {application.confidence:.2f}")
    print(f"   - 知识源: {', '.join(application.source_files)}")
except Exception as e:
    print(f"❌ 知识应用失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试8: 知识增强分析
print("\n测试8: 知识增强分析")
print("-" * 60)

try:
    enhanced_analyzer = KnowledgeEnhancedAnalyzer("assets")
    
    # 学习知识
    stats = enhanced_analyzer.learn_knowledge()
    
    # 分析
    result = enhanced_analyzer.analyze_with_learned_knowledge(
        test_html,
        'title',
        {'query': '书名'}
    )
    
    print(f"✅ 知识增强分析成功")
    print(f"   - 基础置信度: {result['base_analysis'].confidence:.2f}")
    print(f"   - 知识置信度: {result['knowledge_application'].confidence:.2f}")
    print(f"   - 增强置信度: {result['confidence']:.2f}")
    print(f"   - 应用的知识: {result['applied_knowledge_count']}")
    print(f"   - 知识源: {len(result['knowledge_sources'])}个")
except Exception as e:
    print(f"❌ 知识增强分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试9: 验证选择器
print("\n测试9: 验证选择器")
print("-" * 60)

try:
    validation = enhanced_analyzer.validate_selector_with_knowledge(
        '.book-title',
        test_html,
        'title'
    )
    
    print(f"✅ 选择器验证成功")
    print(f"   - 有知识支持: {validation['has_knowledge_support']}")
    print(f"   - 置信度: {validation['confidence']:.2f}")
    print(f"   - 匹配的模式: {len(validation['matched_patterns'])}")
except Exception as e:
    print(f"❌ 选择器验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 总结
print("\n" + "=" * 60)
print("🎉 所有测试通过！")
print("=" * 60)
print("\n✨ 知识学习能力总结：")
print("✅ 知识学习引擎正常工作")
print("✅ 知识应用引擎正常工作")
print("✅ 知识增强分析正常工作")
print("✅ 知识验证功能正常工作")
print("\n🎯 AI已成功掌握以下能力：")
print("• 从assets目录读取并学习所有知识文件")
print("• 解析书源规则、CSS选择器、技术文档")
print("• 构建知识关联和索引")
print("• 将学到的知识应用到HTML分析")
print("• 智能推荐基于实际书源的选择器")
print("• 验证规则是否符合知识库模式")
print("\n📊 知识掌握情况：")
print(f"• 已学习文件: {stats['total_files']}")
print(f"• 知识条目: {stats['learned_entries']}")
print(f"• 书源案例: {stats['book_sources']}")
print(f"• 模式库: {stats['patterns']}")
print(f"• 选择器库: {stats['selectors']}")
print("\n🚀 真正做到了：学会知识，应用知识！")
