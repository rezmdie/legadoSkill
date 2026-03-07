# Legado书源驯兽师

<div align="center">

**AI驱动的Legado阅读书源自动生成工具**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Legado](https://img.shields.io/badge/Legado-阅读-orange.svg)](https://github.com/gedoor/legado)

**数字时代来临，AI写源不再是幻想**

</div>

---

## 📖 项目简介

Legado书源驯兽师是一个基于大语言模型的智能书源开发辅助工具，专门用于辅助**Legado（阅读）Android应用**的书源开发。通过AI技术自动分析网站结构，生成符合Legado规范的书源JSON，让书源开发变得简单高效。

### ✨ 核心功能

- 🤖 **AI自动生成书源** - 输入网站URL，自动分析并生成书源JSON
- 📚 **知识库支持** - 内置完整的CSS选择器规则、POST请求配置、真实书源模板
- 🔍 **智能分析** - 自动识别网站结构，提取书名、作者、封面、目录、正文等
- ✅ **规则验证** - 严格验证生成的规则是否符合Legado官方规范
- 📖 **教学模式** - 提供知识查询和文档展示，帮助学习书源开发
- 🔄 **自我进化** - 自动吸收用户提供的知识，持续优化技能包

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 支持MCP协议的AI客户端（如Trae IDE）

### 安装

```bash
# 克隆项目
git clone https://github.com/mctiantian2501314/legadoSkill.git

# 进入项目目录
cd legadoSkill

# 安装依赖
pip install -r debugger/requirements.txt
```

### 使用方式

1. **在Trae IDE中使用**：直接调用技能包
2. **命令行调试**：运行 `python debugger/test_universal.py`

---

## 📁 项目结构

```
legadoSkill/
├── .trae/skills/legado-book-source-tamer/
│   └── SKILL.md                    # 技能包核心文件
├── assets/                         # 知识库资源
│   ├── legado_knowledge_base.md    # 完整知识库
│   ├── css选择器规则.txt           # CSS选择器规则
│   ├── 书源规则：从入门到入土.md    # 详细教程
│   ├── 真实书源模板库.txt           # 真实模板
│   └── knowledge_base/book_sources/ # 1751个真实书源案例
├── debugger/                       # 调试引擎
│   ├── engine/                     # 核心引擎
│   │   ├── debug_engine.py         # 调试引擎主类
│   │   ├── analyze_rule.py         # 规则分析器
│   │   └── auto_fixer.py           # 自动修复模块
│   └── test_universal.py           # 通用测试入口
├── legado/                         # Legado官方源码
├── config/                         # 配置文件
├── docs/                           # 文档
└── README.md                       # 项目说明
```

---

## 🎯 核心特性

### 三阶段工作流程

```
第一阶段：收集信息
    ├── 查询知识库
    ├── 检测网站编码
    ├── 获取真实HTML
    └── 分析HTML结构

第二阶段：严格审查
    ├── 编写规则
    ├── 验证语法
    └── 处理特殊情况

第三阶段：创建书源
    ├── 准备完整JSON
    ├── 调试测试
    └── 输出JSON文件
```

### 知识库支持

- **1751个真实书源案例** - 学习真实书源的规则写法
- **CSS选择器规则** - 完整的选择器语法手册
- **POST请求配置** - 规范的POST请求配置方法
- **正则表达式规范** - 清理内容的正确写法
- **编码处理指南** - GBK/UTF-8编码处理方法

---

## 📝 项目历程

| 日期 | 里程碑 |
|------|--------|
| 2026/02/17 | 项目创建，开始搜集提示词 |
| 2026/02/24 | Python部署版本落地 |
| 2026/02/25 | 封装好环境版，进入瓶颈期研究 |
| 2026/03/05 | 准备写说明文档，公开测试 |
| 2026/03/08 | 改成技能包完整体，决定开源 |

---

## 🙏 致谢

### 感谢大模型支持

本项目在开发过程中得到了以下大模型的帮助：

- **扣子编程** - 提供开发环境支持
- **元宝** - 提供AI能力支持
- **mlg** - 提供技术支持
- **DeepSeek** - 提供推理能力支持

### 感谢贡献者

| 贡献者 | 贡献内容 |
|--------|----------|
| [xiangseSkill](https://github.com/lindongjiang/xiangseSkill/) | 来自香色闺阁书源的思路和提示 |
| [@雨落星辰(ima版本)搬运工](https://ima.qq.com/wiki/?shareId=7cccd0573f64fe67a4d7c4b05ce801e5cd8daadc9c9dc26e755528eaa5a2439b) | 提供ima版本支持 虽然是一名搬运工|
| [早期阅读AI写源可视化参考](https://github.com/Tthfyth/source/) | 提供可视化参考 |

### 特别感谢

- **Legado开源项目** - 提供优秀的阅读APP
- **各大股东们** - 持续支持和关注
- **社区贡献者** - 提供宝贵的反馈和建议

---

## 📜 开源协议

本项目采用 **MIT协议** 开源。

```
MIT License

Copyright (c) 2026 Legado书源驯兽师

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📚 相关链接

- 📖 [飞书文档](https://my.feishu.cn/wiki/Ogj6wXOrJiSFMEk2dJKcMgZcnzg?from=from_copylink)
- 🎁 [腾讯频道礼包](https://pd.qq.com/s/daef5rxez?b=2)
- 💻 [Legado官方仓库](https://github.com/gedoor/legado)

---

## 🌟 项目愿景

**数字时代来临，AI写源不再是幻想。**

随着模型越来越强大，AI写源将成为可能。本项目致力于：

1. **降低书源开发门槛** - 让更多人能够轻松创建书源
2. **提高书源开发效率** - 自动化繁琐的分析工作
3. **构建知识共享社区** - 汇聚书源开发经验和技巧
4. **持续进化优化** - 吸收用户反馈，不断提升能力

---

## 🤝 参与贡献

欢迎所有形式的贡献！

1. **提交Issue** - 报告问题或提出建议
2. **提交PR** - 贡献代码或文档
3. **分享知识** - 提供书源开发经验和技巧
4. **传播项目** - 让更多人了解和使用

---

## 📮 联系方式

- 项目主页：[GitHub](https://github.com/mctiantian2501314/legadoSkill)
- 问题反馈：[Issues](https://github.com/mctiantian2501314/legadoSkill/issues)

---

<div align="center">

**从MCP到技能包，完完全全都是一个思路**

**一切还是得看飞书文章**

**代码是我写的，代码是我写的，代码是我写的**

**Python写的！**

---

**⭐ 如果这个项目对你有帮助，请给一个Star ⭐**

</div>
