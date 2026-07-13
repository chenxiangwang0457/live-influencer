# backend/tests/influencer/test_agent_tools.py
"""Tests for influencer selection agent tools (harness layer).

Each tool is a factory-built LangChain ``@tool``. These tests use the app-layer
``MockDataAdapter``, ``ScoreEngine``, and ``MatchingEngine`` to construct real
tool instances and exercise them end-to-end.
"""

from __future__ import annotations

import json

import pytest
from app.influencer.services.data_platform.mock import MockDataAdapter
from app.influencer.services.matching import MatchingEngine
from app.influencer.services.scoring import ScoreEngine

from deerflow.tools.influencer.compare_influencers import build_compare_influencers_tool
from deerflow.tools.influencer.recommend_report import build_recommend_report_tool
from deerflow.tools.influencer.search_influencers import build_search_influencers_tool


# ── Fixtures ──


@pytest.fixture
def adapter():
    """Provide a fresh MockDataAdapter with 150 seeded influencers."""
    return MockDataAdapter()


@pytest.fixture
def engine():
    """Provide a MatchingEngine backed by a default ScoreEngine."""
    return MatchingEngine(ScoreEngine())


@pytest.fixture
def search_tool(adapter, engine):
    """Build the search_influencers tool from factory."""
    return build_search_influencers_tool(adapter, engine)


@pytest.fixture
def compare_tool(adapter):
    """Build the compare_influencers tool from factory."""
    return build_compare_influencers_tool(adapter)


@pytest.fixture
def report_tool():
    """Build the recommend_report tool from factory."""
    return build_recommend_report_tool()


# ── Helper ──


def _parse_json(result: str) -> dict:
    """Parse a tool result string as JSON, failing with the raw string on error."""
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        pytest.fail(f"Tool result is not valid JSON:\n{result}")


# ═══════════════════════════════════════════════════════════════════════
# search_influencers
# ═══════════════════════════════════════════════════════════════════════


