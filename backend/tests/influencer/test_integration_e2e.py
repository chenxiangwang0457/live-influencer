"""End-to-end integration test: full influencer selection flow.

Covers the complete workflow:
  search -> create selection -> add candidates -> analyze -> verify scores ->
  feedback -> verify stats -> compare -> report
"""

from __future__ import annotations

import asyncio

import pytest
from httpx import ASGITransport, AsyncClient


# ── Module-level DB init (runs once before all tests) ──


def _init_test_db():
    """Initialize an in-memory SQLite engine for tests."""
    from deerflow.persistence.engine import get_session_factory, init_engine

    if get_session_factory() is not None:
        return  # Already initialized

    async def _init():
        import app.influencer.models.influencer  # noqa: F401
        import app.influencer.models.selection  # noqa: F401
        import app.influencer.models.feedback  # noqa: F401
        from deerflow.persistence.base import Base

        await init_engine("sqlite", url="sqlite+aiosqlite:///:memory:", sqlite_dir=".")

        sf = get_session_factory()
        async with sf() as session:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_init())


_init_test_db()


# ── Helpers ──


from app.gateway.app import create_app
from app.influencer.services.data_platform.mock import MockDataAdapter


def _make_app():
    app = create_app()
    app.state.influencer_adapter = MockDataAdapter()
    return app


# ═══════════════════════════════════════════════════════════════════════
#  Full end-to-end selection flow
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_full_selection_flow(monkeypatch):
    """Complete flow: search -> create selection -> add candidates ->
    analyze -> verify scores -> feedback -> stats -> compare -> report."""
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Search influencers
        resp = await client.get(
            "/api/influencer/search",
            params={"category": "美妆", "page_size": 5},
        )
        assert resp.status_code == 200
        influencers = resp.json()["data"]
        assert len(influencers) > 0

        # 2. Create selection
        resp = await client.post(
            "/api/influencer/selections",
            json={
                "title": "E2E 集成测试",
                "goal": "测试完整选人流程",
                "criteria": {"category": "美妆"},
            },
        )
        assert resp.status_code == 200
        sel_id = resp.json()["id"]

        # 3. Add candidates
        for inf in influencers[:3]:
            resp = await client.post(
                f"/api/influencer/selections/{sel_id}/candidates",
                json={
                    "influencer_id": inf["platform_uid"],
                    "added_by": "manual_add",
                },
            )
            assert resp.status_code == 200

        # 4. Analyze
        resp = await client.post(f"/api/influencer/selections/{sel_id}/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert "report" in data
        assert len(data["candidates"]) == 3

        # 5. Verify scores updated
        resp = await client.get(f"/api/influencer/selections/{sel_id}")
        assert resp.status_code == 200
        detail = resp.json()
        for c in detail["candidates"]:
            assert c["match_score"] > 0  # Should have real scores now

        # 6. Verify result_summary saved
        assert detail.get("result_summary") is not None

        # 7. Submit feedback
        if detail["candidates"]:
            cid = detail["candidates"][0]["influencer_id"]
            resp = await client.post(
                "/api/influencer/feedbacks",
                json={
                    "influencer_id": cid,
                    "selection_id": sel_id,
                    "rating": 4,
                    "review": "测试反馈",
                    "tags": ["专业度高"],
                },
            )
            assert resp.status_code == 200
            assert resp.json()["score_updated"] is True

        # 8. Verify feedback stats
        resp = await client.get("/api/influencer/feedbacks/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total"] >= 1

        # 9. Compare endpoint
        resp = await client.get(f"/api/influencer/selections/{sel_id}/compare")
        assert resp.status_code == 200
        cmp_data = resp.json()
        assert len(cmp_data["candidates"]) == 3

        # 10. Report endpoint
        resp = await client.get(f"/api/influencer/selections/{sel_id}/report")
        assert resp.status_code == 200
        assert resp.json()["report"] is not None
