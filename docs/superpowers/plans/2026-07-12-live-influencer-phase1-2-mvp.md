# Live-Influencer MVP (Phase 1-2) 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建直播带货选达人平台 MVP：达人搜索/浏览 + 选人任务管理 + 评分匹配引擎 + Agent 工具

**Architecture:** 在 DeerFlow 现有 `app/` 和 `deerflow/` 体系内新增 `influencer` 模块，遵循 App Router + FastAPI Router + SQLAlchemy + Agent Tool 的现有模式

**Tech Stack:** Python 3.12+, FastAPI, SQLAlchemy, Alembic, Pydantic, Next.js 16, React 19, TypeScript 5.8, Tailwind CSS 4, TanStack Query

## Global Constraints

- harner → app 单向依赖，`deerflow.*` 不能 import `app.*`
- 所有 ORM 变更必须有 Alembic migration
- 前端使用 Server Components by default，仅交互组件标记 `"use client"`
- API 复用 Gateway 已有认证和 CSRF 中间件
- 后端 TDD：先写 failing test → 实现 → 测试通过 → 提交
- 前端 `pnpm check` 必须在提交前通过

---

## 文件结构总览

```
backend/
├── app/influencer/
│   ├── __init__.py
│   ├── config.py                         # Task 5: 配置解析
│   ├── models/
│   │   ├── __init__.py                   # Task 1: 模型注册
│   │   ├── influencer.py                 # Task 1: 达人画像 ORM
│   │   ├── selection.py                  # Task 7: 选人任务 ORM
│   │   └── feedback.py                   # Task 7: 反馈 ORM (预留)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_platform/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # Task 2: 抽象基类 + DTO
│   │   │   └── mock.py                   # Task 3: Mock 适配器
│   │   ├── scoring.py                    # Task 8: 四维评分引擎
│   │   └── matching.py                   # Task 9: 匹配推荐引擎
│   └── routers/
│       ├── __init__.py
│       ├── influencers.py                # Task 4: 达人搜索/详情 API
│       └── selections.py                 # Task 10: 选人任务 API
│
├── packages/harness/deerflow/
│   └── tools/influencer/
│       ├── __init__.py                   # Task 11: 工具注册
│       ├── search_influencers.py         # Task 11: search 工具
│       ├── compare_influencers.py        # Task 12: compare 工具
│       └── recommend_report.py           # Task 12: report 工具
│
├── tests/influencer/
│   ├── __init__.py
│   ├── conftest.py                       # Task 1: fixtures
│   ├── test_models.py                    # Task 1
│   ├── test_data_platform.py             # Task 3
│   ├── test_api_influencers.py           # Task 4
│   ├── test_scoring.py                   # Task 8
│   ├── test_matching.py                  # Task 9
│   ├── test_api_selections.py            # Task 10
│   └── test_agent_tools.py              # Task 12
│
frontend/src/
├── core/influencer/
│   ├── types.ts                          # Task 6: 类型定义
│   └── api.ts                            # Task 6: API 客户端
├── app/workspace/influencer/
│   ├── page.tsx                          # Task 13: 达人广场页
│   ├── [id]/page.tsx                     # Task 14: 达人详情页
│   └── selections/
│       ├── page.tsx                      # Task 15: 选人任务列表
│       └── [id]/page.tsx                 # Task 16: 任务详情 + 对比
└── components/workspace/influencer/
    ├── influencer-card.tsx               # Task 13
    ├── filter-panel.tsx                  # Task 13
    ├── influencer-detail.tsx             # Task 14
    ├── candidate-table.tsx               # Task 16
    ├── compare-drawer.tsx                # Task 16
    └── messages/
        ├── search-result-msg.tsx         # Task 17: 聊天消息渲染
        └── compare-table-msg.tsx         # Task 17
```

---

### Task 1: 数据库模型 + Alembic 迁移

**Files:**
- Create: `backend/app/influencer/__init__.py`
- Create: `backend/app/influencer/models/__init__.py`
- Create: `backend/app/influencer/models/influencer.py`
- Modify: `backend/app/gateway/app.py` (register router placeholder)
- Create: `backend/tests/influencer/__init__.py`
- Create: `backend/tests/influencer/conftest.py`
- Create: `backend/tests/influencer/test_models.py`

**Interfaces:**
- Produces: `Influencer` ORM model with all fields from spec section 3.1
- Produces: `Base.metadata` includes `influencers` table via `app/influencer/models/__init__.py`

- [ ] **Step 1: Create `app/influencer/__init__.py`**

```python
# backend/app/influencer/__init__.py
"""DeerFlow Influencer Selection Module"""
```

- [ ] **Step 2: Create `app/influencer/models/__init__.py`**

```python
# backend/app/influencer/models/__init__.py
from app.influencer.models.influencer import Influencer

__all__ = ["Influencer"]
```

- [ ] **Step 3: Create `app/influencer/models/influencer.py`**

```python
# backend/app/influencer/models/influencer.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
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
```

- [ ] **Step 4: Generate Alembic migration**

```bash
cd backend && make migrate-rev MSG="add influencers table"
```

- [ ] **Step 5: Verify migration includes `influencers` table**

```bash
cd backend && alembic upgrade head && python -c "
from deerflow.persistence.engine import init_engine
import asyncio
async def check():
    engine = await init_engine()
    async with engine.connect() as conn:
        result = await conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"influencers\"')
        assert result.fetchone() is not None, 'influencers table not found'
        print('OK: influencers table exists')
asyncio.run(check())
"
```

- [ ] **Step 6: Create test fixtures `tests/influencer/conftest.py`**

```python
# backend/tests/influencer/conftest.py
from __future__ import annotations

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from deerflow.persistence.base import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()
```

- [ ] **Step 7: Write model test `tests/influencer/test_models.py`**

