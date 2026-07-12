# backend/packages/harness/deerflow/tools/influencer/__init__.py
"""Influencer selection tools for the Live-Influencer MVP.

Each tool follows the **factory pattern**: a ``build_*_tool(...)`` function
receives app-layer dependencies (adapter, engine) and returns a LangChain
``@tool``. The harness layer never imports from ``app.*``.

Exports:
    build_search_influencers_tool:  Factory for the search + score tool.
    build_compare_influencers_tool: Factory for the side-by-side comparison tool.
    build_recommend_report_tool:    Factory for the Markdown report tool.
"""

from __future__ import annotations

from deerflow.tools.influencer.compare_influencers import build_compare_influencers_tool
from deerflow.tools.influencer.recommend_report import build_recommend_report_tool
from deerflow.tools.influencer.search_influencers import build_search_influencers_tool

__all__ = [
    "build_search_influencers_tool",
    "build_compare_influencers_tool",
    "build_recommend_report_tool",
]
