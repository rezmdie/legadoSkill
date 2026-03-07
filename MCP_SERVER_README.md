# MCP Server - Model Context Protocol Server

健壮、高性能且完全模块化的模型上下文协议（MCP）服务器实现，作为人工智能模型与多样化外部工具生态系统的底层连接桥梁。

## 功能特性

### 核心功能
- **JSON-RPC 2.0协议**: 严格遵循MCP规范进行双向通信
- **异步架构**: 采用异步编程模型保障高并发性能
- **模块化设计**: 高度可扩展的接口设计模式
- **动态配置**: 从`.kilocode/mcp.json`文件中深度解析并加载设置
- **系统提示词注入**: 自动加载`config/system/prompt.md`作为AI会话上下文

### 工具适配器
- **Python工具适配器**: 支持位于`assets/projects_new_extracted/src/`的Python工具
- **Google API适配器**: 集成谷歌API服务（搜索、翻译、地图、YouTube等）
- **动态工具发现**: 运行时动态注册、发现和管理各类工具适配器

### 性能特性
- **并发处理**: 支持多重并发处理，最大可配置100个并发任务
- **任务管理**: 内置异步任务管理器，支持优先级队列和超时控制
- **速率限制**: 可配置的速率限制机制
- **错误处理**: 完善的错误处理机制与日志记录功能

## 项目结构

```
.
├── mcp_server/                 # MCP服务器核心模块
│   ├── __init__.py            # 包初始化
│   ├── server.py              # 服务器核心实现
│   ├── config_loader.py       # 配置加载器
│   ├── system_prompt_injector.py  # 系统提示词注入器
│   ├── tool_registry.py       # 工具注册表
│   ├── protocol.py            # JSON-RPC协议处理器
│   ├── async_manager.py       # 异步任务管理器
│   ├── logger.py              # 日志记录系统
│   ├── exceptions.py          # 异常定义
│   ├── discovery.py           # 工具发现机制
│   └── adapters/              # 工具适配器
│       ├── __init__.py
│       ├── python_adapter.py  # Python工具适配器
│       └── google_adapter.py  # Google API适配器
├── config/                    # 配置目录
│   └── system/
│       └── prompt.md          # 系统提示词
├── .kilocode/                 # Kilocode配置目录
│   ├── mcp.json               # MCP服务器配置
│   └── mcp.json.example       # 配置示例
├── assets/                    # 资源目录
│   └── projects_new_extracted/src/  # Python工具源码
├── logs/                      # 日志目录（自动创建）
├── main.py                    # 主入口文件
├── requirements.txt           # Python依赖
└── MCP_SERVER_README.md       # 本文档
```

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置服务器

复制配置示例文件并修改：

```bash
cp .kilocode/mcp.json.example .kilocode/mcp.json
```

编辑`.kilocode/mcp.json`文件，配置服务器参数、工具和适配器。

### 3. 配置系统提示词

系统提示词文件位于`config/system/prompt.md`，可以根据需要修改。

## 使用方法

### 启动服务器

```bash
# 使用默认配置
python main.py

# 指定主机和端口
python main.py --host 0.0.0.0 --port 8080

# 指定配置文件
python main.py --config /path/to/config.json

# 指定日志级别
python main.py --log-level DEBUG

# 启用JSON格式日志
python main.py --json-logs
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | 服务器主机地址 | 从配置读取或127.0.0.1 |
| `--port` | 服务器端口 | 从配置读取或8080 |
| `--config` | 配置文件路径 | .kilocode/mcp.json |
| `--prompt` | 系统提示词文件路径 | config/system/prompt.md |
| `--log-level` | 日志级别 | INFO |
| `--log-dir` | 日志目录 | logs |
| `--json-logs` | 启用JSON格式日志 | False |
| `--version` | 显示版本信息 | - |

## API端点

### HTTP端点

#### POST /
处理JSON-RPC请求

```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

#### GET /health
健康检查

```bash
curl http://localhost:8080/health
```

响应：
```json
{
  "status": "healthy",
  "initialized": true,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

#### GET /metrics
获取服务器指标

```bash
curl http://localhost:8080/metrics
```

### WebSocket端点

#### WS /ws
WebSocket连接，支持实时双向通信

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
  // 发送JSON-RPC请求
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
    params: {}
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response);
};
```

## MCP协议方法

### 初始化方法