```python
# backend/tests/influencer/test_models.py
from __future__ import annotations

import pytest
from app.influencer.models.influencer import Influencer


@pytest.mark.asyncio
async def test_create_influencer(db_session):
    influencer = Influencer(
        platform="douyin",
        platform_uid="dy_12345",
        nickname="测试达人",
        category="美妆",
        followers_count=1000000,
        avg_gmv=500000.0,
        price_range_min=10000,
        price_range_max=50000,
    )
    db_session.add(influencer)
    await db_session.commit()
    await db_session.refresh(influencer)

    assert influencer.id is not None
    assert influencer.platform == "douyin"
    assert influencer.platform_uid == "dy_12345"
    assert influencer.nickname == "测试达人"
    assert influencer.category == "美妆"
    assert influencer.followers_count == 1000000
    assert influencer.avg_gmv == 500000.0
    assert influencer.data_source == "mock"
    assert influencer.created_at is not None


@pytest.mark.asyncio
async def test_influencer_defaults(db_session):
    influencer = Influencer(
        platform="douyin",
        platform_uid="dy_000",
        nickname="新人",
        category="食品",
    )
    db_session.add(influencer)
    await db_session.commit()

    assert influencer.followers_count == 0
    assert influencer.engagement_rate == 0.0
    assert influencer.avg_gmv == 0.0
    assert influencer.price_range_min == 0


@pytest.mark.asyncio
async def test_influencer_json_fields(db_session):
    influencer = Influencer(
        platform="douyin",
        platform_uid="dy_json",
        nickname="JSON达人",
        category="服饰",
        demographics={"age_18_24": 0.4, "age_25_34": 0.35, "gender_male": 0.3},
        content_style=["测评", "种草", "vlog"],
        brand_history=[{"brand": "品牌A", "year": 2025}],
    )
    db_session.add(influencer)
    await db_session.commit()
    await db_session.refresh(influencer)

    assert influencer.demographics["age_18_24"] == 0.4
    assert "测评" in influencer.content_style
    assert influencer.brand_history[0]["brand"] == "品牌A"
```

- [ ] **Step 8: Run tests**

```bash
cd backend && python -m pytest tests/influencer/test_models.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 9: Commit**

```bash
git add backend/app/influencer/ backend/tests/influencer/
git add backend/packages/harness/deerflow/persistence/migrations/versions/
git commit -m "feat(influencer): add Influencer ORM model and migration"
```

---

### Task 2: 数据平台抽象基类 + DTO

**Files:**
- Create: `backend/app/influencer/services/__init__.py`
- Create: `backend/app/influencer/services/data_platform/__init__.py`
- Create: `backend/app/influencer/services/data_platform/base.py`

**Interfaces:**
- Consumes: `Influencer` ORM from Task 1
- Produces: `DataPlatformAdapter` ABC with `search_influencers()`, `get_influencer_detail()`, `health_check()`
- Produces: `SearchCriteria` Pydantic model, `InfluencerDTO` dataclass

- [ ] **Step 1: Create service `__init__.py` files**

```python
# backend/app/influencer/services/__init__.py
```

```python
# backend/app/influencer/services/data_platform/__init__.py
from app.influencer.services.data_platform.base import (
    DataPlatformAdapter,
    SearchCriteria,
    InfluencerDTO,
)

__all__ = ["DataPlatformAdapter", "SearchCriteria", "InfluencerDTO"]
```

- [ ] **Step 2: Write `base.py` with abstract interface**

```python
# backend/app/influencer/services/data_platform/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field


class SearchCriteria(BaseModel):
    """达人搜索条件"""
    keyword: Optional[str] = Field(default=None, description="关键词搜索")
    platform: str = Field(default="douyin", description="平台")
    category: Optional[str] = Field(default=None, description="主营类目")
    follower_min: Optional[int] = Field(default=None, description="最低粉丝数")
    follower_max: Optional[int] = Field(default=None, description="最高粉丝数")
    engagement_min: Optional[float] = Field(default=None, description="最低互动率")
    engagement_max: Optional[float] = Field(default=None, description="最高互动率")
    price_min: Optional[int] = Field(default=None, description="最低报价")
    price_max: Optional[int] = Field(default=None, description="最高报价")
    gmv_min: Optional[float] = Field(default=None, description="最低场均GMV")
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
    async def search_influencers(
        self, criteria: SearchCriteria
    ) -> tuple[list[InfluencerDTO], int]:
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
```

- [ ] **Step 3: Verify imports**

```bash
cd backend && python -c "from app.influencer.services.data_platform.base import DataPlatformAdapter, SearchCriteria, InfluencerDTO; print('OK: imports work')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/influencer/services/
git commit -m "feat(influencer): add DataPlatformAdapter ABC and DTOs"
```

---

### Task 3: MockDataAdapter 实现

**Files:**
- Create: `backend/app/influencer/services/data_platform/mock.py`
- Create: `backend/tests/influencer/test_data_platform.py`

**Interfaces:**
- Consumes: `DataPlatformAdapter`, `SearchCriteria`, `InfluencerDTO` from Task 2
- Produces: `MockDataAdapter(DataPlatformAdapter)` with 150 preset influencers

- [ ] **Step 1: Write failing test `tests/influencer/test_data_platform.py`**

```python
# backend/tests/influencer/test_data_platform.py
from __future__ import annotations

import pytest
from app.influencer.services.data_platform.base import SearchCriteria
from app.influencer.services.data_platform.mock import MockDataAdapter


@pytest.fixture
def adapter():
    return MockDataAdapter()


@pytest.mark.asyncio
async def test_platform_name(adapter):
    assert adapter.platform_name == "douyin"


@pytest.mark.asyncio
async def test_health_check(adapter):
    assert await adapter.health_check() is True


@pytest.mark.asyncio
async def test_search_returns_results(adapter):
    criteria = SearchCriteria(platform="douyin", page_size=10)
    results, total = await adapter.search_influencers(criteria)
    assert len(results) == 10
    assert total >= 10


@pytest.mark.asyncio
async def test_search_filter_by_category(adapter):
    criteria = SearchCriteria(platform="douyin", category="美妆", page_size=50)
    results, _ = await adapter.search_influencers(criteria)
    assert len(results) > 0
    for r in results:
        assert r.category == "美妆"


@pytest.mark.asyncio
async def test_search_filter_by_followers(adapter):
    criteria = SearchCriteria(
        platform="douyin", follower_min=100000, follower_max=500000, page_size=50
    )
    results, _ = await adapter.search_influencers(criteria)
    for r in results:
        assert 100000 <= r.followers_count <= 500000


@pytest.mark.asyncio
async def test_search_filter_by_price(adapter):
    criteria = SearchCriteria(platform="douyin", price_max=30000, page_size=50)
    results, _ = await adapter.search_influencers(criteria)
    for r in results:
        assert r.price_range_min <= 30000


