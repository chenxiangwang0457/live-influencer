# backend/packages/harness/deerflow/tools/influencer/compare_influencers.py
"""Agent tool for side-by-side comparison of multiple influencers.

Uses the factory pattern: ``build_compare_influencers_tool(adapter)`` receives
the app-layer data adapter and returns a LangChain tool. The harness layer never
imports from ``app.*``.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

_MAX_COMPARE = 6


def build_compare_influencers_tool(
    adapter: Any,  # DataPlatformAdapter
):
    """Factory: receives app-layer data adapter, returns a LangChain tool.

    Args:
        adapter: A ``DataPlatformAdapter`` implementation for fetching influencer details.

    Returns:
        An async LangChain ``@tool`` that compares influencers side-by-side.
    """

    @tool
    async def compare_influencers(platform_uids_json: str) -> str:
        """Compare multiple influencers side-by-side. Returns comparison data as JSON.

        Fetches detailed profiles for up to 6 influencers and returns a
        side-by-side comparison table with key metrics.

        Args:
            platform_uids_json: JSON array of platform UID strings (max 6).
              Example: '["mock_dy_0001", "mock_dy_0042", "mock_dy_0087"]'

        Returns:
            JSON string with:
              - compared: array of {platform_uid, nickname, category, followers_count,
                engagement_rate, avg_gmv, price_range_min, price_range_max,
                content_style}
              - errors: array of UIDs that could not be found
        """
        try:
            uids = json.loads(platform_uids_json)
        except json.JSONDecodeError as exc:
            return json.dumps(
                {"error": f"Invalid JSON: {exc}", "compared": [], "errors": []},
                ensure_ascii=False,
            )

        if not isinstance(uids, list):
            return json.dumps(
                {"error": "platform_uids_json must be a JSON array", "compared": [], "errors": []},
                ensure_ascii=False,
            )

        # Cap at max
        uids = uids[:_MAX_COMPARE]

        if not uids:
            return json.dumps(
                {"compared": [], "errors": []},
                ensure_ascii=False,
            )

        compared = []
        errors = []

        for uid in uids:
            detail = await adapter.get_influencer_detail(str(uid))
            if detail is None:
                errors.append(str(uid))
                continue
            compared.append({
                "platform_uid": detail.platform_uid,
                "nickname": detail.nickname,
                "category": detail.category,
                "followers_count": detail.followers_count,
                "engagement_rate": detail.engagement_rate,
                "avg_gmv": detail.avg_gmv,
                "price_range_min": detail.price_range_min,
                "price_range_max": detail.price_range_max,
                "content_style": detail.content_style,
            })

        return json.dumps(
            {"compared": compared, "errors": errors},
            ensure_ascii=False,
        )

    return compare_influencers
