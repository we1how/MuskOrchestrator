# LEARNING.md - Product Engineer 学习记录

## 学习记录索引

### 已学习项目（近7天）
| 日期 | 项目名称 | 来源 | 核心洞察 |
|------|----------|------|----------|
| 2026-03-08 | Ki Editor - AST-based code editor | Hacker News | 基于AST的结构化编辑器，多光标语义操作 |
| 2026-03-05 | Security boundaries in agentic architectures | Vercel Blog | Agent安全的四层架构与隔离策略 |
| 2026-03-05 | Alibaba OpenSandbox | GitHub Trending | AI应用通用沙盒平台，支持多语言SDK |

---

### 今日学习（2026-03-05）

#### 内容1：Security boundaries in agentic architectures
- **来源**：Vercel Blog (Malte Ubl, Harpreet Arora)
- **核心洞察**：Agentic系统需要四层安全边界——Agent本身、Agent Secrets、生成代码执行、文件系统/环境。当前默认的"零边界"架构使生成的代码能直接访问所有凭据，存在严重的Prompt Injection风险。
- **信息差价值**：高
- **可应用性**：架构

#### 内容2：Alibaba OpenSandbox
- **来源**：GitHub Trending Python
- **核心洞察**：阿里巴巴开源的AI应用通用沙盒平台，提供多语言SDK（Python/Java/JS/C#/Go）、统一沙盒API、Docker/K8s运行时，专门支持Coding Agents、GUI Agents、AI代码执行等场景。
- **信息差价值**：高
- **可应用性**：工具/架构

---

## 2026-03-08 学习记录

### 内容：Ki Editor - 基于AST的结构化代码编辑器

**Source**: https://ki-editor.org/ (Hacker News Top, 347 points)
**Focus**: Editor / Developer Experience

**核心洞察**：
1. **范式突破**：Ki Editor直接操作AST（抽象语法树）而非纯文本，将代码编辑从"字符操作"升级为"语义操作"
2. **多光标+选择模式**：通过"Selection Modes"统一词/行/语法节点级别的导航，支持并行操作多个语法节点
3. **重构安全性**：AST级别的操作天然保证语法有效性，避免传统文本重构引入的语法错误
4. **意图驱动**：减少"键盘/鼠标体操"，让开发者直接表达操作意图（如"提取函数"而非"剪切粘贴"）

**信息差分析**：
- **国外热度**：高（Hacker News Top，347 points）
- **国内使用情况**：几乎无人知晓，属于前沿概念
- **工程价值**：对代码重构、IDE插件开发、AI代码生成有启发意义

**可应用性评估**：
- **短期**：研究其Selection Modes设计，优化我们的代码编辑体验
- **中期**：借鉴AST操作理念，改进AI代码生成后的自动重构能力
- **长期**：探索将结构化编辑集成到Agent代码生成工作流中

---

## 关键学习要点

### Agent安全架构最佳实践

**四 Actor 模型**：
1. **Agent Harness**: 可信任的标准SDLC组件
2. **Agent Secrets**: API Token、数据库凭据等，需严格保护
3. **Generated Code Execution**: 不可信的wildcard，需要隔离
4. **Filesystem/Environment**: 运行环境

**三层安全架构演进**：
1. **零边界（当前默认）**：所有组件共享安全上下文，风险最高
2. **Secret Injection Proxy**: 代理层注入凭据，防止泄露但无法阻止运行时滥用
3. **独立计算分离**: Agent Harness与生成代码在独立VM/沙盒中运行，最优安全

### Alibaba OpenSandbox 特性
- 多语言SDK支持
- Docker + Kubernetes高性能运行时
- 内置命令执行、文件系统、代码解释器
- Ingress Gateway + Egress Controls网络策略
- 适用场景：Coding Agents、GUI Agents、Agent Evaluation、RL Training

---

## 可应用技术

### 立即可以应用：
- [ ] 评估OpenSandbox作为我们的Agent执行环境
- [ ] 设计Agent Secrets管理机制，避免直接暴露给Agent
- [ ] 研究Secret Injection Proxy模式

### 需要进一步研究：
- [ ] OpenSandbox与现有K8s基础设施集成方案
- [ ] 与Claude Code/Cursor沙盒模式的对比
- [ ] Ki Editor的Selection Modes设计原理及实现
- [ ] AST操作在AI代码生成后的自动重构应用