@pytest.mark.asyncio
async def test_search_sort_by_gmv_desc(adapter):
    criteria = SearchCriteria(
        platform="douyin", sort_by="avg_gmv", sort_order="desc", page_size=5
    )
    results, _ = await adapter.search_influencers(criteria)
    gmvs = [r.avg_gmv for r in results]
    assert gmvs == sorted(gmvs, reverse=True)


@pytest.mark.asyncio
async def test_search_pagination(adapter):
    criteria1 = SearchCriteria(platform="douyin", page=1, page_size=5)
    criteria2 = SearchCriteria(platform="douyin", page=2, page_size=5)
    r1, _ = await adapter.search_influencers(criteria1)
    r2, _ = await adapter.search_influencers(criteria2)
    uids1 = {r.platform_uid for r in r1}
    uids2 = {r.platform_uid for r in r2}
    assert uids1.isdisjoint(uids2)


@pytest.mark.asyncio
async def test_get_detail_found(adapter):
    # First search to get a known uid
    criteria = SearchCriteria(page_size=1)
    results, _ = await adapter.search_influencers(criteria)
    uid = results[0].platform_uid
    detail = await adapter.get_influencer_detail(uid)
    assert detail is not None
    assert detail.platform_uid == uid
    assert detail.demographics != {}
    assert len(detail.content_style) > 0


@pytest.mark.asyncio
async def test_get_detail_not_found(adapter):
    detail = await adapter.get_influencer_detail("nonexistent_uid")
    assert detail is None
```

- [ ] **Step 2: Run tests (expected all FAIL)**

```bash
cd backend && python -m pytest tests/influencer/test_data_platform.py -v
```

- [ ] **Step 3: Implement `mock.py`**

```python
# backend/app/influencer/services/data_platform/mock.py
from __future__ import annotations

import random
import uuid

from app.influencer.services.data_platform.base import (
    DataPlatformAdapter,
    InfluencerDTO,
    SearchCriteria,
)

_CATEGORIES = ["美妆", "食品", "服饰", "母婴", "3C数码", "家居", "运动", "图书"]
_CONTENT_STYLES = ["测评", "种草", "教程", "vlog", "搞笑", "剧情", "颜值", "知识"]
_CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
_BRANDS = ["欧莱雅", "蒙牛", "耐克", "小米", "宜家", "安踏", "华为", "良品铺子"]

SEED = 42


class MockDataAdapter(DataPlatformAdapter):
    """模拟数据适配器，内置 150 条达人数据用于开发和演示"""

    def __init__(self):
        self._influencers: list[InfluencerDTO] = []
        self._generate_data()

    @property
    def platform_name(self) -> str:
        return "douyin"

    def _generate_data(self) -> None:
        rng = random.Random(SEED)
        for i in range(150):
            category = rng.choice(_CATEGORIES)
            follower_tier = rng.choice(["koc", "mid", "macro", "top"])
            followers = {
                "koc": rng.randint(10000, 100000),
                "mid": rng.randint(100000, 1000000),
                "macro": rng.randint(1000000, 5000000),
                "top": rng.randint(5000000, 50000000),
            }[follower_tier]

            avg_gmv = round(followers * rng.uniform(0.001, 0.05), 2)
            dto = InfluencerDTO(
                platform="douyin",
                platform_uid=f"mock_dy_{i:04d}",
                nickname=f"Mock达人_{i:04d}",
                avatar_url=f"https://picsum.photos/seed/{i}/200/200",
                category=category,
                sub_categories=rng.sample(_CATEGORIES, k=rng.randint(1, 3)),
                followers_count=followers,
                avg_likes=rng.randint(1000, 500000),
                avg_comments=rng.randint(100, 50000),
                avg_shares=rng.randint(50, 20000),
                engagement_rate=round(rng.uniform(0.5, 8.0), 2),
                avg_gmv=avg_gmv,
                avg_sales=rng.randint(100, 50000),
                price_range_min=rng.randint(1000, 50000),
                price_range_max=rng.randint(50000, 200000),
                demographics={
                    "age_18_24": round(rng.uniform(0.1, 0.5), 2),
                    "age_25_34": round(rng.uniform(0.2, 0.5), 2),
                    "age_35_plus": round(1 - rng.uniform(0.3, 0.7), 2),
                    "gender_male": round(rng.uniform(0.2, 0.8), 2),
                    "top_cities": rng.sample(_CITIES, k=3),
                },
                content_style=rng.sample(_CONTENT_STYLES, k=rng.randint(2, 4)),
                brand_history=[
                    {"brand": rng.choice(_BRANDS), "year": rng.randint(2023, 2026)}
                    for _ in range(rng.randint(0, 3))
                ],
                data_source="mock",
            )
            # Adjust age_35_plus to make sum ~1
            total = dto.demographics["age_18_24"] + dto.demographics["age_25_34"]
            dto.demographics["age_35_plus"] = round(1.0 - total, 2)
            self._influencers.append(dto)

    async def search_influencers(
        self, criteria: SearchCriteria
    ) -> tuple[list[InfluencerDTO], int]:
        results = self._influencers[:]

        if criteria.keyword:
            kw = criteria.keyword.lower()
            results = [r for r in results if kw in r.nickname.lower() or kw in r.category.lower()]

        if criteria.category:
            results = [r for r in results if r.category == criteria.category]

        if criteria.follower_min is not None:
            results = [r for r in results if r.followers_count >= criteria.follower_min]
        if criteria.follower_max is not None:
            results = [r for r in results if r.followers_count <= criteria.follower_max]

        if criteria.engagement_min is not None:
            results = [r for r in results if r.engagement_rate >= criteria.engagement_min]
        if criteria.engagement_max is not None:
            results = [r for r in results if r.engagement_rate <= criteria.engagement_max]

        if criteria.price_min is not None:
            results = [r for r in results if r.price_range_max >= criteria.price_min]
        if criteria.price_max is not None:
            results = [r for r in results if r.price_range_min <= criteria.price_max]

        if criteria.gmv_min is not None:
            results = [r for r in results if r.avg_gmv >= criteria.gmv_min]

        reverse = criteria.sort_order == "desc"
        results.sort(key=lambda r: getattr(r, criteria.sort_by, 0), reverse=reverse)

        total = len(results)
        start = (criteria.page - 1) * criteria.page_size
        end = start + criteria.page_size
        return results[start:end], total

    async def get_influencer_detail(self, platform_uid: str) -> InfluencerDTO | None:
        for r in self._influencers:
            if r.platform_uid == platform_uid:
                return r
        return None

    async def health_check(self) -> bool:
        return True
