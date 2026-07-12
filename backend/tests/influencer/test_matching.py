# backend/tests/influencer/test_matching.py
from __future__ import annotations

import pytest
from app.influencer.services.data_platform.base import InfluencerDTO
from app.influencer.services.matching import MatchingEngine


def make_dto(uid: str, category: str, followers: int, gmv: float, price_min: int) -> InfluencerDTO:
    return InfluencerDTO(
        platform="douyin",
        platform_uid=uid,
        nickname=f"达人_{uid}",
        category=category,
        followers_count=followers,
        engagement_rate=3.0,
        avg_gmv=gmv,
        avg_sales=int(gmv / 20),
        price_range_min=price_min,
        price_range_max=price_min * 3,
    )


@pytest.mark.asyncio
async def test_match_batch_sorts_by_total_desc():
    engine = MatchingEngine()
    dtos = [
        make_dto("a", "美妆", 100000, 50000, 5000),
        make_dto("b", "美妆", 5000000, 1000000, 80000),
        make_dto("c", "美妆", 500000, 200000, 20000),
    ]
    criteria = {"category": "美妆"}
    results = engine.match_batch(dtos, criteria)
    assert results[0].total_score >= results[1].total_score >= results[2].total_score


@pytest.mark.asyncio
async def test_match_batch_adds_scores():
    engine = MatchingEngine()
    dtos = [make_dto("a", "美妆", 500000, 100000, 20000)]
    results = engine.match_batch(dtos, {"category": "美妆"})
    r = results[0]
    assert 0 <= r.match_score <= 100
    assert 0 <= r.reach_score <= 100
    assert 0 <= r.sales_score <= 100
    assert 0 <= r.value_score <= 100
    assert 0 <= r.total_score <= 100


@pytest.mark.asyncio
async def test_match_batch_prefers_same_category():
    engine = MatchingEngine()
    dtos = [
        make_dto("match", "美妆", 500000, 100000, 20000),
        make_dto("diff", "食品", 5000000, 1000000, 20000),  # better stats but wrong category
    ]
    results = engine.match_batch(dtos, {"category": "美妆"})
    # The matching category should have higher match_score
    match_result = next(r for r in results if r.influencer.platform_uid == "match")
    diff_result = next(r for r in results if r.influencer.platform_uid == "diff")
    assert match_result.match_score > diff_result.match_score


@pytest.mark.asyncio
async def test_top_n_returns_requested_count():
    engine = MatchingEngine()
    dtos = [make_dto(str(i), "美妆", 100000 * i, 100000 * i, 10000 * i) for i in range(1, 11)]
    top5 = engine.top_n(dtos, {"category": "美妆"}, n=5)
    assert len(top5) == 5


@pytest.mark.asyncio
async def test_empty_batch():
    engine = MatchingEngine()
    results = engine.match_batch([], {"category": "美妆"})
    assert results == []
