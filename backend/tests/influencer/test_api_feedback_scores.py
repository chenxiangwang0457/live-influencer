# backend/tests/influencer/test_api_feedback_scores.py
"""Integration tests for feedback detail, score, and analytics endpoints.

Covers:
  - GET  /feedbacks/{id}
  - GET  /scores/{id}
  - POST /scores/batch
  - GET  /analytics/weights
  - GET  /analytics/trends
  - GET  /selections/{id}/report
  - GET  /selections/{id}/compare
"""

from __future__ import annotations

import asyncio

import pytest
from httpx import ASGITransport, AsyncClient


# ── Module-level DB init ──


def _init_test_db():
    """Initialize an in-memory SQLite engine for tests."""
    from deerflow.persistence.engine import get_session_factory, init_engine

    if get_session_factory() is not None:
        return

    async def _init():
        import app.influencer.models.influencer  # noqa: F401
        import app.influencer.models.selection    # noqa: F401
        import app.influencer.models.feedback     # noqa: F401
        from app.influencer.models.influencer import Influencer
        from deerflow.persistence.base import Base

        await init_engine("sqlite", url="sqlite+aiosqlite:///:memory:", sqlite_dir=".")

        sf = get_session_factory()
        async with sf() as session:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Seed a test influencer
            test_inf = Influencer(
                id="inf_test_001",
                platform="douyin",
                platform_uid="mock_dy_test_001",
                nickname="测试达人",
                category="美妆",
                followers_count=500000,
                engagement_rate=3.5,
                avg_gmv=100000.0,
            )
            session.add(test_inf)
            await session.commit()

    asyncio.run(_init())


_init_test_db()


# ── Helpers ──


from app.gateway.app import create_app
from app.influencer.services.data_platform.mock import MockDataAdapter


def _make_app():
    app = create_app()
    app.state.influencer_adapter = MockDataAdapter()
    return app


def _get_session_factory():
    from deerflow.persistence.engine import get_session_factory

    sf = get_session_factory()
    if sf is None:
        raise RuntimeError("Persistence engine not initialized.")
    return sf


async def _create_selection(client: AsyncClient, title: str = "测试选人") -> str:
    resp = await client.post(
        "/api/influencer/selections",
        json={"title": title, "goal": "test", "criteria": {"category": "美妆"}},
    )
    return resp.json()["id"]


async def _add_candidate(client: AsyncClient, selection_id: str, influencer_id: str):
    from app.influencer.models.influencer import Influencer

    sf = _get_session_factory()
    async with sf() as session:
        inf_result = await session.execute(
            __import__("sqlalchemy").select(Influencer).where(Influencer.id == influencer_id)
        )
        if inf_result.scalar_one_or_none() is None:
            fake_inf = Influencer(
                id=influencer_id,
                platform="douyin",
                platform_uid=influencer_id,
                nickname=f"达人_{influencer_id}",
                category="美妆",
            )
            session.add(fake_inf)
            await session.commit()

    await client.post(
        f"/api/influencer/selections/{selection_id}/candidates",
        json={"influencer_id": influencer_id},
    )


# ═══════════════════════════════════════════════════════════════════════
#  Feedback detail endpoint
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_feedback_detail_found(monkeypatch):
    """GET /feedbacks/{id} returns feedback detail for an existing entry."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    from app.influencer.models.feedback import Feedback

    sf = _get_session_factory()
    async with sf() as session:
        fb = Feedback(
            influencer_id="inf_test_001",
            rating=4,
            review="很专业",
            tags=["专业"],
        )
        session.add(fb)
        await session.commit()
        fb_id = fb.id

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/influencer/feedbacks/{fb_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == fb_id
    assert data["rating"] == 4
    assert data["review"] == "很专业"
    assert "tags" in data
    assert "sales_performance" in data


@pytest.mark.asyncio
async def test_get_feedback_detail_not_found(monkeypatch):
    """GET /feedbacks/{id} returns 404 for a non-existent id."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/feedbacks/nonexistent-feedback-id")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Feedback not found"