```

- [ ] **Step 4: Run tests (expected all PASS)**

```bash
cd backend && python -m pytest tests/influencer/test_data_platform.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/influencer/services/data_platform/mock.py
git add backend/tests/influencer/test_data_platform.py
git commit -m "feat(influencer): add MockDataAdapter with 150 preset influencers"
```

---

### Task 4: 达人搜索 + 详情 API

**Files:**
- Create: `backend/app/influencer/routers/__init__.py`
- Create: `backend/app/influencer/routers/influencers.py`
- Modify: `backend/app/gateway/app.py` (register influencer router)
- Create: `backend/tests/influencer/test_api_influencers.py`

**Interfaces:**
- Consumes: `MockDataAdapter` from Task 3, `Influencer` ORM from Task 1
- Produces: `GET /api/influencer/search`, `GET /api/influencer/{id}`, `GET /api/influencer/{id}/history`

- [ ] **Step 1: Write failing API test**

```python
# backend/tests/influencer/test_api_influencers.py
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.gateway.app import create_app
from app.influencer.services.data_platform.mock import MockDataAdapter

MOCK_ADAPTER = MockDataAdapter()


def _make_app():
    app = create_app()
    app.state.influencer_adapter = MOCK_ADAPTER
    return app


@pytest.mark.asyncio
async def test_search_influencers_success():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"category": "美妆", "page_size": 5},
        )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert len(data["data"]) == 5
    assert all(r["category"] == "美妆" for r in data["data"])


@pytest.mark.asyncio
async def test_search_with_follower_range():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"follower_min": 100000, "follower_max": 500000, "page_size": 10},
        )
    assert response.status_code == 200
    data = response.json()
    for r in data["data"]:
        assert 100000 <= r["followers_count"] <= 500000


@pytest.mark.asyncio
async def test_search_empty_result():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"category": "不存在的类目"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_search_invalid_page_size():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/influencer/search",
            params={"page_size": 200},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_influencer_detail_found():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/influencer/search", params={"page_size": 1})
        uid = r.json()["data"][0]["platform_uid"]
        detail = await client.get(f"/api/influencer/{uid}")
    assert detail.status_code == 200
    data = detail.json()
    assert data["platform_uid"] == uid
    assert "demographics" in data
    assert "content_style" in data


@pytest.mark.asyncio
async def test_get_influencer_detail_not_found():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/influencer/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Influencer not found"
```

- [ ] **Step 2: Run tests (expected FAIL)**

```bash
cd backend && python -m pytest tests/influencer/test_api_influencers.py -v
```

- [ ] **Step 3: Implement router `routers/influencers.py`**

```python
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
```

- [ ] **Step 4: Create router `__init__.py`**

```python
# backend/app/influencer/routers/__init__.py
from app.influencer.routers.influencers import router as influencers_router

__all__ = ["influencers_router"]
```

- [ ] **Step 5: Register router in Gateway app**

Find the router registration section in `backend/app/gateway/app.py` (in the `create_app()` function) and add:

```python
# In create_app(), alongside other router registrations:
from app.influencer.routers import influencers_router
app.include_router(influencers_router)
```

And in the lifespan (or app startup), initialize the adapter:

```python
# In the lifespan function, add:
from app.influencer.services.data_platform.mock import MockDataAdapter
app.state.influencer_adapter = MockDataAdapter()
```

- [ ] **Step 6: Run API tests (expected PASS)**

```bash
cd backend && python -m pytest tests/influencer/test_api_influencers.py -v
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/influencer/routers/
git add backend/app/gateway/app.py
git add backend/tests/influencer/test_api_influencers.py
git commit -m "feat(influencer): add influencer search and detail API endpoints"
```

---

### Task 5: 配置集成

**Files:**
- Create: `backend/app/influencer/config.py`
- Modify: `config.example.yaml`

**Interfaces:**
- Consumes: DeerFlow config system
- Produces: `InfluencerConfig` Pydantic model, `get_influencer_config()` function

- [ ] **Step 1: Create `config.py`**

```python
# backend/app/influencer/config.py
from __future__ import annotations

from pydantic import BaseModel, Field


class DouyinPlatformConfig(BaseModel):
    api_base: str = "https://api.chanmama.com"
    api_key: str = ""
    timeout: int = 10
    rate_limit: int = 10


class DataPlatformConfig(BaseModel):
    provider: str = Field(default="mock", description="mock | douyin")
    douyin: DouyinPlatformConfig = Field(default_factory=DouyinPlatformConfig)


class InfluencerConfig(BaseModel):
    data_platform: DataPlatformConfig = Field(default_factory=DataPlatformConfig)


def get_influencer_config() -> InfluencerConfig:
    """Parse influencer config section from app config YAML.
    
    Falls back to defaults if section not present.
    """
    try:
        from deerflow.config import get_app_config
        cfg = get_app_config()
        raw = cfg.model_dump().get("influencer", {})
        return InfluencerConfig.model_validate(raw)
    except Exception:
        return InfluencerConfig()
```

- [ ] **Step 2: Add section to `config.example.yaml`**

Append after the existing config sections:

```yaml
# ========== Influencer module ==========
influencer:
  data_platform:
    provider: mock   # mock | douyin
    douyin:
      api_base: "https://api.chanmama.com"
      api_key: "$CHANMAMA_API_KEY"
      timeout: 10
      rate_limit: 10
```

- [ ] **Step 3: Verify config parses**

```bash
cd backend && python -c "
from app.influencer.config import get_influencer_config
cfg = get_influencer_config()
assert cfg.data_platform.provider == 'mock'
print('OK: config parsed', cfg)
"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/influencer/config.py config.example.yaml
git commit -m "feat(influencer): add influencer config section"
```

---

### Task 6: 前端类型定义 + API 客户端

**Files:**
- Create: `frontend/src/core/influencer/types.ts`
- Create: `frontend/src/core/influencer/api.ts`

**Interfaces:**
- Produces: TypeScript types for Influencer, SearchCriteria, SearchResult, etc.
- Produces: API client functions: `searchInfluencers()`, `getInfluencerDetail()`, etc.

- [ ] **Step 1: Write `types.ts`**

```typescript
// frontend/src/core/influencer/types.ts