#### initialize
初始化MCP会话

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "Client",
      "version": "1.0.0"
    }
  }
}
```

#### initialized
通知服务器初始化完成

```json
{
  "jsonrpc": "2.0",
  "method": "initialized",
  "params": {}
}
```

### 工具方法

#### tools/list
列出所有可用工具

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

#### tools/call
调用工具

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "server.info",
    "arguments": {}
  }
}
```

#### tools/cancel
取消工具调用

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/cancel",
  "params": {
    "callId": "call_id"
  }
}
```

### 服务器方法

#### ping
心跳检测

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "ping",
  "params": {}
}
```

#### shutdown
关闭服务器

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "shutdown",
  "params": {}
}
```

## 配置说明

### 服务器配置

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080,
    "max_connections": 100,
    "request_timeout": 60.0,
    "enable_cors": true,
    "cors_origins": ["*"]
  }
}
```

### 日志配置

```json
{
  "logging": {
    "level": "INFO",
    "log_dir": "logs",
    "console_output": true,
    "file_output": true,
    "json_format": false,
    "max_bytes": 10485760,
    "backup_count": 5
  }
}
```

### 工具配置

```json
{
  "tools": [
    {
      "name": "python.execute",
      "enabled": true,
      "adapter": "python",
      "config": {
        "tool_path": "tools/python_execute.py"
      },
      "timeout": 30.0,
      "retry_count": 3
    }
  ]
}
```

### 适配器配置

#### Python适配器

```json
{
  "name": "python",
  "type": "python",
  "enabled": true,
  "config": {
    "base_path": "assets/projects_new_extracted/src",
    "auto_discover": true,
    "tools": []
  },
  "max_concurrent": 10
}
```

#### Google API适配器

```json
{
  "name": "google",
  "type": "google",
  "enabled": false,
  "config": {
    "api_key": "YOUR_GOOGLE_API_KEY",
    "base_url": "https://www.googleapis.com",
    "timeout": 30.0,
    "max_retries": 3,
    "rate_limit": 100,
    "services": ["search", "translate", "maps", "youtube"]
  },
  "max_concurrent": 5
}
```

## 开发指南

### 创建自定义工具

#### 1. 使用装饰器注册工具

```python
from mcp_server.discovery import tool

@tool(
    name="my_tool",
    description="My custom tool",
    category="custom",
    tags=["custom", "tool"]
)
async def my_custom_tool(param1: str, param2: int = 10) -> dict:
    """Tool description"""
    return {
        "result": f"Processed {param1} with {param2}"
    }
```

#### 2. 创建工具文件

在`tools/`目录下创建Python文件：

```python
# tools/my_tool.py
from mcp_server.discovery import tool

@tool(
    name="tools.my_tool",
    description="My custom tool",
    category="custom"
)
def my_tool(data: str) -> dict:
    return {"processed": data}
```

### 创建自定义适配器

```python
from mcp_server.tool_registry import ToolAdapter, ToolDefinition, ToolMetadata
from mcp_server.discovery import adapter

@adapter(name="my_adapter")
class MyAdapter(ToolAdapter):
    async def initialize(self):
        """初始化适配器"""
        pass
    
    async def execute(self, tool_name: str, params: dict) -> any:
        """执行工具"""
        pass
    
    async def list_tools(self) -> list[ToolDefinition]:
        """列出工具"""
        pass
    
    async def shutdown(self):
        """关闭适配器"""
        pass
```

## 故障排除

### 常见问题

1. **工具未找到**
   - 检查工具发现路径配置
   - 确认工具文件存在且格式正确
   - 查看日志获取详细错误信息

2. **超时错误**
   - 增加工具超时时间
   - 优化工具执行效率
   - 检查网络连接

3. **速率限制**
   - 减少请求频率
   - 增加速率限制配置
   - 使用缓存减少API调用

4. **连接错误**
   - 验证网络连接
   - 检查服务可用性
   - 确认API密钥正确

### 调试

启用调试日志：

```bash
python main.py --log-level DEBUG
```

查看日志文件：

```bash
tail -f logs/mcp_server.log
```

## 性能优化

### 并发配置

调整并发任务数：

```json
{
  "server": {
    "max_connections": 200
  }
}
```

### 速率限制

配置工具和适配器的速率限制：

```json
{
  "tools": [
    {
      "name": "my_tool",
      "rate_limit": 100
    }
  ]
}
```

### 缓存

启用工具结果缓存：

```json
{
  "custom_settings": {
    "tool_cache_ttl": 3600
  }
}
```

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交问题和拉取请求！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送Pull Request
- 联系维护者