# ═══════════════════════════════════════════════════════════════════════
#  Score endpoints
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_scores_found(monkeypatch):
    """GET /scores/{id} returns scores for an influencer with existing scores."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    from app.influencer.models.feedback import InfluencerScore

    sf = _get_session_factory()
    async with sf() as session:
        score = InfluencerScore(
            influencer_id="inf_test_001",
            dimension="overall",
            score=85.0,
            confidence=0.8,
            version=1,
            factors={"source": "test"},
        )
        session.add(score)
        await session.commit()

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/scores/inf_test_001")

    assert resp.status_code == 200
    data = resp.json()
    assert "scores" in data
    assert len(data["scores"]) >= 1
    first = data["scores"][0]
    assert first["influencer_id"] == "inf_test_001"
    assert first["dimension"] == "overall"
    assert first["score"] == 85.0
    assert first["confidence"] == 0.8


@pytest.mark.asyncio
async def test_get_scores_by_platform_uid(monkeypatch):
    """GET /scores/{id} resolves by platform_uid when no direct id match."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    from app.influencer.models.feedback import InfluencerScore

    sf = _get_session_factory()
    async with sf() as session:
        score = InfluencerScore(
            influencer_id="inf_test_001",
            dimension="engagement",
            score=72.0,
            confidence=0.6,
            version=2,
            factors={},
        )
        session.add(score)
        await session.commit()

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/scores/mock_dy_test_001")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scores"]) >= 1


@pytest.mark.asyncio
async def test_get_scores_not_found(monkeypatch):
    """GET /scores/{id} returns 404 when no scores exist."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/scores/nonexistent_id_xyz")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_batch_refresh_scores(monkeypatch):
    """POST /scores/batch refreshes scores for given influencer ids."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/influencer/scores/batch",
            json={"influencer_ids": ["inf_test_001"]},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "updated" in data
    assert data["updated"] >= 1


@pytest.mark.asyncio
async def test_batch_refresh_nonexistent_ids(monkeypatch):
    """POST /scores/batch returns updated=0 for nonexistent ids."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/influencer/scores/batch",
            json={"influencer_ids": ["no_such_id_1", "no_such_id_2"]},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] == 0


# ═══════════════════════════════════════════════════════════════════════
#  Analytics endpoints
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_analytics_weights(monkeypatch):
    """GET /analytics/weights returns current weight configuration."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/analytics/weights")

    assert resp.status_code == 200
    data = resp.json()
    assert "weights" in data
    weights = data["weights"]
    # Should contain the four standard dimensions
    for dim in ("match", "reach", "sales", "value"):
        assert dim in weights
        assert isinstance(weights[dim], (int, float))
    # Sum should be approximately 1.0
    assert abs(sum(weights.values()) - 1.0) < 0.01


@pytest.mark.asyncio
async def test_get_analytics_trends_empty(monkeypatch):
    """GET /analytics/trends returns empty list when no feedback exists."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/analytics/trends")

    assert resp.status_code == 200
    data = resp.json()
    assert "trends" in data
    assert isinstance(data["trends"], list)


@pytest.mark.asyncio
async def test_get_analytics_trends_with_data(monkeypatch):
    """GET /analytics/trends returns monthly feedback data."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    from app.influencer.models.feedback import Feedback

    sf = _get_session_factory()
    async with sf() as session:
        fb1 = Feedback(influencer_id="inf_test_001", rating=4)
        fb2 = Feedback(influencer_id="inf_test_001", rating=5)
        session.add_all([fb1, fb2])
        await session.commit()

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/analytics/trends")

    assert resp.status_code == 200
    data = resp.json()
    assert "trends" in data
    assert len(data["trends"]) >= 1
    trend = data["trends"][0]
    assert "month" in trend
    assert "count" in trend
    assert "avg_rating" in trend
    assert isinstance(trend["count"], int)
    assert trend["count"] >= 2


