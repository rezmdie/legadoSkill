MCP 知识要点摘要

概述：
- 项目已支持作为标准 MCP（Model Context Protocol）服务器运行，位于 `src/mcp_server.py`，也有包装/启动脚本 `mcp_server_wrapper.py`、`start_mcp_server.py`。

启动与配置：
- 推荐通过 `uvicorn src.main:app` 启动 FastAPI，或使用 `src/mcp_server.py` 以 stdio MCP 模式运行。
- 关键环境变量：`MCP_MODE=true`、`PYTHONUNBUFFERED=1`、`COZE_WORKSPACE_PATH=.`、`COZE_LOG_LEVEL=CRITICAL`（用于禁用日志以避免污染 JSON-RPC）。
- .kilocode / `mcp.json` 提供了 MCP 客户端配置样例（命令为 python + args 指向 uvicorn 或 `src/mcp_server.py`）。

通信与协议：
- 使用 stdio（标准输入/输出）与 JSON-RPC 2.0 进行通信，返回结构化工具调用结果。
- 日志在 MCP 模式下被禁用或降级，避免破坏 JSON 输出流。

暴露的主要工具（摘要）：
- create_book_source：自动为指定网站生成 Legado 书源 JSON。
- analyze_website / smart_web_analyzer：智能分析网站结构（search/list/detail/toc/content）。
- fetch_html / get_full_html：获取完整 HTML，支持 headers/cookies/方法等。
- debug_book_source / legado_debug_book_source：调试书源规则并返回诊断/修复建议。
- edit_book_source / validate_book_source / export_book_source：编辑、验证与导出书源。
- validate_selector / selector_validator：在真实页面上验证 CSS/XPath/JsonPath 选择器。
- search_knowledge / learn_knowledge_base：知识库检索与学习（资产目录下有 ~167 个文档、~24.9MB 知识）。
- element_picker_guide：元素选择器使用指南。

实现要点与注意事项：
- MCP 服务器在启动时应确保 FastAPI 可用（通常本项目在本地启动 uvicorn 于端口 5000，然后 MCP 通过内部 HTTP 调用 `/run` 端点）。
- 为避免输出污染，代码中多处禁用或重定向日志；Windows 下可能需要额外设置控制台编码与路径兼容（脚本尝试创建 `/tmp/...` 路径的备用目录）。
- 工具调用有统一的输入 schema 与结构化返回（字符串或 JSON），并有错误处理以返回结构化错误。

测试与故障排查：
- 测试脚本：`test_mcp_server_import.py`（用于验证 MCP 导入/启动）。
- 常见排错：确认已安装 `mcp` SDK（`pip install mcp`），检查环境变量、Python 路径与 `COZE_WORKSPACE_PATH`，在 Kilo 中重载 MCP 服务。

下一步建议：
1. 若目标是本地在 Kilo 中使用：使用 `mcp.json` 或 `.kilocode/mcp.json` 将服务注册到 Kilo，重载 MCP。
2. 在本地先通过 `python start_mcp_server.py` 或 `python -m uvicorn src.main:app` 验证 FastAPI 可用，然后运行 MCP 模式。
3. 运行 `python test_mcp_server_import.py` 以验证 MCP 接口是否能被正确导入与调用。

文件位置参考（项目根）：
- MCP 使用说明：MCP_SERVER_GUIDE.md
- 启动包装/脚本：mcp_server_wrapper.py, start_mcp_server.py
- 配置示例：mcp.json, mcp_config.json
- MCP 实现：src/mcp_server.py

如需，我可以：
- 将此摘要写入仓库（已完成），或
- 继续逐个工具提取更详细的参数与示例调用，或
- 帮你在本机启动并运行一次简单的调用测试。
