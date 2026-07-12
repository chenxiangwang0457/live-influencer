# backend/app/influencer/services/data_platform/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class SearchCriteria(BaseModel):
    """达人搜索条件"""

    keyword: str | None = Field(default=None, description="关键词搜索")
    platform: str = Field(default="douyin", description="平台")
    category: str | None = Field(default=None, description="主营类目")
    follower_min: int | None = Field(default=None, description="最低粉丝数")
    follower_max: int | None = Field(default=None, description="最高粉丝数")
    engagement_min: float | None = Field(default=None, description="最低互动率")
    engagement_max: float | None = Field(default=None, description="最高互动率")
    price_min: int | None = Field(default=None, description="最低报价")
    price_max: int | None = Field(default=None, description="最高报价")
    gmv_min: float | None = Field(default=None, description="最低场均GMV")
    sort_by: str = Field(default="followers_count", description="排序字段")
    sort_order: str = Field(default="desc", description="排序方向 asc/desc")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


@dataclass
class InfluencerDTO:
    """平台无关的达人数据传输对象"""

    platform: str
    platform_uid: str
    nickname: str
    avatar_url: str = ""
    category: str = ""
    sub_categories: list[str] = field(default_factory=list)
    followers_count: int = 0
    avg_likes: int = 0
    avg_comments: int = 0
    avg_shares: int = 0
    engagement_rate: float = 0.0
    avg_gmv: float = 0.0
    avg_sales: int = 0
    price_range_min: int = 0
    price_range_max: int = 0
    demographics: dict = field(default_factory=dict)
    content_style: list[str] = field(default_factory=list)
    brand_history: list[dict] = field(default_factory=list)
    data_source: str = "mock"

    def to_orm_dict(self) -> dict:
        """Convert to dict suitable for Influencer ORM creation"""
        result = {
            "platform": self.platform,
            "platform_uid": self.platform_uid,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "category": self.category,
            "sub_categories": self.sub_categories,
            "followers_count": self.followers_count,
            "avg_likes": self.avg_likes,
            "avg_comments": self.avg_comments,
            "avg_shares": self.avg_shares,
            "engagement_rate": self.engagement_rate,
            "avg_gmv": self.avg_gmv,
            "avg_sales": self.avg_sales,
            "price_range_min": self.price_range_min,
            "price_range_max": self.price_range_max,
            "demographics": self.demographics,
            "content_style": self.content_style,
            "brand_history": self.brand_history,
            "data_source": self.data_source,
        }
        return result


class DataPlatformAdapter(ABC):
    """第三方数据平台统一适配接口"""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """返回平台标识: douyin / kuaishou / xiaohongshu"""
        ...

    @abstractmethod
    async def search_influencers(self, criteria: SearchCriteria) -> tuple[list[InfluencerDTO], int]:
        """搜索达人，返回 (结果列表, 总数)"""
        ...

    @abstractmethod
    async def get_influencer_detail(self, platform_uid: str) -> InfluencerDTO | None:
        """获取单个达人完整画像，不存在返回 None"""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """平台 API 连通性检查"""
        ...
