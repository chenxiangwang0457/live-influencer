"""Built-in subagent configurations."""

from .bash_agent import BASH_AGENT_CONFIG
from .commercial_analyst import COMMERCIAL_ANALYST_CONFIG
from .content_analyst import CONTENT_ANALYST_CONFIG
from .fan_analyst import FAN_ANALYST_CONFIG
from .general_purpose import GENERAL_PURPOSE_CONFIG
from .risk_scanner import RISK_SCANNER_CONFIG

__all__ = [
    "BASH_AGENT_CONFIG",
    "COMMERCIAL_ANALYST_CONFIG",
    "CONTENT_ANALYST_CONFIG",
    "FAN_ANALYST_CONFIG",
    "GENERAL_PURPOSE_CONFIG",
    "RISK_SCANNER_CONFIG",
]

# Registry of built-in subagents
BUILTIN_SUBAGENTS = {
    "general-purpose": GENERAL_PURPOSE_CONFIG,
    "bash": BASH_AGENT_CONFIG,
    "fan-analyst": FAN_ANALYST_CONFIG,
    "content-analyst": CONTENT_ANALYST_CONFIG,
    "commercial-analyst": COMMERCIAL_ANALYST_CONFIG,
    "risk-scanner": RISK_SCANNER_CONFIG,
}
