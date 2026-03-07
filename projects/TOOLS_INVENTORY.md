# Legado书源驯兽师 - 工具清单

## 📊 工具统计

- **工具文件总数**: 23个
- **MCP已暴露工具**: 8个
- **待暴露工具**: 15个

---

## ✅ 已暴露的MCP工具 (8个)

### 1. create_book_source
- **文件**: 通过main.py的service调用
- **功能**: 为指定网站创建Legado书源
- **状态**: ✅ 已暴露

### 2. analyze_website
- **文件**: smart_web_analyzer.py
- **功能**: 智能分析网站结构
- **状态**: ✅ 已暴露

### 3. fetch_html
- **文件**: web_fetch_tool.py
- **功能**: 获取网页HTML内容
- **状态**: ✅ 已暴露

### 4. debug_book_source
- **文件**: book_source_debugger.py
- **功能**: 调试书源规则
- **状态**: ✅ 已暴露

### 5. edit_book_source
- **文件**: book_source_editor.py
- **功能**: 编辑书源配置
- **状态**: ✅ 已暴露

### 6. validate_selector
- **文件**: selector_validator.py
- **功能**: 验证CSS选择器
- **状态**: ✅ 已暴露

### 7. search_knowledge
- **文件**: knowledge_search_tool.py
- **功能**: 搜索知识库
- **状态**: ✅ 已暴露

### 8. get_element_picker_guide
- **文件**: element_picker_guide.py
- **功能**: 获取选择器使用指南
- **状态**: ✅ 已暴露

---

## 🔧 核心工具文件详情 (23个)

### 📚 书源编辑类 (5个)

#### 1. book_source_editor.py
- **工具**: edit_book_source, export_book_source, save_to_knowledge, validate_book_source
- **功能**: 书源创建、编辑、导出、验证
- **MCP状态**: ✅ edit_book_source已暴露

#### 2. book_source_html_editor.py
- **工具**: 未知（需要分析）
- **功能**: HTML编辑相关
- **MCP状态**: ❌ 未暴露

#### 3. collaborative_edit.py
- **工具**: 未知（需要分析）
- **功能**: 协作编辑
- **MCP状态**: ❌ 未暴露

#### 4. book_source_crawler.py
- **工具**: 未知（需要分析）
- **功能**: 书源爬取
- **MCP状态**: ❌ 未暴露

#### 5. user_intervention.py
- **工具**: 未知（需要分析）
- **功能**: 用户干预
- **MCP状态**: ❌ 未暴露

### 🔍 调试验证类 (4个)

#### 6. book_source_debugger.py
- **工具**: BookSourceDebugger类
- **功能**: 完整的书源调试器
- **MCP状态**: ✅ 部分暴露（debug_book_source）

#### 7. legado_debugger.py
- **工具**: LegadoDebugger类
- **功能**: Legado规则调试
- **MCP状态**: ❌ 未暴露

#### 8. legado_debug_tools.py
- **工具**: 调试工具函数
- **功能**: 调试辅助工具
- **MCP状态**: ❌ 未暴露

#### 9. selector_validator.py
- **工具**: validate_selector_on_real_web, extract_from_real_web
- **功能**: 选择器真实验证
- **MCP状态**: ✅ validate_selector已暴露

### 🤖 智能分析类 (6个)

#### 10. smart_web_analyzer.py
- **工具**: smart_analyze_website, smart_build_search_request, smart_fetch_list
- **功能**: 智能网站分析
- **MCP状态**: ✅ 部分暴露（analyze_website）

#### 11. smart_full_analyzer.py
- **工具**: 未知（需要分析）
- **功能**: 完整智能分析
- **MCP状态**: ❌ 未暴露

#### 12. smart_bookinfo_analyzer.py
- **工具**: 未知（需要分析）
- **功能**: 书籍信息智能分析
- **MCP状态**: ❌ 未暴露

#### 13. smart_toc_analyzer.py
- **工具**: 未知（需要分析）
- **功能**: 目录智能分析
- **MCP状态**: ❌ 未暴露

#### 14. smart_content_analyzer.py
- **工具**: 未知（需要分析）
- **功能**: 内容智能分析
- **MCP状态**: ❌ 未暴露

#### 15. smart_fetcher.py
- **工具**: 未知（需要分析）
- **功能**: 智能获取
- **MCP状态**: ❌ 未暴露

### 📖 知识库类 (4个)

#### 16. knowledge_search_tool.py
- **工具**: search_knowledge
- **功能**: 知识库搜索
- **MCP状态**: ✅ 已暴露

