# MCP服务器使用指南

## 概述

本项目已成功转换为标准MCP（Model Context Protocol）服务器，可以在Kilo等支持MCP的IDE中使用。

## 架构说明

### 原有架构
- **FastAPI应用** (`src/main.py`): HTTP服务器，提供REST API接口
- **GraphService**: 核心服务，处理LangGraph工作流

### 新增MCP架构
- **MCP服务器** (`src/mcp_server.py`): 标准MCP协议实现
- **工具暴露**: 将GraphService功能包装为MCP工具
- **Stdio通信**: 使用标准输入/输出进行JSON-RPC通信

## 配置文件

### `.kilocode/mcp.json`
```json
{
  "mcpServers": {
    "legado-book-source-tamer": {
      "description": "Legado书源驯兽师 - 智能书源开发助手",
      "command": "python",
      "args": ["src/mcp_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "COZE_WORKSPACE_PATH": ".",
        "MCP_MODE": "true",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## 可用工具

MCP服务器提供以下8个工具：

### 1. create_book_source
为指定网站创建Legado书源。自动分析网站结构，生成完整的书源JSON配置。

**参数:**
- `url` (必需): 目标网站URL
- `source_name` (可选): 书源名称

### 2. analyze_website
智能分析网站结构，识别搜索页、列表页、详情页、目录页和内容页的关键元素。

**参数:**
- `url` (必需): 要分析的网站URL
- `page_type` (可选): 页面类型 (search/list/detail/toc/content/all)

### 3. fetch_html
智能获取网页HTML内容，支持GET/POST请求、自定义headers、cookies等。

**参数:**
- `url` (必需): 目标URL
- `method` (可选): HTTP方法 (GET/POST)
- `headers` (可选): 自定义HTTP headers
- `data` (可选): POST请求的数据

### 4. debug_book_source
调试书源规则，测试搜索、列表、详情、目录、内容等规则是否正确。

**参数:**
- `book_source_json` (必需): 书源JSON字符串
- `test_url` (必需): 测试URL
- `rule_type` (必需): 规则类型 (search/bookList/bookInfo/tocUrl/chapterList/content)

### 5. edit_book_source
编辑和修改书源配置，支持修改规则、添加字段、调整参数等。

**参数:**
- `book_source_json` (必需): 原始书源JSON字符串
- `modifications` (必需): 要修改的内容

### 6. validate_selector
验证CSS选择器或XPath表达式是否正确，测试能否提取到目标内容。

**参数:**
- `url` (必需): 测试URL
- `selector` (必需): CSS选择器或XPath表达式
- `selector_type` (可选): 选择器类型 (css/xpath/json)

### 7. search_knowledge
搜索Legado书源开发知识库，获取相关文档和示例。

**参数:**
- `query` (必需): 搜索关键词
- `top_k` (可选): 返回结果数量，默认5

### 8. get_element_picker_guide
获取元素选择器使用指南，包括CSS选择器、XPath、JSONPath等的使用方法。

**参数:**
- `selector_type` (可选): 选择器类型 (css/xpath/json/all)

## 使用方法

### 在Kilo中使用

1. **重新加载MCP服务器**
   - 在Kilo中打开命令面板
   - 选择 "Reload MCP Servers" 或重启Kilo

2. **调用工具**
   - MCP工具会自动出现在Kilo的工具列表中
   - 直接在对话中请求使用相关功能
   - 例如: "帮我为 https://www.example.com 创建书源"

### 测试MCP服务器

运行测试脚本验证配置：
```bash
python test_mcp_server_import.py
```

## 提示模板

MCP服务器还提供了两个提示模板：

### 1. create_book_source
创建书源的完整工作流程提示

### 2. debug_book_source
调试书源问题的提示模板

## 技术细节

### 日志管理
- MCP模式下完全禁用日志输出，避免干扰JSON-RPC通信
- 通过 `MCP_MODE=true` 环境变量控制

### 通信协议
- 使用标准输入/输出 (stdio) 进行通信
- JSON-RPC 2.0协议
- 支持异步操作

### 错误处理
- 所有工具调用都有完整的错误处理
- 返回结构化的错误信息

## 故障排除

### 问题1: MCP服务器无法启动
**解决方案:**
1. 确保已安装MCP SDK: `pip install mcp`
2. 检查Python路径配置
3. 运行测试脚本: `python test_mcp_server_import.py`

### 问题2: 工具调用失败
**解决方案:**
1. 检查环境变量配置
2. 确保 `COZE_WORKSPACE_PATH` 正确
3. 查看Kilo的MCP日志

### 问题3: 编码问题
**解决方案:**
- 确保 `PYTHONUNBUFFERED=1` 已设置
- Windows系统可能需要设置控制台编码

## 与原有FastAPI服务的关系

- **MCP服务器**: 用于IDE集成，通过stdio通信
- **FastAPI服务**: 仍然可用，用于HTTP API调用
- 两者共享相同的 `GraphService` 核心逻辑
- 可以同时运行，互不干扰

启动FastAPI服务:
```bash
python src/main.py -m http -p 5000
```

## 下一步

1. 在Kilo中重新加载MCP服务器
2. 尝试使用工具创建书源
3. 根据需要调整工具参数和提示模板

## 参考资料

- [MCP协议文档](https://modelcontextprotocol.io/)
- [Legado书源开发文档](./docs/)
- [项目完整报告](./FINAL_REPORT.md)
