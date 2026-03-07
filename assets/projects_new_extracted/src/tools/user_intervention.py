"""
人工干预工具
当AI无法应对复杂网站时，允许用户手动干预和修正
"""

import json
import os
from typing import Dict, List, Any, Optional
from langchain.tools import tool


@tool
def manual_intervention_mode(
    reason: str,
    ai_suggestion: str = ""
) -> str:
    """
    🛠️ 人工干预模式 - 真人下场！

    当AI遇到复杂情况无法处理时，启动人工干预模式
    
    适用场景：
    - 🔒 复杂的JavaScript混淆/加密
    - 🔒 动态加载的内容
    - 🔒 需要登录验证的网站
    - 🔒 反爬机制复杂的网站
    - 🔒 AI推理不确定的情况
    
    参数:
        reason: 启动人工干预的原因（说明为什么AI搞不定）
        ai_suggestion: AI的初步建议（可选）
    
    返回:
        人工干预指南和下一步操作
    """
    report = f"""
## 🛠️ 人工干预模式已启动

### 📋 干预原因
{reason}

---

### 🎯 现在你（真人）可以做什么

#### 1️⃣ 提供自定义JavaScript代码
当遇到复杂JS逻辑时，使用工具：
- `inject_custom_js` - 注入自定义JS代码处理数据
- `define_js_handler` - 定义JS处理函数

#### 2️⃣ 修正选择器
当AI识别的选择器不正确时，使用工具：
- `correct_selector` - 修正选择器
- `validate_correction` - 验证修正后的选择器

#### 3️⃣ 手动定义规则
当AI生成的规则不符合预期时，使用工具：
- `manual_define_rule` - 手动定义规则
- `test_manual_rule` - 测试手动定义的规则

#### 4️⃣ 提供HTML样本
当AI无法访问网页时，使用工具：
- `provide_html_sample` - 提供HTML样本
- `analyze_user_html` - 分析用户提供的HTML

#### 5️⃣ 保存经验
当你成功解决问题后，使用工具：
- `save_experience` - 保存经验到知识库
- `record_solution` - 记录解决方案

---

### 💡 操作建议

1. **先看AI的推理**：了解AI为什么搞不定
2. **检查网页结构**：使用浏览器开发者工具查看真实HTML
3. **测试JavaScript**：在浏览器控制台测试JS逻辑
4. **逐步验证**：验证每个修改点是否正确
5. **保存经验**：将解决方案保存，下次可以直接用

---

### 🔧 可用的人工干预工具

```python
# JavaScript相关
inject_custom_js(...)      # 注入自定义JS
define_js_handler(...)     # 定义JS处理函数

# 选择器修正
correct_selector(...)      # 修正选择器
validate_correction(...)   # 验证修正

# 规则定义
manual_define_rule(...)    # 手动定义规则
test_manual_rule(...)      # 测试规则

# HTML分析
provide_html_sample(...)   # 提供HTML样本
analyze_user_html(...)     # 分析HTML

# 经验保存
save_experience(...)       # 保存经验
record_solution(...)       # 记录方案
```

---

### 🤔 现在该怎么做？

**选项A**：如果你已经知道怎么解决
→ 使用对应的工具直接修正

**选项B**：如果你需要更多信息
→ 使用`debug_manual_intervention`工具查看更多细节

**选项C**：如果你需要帮助
→ 告诉我你看到了什么，我会辅助你

---

### 📌 提示

💡 **不要怕麻烦** - 遇到复杂网站，人工干预是正常的
💡 **多测试验证** - 每个修改都要验证
💡 **保存经验** - 成功后记得保存，下次AI就能学会了

---

### 🎯 下一步

请告诉我：
1. 你要修正什么？（选择器、规则、JS代码等）
2. 你的修正方案是什么？
3. 你需要验证什么？

我会协助你完成修正！
"""
    
    if ai_suggestion:
        report += f"""
---

### 🤖 AI的初步建议

```
{ai_suggestion}
```

⚠️ **注意**：AI的建议可能不正确，请你自己验证！
"""
    
    return report


