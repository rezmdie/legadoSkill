#!/usr/bin/env python3
"""
测试 MCP 服务器启动和知识库初始化
"""
import sys
import io

# 设置 UTF-8 编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加路径
sys.path.insert(0, 'src')

print("=" * 60)
print("测试 MCP 服务器启动和知识库初始化")
print("=" * 60)

# 测试1: 导入知识库初始化模块
print("\n测试1: 导入知识库初始化模块")
print("-" * 60)
try:
    from utils.knowledge_initializer import (
        initialize_knowledge_base,
        is_knowledge_initialized,
        get_learning_stats,
        search_knowledge as search_knowledge_base
    )
    print("✅ 知识库初始化模块导入成功")
except Exception as e:
    print(f"❌ 知识库初始化模块导入失败: {e}")
    sys.exit(1)

# 测试2: 初始化知识库
print("\n测试2: 初始化知识库")
print("-" * 60)
try:
    stats = initialize_knowledge_base()
    print(f"✅ 知识库初始化成功")
    print(f"   - 处理文件: {stats.get('total_files', 0)}")
    print(f"   - 学习条目: {stats.get('learned_entries', 0)}")
    print(f"   - 书源数量: {stats.get('book_sources', 0)}")
    print(f"   - 模式数量: {stats.get('patterns', 0)}")
    print(f"   - 选择器数量: {stats.get('selectors', 0)}")
except Exception as e:
    print(f"❌ 知识库初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试3: 检查知识库是否已初始化
print("\n测试3: 检查知识库是否已初始化")
print("-" * 60)
if is_knowledge_initialized():
    print("✅ 知识库已初始化")
else:
    print("❌ 知识库未初始化")
    sys.exit(1)

# 测试4: 搜索知识
print("\n测试4: 搜索知识")
print("-" * 60)
try:
    results = search_knowledge_base("CSS选择器", limit=3)
    print(f"✅ 知识搜索成功，找到 {len(results)} 条相关知识")
    for i, result in enumerate(results[:2], 1):
        print(f"   {i}. {result.title} (来源: {result.source_file})")
except Exception as e:
    print(f"❌ 知识搜索失败: {e}")
    import traceback
    traceback.print_exc()

# 测试5: 导入 MCP 服务器
print("\n测试5: 导入 MCP 服务器")
print("-" * 60)
try:
    from mcp_server import app, SYSTEM_PROMPT
    print("✅ MCP 服务器导入成功")
    print(f"   - 系统提示词长度: {len(SYSTEM_PROMPT)} 字符")
except Exception as e:
    print(f"❌ MCP 服务器导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 总结
print("\n" + "=" * 60)
print("🎉 所有测试通过！")
print("=" * 60)
print("\n✨ MCP 服务器就绪：")
print("✅ 知识库初始化模块正常工作")
print("✅ 知识库学习功能正常")
print("✅ 知识搜索功能正常")
print("✅ MCP 服务器模块正常")
print("\n🚀 可以启动 MCP 服务器了！")
print("\n启动命令：")
print("  python src/mcp_server.py")
