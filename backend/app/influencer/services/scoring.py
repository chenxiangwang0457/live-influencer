# backend/app/influencer/services/scoring.py
from __future__ import annotations

import math

from app.influencer.services.data_platform.base import InfluencerDTO

_DEFAULT_WEIGHTS = {
    "match": 0.35,
    "reach": 0.25,
    "sales": 0.25,
    "value": 0.15,
}


def get_default_weights() -> dict[str, float]:
    return dict(_DEFAULT_WEIGHTS)


class ScoreEngine:
    """四维达人评分引擎: 匹配度 + 传播力 + 带货力 + 性价比"""

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or get_default_weights()

    def score_influencer(
        self, influencer: InfluencerDTO, criteria: dict
    ) -> dict[str, float]:
        return {
            "match_score": self._score_match(influencer, criteria),
            "reach_score": self._score_reach(influencer),
            "sales_score": self._score_sales(influencer),
            "value_score": self._score_value(influencer),
        }

    def calculate_total(
        self, influencer: InfluencerDTO, criteria: dict
    ) -> float:
        scores = self.score_influencer(influencer, criteria)
        total = sum(
            scores[f"{dim}_score"] * weight
            for dim, weight in self.weights.items()
        )
        return round(total, 2)

    # ── Private scoring methods ──

    def _score_match(self, inf: InfluencerDTO, criteria: dict) -> float:
        """匹配度: 类目重合 (60%) + 粉丝画像契合 (40%)"""
        target_cat = criteria.get("category", "")
        cat_score = 100.0 if not target_cat else (
            100.0 if inf.category == target_cat else
            50.0 if target_cat in (inf.sub_categories or []) else
            20.0
        )
        # Demographics match: prefer young audience for most brands
        demo = inf.demographics or {}
        young_ratio = demo.get("age_18_24", 0) + demo.get("age_25_34", 0)
        demo_score = min(100.0, young_ratio * 100 + 20)
        return round(cat_score * 0.6 + demo_score * 0.4, 2)

    def _score_reach(self, inf: InfluencerDTO) -> float:
        """传播力: 粉丝量归一化 (50%) + 互动率 (50%)"""
        follower_log = math.log10(max(inf.followers_count, 1))
        follower_norm = min(100.0, (follower_log / 7.0) * 100)  # 7 ≈ log10(10M)
        engagement_norm = min(100.0, (inf.engagement_rate / 10.0) * 100)  # 10% as benchmark
        return round(follower_norm * 0.5 + engagement_norm * 0.5, 2)

    def _score_sales(self, inf: InfluencerDTO) -> float:
        """带货力: GMV (50%) + 销量 (30%) + 转化暗示 (20%)"""
        gmv_log = math.log10(max(inf.avg_gmv, 1))
        gmv_norm = min(100.0, (gmv_log / 6.0) * 100)  # 6 ≈ log10(1M)
        sales_log = math.log10(max(inf.avg_sales, 1))
        sales_norm = min(100.0, (sales_log / 5.0) * 100)
        # Conversion proxy: sales per follower
        conversion = (inf.avg_sales / max(inf.followers_count, 1)) * 100
        conversion_norm = min(100.0, conversion * 1000)
        return round(gmv_norm * 0.5 + sales_norm * 0.3 + conversion_norm * 0.2, 2)

    def _score_value(self, inf: InfluencerDTO) -> float:
        """性价比: 预估 ROI = (场均GMV × 0.01) / (报价中位数)"""
        avg_price = (inf.price_range_min + inf.price_range_max) / 2
        if avg_price <= 0:
            return 50.0
        roi = (inf.avg_gmv * 0.01) / avg_price  # rough estimate
        return round(min(100.0, roi * 200), 2)
