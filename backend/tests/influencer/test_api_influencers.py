from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.gateway.app import create_app
from app.influencer.services.data_platform.mock import MockDataAdapter

MOCK_ADAPTER = MockDataAdapter()


def _make_app():
    app = create_app()
    app.state.influencer_adapter = MOCK_ADAPTER
    return app


@pytest.mark.asyncio
async def test_search_influencers_success(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"category": "美妆", "page_size": 5},
        )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert len(data["data"]) == 5
    assert all(r["category"] == "美妆" for r in data["data"])


@pytest.mark.asyncio
async def test_search_with_follower_range(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"follower_min": 100000, "follower_max": 500000, "page_size": 10},
        )
    assert response.status_code == 200
    data = response.json()
    for r in data["data"]:
        assert 100000 <= r["followers_count"] <= 500000


@pytest.mark.asyncio
async def test_search_empty_result(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"category": "不存在的类目"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_search_invalid_page_size(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"page_size": 200},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_influencer_detail_found(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/influencer/search", params={"page_size": 1})
        uid = r.json()["data"][0]["platform_uid"]
        detail = await client.get(f"/api/influencer/{uid}")
    assert detail.status_code == 200
    data = detail.json()
    assert data["platform_uid"] == uid
    assert "demographics" in data
    assert "content_style" in data


@pytest.mark.asyncio
async def test_get_influencer_detail_not_found(monkeypatch):
    monkeypatch.setenv("DEER_FLOW_AUTH_DISABLED", "1")
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/influencer/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Influencer not found"
