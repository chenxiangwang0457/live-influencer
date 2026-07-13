# backend/app/influencer/models/feedback.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from deerflow.persistence.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    selection_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("selections.id", ondelete="SET NULL"), nullable=True
    )
    influencer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str | None] = mapped_column(Text, nullable=True)
    # B方案扩展点：品牌方手动评分(A方案) + 平台自动回传(B方案)
    # 当接入抖音/快手等平台投放API后，可通过 webhook 或定时任务自动写入此字段：
    #   {"gmv": 500000, "roi": 3.2, "conversion_rate": 0.05, "impressions": 1000000}
    # 配合 feedbacks 表的 rating/review 字段，双重反馈驱动评分模型优化
    sales_performance: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class InfluencerScore(Base):
    __tablename__ = "influencer_scores"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    influencer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dimension: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # overall / engagement / sales / professionalism
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
