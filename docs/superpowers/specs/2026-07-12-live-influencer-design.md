# 直播带货智能选达人平台 — 设计文档

> 基于 DeerFlow 二次开发 | 秋招项目
> 创建日期: 2026-07-12

## 1. 项目概述

### 1.1 业务场景

品牌方在直播带货前，需要从海量达人中筛选最匹配的人选。本系统通过 AI Agent 协作，实现从需求理解、多维度分析、智能推荐到合作反馈闭环的全流程管理。

### 1.2 核心功能

| 功能 | 说明 |
|------|------|
| 达人搜索 | 自然语言 + 结构化筛选，对接第三方平台数据 |
| 多维度分析 | 粉丝画像、内容风格、商业表现、风险合规四个专业维度的深度分析 |
| 智能推荐 | 加权评分模型 + AI 推荐报告 |
| 效果反馈闭环 | 合作后评分反馈 → 模型权重自优化 |
| 多平台架构 | 抽象适配层，先接入抖音，预留快手/小红书扩展点 |

### 1.3 技术方案

采用 **DeerFlow 模块内嵌** 架构——在 DeerFlow 现有 `app/` 和 `deerflow/` 体系内新增 `influencer` 模块，遵循现有架构模式（类比 IM Channels），拥有独立数据模型、API 路由、业务逻辑和前端页面，同时复用 Agent/Memory/Sandbox 等基础设施。

---

## 2. 系统架构

### 2.1 模块目录结构

```
live-influencer/
├── backend/
│   ├── app/influencer/              # [新增] 达人模块 - API 层
│   │   ├── __init__.py
│   │   ├── routers/
│   │   │   ├── influencers.py       # 达人 CRUD + 搜索/筛选 API
│   │   │   ├── selections.py        # 选人任务 API
│   │   │   ├── feedbacks.py         # 评分反馈 API
│   │   │   └── analytics.py         # 数据分析/看板 API
│   │   ├── models/                  # SQLAlchemy ORM 模型
│   │   │   ├── influencer.py        # 达人画像表
│   │   │   ├── selection.py         # 选人任务表
│   │   │   ├── feedback.py          # 合作反馈表
│   │   │   └── platform_data.py     # 平台原始数据表
│   │   └── services/                # 业务逻辑层
│   │       ├── data_platform/       # 第三方平台API适配
│   │       │   ├── base.py          # 抽象基类 (预留多平台扩展)
│   │       │   ├── douyin.py        # 抖音/蝉妈妈API适配
│   │       │   └── mock.py          # 模拟数据 (开发/演示用)
│   │       ├── matching.py          # 匹配推荐引擎
│   │       ├── scoring.py           # 达人评分模型
│   │       └── feedback.py          # 反馈处理 + 评分自优化
│   │
│   └── packages/harness/deerflow/
│       └── tools/influencer/        # [新增] 暴露给 Agent 的工具
│           ├── search_influencers.py
│           ├── compare_influencers.py
│           ├── recommend_report.py
│           └── record_feedback.py
│
├── frontend/src/
│   ├── app/workspace/influencer/    # [新增] 达人管理页面路由
│   │   ├── page.tsx                 # 达人广场
│   │   ├── [id]/page.tsx            # 达人详情
│   │   ├── selections/
│   │   │   ├── page.tsx             # 选人任务列表
│   │   │   └── [id]/page.tsx        # 任务详情
│   │   └── analytics/
│   │       └── page.tsx             # 反馈统计 + 评分趋势
│   ├── core/influencer/             # [新增] 前端业务逻辑
│   │   ├── hooks.ts
│   │   ├── types.ts
│   │   └── api.ts
│   └── components/workspace/        # [新增] 达人相关组件
│       └── influencer/
│           ├── influencer-list.tsx
│           ├── influencer-card.tsx
│           ├── influencer-detail.tsx
│           ├── influencer-compare.tsx
│           ├── selection-wizard.tsx
│           ├── feedback-form.tsx
│           ├── filter-panel.tsx
│           ├── report-card.tsx
│           └── messages/            # 聊天消息渲染
│               ├── search-result-msg.tsx
│               ├── compare-table-msg.tsx
│               └── report-artifact-msg.tsx
│
└── skills/public/influencer/        # [新增] Agent Skill 定义
    └── SKILL.md
```

### 2.2 模块边界规则

