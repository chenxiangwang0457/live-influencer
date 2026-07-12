# backend/app/influencer/routers/influencers.py
from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.influencer.models.selection import Selection, SelectionInfluencer
from app.influencer.services.data_platform.base import SearchCriteria

router = APIRouter(prefix="/api/influencer", tags=["influencers"])


# ═══════════════════════════════════════════
#  Request Schemas
# ═══════════════════════════════════════════

class CreateSelectionRequest(BaseModel):
    title: str
    goal: str | None = None
    criteria: dict | None = None
    thread_id: str | None = None


class UpdateSelectionRequest(BaseModel):
    title: str | None = None
    goal: str | None = None
    criteria: dict | None = None
    status: str | None = None


class AddCandidateRequest(BaseModel):
    influencer_id: str
    added_by: str = "manual_add"


class UpdateCandidateRequest(BaseModel):
    status: str | None = None
    notes: str | None = None


# ═══════════════════════════════════════════
#  DB helper
# ═══════════════════════════════════════════

def _get_session_factory():
    from deerflow.persistence.engine import get_session_factory

    sf = get_session_factory()
    if sf is None:
        raise RuntimeError(
            "Persistence engine not initialized. "
            "The selection API requires a SQL database (backend=sqlite or postgres)."
        )
    return sf


# ═══════════════════════════════════════════
#  Selection Routes (MUST come before /{platform_uid})
# ═══════════════════════════════════════════

@router.post("/selections")
async def create_selection(body: CreateSelectionRequest, request: Request):
    """Create a new influencer selection task."""
    sel = Selection(
        title=body.title,
        goal=body.goal,
        criteria=body.criteria,
        thread_id=body.thread_id,
        status="draft",
    )
    sf = _get_session_factory()
    async with sf() as session:
        session.add(sel)
        await session.commit()
        return {
            "id": sel.id,
            "title": sel.title,
            "goal": sel.goal,
            "criteria": sel.criteria,
            "status": sel.status,
            "thread_id": sel.thread_id,
            "created_at": sel.created_at.isoformat() if sel.created_at else None,
        }


