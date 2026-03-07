# Kilo MCP配置完成

## ✅ 配置已成功添加

MCP配置已成功添加到 `.kilocode/mcp.json` 文件中。

## 📋 配置信息

**服务器名称**: `legado-book-source-tamer`

**启动命令**:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 5000
```

**环境变量**:
- `PYTHONPATH=.`
- `COZE_WORKSPACE_PATH=.`

## 🚀 使用步骤

### 1. 启动MCP服务

**方法一：使用启动脚本（推荐）**

双击运行 `start_mcp.bat` 文件，或在命令行中执行：

```bash
start_mcp.bat
```

**方法二：使用Python脚本**

```bash
python start_mcp_server.py
```

**方法三：使用uvicorn直接启动**

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --log-level error --no-access-log
```

### 2. 停止MCP服务

双击运行 `stop_mcp.bat` 文件，或在命令行中执行：

```bash
stop_mcp.bat
```

停止脚本会自动查找并停止占用5000端口的进程。

### 2. 重启Kilo

重启Kilo以加载新的MCP配置。

### 3. 在Kilo中使用

现在你可以在Kilo中直接调用以下工具：

#### 网页获取工具
- `smart_fetch_html` - 智能获取网页HTML
- `get_full_html` - 获取完整HTML源代码
- `test_request_method` - 测试请求方法

#### 知识库工具
- `search_knowledge` - 搜索知识库
- `get_book_source_examples` - 获取书源示例
- `check_knowledge_status` - 检查知识状态
- `learn_knowledge_base` - 学习知识库
- `audit_knowledge_base` - 审查知识库
- `get_css_selector_rules` - 获取CSS选择器规则
- `get_real_book_source_examples` - 获取真实书源示例
- `get_book_source_templates` - 获取书源模板

#### 智能分析工具
- `smart_web_analyzer` - 智能分析网站整体结构
- `smart_bookinfo_analyzer` - 智能分析书籍详情页
- `smart_toc_analyzer` - 智能分析目录页
- `smart_content_analyzer` - 智能分析正文页
- `smart_full_analyzer` - 综合分析器

#### 书源编辑工具
- `edit_book_source` - 编辑书源
- `validate_book_source` - 验证书源
- `export_book_source` - 导出书源

#### 调试工具
- `debug_book_source` - 调试书源
- `legado_debug_book_source` - Legado调试器

#### 可视化工具
- `element_picker_guide` - 元素选择器指南
- `browser_debug_helper` - 浏览器调试助手

#### 用户干预工具
- `user_intervention` - 人工干预
- `collaborative_edit` - 协同编辑

#### 验证工具
- `selector_validator` - 验证选择器
- `validate_selector_on_real_web` - 在真实网页验证选择器

## 💡 使用示例

### 示例1：为网站创建书源

```
用户: 帮我为 https://www.sudugu.org 创建一个书源

AI: 好的，我来帮你创建书源。

[调用 smart_fetch_html 获取HTML]
[调用 smart_web_analyzer 分析结构]
[调用 edit_book_source 生成书源]

AI: 书源已创建完成！
```

### 示例2：查询CSS选择器规则

```
用户: CSS选择器中@text和@html有什么区别？

AI: [调用 search_knowledge 查询知识库]

AI: @text提取所有文字（包括子标签），@html提取完整HTML（保留标签）。
```

### 示例3：调试书源

```
用户: 这个书源为什么不能用？

AI: [调用 debug_book_source 调试书源]

AI: 调试结果：搜索规则中的选择器未找到。建议使用 validate_selector_on_real_web 验证选择器。
```

## 📊 工具统计

- **工具总数**: 22个
- **函数总数**: 59个
- **知识库大小**: 24.93MB
- **文档数量**: 167个
- **真实书源**: 134个

## 🔧 故障排除

### 问题1：无法连接到MCP服务

**解决方案**:
1. 确保MCP服务已启动
2. 检查端口5000是否被占用
3. 查看服务日志

### 问题2：工具调用失败

**解决方案**:
1. 检查Python环境是否正确
2. 确保所有依赖已安装
3. 查看错误日志

### 问题3：知识库查询无结果

**解决方案**:
1. 运行 `learn_knowledge_base` 学习知识库
2. 检查知识库文件是否存在

## 📚 相关文档

- [MCP配置指南](MCP_SETUP_GUIDE.md)
- [用户指南](USER_GUIDE.md)
- [最终报告](FINAL_REPORT.md)
- [MCP工具文档](MCP_TOOLS_DOCUMENTATION.md)

## 🎉 完成

配置已完成！现在你可以在Kilo中使用Legado书源驯兽师的所有功能了。
