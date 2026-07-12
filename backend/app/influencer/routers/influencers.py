# backend/app/influencer/routers/influencers.py
from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.influencer.services.data_platform.base import SearchCriteria

router = APIRouter(prefix="/api/influencer", tags=["influencers"])


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
