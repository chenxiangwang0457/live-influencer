# backend/packages/harness/deerflow/tools/influencer/recommend_report.py
"""Agent tool for generating a Markdown-formatted influencer recommendation report.

Uses the factory pattern: ``build_recommend_report_tool(engine)`` receives the
scoring engine (for weight metadata) and returns a LangChain tool. This is a pure
text-formatting tool — it performs no external calls.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool


def _format_price(price_min: int | None, price_max: int | None) -> str:
    """Format a price range for display."""
    if price_min and price_max:
        if price_min >= 10000:
            return f"{price_min // 10000}万 - {price_max // 10000}万"
        return f"{price_min:,} - {price_max:,}"
    if price_max:
        return f"最高 {price_max:,}"
    return "未公开"


def _format_score(score: float) -> str:
    """Format a score for display."""
    return f"{score:.1f}"


def build_recommend_report_tool(
    engine: Any = None,  # MatchingEngine
):
    """Factory: receives scoring engine, returns a LangChain tool.

    Args:
        engine: A ``MatchingEngine`` instance (unused in report generation;
            accepted for consistency with the factory pattern).

    Returns:
        An async LangChain ``@tool`` that generates a Markdown recommendation report.
    """

    @tool
    async def recommend_report(selection_json: str) -> str:
        """Generate a Markdown-formatted influencer recommendation report.

        Takes a JSON selection payload with criteria and ranked picks,
        and produces a human-readable Markdown report summarizing the top
        recommendations with reasoning and suggested next steps.

        This is a pure text tool — no external API calls are made.

        Args:
            selection_json: JSON string with:
              - criteria: dict with search criteria used (category, follower range,
                engagement range, price range, gmv_min, etc.)
              - picks: array of {platform_uid, nickname, score, reason}
                (at least 1 entry)

        Returns:
            Markdown-formatted recommendation report as a string.
        """
        try:
            data = json.loads(selection_json)
        except json.JSONDecodeError as exc:
            return f"**Error**: Invalid JSON input — {exc}"

        if not isinstance(data, dict):
            return "**Error**: Input must be a JSON object with 'criteria' and 'picks' fields."

        criteria = data.get("criteria", {})
        picks = data.get("picks", [])

        if not isinstance(picks, list) or len(picks) == 0:
            return "**Error**: 'picks' must be a non-empty array."

        # ── Build report ──

        lines: list[str] = []

        lines.append("# 达人推荐报告")
        lines.append("")
        lines.append("## 一、筛选条件")
        lines.append("")

        cat = criteria.get("category", "不限")
        lines.append(f"- **主营类目**: {cat}")

        f_min = criteria.get("follower_min")
        f_max = criteria.get("follower_max")
        if f_min or f_max:
            f_range = f"{f_min or '不限'} - {f_max or '不限'}"
            lines.append(f"- **粉丝量**: {f_range}")

        e_min = criteria.get("engagement_min")
        e_max = criteria.get("engagement_max")
        if e_min or e_max:
            e_range = f"{e_min or '不限'}% - {e_max or '不限'}%"
            lines.append(f"- **互动率**: {e_range}")

        p_min = criteria.get("price_min")
        p_max = criteria.get("price_max")
        if p_min or p_max:
            lines.append(f"- **报价范围**: {p_min or '不限'} - {p_max or '不限'}")

        gmv = criteria.get("gmv_min")
        if gmv:
            lines.append(f"- **最低场均GMV**: {gmv}")

        kw = criteria.get("keyword")
        if kw:
            lines.append(f"- **关键词**: {kw}")

        lines.append("")
        lines.append("## 二、推荐达人 Top {count}".format(count=len(picks)))
        lines.append("")

        for i, pick in enumerate(picks, 1):
            nickname = pick.get("nickname", pick.get("platform_uid", f"达人{i}"))
            platform_uid = pick.get("platform_uid", "N/A")
            score = pick.get("score", pick.get("total_score", pick.get("match_score", 0)))
            reason = pick.get("reason", pick.get("match_reason", "综合匹配"))

            lines.append(f"### {i}. {nickname}")
            lines.append("")
            lines.append(f"- **平台UID**: `{platform_uid}`")
            lines.append(f"- **综合得分**: {_format_score(float(score))}/100")
            lines.append(f"- **推荐理由**: {reason}")
            lines.append("")

        lines.append("## 三、综合分析与建议")
        lines.append("")

        # Category-focused commentary
        if cat and cat != "不限":
            lines.append(f"以上达人主营类目均为 **{cat}**，与品牌需求高度契合。")
        else:
            lines.append("以上达人覆盖多个类目，建议结合品牌定位做进一步筛选。")

        lines.append("")

        # Score-based commentary
        if picks:
            avg_score = sum(float(p.get("score", p.get("total_score", p.get("match_score", 0)))) for p in picks) / len(picks)
            if avg_score >= 75:
                lines.append(f"推荐达人的平均综合得分为 {avg_score:.1f}/100，整体匹配度较高，建议优先联系得分排名前 3 的达人。")
            elif avg_score >= 50:
                lines.append(f"推荐达人的平均综合得分为 {avg_score:.1f}/100，匹配度中等，建议结合具体传播力和性价比进一步筛选。")
            else:
                lines.append(f"推荐达人的平均综合得分为 {avg_score:.1f}/100，匹配度偏低，建议拓宽筛选条件或调整预期。")

        lines.append("")
        lines.append("## 四、下一步行动建议")
        lines.append("")
        lines.append("1. **优先联系 Top 3 达人**: 通过平台私信或商务渠道建立初步联系")
        lines.append("2. **索要详细刊例**: 获取最新的报价单、档期安排和合作案例")
        lines.append("3. **安排样品寄送**: 选定意向达人后，寄送产品样品进行体验")
        lines.append("4. **制定Brief**: 根据达人内容风格，撰写合作Brief和内容方向")
        lines.append("5. **签订合作协议**: 明确交付物、排期、保价、数据要求等条款")

        return "\n".join(lines)

    return recommend_report
