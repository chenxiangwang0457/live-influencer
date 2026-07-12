# backend/packages/harness/deerflow/tools/influencer/search_influencers.py
"""Agent tool for searching influencers and returning scored match results.

Uses the factory pattern: ``build_search_influencers_tool(adapter, engine)``
receives app-layer dependencies and returns a LangChain tool. The harness layer
never imports from ``app.*`` — criteria construction uses ``SimpleNamespace`` with
explicit defaults mirroring the app-layer ``SearchCriteria`` contract.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from langchain_core.tools import tool

# ── Defaults mirroring app.influencer.services.data_platform.base.SearchCriteria ──

_CRITERIA_DEFAULTS: dict[str, Any] = {
    "keyword": None,
    "platform": "douyin",
    "category": None,
    "follower_min": None,
    "follower_max": None,
    "engagement_min": None,
    "engagement_max": None,
    "price_min": None,
    "price_max": None,
    "gmv_min": None,
    "sort_by": "followers_count",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20,
}


def _build_criteria(criteria_dict: dict[str, Any]) -> SimpleNamespace:
    """Build a criteria object from a dict, applying defaults for missing fields.

    Returns a ``SimpleNamespace`` with attribute access so it behaves like the
    app-layer ``SearchCriteria`` Pydantic model without importing from ``app.*``.
    """
    merged = {**_CRITERIA_DEFAULTS, **criteria_dict}
    return SimpleNamespace(**merged)


def build_search_influencers_tool(
    adapter: Any,  # DataPlatformAdapter
    engine: Any,  # MatchingEngine
):
    """Factory: receives app-layer deps, returns a LangChain tool.

    Args:
        adapter: A ``DataPlatformAdapter`` implementation for searching influencers.
        engine: A ``MatchingEngine`` implementation for scoring results.

    Returns:
        An async LangChain ``@tool`` that searches and scores influencers.
    """

    @tool
    async def search_influencers(criteria_json: str) -> str:
        """Search for influencers matching criteria. Returns scored results as JSON.

        Searches the influencer data platform for profiles matching the given
        criteria, then scores each result using the matching engine. Returns
        the top 10 matches sorted by total score descending.

        Args:
            criteria_json: JSON string with search criteria fields:
              {keyword, category, follower_min, follower_max, engagement_min,
               engagement_max, price_min, price_max, gmv_min, sort_by, sort_order,
               platform, page, page_size}

        Returns:
            JSON string with:
              - results: array of top 10 {nickname, platform_uid, category,
                followers_count, engagement_rate, avg_gmv, price_range_max,
                match_score, reach_score, sales_score, value_score, total_score}
              - total_count: total number of matching influencers before scoring
        """
        try:
            criteria_dict = json.loads(criteria_json)
        except json.JSONDecodeError as exc:
            return json.dumps(
                {"error": f"Invalid JSON: {exc}", "results": [], "total_count": 0},
                ensure_ascii=False,
            )

        if not isinstance(criteria_dict, dict):
            return json.dumps(
                {"error": "criteria_json must be a JSON object", "results": [], "total_count": 0},
                ensure_ascii=False,
            )

        criteria = _build_criteria(criteria_dict)
        results, total = await adapter.search_influencers(criteria)

        if not results:
            return json.dumps(
                {"results": [], "total_count": 0},
                ensure_ascii=False,
            )

        # Score results using the matching engine
        scored = engine.match_batch(results, criteria_dict)

        # Return top 10
        top10 = scored[:10]
        output = []
        for r in top10:
            inf = r.influencer
            output.append({
                "nickname": inf.nickname,
                "platform_uid": inf.platform_uid,
                "category": inf.category,
                "followers_count": inf.followers_count,
                "engagement_rate": inf.engagement_rate,
                "avg_gmv": inf.avg_gmv,
                "price_range_max": inf.price_range_max,
                "match_score": r.match_score,
                "reach_score": r.reach_score,
                "sales_score": r.sales_score,
                "value_score": r.value_score,
                "total_score": r.total_score,
            })

        return json.dumps(
            {"results": output, "total_count": total},
            ensure_ascii=False,
        )

    return search_influencers