```
deerflow.influencer.* (harness层)
  → 纯工具定义，不依赖 app.*
  → 暴露: search_influencers / compare_influencers / recommend_report / record_feedback

app.influencer.* (应用层)
  → API路由 + 业务逻辑
  → 可依赖 deerflow.*
  → 数据平台适配器: 统一 base.py 抽象，通过配置切换实现

前端
  → 新增独立 Workspace 子页面，不影响现有聊天页面
  → 聊天页面内渲染达人相关消息卡片
```

### 2.3 技术栈

| 层 | 技术 |
|----|------|
| Agent 框架 | LangGraph (复用 DeerFlow) |
| 后端 API | FastAPI (复用 DeerFlow Gateway) |
| 数据库 | SQLAlchemy + Alembic (复用 DeerFlow 迁移体系) |
| 前端 | Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 |
| 图表 | 雷达图/对比图 (dataviz 组件) |
| 数据平台对接 | HTTP + Token Bucket 限流 |

---

## 3. 数据模型

### 3.1 达人画像 `influencers`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| platform | String(32) | douyin / kuaishou / xiaohongshu |
| platform_uid | String(128) | 平台唯一ID |
| nickname | String(128) | 昵称 |
| avatar_url | String(512) | 头像URL |
| category | String(64) | 主营类目 |
| sub_categories | JSON | 二级类目列表 |
| followers_count | Integer | 粉丝数 |
| avg_likes | Integer | 近30天平均点赞 |
| avg_comments | Integer | 近30天平均评论 |
| avg_shares | Integer | 近30天平均转发 |
| engagement_rate | Float | 互动率(%) |
| avg_gmv | Float | 近30天场均GMV |
| avg_sales | Integer | 近30天场均销量 |
| price_range_min | Integer | 最低报价 |
| price_range_max | Integer | 最高报价 |
| demographics | JSON | 粉丝画像 {age, gender, city} |
| content_style | JSON | 内容风格标签 |
| brand_history | JSON | 历史合作品牌 |
| data_source | String(32) | 数据来源: mock / chamama / feigua |
| created_at | DateTime | |
| updated_at | DateTime | |

### 3.2 选人任务 `selections`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| thread_id | String(128) | 关联 DeerFlow 对话线程 |
| title | String(256) | 任务名称 |
| goal | Text | 选人目标描述 |
| criteria | JSON | 筛选条件 {category, follower_range, ...} |
| status | String(32) | draft / in_progress / completed / archived |
| result_summary | Text | AI 生成结论摘要 |
| created_at | DateTime | |
| updated_at | DateTime | |

### 3.3 任务-达人关联 `selection_influencers`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| selection_id | FK → selections | |
| influencer_id | FK → influencers | |
| match_score | Float | 匹配得分 (0-100) |
| match_reason | Text | AI 匹配理由 |
| status | String(32) | shortlisted / contacted / selected / rejected |
| added_by | String(32) | ai_recommend / manual_add |
| notes | Text | 品牌方备注 |

### 3.4 合作反馈 `feedbacks`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| selection_id | FK → selections | |
| influencer_id | FK → influencers | |
| rating | Integer | 1-5 星 |
| review | Text | 文字评价 |
| sales_performance | JSON | 带货表现 {gmv, roi, conversion} (预留自动回传) |
| tags | JSON | 评价标签 |
| created_at | DateTime | |

### 3.5 达人评分 `influencer_scores`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| influencer_id | FK → influencers | |
| dimension | String(32) | overall / engagement / sales / professionalism |
| score | Float | 0-100 |
| confidence | Float | 置信度 0-1 |
| version | Integer | 评分模型版本号 |
| factors | JSON | 评分因子明细 |
| updated_at | DateTime | |

---

## 4. 匹配评分模型

### 4.1 四维加权公式

```
总分 = W1 × 匹配度 + W2 × 传播力 + W3 × 带货力 + W4 × 性价比
       (默认权重: 0.35, 0.25, 0.25, 0.15)
```

| 维度 | 计算方式 | 数据来源 |
|------|---------|---------|
| **匹配度** | 类目重合度 × 粉丝画像契合度 × 历史品牌调性相似度 | 达人画像 + 品牌需求 |
| **传播力** | 粉丝量归一化 × 互动率 × 内容质量标签得分 | 平台数据 |
| **带货力** | GMV归一化 × 转化率 × 场均销量 | 平台数据 |
| **性价比** | 预估ROI = (场均GMV × 预估转化) / 报价 | 报价 + 历史GMV |

### 4.2 评分自优化机制

