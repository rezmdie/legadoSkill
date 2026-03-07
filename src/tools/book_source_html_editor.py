"""
书源HTML编辑器工具
生成可视化HTML编辑器，让用户可以在浏览器中编辑书源
"""

import json
import os
from langchain.tools import tool, ToolRuntime


def _escape_json_for_html(value):
    """将JSON值转换为HTML-safe的字符串"""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).replace('"', '&quot;')


def _build_html_template(source_data):
    """构建HTML模板"""
    
    # 获取字段值
    get_val = lambda path, default="": _escape_json_for_html(
        source_data.get(path, default) if '.' not in path else 
        source_data.get(path.split('.')[0], {}).get(path.split('.')[1], default)
    )
    
    # 构建HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legado书源可视化编辑器</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            overflow-x: auto;
        }}
        .tab {{
            padding: 15px 25px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 14px;
            font-weight: 500;
            color: #495057;
            white-space: nowrap;
            transition: all 0.3s;
        }}
        .tab:hover {{ background: #e9ecef; }}
        .tab.active {{ color: #667eea; border-bottom: 2px solid #667eea; background: white; }}
        .tab-content {{ padding: 30px; display: none; }}
        .tab-content.active {{ display: block; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #495057;
            font-size: 14px;
        }}
        .form-group input,
        .form-group textarea,
        .form-group select {{
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        .form-group textarea {{ min-height: 100px; resize: vertical; font-family: 'Courier New', monospace; }}
        .form-row {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        .form-row-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #343a40;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        .button-group {{ display: flex; gap: 10px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }}
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn-secondary:hover {{ background: #5a6268; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-success:hover {{ background: #218838; }}
        .checkbox-group {{ display: flex; align-items: center; gap: 10px; }}
        .checkbox-group input[type="checkbox"] {{ width: auto; }}
        .preview-box {{ background: #f8f9fa; padding: 20px; border-radius: 6px; margin-top: 20px; }}
        .preview-box h4 {{ margin-bottom: 15px; color: #495057; }}
        .preview-content {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .json-output {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 600px;
            overflow-y: auto;
        }}
        .json-output .string {{ color: #ce9178; }}
        .json-output .number {{ color: #b5cea8; }}
        .json-output .boolean {{ color: #569cd6; }}
        .json-output .null {{ color: #569cd6; }}
        .json-output .key {{ color: #9cdcfe; }}
        .tip {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #0d47a1;
        }}
        .tip.warning {{ background: #fff3cd; border-left-color: #ffc107; color: #856404; }}
        @media (max-width: 768px) {{
            .form-row, .form-row-3 {{ grid-template-columns: 1fr; }}
            .tabs {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Legado书源可视化编辑器</h1>
            <p>在浏览器中编辑书源，一键导出完整JSON格式</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" data-tab="basic">基础信息</button>
            <button class="tab" data-tab="search">搜索规则</button>
            <button class="tab" data-tab="explore">发现规则</button>
            <button class="tab" data-tab="bookinfo">书籍信息</button>
            <button class="tab" data-tab="toc">目录规则</button>
            <button class="tab" data-tab="content">正文规则</button>
            <button class="tab" data-tab="advanced">高级设置</button>
            <button class="tab" data-tab="export">导出预览</button>
        </div>
        
        <!-- 基础信息 -->
        <div class="tab-content active" id="tab-basic">
            <div class="tip">
                💡 <strong>提示：</strong>基础信息是书源的必填项，请确保填写完整。
            </div>
            
            <div class="section-title">📝 书源基本信息</div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="bookSourceName">书源名称 *</label>
                    <input type="text" id="bookSourceName" value="{get_val('bookSourceName', '')}" placeholder="例如：起点中文网">
                </div>
                
                <div class="form-group">
                    <label for="bookSourceGroup">分组</label>
                    <input type="text" id="bookSourceGroup" value="{get_val('bookSourceGroup', '小说')}" placeholder="例如：小说、漫画">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="bookSourceUrl">书源URL *</label>
                    <input type="url" id="bookSourceUrl" value="{get_val('bookSourceUrl', '')}" placeholder="https://example.com">
                </div>
                
                <div class="form-group">
                    <label for="bookSourceType">书源类型</label>
                    <select id="bookSourceType">
                        <option value="0" {"selected" if str(source_data.get('bookSourceType', 0)) == "0" else ""}>文字</option>
                        <option value="1" {"selected" if str(source_data.get('bookSourceType', 0)) == "1" else ""}>音频</option>
                        <option value="2" {"selected" if str(source_data.get('bookSourceType', 0)) == "2" else ""}>图片</option>
                        <option value="3" {"selected" if str(source_data.get('bookSourceType', 0)) == "3" else ""}>漫画</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label for="bookSourceComment">书源注释</label>
                <textarea id="bookSourceComment" placeholder="注释信息，包含作者、更新日期、功能说明等">{get_val('bookSourceComment', '')}</textarea>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="searchUrl">搜索URL</label>
                    <input type="text" id="searchUrl" value="{get_val('searchUrl', '')}" placeholder="https://example.com/search?q={{key}}">
                </div>
                
                <div class="form-group">
                    <label for="exploreUrl">发现URL</label>
                    <input type="text" id="exploreUrl" value="{get_val('exploreUrl', '')}" placeholder="发现页URL">
                </div>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="enabled" {"checked" if source_data.get('enabled', True) else ""}>
                <label for="enabled">启用书源</label>
                
                <input type="checkbox" id="enabledCookieJar" {"checked" if source_data.get('enabledCookieJar', True) else ""}>
                <label for="enabledCookieJar">启用Cookie</label>
                
                <input type="checkbox" id="enabledExplore" {"checked" if source_data.get('enabledExplore', True) else ""}>
                <label for="enabledExplore">启用发现</label>
            </div>
        </div>
        
        <!-- 搜索规则 -->
        <div class="tab-content" id="tab-search">
            <div class="section-title">🔍 搜索规则配置</div>
            
            <div class="form-group">
                <label for="ruleSearch-checkKeyWord">测试关键词</label>
                <input type="text" id="ruleSearch-checkKeyWord" value="{get_val('ruleSearch.checkKeyWord', '我的')}" placeholder="用于测试搜索的关键词">
            </div>
            
            <div class="form-group">
                <label for="ruleSearch-bookList">书籍列表 *</label>
                <textarea id="ruleSearch-bookList" placeholder="//div[@class='book-item']">{get_val('ruleSearch.bookList', '')}</textarea>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleSearch-name">书名 *</label>
                    <input type="text" id="ruleSearch-name" value="{get_val('ruleSearch.name', '')}" placeholder=".book-title@text">
                </div>
                
                <div class="form-group">
                    <label for="ruleSearch-author">作者</label>
                    <input type="text" id="ruleSearch-author" value="{get_val('ruleSearch.author', '')}" placeholder=".author@text">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleSearch-coverUrl">封面</label>
                    <input type="text" id="ruleSearch-coverUrl" value="{get_val('ruleSearch.coverUrl', '')}" placeholder="img@src">
                </div>
                
                <div class="form-group">
                    <label for="ruleSearch-intro">简介</label>
                    <input type="text" id="ruleSearch-intro" value="{get_val('ruleSearch.intro', '')}" placeholder=".intro@text">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleSearch-bookUrl">书籍URL *</label>
                    <input type="text" id="ruleSearch-bookUrl" value="{get_val('ruleSearch.bookUrl', '')}" placeholder="a@href">
                </div>
                
                <div class="form-group">
                    <label for="ruleSearch-kind">分类</label>
                    <input type="text" id="ruleSearch-kind" value="{get_val('ruleSearch.kind', '')}" placeholder=".kind@text">
                </div>
            </div>
        </div>
        
        <!-- 发现规则 -->
        <div class="tab-content" id="tab-explore">
            <div class="section-title">🌟 发现规则配置</div>
            
            <div class="form-group">
                <label for="ruleExplore-bookList">书籍列表 *</label>
                <textarea id="ruleExplore-bookList" placeholder="//div[@class='book-item']">{get_val('ruleExplore.bookList', '')}</textarea>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleExplore-name">书名 *</label>
                    <input type="text" id="ruleExplore-name" value="{get_val('ruleExplore.name', '')}" placeholder=".book-title@text">
                </div>
                
                <div class="form-group">
                    <label for="ruleExplore-author">作者</label>
                    <input type="text" id="ruleExplore-author" value="{get_val('ruleExplore.author', '')}" placeholder=".author@text">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleExplore-coverUrl">封面</label>
                    <input type="text" id="ruleExplore-coverUrl" value="{get_val('ruleExplore.coverUrl', '')}" placeholder="img@src">
                </div>
                
                <div class="form-group">
                    <label for="ruleExplore-intro">简介</label>
                    <input type="text" id="ruleExplore-intro" value="{get_val('ruleExplore.intro', '')}" placeholder=".intro@text">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleExplore-bookUrl">书籍URL *</label>
                    <input type="text" id="ruleExplore-bookUrl" value="{get_val('ruleExplore.bookUrl', '')}" placeholder="a@href">
                </div>
                
                <div class="form-group">
                    <label for="ruleExplore-kind">分类</label>
                    <input type="text" id="ruleExplore-kind" value="{get_val('ruleExplore.kind', '')}" placeholder=".kind@text">
                </div>
            </div>
        </div>
        
        <!-- 书籍信息 -->
        <div class="tab-content" id="tab-bookinfo">
            <div class="section-title">📖 书籍信息规则配置</div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleBookInfo-name">书名 *</label>
                    <input type="text" id="ruleBookInfo-name" value="{get_val('ruleBookInfo.name', '')}" placeholder="h1@text">
                </div>
                
                <div class="form-group">
                    <label for="ruleBookInfo-author">作者 *</label>
                    <input type="text" id="ruleBookInfo-author" value="{get_val('ruleBookInfo.author', '')}" placeholder=".author@text">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleBookInfo-coverUrl">封面 *</label>
                    <input type="text" id="ruleBookInfo-coverUrl" value="{get_val('ruleBookInfo.coverUrl', '')}" placeholder="img@src">
                </div>
                
                <div class="form-group">
                    <label for="ruleBookInfo-intro">简介</label>
                    <input type="text" id="ruleBookInfo-intro" value="{get_val('ruleBookInfo.intro', '')}" placeholder=".intro@text">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleBookInfo-kind">分类</label>
                    <input type="text" id="ruleBookInfo-kind" value="{get_val('ruleBookInfo.kind', '')}" placeholder=".kind@text">
                </div>
                
                <div class="form-group">
                    <label for="ruleBookInfo-lastChapter">最新章节</label>
                    <input type="text" id="ruleBookInfo-lastChapter" value="{get_val('ruleBookInfo.lastChapter', '')}" placeholder=".last-chapter@text">
                </div>
            </div>
            
            <div class="form-group">
                <label for="ruleBookInfo-tocUrl">目录URL</label>
                <input type="text" id="ruleBookInfo-tocUrl" value="{get_val('ruleBookInfo.tocUrl', '')}" placeholder="目录页URL规则">
            </div>
        </div>
        
        <!-- 目录规则 -->
        <div class="tab-content" id="tab-toc">
            <div class="section-title">📑 目录规则配置</div>
            
            <div class="form-group">
                <label for="ruleToc-chapterList">章节列表 *</label>
                <textarea id="ruleToc-chapterList" placeholder="//div[@class='chapter']">{get_val('ruleToc.chapterList', '')}</textarea>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleToc-chapterName">章节名称 *</label>
                    <input type="text" id="ruleToc-chapterName" value="{get_val('ruleToc.chapterName', '')}" placeholder="a@text">
                </div>
                
                <div class="form-group">
                    <label for="ruleToc-chapterUrl">章节URL *</label>
                    <input type="text" id="ruleToc-chapterUrl" value="{get_val('ruleToc.chapterUrl', '')}" placeholder="a@href">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="ruleToc-isVolume">是否为卷</label>
                    <input type="text" id="ruleToc-isVolume" value="{get_val('ruleToc.isVolume', '')}" placeholder="卷标识规则">
                </div>
                
                <div class="form-group">
                    <label for="ruleToc-updateTime">更新时间</label>
                    <input type="text" id="ruleToc-updateTime" value="{get_val('ruleToc.updateTime', '')}" placeholder="更新时间规则">
                </div>
            </div>
        </div>
        
        <!-- 正文规则 -->
        <div class="tab-content" id="tab-content">
            <div class="section-title">📄 正文规则配置</div>
            
            <div class="form-group">
                <label for="ruleContent-content">正文内容 *</label>
                <textarea id="ruleContent-content" placeholder="#content" style="min-height: 150px;">{get_val('ruleContent.content', '')}</textarea>
            </div>
            
            <div class="tip warning">
                ⚠️ <strong>注意：</strong>正文规则是阅读内容的关键，请确保选择器能准确提取正文内容。
            </div>
        </div>
        
        <!-- 高级设置 -->
        <div class="tab-content" id="tab-advanced">
            <div class="section-title">⚙️ 高级设置</div>
            
            <div class="form-group">
                <label for="respondTime">响应超时时间（毫秒）</label>
                <input type="number" id="respondTime" value="{get_val('respondTime', 180000)}" placeholder="180000">
            </div>
            
            <div class="form-group">
                <label for="customOrder">自定义排序</label>
                <input type="number" id="customOrder" value="{get_val('customOrder', 0)}" placeholder="0">
            </div>
            
            <div class="form-group">
                <label for="weight">权重</label>
                <input type="number" id="weight" value="{get_val('weight', 0)}" placeholder="0">
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="loginUrl">登录URL</label>
                    <input type="text" id="loginUrl" value="{get_val('loginUrl', '')}" placeholder="登录页面URL">
                </div>
                
                <div class="form-group">
                    <label for="bookUrlPattern">URL匹配规则</label>
                    <input type="text" id="bookUrlPattern" value="{get_val('bookUrlPattern', '')}" placeholder="URL匹配正则表达式">
                </div>
            </div>
            
            <div class="form-group">
                <label for="header">请求头配置（JSON格式）</label>
                <textarea id="header" placeholder='{{"User-Agent": "Mozilla/5.0..."}}' style="min-height: 120px; font-family: 'Courier New', monospace;">{get_val('header', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label for="jsLib">JavaScript库代码</label>
                <textarea id="jsLib" placeholder="用于加密解密等功能的JavaScript代码" style="min-height: 150px; font-family: 'Courier New', monospace;">{get_val('jsLib', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label for="loginCheckJs">登录检查脚本</label>
                <textarea id="loginCheckJs" placeholder="CloudFlare绕过、滑块验证等脚本" style="min-height: 150px; font-family: 'Courier New', monospace;">{get_val('loginCheckJs', '')}</textarea>
            </div>
        </div>
        
        <!-- 导出预览 -->
        <div class="tab-content" id="tab-export">
            <div class="section-title">📤 导出预览</div>
            
            <div class="tip">
                💡 <strong>重要：</strong>点击"导出完整书源"按钮会下载完整的JSON文件，Legado只能导入完整的书源格式（数组格式）。
            </div>
            
            <div class="preview-box">
                <h4>📋 书源JSON预览（只读）</h4>
                <div class="json-output" id="jsonPreview"></div>
            </div>
            
            <div class="button-group">
                <button class="btn btn-primary" onclick="generatePreview()">生成预览</button>
                <button class="btn btn-success" onclick="exportBookSource()">📥 导出完整书源</button>
                <button class="btn btn-secondary" onclick="copyToClipboard()">复制到剪贴板</button>
            </div>
        </div>
        
        <div class="button-group" style="padding: 30px;">
            <button class="btn btn-primary" onclick="saveAndExport()">💾 保存并导出</button>
            <button class="btn btn-secondary" onclick="resetForm()">重置表单</button>
        </div>
    </div>
    
    <script>
        // 标签切换
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', function() {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                this.classList.add('active');
                document.getElementById('tab-' + this.dataset.tab).classList.add('active');
            }});
        }});
        
        // 获取表单数据
        function getFormData() {{
            const bookSource = {{
                bookSourceName: document.getElementById('bookSourceName').value,
                bookSourceGroup: document.getElementById('bookSourceGroup').value,
                bookSourceUrl: document.getElementById('bookSourceUrl').value,
                bookSourceType: parseInt(document.getElementById('bookSourceType').value),
                bookSourceComment: document.getElementById('bookSourceComment').value,
                searchUrl: document.getElementById('searchUrl').value,
                exploreUrl: document.getElementById('exploreUrl').value,
                enabled: document.getElementById('enabled').checked,
                enabledCookieJar: document.getElementById('enabledCookieJar').checked,
                enabledExplore: document.getElementById('enabledExplore').checked,
                respondTime: parseInt(document.getElementById('respondTime').value) || 180000,
                customOrder: parseInt(document.getElementById('customOrder').value) || 0,
                weight: parseInt(document.getElementById('weight').value) || 0,
                loginUrl: document.getElementById('loginUrl').value,
                bookUrlPattern: document.getElementById('bookUrlPattern').value,
                header: document.getElementById('header').value,
                jsLib: document.getElementById('jsLib').value,
                loginCheckJs: document.getElementById('loginCheckJs').value,
                lastUpdateTime: Date.now(),
                ruleSearch: {{
                    checkKeyWord: document.getElementById('ruleSearch-checkKeyWord').value,
                    bookList: document.getElementById('ruleSearch-bookList').value,
                    name: document.getElementById('ruleSearch-name').value,
                    author: document.getElementById('ruleSearch-author').value,
                    coverUrl: document.getElementById('ruleSearch-coverUrl').value,
                    intro: document.getElementById('ruleSearch-intro').value,
                    bookUrl: document.getElementById('ruleSearch-bookUrl').value,
                    kind: document.getElementById('ruleSearch-kind').value
                }},
                ruleExplore: {{
                    bookList: document.getElementById('ruleExplore-bookList').value,
                    name: document.getElementById('ruleExplore-name').value,
                    author: document.getElementById('ruleExplore-author').value,
                    coverUrl: document.getElementById('ruleExplore-coverUrl').value,
                    intro: document.getElementById('ruleExplore-intro').value,
                    bookUrl: document.getElementById('ruleExplore-bookUrl').value,
                    kind: document.getElementById('ruleExplore-kind').value
                }},
                ruleBookInfo: {{
                    name: document.getElementById('ruleBookInfo-name').value,
                    author: document.getElementById('ruleBookInfo-author').value,
                    coverUrl: document.getElementById('ruleBookInfo-coverUrl').value,
                    intro: document.getElementById('ruleBookInfo-intro').value,
                    kind: document.getElementById('ruleBookInfo-kind').value,
                    lastChapter: document.getElementById('ruleBookInfo-lastChapter').value,
                    tocUrl: document.getElementById('ruleBookInfo-tocUrl').value
                }},
                ruleToc: {{
                    chapterList: document.getElementById('ruleToc-chapterList').value,
                    chapterName: document.getElementById('ruleToc-chapterName').value,
                    chapterUrl: document.getElementById('ruleToc-chapterUrl').value,
                    isVolume: document.getElementById('ruleToc-isVolume').value,
                    updateTime: document.getElementById('ruleToc-updateTime').value
                }},
                ruleContent: {{
                    content: document.getElementById('ruleContent-content').value
                }}
            }};
            
            return [bookSource];
        }}
        
        // 生成预览
        function generatePreview() {{
            const data = getFormData();
            const jsonStr = JSON.stringify(data, null, 2);
            document.getElementById('jsonPreview').innerHTML = syntaxHighlight(jsonStr);
        }}
        
        // JSON语法高亮
        function syntaxHighlight(json) {{
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\\\u[a-zA-Z0-9]{{4}}|\\\\[^u]|[^\\\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {{
                var cls = 'number';
                if (/^"/.test(match)) {{
                    if (/:$/.test(match)) {{
                        cls = 'key';
                    }} else {{
                        cls = 'string';
                    }}
                }} else if (/true|false/.test(match)) {{
                    cls = 'boolean';
                }} else if (/null/.test(match)) {{
                    cls = 'null';
                }}
                return '<span class="' + cls + '">' + match + '</span>';
            }});
        }}
        
        // 导出书源
        function exportBookSource() {{
            const data = getFormData();
            const jsonStr = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonStr], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = (data[0].bookSourceName || 'book_source') + '.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        // 复制到剪贴板
        function copyToClipboard() {{
            const data = getFormData();
            const jsonStr = JSON.stringify(data, null, 2);
            navigator.clipboard.writeText(jsonStr).then(() => {{
                alert('✅ 已复制到剪贴板！');
            }}).catch(() => {{
                alert('❌ 复制失败，请手动复制');
            }});
        }}
        
        // 保存并导出
        function saveAndExport() {{
            exportBookSource();
        }}
        
        // 重置表单
        function resetForm() {{
            if (confirm('确定要重置表单吗？所有未保存的数据将丢失。')) {{
                location.reload();
            }}
        }}
        
        // 初始化生成预览
        window.onload = function() {{
            generatePreview();
        }};
    </script>
</body>
</html>"""
    
    return html


@tool
def generate_html_editor(
    book_source_json: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    生成可视化HTML书源编辑器
    
    Args:
        book_source_json: 书源JSON字符串（可选，用于预填充）
    
    Returns:
        HTML文件内容字符串
    """
    
    # 解析书源JSON，如果没有则使用默认模板
    if book_source_json:
        try:
            book_source = json.loads(book_source_json)
            if isinstance(book_source, list) and len(book_source) > 0:
                source_data = book_source[0]
            elif isinstance(book_source, dict):
                source_data = book_source
            else:
                source_data = {}
        except:
            source_data = {}
    else:
        source_data = {}
    
    # 构建HTML
    html_content = _build_html_template(source_data)
    
    # 保存到临时文件
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    temp_dir = os.path.join(workspace_path, "tmp")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, "book_source_editor.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return f"""
## 🎨 HTML可视化编辑器已生成

### 📄 文件信息
- **文件路径**：`{file_path}`
- **文件名**：`book_source_editor.html`

### 🚀 使用方法

1. **打开编辑器**
   - 在浏览器中打开 `{file_path}`
   - 或直接双击HTML文件

2. **填写书源信息**
   - 基础信息：书源名称、URL、分组等
   - 搜索规则：书籍列表、书名、作者等
   - 发现规则：发现页配置
   - 书籍信息：详情页规则
   - 目录规则：章节列表配置
   - 正文规则：正文内容提取
   - 高级设置：请求头、JS库等

3. **导出书源**
   - 点击"导出完整书源"按钮
   - 会自动下载完整的JSON文件
   - **注意：导出的是完整的数组格式 [{{...}}]，可直接导入Legado**

### ✨ 功能特点

- ✅ **可视化编辑**：表单化操作，无需手写JSON
- ✅ **多标签页**：分类清晰，易于管理
- ✅ **实时预览**：即时查看JSON输出
- ✅ **一键导出**：自动生成完整JSON文件
- ✅ **语法高亮**：JSON预览带有颜色标注
- ✅ **完整格式**：导出符合Legado标准的数组格式

### ⚠️ 重要提示

- 导出的是**完整的数组格式** `[{{...}}]`，可以直接导入Legado
- 如果只导出部分字段，会导致导入失败
- 必填字段：书源名称、URL、至少一个规则的配置

### 📌 下一步操作

1. 在浏览器中打开编辑器
2. 填写书源配置
3. 点击"导出完整书源"
4. 在Legado APP中导入导出的JSON文件

---

💡 **提示**：这个HTML编辑器是独立的，可以在任何浏览器中使用，无需联网！
"""
