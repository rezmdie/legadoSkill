"""
元素选择指南工具
帮助用户生成XPath和CSS选择器规则，并提供元素选择指南
"""

import json
from langchain.tools import tool, ToolRuntime


# 辅助函数：生成元素选择指南内容（不使用@tool装饰）
def _generate_element_guide_content(element_type: str = "") -> str:
    """生成元素选择指南内容（辅助函数）"""
    
    # 元素类型配置
    element_configs = {
        "书名": {
            "description": "书籍名称",
            "typical_selectors": [".book-name", ".title", "h1", "h2", ".book-title"],
            "xpath_examples": [
                "//h1[@class='book-name']/text()",
                "//h2[@class='title']/text()",
                "//div[@class='book-info']/h3/text()",
                "//span[@class='book-title']/text()"
            ],
            "css_examples": [
                ".book-name@text",
                ".title@text",
                "h1@text",
                ".book-title@text"
            ],
            "tips": [
                "书名通常在h1、h2或h3标签中",
                "注意提取纯文本，避免包含标签",
                "检查是否在a标签中（可能是链接文本）"
            ]
        },
        "作者": {
            "description": "作者姓名",
            "typical_selectors": [".author", ".book-author", "span.author", ".writer"],
            "xpath_examples": [
                "//p[@class='author']/text()",
                "//span[@class='book-author']/text()",
                "//div[@class='book-info']/span[@class='author']/text()"
            ],
            "css_examples": [
                ".author@text",
                ".book-author@text",
                "span.author@text",
                ".writer@text"
            ],
            "tips": [
                "作者名通常在span或p标签中",
                "可能包含'作者:'等前缀，需要清理",
                "注意区分作者名和其他文本"
            ]
        },
        "封面": {
            "description": "书籍封面图片",
            "typical_selectors": [".cover img", ".book-img img", "img.cover", ".poster"],
            "xpath_examples": [
                "//img[@class='cover']/@src",
                "//div[@class='book-img']/img/@src",
                "//img[contains(@src,'cover')]/@src"
            ],
            "css_examples": [
                ".cover img@src",
                ".book-img img@src",
                "img.cover@src",
                ".poster@src"
            ],
            "tips": [
                "封面通常是img标签的src属性",
                "使用@src提取图片URL",
                "注意检查是否是懒加载（data-src）"
            ]
        },
        "简介": {
            "description": "书籍简介",
            "typical_selectors": [".intro", ".description", ".book-desc", ".summary"],
            "xpath_examples": [
                "//p[@class='intro']/text()",
                "//div[@class='description']/text()",
                "//div[@class='book-info']//p[@class='desc']/text()"
            ],
            "css_examples": [
                ".intro@text",
                ".description@text",
                ".book-desc@text",
                ".summary@text"
            ],
            "tips": [
                "简介可能是多行文本，注意拼接",
                "可能包含HTML标签，需要清理",
                "注意字数限制"
            ]
        },
        "书名列表": {
            "description": "搜索或发现页的书籍列表容器",
            "typical_selectors": [".book-list", ".result-list", ".books", ".search-result"],
            "xpath_examples": [
                "//div[@class='book-list']",
                "//ul[@class='books']",
                "//div[contains(@class,'result-list')]"
            ],
            "css_examples": [
                ".book-list",
                ".result-list",
                ".books"
            ],
            "tips": [
                "书籍列表是一个容器，包含多个书籍项",
                "每个书籍项应该是兄弟元素",
                "注意区分列表和单个书籍项"
            ]
        },
        "章节列表": {
            "description": "目录页的章节列表",
            "typical_selectors": [".chapter-list", ".toc-list", ".catalog", "ul.chapters"],
            "xpath_examples": [
                "//ul[@class='chapter-list']/li",
                "//div[@class='catalog']/div[@class='chapter']",
                "//div[contains(@class,'toc')]/div"
            ],
            "css_examples": [
                ".chapter-list li",
                ".catalog .chapter",
                ".toc > div"
            ],
            "tips": [
                "章节列表包含多个章节",
                "每个章节可能包含章节名和章节链接",
                "注意是否分页"
            ]
        },
        "章节名称": {
            "description": "章节标题",
            "typical_selectors": [".chapter-title", "a", "[class*='chapter']"],
            "xpath_examples": [
                "//li/a/text()",
                "//div[@class='chapter']/a/text()",
                "//span[@class='chapter-title']/text()"
            ],
            "css_examples": [
                "a",
                ".chapter-title",
                ".chapter a"
            ],
            "tips": [
                "章节名称通常在a标签中",
                "检查是否需要提取纯文本或保留链接",
                "注意是否包含章节号"
            ]
        },
        "章节链接": {
            "description": "章节URL",
            "typical_selectors": ["a[href]"],
            "xpath_examples": [
                "//li/a/@href",
                "//div[@class='chapter']/a/@href",
                "//a[contains(@href,'chapter')]/@href"
            ],
            "css_examples": [
                "a@href",
                ".chapter a@href",
                "a[href*='chapter']@href"
            ],
            "tips": [
                "章节链接在a标签的href属性中",
                "使用@href提取属性值",
                "可能需要处理相对路径"
            ]
        },
        "正文": {
            "description": "章节正文内容",
            "typical_selectors": [".content", ".article", "#content", "#chapter-content", ".text"],
            "xpath_examples": [
                "//div[@id='content']/text()",
                "//div[@class='article']/text()",
                "//div[@class='chapter-content']//text()",
                "//div[@id='text']//p/text()"
            ],
            "css_examples": [
                "#content",
                ".article",
                ".chapter-content",
                "#text"
            ],
            "tips": [
                "正文内容通常在div容器中",
                "可能包含多个p标签，需要拼接",
                "注意去除广告和无关内容",
                "检查是否需要清理空格和换行"
            ]
        }
    }
    
    # 如果没有指定元素类型，返回通用指南
    if not element_type or element_type not in element_configs:
        return """
## 🎯 元素选择指南 - 通用版

### 📚 支持的元素类型

- **书名** - 书籍名称
- **作者** - 作者姓名
- **封面** - 书籍封面图片
- **简介** - 书籍简介
- **书名列表** - 搜索/发现页的书籍列表
- **章节列表** - 目录页的章节列表
- **章节名称** - 章节标题
- **章节链接** - 章节URL
- **正文** - 章节正文内容

### 🔧 使用方法

指定具体的元素类型以获取详细的指南：

```
element_picker_guide(element_type="书名")
element_picker_guide(element_type="章节列表")
```

### 💡 快速开始

1. **打开浏览器开发者工具**
   - 按F12或右键 -> 检查

2. **定位目标元素**
   - 按Ctrl+Shift+C点击页面元素

3. **查看HTML结构**
   - 在Elements面板中查看元素标签、class、id

4. **生成选择器**
   - 右键元素 -> Copy -> Copy selector（CSS）
   - 右键元素 -> Copy -> Copy XPath

5. **转换为Legado格式**
   - CSS选择器：添加@属性或@text
   - XPath选择器：保持原样

### 📊 选择器语法

**CSS选择器（Legado格式）**：
```css
.class@text           # 提取文本
.class@href           # 提取链接
#id@src               # 提取图片
div.class span@text   # 嵌套选择
```

**XPath选择器**：
```xpath
//div[@class='title']/text()    # 提取文本
//a/@href                        # 提取链接
//img/@src                       # 提取图片
```
"""
    
    # 获取配置
    config = element_configs[element_type]
    
    # 生成指南
    guide = f"""
## 🎯 元素选择指南 - {element_type}

### 📋 元素描述
**描述**：{config['description']}

### 🔍 典型的CSS选择器
```css
{chr(10).join(config['typical_selectors'])}
```

### 📝 XPath规则示例
```xpath
{chr(10).join(config['xpath_examples'])}
```

### 🎨 CSS规则示例（Legado格式）
```css
{chr(10).join(config['css_examples'])}
```

### 💡 选择技巧
{chr(10).join([f"- {tip}" for tip in config['tips']])}

### 🛠️ 浏览器开发者工具使用步骤

1. **打开网页**
   ```
   在浏览器中打开目标网站
   ```

2. **打开开发者工具**
   ```
   按F12 或 右键 -> 检查
   ```

3. **选择元素**
   ```
   按Ctrl+Shift+C（或点击元素选择器图标）
   点击页面上想要提取的{element_type}
   ```

4. **查看元素结构**
   ```
   在Elements面板中查看HTML结构
   记录元素的标签名、class、id等属性
   ```

5. **生成选择器**
   ```
   在元素上右键 -> Copy -> Copy selector
   或手动编写选择器
   ```

6. **测试选择器**
   ```
   在控制台测试：
   document.querySelector('选择器')
   检查是否选中正确的元素
   ```

### 📊 选择器优先级

**推荐顺序**：
1. ID选择器（#id）- 最精确
2. Class选择器（.class）- 最常用
3. 属性选择器（[attr=value]）- 适合特殊属性
4. 标签选择器（tag）- 最宽泛

**示例**：
```css
/* 优先级从高到低 */
#content              /* ID选择器 */
.chapter-title        /* Class选择器 */
a[href*='chapter']    /* 属性选择器 */
div                   /* 标签选择器 */
```

### ⚠️ 注意事项

1. **相对路径与绝对路径**
   - 优先使用相对路径（从当前元素查找）
   - 避免使用绝对路径（从根元素查找）

2. **动态ID和Class**
   - 避免使用动态生成的ID（如 id="book-12345"）
   - 优先使用稳定的Class名称

3. **嵌套关系**
   - 理解父子关系和兄弟关系
   - 使用适当的轴表达式（//, /, ..）

4. **Legado语法**
   - XPath：`//div[@class='title']/text()`
   - CSS：`div.title@text`
   - 属性提取：`@href`, `@src`

### 🎯 实际应用示例

**示例1：提取书名**
```css
/* XPath */
//h1[@class='book-title']/text()

/* CSS (Legado格式) */
.book-title@text
```

**示例2：提取作者**
```css
/* XPath */
//p[@class='author']/text()

/* CSS (Legado格式) */
.author@text
```

**示例3：提取章节链接**
```css
/* XPath */
//ul[@class='chapter-list']/li/a/@href

/* CSS (Legado格式) */
.chapter-list li a@href
```

### 📝 完整流程

1. **分析网页结构** - 使用开发者工具查看HTML
2. **选择合适的选择器** - 根据元素特征选择
3. **测试选择器** - 在浏览器控制台验证
4. **转换为Legado格式** - 应用@属性或text()
5. **应用到书源** - 填写规则字段
6. **实际测试** - 在Legado APP中验证

---

💡 **提示**：如果你有具体的HTML片段，可以使用 `generate_selector_suggestions` 工具来生成更精确的选择器！
"""
    
    return guide


