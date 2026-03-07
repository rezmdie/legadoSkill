# Legado书源驯兽师 🦁

> 智能化的Legado书源创建和调试工具，现已支持MCP协议

[![MCP](https://img.shields.io/badge/MCP-Enabled-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-orange)](https://langchain.com)

## 🎯 项目简介

Legado书源驯兽师是一个基于AI的智能工具，帮助你快速创建和调试Legado阅读APP的书源。通过MCP协议集成到Kilo IDE，提供强大的书源开发能力。

### 核心功能

- 🤖 **智能分析**: 自动分析网站结构，识别关键元素
- 📝 **自动生成**: 一键生成完整的书源JSON配置
- 🔍 **规则调试**: 实时测试和验证书源规则
- 📚 **知识库**: 24.93MB的书源开发文档和案例
- 🔧 **选择器工具**: CSS/XPath/JSONPath选择器验证
- 🌐 **网页获取**: 智能HTTP请求，支持各种网站

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 在Kilo IDE中使用

MCP服务器已配置在 `.kilocode/mcp.json`，Kilo会自动加载。

### 3. 手动启动（可选）

```bash
# Windows
start_mcp.bat

# Linux/Mac
python -u src/mcp_server.py
```

## 📖 MCP工具列表

### 已暴露的8个工具

| 工具 | 功能 | 使用场景 |
|------|------|---------|
| `create_book_source` | 创建书源 | 为新网站生成书源 |
| `analyze_website` | 分析网站 | 识别页面结构 |
| `fetch_html` | 获取HTML | 下载网页内容 |
| `debug_book_source` | 调试书源 | 测试规则是否正确 |
| `edit_book_source` | 编辑书源 | 修改书源配置 |
| `validate_selector` | 验证选择器 | 测试CSS/XPath |
| `search_knowledge` | 搜索知识库 | 查找文档和案例 |
| `get_element_picker_guide` | 选择器指南 | 学习选择器语法 |

### 可用但未暴露的11个工具

查看 [TOOLS_INVENTORY.md](TOOLS_INVENTORY.md) 了解完整工具清单。

## 💡 使用示例

### 创建书源

```javascript
// 在Kilo IDE中调用
mcp.call_tool("create_book_source", {
  url: "https://www.example.com",
  source_name: "示例书源"
})
```

### 分析网站

```javascript
mcp.call_tool("analyze_website", {
  url: "https://www.example.com",
  page_type: "all"  // search, list, detail, toc, content, all
})
```

### 验证选择器

```javascript
mcp.call_tool("validate_selector", {
  url: "https://www.example.com",
  selector: "div.book-item",
  selector_type: "css"
})
```

### 搜索知识库

```javascript
mcp.call_tool("search_knowledge", {
  query: "CSS选择器",
  top_k: 5
})
```

## 🎉 成功案例

### sudugu.org 书源

已成功创建完整书源，包含：
- ✅ 搜索功能
- ✅ 列表页解析
- ✅ 详情页解析
- ✅ 目录页解析
- ✅ 内容页解析

查看: [sudugu_book_source_final.json](sudugu_book_source_final.json)

## 📚 文档

- [MCP服务器指南](MCP_SERVER_GUIDE.md) - 详细使用说明
- [工具清单](TOOLS_INVENTORY.md) - 所有工具的详细信息
- [最终报告](MCP_FINAL_REPORT.md) - 完整的项目报告
- [转换报告](MCP_CONVERSION_REPORT.md) - MCP转换详情

## 🏗️ 项目结构

```
legado-book-source-tamer/
├── src/
│   ├── mcp_server.py          # MCP服务器入口
│   ├── main.py                # LangGraph服务
│   ├── agents/                # AI代理
│   ├── graphs/                # 工作流图
│   └── tools/                 # 23个工具模块
├── .kilocode/
│   └── mcp.json              # Kilo MCP配置
├── config/                    # 配置文件
├── knowledge_base/            # 知识库 (24.93MB)
├── test_*.py                  # 测试脚本
└── *.md                       # 文档
```

## 🔧 技术栈

- **MCP协议**: 标准Model Context Protocol
- **AI框架**: LangChain + LangGraph
- **Python**: 3.10+
- **异步**: asyncio
- **知识库**: 向量搜索 + RAG

## 📊 项目统计

- **工具文件**: 23个
- **已暴露工具**: 8个
- **可用工具**: 19个
- **知识库大小**: 24.93MB
- **知识库文件**: 167个
- **代码行数**: ~18,000行

## 🎯 工作流程

```
1. 分析网站 (analyze_website)
   ↓
2. 获取HTML (fetch_html)
   ↓
3. 验证选择器 (validate_selector)
   ↓
4. 创建书源 (create_book_source)
   ↓
5. 调试规则 (debug_book_source)
   ↓
6. 编辑优化 (edit_book_source)
   ↓
7. 导出使用 ✅
```

## 🚦 测试

```bash
# 测试MCP服务器导入
python test_mcp_server_import.py

# 测试所有工具
python test_all_mcp_tools.py
```

## 📝 配置

### MCP配置 (.kilocode/mcp.json)

```json
{
  "mcpServers": {
    "legado-book-source-tamer": {
      "command": "python",
      "args": ["-u", "src/mcp_server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "MCP_MODE": "true"
      }
    }
  }
}
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可

MIT License

## 🔗 相关链接

- [Legado阅读](https://github.com/gedoor/legado)
- [MCP协议](https://modelcontextprotocol.io)
- [LangChain](https://langchain.com)

---

**状态**: ✅ 生产就绪  
**版本**: 1.0.0  
**最后更新**: 2026-02-18
