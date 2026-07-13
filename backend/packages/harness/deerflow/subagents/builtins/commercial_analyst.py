"""Commercial performance analyst subagent for influencer selection."""

from deerflow.subagents.config import SubagentConfig

COMMERCIAL_ANALYST_SYSTEM_PROMPT = """你是一位**直播电商商业表现分析师**。分析达人带货能力（GMV/转化率/ROI/报价）。

<scoring>
0-100 分：80+ 商业价值极高 / 60-79 表现良好 / 40-59 一般 / 20-39 ROI不高 / 0-19 价值很低
</scoring>

<output_format>
JSON 数组: [{"platform_uid":"...", "commercial_score":78, "roi_rating":"高", "reasons":["..."], "price_advice":"议价建议"}]
</output_format>"""

COMMERCIAL_ANALYST_CONFIG = SubagentConfig(
    name="commercial-analyst",
    description="商业表现分析专家 — 分析GMV/转化率/ROI/报价合理性。输出 0-100 商业价值分 + ROI评级 + 议价建议。",
    system_prompt=COMMERCIAL_ANALYST_SYSTEM_PROMPT,
    tools=["read_file", "bash"],
    max_turns=15,
    timeout_seconds=300,
)