#### 17. knowledge_tools.py
- **工具**: 未知（需要分析）
- **功能**: 知识库工具集
- **MCP状态**: ❌ 未暴露

#### 18. knowledge_index_tool.py
- **工具**: 未知（需要分析）
- **功能**: 知识库索引
- **MCP状态**: ❌ 未暴露

#### 19. knowledge_auditor.py
- **工具**: 未知（需要分析）
- **功能**: 知识库审计
- **MCP状态**: ❌ 未暴露

### 🌐 网页获取类 (2个)

#### 20. web_fetch_tool.py
- **工具**: fetch_web_page, extract_elements, analyze_search_structure
- **功能**: 网页获取和分析
- **MCP状态**: ✅ 部分暴露（fetch_html）

#### 21. element_picker_guide.py
- **工具**: get_element_picker_guide
- **功能**: 元素选择器指南
- **MCP状态**: ✅ 已暴露

### 🔧 Legado工具类 (2个)

#### 22. legado_tools.py
- **工具**: debug_legado_book_source, test_legado_rule, validate_legado_rules
- **功能**: Legado书源工具
- **MCP状态**: ❌ 未暴露

#### 23. __init__.py
- **工具**: 空文件
- **功能**: 包初始化
- **MCP状态**: N/A

---

## 📋 建议暴露的额外工具

### 高优先级 (应该暴露)

1. **smart_build_search_request** (smart_web_analyzer.py)
   - 智能构建搜索请求
   - 对书源创建非常有用

2. **smart_fetch_list** (smart_web_analyzer.py)
   - 智能获取列表页面
   - 自动处理分页

3. **extract_elements** (web_fetch_tool.py)
   - 从HTML提取元素
   - 辅助选择器编写

4. **analyze_search_structure** (web_fetch_tool.py)
   - 分析搜索页面结构
   - 帮助构建搜索URL

5. **export_book_source** (book_source_editor.py)
   - 导出书源为文件
   - 方便用户使用

6. **validate_book_source** (book_source_editor.py)
   - 验证书源完整性
   - 质量保证

7. **extract_from_real_web** (selector_validator.py)
   - 从真实网页提取内容
   - 真实性验证

### 中优先级 (可选暴露)

8. **test_legado_rule** (legado_tools.py)
   - 测试单个Legado规则
   - 细粒度调试

9. **validate_legado_rules** (legado_tools.py)
   - 验证Legado规则语法
   - 语法检查

10. **save_to_knowledge** (book_source_editor.py)
    - 保存成功案例到知识库
    - 知识积累

### 低优先级 (暂不暴露)

- smart_full_analyzer.py - 可能与现有工具重复
- smart_bookinfo_analyzer.py - 特定场景工具
- smart_toc_analyzer.py - 特定场景工具
- smart_content_analyzer.py - 特定场景工具
- knowledge_tools.py - 内部工具
- knowledge_index_tool.py - 内部工具
- knowledge_auditor.py - 内部工具
- book_source_html_editor.py - 高级功能
- collaborative_edit.py - 协作功能
- user_intervention.py - 交互功能

---

## 🎯 下一步行动

### 1. 立即行动
- ✅ 创建工具清单文档（本文档）
- ⏳ 分析未暴露工具的具体功能
- ⏳ 更新MCP服务器，暴露高优先级工具
- ⏳ 测试新暴露的工具

### 2. 短期计划
- 为所有工具创建详细文档
- 编写工具使用示例
- 创建工具测试套件

### 3. 长期计划
- 优化工具接口
- 添加更多智能分析功能
- 完善知识库系统

---

## 📝 工具使用统计

| 类别 | 文件数 | 已暴露 | 未暴露 | 暴露率 |
|------|--------|--------|--------|--------|
| 书源编辑 | 5 | 1 | 4 | 20% |
| 调试验证 | 4 | 2 | 2 | 50% |
| 智能分析 | 6 | 1 | 5 | 17% |
| 知识库 | 4 | 1 | 3 | 25% |
| 网页获取 | 2 | 2 | 0 | 100% |
| Legado工具 | 2 | 0 | 2 | 0% |
| **总计** | **23** | **8** | **15** | **35%** |

---

## 🔗 相关文档

- [MCP服务器指南](MCP_SERVER_GUIDE.md)
- [MCP转换报告](MCP_CONVERSION_REPORT.md)
- [项目状态](PROJECT_STATUS.md)

---

**最后更新**: 2026-02-18
**维护者**: Legado书源驯兽师团队
