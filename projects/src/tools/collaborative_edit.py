"""
协同编辑和验证工具
让用户可以查看AI的推理，并提供修正和验证
"""

import json
from typing import Dict, List, Any, Optional
from langchain.tools import tool
from bs4 import BeautifulSoup


@tool
def validate_correction(
    url: str,
    selector: str,
    field_name: str
) -> str:
    """
    ✅ 验证用户修正的选择器
    
    在真实网页上验证用户修正的选择器是否正确
    
    参数:
        url: 目标网页URL
        selector: 用户修正后的选择器
        field_name: 字段名称
    
    返回:
        验证结果报告
    """
    try:
        from utils.smart_request import smart_request
        
        # 获取真实HTML
        print(f"🌐 正在访问真实网页验证修正: {url}")
        response = smart_request(url)
        
        if not response or not response.get('success'):
            raise Exception(f"获取真实网页失败: {response.get('error', 'Unknown error') if response else 'No response'}")
        
        html = response['content']
        print(f"✅ 成功获取真实HTML，大小: {len(html)} 字符")
        
        # 验证选择器
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.select(selector)
        
        valid = len(elements) > 0
        
        # 构建报告
        report = f"""
## ✅ 选择器修正验证报告

### 📋 验证信息

**字段**: {field_name}
**选择器**: `{selector}`
**网页**: {url}

---

### 🔬 验证结果

**状态**: {'✅ 有效' if valid else '❌ 无效'}

**匹配数量**: {len(elements)} 个元素

**消息**: {'选择器有效，可以提取到内容' if valid else '选择器无效，未提取到任何内容'}

---

### 📋 提取的内容样本

"""
        
        if elements:
            for i, elem in enumerate(elements[:10], 1):
                text = elem.get_text(strip=True)[:100]
                tag = elem.name
                classes = ' '.join(elem.get('class', []))
                report += f"""
**样本 {i}**:
- **文本**: {text}
- **标签**: {tag}
- **类名**: {classes}
"""
        else:
            report += "❌ 未提取到任何内容\n"
        
        # 建议
        report += f"""

---

### 💡 验证结论

"""

        if valid:
            report += f"""
🎉 **恭喜！你的修正是正确的！**

✅ 选择器有效
✅ 可以提取到内容
✅ 可以应用到书源规则中

**建议**:
1. ✅ 继续验证其他字段
2. ✅ 更新书源规则
3. ✅ 保存经验
"""
        else:
            report += f"""
⚠️ **修正可能有问题**

❌ 选择器无效
❌ 未提取到内容
❌ 需要进一步修正

**可能的问题**:
1. 选择器语法错误
2. 选择器与网页结构不匹配
3. 页面结构可能已变化

**建议**:
1. 在浏览器开发者工具中检查元素
2. 使用更简单的选择器测试
3. 检查页面是否动态加载
"""
        
        report += f"""

---

### 🔒 真实性保证

- ✅ 已访问真实网页
- ✅ HTML来源：真实网页源代码
- ✅ 选择器已在真实HTML上验证
- ✅ 禁止任何Mock或示例

---

### 🎯 下一步

"""
        
        if valid:
            report += f"""
1. ✅ 如果还有其他字段需要修正，继续验证
2. ✅ 如果所有字段都正确，更新书源规则
3. ✅ 保存这次成功的修正经验
"""
        else:
            report += f"""
1. 🔍 重新检查选择器
2. 🔍 使用浏览器开发者工具查看元素
3. 🔍 再次修正选择器
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 验证失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```

### 💡 建议

1. 检查URL是否正确且可访问
2. 检查选择器语法是否正确
3. 在浏览器中打开URL，使用开发者工具测试选择器
"""


