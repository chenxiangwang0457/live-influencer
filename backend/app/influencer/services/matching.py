# backend/app/influencer/services/matching.py
from __future__ import annotations

from dataclasses import dataclass

from app.influencer.services.data_platform.base import InfluencerDTO
from app.influencer.services.errors import MatchingError
from app.influencer.services.scoring import ScoreEngine


@dataclass
class MatchResult:
    influencer: InfluencerDTO
    match_score: float
    reach_score: float
    sales_score: float
    value_score: float
    total_score: float


class MatchingEngine:
    """达人匹配推荐引擎: 批量打分、排序、Top-N"""

    def __init__(self, score_engine: ScoreEngine | None = None):
        self._scorer = score_engine or ScoreEngine()

    def match_batch(
        self, influencers: list[InfluencerDTO], criteria: dict
    ) -> list[MatchResult]:
        if not influencers:
            return []
        results = []
        for inf in influencers:
            try:
                scores = self._scorer.score_influencer(inf, criteria)
                total = self._scorer.calculate_total(inf, criteria)
            except Exception as e:
                raise MatchingError(
                    f"Failed to score influencer {inf.platform_uid}: {e}"
                ) from e
            results.append(
                MatchResult(
                    influencer=inf,
                    match_score=scores["match_score"],
                    reach_score=scores["reach_score"],
                    sales_score=scores["sales_score"],
                    value_score=scores["value_score"],
                    total_score=total,
                )
            )
        results.sort(key=lambda r: r.total_score, reverse=True)
        return results

    def top_n(
        self, influencers: list[InfluencerDTO], criteria: dict, n: int = 10
    ) -> list[MatchResult]:
        return self.match_batch(influencers, criteria)[:n]
