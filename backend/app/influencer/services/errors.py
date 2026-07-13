# backend/app/influencer/services/errors.py
"""Service-layer exception types for the Live-Influencer module.

All exceptions inherit from ``InfluencerServiceError`` so callers can
catch a single base type or handle specific error categories individually.
"""

from __future__ import annotations


class InfluencerServiceError(Exception):
    """Base exception for all influencer service errors."""


class DataPlatformError(InfluencerServiceError):
    """Error communicating with a third-party data platform (e.g. Douyin API)."""


class MatchingError(InfluencerServiceError):
    """Error during influencer matching / scoring."""


class ScoringError(InfluencerServiceError):
    """Error during score computation or persistence."""
