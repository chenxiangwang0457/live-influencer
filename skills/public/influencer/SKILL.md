---
name: influencer-selection
description: 直播带货达人智能筛选 — 搜索、分析、对比、推荐达人
allowed-tools:
  - search_influencers
  - compare_influencers
  - recommend_report
  - record_feedback
  - read_file
  - write_file
  - task
license: MIT
---

# 达人智能筛选

## When to Use
- 品牌方需要找直播带货达人
- 需要对比分析多位达人
- 需要生成达人推荐报告

## Workflow (MUST follow this order)
1. 理解需求 — 确认类目/粉丝/预算/转化要求
2. 搜索初筛 — search_influencers → 获取得分排序的候选人
3. 并行分析 — 对 Top 6 候选人同时派遣 fan-analyst / content-analyst / commercial-analyst（最多3个并行）
4. 风险扫描 — 任一 analyst 完成后立即派遣 risk-scanner
5. 对比报告 — compare_influencers + recommend_report
6. 确认闭环 — 呈现结果，等待用户决策，保存到选人任务

## Fallback Rules (MUST apply)
- SubAgent timeout (>30s): 标记该维度"暂不可用"，用剩余维度计算总分
- Risk scan no result: 标记"未评估"，不扣分
- ALL subagents fail: 降级为纯数据对比
- Search empty: 提示放宽条件