@tool
def test_manual_rule(
    rule_name: str,
    rule_content: str,
    test_url: str
) -> str:
    """
    🧪 测试手动定义的规则
    
    在真实网页上测试手动定义的规则
    
    参数:
        rule_name: 规则名称
        rule_content: 规则内容（JSON格式）
        test_url: 测试网页URL
    
    返回:
        测试结果报告
    """
    try:
        # 解析规则
        try:
            rule_data = json.loads(rule_content)
        except:
            return "❌ 规则格式错误，必须是有效的JSON格式"
        
        from utils.smart_request import smart_request
        
        # 获取真实HTML
        print(f"🌐 正在访问真实网页测试规则: {test_url}")
        response = smart_request(test_url)
        
        if not response or not response.get('success'):
            raise Exception(f"获取真实网页失败: {response.get('error', 'Unknown error') if response else 'No response'}")
        
        html = response['content']
        print(f"✅ 成功获取真实HTML，大小: {len(html)} 字符")
        
        # 测试规则中的每个选择器
        soup = BeautifulSoup(html, 'html.parser')
        
        report = f"""
## 🧪 手动规则测试报告

### 📋 规则信息

**规则名称**: {rule_name}
**测试网页**: {test_url}

---

### 🔬 测试结果

#### 规则内容

```json
{json.dumps(rule_data, ensure_ascii=False, indent=2)}
```

---

#### 选择器测试

"""
        
        test_count = 0
        success_count = 0
        
        for field, selector in rule_data.items():
            test_count += 1
            
            # 解析选择器（处理 @text, @href 等后缀）
            clean_selector = selector
            extract_attr = None
            
            if '@' in selector:
                parts = selector.split('@')
                clean_selector = parts[0]
                extract_attr = parts[1]
            
            # 测试选择器
            try:
                elements = soup.select(clean_selector)
                is_valid = len(elements) > 0
                
                if is_valid:
                    success_count += 1
                
                # 提取样本
                samples = []
                for elem in elements[:3]:
                    if extract_attr:
                        value = elem.get(extract_attr, '')
                    else:
                        value = elem.get_text(strip=True)
                    samples.append(value[:50])
                
                status = '✅' if is_valid else '❌'
                
                report += f"""
**{field}** {status}
- **选择器**: `{clean_selector}`
- **提取属性**: `{extract_attr or 'text'}`
- **匹配数量**: {len(elements)}
- **样本**: {', '.join(samples) if samples else '无'}
- **状态**: {'有效' if is_valid else '无效'}

"""
            except Exception as e:
                report += f"""
**{field}** ❌
- **选择器**: `{clean_selector}`
- **错误**: {str(e)}

"""
        
        # 总体结论
        report += f"""
---

### 📊 总体结论

**测试项数**: {test_count}
**成功项数**: {success_count}
**失败项数**: {test_count - success_count}
**成功率**: {(success_count / test_count * 100) if test_count > 0 else 0:.1f}%

"""

        if success_count == test_count:
            report += """
🎉 **恭喜！规则完全正确！**

✅ 所有选择器都有效
✅ 所有字段都能正常提取
✅ 可以应用到书源中

**建议**:
1. ✅ 将规则应用到书源配置
2. ✅ 保存经验
3. ✅ 继续处理其他规则
"""
        elif success_count > 0:
            report += f"""
⚠️ **规则部分正确**

✅ {success_count} 个字段正确
❌ {test_count - success_count} 个字段有问题

**建议**:
1. 修正无效的选择器
2. 重新测试
"""
        else:
            report += """
❌ **规则完全无效**

所有选择器都无法正常工作

**建议**:
1. 检查网页URL是否正确
2. 使用浏览器开发者工具查看HTML结构
3. 重新定义选择器
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 测试失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```

### 💡 建议

1. 检查URL是否正确且可访问
2. 检查规则格式是否正确
3. 检查选择器语法是否正确
"""


