# MCP工具列表文档

生成时间: 2026-02-19 00:33:54
工具总数: 22
函数总数: 57

## 工具分类

### 智能分析工具

#### smart_web_analyzer

- **文件**: `smart_web_analyzer.py`
- **函数数**: 7
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `parse_qs`: Parse a query given as a string argument.

Argumen...
  - `tool`: Convert Python functions and `Runnables` to LangCh...
  - `urlencode`: Encode a dict or sequence of two-element tuples in...
  - `urljoin`: 简单的URL拼接...
  - `urlparse`: Parse a URL into 6 components:
<scheme>://<netloc>...
  - `urlunparse`: Put a parsed URL back together again.  This may re...

#### smart_bookinfo_analyzer

- **文件**: `smart_bookinfo_analyzer.py`
- **函数数**: 5
- **函数列表**:
  - `get_real_web_validator`: 获取全局真实网页验证器实例...
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `save_html_permanently`: 永久保存HTML

Args:
    url: 网页URL
    html: HTML内容

R...
  - `tool`: Convert Python functions and `Runnables` to LangCh...
  - `validate_real_html_required`: 验证HTML是否是真实的

Args:
    html: HTML内容

Returns:
   ...

#### smart_toc_analyzer

- **文件**: `smart_toc_analyzer.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### smart_content_analyzer

- **文件**: `smart_content_analyzer.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### smart_full_analyzer

- **文件**: `smart_full_analyzer.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

### 网页获取工具

#### smart_fetcher

- **文件**: `smart_fetcher.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### web_fetch_tool

- **文件**: `web_fetch_tool.py`
- **函数数**: 3
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...
  - `urljoin`: Join a base URL and a possibly relative URL to for...

### 知识库工具

#### knowledge_tools

- **文件**: `knowledge_tools.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### knowledge_index_tool

- **文件**: `knowledge_index_tool.py`
- **函数数**: 4
- **函数列表**:
  - `get_content_splitter`: 获取内容分割器实例...
  - `get_knowledge_index_searcher`: 获取知识库索引搜索器实例...
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### knowledge_auditor

- **文件**: `knowledge_auditor.py`
- **函数数**: 5
- **函数列表**:
  - `get_html_storage_path`: 获取HTML存储路径

Args:
    url: 网页URL

Returns:
    存储路...
  - `load_html_permanently`: 加载永久保存的HTML

Args:
    url: 网页URL

Returns:
    HT...
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `save_html_permanently`: 永久保存HTML

Args:
    url: 网页URL
    html: HTML内容

R...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

### 调试工具

#### legado_debugger

- **文件**: `legado_debugger.py`
- **函数数**: 3
- **函数列表**:
  - `test_debugger`: 测试调试器...
  - `urljoin`: Join a base URL and a possibly relative URL to for...
  - `urlparse`: Parse a URL into 6 components:
<scheme>://<netloc>...

#### book_source_debugger

- **文件**: `book_source_debugger.py`
- **函数数**: 1
- **函数列表**:
  - `test_book_source_debugger`: 测试书源调试器...

#### legado_debug_tools

- **文件**: `legado_debug_tools.py`
- **函数数**: 4
- **函数列表**:
  - `debug_book_source`: 调试书源规则

Args:
    book_source_json: 书源JSON字符串
    ...
  - `format_debug_result`: 格式化调试结果为可读字符串

Args:
    result: 调试结果字典

Returns:
...
  - `quick_test`: 快速测试规则并返回格式化结果

Args:
    html_content: HTML内容
   ...
  - `test_legado_rule`: 测试单个Legado规则

Args:
    html_content: HTML内容
    r...

### 编辑验证工具

#### book_source_editor

- **文件**: `book_source_editor.py`
- **函数数**: 1
- **函数列表**:
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### selector_validator

- **文件**: `selector_validator.py`
- **函数数**: 3
- **函数列表**:
  - `get_real_web_validator`: 获取全局真实网页验证器实例...
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### collaborative_edit

- **文件**: `collaborative_edit.py`
- **函数数**: 3
- **函数列表**:
  - `get_real_web_validator`: 获取全局真实网页验证器实例...
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### user_intervention

- **文件**: `user_intervention.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

### 可视化工具

#### element_picker_guide

- **文件**: `element_picker_guide.py`
- **函数数**: 1
- **函数列表**:
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### book_source_html_editor