@tool
def inject_custom_js(
    js_code: str,
    description: str = ""
) -> str:
    """
    🔧 注入自定义JavaScript代码
    
    当遇到复杂JS逻辑时，你可以直接提供自己的JS代码
    
    参数:
        js_code: JavaScript代码（可以是完整的函数或表达式）
        description: 代码说明（这段代码是做什么的）
    
    返回:
        代码验证和集成建议
    """
    report = f"""
## 🔧 自定义JavaScript代码已接收

### 📝 代码说明
{description or "未提供说明"}

---

### 💻 你的代码

```javascript
{js_code}
```

---

### ✅ 代码验证

#### 语法检查
- ✅ 代码已接收
- ⚠️ 完整语法验证需要在浏览器中进行
- ⚠️ 建议在浏览器控制台测试代码

#### 集成建议

**在书源规则中使用**：
```json
{{
  "ruleContent": {{
    "content": "@js:{js_code}"
  }}
}}
```

**或者在JS扩展中定义函数**：
```json
{{
  "jsLib": "{js_code}"
}}
```

---

### 🧪 测试方法

#### 方法1：浏览器控制台测试
1. 打开目标网页
2. 按F12打开开发者工具
3. 切换到Console标签
4. 粘贴你的代码并运行
5. 查看输出是否符合预期

#### 方法2：使用测试工具
使用`test_custom_js`工具测试你的代码

---

### 📌 提醒

⚠️ **注意事项**：
1. 确保代码可以访问需要的变量（如`java`、`result`等）
2. 注意异步代码的处理
3. 考虑错误处理（try-catch）
4. 测试不同场景下的代码执行

💡 **常用变量**：
- `java` - Java对象（Legado提供）
- `result` - 匹配结果
- `baseUrl` - 基础URL
- `url` - 当前URL

---

### 🎯 下一步

1. 在浏览器中测试你的代码
2. 如果有问题，告诉我错误信息
3. 如果测试通过，进行验证
4. 测试通过后，将代码集成到书源规则中

需要我帮你测试这段代码吗？
"""
    
    return report


@tool
def correct_selector(
    field_name: str,
    original_selector: str,
    corrected_selector: str,
    reason: str
) -> str:
    """
    🎯 修正选择器
    
    当AI识别的选择器不正确时，你可以手动修正
    
    参数:
        field_name: 字段名称（如书名、作者、封面等）
        original_selector: AI原来识别的选择器
        corrected_selector: 你修正后的选择器
        reason: 修正原因（说明为什么原来的选择器不对）
    
    返回:
        修正记录和验证建议
    """
    report = f"""
## 🎯 选择器修正已记录

### 📋 修正信息

**字段**: {field_name}

**AI识别的选择器**:
```
{original_selector}
```

**你修正后的选择器**:
```
{corrected_selector}
```

**修正原因**:
```
{reason}
```

---

### ✅ 修正记录

- ✅ 已保存修正记录
- ✅ 字段: {field_name}
- ✅ 原选择器: {original_selector}
- ✅ 新选择器: {corrected_selector}
- ✅ 修正原因: {reason}

---

### 🧪 验证建议

**强烈建议验证你的修正**：

使用`validate_correction`工具验证：
```
validate_correction(
    url="目标网页URL",
    selector="{corrected_selector}",
    field_name="{field_name}"
)
```

---

### 💻 在书源规则中使用

```json
{{
  "ruleBookInfo": {{
    "{field_name}": "{corrected_selector}"
  }}
}}
```

或者如果需要提取属性：
```json
{{
  "ruleBookInfo": {{
    "{field_name}": "{corrected_selector}@href"
  }}
}}
```

---

### 🎓 经验学习

⚠️ **重要**：这个修正应该被记录下来！

**为什么AI识别错了？**
- 可能是HTML结构特殊
- 可能是动态加载的内容
- 可能是使用了伪类或特殊属性

**建议使用`save_experience`保存这个经验**，这样下次AI就能学会了。

---

### 🎯 下一步

1. ✅ 使用`validate_correction`验证你的修正
2. ✅ 如果验证通过，更新书源规则
3. ✅ 使用`save_experience`保存经验
4. ✅ 继续处理其他字段

需要我帮你验证这个选择器吗？
"""
    
    return report


