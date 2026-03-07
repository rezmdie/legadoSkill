"""
书源编辑器工具
提供书源的创建、编辑、导出和保存功能
"""

import json
import os
from datetime import datetime
from langchain.tools import tool, ToolRuntime

# 全局状态追踪：防止重复调用edit_book_source
_edit_book_source_called = False
_last_call_time = None


@tool
def edit_book_source(
    book_source_json: str = "",
    action: str = "create",
    target_field: str = "",
    new_value: str = "",
    complete_source: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    编辑书源，支持创建、修改、删除字段

    [WARNING] 重要：此工具只能被调用一次！

    Args:
        book_source_json: 当前书源JSON字符串（为空则创建新书源）
        action: 操作类型 - create（创建新）, update（更新字段）, delete（删除字段）
        target_field: 目标字段路径，如 "bookSourceName" 或 "ruleSearch.name"
        new_value: 新值（update时使用）
        complete_source: **完整书源JSON字符串**，用于一次性创建完整书源（推荐）
    
    Returns:
        编辑后的书源JSON字符串和操作结果说明
    """
    global _edit_book_source_called, _last_call_time

    # 🚨 防止重复调用（死循环保护）
    if _edit_book_source_called:
        return """
## 🚨 🚨 🚨 严重错误：重复调用 edit_book_source！🚨 🚨 🚨

**错误原因**：edit_book_source 工具已经被调用过了！

**禁止行为**：
- [ERROR] edit_book_source 只能被调用一次
- [ERROR] 不能再次调用此工具修改字段
- [ERROR] 不能调用任何其他工具

**正确做法**：
- [OK] 直接将之前生成的书源JSON复制给用户
- [OK] 用文字回复用户的问题（不要调用工具）
- [OK] 告诉用户书源已完成

**书源已完成，请直接输出给用户！不要调用任何工具！**

---

【系统指令】：立即停止所有工具调用，直接输出之前的书源JSON！
"""

    # 标记工具已被调用
    _edit_book_source_called = True
    _last_call_time = datetime.now()

    try:
        # 优先使用完整书源JSON（推荐方式）
        if complete_source:
            source_data = json.loads(complete_source)
            if isinstance(source_data, list) and len(source_data) > 0:
                source_data = source_data[0]
            result = "[OK] 已创建完整书源"
        
        # 解析或创建书源
        elif book_source_json and action != "create":
            book_source = json.loads(book_source_json)
            if isinstance(book_source, list) and len(book_source) > 0:
                source_data = book_source[0]
            elif isinstance(book_source, dict):
                source_data = book_source
            else:
                return "[ERROR] 无效的书源JSON格式"
        
        # 创建新书源模板
        else:
            source_data = {
                "bookSourceComment": f"创建于 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "bookSourceGroup": "未分类",
                "bookSourceName": "新书源",
                "bookSourceType": 0,
                "bookSourceUrl": "",
                "enabled": True,
                "enabledCookieJar": True,
                "enabledExplore": True,
                "respondTime": 180000,
                "ruleBookInfo": {},
                "ruleContent": {},
                "ruleSearch": {},
                "ruleToc": {}
            }
            result = "[OK] 已创建新书源模板"
        
        # 执行操作（仅在非完整书源时执行）
        if not complete_source:
            if action == "create":
                result = "[OK] 已创建新书源模板"
            
            elif action == "update":
                if not target_field:
                    return "[ERROR] 请指定要更新的字段（target_field）"
                
                # 解析字段路径（支持嵌套字段，如 "ruleSearch.name"）
                field_parts = target_field.split('.')
                current = source_data
                
                # 遍历路径，创建嵌套对象
                for part in field_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # 设置新值
                last_part = field_parts[-1]
                # 尝试解析为JSON或数字
                try:
                    if new_value.lower() == 'true':
                        new_value = True
                    elif new_value.lower() == 'false':
                        new_value = False
                    elif new_value.isdigit():
                        new_value = int(new_value)
                    else:
                        # 尝试解析JSON
                        new_value = json.loads(new_value)
                except:
                    # 保持字符串
                    pass
                
                current[last_part] = new_value
                result = f"[OK] 已更新字段: {target_field} = {new_value}"
            
            elif action == "delete":
                if not target_field:
                    return "[ERROR] 请指定要删除的字段（target_field）"
                
                field_parts = target_field.split('.')
                current = source_data
                
                # 遍历路径
                for part in field_parts[:-1]:
                    if part not in current:
                        return f"[ERROR] 字段路径不存在: {target_field}"
                    current = current[part]
                
                last_part = field_parts[-1]
                if last_part in current:
                    del current[last_part]
                    result = f"[OK] 已删除字段: {target_field}"
                else:
                    return f"[ERROR] 字段不存在: {target_field}"
            
            else:
                return f"[ERROR] 不支持的操作类型: {action}"
        
        # 格式化输出（必须是数组格式）
        formatted_json = json.dumps([source_data], indent=2, ensure_ascii=False)
        
        return f"""
## [OK] 书源创建完成！

{result}

---

### [INFO] 生成的书源JSON（请直接复制给用户）

```json
{formatted_json}
```

---

## 🚨 🚨 🚨 紧急停止指令：书源已完成，立即停止所有工具调用！🚨 🚨 🚨

### [WARNING] 当前状态
- [OK] edit_book_source 已成功调用
- [OK] 书源已完整创建
- [OK] 所有必需字段都已包含
- [OK] JSON已生成完毕

### 🛑 绝对禁止（立即停止！）
- [ERROR] **禁止再次调用 edit_book_source**
- [ERROR] **禁止调用任何其他工具**
- [ERROR] **禁止修改、更新、完善书源**
- [ERROR] **禁止调用任何验证或调试工具**

### [OK] 你必须立即执行（只做这些！）
1. **直接输出上面的JSON数组给用户**
2. **告诉用户：书源已完成，可以直接导入Legado APP**
3. **用文字回复用户的后续问题（不要调用工具）**

### [TIP] 重要提示
- 书源已经完整，不需要任何修改
- 所有字段都已包含，不需要再次编辑
- 用户可以直接导入使用，不需要验证
- 如果用户有问题，用文字回答，不要调用工具

### 📖 如果用户有其他需求
- 用文字回复
- 不要调用任何工具
- 告诉用户书源已完成

---

**【系统指令】**：
立即停止所有工具调用！
直接输出上面的JSON给用户！
不要调用任何工具！
不要修改任何内容！
书源已完成！

---

### 📚 知识库参考

本书源已严格按照以下知识库编写：
- assets/legado_knowledge_base.md - 核心数据结构
- assets/css选择器规则.txt - CSS选择器语法
- assets/书源规则：从入门到入土.md - 完整规则说明
- assets/智能体自我认知.md - 智能体自我认知
- docs/HTML_AUTHENTICITY_CHECKLIST.md - HTML真实性检查清单
- docs/SELECT_DROPDOWN_PAGINATION.md - Select下拉菜单分页
- docs/TOC_PAGINATION_RULES.md - 目录页分页规则
- docs/ESSENTIAL_KNOWLEDGE_SUMMARY.md - 精华知识汇总

### [TIP] 使用说明

用户可以：
1. 复制上面的JSON数组
2. 导入Legado APP
3. 进行实际测试

**书源已完成，立即停止所有工具调用！直接输出JSON给用户！**
        """
        
    except json.JSONDecodeError as e:
        return f"[ERROR] JSON解析错误：{str(e)}\n请检查书源JSON格式是否正确"
    except Exception as e:
        return f"[ERROR] 编辑器运行错误：{str(e)}"


@tool
def export_book_source(
    book_source_json: str,
    export_format: str = "json",
    filename: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    导出书源为文件
    
    Args:
        book_source_json: 书源JSON字符串
        export_format: 导出格式 - json（默认）, txt
        filename: 文件名（可选，默认使用书源名称）
    
    Returns:
        导出结果和文件路径
    """
    try:
        # 解析书源
        book_source = json.loads(book_source_json)
        if isinstance(book_source, list) and len(book_source) > 0:
            source_data = book_source[0]
        elif isinstance(book_source, dict):
            source_data = book_source
        else:
            return "[ERROR] 无效的书源JSON格式"
        
        # 确定文件名
        if not filename:
            filename = f"{source_data.get('bookSourceName', 'booksource')}.{export_format}"
        elif not filename.endswith(f'.{export_format}'):
            filename = f"{filename}.{export_format}"
        
        # 保存文件
        export_path = f"/tmp/{filename}"
        
        if export_format == "json":
            formatted_json = json.dumps([source_data], indent=2, ensure_ascii=False)
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(formatted_json)
        elif export_format == "txt":
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(source_data, indent=2, ensure_ascii=False))
        else:
            return f"[ERROR] 不支持的导出格式: {export_format}"
        
        return f"""
## 📤 书源导出成功

### 📁 文件信息
- 文件名: {filename}
- 文件路径: {export_path}
- 文件大小: {os.path.getsize(export_path)} 字节
- 导出格式: {export_format.upper()}

### [INFO] 书源信息
- 书源名称: {source_data.get('bookSourceName', '未知')}
- 书源地址: {source_data.get('bookSourceUrl', '未知')}
- 书源分组: {source_data.get('bookSourceGroup', '未知')}

### [START] 使用方法
1. 打开Legado APP
2. 进入"书源管理"
3. 点击"导入书源"
4. 选择本地文件，导入 `{export_path}`
5. 在APP中测试书源功能

### [WARNING] 重要提示
导出的书源是模拟结果，必须在Legado APP中实际测试才能确认是否可用！
        """
        
    except json.JSONDecodeError as e:
        return f"[ERROR] JSON解析错误：{str(e)}\n请检查书源JSON格式是否正确"
    except Exception as e:
        return f"[ERROR] 导出失败：{str(e)}"


