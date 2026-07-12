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


def test_create_selection(db_session):
    from app.influencer.models.selection import Selection

    sel = Selection(
        title="2026春季美妆达人筛选",
        goal="找3位美妆类达人中腰部达人",
        criteria={"category": "美妆", "follower_min": 100000, "follower_max": 500000},
    )
    db_session.add(sel)
    db_session.commit()
    db_session.refresh(sel)

    assert sel.id is not None
    assert sel.status == "draft"
    assert sel.criteria["category"] == "美妆"


def test_create_selection_with_candidates(db_session):
    from app.influencer.models.selection import Selection, SelectionInfluencer
    from app.influencer.models.influencer import Influencer

    inf = Influencer(platform="douyin", platform_uid="dy_test", nickname="测试", category="美妆")
    db_session.add(inf)
    db_session.flush()

    sel = Selection(title="测试选人任务")
    db_session.add(sel)
    db_session.flush()

    link = SelectionInfluencer(
        selection_id=sel.id,
        influencer_id=inf.id,
        match_score=85.5,
        match_reason="粉丝画像高度匹配",
        status="shortlisted",
        added_by="ai_recommend",
    )
    db_session.add(link)
    db_session.commit()
    db_session.refresh(sel)

    assert len(sel.candidates) == 1
    assert sel.candidates[0].match_score == 85.5


def test_create_feedback(db_session):
    from app.influencer.models.feedback import Feedback
    from app.influencer.models.influencer import Influencer

    inf = Influencer(platform="douyin", platform_uid="dy_fb", nickname="反馈测试", category="食品")
    db_session.add(inf)
    db_session.flush()

    fb = Feedback(
        influencer_id=inf.id,
        rating=4,
        review="配合度高，转化效果好",
        tags=["专业", "配合度高"],
    )
    db_session.add(fb)
    db_session.commit()

    assert fb.rating == 4
    assert "配合度高" in fb.tags


def test_create_influencer_score(db_session):
    from app.influencer.models.feedback import InfluencerScore
    from app.influencer.models.influencer import Influencer

    inf = Influencer(platform="douyin", platform_uid="dy_score", nickname="评分测试", category="服饰")
    db_session.add(inf)
    db_session.flush()

    score = InfluencerScore(
        influencer_id=inf.id,
        dimension="engagement",
        score=88.5,
        confidence=0.95,
        version=1,
        factors={"avg_likes": 50000, "avg_comments": 3000},
    )
    db_session.add(score)
    db_session.commit()
    db_session.refresh(score)

    assert score.dimension == "engagement"
    assert score.score == 88.5
    assert score.confidence == 0.95
    assert score.version == 1
    assert score.factors["avg_likes"] == 50000