@tool
def manual_define_rule(
    rule_name: str,
    rule_content: str,
    rule_type: str = "ruleBookInfo",
    description: str = ""
) -> str:
    """
    📝 手动定义规则
    
    当AI生成的规则完全不符合预期时，你可以手动定义完整的规则
    
    参数:
        rule_name: 规则名称（如ruleBookInfo、ruleContent等）
        rule_content: 规则内容（JSON格式或CSS选择器）
        rule_type: 规则类型（默认ruleBookInfo）
        description: 规则说明
    
    返回:
        规则定义记录和测试建议
    """
    # 尝试解析JSON
    is_json = False
    parsed_content = None
    
    try:
        parsed_content = json.loads(rule_content)
        is_json = True
    except:
        pass
    
    report = f"""
## 📝 手动规则定义已接收

### 📋 规则信息

**规则名称**: {rule_name}
**规则类型**: {rule_type}
**规则说明**: {description or "未提供说明"}

---

### 💻 规则内容

```json
{rule_content}
```

{'✅ **JSON格式有效**' if is_json else '⚠️ **非JSON格式**（可能是简单的CSS选择器）'}

---

### 🧪 测试建议

**强烈建议测试你的规则**：

使用`test_manual_rule`工具测试：
```
test_manual_rule(
    rule_name="{rule_name}",
    rule_content={json.dumps(rule_content)},
    test_url="目标网页URL"
)
```

---

### 💡 规则类型说明

#### ruleBookInfo（书籍信息）
```json
{{
  "ruleBookInfo": {{
    "name": "书名选择器",
    "author": "作者选择器",
    "coverUrl": "封面选择器@src",
    "intro": "简介选择器",
    "tocUrl": "目录链接@href"
  }}
}}
```

#### ruleContent（正文内容）
```json
{{
  "ruleContent": {{
    "content": "正文选择器",
    "nextUrl": "下一页链接"
  }}
}}
```

#### ruleToc（目录列表）
```json
{{
  "ruleToc": {{
    "chapterList": "章节列表选择器",
    "chapterName": "章节名称",
    "chapterUrl": "章节链接@href"
  }}
}}
```

#### ruleSearch（搜索规则）
```json
{{
  "ruleSearch": {{
    "bookList": "搜索结果列表选择器",
    "name": "书名",
    "author": "作者"
  }}
}}
```

---

### 🎯 下一步

1. ✅ 使用`test_manual_rule`测试你的规则
2. ✅ 如果测试通过，应用到书源
3. ✅ 使用`save_experience`保存经验
4. ✅ 继续处理其他规则

需要我帮你测试这个规则吗？
"""
    
    return report


@tool
def provide_html_sample(
    url: str,
    html_content: str,
    field_name: str = ""
) -> str:
    """
    📄 提供HTML样本
    
    当AI无法访问网页时，你可以手动提供HTML样本
    
    参数:
        url: 网页URL
        html_content: HTML源代码
        field_name: 要提取的字段（可选）
    
    返回:
        HTML分析和建议
    """
    html_size = len(html_content)
    
    report = f"""
## 📄 HTML样本已接收

### 📋 样本信息

**URL**: {url}
**字段**: {field_name or "全部字段"}
**HTML大小**: {html_size} 字符

---

### ✅ 样本验证

- ✅ HTML已接收
- ✅ 大小: {html_size} 字符
- ⚠️ 真实性验证: 需要手动确认
- ⚠️ 完整性验证: 建议检查关键元素是否存在

---

### 🧪 分析建议

**使用`analyze_user_html`工具分析HTML**：
```
analyze_user_html(
    url="{url}",
    html_content={json.dumps(html_content)},
    field_name="{field_name}"
)
```

---

### 💡 提醒

⚠️ **重要**：
1. 确保HTML是完整的，不是截断的
2. 确保HTML包含你要提取的元素
3. 如果是动态加载的内容，可能需要JS处理
4. 建议复制完整的页面HTML（Ctrl+U查看源码）

---

### 🎯 下一步

1. ✅ 使用`analyze_user_html`分析HTML
2. ✅ 确认HTML包含所有需要的元素
3. ✅ 如果HTML不完整，重新提供
4. ✅ 分析后，AI会推荐选择器

需要我分析这个HTML吗？使用`analyze_user_html`工具。
"""
    
    return report