```
品牌方提交反馈(1-5星+评价)
  → 写入 feedbacks 表
  → 调用 scoring.py 更新维度得分
  → 对比预测分 vs 实际反馈分
  → 偏差 > 阈值 → 按维度贡献度反向微调权重（梯度下降简化版）
  → 更新 influencer_scores.score + confidence
  → version++ 标记变更
```

权重调整只对满足 `confidence >= 0.6` 的达人进行（数据量够大才可信）。反馈越多，confidence 单调递增，权重逐渐收敛。

---

## 5. Agent 协作流程

### 5.1 总体架构

**1 个 Lead Agent + 4 个专业 SubAgent 并行协作**

Lead Agent 负责任务编排、需求理解、结果汇总和用户交互。SubAgent 各司其职，按维度独立分析，结果由 Lead Agent 组合汇总。

### 5.2 专业 SubAgent 定义

| SubAgent | 类型 | 核心能力 | 输出格式 |
|----------|------|---------|---------|
| 粉丝画像分析师 | general-purpose + 专属 prompt | 读取粉丝画像JSON + LLM语义分析客群匹配度 | 每位达人 0-100分 + 3点理由 |
| 内容风格分析师 | general-purpose + 专属 prompt | 分析内容标签/风格描述 + 品牌调性语义匹配 | 每位达人 0-100分 + 3点理由 |
| 商业表现分析师 | general-purpose + 专属 prompt | 数值计算(GMV/ROI/转化) + LLM综合评估 | 每位达人 0-100分 + 数据支撑 |
| 风险合规扫描师 | bash 工具增强 | 联网搜索负面信息 + 数据异常检测(假粉/水军) | 风险等级 + 明细列表 |

### 5.3 五阶段流程

**阶段一：需求理解与结构化** (Lead Agent)
- ask_clarification 补充不清晰的筛选条件
- 自然语言转结构化 criteria
- 创建选人任务，写入 selection.goal

**阶段二：达人搜索与初筛** (Lead Agent + Tools)
- search_influencers(criteria) → 调用 data_platform API
- scoring.match_batch() 四维评分排序
- 输出 Top 15 候选列表给用户

**阶段三：专业化并行分析** (3 SubAgent 并行 + 1 后续)
```
t=0    并行启动:
       SubAgent-1 (粉丝画像分析) ─→ 6-9位达人粉丝契合分
       SubAgent-2 (内容风格分析) ─→ 6-9位达人内容契合分
       SubAgent-3 (商业表现分析) ─→ 6-9位达人商业价值分

t=~8s  三者中最快完成者 → SubAgent-4 (风险合规扫描) 立即启动
       分析全部候选人风险等级

t=~12s 全部完成 → Lead Agent 汇总
```

**阶段四：总分汇总与推荐报告** (Lead Agent + 可选 SubAgent)
- scoring.aggregate() 四维加权汇总
- compare_influencers(top_n) 横向对比表
- recommend_report(selection_id) AI 推荐报告（可下载为 Markdown/PDF）

**阶段五：确认与闭环** (Lead Agent + Tools)
- record_feedback(selection_id, influencer_id, rating, review)
- feedback.py → 更新评分权重 → influencer_scores 更新

### 5.4 SubAgent 降级策略

| 场景 | 降级行为 |
|------|---------|
| 某 SubAgent 超时 | 该维度标记"不可用"，总分用剩余维度计算 |
| 风险扫描无结果 | 风险标记"未评估"，不做扣分 |
| 全部 SubAgent 失败 | 降级为纯数值对比，无 AI 分析理由 |
| Data Platform API 不可用 | 降级到 MockAdapter 或缓存数据 |

核心原则：**宁可出少维度的结果，也不让用户白等或收空白页**。

---

## 6. API 设计

所有路由挂载在 `/api/influencer` 下，复用 DeerFlow Gateway 认证和中间件。REST API 和 Agent Tool 共享同一 Service 层。

### 6.1 达人管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/influencer/search` | 搜索达人（类目/粉丝区间/互动率/报价） |
| `GET` | `/api/influencer/{id}` | 达人详情+完整画像 |
| `GET` | `/api/influencer/{id}/history` | 达人历史合作记录 |