@router.get("/selections")
async def list_selections(
    request: Request,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """List selections with optional status filter."""
    sf = _get_session_factory()
    async with sf() as session:
        stmt = select(Selection).order_by(Selection.created_at.desc())
        if status:
            stmt = stmt.where(Selection.status == status)

        count_stmt = select(func.count()).select_from(Selection)
        if status:
            count_stmt = count_stmt.where(Selection.status == status)
        total = (await session.execute(count_stmt)).scalar() or 0

        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        result = await session.execute(stmt)
        rows = result.scalars().all()

        return {
            "data": [
                {
                    "id": r.id,
                    "title": r.title,
                    "goal": r.goal,
                    "status": r.status,
                    "criteria": r.criteria,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }


@router.get("/selections/{selection_id}")
async def get_selection(selection_id: str, request: Request):
    """Get selection detail with candidates."""
    sf = _get_session_factory()
    async with sf() as session:
        stmt = (
            select(Selection)
            .where(Selection.id == selection_id)
            .options(selectinload(Selection.candidates))
        )
        result = await session.execute(stmt)
        sel = result.scalar_one_or_none()

        if sel is None:
            return JSONResponse(status_code=404, content={"detail": "Selection not found"})

        candidates = []
        for c in sel.candidates:
            candidates.append({
                "id": c.id,
                "influencer_id": c.influencer_id,
                "match_score": c.match_score,
                "match_reason": c.match_reason,
                "status": c.status,
                "added_by": c.added_by,
                "notes": c.notes,
            })

        return {
            "id": sel.id,
            "title": sel.title,
            "goal": sel.goal,
            "criteria": sel.criteria,
            "status": sel.status,
            "thread_id": sel.thread_id,
            "result_summary": sel.result_summary,
            "candidates": candidates,
            "created_at": sel.created_at.isoformat() if sel.created_at else None,
            "updated_at": sel.updated_at.isoformat() if sel.updated_at else None,
        }


@router.put("/selections/{selection_id}")
async def update_selection(selection_id: str, body: UpdateSelectionRequest, request: Request):
    """Update a selection's fields."""
    sf = _get_session_factory()
    async with sf() as session:
        result = await session.execute(
            select(Selection).where(Selection.id == selection_id)
        )
        sel = result.scalar_one_or_none()
        if sel is None:
            return JSONResponse(status_code=404, content={"detail": "Selection not found"})

        if body.title is not None:
            sel.title = body.title
        if body.goal is not None:
            sel.goal = body.goal
        if body.criteria is not None:
            sel.criteria = body.criteria
        if body.status is not None:
            sel.status = body.status

        await session.commit()
        return {"id": sel.id, "title": sel.title, "status": sel.status, "goal": sel.goal}


@router.post("/selections/{selection_id}/candidates")
async def add_candidate(selection_id: str, body: AddCandidateRequest, request: Request):
    """Add a candidate influencer to a selection."""
    from app.influencer.models.influencer import Influencer

    sf = _get_session_factory()
    async with sf() as session:
        sel_result = await session.execute(
            select(Selection).where(Selection.id == selection_id)
        )
        if sel_result.scalar_one_or_none() is None:
            return JSONResponse(status_code=404, content={"detail": "Selection not found"})

        # Look up influencer by platform_uid or id
        inf_result = await session.execute(
            select(Influencer).where(
                (Influencer.platform_uid == body.influencer_id)
                | (Influencer.id == body.influencer_id)
            )
        )
        influencer = inf_result.scalar_one_or_none()

        # If not in DB, sync from adapter
        if influencer is None:
            adapter = request.app.state.influencer_adapter
            dto = await adapter.get_influencer_detail(body.influencer_id)
            if dto is None:
                return JSONResponse(
                    status_code=404, content={"detail": "Influencer not found"}
                )
            influencer = Influencer(**dto.to_orm_dict())
            session.add(influencer)
            await session.flush()

        link = SelectionInfluencer(
            selection_id=selection_id,
            influencer_id=influencer.id,
            added_by=body.added_by,
        )
        session.add(link)
        await session.commit()
        return {"id": link.id, "status": link.status}


@router.delete("/selections/{selection_id}/candidates/{candidate_id}")
async def remove_candidate(selection_id: str, candidate_id: str, request: Request):
    """Remove a candidate from a selection."""
    sf = _get_session_factory()
    async with sf() as session:
        result = await session.execute(
            select(SelectionInfluencer).where(
                SelectionInfluencer.id == candidate_id,
                SelectionInfluencer.selection_id == selection_id,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            return JSONResponse(status_code=404, content={"detail": "Candidate not found"})
        await session.delete(link)
        await session.commit()
        return {"detail": "deleted"}


@router.patch("/selections/{selection_id}/candidates/{candidate_id}")
async def update_candidate(
    selection_id: str, candidate_id: str, body: UpdateCandidateRequest, request: Request
):
    """Update a candidate's status or notes."""
    sf = _get_session_factory()
    async with sf() as session:
        result = await session.execute(
            select(SelectionInfluencer).where(
                SelectionInfluencer.id == candidate_id,
                SelectionInfluencer.selection_id == selection_id,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            return JSONResponse(status_code=404, content={"detail": "Candidate not found"})
        if body.status is not None:
            link.status = body.status
        if body.notes is not None:
            link.notes = body.notes
        await session.commit()
        return {"id": link.id, "status": link.status}


# ═══════════════════════════════════════════
#  Influencer Search & Detail Routes
# ═══════════════════════════════════════════

@router.get("/search")
async def search_influencers(
    request: Request,
    keyword: str | None = Query(default=None),
    platform: str = Query(default="douyin"),
    category: str | None = Query(default=None),
    follower_min: int | None = Query(default=None),
    follower_max: int | None = Query(default=None),
    engagement_min: float | None = Query(default=None),
    engagement_max: float | None = Query(default=None),
    price_min: int | None = Query(default=None),
    price_max: int | None = Query(default=None),
    gmv_min: float | None = Query(default=None),
    sort_by: str = Query(default="followers_count"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    criteria = SearchCriteria(
        keyword=keyword,
        platform=platform,
        category=category,
        follower_min=follower_min,
        follower_max=follower_max,
        engagement_min=engagement_min,
        engagement_max=engagement_max,
        price_min=price_min,
        price_max=price_max,
        gmv_min=gmv_min,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    adapter = request.app.state.influencer_adapter
    results, total = await adapter.search_influencers(criteria)
    return {
        "data": [r.__dict__ for r in results],
        "total": total,
        "page": criteria.page,
        "page_size": criteria.page_size,
    }


@router.get("/{platform_uid}")
async def get_influencer_detail(request: Request, platform_uid: str):
    adapter = request.app.state.influencer_adapter
    result = await adapter.get_influencer_detail(platform_uid)
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Influencer not found"})
    return result.__dict__


@router.get("/{platform_uid}/history")
async def get_influencer_history(request: Request, platform_uid: str):
    adapter = request.app.state.influencer_adapter
    result = await adapter.get_influencer_detail(platform_uid)
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Influencer not found"})
    return {"platform_uid": platform_uid, "brand_history": result.brand_history}
