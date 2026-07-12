# backend/app/influencer/services/data_platform/mock.py
from __future__ import annotations

import random

from app.influencer.services.data_platform.base import (
    DataPlatformAdapter,
    InfluencerDTO,
    SearchCriteria,
)

_CATEGORIES = ["美妆", "食品", "服饰", "母婴", "3C数码", "家居", "运动", "图书"]
_CONTENT_STYLES = ["测评", "种草", "教程", "vlog", "搞笑", "剧情", "颜值", "知识"]
_CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
_BRANDS = ["欧莱雅", "蒙牛", "耐克", "小米", "宜家", "安踏", "华为", "良品铺子"]

SEED = 42


class MockDataAdapter(DataPlatformAdapter):
    """模拟数据适配器，内置 150 条达人数据用于开发和演示"""

    def __init__(self):
        self._influencers: list[InfluencerDTO] = []
        self._generate_data()

    @property
    def platform_name(self) -> str:
        return "douyin"

    def _generate_data(self) -> None:
        rng = random.Random(SEED)
        for i in range(150):
            category = rng.choice(_CATEGORIES)
            follower_tier = rng.choice(["koc", "mid", "macro", "top"])
            followers = {
                "koc": rng.randint(10000, 100000),
                "mid": rng.randint(100000, 1000000),
                "macro": rng.randint(1000000, 5000000),
                "top": rng.randint(5000000, 50000000),
            }[follower_tier]

            avg_gmv = round(followers * rng.uniform(0.001, 0.05), 2)
            dto = InfluencerDTO(
                platform="douyin",
                platform_uid=f"mock_dy_{i:04d}",
                nickname=f"Mock达人_{i:04d}",
                avatar_url=f"https://picsum.photos/seed/{i}/200/200",
                category=category,
                sub_categories=rng.sample(_CATEGORIES, k=rng.randint(1, 3)),
                followers_count=followers,
                avg_likes=rng.randint(1000, 500000),
                avg_comments=rng.randint(100, 50000),
                avg_shares=rng.randint(50, 20000),
                engagement_rate=round(rng.uniform(0.5, 8.0), 2),
                avg_gmv=avg_gmv,
                avg_sales=rng.randint(100, 50000),
                price_range_min=rng.randint(1000, 50000),
                price_range_max=rng.randint(50000, 200000),
                demographics={
                    "age_18_24": round(rng.uniform(0.1, 0.5), 2),
                    "age_25_34": round(rng.uniform(0.2, 0.5), 2),
                    "age_35_plus": round(1 - rng.uniform(0.3, 0.7), 2),
                    "gender_male": round(rng.uniform(0.2, 0.8), 2),
                    "top_cities": rng.sample(_CITIES, k=3),
                },
                content_style=rng.sample(_CONTENT_STYLES, k=rng.randint(2, 4)),
                brand_history=[
                    {"brand": rng.choice(_BRANDS), "year": rng.randint(2023, 2026)}
                    for _ in range(rng.randint(0, 3))
                ],
                data_source="mock",
            )
            # Adjust age_35_plus to make sum ~1
            total = dto.demographics["age_18_24"] + dto.demographics["age_25_34"]
            dto.demographics["age_35_plus"] = round(1.0 - total, 2)
            self._influencers.append(dto)

    async def search_influencers(
        self, criteria: SearchCriteria
    ) -> tuple[list[InfluencerDTO], int]:
        results = self._influencers[:]

        if criteria.keyword:
            kw = criteria.keyword.lower()
            results = [r for r in results if kw in r.nickname.lower() or kw in r.category.lower()]

        if criteria.category:
            results = [r for r in results if r.category == criteria.category]

        if criteria.follower_min is not None:
            results = [r for r in results if r.followers_count >= criteria.follower_min]
        if criteria.follower_max is not None:
            results = [r for r in results if r.followers_count <= criteria.follower_max]

        if criteria.engagement_min is not None:
            results = [r for r in results if r.engagement_rate >= criteria.engagement_min]
        if criteria.engagement_max is not None:
            results = [r for r in results if r.engagement_rate <= criteria.engagement_max]

        if criteria.price_min is not None:
            results = [r for r in results if r.price_range_max >= criteria.price_min]
        if criteria.price_max is not None:
            results = [r for r in results if r.price_range_min <= criteria.price_max]

        if criteria.gmv_min is not None:
            results = [r for r in results if r.avg_gmv >= criteria.gmv_min]

        reverse = criteria.sort_order == "desc"
        results.sort(key=lambda r: getattr(r, criteria.sort_by, 0), reverse=reverse)

        total = len(results)
        start = (criteria.page - 1) * criteria.page_size
        end = start + criteria.page_size
        return results[start:end], total

    async def get_influencer_detail(self, platform_uid: str) -> InfluencerDTO | None:
        for r in self._influencers:
            if r.platform_uid == platform_uid:
                return r
        return None

    async def health_check(self) -> bool:
        return True
