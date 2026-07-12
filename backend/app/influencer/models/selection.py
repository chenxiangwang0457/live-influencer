# backend/app/influencer/models/selection.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from deerflow.persistence.base import Base


class Selection(Base):
    __tablename__ = "selections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    thread_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft", index=True
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    candidates: Mapped[list["SelectionInfluencer"]] = relationship(
        back_populates="selection", cascade="all, delete-orphan"
    )


class SelectionInfluencer(Base):
    __tablename__ = "selection_influencers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    selection_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("selections.id", ondelete="CASCADE"), nullable=False
    )
    influencer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    match_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="shortlisted"
    )
    added_by: Mapped[str] = mapped_column(
        String(32), nullable=False, default="ai_recommend"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    selection: Mapped["Selection"] = relationship(back_populates="candidates")
