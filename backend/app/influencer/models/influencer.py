# backend/app/influencer/models/influencer.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from deerflow.persistence.base import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    platform: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    platform_uid: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    nickname: Mapped[str] = mapped_column(String(128), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(512), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sub_categories: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    followers_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_comments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_gmv: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_sales: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price_range_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price_range_max: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    demographics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content_style: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    brand_history: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_source: Mapped[str] = mapped_column(
        String(32), nullable=False, default="mock"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
