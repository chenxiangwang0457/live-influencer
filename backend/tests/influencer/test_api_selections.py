# backend/tests/influencer/test_api_selections.py
from __future__ import annotations

import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from deerflow.persistence.engine import get_session_factory, init_engine


# ── Module-level DB init (runs once before all tests) ──

def _init_test_db():
    """Initialize an in-memory SQLite engine for tests."""
    if get_session_factory() is not None:
        return  # Already initialized

    async def _init():
        # Import models so their tables are registered in Base.metadata
        import app.influencer.models.selection  # noqa: F401
        from deerflow.persistence.base import Base

        await init_engine("sqlite", url="sqlite+aiosqlite:///:memory:", sqlite_dir=".")

        # Ensure our tables are created (bootstrap_schema may have done this,
        # but be explicit for test isolation)
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


# ── Tests ──


@pytest.mark.asyncio
async def test_create_selection(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/influencer/selections/",
            json={
                "title": "测试选人任务",
                "goal": "找3位美妆达人",
                "criteria": {"category": "美妆", "follower_min": 100000},
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "测试选人任务"
    assert data["status"] == "draft"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_list_selections(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create one first
        await client.post(
            "/api/influencer/selections/",
            json={"title": "列表测试", "goal": "test", "criteria": {}},
        )
        resp = await client.get("/api/influencer/selections/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_selection_detail(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/influencer/selections/",
            json={"title": "详情测试", "goal": "test", "criteria": {"category": "美妆"}},
        )
        sid = created.json()["id"]
        resp = await client.get(f"/api/influencer/selections/{sid}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "详情测试"


@pytest.mark.asyncio
async def test_update_selection_status(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/influencer/selections/",
            json={"title": "状态测试", "goal": "test", "criteria": {}},
        )
        sid = created.json()["id"]
        resp = await client.put(
            f"/api/influencer/selections/{sid}",
            json={"status": "in_progress", "title": "状态测试(更新)"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_add_candidate(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")

    # Insert a fake influencer into the DB so the FK constraint is satisfied
    from app.influencer.models.influencer import Influencer

    sf = get_session_factory()
    async with sf() as session:
        fake_inf = Influencer(
            id="mock_dy_0000",
            platform="douyin",
            platform_uid="mock_dy_0000",
            nickname="Mock达人_0000",
            category="美妆",
        )
        session.add(fake_inf)
        await session.commit()

    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get an influencer
        search = await client.get("/api/influencer/search", params={"page_size": 1})
        inf = search.json()["data"][0]

        # Create selection
        created = await client.post(
            "/api/influencer/selections/",
            json={"title": "添加候选测试", "goal": "test", "criteria": {"category": inf["category"]}},
        )
        sid = created.json()["id"]

        # Add candidate using the fake influencer's id
        resp = await client.post(
            f"/api/influencer/selections/{sid}/candidates",
            json={"influencer_id": "mock_dy_0000", "added_by": "manual_add"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_selection_not_found(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/selections/nonexistent-id")
    assert resp.status_code == 404
