# 🎯 直播带货智能选达人平台

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)](./frontend/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](./backend/pyproject.toml)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white)](./frontend/package.json)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-1acb73?logo=langchain&logoColor=white)](./backend/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> 基于字节跳动开源 [DeerFlow](https://github.com/bytedance/deer-flow) AI超级智能体框架二次开发的直播带货达人甄选平台。

**品牌方输入选人需求 → 平台自动采集多平台数据 → 四维评分 + 多Agent并行分析 → 生成对比推荐报告 → 合作反馈驱动模型自优化。形成"搜索→分析→推荐→反馈进化"闭环。**

---

## 📖 目录

- [项目背景](#项目背景)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [功能演示](#功能演示)
- [API 文档](#api-文档)
- [项目结构](#项目结构)
- [测试](#测试)
- [里程碑](#里程碑)
- [许可证](#许可证)

---

## 项目背景

品牌方在直播带货前需要从海量达人中筛选最匹配的人选，传统方式依赖人工分析，耗时长、维度少、缺乏数据闭环。

本系统在 DeerFlow AI 超级智能体框架之上，新增 **达人搜索、多维度评分、Agent并行分析、推荐报告生成、效果反馈闭环** 五大模块，将原本需要 2-3 天的人工选人流程压缩至分钟级。

### 适用场景

- 🛍️ **品牌方**：大促前批量筛选带货达人，输出结构化推荐报告
- 📊 **MCN机构**：管理达人资源池，评估合作ROI
- 🤖 **个人运营**：快速匹配适合自己品类的中腰部达人

---

## 核心功能

| 功能模块 | 说明 | 亮点 |
|---------|------|------|
| 🔍 **达人搜索** | 自然语言 + 结构化筛选，对接第三方数据平台 | 品类/粉丝/互动率/报价多维过滤，8品类150位达人 |
| 📊 **多维度分析** | 粉丝画像、内容风格、商业表现、风险合规四大专业维度 | 4个专业SubAgent并行分析，每个输出0-100分+理由 |
| 🧠 **智能推荐** | 四维加权评分模型 + AI 推荐报告 | 匹配度(0.35)×传播力(0.25)×带货力(0.25)×性价比(0.15) |
| 🔄 **效果反馈闭环** | 合作后评分反馈 → 模型权重自优化 | 梯度下降简化版，learning_rate=0.05，confidence≥0.6门控 |
| 🏗️ **多平台架构** | 抽象适配层，已完成抖音Mock数据，预留快手/小红书扩展点 | DataPlatformAdapter ABC → MockAdapter/DouyinAdapter |
| 📈 **反馈看板** | 评分分布、趋势统计、权重配置可视化 | 总反馈/平均分/星级分布三卡一屏 |

---

## 系统架构

```
┌──────────────────────────────────────────────────┐
│                    Frontend                       │
│  Next.js 16 + React 19 + TypeScript + Tailwind CSS│
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ 达人广场  │ │ 选人任务  │ │   反馈分析看板    │  │
│  │ 搜索+筛选 │ │ 候选人CRUD │ │ 评分分布+趋势    │  │
│  └──────────┘ └──────────┘ └──────────────────┘  │
└────────────────────┬─────────────────────────────┘
                     │ /api/influencer/*
┌────────────────────▼─────────────────────────────┐
│               Gateway API (FastAPI)               │
│  ┌───────────────────────────────────────────┐   │
│  │         influencer 路由器 (20+ 端点)       │   │
│  │  搜索 · 详情 · 任务CRUD · 对比 · 反馈 · 分析  │   │
│  └───────────────────────────────────────────┘   │
│  ┌──────────────┐ ┌──────────┐ ┌─────────────┐   │
│  │ DataPlatform │ │ Scoring  │ │  Feedback   │   │
│  │   Adapter    │ │  Engine  │ │   Service   │   │
│  └──────────────┘ └──────────┘ └─────────────┘   │
└────────────────────┬─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│          DeerFlow Harness (LangGraph)             │
│  ┌──────────────────────────────────────────┐    │
│  │         Lead Agent (任务编排)             │    │
│  │   ┌──────────┐  ┌──────────┐             │    │
│  │   │ Agent工具 │  │ SubAgent │             │    │
│  │   │ search   │  │ fan      │ ─ 粉丝分析   │    │
│  │   │ compare  │  │ content  │ ─ 内容分析   │    │
│  │   │ report   │  │commercial│ ─ 商业分析   │    │
│  │   │ feedback │  │ risk     │ ─ 风险扫描   │    │
│  │   └──────────┘  └──────────┘             │    │
│  └──────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────┐    │
│  │  29层中间件链 · Skill系统 · 记忆/沙箱      │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### Agent 协作流程（5 阶段）

```
阶段1: 需求理解   → Lead Agent 将自然语言转为结构化筛选条件
阶段2: 达人搜索   → search_influencers + 四维评分排序，输出 Top 15
阶段3: 并行分析   → 3个SubAgent并行(粉丝/内容/商业) → 风险扫描紧随启动
阶段4: 报告生成   → 加权汇总 + 横向对比 + AI推荐报告(Markdown)
阶段5: 反馈闭环   → 合作评分 → 权重微调 → 模型进化
```

---

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| **Agent 框架** | LangGraph + LangChain | 复用 DeerFlow Lead Agent + SubAgent 体系 |
| **后端** | Python 3.12 + FastAPI | REST API + LangGraph 兼容路由 |
| **ORM** | SQLAlchemy 2.0 + Alembic | 5张业务表，复用 DeerFlow 迁移体系 |
| **数据库** | SQLite (开发) / PostgreSQL (生产) | 通过 DeerFlow config.yaml 切换 |
| **前端** | Next.js 16 + React 19 + TypeScript | App Router，5条业务路由 |
| **样式** | Tailwind CSS 4 + shadcn/ui | 组件化，深色模式支持 |
| **图表** | 手写 SVG 雷达图 / 对比图 | 无第三方图表库依赖 |
| **数据平台** | 抽象适配层 (ABC) → Mock/Douyin | 150条模拟数据(SEED=42)，8品类 |

### DeerFlow 基础设施复用

| 能力 | 说明 |
|------|------|
| **29层中间件链** | 记忆管理、上下文压缩、工具异常归一化、Loop检测、Sandbox审计 |
| **20+公共Skill** | 声明式SKILL.md扩展，7大类安全规则 |
| **三级记忆** | 用户画像 → 历史背景 → 分类事实，防抖队列异步提取，保鲜淘汰 |
| **上下文管理** | 渐进式摘要 + 持久上下文捕获 + SystemMessage合并 |

---

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 22+
- pnpm
- uv
- Git

### 1. 克隆仓库

```bash
git clone git@github.com:chenxiangwang0457/live-influencer.git
cd live-influencer
```

### 2. 配置环境

```bash
# 复制配置模板
cp config.example.yaml config.yaml
cp extensions_config.example.json extensions_config.json

# 创建 .env 文件并配置 LLM API Key
echo "OPENAI_API_KEY=your-key" > .env
```

### 3. 安装依赖

```bash
# 后端
cd backend
uv sync

# 前端
cd ../frontend
pnpm install
```

### 4. 启动服务

```bash
# 终端1: 启动后端 (端口 8001)
cd backend
DEER_FLOW_AUTH_DISABLED=1 PYTHONPATH=. uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --reload

# 终端2: 启动前端 (端口 3000)
cd frontend
pnpm dev
```

### 5. 打开浏览器

访问 **http://localhost:3000**，左侧导航栏：

```
💬 对话        → Agent 对话（支持 "帮我找美妆达人" 自然语言交互）
🤖 智能体      → SubAgent 管理
⏰ 定时任务    → 定时任务配置
✅ 达人广场    → 搜索/筛选/浏览达人
📋 选人任务    → 创建选人任务，管理候选人
📊 反馈分析    → 合作反馈统计 + 评分趋势
```

### 体验路径

```
达人广场 → 筛选"美妆"品类(10-50万粉丝) → 浏览达人详情
    → 创建选人任务"618美妆达人选拔"
    → 添加3位候选人 → AI推荐 → 查看报告 → 下载
    → 横向对比 → 选定达人 → 提交合作反馈
    → 反馈分析看板 → 查看评分分布
```

---

## 功能演示

### 达人广场 + 筛选

支持按品类、粉丝区间(万)、互动率(%)、报价(元)、关键词多维筛选，300ms 防抖实时过滤。分页浏览 150 位达人，按 GMV/粉丝数/互动率排序。

### 达人详情页

SVG 四维雷达图（匹配度/传播力/带货力/性价比）+ 粉丝画像分布（年龄/性别/城市）+ 内容风格标签云 + 品牌合作历史时间线。

### 选人任务 + 候选人管理

任务 CRUD + 手动添加/批量移除候选人 + 状态流转（待联系→已联系→已选定→已淘汰）+ 可排序候选人表格。

### 横向对比抽屉

勾选 ≥2 位达人 → 侧滑面板：多人 SVG 雷达图叠加 + 6 维指标逐行对比表（红绿高亮优劣）。

### AI 推荐报告

后端四维评分引擎 → 生成结构化 Markdown 报告（筛选条件 + 达人排名 + 综合分析 + 行动建议）→ 支持浏览器下载 .md 文件。

### 反馈闭环

已选定达人出现反馈表单：1-5星评分 + 10种评价标签 + 文字评价 → 写入数据库 → 自动更新 influencer_scores + 权重微调（confidence ≥ 0.6 门控）。

### 反馈分析看板

总反馈数 / 平均评分 / 评分分布概览 一目了然，当前四维权重配置 + 自优化机制说明。

### Agent 对话模式

在对话页输入"帮我找美妆类达人"→ Agent 调用 search_influencers 工具 → 聊天内渲染达人卡片/对比表/报告 Artifact。启用 SubAgent 后自动并行派遣 fan-analyst / content-analyst / commercial-analyst / risk-scanner 进行深度分析。

---

## API 文档

所有端点挂载在 `/api/influencer` 下，共 **20+ 个 REST 端点**：

### 达人管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/influencer/search` | 搜索达人（品类/粉丝/互动率/报价/排序/分页） |
| `GET` | `/api/influencer/{platform_uid}` | 达人详情 + 完整画像（ID 或平台UID均可） |
| `GET` | `/api/influencer/{platform_uid}/history` | 达人历史合作记录 |

### 选人任务

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/influencer/selections` | 创建选人任务 |
| `GET` | `/api/influencer/selections` | 任务列表（分页 + 状态筛选） |
| `GET` | `/api/influencer/selections/{id}` | 任务详情（含候选人 + 分数） |
| `PUT` | `/api/influencer/selections/{id}` | 更新任务（标题/目标/状态） |
| `POST` | `/api/influencer/selections/{id}/analyze` | AI 分析生成推荐报告 |
| `POST` | `/api/influencer/selections/{id}/candidates` | 手动添加候选人 |
| `DELETE` | `/api/influencer/selections/{id}/candidates/{cid}` | 移除候选人 |
| `PATCH` | `/api/influencer/selections/{id}/candidates/{cid}` | 更新候选状态 |

### 反馈闭环

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/influencer/feedbacks` | 提交合作反馈（含评分自优化） |
| `GET` | `/api/influencer/feedbacks` | 反馈列表（按达人/任务筛选） |
| `GET` | `/api/influencer/feedbacks/stats` | 反馈统计（评分分布/趋势） |

### 分析与评分

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/influencer/scores/{platform_uid}` | 达人四维评分明细 |
| `GET` | `/api/influencer/analytics/weights` | 当前评分权重配置 |
| `GET` | `/api/influencer/analytics/trends` | 评分模型趋势数据 |

---

## 项目结构

```
live-influencer/
├── backend/
│   ├── app/influencer/                    # 达人模块 - API 层
│   │   ├── models/                        # SQLAlchemy ORM (5张表)
│   │   │   ├── influencer.py              # 达人画像表
│   │   │   ├── selection.py               # 选人任务 + 任务-达人关联表
│   │   │   └── feedback.py                # 合作反馈 + 达人评分表
│   │   ├── services/                      # 业务逻辑层
│   │   │   ├── data_platform/             # 第三方平台API适配
│   │   │   │   ├── base.py                # DataPlatformAdapter 抽象基类
│   │   │   │   └── mock.py                # MockAdapter (150条模拟数据)
│   │   │   ├── scoring.py                 # 四维评分引擎
│   │   │   ├── matching.py                # 匹配推荐引擎
│   │   │   ├── feedback.py                # 反馈处理 + 权重自优化
│   │   │   └── errors.py                  # 自定义异常体系
│   │   ├── routers/
│   │   │   └── influencers.py             # 20+ REST端点 (单路由器)
│   │   └── config.py                      # 模块配置
│   │
│   └── packages/harness/deerflow/
│       ├── tools/influencer/              # Agent 工具层
│       │   ├── search_influencers.py      # 达人搜索工具 (工厂模式)
│       │   ├── compare_influencers.py     # 达人对比工具
│       │   ├── recommend_report.py        # 推荐报告工具
│       │   ├── record_feedback.py         # 反馈记录工具
│       │   ├── fallback.py                # 降级兜底
│       │   └── registry.py                # 工具注册中心
│       └── subagents/builtins/            # 专业分析 SubAgent
│           ├── fan_analyst.py             # 粉丝画像分析师
│           ├── content_analyst.py         # 内容风格分析师
│           ├── commercial_analyst.py      # 商业表现分析师
│           └── risk_scanner.py            # 风险合规扫描师
│
├── frontend/src/
│   ├── app/workspace/influencer/          # 页面路由
│   │   ├── page.tsx                       # 达人广场
│   │   ├── [id]/page.tsx                  # 达人详情页
│   │   ├── selections/page.tsx            # 选人任务列表
│   │   ├── selections/[id]/page.tsx       # 任务详情 (候选人+对比+报告+反馈)
│   │   └── analytics/page.tsx             # 反馈分析看板
│   ├── core/influencer/                   # 前端业务逻辑
│   │   ├── types.ts                       # 类型定义 + 工具函数
│   │   └── api.ts                         # 11个 API 函数
│   └── components/workspace/influencer/   # UI 组件 (14个)
│       ├── filter-panel.tsx               # 筛选面板 (300ms防抖)
│       ├── search-bar.tsx                 # 搜索栏
│       ├── influencer-card.tsx            # 达人卡片
│       ├── influencer-detail.tsx          # 达人详情
│       ├── candidate-table.tsx            # 候选人表格 (可排序)
│       ├── compare-drawer.tsx             # 对比抽屉 (多人雷达+指标对比)
│       ├── report-card.tsx                # 报告卡片 (Markdown+下载)
│       ├── feedback-form.tsx              # 反馈表单 (星级+标签+评价)
│       ├── add-influencer-dialog.tsx      # 手动添加达人弹窗
│       ├── radar-chart.tsx                # SVG雷达图 (单人+多人叠加)
│       └── messages/                      # 聊天消息渲染
│           ├── search-result-msg.tsx      # 达人搜索结果卡片
│           ├── compare-table-msg.tsx       # 对比表消息
│           ├── report-artifact-msg.tsx     # 报告 Artifact 消息
│           └── influencer-result-renderer.tsx # 消息类型分发器
│
├── skills/public/influencer/              # Agent Skill 定义
│   └── SKILL.md                           # 6步标准工作流 + 降级规则
│
├── docs/superpowers/
│   ├── specs/2026-07-12-live-influencer-design.md  # 设计文档 (12章节)
│   └── plans/2026-07-12-live-influencer-phase1-2-mvp.md  # 实施计划
│
└── backend/tests/influencer/              # 测试套件 (116 tests)
    ├── test_models.py                     # 模型测试 (7)
    ├── test_data_platform.py              # 数据平台测试 (28)
    ├── test_scoring.py                    # 评分模型测试 (9)
    ├── test_matching.py                   # 匹配引擎测试 (5)
    ├── test_api_influencers.py            # 达人 API 测试 (6)
    ├── test_api_selections.py             # 选人任务 API 测试 (6)
    ├── test_api_feedback_scores.py        # 反馈/评分 API 测试 (17)
    ├── test_agent_tools.py                # Agent 工具测试 (37)
    └── test_integration_e2e.py            # 端到端集成测试 (1)
```

---

## 测试

```bash
# 运行全部测试
cd backend
PYTHONPATH=. uv run pytest tests/influencer/ -v

# 结果: 116 passed, 0 failed
```

| 测试层级 | 文件 | 用例数 | 覆盖内容 |
|---------|------|--------|---------|
| Unit - 模型 | test_models.py | 7 | ORM 字段验证、关联关系 |
| Unit - 数据平台 | test_data_platform.py | 28 | MockAdapter 搜索/详情，边界值 |
| Unit - 评分 | test_scoring.py | 9 | 四维计算正确性、边界值 |
| Unit - 匹配 | test_matching.py | 5 | 匹配排序、Top-N |
| API - 达人 | test_api_influencers.py | 6 | 搜索/详情端点，参数校验，错误码 |
| API - 任务 | test_api_selections.py | 6 | 任务 CRUD、候选人管理 |
| API - 反馈 | test_api_feedback_scores.py | 17 | 反馈提交、评分更新、统计 |
| Agent - 工具 | test_agent_tools.py | 37 | search/compare/report/feedback 工具 |
| 集成 | test_integration_e2e.py | 1 | 搜索→创建→分析→反馈 完整链路 |

---

## 里程碑

| 阶段 | 内容 | 状态 |
|------|------|------|
| **Phase 1** | 数据模型、MockAdapter、达人搜索/详情 API、达人广场页面 | ✅ 完成 |
| **Phase 2** | 选人任务 CRUD、评分模型、匹配引擎、候选人管理、Agent Tools | ✅ 完成 |
| **Phase 3** | 4个专业SubAgent、Lead Agent五阶段编排、降级处理、AI推荐报告 | ✅ 完成 |
| **Phase 4** | 反馈API、评分自优化、反馈统计看板 | ✅ 完成 |
| **Phase 5** | 真实平台对接 (DouyinAdapter)、Token Bucket限流、数据同步 | 📋 规划中 |
| **Phase 6** | E2E测试覆盖、移动端适配、性能优化 | 📋 规划中 |

---

## 设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 架构模式 | DeerFlow 模块内嵌 | 复用29层中间件/记忆/Skill/沙箱基础设施 |
| SubAgent 拆分 | 按分析维度拆分（粉丝/内容/商业/风险） | 同一维度同一裁判，评分可比；独立降级 |
| 数据源策略 | 第三方API为主 + Mock为辅 | Mock保底开发演示，API打通后无缝切换 |
| Agent工具模式 | 工厂模式 (adapter + engine 闭包注入) | harness层不依赖app层，工具实例化在Gateway启动时 |
| 路由设计 | 单路由器，静态路径优先于动态路径 | 避免 /{platform_uid} 拦截 /selections |
| 反馈机制 | 手动评分为主，sales_performance字段预留自动回传 | 先跑通闭环，预留自动化扩展点 |

---

## 许可证

本项目基于 [MIT License](./LICENSE) 开源。

上游项目 [DeerFlow](https://github.com/bytedance/deer-flow) © 2025 ByteDance，同样使用 MIT License。

---

## 相关资源

- 📘 [设计文档](docs/superpowers/specs/2026-07-12-live-influencer-design.md) — 12章节完整设计
- 📋 [功能清单](功能清单.md) — 50+条可测试功能点
- 🧪 [测试套件](backend/tests/influencer/) — 116个测试用例
- 🦌 [DeerFlow 上游](https://github.com/bytedance/deer-flow) — 字节跳动开源 AI 超级智能体框架