export interface InfluencerDemographics {
  age_18_24: number;
  age_25_34: number;
  age_35_plus: number;
  gender_male: number;
  top_cities: string[];
}

export interface BrandHistory {
  brand: string;
  year: number;
}

export interface Influencer {
  platform: string;
  platform_uid: string;
  nickname: string;
  avatar_url: string;
  category: string;
  sub_categories: string[];
  followers_count: number;
  avg_likes: number;
  avg_comments: number;
  avg_shares: number;
  engagement_rate: number;
  avg_gmv: number;
  avg_sales: number;
  price_range_min: number;
  price_range_max: number;
  demographics: InfluencerDemographics;
  content_style: string[];
  brand_history: BrandHistory[];
  data_source: string;
}

export interface SearchCriteria {
  keyword?: string;
  platform?: string;
  category?: string;
  follower_min?: number;
  follower_max?: number;
  engagement_min?: number;
  engagement_max?: number;
  price_min?: number;
  price_max?: number;
  gmv_min?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
}

export const CATEGORIES = [
  "美妆", "食品", "服饰", "母婴", "3C数码", "家居", "运动", "图书",
] as const;

export const SORT_OPTIONS = [
  { value: "followers_count", label: "粉丝数" },
  { value: "engagement_rate", label: "互动率" },
  { value: "avg_gmv", label: "场均GMV" },
  { value: "avg_sales", label: "场均销量" },
  { value: "price_range_min", label: "报价" },
] as const;

export function formatFollowers(n: number): string {
  if (n >= 10000_0000) return `${(n / 10000_0000).toFixed(1)}亿`;
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`;
  return n.toString();
}

export function formatPrice(n: number): string {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`;
  return `¥${n.toLocaleString()}`;
}
```

- [ ] **Step 2: Write `api.ts`**

```typescript
// frontend/src/core/influencer/api.ts

import type { Influencer, PaginatedResponse, SearchCriteria } from "./types";

const BASE = "/api/influencer";

export async function searchInfluencers(
  criteria: SearchCriteria,
): Promise<PaginatedResponse<Influencer>> {
  const params = new URLSearchParams();
  if (criteria.keyword) params.set("keyword", criteria.keyword);
  if (criteria.category) params.set("category", criteria.category);
  if (criteria.follower_min) params.set("follower_min", String(criteria.follower_min));
  if (criteria.follower_max) params.set("follower_max", String(criteria.follower_max));
  if (criteria.engagement_min) params.set("engagement_min", String(criteria.engagement_min));
  if (criteria.engagement_max) params.set("engagement_max", String(criteria.engagement_max));
  if (criteria.price_min) params.set("price_min", String(criteria.price_min));
  if (criteria.price_max) params.set("price_max", String(criteria.price_max));
  if (criteria.gmv_min) params.set("gmv_min", String(criteria.gmv_min));
  if (criteria.sort_by) params.set("sort_by", criteria.sort_by);
  if (criteria.sort_order) params.set("sort_order", criteria.sort_order);
  if (criteria.page) params.set("page", String(criteria.page));
  if (criteria.page_size) params.set("page_size", String(criteria.page_size));

  const res = await fetch(`${BASE}/search?${params}`);
  if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
  return res.json();
}

export async function getInfluencerDetail(platformUid: string): Promise<Influencer> {
  const res = await fetch(`${BASE}/${platformUid}`);
  if (!res.ok) throw new Error(`Detail failed: ${res.statusText}`);
  return res.json();
}

export async function getInfluencerHistory(
  platformUid: string,
): Promise<{ platform_uid: string; brand_history: Influencer["brand_history"] }> {
  const res = await fetch(`${BASE}/${platformUid}/history`);
  if (!res.ok) throw new Error(`History failed: ${res.statusText}`);
  return res.json();
}
```

- [ ] **Step 3: Verify typecheck**

```bash
cd frontend && pnpm typecheck
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/core/influencer/
git commit -m "feat(influencer): add frontend types and API client"
```

---

### Task 7: Selection + Feedback ORM 模型

**Files:**
- Modify: `backend/app/influencer/models/__init__.py`
- Create: `backend/app/influencer/models/selection.py`
- Create: `backend/app/influencer/models/feedback.py`
- Modify: `backend/tests/influencer/test_models.py` (add new tests)

**Interfaces:**
- Consumes: `Influencer` from Task 1
- Produces: `Selection`, `SelectionInfluencer`, `Feedback`, `InfluencerScore` ORM models

- [ ] **Step 1: Write models**

```python
# backend/app/influencer/models/selection.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
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
```

```python
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
```

- [ ] **Step 2: Update `models/__init__.py`**

```python
# backend/app/influencer/models/__init__.py
from app.influencer.models.influencer import Influencer
from app.influencer.models.selection import Selection, SelectionInfluencer
from app.influencer.models.feedback import Feedback, InfluencerScore

__all__ = [
    "Influencer",
    "Selection",
    "SelectionInfluencer",
    "Feedback",
    "InfluencerScore",
]
```

- [ ] **Step 3: Add model tests to `test_models.py`**

```python
# Append to backend/tests/influencer/test_models.py

@pytest.mark.asyncio
async def test_create_selection(db_session):
    from app.influencer.models.selection import Selection

    sel = Selection(
        title="2026春季美妆达人筛选",
        goal="找3位美妆类达人中腰部达人",
        criteria={"category": "美妆", "follower_min": 100000, "follower_max": 500000},
    )
    db_session.add(sel)
    await db_session.commit()
    await db_session.refresh(sel)

    assert sel.id is not None
    assert sel.status == "draft"
    assert sel.criteria["category"] == "美妆"