### 6.2 选人任务

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/influencer/selections` | 创建选人任务 |
| `GET` | `/api/influencer/selections` | 任务列表（分页+状态筛选） |
| `GET` | `/api/influencer/selections/{id}` | 任务详情（含候选人+分数） |
| `PUT` | `/api/influencer/selections/{id}` | 更新筛选条件/状态 |
| `POST` | `/api/influencer/selections/{id}/candidates` | 手动添加候选人 |
| `DELETE` | `/api/influencer/selections/{id}/candidates/{cid}` | 移除候选人 |
| `PATCH` | `/api/influencer/selections/{id}/candidates/{cid}` | 更新候选状态 |
| `GET` | `/api/influencer/selections/{id}/report` | 获取/重新生成推荐报告 |
| `GET` | `/api/influencer/selections/{id}/compare` | 横向对比数据 |

### 6.3 分析与评分

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/influencer/scores/{id}` | 达人评分明细（四维度+总分） |
| `POST` | `/api/influencer/scores/batch` | 批量计算/刷新评分 |
| `GET` | `/api/influencer/analytics/weights` | 当前权重配置 |
| `GET` | `/api/influencer/analytics/trends` | 评分趋势/模型效果统计 |

### 6.4 反馈闭环

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/influencer/feedbacks` | 提交合作反馈 |
| `GET` | `/api/influencer/feedbacks` | 反馈列表（按达人/按任务筛选） |
| `GET` | `/api/influencer/feedbacks/{id}` | 反馈详情 |
| `GET` | `/api/influencer/feedbacks/stats` | 反馈统计（评分分布/趋势） |

### 6.5 数据平台

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/influencer/platforms` | 已接入平台列表+状态 |
| `POST` | `/api/influencer/platforms/sync` | 手动触发数据同步 |
| `GET` | `/api/influencer/platforms/sync/status` | 同步任务状态（预留定时任务） |

---

## 7. 数据平台适配器

### 7.1 抽象基类

```python
class DataPlatformAdapter(ABC):
    """第三方数据平台统一适配接口"""

    @property
    @abstractmethod
    def platform_name(self) -> str: ...

    @abstractmethod
    async def search_influencers(self, criteria: SearchCriteria) -> list[InfluencerDTO]: ...

    @abstractmethod
    async def get_influencer_detail(self, platform_uid: str) -> InfluencerDTO: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

### 7.2 实现矩阵

| | MockAdapter | DouyinAdapter | (预留) KuaishouAdapter |
|---|---|---|---|
| 数据源 | 内置 150 条模拟数据 | 蝉妈妈/飞瓜 API | - |
| search | 本地内存查询 | HTTP → 平台 API → 字段映射 | - |
| detail | 直接返回 | HTTP → 平台 API → 归一化 | - |
| 限流 | 无 | Token Bucket 10次/秒 | - |
| 容错 | 无 | 超时5s → 重试1次 → 降级标记 | - |

### 7.3 配置

```yaml
# config.yaml 新增
influencer:
  data_platform:
    provider: mock           # mock | douyin
    douyin:
      api_base: "https://api.chanmama.com"
      api_key: "$CHANMAMA_API_KEY"
      timeout: 10
      rate_limit: 10
