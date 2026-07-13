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
license: MIT
---

# 达人智能筛选

## When to Use
- 品牌方需要找直播带货达人
- 需要对比分析多位达人
- 需要生成达人推荐报告

## Workflow
1. 理解品牌需求（类目、预算、粉丝量级、转化要求）
2. 使用 search_influencers 搜索候选人
3. 为 Top 候选人派遣专业分析 subagent（fan-analyst/content-analyst/commercial-analyst/risk-scanner）
4. 使用 compare_influencers 横向对比
5. 使用 recommend_report 生成推荐报告
6. 合作完成后使用 record_feedback 记录反馈
