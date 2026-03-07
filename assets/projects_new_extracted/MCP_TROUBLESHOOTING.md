# MCP连接故障排查指南

## 当前状态
- MCP服务器代码：✅ 已创建 (`src/mcp_server.py`)
- 配置文件：✅ 已配置 (`.kilocode/mcp.json`)
- 诊断测试：✅ 服务器可以启动
- Kilo连接：❌ 显示 "Not connected"

## 可能的原因和解决方案

### 1. Kilo IDE缓存问题
**解决方案：**
- 完全关闭Kilo IDE
- 重新打开Kilo IDE
- 等待MCP服务器自动连接

### 2. Python路径问题
**检查：**
```bash
python --version
where python
```

**如果python命令不可用，修改配置：**
```json
{
  "mcpServers": {
    "legado-book-source-tamer": {
      "command": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": ["src/mcp_server.py"],
      "env": {
        "MCP_MODE": "true",
        "COZE_LOG_LEVEL": "CRITICAL"
      }
    }
  }
}
```

### 3. 工作目录问题
**当前配置使用相对路径，Kilo应该在项目根目录执行**

如果不行，尝试添加`cwd`：
```json
{
  "mcpServers": {
    "legado-book-source-tamer": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "cwd": "d:/阅读提示词/pack_project_1771424257048/projects",
      "env": {
        "MCP_MODE": "true",
        "COZE_LOG_LEVEL": "CRITICAL"
      }
    }
  }
}
```

### 4. 依赖问题
**检查所有依赖是否安装：**
```bash
pip install mcp
pip install langchain-core
pip install -r requirements.txt
```

### 5. 查看Kilo日志
**在Kilo IDE中：**
1. 打开开发者工具（如果有）
2. 查看控制台日志
3. 寻找MCP相关的错误信息

### 6. 手动测试MCP服务器
**运行测试脚本：**
```bash
python test_mcp_connection.py
```

**应该看到：**
```
[OK] 连接成功!
[OK] 找到 8 个工具
[OK] 工具调用成功!
```

### 7. 检查端口冲突
MCP使用stdio通信，不应该有端口冲突，但可以检查：
```bash
netstat -ano | findstr :LISTEN
```

### 8. 尝试简化配置
**最简配置：**
```json
{
  "mcpServers": {
    "legado-book-source-tamer": {
      "command": "python",
      "args": ["src/mcp_server.py"]
    }
  }
}
```

## 调试步骤

### 步骤1：验证服务器可以启动
```bash
python diagnose_mcp.py
```
应该显示：`[SUCCESS] 所有诊断检查通过!`

### 步骤2：验证MCP通信
```bash
python test_mcp_connection.py
```
应该显示：`[SUCCESS] 所有测试通过!`

### 步骤3：重启Kilo IDE
1. 完全关闭Kilo IDE
2. 重新打开
3. 打开此项目
4. 等待30秒让MCP服务器连接

### 步骤4：手动刷新
在Kilo MCP面板中点击"刷新 MCP 服务器"

### 步骤5：检查配置文件
确保`.kilocode/mcp.json`格式正确，没有语法错误

## 当前配置文件内容

```json
{
  "mcpServers": {
    "legado-book-source-tamer": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "env": {
        "MCP_MODE": "true",
        "COZE_LOG_LEVEL": "CRITICAL",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## 替代方案

如果Kilo IDE始终无法连接，可以：

1. **使用测试脚本直接调用工具**
   ```bash
   python test_mcp_connection.py
   ```

2. **使用原始FastAPI服务器**
   ```bash
   python src/main.py
   ```
   然后通过HTTP API调用工具

3. **直接导入工具使用**
   ```python
   from src.tools.smart_full_analyzer import analyze_complete_book_source
   result = await analyze_complete_book_source.ainvoke({"url": "https://example.com"})
   ```

## 联系支持

如果以上方法都不行，可能是Kilo IDE的MCP实现有特殊要求。建议：
1. 查看Kilo IDE的MCP文档
2. 查看Kilo IDE的日志文件
3. 联系Kilo IDE支持团队

## 已验证的信息

✅ Python 3.13.11 已安装
✅ MCP SDK 已安装
✅ LangChain Core 已安装
✅ MCP服务器可以启动
✅ MCP服务器可以响应请求
✅ 8个工具已注册
✅ 2个提示模板已配置
✅ 测试脚本全部通过

问题出在Kilo IDE与MCP服务器的连接环节。