class TestSearchInfluencers:
    """Tests for the ``search_influencers`` agent tool."""

    @pytest.mark.asyncio
    async def test_returns_valid_json_with_results(self, search_tool):
        """Basic: search returns JSON with scored results."""
        result = await search_tool.ainvoke({"criteria_json": json.dumps({"category": "美妆"})})
        data = _parse_json(result)
        assert "results" in data
        assert "total_count" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["total_count"], int)

    @pytest.mark.asyncio
    async def test_results_have_required_fields(self, search_tool):
        """Each result entry contains all required fields."""
        result = await search_tool.ainvoke({"criteria_json": json.dumps({"category": "美妆"})})
        data = _parse_json(result)
        if data["results"]:
            entry = data["results"][0]
            expected_keys = {
                "nickname", "platform_uid", "category", "followers_count",
                "engagement_rate", "avg_gmv", "price_range_max",
                "match_score", "reach_score", "sales_score", "value_score",
                "total_score",
            }
            assert set(entry.keys()) == expected_keys, f"Missing or extra keys: {set(entry.keys()) ^ expected_keys}"

    @pytest.mark.asyncio
    async def test_results_sorted_by_total_score_desc(self, search_tool):
        """Results are returned in descending total_score order."""
        result = await search_tool.ainvoke({"criteria_json": json.dumps({"category": "美妆"})})
        data = _parse_json(result)
        if len(data["results"]) >= 2:
            scores = [r["total_score"] for r in data["results"]]
            assert scores == sorted(scores, reverse=True), f"Not sorted desc: {scores}"

    @pytest.mark.asyncio
    async def test_returns_at_most_10(self, search_tool):
        """Tool caps results at 10 entries."""
        result = await search_tool.ainvoke({"criteria_json": json.dumps({"page_size": 100})})
        data = _parse_json(result)
        assert len(data["results"]) <= 10

    @pytest.mark.asyncio
    async def test_with_keyword_filter(self, search_tool):
        """Keyword search filters results."""
        result = await search_tool.ainvoke({"criteria_json": json.dumps({"keyword": "美妆", "page_size": 50})})
        data = _parse_json(result)
        for entry in data["results"]:
            assert ("美妆" in entry.get("nickname", "")) or ("美妆" in entry.get("category", ""))

    @pytest.mark.asyncio
    async def test_empty_results_when_no_match(self, search_tool):
        """Returns empty results list when no influencers match."""
        result = await search_tool.ainvoke(
            {"criteria_json": json.dumps({"keyword": "NONEXISTENT_XYZ_123"})}
        )
        data = _parse_json(result)
        assert data["results"] == []
        assert data["total_count"] == 0

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error(self, search_tool):
        """Malformed JSON returns an error field with empty results."""
        result = await search_tool.ainvoke({"criteria_json": "not-valid-json!!!!"})
        data = _parse_json(result)
        assert "error" in data
        assert data["results"] == []

    @pytest.mark.asyncio
    async def test_non_dict_input_returns_error(self, search_tool):
        """JSON array instead of object returns an error."""
        result = await search_tool.ainvoke({"criteria_json": "[1, 2, 3]"})
        data = _parse_json(result)
        assert "error" in data
        assert data["results"] == []

    @pytest.mark.asyncio
    async def test_follower_range_filter(self, search_tool):
        """Follower min/max filtering works."""
        result = await search_tool.ainvoke(
            {"criteria_json": json.dumps({"follower_min": 100000, "follower_max": 1000000, "page_size": 100})}
        )
        data = _parse_json(result)
        for entry in data["results"]:
            assert 100000 <= entry["followers_count"] <= 1000000

    @pytest.mark.asyncio
    async def test_engagement_filter(self, search_tool):
        """Engagement rate min/max filtering works."""
        result = await search_tool.ainvoke(
            {"criteria_json": json.dumps({"engagement_min": 2.0, "engagement_max": 6.0, "page_size": 100})}
        )
        data = _parse_json(result)
        for entry in data["results"]:
            assert 2.0 <= entry["engagement_rate"] <= 6.0

    @pytest.mark.asyncio
    async def test_price_filter(self, search_tool):
        """Price range filtering works."""
        result = await search_tool.ainvoke(
            {"criteria_json": json.dumps({"price_min": 20000, "price_max": 100000, "page_size": 100})}
        )
        data = _parse_json(result)
        for entry in data["results"]:
            # price_range_max of result must be >= price_min
            assert entry["price_range_max"] >= 20000

    @pytest.mark.asyncio
    async def test_score_ranges(self, search_tool):
        """All scores are within valid 0-100 range."""
        result = await search_tool.ainvoke({"criteria_json": json.dumps({"category": "美妆"})})
        data = _parse_json(result)
        for entry in data["results"]:
            for key in ["match_score", "reach_score", "sales_score", "value_score", "total_score"]:
                assert 0 <= entry[key] <= 100, f"{key}={entry[key]} out of range"


# ═══════════════════════════════════════════════════════════════════════
# compare_influencers
# ═══════════════════════════════════════════════════════════════════════


