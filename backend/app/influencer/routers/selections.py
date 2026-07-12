# backend/app/influencer/routers/selections.py
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.influencer.models.selection import Selection, SelectionInfluencer

router = APIRouter(prefix="/api/influencer/selections", tags=["selections"])


# ── Request schemas ──

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


# ── DB session helper ──

def _get_session_factory():
    """Return the async session factory, raising if not initialized."""
    from deerflow.persistence.engine import get_session_factory

    sf = get_session_factory()
    if sf is None:
        raise RuntimeError(
            "Persistence engine not initialized. "
            "The selection API requires a SQL database (backend=sqlite or postgres)."
        )
    return sf


# ── Routes ──


@router.post("/")
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


@router.get("/")
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


@router.get("/{selection_id}")
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


@router.put("/{selection_id}")
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


@router.post("/{selection_id}/candidates")
async def add_candidate(selection_id: str, body: AddCandidateRequest, request: Request):
    """Add a candidate influencer to a selection."""
    sf = _get_session_factory()
    async with sf() as session:
        # Verify selection exists
        sel_result = await session.execute(
            select(Selection).where(Selection.id == selection_id)
        )
        if sel_result.scalar_one_or_none() is None:
            return JSONResponse(status_code=404, content={"detail": "Selection not found"})

        link = SelectionInfluencer(
            selection_id=selection_id,
            influencer_id=body.influencer_id,
            added_by=body.added_by,
        )
        session.add(link)
        await session.commit()
        return {"id": link.id, "status": link.status}


@router.delete("/{selection_id}/candidates/{candidate_id}")
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


@router.patch("/{selection_id}/candidates/{candidate_id}")
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
