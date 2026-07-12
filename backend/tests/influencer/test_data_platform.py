# backend/tests/influencer/test_data_platform.py
from __future__ import annotations

from abc import ABC

import pytest
from pydantic import ValidationError

from app.influencer.services.data_platform.base import (
    DataPlatformAdapter,
    InfluencerDTO,
    SearchCriteria,
)


class TestSearchCriteria:
    """SearchCriteria Pydantic model tests"""

    def test_defaults(self):
        criteria = SearchCriteria()
        assert criteria.platform == "douyin"
        assert criteria.page == 1
        assert criteria.page_size == 20
        assert criteria.sort_by == "followers_count"
        assert criteria.sort_order == "desc"

    def test_keyword_set(self):
        criteria = SearchCriteria(keyword="美妆达人")
        assert criteria.keyword == "美妆达人"

    def test_follower_range(self):
        criteria = SearchCriteria(follower_min=1000, follower_max=100000)
        assert criteria.follower_min == 1000
        assert criteria.follower_max == 100000

    def test_engagement_range(self):
        criteria = SearchCriteria(engagement_min=1.5, engagement_max=10.0)
        assert criteria.engagement_min == 1.5
        assert criteria.engagement_max == 10.0

    def test_category_filter(self):
        criteria = SearchCriteria(category="美妆")
        assert criteria.category == "美妆"

    def test_price_range(self):
        criteria = SearchCriteria(price_min=5000, price_max=50000)
        assert criteria.price_min == 5000
        assert criteria.price_max == 50000

    def test_gmv_min(self):
        criteria = SearchCriteria(gmv_min=10000.0)
        assert criteria.gmv_min == 10000.0

    def test_sort_order_asc(self):
        criteria = SearchCriteria(sort_order="asc")
        assert criteria.sort_order == "asc"

    def test_page_size_validation(self):
        with pytest.raises(ValidationError):
            SearchCriteria(page_size=200)

    def test_page_ge_one(self):
        with pytest.raises(ValidationError):
            SearchCriteria(page=0)


class TestInfluencerDTO:
    """InfluencerDTO dataclass tests"""

    def test_minimal_dto(self):
        dto = InfluencerDTO(
            platform="douyin",
            platform_uid="dy_12345",
            nickname="测试达人",
        )
        assert dto.platform == "douyin"
        assert dto.platform_uid == "dy_12345"
        assert dto.nickname == "测试达人"
        assert dto.avatar_url == ""
        assert dto.followers_count == 0
        assert dto.engagement_rate == 0.0
        assert dto.data_source == "mock"

    def test_full_dto(self):
        dto = InfluencerDTO(
            platform="douyin",
            platform_uid="dy_full",
            nickname="完整达人",
            avatar_url="https://example.com/avatar.jpg",
            category="美妆",
            sub_categories=["护肤", "彩妆"],
            followers_count=500000,
            avg_likes=12000,
            avg_comments=800,
            avg_shares=300,
            engagement_rate=3.5,
            avg_gmv=200000.0,
            avg_sales=5000,
            price_range_min=10000,
            price_range_max=30000,
            demographics={"age_18_24": 0.5, "gender_female": 0.8},
            content_style=["测评", "教程"],
            brand_history=[{"brand": "品牌X", "year": 2025}],
            data_source="official",
        )
        assert dto.category == "美妆"
        assert dto.followers_count == 500000
        assert dto.engagement_rate == 3.5
        assert dto.data_source == "official"

    def test_to_orm_dict(self):
        dto = InfluencerDTO(
            platform="kuaishou",
            platform_uid="ks_001",
            nickname="快手达人",
            category="美食",
            followers_count=200000,
            avg_gmv=80000.0,
        )
        orm_dict = dto.to_orm_dict()

        assert orm_dict["platform"] == "kuaishou"
        assert orm_dict["platform_uid"] == "ks_001"
        assert orm_dict["nickname"] == "快手达人"
        assert orm_dict["category"] == "美食"
        assert orm_dict["followers_count"] == 200000
        assert orm_dict["avg_gmv"] == 80000.0
        assert orm_dict["data_source"] == "mock"
        # Should not include ORM-only fields like id, created_at, updated_at
        assert "id" not in orm_dict
        assert "created_at" not in orm_dict
        assert "updated_at" not in orm_dict

    def test_to_orm_dict_all_fields(self):
        dto = InfluencerDTO(
            platform="douyin",
            platform_uid="dy_all",
            nickname="全字段达人",
            avatar_url="https://example.com/avatar.png",
            category="数码",
            sub_categories=["手机", "电脑"],
            followers_count=1000000,
            avg_likes=25000,
            avg_comments=1500,
            avg_shares=500,
            engagement_rate=2.7,
            avg_gmv=500000.0,
            avg_sales=10000,
            price_range_min=20000,
            price_range_max=100000,
            demographics={"age_25_34": 0.6},
            content_style=["评测"],
            brand_history=[{"brand": "品牌Y"}],
            data_source="official",
        )
        orm_dict = dto.to_orm_dict()
        assert orm_dict["avatar_url"] == "https://example.com/avatar.png"
        assert orm_dict["sub_categories"] == ["手机", "电脑"]
        assert orm_dict["avg_likes"] == 25000
        assert orm_dict["avg_comments"] == 1500
        assert orm_dict["avg_shares"] == 500
        assert orm_dict["engagement_rate"] == 2.7
        assert orm_dict["avg_sales"] == 10000
        assert orm_dict["price_range_min"] == 20000
        assert orm_dict["price_range_max"] == 100000
        assert orm_dict["demographics"] == {"age_25_34": 0.6}
        assert orm_dict["content_style"] == ["评测"]
        assert orm_dict["brand_history"] == [{"brand": "品牌Y"}]
        assert orm_dict["data_source"] == "official"


class TestDataPlatformAdapter:
    """DataPlatformAdapter ABC tests"""

    def test_cannot_instantiate(self):
        """ABC should not be directly instantiable"""
        with pytest.raises(TypeError, match="abstract"):
            DataPlatformAdapter()

    def test_concrete_subclass(self):
        """A concrete subclass with all methods implemented should work"""

        class MockPlatform(DataPlatformAdapter):
            @property
            def platform_name(self) -> str:
                return "mock_platform"

            async def search_influencers(self, criteria: SearchCriteria) -> tuple[list[InfluencerDTO], int]:
                return [], 0

            async def get_influencer_detail(self, platform_uid: str) -> InfluencerDTO | None:
                return None

            async def health_check(self) -> bool:
                return True

        adapter = MockPlatform()
        assert adapter.platform_name == "mock_platform"
        assert issubclass(DataPlatformAdapter, ABC)
        assert isinstance(adapter, DataPlatformAdapter)

    def test_subclass_missing_method_raises(self):
        """Subclass missing abstract methods should not be instantiable"""

        class IncompleteAdapter(DataPlatformAdapter):
            @property
            def platform_name(self) -> str:
                return "incomplete"

            async def search_influencers(self, criteria: SearchCriteria) -> tuple[list[InfluencerDTO], int]:
                return [], 0

            async def get_influencer_detail(self, platform_uid: str) -> InfluencerDTO | None:
                return None

            # Missing health_check

        with pytest.raises(TypeError, match="abstract"):
            IncompleteAdapter()


class TestImports:
    """Verify package-level imports"""

    def test_data_platform_init_exports(self):
        from app.influencer.services.data_platform import (  # noqa: F811
            DataPlatformAdapter,
            InfluencerDTO,
            SearchCriteria,
        )

        assert DataPlatformAdapter is not None
        assert SearchCriteria is not None
        assert InfluencerDTO is not None