class TestCompareInfluencers:
    """Tests for the ``compare_influencers`` agent tool."""

    @pytest.mark.asyncio
    async def test_compares_valid_uids(self, compare_tool):
        """Compare existing UIDs returns side-by-side data."""
        result = await compare_tool.ainvoke(
            {"platform_uids_json": json.dumps(["mock_dy_0001", "mock_dy_0002", "mock_dy_0003"])}
        )
        data = _parse_json(result)
        assert "compared" in data
        assert "errors" in data
        assert len(data["compared"]) == 3
        assert len(data["errors"]) == 0

    @pytest.mark.asyncio
    async def test_compared_entries_have_required_fields(self, compare_tool):
        """Each compared entry contains all required fields."""
        result = await compare_tool.ainvoke(
            {"platform_uids_json": json.dumps(["mock_dy_0042"])}
        )
        data = _parse_json(result)
        entry = data["compared"][0]
        expected_keys = {
            "platform_uid", "nickname", "category", "followers_count",
            "engagement_rate", "avg_gmv", "price_range_min", "price_range_max",
            "content_style",
        }
        assert set(entry.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_caps_at_max_6(self, compare_tool):
        """A request with more than 6 UIDs is capped at 6."""
        many_uids = [f"mock_dy_{i:04d}" for i in range(20)]
        result = await compare_tool.ainvoke(
            {"platform_uids_json": json.dumps(many_uids)}
        )
        data = _parse_json(result)
        assert len(data["compared"]) <= 6

    @pytest.mark.asyncio
    async def test_nonexistent_uids_in_errors(self, compare_tool):
        """Non-existent UIDs appear in the errors list."""
        result = await compare_tool.ainvoke(
            {"platform_uids_json": json.dumps(["mock_dy_0001", "nonexistent_9999"])}
        )
        data = _parse_json(result)
        assert len(data["compared"]) == 1
        assert "nonexistent_9999" in data["errors"]

    @pytest.mark.asyncio
    async def test_all_nonexistent_returns_empty_compared(self, compare_tool):
        """When no UIDs are found, compared is empty and all are in errors."""
        result = await compare_tool.ainvoke(
            {"platform_uids_json": json.dumps(["bad_001", "bad_002"])}
        )
        data = _parse_json(result)
        assert data["compared"] == []
        assert len(data["errors"]) == 2

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error(self, compare_tool):
        """Malformed JSON returns an error field."""
        result = await compare_tool.ainvoke({"platform_uids_json": "{{broken"})
        data = _parse_json(result)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_non_array_input_returns_error(self, compare_tool):
        """JSON object instead of array returns an error."""
        result = await compare_tool.ainvoke({"platform_uids_json": '{"uid": "mock_dy_0001"}'})
        data = _parse_json(result)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_empty_array(self, compare_tool):
        """Empty UID array returns empty compared."""
        result = await compare_tool.ainvoke({"platform_uids_json": "[]"})
        data = _parse_json(result)
        assert data["compared"] == []
        assert data["errors"] == []


# ═══════════════════════════════════════════════════════════════════════
# recommend_report
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendReport:
    """Tests for the ``recommend_report`` agent tool."""

    _VALID_INPUT = json.dumps({
        "criteria": {
            "category": "美妆",
            "follower_min": 100000,
            "follower_max": 1000000,
            "engagement_min": 2.0,
            "price_min": 10000,
            "price_max": 80000,
            "gmv_min": 50000,
            "keyword": "美妆护肤",
        },
        "picks": [
            {"platform_uid": "mock_dy_0001", "nickname": "美妆达人A", "score": 92.5, "reason": "类目精准匹配，互动率高"},
            {"platform_uid": "mock_dy_0042", "nickname": "护肤专家B", "score": 88.3, "reason": "粉丝画像契合，GMV稳定"},
            {"platform_uid": "mock_dy_0087", "nickname": "时尚博主C", "score": 81.0, "reason": "性价比突出，内容质量高"},
        ],
    })

    @pytest.mark.asyncio
    async def test_returns_markdown_string(self, report_tool):
        """Valid input produces a Markdown-formatted string."""
        result = await report_tool.ainvoke({"selection_json": self._VALID_INPUT})
        assert isinstance(result, str)
        assert result.startswith("# 达人推荐报告")
        assert "## 一、筛选条件" in result
        assert "## 二、推荐达人" in result
        assert "## 三、综合分析与建议" in result
        assert "## 四、下一步行动建议" in result

    @pytest.mark.asyncio
    async def test_report_contains_all_pick_names(self, report_tool):
        """Report includes all recommended influencer nicknames."""
        result = await report_tool.ainvoke({"selection_json": self._VALID_INPUT})
        assert "美妆达人A" in result
        assert "护肤专家B" in result
        assert "时尚博主C" in result

    @pytest.mark.asyncio
    async def test_report_contains_criteria_fields(self, report_tool):
        """Report includes the search criteria in section 1."""
        result = await report_tool.ainvoke({"selection_json": self._VALID_INPUT})
        assert "美妆" in result
        assert "100000" in result
        assert "美妆护肤" in result

    @pytest.mark.asyncio
    async def test_report_contains_next_steps(self, report_tool):
        """Report includes actionable next steps in section 4."""
        result = await report_tool.ainvoke({"selection_json": self._VALID_INPUT})
        assert "优先联系" in result
        assert "样品寄送" in result
        assert "合作协议" in result

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error_message(self, report_tool):
        """Malformed JSON returns a clear error message."""
        result = await report_tool.ainvoke({"selection_json": "not-json"})
        assert "Error" in result
        assert "Invalid JSON" in result

    @pytest.mark.asyncio
    async def test_non_dict_input_returns_error(self, report_tool):
        """Non-object JSON returns an error."""
        result = await report_tool.ainvoke({"selection_json": "[1, 2, 3]"})
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_empty_picks_returns_error(self, report_tool):
        """Empty picks array returns an error."""
        result = await report_tool.ainvoke(
            {"selection_json": json.dumps({"criteria": {"category": "美妆"}, "picks": []})}
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_missing_picks_key_returns_error(self, report_tool):
        """Missing 'picks' field returns an error."""
        result = await report_tool.ainvoke(
            {"selection_json": json.dumps({"criteria": {"category": "美妆"}})}
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_single_pick_produces_valid_report(self, report_tool):
        """Report with only 1 pick is still valid."""
        result = await report_tool.ainvoke({
            "selection_json": json.dumps({
                "criteria": {"category": "食品"},
                "picks": [{"platform_uid": "x", "nickname": "美食家D", "score": 95, "reason": "顶级美食博主"}],
            })
        })
        assert "美食家D" in result
        assert "95" in result

    @pytest.mark.asyncio
    async def test_picks_without_nickname_falls_back_to_uid(self, report_tool):
        """Picks without nickname use platform_uid as fallback."""
        result = await report_tool.ainvoke({
            "selection_json": json.dumps({
                "criteria": {},
                "picks": [{"platform_uid": "uid_123", "score": 70, "reason": "ok"}],
            })
        })
        assert "uid_123" in result

    @pytest.mark.asyncio
    async def test_no_category_shows_all_categories_message(self, report_tool):
        """When no category filter, the report mentions multi-category coverage."""
        result = await report_tool.ainvoke({
            "selection_json": json.dumps({
                "criteria": {},
                "picks": [{"platform_uid": "x", "nickname": "达人E", "score": 80, "reason": "good"}],
            })
        })
        assert "多个类目" in result


# ═══════════════════════════════════════════════════════════════════════
# record_feedback
# ═══════════════════════════════════════════════════════════════════════


class TestRecordFeedback:
    """Tests for the ``record_feedback`` agent tool.

    These tests validate input handling only — actual HTTP calls are not
    made because there is no live Gateway server during unit test runs.
    """

    @pytest.fixture
    def feedback_tool(self):
        from deerflow.tools.influencer.record_feedback import build_record_feedback_tool

        return build_record_feedback_tool(base_url="http://localhost:9999")

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error(self, feedback_tool):
        """Malformed JSON input returns an error."""
        result = await feedback_tool.ainvoke({"feedback_json": "not-valid-json!!!!"})
        data = json.loads(result)
        assert "error" in data
        assert "Invalid JSON" in data["error"]

    @pytest.mark.asyncio
    async def test_non_dict_input_returns_error(self, feedback_tool):
        """Non-object JSON input returns an error."""
        result = await feedback_tool.ainvoke({"feedback_json": "[1, 2, 3]"})
        data = json.loads(result)
        assert "error" in data
        assert "JSON object" in data["error"]

    @pytest.mark.asyncio
    async def test_missing_influencer_id_returns_error(self, feedback_tool):
        """Missing required influencer_id returns an error."""
        result = await feedback_tool.ainvoke({
            "feedback_json": json.dumps({"rating": 4})
        })
        data = json.loads(result)
        assert "error" in data
        assert "influencer_id" in data["error"]

    @pytest.mark.asyncio
    async def test_invalid_rating_returns_error(self, feedback_tool):
        """Rating out of range returns an error."""
        result = await feedback_tool.ainvoke({
            "feedback_json": json.dumps({"influencer_id": "test_001", "rating": 6})
        })
        data = json.loads(result)
        assert "error" in data
        assert "rating" in data["error"]

    @pytest.mark.asyncio
    async def test_missing_rating_returns_error(self, feedback_tool):
        """Missing rating field returns an error."""
        result = await feedback_tool.ainvoke({
            "feedback_json": json.dumps({"influencer_id": "test_001"})
        })
        data = json.loads(result)
        assert "error" in data
        assert "rating" in data["error"]
