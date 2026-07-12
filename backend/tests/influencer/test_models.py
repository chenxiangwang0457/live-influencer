# backend/tests/influencer/test_models.py
from __future__ import annotations

import pytest
from app.influencer.models.influencer import Influencer


def test_create_influencer(db_session):
    influencer = Influencer(
        platform="douyin",
        platform_uid="dy_12345",
        nickname="测试达人",
        category="美妆",
        followers_count=1000000,
        avg_gmv=500000.0,
        price_range_min=10000,
        price_range_max=50000,
    )
    db_session.add(influencer)
    db_session.commit()
    db_session.refresh(influencer)

    assert influencer.id is not None
    assert influencer.platform == "douyin"
    assert influencer.platform_uid == "dy_12345"
    assert influencer.nickname == "测试达人"
    assert influencer.category == "美妆"
    assert influencer.followers_count == 1000000
    assert influencer.avg_gmv == 500000.0
    assert influencer.data_source == "mock"
    assert influencer.created_at is not None


def test_influencer_defaults(db_session):
    influencer = Influencer(
        platform="douyin",
        platform_uid="dy_000",
        nickname="新人",
        category="食品",
    )
    db_session.add(influencer)
    db_session.commit()

    assert influencer.followers_count == 0
    assert influencer.engagement_rate == 0.0
    assert influencer.avg_gmv == 0.0
    assert influencer.price_range_min == 0


def test_influencer_json_fields(db_session):
    influencer = Influencer(
        platform="douyin",
        platform_uid="dy_json",
        nickname="JSON达人",
        category="服饰",
        demographics={"age_18_24": 0.4, "age_25_34": 0.35, "gender_male": 0.3},
        content_style=["测评", "种草", "vlog"],
        brand_history=[{"brand": "品牌A", "year": 2025}],
    )
    db_session.add(influencer)
    db_session.commit()
    db_session.refresh(influencer)

    assert influencer.demographics["age_18_24"] == 0.4
    assert "测评" in influencer.content_style
    assert influencer.brand_history[0]["brand"] == "品牌A"