- **文件**: `book_source_html_editor.py`
- **函数数**: 1
- **函数列表**:
  - `tool`: Convert Python functions and `Runnables` to LangCh...

### 其他工具

#### book_source_crawler

- **文件**: `book_source_crawler.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### legado_tools

- **文件**: `legado_tools.py`
- **函数数**: 1
- **函数列表**:
  - `tool`: Convert Python functions and `Runnables` to LangCh...

#### knowledge_search_tool

- **文件**: `knowledge_search_tool.py`
- **函数数**: 1
- **函数列表**:
  - `tool`: Convert Python functions and `Runnables` to LangCh...

## 完整工具列表

### book_source_crawler

- **文件**: `book_source_crawler.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### book_source_debugger

- **文件**: `book_source_debugger.py`
- **函数数**: 1
- **函数列表**:
  - `test_book_source_debugger`
    - 签名: `()`
    - 文档: 测试书源调试器...

### book_source_editor

- **文件**: `book_source_editor.py`
- **函数数**: 1
- **函数列表**:
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### book_source_html_editor

- **文件**: `book_source_html_editor.py`
- **函数数**: 1
- **函数列表**:
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### collaborative_edit

- **文件**: `collaborative_edit.py`
- **函数数**: 3
- **函数列表**:
  - `get_real_web_validator`
    - 签名: `(timeout: int = 30) -> utils.real_web_validator.RealWebValidator`
    - 文档: 获取全局真实网页验证器实例...
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### element_picker_guide

- **文件**: `element_picker_guide.py`
- **函数数**: 1
- **函数列表**:
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### knowledge_auditor

- **文件**: `knowledge_auditor.py`
- **函数数**: 5
- **函数列表**:
  - `get_html_storage_path`
    - 签名: `(url: str) -> str`
    - 文档: 获取HTML存储路径

Args:
    url: 网页URL

Returns:
    存储路径...
  - `load_html_permanently`
    - 签名: `(url: str) -> Optional[Dict[str, Any]]`
    - 文档: 加载永久保存的HTML

Args:
    url: 网页URL

Returns:
    HTML内容和元数据，如果不存在则返回None...
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `save_html_permanently`
    - 签名: `(url: str, html: str) -> str`
    - 文档: 永久保存HTML

Args:
    url: 网页URL
    html: HTML内容

Returns:
    保存路径...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### knowledge_index_tool

- **文件**: `knowledge_index_tool.py`
- **函数数**: 4
- **函数列表**:
  - `get_content_splitter`
    - 签名: `() -> utils.content_splitter.ContentSplitter`
    - 文档: 获取内容分割器实例...
  - `get_knowledge_index_searcher`
    - 签名: `() -> utils.content_splitter.KnowledgeIndexSearcher`
    - 文档: 获取知识库索引搜索器实例...
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### knowledge_search_tool

- **文件**: `knowledge_search_tool.py`
- **函数数**: 1
- **函数列表**:
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### knowledge_tools

