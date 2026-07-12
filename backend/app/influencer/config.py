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
