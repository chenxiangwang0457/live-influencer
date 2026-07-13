"""Code-level fallback for influencer subagent analysis.

When subagent calls fail or timeout, these functions provide deterministic
fallback scores and status markers so the Lead Agent always has data to work with.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FallbackResult:
    """Holds fallback scores and status for each analysis dimension.

    Attributes:
        fan_score: Fallback fan demographic score (0-100).
        fan_status: ``ok`` or ``unavailable``.
        content_score: Fallback content style score (0-100).
        content_status: ``ok`` or ``unavailable``.
        commercial_score: Fallback commercial performance score (0-100).
        commercial_status: ``ok`` or ``unavailable``.
        risk_level: Risk assessment result. Defaults to ``"未评估"``.
        risk_status: ``ok`` or ``unavailable``. Defaults to ``"unavailable"``.
        all_failed: True when all three primary dimensions (fan, content, commercial)
            are unavailable.
    """

    fan_score: float = 50.0
    fan_status: str = "ok"
    content_score: float = 50.0
    content_status: str = "ok"
    commercial_score: float = 50.0
    commercial_status: str = "ok"
    risk_level: str = "未评估"
    risk_status: str = "unavailable"
    all_failed: bool = False


def build_fallback_result(
    fan_ok: bool = True,
    content_ok: bool = True,
    commercial_ok: bool = True,
    risk_ok: bool = False,
) -> FallbackResult:
    """Build a FallbackResult marking which dimensions succeeded.

    Args:
        fan_ok: Whether the fan-analyst subagent returned a result.
        content_ok: Whether the content-analyst subagent returned a result.
        commercial_ok: Whether the commercial-analyst subagent returned a result.
        risk_ok: Whether the risk-scanner subagent returned a result.

    Returns:
        A FallbackResult with status flags set and ``all_failed`` computed.
    """
    result = FallbackResult()
    if not fan_ok:
        result.fan_status = "unavailable"
    if not content_ok:
        result.content_status = "unavailable"
    if not commercial_ok:
        result.commercial_status = "unavailable"
    result.risk_status = "ok" if risk_ok else "unavailable"
    result.all_failed = not any([fan_ok, content_ok, commercial_ok])
    return result


def format_fallback_summary(result: FallbackResult) -> str:
    """Generate a human-readable summary of fallback status.

    Args:
        result: A FallbackResult produced by :func:`build_fallback_result`.

    Returns:
        A markdown-formatted string describing which dimensions are
        unavailable. Returns an empty string when all dimensions are ok.
    """
    parts: list[str] = []
    for _dim, status, label in [
        ("fan", result.fan_status, "粉丝画像"),
        ("content", result.content_status, "内容风格"),
        ("commercial", result.commercial_status, "商业表现"),
        ("risk", result.risk_status, "风险合规"),
    ]:
        if status == "unavailable":
            parts.append(f"- {label}: 暂不可用")

    if result.all_failed:
        return "所有分析维度暂不可用，以下为纯数据对比结果。\n" + "\n".join(parts)
    if parts:
        return "部分分析维度暂不可用：\n" + "\n".join(parts)
    return ""