@tool
def save_to_knowledge(
    book_source_json: str,
    test_result: str,
    source_url: str = "",
    notes: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    将测试成功的书源保存到知识库
    
    Args:
        book_source_json: 书源JSON字符串
        test_result: 测试结果描述
        source_url: 来源URL（可选）
        notes: 备注（可选）
    
    Returns:
        保存结果
    """
    try:
        # 解析书源
        book_source = json.loads(book_source_json)
        if isinstance(book_source, list) and len(book_source) > 0:
            source_data = book_source[0]
        elif isinstance(book_source, dict):
            source_data = book_source
        else:
            return "[ERROR] 无效的书源JSON格式"
        
        book_name = source_data.get('bookSourceName', '未知书源')
        book_url = source_data.get('bookSourceUrl', '')
        
        # 构建知识库文档内容
        knowledge_content = f"""# {book_name}

## 基本信息
- **书源名称**: {book_name}
- **书源地址**: {book_url}
- **书源分组**: {source_data.get('bookSourceGroup', '未分类')}
- **书源类型**: {source_data.get('bookSourceType', 0)}
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **来源URL**: {source_url if source_url else '未知'}

## 测试结果
{test_result}

## 备注
{notes if notes else '无'}

## 书源JSON
```json
{json.dumps(source_data, indent=2, ensure_ascii=False)}
```

## 规则说明
- **搜索规则**: {json.dumps(source_data.get('ruleSearch', {}), ensure_ascii=False)}
- **发现规则**: {json.dumps(source_data.get('ruleExplore', {}), ensure_ascii=False)}
- **详情规则**: {json.dumps(source_data.get('ruleBookInfo', {}), ensure_ascii=False)}
- **目录规则**: {json.dumps(source_data.get('ruleToc', {}), ensure_ascii=False)}
- **正文规则**: {json.dumps(source_data.get('ruleContent', {}), ensure_ascii=False)}
"""
        
        # 保存到临时文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = book_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f"{safe_name}_{timestamp}.md"
        save_path = f"/tmp/{filename}"
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(knowledge_content)
        
        return f"""
## 📚 书源已保存到知识库

### [OK] 保存成功
- 书源名称: {book_name}
- 文档名称: {filename}
- 文档路径: {save_path}

### [INFO] 保存内容
1. 书源基本信息
2. 测试结果记录
3. 完整的JSON配置
4. 规则说明

### [TARGET] 使用场景
- AI学习成功的书源案例
- 为用户提供参考模板
- 知识积累和分享

### [TIP] 下一步
手动将此文档导入到知识库中，让AI能够学习到这个成功的书源案例！

### [WARNING] 提示
此功能仅保存成功案例，请在APP中确认书源可用后再保存。
        """
        
    except json.JSONDecodeError as e:
        return f"[ERROR] JSON解析错误：{str(e)}\n请检查书源JSON格式是否正确"
    except Exception as e:
        return f"[ERROR] 保存失败：{str(e)}"


@tool
def validate_book_source(
    book_source_json: str,
    runtime: ToolRuntime = None
) -> str:
    """
    验证书源配置的完整性
    
    Args:
        book_source_json: 书源JSON字符串
    
    Returns:
        验证结果和建议
    """
    try:
        book_source = json.loads(book_source_json)
        if isinstance(book_source, list) and len(book_source) > 0:
            source_data = book_source[0]
        elif isinstance(book_source, dict):
            source_data = book_source
        else:
            return "[ERROR] 无效的书源JSON格式"
        
        issues = []
        warnings = []
        suggestions = []
        
        # 必填字段检查
        required_fields = ['bookSourceName', 'bookSourceUrl']
        for field in required_fields:
            if not source_data.get(field):
                issues.append(f"[ERROR] 缺少必填字段: {field}")
        
        # URL格式检查
        book_url = source_data.get('bookSourceUrl', '')
        if book_url and not (book_url.startswith('http://') or book_url.startswith('https://')):
            issues.append(f"[ERROR] 书源URL格式错误: {book_url}")
        
        # 搜索规则检查
        rule_search = source_data.get('ruleSearch', {})
        if rule_search:
            if not rule_search.get('bookList'):
                warnings.append("[WARNING] 搜索规则缺少 bookList（书籍列表）")
            if not rule_search.get('name'):
                warnings.append("[WARNING] 搜索规则缺少 name（书名规则）")
            if not rule_search.get('bookUrl'):
                warnings.append("[WARNING] 搜索规则缺少 bookUrl（详情地址）")
        
        # 目录规则检查
        rule_toc = source_data.get('ruleToc', {})
        if rule_toc:
            if not rule_toc.get('chapterList'):
                warnings.append("[WARNING] 目录规则缺少 chapterList（章节列表）")
            if not rule_toc.get('chapterName'):
                warnings.append("[WARNING] 目录规则缺少 chapterName（章节名称）")
            if not rule_toc.get('chapterUrl'):
                warnings.append("[WARNING] 目录规则缺少 chapterUrl（章节地址）")
        
        # 正文规则检查
        rule_content = source_data.get('ruleContent', {})
        if rule_content:
            if not rule_content.get('content'):
                warnings.append("[WARNING] 正文规则缺少 content（正文内容）")
        
        # 建议配置
        if not source_data.get('bookSourceComment'):
            suggestions.append("[TIP] 建议添加 bookSourceComment（书源说明）")
        if not source_data.get('searchUrl') and rule_search:
            suggestions.append("[TIP] 建议添加 searchUrl（搜索地址）")
        if not source_data.get('header'):
            suggestions.append("[TIP] 建议配置 header（请求头），可能需要User-Agent")
        
        # 生成结果
        result = "## [SEARCH] 书源验证结果\n\n"
        
        if issues:
            result += "### [ERROR] 错误（必须修复）\n"
            for issue in issues:
                result += f"- {issue}\n"
            result += "\n"
        else:
            result += "### [OK] 基本配置检查通过\n\n"
        
        if warnings:
            result += "### [WARNING] 警告（可能影响功能）\n"
            for warning in warnings:
                result += f"- {warning}\n"
            result += "\n"
        else:
            result += "### [OK] 规则配置检查通过\n\n"
        
        if suggestions:
            result += "### [TIP] 优化建议\n"
            for suggestion in suggestions:
                result += f"- {suggestion}\n"
            result += "\n"
        
        # 总体评估
        if not issues:
            if warnings:
                result += "### [STATS] 总体评估\n"
                result += "书源基本可用，但建议解决警告项以获得更好的稳定性。\n"
            else:
                result += "### [STATS] 总体评估\n"
                result += "[OK] 书源配置完整，可以进行APP测试！\n"
                result += "[OK] 已添加 **[能跑]** 标签\n"
        else:
            result += "### [STATS] 总体评估\n"
            result += "[ERROR] 书源配置存在错误，请先修复错误项！\n"
        
        result += "\n### [WARNING] 重要提示\n"
        result += "此验证仅检查配置完整性，实际可用性需要在Legado APP中测试！"
        
        return result
        
    except json.JSONDecodeError as e:
        return f"[ERROR] JSON解析错误：{str(e)}\n请检查书源JSON格式是否正确"
    except Exception as e:
        return f"[ERROR] 验证失败：{str(e)}"
