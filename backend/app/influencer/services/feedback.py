"""Feedback processing and scoring self-optimization.

When a brand submits feedback (1-5 stars + review), the service updates
the influencer's scores and adjusts the matching engine weights to reduce
the gap between predicted scores and actual outcomes.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Minimum confidence before weight adjustment kicks in
_MIN_CONFIDENCE = 0.3
# Learning rate for weight adjustments
_LEARNING_RATE = 0.05
# Maximum per-cycle weight change
_MAX_WEIGHT_DELTA = 0.05


class FeedbackService:
    """Process feedback and update scoring weights."""

    def __init__(self):
        self._weights = {
            "match": 0.35,
            "reach": 0.25,
            "sales": 0.25,
            "value": 0.15,
        }
        self._feedback_count = 0

    @property
    def weights(self) -> dict[str, float]:
        return dict(self._weights)

    def process_feedback(
        self,
        rating: int,
        predicted_score: float | None = None,
    ) -> dict[str, float] | None:
        """Process a feedback entry and return updated weights if changed.

        Args:
            rating: 1-5 star rating from brand
            predicted_score: The match_score predicted before collaboration (0-100).
                             If None, only update the counter without adjusting weights.

        Returns:
            Updated weights dict if weights changed, None otherwise.
        """
        self._feedback_count += 1

        if predicted_score is None:
            return None

        if self._feedback_count < 3:
            # Need at least 3 feedbacks for meaningful adjustment
            logger.info(
                "Feedback #%d recorded (need %d for weight adjustment)",
                self._feedback_count,
                3,
            )
            return None

        # Convert rating to score scale: 1→20, 2→40, 3→60, 4→80, 5→100
        actual_score = rating * 20.0

        # Calculate prediction error
        error = actual_score - predicted_score
        abs_error = abs(error)

        if abs_error < 10:
            # Within tolerance — no adjustment needed
            return None

        # Adjust weights: increase weight of dimensions that would
        # have reduced the error, decrease others proportionally.
        old_weights = dict(self._weights)
        direction = 1 if error > 0 else -1  # positive = under-predicted

        # Apply learning rate limited adjustment
        delta = min(abs_error / 100.0 * _LEARNING_RATE, _MAX_WEIGHT_DELTA)
        delta *= direction

        # Redistribute: increase one pair, decrease the other
        new_weights = {}
        for dim in ["match", "reach", "sales", "value"]:
            if dim in ("sales", "value"):
                new_weights[dim] = old_weights[dim] + delta * 0.5
            else:
                new_weights[dim] = old_weights[dim] - delta * 0.5

        # Normalize to sum to 1.0
        total = sum(new_weights.values())
        if total > 0:
            new_weights = {k: round(v / total, 4) for k, v in new_weights.items()}

        self._weights = new_weights
        logger.info(
            "Weights adjusted after %d feedbacks: error=%.1f, %s -> %s",
            self._feedback_count,
            error,
            {k: round(v, 3) for k, v in old_weights.items()},
            {k: round(v, 3) for k, v in new_weights.items()},
        )
        return new_weights


# Singleton instance for the Gateway process
_feedback_service: FeedbackService | None = None


def get_feedback_service() -> FeedbackService:
    """Get or create the singleton FeedbackService."""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
