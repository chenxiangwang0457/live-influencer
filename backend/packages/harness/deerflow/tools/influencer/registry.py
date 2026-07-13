# backend/packages/harness/deerflow/tools/influencer/registry.py
"""Simple registry for influencer tools.

The app layer creates tool instances via the factory functions and
registers them here. The agent factory picks them up when assembling
the tool list. This keeps the harness/app boundary clean: the harness
layer defines the registry; the app layer populates it.
"""
from __future__ import annotations

from langchain.tools import BaseTool

_influencer_tools: list[BaseTool] = []


def register_influencer_tools(tools: list[BaseTool]) -> None:
    """Register influencer tool instances from the app layer."""
    _influencer_tools.clear()
    _influencer_tools.extend(tools)


def get_influencer_tools() -> list[BaseTool]:
    """Return a copy of the registered influencer tools."""
    return list(_influencer_tools)