```

---

## 8. 前端设计

### 8.1 路由

```
/workspace/influencer/          达人广场 - 搜索浏览
/workspace/influencer/[id]/     达人详情页
/workspace/influencer/selections/        选人任务列表
/workspace/influencer/selections/[id]/   任务详情（候选人+对比）
/workspace/influencer/analytics/         反馈统计 + 评分趋势看板
```

### 8.2 核心组件

| 组件 | 用途 |
|------|------|
| FilterPanel | 结构化筛选面板（类目/粉丝区间/互动率/报价），防抖300ms |
| SearchBar | 自然语言搜索入口，对接对话模式 |
| InfluencerCard | 达人卡片（头像+平台标识+综合评分+关键数字） |
| InfluencerDetail | 达人详情（四维雷达图+粉丝画像分布图+风格标签云+历史合作时间线） |
| CandidateTable | 候选人排序列表（四维分数列+可排序+状态变更） |
| CompareDrawer | 横向对比抽屉（多人雷达图叠加+指标逐行对比表） |
| ReportCard | AI 推荐报告（Markdown 渲染+下载） |
| FeedbackForm | 星级评分+评价标签+文字评价 |
| InfluencerSearchResultMsg | 聊天内达人搜索结果卡片 |
| CompareTableMsg | 聊天内对比表消息 |
| ReportArtifactMsg | 聊天内报告 Artifact 消息 |

### 8.3 消息类型识别

聊天页面通过 `additional_kwargs.type` 识别达人相关消息：

| type | 组件 | 来源 |
|------|------|------|
| `influencer:search_result` | InfluencerSearchResultMsg | search_influencers tool |
| `influencer:compare` | CompareTableMsg | compare_influencers tool |
| `influencer:report` | ReportArtifactMsg | recommend_report tool |

---

## 9. 错误处理

### 9.1 分层策略

| 层 | 策略 |
|----|------|
| **前端** | Toast 中文错误提示；组件级 Loading/Skeleton/Error；搜索失败提示切对话模式 |
| **API Router** | 参数校验 → 422；资源不存在 → 404；业务异常 → 400 + error_code；未知异常 → 500 + trace_id |
| **Service** | DataPlatformError → 降级缓存/mock；MatchingError → 返回部分结果；ScoringError → 使用历史分数 |
| **Agent SubAgent** | 超时 → 该维度标记不可用；全失败 → 降级纯数值对比 |

### 9.2 SubAgent 降级

一条核心原则：**宁可出少维度的结果，也不让用户白等或收空白页**。

---

## 10. 测试策略

### 10.1 后端

| 层级 | 内容 | 工具 | 目标覆盖率 |
|------|------|------|-----------|
| Unit | 数据模型、scoring计算、feedback权重更新 | pytest | ≥90% |
| Service | matching/mock adapter/CRUD | pytest + fixtures | ≥80% |
| API | 路由参数校验、响应格式、错误码 | pytest + httpx | ≥80% |
| Agent Tool | search/compare/report 工具调用 | pytest + mock agent | ≥70% |
| 集成 | 完整选人流程 end-to-end | pytest + 测试DB | 核心路径全覆盖 |

### 10.2 前端

| 层级 | 内容 | 工具 |
|------|------|------|
| Unit | hooks 逻辑、类型守卫、API 请求串 | Rstest |
| Component | 组件交互行为 | Rstest + React Testing Library |
| E2E | 搜索→筛选→对比→反馈 完整流程 | Playwright |

### 10.3 关键测试用例

- scoring: 四维打分正确性、权重微调方向验证、边界值 (0粉丝/0GMV/空标签)
- data_platform: MockAdapter 与真实 Adapter 输出格式一致性
- Agent Tool: 空结果时 Agent 建议合理性
- SubAgent: 超时后 Lead Agent 汇总完整性
- feedback 闭环: 评分写入后 influencer_scores 更新、权重收敛验证
- confidence: 随数据量单调递增

---

## 11. 里程碑

### Phase 1: 核心骨架（MVP）
- [ ] 数据库模型 + Alembic 迁移
- [ ] MockDataAdapter + 150 条模拟数据
- [ ] 达人搜索/详情 API
- [ ] 达人广场页面 + 筛选面板 + 达人卡片

### Phase 2: 选人流程
- [ ] 选人任务 CRUD API
- [ ] 评分模型 + 匹配引擎
- [ ] 任务详情页 + 候选人列表 + 对比抽屉
- [ ] Agent Tools (search/compare/recommend)

### Phase 3: Agent 协作
- [ ] 4 个专业 SubAgent 定义 (粉丝/内容/商业/风险)
- [ ] Lead Agent 五阶段编排逻辑
- [ ] SubAgent 并行调度 + 降级处理
- [ ] 推荐报告生成 + Artifact 渲染

### Phase 4: 反馈闭环
- [ ] 反馈 API + 前端表单
- [ ] 评分自优化 (权重微调)
- [ ] 反馈统计/趋势看板
- [ ] feedbacks 表的 sales_performance 字段（预留自动回传扩展点）

### Phase 5: 真实平台对接
- [ ] DouyinAdapter 实现
- [ ] Token Bucket 限流
- [ ] 数据同步定时任务
- [ ] 平台切换配置

### Phase 6: 体验打磨
- [ ] E2E 测试覆盖
- [ ] 错误处理 + 降级完善
- [ ] 移动端适配
- [ ] 性能优化

---

## 12. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 架构模式 | DeerFlow 模块内嵌 | 复用基础设施，面试展示"二开+独立设计"双重能力 |
| SubAgent 拆分方式 | 按分析维度拆分 | 同一维度同一裁判，评分可比；独立降级不影响整体 |
| 数据源策略 | 第三方 API 为主 + Mock 为辅 | Mock 保底开发演示，API 打通后无缝切换 |
| 交互方式 | 表单 + 对话混合 | 表单快筛 + AI 深度分析，覆盖两种使用习惯 |
| 反馈机制 | A 方案为主（手动评分），预留 B 方案 | 先做闭环跑通，sales_performance 字段预留自动回传 |
| 平台范围 | 多平台架构，先接入抖音 | 架构提前预留扩展点，实现分阶段聚焦 |
