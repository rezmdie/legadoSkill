# MCP工具快速参考

## 🚀 8个MCP工具速查

### 1️⃣ create_book_source - 创建书源
```javascript
{
  "url": "https://www.example.com",      // 必需：目标网站
  "source_name": "示例书源"               // 可选：书源名称
}
```
**用途**: 自动分析网站并生成完整书源配置

---

### 2️⃣ analyze_website - 分析网站
```javascript
{
  "url": "https://www.example.com",      // 必需：要分析的URL
  "page_type": "all"                     // 可选：search|list|detail|toc|content|all
}
```
**用途**: 识别页面结构，提取关键元素

---

### 3️⃣ fetch_html - 获取HTML
```javascript
{
  "url": "https://www.example.com",      // 必需：目标URL
  "method": "GET",                       // 可选：GET|POST
  "headers": {},                         // 可选：自定义headers
  "data": {}                             // 可选：POST数据
}
```
**用途**: 下载网页内容，支持自定义请求

---

### 4️⃣ debug_book_source - 调试书源
```javascript
{
  "book_source_json": "{...}",           // 必需：书源JSON字符串
  "test_url": "https://...",             // 必需：测试URL
  "rule_type": "search"                  // 必需：search|bookList|bookInfo|tocUrl|chapterList|content
}
```
**用途**: 测试书源规则是否正确工作

---

### 5️⃣ edit_book_source - 编辑书源
```javascript
{
  "book_source_json": "{...}",           // 必需：原始书源JSON
  "modifications": {                     // 必需：要修改的内容
    "bookSourceName": "新名称",
    "ruleSearch.bookList": "新规则"
  }
}
```
**用途**: 修改书源配置，更新规则

---

### 6️⃣ validate_selector - 验证选择器
```javascript
{
  "url": "https://www.example.com",      // 必需：测试URL
  "selector": "div.book-item",           // 必需：选择器表达式
  "selector_type": "css"                 // 可选：css|xpath|json
}
```
**用途**: 测试选择器能否提取到目标内容

---

### 7️⃣ search_knowledge - 搜索知识库
```javascript
{
  "query": "CSS选择器",                   // 必需：搜索关键词
  "top_k": 5                             // 可选：返回结果数量
}
```
**用途**: 查找书源开发文档和案例

---

### 8️⃣ get_element_picker_guide - 选择器指南
```javascript
{
  "selector_type": "css"                 // 可选：css|xpath|json|all
}
```
**用途**: 获取选择器语法使用指南

---

## 📋 常用工作流

### 🎯 创建新书源
```
1. analyze_website     → 分析网站结构
2. fetch_html          → 获取示例页面
3. validate_selector   → 验证选择器
4. create_book_source  → 生成书源
5. debug_book_source   → 测试规则
6. edit_book_source    → 优化配置
```

### 🔍 调试现有书源
```
1. debug_book_source   → 测试问题规则
2. validate_selector   → 验证选择器
3. search_knowledge    → 查找解决方案
4. edit_book_source    → 修复问题
5. debug_book_source   → 再次测试
```

### 📚 学习书源开发
```
1. search_knowledge           → 搜索"书源入门"
2. get_element_picker_guide   → 学习选择器
3. analyze_website            → 分析示例网站
4. create_book_source         → 实践创建
```

---

## 🎨 选择器类型

### CSS选择器
```css
div.book-item              /* 类选择器 */
#book-list                 /* ID选择器 */
a[href*="book"]            /* 属性选择器 */
div > a                    /* 子元素选择器 */
div a                      /* 后代选择器 */
```

### XPath
```xpath
//div[@class='book-item']   /* 类选择器 */
//a[contains(@href,'book')] /* 包含选择器 */
//div/a                     /* 子元素 */
//div//a                    /* 后代元素 */
```

### JSONPath
```json
$.data.books[*].name       /* 数组遍历 */
$.data.books[0]            /* 索引访问 */
$..name                    /* 递归查找 */
```

---

## 🔧 规则类型说明

| 规则类型 | 用途 | 测试URL示例 |
|---------|------|------------|
| `search` | 搜索功能 | 搜索结果页 |
| `bookList` | 书籍列表 | 列表页/搜索结果 |
| `bookInfo` | 书籍详情 | 书籍详情页 |
| `tocUrl` | 目录URL | 详情页 |
| `chapterList` | 章节列表 | 目录页 |
| `content` | 章节内容 | 内容页 |

---

## 💡 实用技巧

### 1. 快速测试选择器
```javascript
// 先验证选择器
validate_selector({
  url: "https://example.com/book/123",
  selector: "h1.title"
})

// 再用于书源
```

### 2. 分步调试
```javascript
// 逐个规则测试
debug_book_source({ rule_type: "search" })
debug_book_source({ rule_type: "bookList" })
debug_book_source({ rule_type: "bookInfo" })
// ...
```

### 3. 利用知识库
```javascript
// 遇到问题先搜索
search_knowledge({ query: "反爬虫" })
search_knowledge({ query: "动态加载" })
search_knowledge({ query: "POST请求" })
```

### 4. 查看指南
```javascript
// 不确定语法时
get_element_picker_guide({ selector_type: "css" })
get_element_picker_guide({ selector_type: "xpath" })
```

---

## 🚨 常见问题

### Q: 选择器提取不到内容？
```javascript
// 1. 先验证选择器
validate_selector({...})

// 2. 检查页面是否动态加载
fetch_html({...})  // 查看实际HTML

// 3. 搜索类似案例
search_knowledge({ query: "动态加载" })
```

### Q: 搜索功能不工作？
```javascript
// 1. 分析搜索页面
analyze_website({
  url: "搜索结果页URL",
  page_type: "search"
})

// 2. 调试搜索规则
debug_book_source({
  rule_type: "search",
  test_url: "搜索结果页"
})
```

### Q: 如何处理反爬虫？
```javascript
// 1. 搜索知识库
search_knowledge({ query: "反爬虫" })

// 2. 自定义headers
fetch_html({
  url: "...",
  headers: {
    "User-Agent": "...",
    "Referer": "..."
  }
})
```

---

## 📖 更多资源

- **完整文档**: [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)
- **工具清单**: [TOOLS_INVENTORY.md](TOOLS_INVENTORY.md)
- **项目报告**: [MCP_FINAL_REPORT.md](MCP_FINAL_REPORT.md)
- **成功案例**: [sudugu_book_source_final.json](sudugu_book_source_final.json)

---

**提示**: 在Kilo IDE中，输入 `mcp.` 可以看到所有可用工具的自动补全
