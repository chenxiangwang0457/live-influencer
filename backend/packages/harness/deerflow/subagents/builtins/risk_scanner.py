"""Risk compliance scanner subagent for influencer selection."""

from deerflow.subagents.config import SubagentConfig

RISK_SCANNER_SYSTEM_PROMPT = """你是一位**达人风险合规扫描师**。排查达人合作风险（粉丝质量/负面舆情/品牌安全/平台违规）。

<risk_levels>
🟢 低风险 / 🟡 中风险（需核实）/ 🔴 高风险（建议放弃）
</risk_levels>

<output_format>
JSON 数组: [{"platform_uid":"...", "risk_level":"🟢", "risk_details":[], "verification_advice":null}]
</output_format>"""

RISK_SCANNER_CONFIG = SubagentConfig(
    name="risk-scanner",
    description="风险合规扫描专家 — 排查粉丝质量/负面舆情/品牌安全。输出 🟢🟡🔴 风险等级 + 明细 + 核实建议。",
    system_prompt=RISK_SCANNER_SYSTEM_PROMPT,
    tools=["read_file", "bash"],
    max_turns=20,
    timeout_seconds=600,
)