@tool
def analyze_user_html(
    url: str,
    html_content: str,
    field_name: str = ""
) -> str:
    """
    🔍 分析用户提供的HTML
    
    分析用户提供的HTML样本，推荐选择器
    
    参数:
        url: 网页URL
        html_content: HTML内容
        field_name: 要提取的字段（可选）
    
    返回:
        HTML分析报告
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        report = f"""
## 🔍 用户HTML分析报告

### 📋 分析信息

**URL**: {url}
**字段**: {field_name or "全部字段"}
**HTML大小**: {len(html_content)} 字符

---

### 🔬 HTML结构分析

#### 页面基本信息
- **标签数量**: {len(soup.find_all())}
- **链接数量**: {len(soup.find_all('a'))}
- **图片数量**: {len(soup.find_all('img'))}
- **标题数量**: {len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))}

---

#### 推荐的常见元素

**可能的标题（h1-h6）**:
"""
        
        # 查找标题
        for i, title in enumerate(soup.find_all(['h1', 'h2', 'h3'])[:5], 1):
            text = title.get_text(strip=True)
            tag = title.name
            classes = ' '.join(title.get('class', []))
            selector = f"{tag}{'.' + classes if classes else ''}"
            
            report += f"""
{i}. `{selector}` 
   - **文本**: {text}
   - **标签**: {tag}
   - **类名**: {classes}
"""
        
        report += f"""

**可能的链接（a标签）**:
"""
        
        # 查找链接
        for i, link in enumerate(soup.find_all('a', href=True)[:5], 1):
            text = link.get_text(strip=True)
            href = link['href']
            classes = ' '.join(link.get('class', []))
            selector = f"a[href]{'.' + classes if classes else ''}"
            
            report += f"""
{i}. `{selector}@href`
   - **文本**: {text}
   - **链接**: {href}
   - **类名**: {classes}
"""
        
        report += f"""

**可能的图片（img标签）**:
"""
        
        # 查找图片
        for i, img in enumerate(soup.find_all('img', src=True)[:5], 1):
            src = img['src']
            alt = img.get('alt', '')
            classes = ' '.join(img.get('class', []))
            selector = f"img[src]{'.' + classes if classes else ''}"
            
            report += f"""
{i}. `{selector}@src`
   - **源**: {src}
   - **Alt**: {alt}
   - **类名**: {classes}
"""
        
        # 根据字段给出建议
        if field_name:
            report += f"""

---

### 💡 针对【{field_name}】的建议

"""
            
            if field_name in ['书名', 'name', 'title']:
                report += f"""
建议使用 h1, h2 或 .title, .book-name 等选择器
"""
            elif field_name in ['作者', 'author']:
                report += f"""
建议使用 .author, .writer 或包含"作者"文本的元素
"""
            elif field_name in ['封面', 'cover', 'image']:
                report += f"""
建议使用 img[src] 选择器
"""
            elif field_name in ['简介', 'intro', 'description']:
                report += f"""
建议使用 .intro, .description 或 p, div 等容器
"""
            elif field_name in ['链接', 'link', 'url']:
                report += f"""
建议使用 a[href] 选择器
"""
        
        report += f"""

---

### ⚠️ 注意事项

1. **HTML样本可能不完整**
   - 确保你提供了完整的HTML源代码
   - 建议使用浏览器的"查看源代码"功能获取完整HTML

2. **动态内容可能缺失**
   - 如果内容是JS动态生成的，HTML样本可能不包含

3. **选择器需要验证**
   - 推荐的选择器需要在实际网页上验证
   - 使用`validate_correction`工具验证

---

### 🎯 下一步

1. ✅ 查看推荐的选择器
2. ✅ 如果满意，使用`validate_correction`验证
3. ✅ 如果不满意，手动修正选择器
4. ✅ 如果HTML不完整，重新提供

需要我帮你测试这些选择器吗？
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 分析失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```

### 💡 建议

1. 检查HTML内容是否完整
2. 检查HTML格式是否正确
3. 确保不是截断的HTML
"""