# ═══════════════════════════════════════════════════════════════════════
#  Selection report & compare endpoints
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_selection_report_with_summary(monkeypatch):
    """GET /selections/{id}/report returns cached summary after analyze."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create selection and add candidate
        sid = await _create_selection(client)
        await _add_candidate(client, sid, "inf_test_001")

        # Analyze to generate report + summary
        analyze_resp = await client.post(f"/api/influencer/selections/{sid}/analyze")
        assert analyze_resp.status_code == 200

        # Fetch report
        resp = await client.get(f"/api/influencer/selections/{sid}/report")

    assert resp.status_code == 200
    data = resp.json()
    assert "report" in data
    assert "generated_at" in data
    assert len(data["report"]) > 0


@pytest.mark.asyncio
async def test_selection_report_not_found(monkeypatch):
    """GET /selections/{id}/report returns 404 for missing selection."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/selections/nonexistent/report")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_selection_compare_with_candidates(monkeypatch):
    """GET /selections/{id}/compare returns structured comparison data."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = await _create_selection(client)
        await _add_candidate(client, sid, "inf_test_001")

        resp = await client.get(f"/api/influencer/selections/{sid}/compare")

    assert resp.status_code == 200
    data = resp.json()
    assert "candidates" in data
    assert "metrics" in data
    assert isinstance(data["candidates"], list)
    assert len(data["candidates"]) >= 1

    candidate = data["candidates"][0]
    for key in ("platform_uid", "nickname", "followers", "engagement", "gmv",
                "price_min", "price_max", "content_style", "match_score"):
        assert key in candidate, f"Missing key '{key}' in candidate data"

    # metrics must be a list of strings
    assert isinstance(data["metrics"], list)
    for m in data["metrics"]:
        assert isinstance(m, str)


@pytest.mark.asyncio
async def test_selection_compare_not_found(monkeypatch):
    """GET /selections/{id}/compare returns 404 for missing selection."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/selections/nonexistent/compare")

    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════
#  result_summary persistence (F5)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_result_summary_persisted_after_analyze(monkeypatch):
    """After analyze, the selection's result_summary is populated."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    from sqlalchemy import select as sa_select
    from app.influencer.models.selection import Selection

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = await _create_selection(client)
        await _add_candidate(client, sid, "inf_test_001")

        # Before analyze, result_summary should be None
        sf = _get_session_factory()
        async with sf() as session:
            result = await session.execute(
                sa_select(Selection).where(Selection.id == sid)
            )
            sel = result.scalar_one_or_none()
            assert sel is not None
            assert sel.result_summary is None

        # Run analyze
        analyze_resp = await client.post(f"/api/influencer/selections/{sid}/analyze")
        assert analyze_resp.status_code == 200

        # After analyze, result_summary should be populated
        async with sf() as session:
            result = await session.execute(
                sa_select(Selection).where(Selection.id == sid)
            )
            sel = result.scalar_one_or_none()
            assert sel is not None
            assert sel.result_summary is not None
            assert len(sel.result_summary) > 0
            assert len(sel.result_summary) <= 500


# ═══════════════════════════════════════════════════════════════════════
#  Error types smoke tests (F6)
# ═══════════════════════════════════════════════════════════════════════


class TestInfluencerServiceErrors:
    """Smoke tests for the new service error types."""

    def test_error_hierarchy(self):
        from app.influencer.services.errors import (
            InfluencerServiceError,
            DataPlatformError,
            MatchingError,
            ScoringError,
        )

        # All should be instances of the base
        for err_type in (DataPlatformError, MatchingError, ScoringError):
            assert issubclass(err_type, InfluencerServiceError)
            assert issubclass(err_type, Exception)

    def test_error_instantiation(self):
        from app.influencer.services.errors import (
            DataPlatformError,
            MatchingError,
            ScoringError,
        )

        for err_type, msg in (
            (DataPlatformError, "API timeout"),
            (MatchingError, "Invalid criteria"),
            (ScoringError, "Division by zero"),
        ):
            err = err_type(msg)
            assert str(err) == msg