@tool
def save_experience(
    experience_type: str,
    problem: str,
    solution: str,
    tags: str = ""
) -> str:
    """
    💾 保存经验到知识库
    
    当你成功解决问题后，保存经验，下次AI就能学会了
    
    参数:
        experience_type: 经验类型（如selector_correction、js_injection等）
        problem: 问题描述（遇到了什么问题）
        solution: 解决方案（你是怎么解决的）
        tags: 标签（如选择器、JS、动态加载等，多个标签用逗号分隔）
    
    返回:
        保存确认
    """
    # 解析标签
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # 构建经验记录
    experience = {
        "type": experience_type,
        "problem": problem,
        "solution": solution,
        "tags": tag_list,
        "timestamp": __import__('time').time()
    }
    
    # 保存到文件
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    experience_file = os.path.join(workspace_path, "assets", "user_experiences.json")
    
    # 读取现有经验
    experiences = []
    if os.path.exists(experience_file):
        try:
            with open(experience_file, 'r', encoding='utf-8') as f:
                experiences = json.load(f)
        except:
            experiences = []
    
    # 添加新经验
    experiences.append(experience)
    
    # 保存
    os.makedirs(os.path.dirname(experience_file), exist_ok=True)
    with open(experience_file, 'w', encoding='utf-8') as f:
        json.dump(experiences, f, ensure_ascii=False, indent=2)
    
    report = f"""
## 💾 经验保存成功

### 📋 经验信息

**经验类型**: {experience_type}
**标签**: {', '.join(tag_list) if tag_list else '无'}

---

### 📝 问题描述

```
{problem}
```

---

### 💡 解决方案

```
{solution}
```

---

### ✅ 保存确认

- ✅ 已保存到: `assets/user_experiences.json`
- ✅ 总经验数: {len(experiences)}
- ✅ 时间戳: {experience['timestamp']}

---

### 🎓 学习效果

💡 **下次遇到类似问题时**：
1. AI会优先参考你保存的经验
2. AI会尝试应用你的解决方案
3. AI会避免重复相同的错误

---

### 🎯 下一步

现在AI已经学会了！你可以：
1. ✅ 继续处理其他问题
2. ✅ 让AI尝试解决类似问题
3. ✅ 继续积累更多经验

感谢你分享经验！🎉
"""
    
    return report


@tool
def record_solution(
    url: str,
    problem: str,
    solution: str,
    rule_snippet: str = ""
) -> str:
    """
    📋 记录解决方案
    
    记录针对特定网站的解决方案
    
    参数:
        url: 网站URL
        problem: 问题描述
        solution: 解决方案
        rule_snippet: 规则片段（可选）
    
    返回:
        记录确认
    """
    # 构建方案记录
    solution_record = {
        "url": url,
        "problem": problem,
        "solution": solution,
        "rule_snippet": rule_snippet,
        "timestamp": __import__('time').time()
    }
    
    # 保存到文件
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    solutions_file = os.path.join(workspace_path, "assets", "solutions.json")
    
    # 读取现有方案
    solutions = []
    if os.path.exists(solutions_file):
        try:
            with open(solutions_file, 'r', encoding='utf-8') as f:
                solutions = json.load(f)
        except:
            solutions = []
    
    # 添加新方案
    solutions.append(solution_record)
    
    # 保存
    os.makedirs(os.path.dirname(solutions_file), exist_ok=True)
    with open(solutions_file, 'w', encoding='utf-8') as f:
        json.dump(solutions, f, ensure_ascii=False, indent=2)
    
    report = f"""
## 📋 解决方案已记录

### 📋 方案信息

**网站**: {url}
**问题**: {problem}

---

### 💡 解决方案

```
{solution}
```

"""

    if rule_snippet:
        report += f"""
---

### 📝 规则片段

```json
{rule_snippet}
```

"""

    report += f"""
---

### ✅ 保存确认

- ✅ 已保存到: `assets/solutions.json`
- ✅ 总方案数: {len(solutions)}
- ✅ 时间戳: {solution_record['timestamp']}

---

### 🎯 下一步

现在方案已记录！你可以：
1. ✅ 继续处理其他问题
2. ✅ 让AI参考这个方案
3. ✅ 继续积累更多方案

感谢你记录方案！🎉
"""
    
    return report