- **文件**: `knowledge_tools.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### legado_debug_tools

- **文件**: `legado_debug_tools.py`
- **函数数**: 4
- **函数列表**:
  - `debug_book_source`
    - 签名: `(book_source_json: str, keyword: str = '斗破苍穹', test_type: str = 'full') -> Dict[str, Any]`
    - 文档: 调试书源规则

Args:
    book_source_json: 书源JSON字符串
    keyword: 测试关键词
    test_type: 测试类型
        - "full...
  - `format_debug_result`
    - 签名: `(result: Dict[str, Any]) -> str`
    - 文档: 格式化调试结果为可读字符串

Args:
    result: 调试结果字典

Returns:
    格式化的字符串...
  - `quick_test`
    - 签名: `(html_content: str, rule: str) -> str`
    - 文档: 快速测试规则并返回格式化结果

Args:
    html_content: HTML内容
    rule: 规则字符串

Returns:
    格式化的测试结果...
  - `test_legado_rule`
    - 签名: `(html_content: str, rule: str, base_url: str = '') -> Dict[str, Any]`
    - 文档: 测试单个Legado规则

Args:
    html_content: HTML内容
    rule: 规则字符串（如 ".title@text", "text.下一章@href"）
    b...

### legado_debugger

- **文件**: `legado_debugger.py`
- **函数数**: 3
- **函数列表**:
  - `test_debugger`
    - 签名: `()`
    - 文档: 测试调试器...
  - `urljoin`
    - 签名: `(base, url, allow_fragments=True)`
    - 文档: Join a base URL and a possibly relative URL to form an absolute
interpretation of the latter....
  - `urlparse`
    - 签名: `(url, scheme='', allow_fragments=True)`
    - 文档: Parse a URL into 6 components:
<scheme>://<netloc>/<path>;<params>?<query>#<fragment>

The result is...

### legado_tools

- **文件**: `legado_tools.py`
- **函数数**: 1
- **函数列表**:
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### selector_validator

- **文件**: `selector_validator.py`
- **函数数**: 3
- **函数列表**:
  - `get_real_web_validator`
    - 签名: `(timeout: int = 30) -> utils.real_web_validator.RealWebValidator`
    - 文档: 获取全局真实网页验证器实例...
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### smart_bookinfo_analyzer

- **文件**: `smart_bookinfo_analyzer.py`
- **函数数**: 5
- **函数列表**:
  - `get_real_web_validator`
    - 签名: `(timeout: int = 30) -> utils.real_web_validator.RealWebValidator`
    - 文档: 获取全局真实网页验证器实例...
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `save_html_permanently`
    - 签名: `(url: str, html: str) -> str`
    - 文档: 永久保存HTML

Args:
    url: 网页URL
    html: HTML内容

Returns:
    保存路径...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...
  - `validate_real_html_required`
    - 签名: `(html: str) -> bool`
    - 文档: 验证HTML是否是真实的

Args:
    html: HTML内容

Returns:
    是否是真实HTML...

### smart_content_analyzer

- **文件**: `smart_content_analyzer.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### smart_fetcher

- **文件**: `smart_fetcher.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### smart_full_analyzer

- **文件**: `smart_full_analyzer.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### smart_toc_analyzer

- **文件**: `smart_toc_analyzer.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### smart_web_analyzer

- **文件**: `smart_web_analyzer.py`
- **函数数**: 7
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `parse_qs`
    - 签名: `(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace', max_num_fields=None, separator='&')`
    - 文档: Parse a query given as a string argument.

Arguments:

qs: percent-encoded query string to be parsed...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...
  - `urlencode`
    - 签名: `(query, doseq=False, safe='', encoding=None, errors=None, quote_via=<function quote_plus at 0x00000184D885A660>)`
    - 文档: Encode a dict or sequence of two-element tuples into a URL query string.

If any values in the query...
  - `urljoin`
    - 签名: `(base: str, url: str) -> str`
    - 文档: 简单的URL拼接...
  - `urlparse`
    - 签名: `(url, scheme='', allow_fragments=True)`
    - 文档: Parse a URL into 6 components:
<scheme>://<netloc>/<path>;<params>?<query>#<fragment>

The result is...
  - `urlunparse`
    - 签名: `(components)`
    - 文档: Put a parsed URL back together again.  This may result in a
slightly different, but equivalent URL, ...

### user_intervention

- **文件**: `user_intervention.py`
- **函数数**: 2
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...

### web_fetch_tool

- **文件**: `web_fetch_tool.py`
- **函数数**: 3
- **函数列表**:
  - `new_context`
    - 签名: `(method: str, headers: Optional[Mapping[str, str]] = None) -> coze_coding_utils.runtime_ctx.context.Context`
    - 文档: 创建上下文对象，读取必要环境变量并可从请求头补充可选字段。...
  - `tool`
    - 签名: `(name_or_callable: str | collections.abc.Callable | None = None, runnable: langchain_core.runnables.base.Runnable | None = None, *args: Any, description: str | None = None, return_direct: bool = False, args_schema: type[pydantic.main.BaseModel] | dict[str, typing.Any] | None = None, infer_schema: bool = True, response_format: Literal['content', 'content_and_artifact'] = 'content', parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, typing.Any] | None = None) -> langchain_core.tools.base.BaseTool | collections.abc.Callable[[collections.abc.Callable | langchain_core.runnables.base.Runnable], langchain_core.tools.base.BaseTool]`
    - 文档: Convert Python functions and `Runnables` to LangChain tools.

Can be used as a decorator with or wit...
  - `urljoin`
    - 签名: `(base, url, allow_fragments=True)`
    - 文档: Join a base URL and a possibly relative URL to form an absolute
interpretation of the latter....