@tool
def element_picker_guide(
    element_type: str = "",
    target_field: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    生成元素选择指南和选择器规则
    
    Args:
        element_type: 元素类型（书名/作者/封面/简介/书名列表/章节列表/正文等）
        target_field: 目标规则字段（如 ruleSearch.name, ruleToc.chapterName 等）
    
    Returns:
        元素选择指南和选择器规则建议
    """
    
    # 调用辅助函数生成指南
    guide = _generate_element_guide_content(element_type)
    
    # 如果指定了目标字段，添加字段说明
    if target_field:
        field_info = f"""

### 📌 目标规则字段

**字段名称**：`{target_field}`

**填写位置**：在书源JSON中找到该字段，填入生成的选择器规则

**示例**：
```json
{{
  "ruleSearch": {{
    "name": ".book-title@text"
  }}
}}
```
"""
        guide += field_info
    
    return guide


@tool
def generate_selector_suggestions(
    html_structure: str = "",
    element_type: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    根据HTML结构生成选择器建议
    
    Args:
        html_structure: HTML片段（简化版）
        element_type: 元素类型（书名/作者等）
    
    Returns:
        选择器建议和规则
    """
    
    if not html_structure:
        return """
## 📝 HTML结构分析工具

请提供HTML片段来生成选择器建议。

### 使用方法
```
generate_selector_suggestions(
    html_structure="<div class='book-list'>...</div>",
    element_type="书名"
)
```

### 示例HTML
```html
<div class="book-list">
  <div class="book-item">
    <div class="book-img">
      <img src="cover.jpg" class="cover">
    </div>
    <div class="book-info">
      <h3 class="book-name">书名</h3>
      <p class="author">作者名</p>
      <p class="intro">简介...</p>
    </div>
  </div>
</div>
```

### 💡 获取HTML结构的方法
1. 在浏览器中右键 -> 检查
2. 在Elements面板中找到目标元素
3. 右键 -> Copy -> Copy outerHTML
4. 粘贴到本工具中
        """
    
    # 分析HTML结构并生成建议
    suggestions = []
    
    # 检测标签
    if '<h1' in html_structure:
        suggestions.append("检测到h1标签，可能是标题/书名")
    if '<h2' in html_structure:
        suggestions.append("检测到h2标签，可能是标题/章节名")
    if '<h3' in html_structure:
        suggestions.append("检测到h3标签，可能是标题/章节名")
    
    # 检测class
    if 'class=' in html_structure:
        import re
        classes = re.findall(r'class=["\']([^"\']+)["\']', html_structure)
        if classes:
            suggestions.append(f"检测到class: {', '.join(set(classes))}")
    
    # 检测img
    if '<img' in html_structure:
        suggestions.append("检测到img标签，可能是封面图片")
        if 'src=' in html_structure:
            suggestions.append("可以使用 @src 提取图片URL")
    
    # 检测a标签
    if '<a' in html_structure:
        suggestions.append("检测到a标签，可能是链接")
        if 'href=' in html_structure:
            suggestions.append("可以使用 @href 提取URL")
    
    # 生成具体建议
    result = f"""
## 🎯 元素选择建议

### 📊 结构分析
{chr(10).join([f"- {s}" for s in suggestions]) if suggestions else "- 未检测到明显的特征"}

### 💡 推荐选择器

#### XPath规则
```xpath
//选择器规则
```

#### CSS规则（Legado格式）
```css
选择器规则@属性
```

### 🎨 规则生成建议

1. **最精确的选择**
   - 优先使用ID或唯一的Class
   - 避免使用动态ID

2. **相对路径选择**
   - 从最近的父元素开始
   - 使用 > 表示直接子元素

3. **属性选择**
   - 使用@提取属性值（如@href, @src）
   - 使用text()提取文本内容

### 🔧 快速开始

1. 查看下方的详细指南
2. 使用浏览器开发者工具测试选择器
3. 将规则应用到书源配置中
4. 在Legado APP中测试效果

### 📚 完整指南

{_generate_element_guide_content(element_type)}
    """
    
    return result


@tool
def browser_debug_helper(
    url: str = "",
    instruction: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    浏览器调试帮助工具
    
    Args:
        url: 网页URL
        instruction: 具体需求（如"提取书名"、"查找封面"等）
    
    Returns:
        调试步骤和指南
    """
    
    guide = f"""
## 🌐 浏览器调试指南

### 📋 任务信息

**目标URL**：{url if url else "（未指定）"}

**需求说明**：{instruction if instruction else "（未指定）"}

---

### 🔧 Chrome开发者工具使用步骤

#### 步骤1：打开网页
```
在Chrome浏览器中打开目标网页
```

#### 步骤2：打开开发者工具
```
方法1：按F12键
方法2：右键 -> 检查
方法3：Ctrl+Shift+I（Windows）或Cmd+Option+I（Mac）
```

#### 步骤3：使用Elements面板
```
1. 点击Elements标签
2. 按Ctrl+Shift+C（或点击左上角的箭头图标）
3. 在页面上点击想要定位的元素
4. Elements面板会自动高亮对应的HTML代码
```

#### 步骤4：复制选择器
```
在Elements面板中：
1. 右键点击高亮的HTML元素
2. 选择 Copy
3. 选择 Copy selector（CSS选择器）或 Copy XPath（XPath选择器）
```

#### 步骤5：测试选择器
```
在Console面板中测试：

// 测试CSS选择器
document.querySelector('.class-name')

// 测试XPath（需要扩展）
$x('//div[@class="title"]')

// 查看元素内容
document.querySelector('.class-name').textContent
document.querySelector('.class-name').href
```

#### 步骤6：转换为Legado格式
```
CSS选择器转换：
.class-name -> .class-name@text
a[href] -> a@href
img -> img@src

XPath选择器：
//div[@class='title']/text() -> 直接使用
//a/@href -> 直接使用
```

---

### 💡 常见场景

#### 场景1：提取书名
```
1. 定位到书名元素（通常在h1、h2或特定class中）
2. 右键 -> Copy -> Copy selector
3. 转换为Legado格式：.book-title@text
4. 填写到 ruleBookInfo.name 或 ruleSearch.name
```

#### 场景2：提取作者
```
1. 定位到作者元素（通常在span、p或特定class中）
2. 右键 -> Copy -> Copy selector
3. 转换为Legado格式：.author@text
4. 填写到 ruleBookInfo.author 或 ruleSearch.author
```

#### 场景3：提取封面图片
```
1. 定位到图片元素（img标签）
2. 右键 -> Copy -> Copy selector
3. 转换为Legado格式：img@src
4. 填写到 ruleBookInfo.coverUrl 或 ruleSearch.coverUrl
```

#### 场景4：提取章节列表
```
1. 定位到章节列表容器
2. 右键 -> Copy -> Copy selector
3. 转换为Legado格式：.chapter-list li
4. 填写到 ruleToc.chapterList
```

#### 场景5：提取正文内容
```
1. 定位到正文容器（通常在div中）
2. 右键 -> Copy -> Copy selector
3. 转换为Legado格式：#content
4. 填写到 ruleContent.content
```

---

### ⚠️ 注意事项

1. **相对路径 vs 绝对路径**
   - 优先使用相对路径（更稳健）
   - 避免使用从body开始的绝对路径

2. **动态class和id**
   - 避免使用动态生成的class（如 .item-12345）
   - 优先使用稳定的语义化class（如 .book-title）

3. **嵌套结构**
   - 理解父子关系和兄弟关系
   - 使用适当的选择器组合

4. **特殊属性**
   - 检查是否有data-*属性
   - 检查是否有自定义属性

---

### 🐛 常见问题排查

#### 问题1：选择器匹配到多个元素
```
解决方案：
1. 使用更精确的选择器
2. 添加父容器限制
3. 使用:nth-child()指定第几个元素
```

#### 问题2：选择器匹配不到元素
```
解决方案：
1. 检查元素是否在iframe中
2. 检查元素是否是动态加载的
3. 检查class名称是否正确
4. 检查元素是否被隐藏或display:none
```

#### 问题3：提取到空值
```
解决方案：
1. 确认选择器是否正确
2. 检查元素是否有文本内容
3. 检查是否需要等待页面加载完成
4. 检查是否需要处理懒加载
```

---

### 📚 相关工具

- **element_picker_guide** - 获取特定元素类型的详细指南
- **generate_selector_suggestions** - 根据HTML结构生成选择器
- **search_knowledge** - 搜索更多选择器示例和技巧

---

### ✅ 完成检查清单

在应用选择器到书源之前，请确保：

- [ ] 已在浏览器控制台测试选择器
- [ ] 选择器能正确匹配目标元素
- [ ] 提取的内容符合预期
- [ ] 已转换为Legado格式
- [ ] 已填写到正确的规则字段

---

💡 **提示**：选择器调试是一个迭代过程，可能需要多次尝试和优化。遇到问题时，多使用浏览器开发者工具检查元素结构！
"""
    
    return guide
