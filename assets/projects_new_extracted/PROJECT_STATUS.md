# Legado书源驯兽师 - 项目状态说明

## 重要说明

### 当前项目状态

这个项目是一个基于 **LangChain** 和 **LangGraph** 的 **FastAPI Web应用**，而不是一个标准的 **MCP (Model Context Protocol) 服务器**。

### 为什么Kilo无法连接？

Kilo期望的是一个实现了MCP协议的服务器，该服务器需要：
1. 实现MCP协议的通信规范
2. 提供标准的MCP端点（如 `/`、`/tools/list`、`/tools/call` 等）
3. 返回符合MCP协议格式的JSON响应

而这个项目提供的是：
- FastAPI HTTP API端点（`/run`、`/stream_run`、`/cancel/{run_id}` 等）
- 基于LangChain和LangGraph的工作流引擎
- 书源开发和调试工具

### 如何使用这个项目？

#### 方法1：作为HTTP API使用

1. **启动服务器**：
   ```bash
   # 使用启动脚本
   start_mcp.bat
   
   # 或直接使用uvicorn
   python -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --log-level critical --no-access-log
   ```

2. **调用API端点**：
   ```bash
   # 运行任务
   curl -X POST http://localhost:5000/run \
     -H "Content-Type: application/json" \
     -d '{"text": "帮我创建一个书源"}'
   
   # 流式运行
   curl -X POST http://localhost:5000/stream_run \
     -H "Content-Type: application/json" \
     -d '{"text": "帮我创建一个书源"}'
   ```

#### 方法2：通过Python脚本使用

创建一个Python脚本调用API：

```python
import requests
import json

# 启动服务器后，调用API
response = requests.post(
    "http://localhost:5000/run",
    json={"text": "帮我为 https://www.sudugu.org 创建书源"}
)

print(response.json())
```

#### 方法3：集成到其他应用

这个项目可以作为后端服务集成到其他应用中，通过HTTP API调用其功能。

### 项目功能

这个项目提供了以下功能：

1. **智能HTML获取** - 支持GET/POST等各种请求方法
2. **知识库查询** - 24.93MB知识库，167个文档
3. **智能分析** - 自动分析网站结构，识别关键元素
4. **书源生成** - 自动生成符合Legado规范的书源JSON
5. **规则验证** - 基于Legado官方源码验证规则
6. **调试支持** - 完整的调试工具链

### 可用的API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/run` | POST | 运行任务 |
| `/stream_run` | POST | 流式运行 |
| `/cancel/{run_id}` | POST | 取消任务 |
| `/node_run/{node_id}` | POST | 运行指定节点 |
| `/graph_parameter` | GET | 获取图参数 |
| `/v1/chat/completions` | POST | OpenAI兼容接口 |
| `/health` | GET | 健康检查 |

### 总结

这个项目是一个功能强大的Legado书源开发助手，但它是一个**HTTP API服务**，而不是**MCP服务器**。

如果您需要在Kilo中使用类似的功能，建议：
1. 直接通过HTTP API调用这个项目
2. 或者创建一个真正的MCP服务器包装器来桥接这个项目

### 相关文档

- [`src/main.py`](src/main.py) - 主程序入口
- [`start_mcp.bat`](start_mcp.bat) - 启动脚本
- [`stop_mcp.bat`](stop_mcp.bat) - 停止脚本
- [`FINAL_REPORT.md`](FINAL_REPORT.md) - 最终项目报告
- [`MCP_TOOLS_DOCUMENTATION.md`](MCP_TOOLS_DOCUMENTATION.md) - 工具文档
- [`USER_GUIDE.md`](USER_GUIDE.md) - 用户指南
