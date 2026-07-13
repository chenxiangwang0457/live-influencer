# backend/packages/harness/deerflow/tools/influencer/record_feedback.py
"""Agent tool for recording collaboration feedback.

Uses the factory pattern: ``build_record_feedback_tool(base_url)`` receives
the Gateway base URL and returns a LangChain tool. The harness layer never
imports from ``app.*``.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool


def build_record_feedback_tool(
    base_url: str = "http://localhost:8001",
):
    """Factory: receives Gateway base URL, returns a LangChain tool.

    Args:
        base_url: Base URL of the Gateway API (default: http://localhost:8001).

    Returns:
        An async LangChain ``@tool`` that records collaboration feedback.
    """

    @tool
    async def record_feedback(feedback_json: str) -> str:
        """Record collaboration feedback for an influencer after campaign completion.

        Submits a rating and review for an influencer collaboration. Optionally
        links it to a specific selection task.

        Args:
            feedback_json: JSON string with:
              - influencer_id (required): Platform UID or DB id of the influencer
              - rating (required): 1-5 star rating
              - review (optional): Text review of the collaboration
              - tags (optional): Array of tag strings
              - selection_id (optional): ID of the selection task this feedback relates to

        Returns:
            JSON string with {id, score_updated, weights_adjusted?}
        """
        import httpx

        try:
            data = json.loads(feedback_json)
        except json.JSONDecodeError as exc:
            return json.dumps(
                {"error": f"Invalid JSON: {exc}"},
                ensure_ascii=False,
            )

        if not isinstance(data, dict):
            return json.dumps(
                {"error": "feedback_json must be a JSON object"},
                ensure_ascii=False,
            )

        influencer_id = data.get("influencer_id")
        rating = data.get("rating")

        if not influencer_id:
            return json.dumps(
                {"error": "influencer_id is required"},
                ensure_ascii=False,
            )
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return json.dumps(
                {"error": "rating must be an integer between 1 and 5"},
                ensure_ascii=False,
            )

        payload: dict[str, Any] = {
            "influencer_id": str(influencer_id),
            "rating": int(rating),
        }
        if data.get("review"):
            payload["review"] = str(data["review"])
        if data.get("tags"):
            payload["tags"] = [str(t) for t in data["tags"]]
        if data.get("selection_id"):
            payload["selection_id"] = str(data["selection_id"])

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{base_url.rstrip('/')}/api/influencer/feedbacks",
                    json=payload,
                )
                resp.raise_for_status()
                result = resp.json()
        except httpx.HTTPStatusError as exc:
            return json.dumps(
                {"error": f"Feedback API returned {exc.response.status_code}: {exc.response.text}"},
                ensure_ascii=False,
            )
        except httpx.RequestError as exc:
            return json.dumps(
                {"error": f"Failed to connect to feedback API: {exc}"},
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "id": result.get("id"),
                "score_updated": result.get("score_updated", False),
                "weights_adjusted": result.get("weights_adjusted", False),
            },
            ensure_ascii=False,
        )

    return record_feedback
