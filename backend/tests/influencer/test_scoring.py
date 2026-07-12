# backend/tests/influencer/test_scoring.py
from __future__ import annotations

import pytest
from app.influencer.services.data_platform.base import InfluencerDTO
from app.influencer.services.scoring import ScoreEngine, get_default_weights


def make_dto(**overrides) -> InfluencerDTO:
    defaults = {
        "platform": "douyin",
        "platform_uid": "test_001",
        "nickname": "测试达人",
        "category": "美妆",
        "sub_categories": ["美妆", "护肤"],
        "followers_count": 500000,
        "engagement_rate": 3.5,
        "avg_gmv": 100000.0,
        "avg_sales": 5000,
        "price_range_min": 10000,
        "price_range_max": 30000,
        "demographics": {"age_18_24": 0.3, "age_25_34": 0.5, "age_35_plus": 0.2, "gender_male": 0.2},
        "content_style": ["测评", "教程"],
        "brand_history": [],
        "data_source": "mock",
    }
    defaults.update(overrides)
    return InfluencerDTO(**defaults)


class TestScoreEngine:

    @pytest.fixture
    def engine(self):
        return ScoreEngine()

    def test_score_is_between_0_and_100(self, engine):
        dto = make_dto()
        criteria = {"category": "美妆"}
        result = engine.score_influencer(dto, criteria)
        for dim in ["match_score", "reach_score", "sales_score", "value_score"]:
            assert 0 <= result[dim] <= 100, f"{dim} out of range: {result[dim]}"

    def test_exact_category_match_high_score(self, engine):
        dto = make_dto(category="美妆", sub_categories=["美妆", "护肤"])
        dto_diff = make_dto(category="食品", sub_categories=["零食"])
        criteria = {"category": "美妆"}
        score_match = engine.score_influencer(dto, criteria)["match_score"]
        score_diff = engine.score_influencer(dto_diff, criteria)["match_score"]
        assert score_match > score_diff, f"match: {score_match} <= diff: {score_diff}"

    def test_higher_followers_more_reach(self, engine):
        dto_big = make_dto(followers_count=5000000)
        dto_small = make_dto(followers_count=50000)
        criteria = {"category": "美妆"}
        score_big = engine.score_influencer(dto_big, criteria)["reach_score"]
        score_small = engine.score_influencer(dto_small, criteria)["reach_score"]
        assert score_big > score_small

    def test_higher_engagement_more_reach(self, engine):
        dto_high = make_dto(followers_count=500000, engagement_rate=8.0)
        dto_low = make_dto(followers_count=500000, engagement_rate=0.5)
        criteria = {"category": "美妆"}
        score_high = engine.score_influencer(dto_high, criteria)["reach_score"]
        score_low = engine.score_influencer(dto_low, criteria)["reach_score"]
        assert score_high > score_low

    def test_higher_gmv_more_sales(self, engine):
        dto_high = make_dto(avg_gmv=1000000.0, avg_sales=50000)
        dto_low = make_dto(avg_gmv=10000.0, avg_sales=500)
        criteria = {"category": "美妆"}
        score_high = engine.score_influencer(dto_high, criteria)["sales_score"]
        score_low = engine.score_influencer(dto_low, criteria)["sales_score"]
        assert score_high > score_low

    def test_calculate_total_weighted(self, engine):
        dto = make_dto()
        criteria = {"category": "美妆"}
        total = engine.calculate_total(dto, criteria)
        assert 0 <= total <= 100

    def test_low_price_better_value(self, engine):
        dto_cheap = make_dto(price_range_min=1000, price_range_max=5000, avg_gmv=100000.0)
        dto_expensive = make_dto(price_range_min=50000, price_range_max=100000, avg_gmv=100000.0)
        criteria = {"category": "美妆"}
        score_cheap = engine.score_influencer(dto_cheap, criteria)["value_score"]
        score_expensive = engine.score_influencer(dto_expensive, criteria)["value_score"]
        assert score_cheap > score_expensive


class TestDefaultWeights:

    def test_weights_sum_to_one(self):
        w = get_default_weights()
        total = sum(w.values())
        assert abs(total - 1.0) < 0.001

    def test_weights_have_all_dimensions(self):
        w = get_default_weights()
        assert set(w.keys()) == {"match", "reach", "sales", "value"}
