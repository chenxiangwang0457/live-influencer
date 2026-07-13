"""Content style analyst subagent for influencer selection."""

from deerflow.subagents.config import SubagentConfig

CONTENT_ANALYST_SYSTEM_PROMPT = """你是一位**直播电商内容风格分析师**。分析达人内容调性与品牌形象的匹配度。

<scoring>
0-100 分：80+ 高度契合 / 60-79 风格接近 / 40-59 存在偏差 / 20-39 差异较大 / 0-19 完全不匹配
</scoring>

<output_format>
JSON 数组: [{"platform_uid":"...", "content_score":82, "style_tags":["标签"], "reasons":["..."], "suggestion":"合作建议"}]
</output_format>"""

CONTENT_ANALYST_CONFIG = SubagentConfig(
    name="content-analyst",
    description="内容风格分析专家 — 分析达人内容风格与品牌调性匹配度。输出 0-100 内容契合分 + 风格标签 + 合作建议。",
    system_prompt=CONTENT_ANALYST_SYSTEM_PROMPT,
    tools=["read_file", "bash"],
    max_turns=15,
    timeout_seconds=300,
)
