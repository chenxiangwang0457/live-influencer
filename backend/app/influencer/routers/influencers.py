# backend/app/influencer/routers/influencers.py
from __future__ import annotations

import json

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


@router.post("/selections/{selection_id}/analyze")
async def analyze_selection(selection_id: str, request: Request):
    """Run AI analysis on a selection: score candidates and generate report."""
    from app.influencer.models.influencer import Influencer
    from app.influencer.services.matching import MatchingEngine

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

        if not sel.candidates:
            return JSONResponse(status_code=400, content={"detail": "No candidates in selection"})

        # Load influencer data for each candidate
        inf_map = {}
        for c in sel.candidates:
            inf_result = await session.execute(
                select(Influencer).where(Influencer.id == c.influencer_id)
            )
            inf = inf_result.scalar_one_or_none()
            if inf is not None:
                inf_map[c.influencer_id] = inf

        if not inf_map:
            return JSONResponse(status_code=400, content={"detail": "No influencer data found"})

        # Run matching engine on candidates
        engine = MatchingEngine()
        criteria = sel.criteria or {}

        # Build InfluencerDTO list from DB models
        from app.influencer.services.data_platform.base import InfluencerDTO

        dtos = []
        for inf in inf_map.values():
            dto = InfluencerDTO(
                platform=inf.platform,
                platform_uid=inf.platform_uid,
                nickname=inf.nickname,
                avatar_url=inf.avatar_url or "",
                category=inf.category,
                sub_categories=inf.sub_categories or [],
                followers_count=inf.followers_count,
                avg_likes=inf.avg_likes,
                avg_comments=inf.avg_comments,
                avg_shares=inf.avg_shares,
                engagement_rate=inf.engagement_rate,
                avg_gmv=inf.avg_gmv,
                avg_sales=inf.avg_sales,
                price_range_min=inf.price_range_min,
                price_range_max=inf.price_range_max,
                demographics=inf.demographics or {},
                content_style=inf.content_style or [],
                brand_history=inf.brand_history or [],
                data_source=inf.data_source,
            )
            dtos.append(dto)

        # Score all candidates
        scored = engine.match_batch(dtos, criteria)

        # Update candidate match_scores in DB
        score_map = {r.influencer.platform_uid: r for r in scored}
        for c in sel.candidates:
            inf = inf_map.get(c.influencer_id)
            if inf and inf.platform_uid in score_map:
                r = score_map[inf.platform_uid]
                c.match_score = r.total_score
                c.match_reason = (
                    f"匹配度{r.match_score:.0f} | 传播力{r.reach_score:.0f} | "
                    f"带货力{r.sales_score:.0f} | 性价比{r.value_score:.0f}"
                )

        await session.commit()

        # Build report data
        picks = []
        for r in scored[:10]:
            picks.append({
                "platform_uid": r.influencer.platform_uid,
                "nickname": r.influencer.nickname,
                "score": r.total_score,
                "reason": (
                    f"匹配度{r.match_score:.0f} | 传播力{r.reach_score:.0f} | "
                    f"带货力{r.sales_score:.0f} | 性价比{r.value_score:.0f}"
                ),
            })

        # Use the report tool to generate markdown
        from deerflow.tools.influencer.recommend_report import build_recommend_report_tool

        report_tool = build_recommend_report_tool(engine)
        report = await report_tool.ainvoke({
            "selection_json": json.dumps({"criteria": criteria, "picks": picks})
        })

        return {
            "report": report,
            "candidates": [
                {
                    "id": c.id,
                    "influencer_id": c.influencer_id,
                    "match_score": c.match_score,
                    "match_reason": c.match_reason,
                }
                for c in sel.candidates
            ],
        }


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
    import logging
    _log = logging.getLogger(__name__)

    from app.influencer.models.influencer import Influencer

    # First try DB lookup by id or platform_uid
    try:
        sf = _get_session_factory()
        _log.info(f"DB lookup for influencer: {platform_uid}")
        async with sf() as session:
            inf_result = await session.execute(
                select(Influencer).where(
                    (Influencer.id == platform_uid)
                    | (Influencer.platform_uid == platform_uid)
                )
            )
            db_inf = inf_result.scalar_one_or_none()
            if db_inf is not None:
                return {
                    "platform": db_inf.platform,
                    "platform_uid": db_inf.platform_uid,
                    "nickname": db_inf.nickname,
                    "avatar_url": db_inf.avatar_url or "",
                    "category": db_inf.category,
                    "sub_categories": db_inf.sub_categories or [],
                    "followers_count": db_inf.followers_count,
                    "avg_likes": db_inf.avg_likes,
                    "avg_comments": db_inf.avg_comments,
                    "avg_shares": db_inf.avg_shares,
                    "engagement_rate": db_inf.engagement_rate,
                    "avg_gmv": db_inf.avg_gmv,
                    "avg_sales": db_inf.avg_sales,
                    "price_range_min": db_inf.price_range_min,
                    "price_range_max": db_inf.price_range_max,
                    "demographics": db_inf.demographics or {},
                    "content_style": db_inf.content_style or [],
                    "brand_history": db_inf.brand_history or [],
                    "data_source": db_inf.data_source,
                }
    except RuntimeError as e:
        _log.warning(f"DB not available for influencer lookup: {e}")

    # Fall back to adapter (mock data or external platform)
    adapter = request.app.state.influencer_adapter
    result = await adapter.get_influencer_detail(platform_uid)
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Influencer not found"})
    return result.__dict__


@router.get("/{platform_uid}/history")
async def get_influencer_history(request: Request, platform_uid: str):
    from app.influencer.models.influencer import Influencer

    # First try DB lookup
    try:
        sf = _get_session_factory()
        async with sf() as session:
            inf_result = await session.execute(
                select(Influencer).where(
                    (Influencer.id == platform_uid)
                    | (Influencer.platform_uid == platform_uid)
                )
            )
            db_inf = inf_result.scalar_one_or_none()
            if db_inf is not None:
                return {
                    "platform_uid": db_inf.platform_uid,
                    "brand_history": db_inf.brand_history or [],
                }
    except RuntimeError:
        pass

    # Fall back to adapter
    adapter = request.app.state.influencer_adapter
    result = await adapter.get_influencer_detail(platform_uid)
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Influencer not found"})
    return {"platform_uid": platform_uid, "brand_history": result.brand_history}