@pytest.mark.asyncio
async def test_create_selection_with_candidates(db_session):
    from app.influencer.models.selection import Selection, SelectionInfluencer
    from app.influencer.models.influencer import Influencer

    inf = Influencer(platform="douyin", platform_uid="dy_test", nickname="测试", category="美妆")
    db_session.add(inf)
    await db_session.flush()

    sel = Selection(title="测试选人任务")
    db_session.add(sel)
    await db_session.flush()

    link = SelectionInfluencer(
        selection_id=sel.id,
        influencer_id=inf.id,
        match_score=85.5,
        match_reason="粉丝画像高度匹配",
        status="shortlisted",
        added_by="ai_recommend",
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(sel)

    assert len(sel.candidates) == 1
    assert sel.candidates[0].match_score == 85.5


@pytest.mark.asyncio
async def test_create_feedback(db_session):
    from app.influencer.models.feedback import Feedback
    from app.influencer.models.influencer import Influencer

    inf = Influencer(platform="douyin", platform_uid="dy_fb", nickname="反馈测试", category="食品")
    db_session.add(inf)
    await db_session.flush()

    fb = Feedback(
        influencer_id=inf.id,
        rating=4,
        review="配合度高，转化效果好",
        tags=["专业", "配合度高"],
    )
    db_session.add(fb)
    await db_session.commit()

    assert fb.rating == 4
    assert "配合度高" in fb.tags
```

- [ ] **Step 4: Generate migration**

```bash
cd backend && make migrate-rev MSG="add selections feedbacks influencer_scores tables"
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/influencer/test_models.py -v
```

Expected: All tests PASS (3 original + 3 new)

- [ ] **Step 6: Commit**

```bash
git add backend/app/influencer/models/ backend/tests/influencer/test_models.py
git add backend/packages/harness/deerflow/persistence/migrations/versions/
git commit -m "feat(influencer): add Selection, Feedback, InfluencerScore ORM models"
```

---

### Task 8: 四维评分引擎

**Files:**
- Create: `backend/app/influencer/services/scoring.py`
- Create: `backend/tests/influencer/test_scoring.py`

**Interfaces:**
- Produces: `ScoreEngine` with `score_influencer(influencer, criteria)` → `dict[str, float]`
- Produces: `get_default_weights()` → `dict` (W1=0.35, W2=0.25, W3=0.25, W4=0.15)

- [ ] **Step 1: Write failing test**

```python
# backend/tests/influencer/test_scoring.py
from __future__ import annotations

import pytest
from app.influencer.services.data_platform.base import InfluencerDTO
from app.influencer.services.scoring import ScoreEngine, get_default_weights


def make_dto(**overrides) -> InfluencerDTO:
    defaults = {
        "platform": "douyin",
        "platform_uid": "test_001",
        "nickname": "测试达人",
        "category": "美妆",
        "sub_categories": ["美妆", "护肤"],
        "followers_count": 500000,
        "engagement_rate": 3.5,
        "avg_gmv": 100000.0,
        "avg_sales": 5000,
        "price_range_min": 10000,
        "price_range_max": 30000,
        "demographics": {"age_18_24": 0.3, "age_25_34": 0.5, "age_35_plus": 0.2, "gender_male": 0.2},
        "content_style": ["测评", "教程"],
        "brand_history": [],
        "data_source": "mock",
    }
    defaults.update(overrides)
    return InfluencerDTO(**defaults)


class TestScoreEngine:

    @pytest.fixture
    def engine(self):
        return ScoreEngine()

    def test_score_is_between_0_and_100(self, engine):
        dto = make_dto()
        criteria = {"category": "美妆"}
        result = engine.score_influencer(dto, criteria)
        for dim in ["match_score", "reach_score", "sales_score", "value_score"]:
            assert 0 <= result[dim] <= 100, f"{dim} out of range: {result[dim]}"

    def test_exact_category_match_high_score(self, engine):
        dto = make_dto(category="美妆", sub_categories=["美妆", "护肤"])
        dto_diff = make_dto(category="食品", sub_categories=["零食"])
        criteria = {"category": "美妆"}
        score_match = engine.score_influencer(dto, criteria)["match_score"]
        score_diff = engine.score_influencer(dto_diff, criteria)["match_score"]
        assert score_match > score_diff, f"match: {score_match} <= diff: {score_diff}"

    def test_higher_followers_more_reach(self, engine):
        dto_big = make_dto(followers_count=5000000)
        dto_small = make_dto(followers_count=50000)
        criteria = {"category": "美妆"}
        score_big = engine.score_influencer(dto_big, criteria)["reach_score"]
        score_small = engine.score_influencer(dto_small, criteria)["reach_score"]
        assert score_big > score_small

    def test_higher_engagement_more_reach(self, engine):
        dto_high = make_dto(followers_count=500000, engagement_rate=8.0)
        dto_low = make_dto(followers_count=500000, engagement_rate=0.5)
        criteria = {"category": "美妆"}
        score_high = engine.score_influencer(dto_high, criteria)["reach_score"]
        score_low = engine.score_influencer(dto_low, criteria)["reach_score"]
        assert score_high > score_low

    def test_higher_gmv_more_sales(self, engine):
        dto_high = make_dto(avg_gmv=1000000.0, avg_sales=50000)
        dto_low = make_dto(avg_gmv=10000.0, avg_sales=500)
        criteria = {"category": "美妆"}
        score_high = engine.score_influencer(dto_high, criteria)["sales_score"]
        score_low = engine.score_influencer(dto_low, criteria)["sales_score"]
        assert score_high > score_low

    def test_calculate_total_weighted(self, engine):
        dto = make_dto()
        criteria = {"category": "美妆"}
        total = engine.calculate_total(dto, criteria)
        assert 0 <= total <= 100

    def test_low_price_better_value(self, engine):
        dto_cheap = make_dto(price_range_min=1000, price_range_max=5000, avg_gmv=100000.0)
        dto_expensive = make_dto(price_range_min=50000, price_range_max=100000, avg_gmv=100000.0)
        criteria = {"category": "美妆"}
        score_cheap = engine.score_influencer(dto_cheap, criteria)["value_score"]
        score_expensive = engine.score_influencer(dto_expensive, criteria)["value_score"]
        assert score_cheap > score_expensive


class TestDefaultWeights:

    def test_weights_sum_to_one(self):
        w = get_default_weights()
        total = sum(w.values())
        assert abs(total - 1.0) < 0.001

    def test_weights_have_all_dimensions(self):
        w = get_default_weights()
        assert set(w.keys()) == {"match", "reach", "sales", "value"}
```

- [ ] **Step 2: Run tests (expected FAIL)**

```bash
cd backend && python -m pytest tests/influencer/test_scoring.py -v
```

- [ ] **Step 3: Implement `scoring.py`**

```python
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
```

- [ ] **Step 4: Run tests (expected PASS)**

```bash
cd backend && python -m pytest tests/influencer/test_scoring.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/influencer/services/scoring.py backend/tests/influencer/test_scoring.py
git commit -m "feat(influencer): add 4-dimension scoring engine"
```

---

### Task 9: 匹配推荐引擎

**Files:**
- Create: `backend/app/influencer/services/matching.py`
- Create: `backend/tests/influencer/test_matching.py`

**Interfaces:**
- Consumes: `ScoreEngine` from Task 8, `InfluencerDTO` from Task 2
- Produces: `MatchingEngine` with `match_batch(influencers, criteria)` → sorted list with scores

- [ ] **Step 1: Write test**

```python
# backend/tests/influencer/test_matching.py
from __future__ import annotations

import pytest
from app.influencer.services.data_platform.base import InfluencerDTO
from app.influencer.services.matching import MatchingEngine


def make_dto(uid: str, category: str, followers: int, gmv: float, price_min: int) -> InfluencerDTO:
    return InfluencerDTO(
        platform="douyin",
        platform_uid=uid,
        nickname=f"达人_{uid}",
        category=category,
        followers_count=followers,
        engagement_rate=3.0,
        avg_gmv=gmv,
        avg_sales=int(gmv / 20),
        price_range_min=price_min,
        price_range_max=price_min * 3,
    )


@pytest.mark.asyncio
async def test_match_batch_sorts_by_total_desc():
    engine = MatchingEngine()
    dtos = [
        make_dto("a", "美妆", 100000, 50000, 5000),
        make_dto("b", "美妆", 5000000, 1000000, 80000),
        make_dto("c", "美妆", 500000, 200000, 20000),
    ]
    criteria = {"category": "美妆"}
    results = engine.match_batch(dtos, criteria)
    assert results[0].total_score >= results[1].total_score >= results[2].total_score


@pytest.mark.asyncio
async def test_match_batch_adds_scores():
    engine = MatchingEngine()
    dtos = [make_dto("a", "美妆", 500000, 100000, 20000)]
    results = engine.match_batch(dtos, {"category": "美妆"})
    r = results[0]
    assert 0 <= r.match_score <= 100
    assert 0 <= r.reach_score <= 100
    assert 0 <= r.sales_score <= 100
    assert 0 <= r.value_score <= 100
    assert 0 <= r.total_score <= 100


@pytest.mark.asyncio
async def test_match_batch_prefers_same_category():
    engine = MatchingEngine()
    dtos = [
        make_dto("match", "美妆", 500000, 100000, 20000),
        make_dto("diff", "食品", 5000000, 1000000, 20000),  # better stats but wrong category
    ]
    results = engine.match_batch(dtos, {"category": "美妆"})
    # The matching category should have higher match_score
    match_result = next(r for r in results if r.influencer.platform_uid == "match")
    diff_result = next(r for r in results if r.influencer.platform_uid == "diff")
    assert match_result.match_score > diff_result.match_score


@pytest.mark.asyncio
async def test_top_n_returns_requested_count():
    engine = MatchingEngine()
    dtos = [make_dto(str(i), "美妆", 100000 * i, 100000 * i, 10000 * i) for i in range(1, 11)]
    top5 = engine.top_n(dtos, {"category": "美妆"}, n=5)
    assert len(top5) == 5


@pytest.mark.asyncio
async def test_empty_batch():
    engine = MatchingEngine()
    results = engine.match_batch([], {"category": "美妆"})
    assert results == []
```

- [ ] **Step 2: Run tests (expected FAIL)**

```bash
cd backend && python -m pytest tests/influencer/test_matching.py -v
```

- [ ] **Step 3: Implement `matching.py`**

```python
# backend/app/influencer/services/matching.py
from __future__ import annotations

from dataclasses import dataclass

from app.influencer.services.data_platform.base import InfluencerDTO
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
        results = []
        for inf in influencers:
            scores = self._scorer.score_influencer(inf, criteria)
            total = self._scorer.calculate_total(inf, criteria)
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
```

- [ ] **Step 4: Run tests (expected PASS)**

```bash
cd backend && python -m pytest tests/influencer/test_matching.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/influencer/services/matching.py backend/tests/influencer/test_matching.py
git commit -m "feat(influencer): add matching engine with batch scoring and top-N"
```

---

### Task 10: 选人任务 API

**Files:**
- Create: `backend/app/influencer/routers/selections.py`
- Modify: `backend/app/influencer/routers/__init__.py`
- Modify: `backend/app/gateway/app.py` (register selections router)
- Create: `backend/tests/influencer/test_api_selections.py`

**Interfaces:**
- Consumes: Selection/Facebook models, MockDataAdapter, MatchingEngine
- Produces: Full Selection CRUD API with candidate management

- [ ] **Step 1: Write API test**

```python
# backend/tests/influencer/test_api_selections.py
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.gateway.app import create_app
from app.influencer.services.data_platform.mock import MockDataAdapter


def _make_app():
    app = create_app()
    app.state.influencer_adapter = MockDataAdapter()
    return app


@pytest.mark.asyncio
async def test_create_selection():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/influencer/selections",
            json={
                "title": "测试选人任务",
                "goal": "找3位美妆达人",
                "criteria": {"category": "美妆", "follower_min": 100000},
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "测试选人任务"
    assert data["status"] == "draft"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_list_selections():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create one first
        await client.post(
            "/api/influencer/selections",
            json={"title": "列表测试", "goal": "test", "criteria": {}},
        )
        resp = await client.get("/api/influencer/selections")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_selection_detail():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/influencer/selections",
            json={"title": "详情测试", "goal": "test", "criteria": {"category": "美妆"}},
        )
        sid = created.json()["id"]
        resp = await client.get(f"/api/influencer/selections/{sid}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "详情测试"


@pytest.mark.asyncio
async def test_update_selection_status():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/influencer/selections",
            json={"title": "状态测试", "goal": "test", "criteria": {}},
        )
        sid = created.json()["id"]
        resp = await client.put(
            f"/api/influencer/selections/{sid}",
            json={"status": "in_progress", "title": "状态测试(更新)"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_add_candidate():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get an influencer
        search = await client.get("/api/influencer/search", params={"page_size": 1})
        inf = search.json()["data"][0]

        # Create selection
        created = await client.post(
            "/api/influencer/selections",
            json={"title": "添加候选测试", "goal": "test", "criteria": {"category": inf["category"]}},
        )
        sid = created.json()["id"]

        # Add candidate
        resp = await client.post(
            f"/api/influencer/selections/{sid}/candidates",
            json={"influencer_id": inf["id"], "added_by": "manual_add"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_selection_not_found():
    transport = ASGITransport(app=_make_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/influencer/selections/nonexistent-id")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests (expected FAIL)**

```bash
cd backend && python -m pytest tests/influencer/test_api_selections.py -v
```

- [ ] **Step 3: Implement `routers/selections.py`**

```python
# backend/app/influencer/routers/selections.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.influencer.models.selection import Selection, SelectionInfluencer
from app.influencer.models.influencer import Influencer
from app.influencer.services.matching import MatchingEngine

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


# ── DB session dependency ──

async def get_db(request: Request) -> AsyncSession:
    from deerflow.persistence.engine import get_session
    async with get_session() as session:
        yield session


# ── Routes ──

@router.post("/")
async def create_selection(
    body: CreateSelectionRequest,
    request: Request,
):
    """Create a new influencer selection task."""
    # Direct sync creation for mock/simple case
    from deerflow.persistence.engine import get_session
    from sqlalchemy.ext.asyncio import AsyncSession

    sel = Selection(
        title=body.title,
        goal=body.goal,
        criteria=body.criteria,
        thread_id=body.thread_id,
        status="draft",
    )

    async with get_session() as session:
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
    from deerflow.persistence.engine import get_session

    async with get_session() as session:
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
    from deerflow.persistence.engine import get_session

    async with get_session() as session:
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
    from deerflow.persistence.engine import get_session

    async with get_session() as session:
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
    from deerflow.persistence.engine import get_session

    async with get_session() as session:
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
        return {"id": link.id, "status": "added"}


@router.delete("/{selection_id}/candidates/{candidate_id}")
async def remove_candidate(selection_id: str, candidate_id: str, request: Request):
    from deerflow.persistence.engine import get_session

    async with get_session() as session:
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
    from deerflow.persistence.engine import get_session

    async with get_session() as session:
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
```

- [ ] **Step 4: Update routers `__init__.py`**

```python
# backend/app/influencer/routers/__init__.py
from app.influencer.routers.influencers import router as influencers_router
from app.influencer.routers.selections import router as selections_router

__all__ = ["influencers_router", "selections_router"]
```

- [ ] **Step 5: Register in gateway app.py**

```python
# In create_app(), add:
from app.influencer.routers import selections_router
app.include_router(selections_router)
```

- [ ] **Step 6: Run tests**

```bash
cd backend && python -m pytest tests/influencer/test_api_selections.py -v
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/influencer/routers/ backend/app/gateway/app.py
git add backend/tests/influencer/test_api_selections.py
git commit -m "feat(influencer): add selection CRUD API with candidates"
```

---

*(Due to plan length, Tasks 11-17 are summarized below with key deliverables. Full detail follows the same TDD pattern as Tasks 1-10.)*

### Task 11: Agent Tools — search_influencers

**Files:** `deerflow/tools/influencer/__init__.py`, `search_influencers.py`
**Deliverable:** LangChain tool that calls `DataPlatformAdapter.search` and `MatchingEngine.match_batch`, returns structured results with scores
**Test:** `tests/influencer/test_agent_tools.py::test_search_influencers_tool`

### Task 12: Agent Tools — compare & report

**Files:** `deerflow/tools/influencer/compare_influencers.py`, `recommend_report.py`
**Deliverable:** Compare tool returns dimension-by-dimension comparison. Report tool generates markdown recommendation
**Test:** comparison correctness, report not-empty

### Task 13: Frontend — 达人广场页

**Files:** `app/workspace/influencer/page.tsx`, `components/workspace/influencer/filter-panel.tsx`, `influencer-card.tsx`
**Deliverable:** Full influencer search/browse page with filter panel + card grid + pagination
**Test:** E2E with Playwright

### Task 14: Frontend — 达人详情页

**Files:** `app/workspace/influencer/[id]/page.tsx`, `components/workspace/influencer/influencer-detail.tsx`
**Deliverable:** Detail page with radar chart, demographics, content analysis, brand history

### Task 15: Frontend — 选人任务列表

**Files:** `app/workspace/influencer/selections/page.tsx`
**Deliverable:** Selection task list with status badges, create/delete

### Task 16: Frontend — 任务详情 + 对比

**Files:** `app/workspace/influencer/selections/[id]/page.tsx`, `candidate-table.tsx`, `compare-drawer.tsx`
**Deliverable:** Candidate table with sort + compare drawer with overlay radar chart

### Task 17: Frontend — 聊天消息渲染

**Files:** `components/workspace/influencer/messages/search-result-msg.tsx`, `compare-table-msg.tsx`
**Deliverable:** Message type detection via `additional_kwargs.type`, card-style rendering in chat

---

### Phase 2 Completion Gate

After Task 17, the MVP is complete. Verification checklist:
- [ ] Mock adapter returns 150 influencers across 8 categories
- [ ] Search API filters by category, followers, engagement, price
- [ ] Scoring engine produces 4-dimension scores for any influencer
- [ ] Matching engine sorts by total score correctly
- [ ] Selection CRUD: create → add candidates → update status
- [ ] Frontend: browse influencers, view detail, manage selections
- [ ] Backend `make test` all passing
- [ ] Frontend `pnpm check` passing

---

## 后续阶段（独立计划）

| Phase | 内容 | 产出 |
|-------|------|------|
| 3 | Agent 协作 | 4个 SubAgent + 并行编排 + 降级 |
| 4 | 反馈闭环 | Feedback API + 评分自优化 + 看板 |
| 5 | 真实平台 | DouyinAdapter + 限流 + 定时同步 |
| 6 | 打磨 | E2E全覆盖 + 移动端适配 + 性能优化 |
