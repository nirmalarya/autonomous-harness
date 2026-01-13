"""
Retry manager for claude-harness v3.1.0.

Ported from cursor-harness v3.0.20 - auto-recovery logic.

Features:
- Auto-retry failed features (default: 3 attempts)
- Skip features stuck in retry loop after max retries
- Track retry history for debugging
- Smart feature selection (skips completed and failed-after-retries)
"""

import json
from pathlib import Path


class RetryManager:
    """Manage retry logic for failed features."""

    def __init__(self, project_dir: Path, max_retries: int = 3):
        """
        Initialize retry manager.

        Args:
            project_dir: Project directory for state tracking
            max_retries: Maximum retry attempts per feature (default: 3)
        """
        self.project_dir = project_dir
        self.max_retries = max_retries
        self.retry_count: dict[str, int] = {}  # {feature_id: count}
        self.skipped_features: set[str] = set()
        self.retry_history: list[dict] = []  # Track all retry attempts

        # State file for persistence across sessions
        self.state_file = project_dir / ".claude" / "retry_state.json"
        self._load_state()

    def _load_state(self):
        """Load retry state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                    self.retry_count = state.get("retry_count", {})
                    self.skipped_features = set(state.get("skipped_features", []))
                    self.retry_history = state.get("retry_history", [])
            except (OSError, json.JSONDecodeError):
                pass  # Start fresh if state file is corrupted

    def _save_state(self):
        """Save retry state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "retry_count": self.retry_count,
            "skipped_features": list(self.skipped_features),
            "retry_history": self.retry_history,
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def should_retry(self, feature_id: str) -> bool:
        """
        Check if feature should be retried.

        Args:
            feature_id: Unique feature identifier

        Returns:
            True if should retry, False if max retries exceeded
        """
        count = self.retry_count.get(feature_id, 0)
        return count < self.max_retries

    def record_failure(self, feature_id: str, error: str = ""):
        """
        Record a feature failure and increment retry count.

        Args:
            feature_id: Unique feature identifier
            error: Error message or reason for failure
        """
        self.retry_count[feature_id] = self.retry_count.get(feature_id, 0) + 1

        # Log to history
        self.retry_history.append(
            {
                "feature_id": feature_id,
                "attempt": self.retry_count[feature_id],
                "error": error,
            }
        )

        # Check if we should skip this feature
        if self.retry_count[feature_id] >= self.max_retries:
            self.skipped_features.add(feature_id)
            print(f"\n⚠️  Feature {feature_id} failed {self.max_retries} times - SKIPPING")
            print("   Will continue with remaining features\n")

        self._save_state()

    def record_success(self, feature_id: str):
        """
        Record a feature success (reset retry count).

        Args:
            feature_id: Unique feature identifier
        """
        # Remove from retry tracking on success
        if feature_id in self.retry_count:
            del self.retry_count[feature_id]
        if feature_id in self.skipped_features:
            self.skipped_features.remove(feature_id)

        self._save_state()

    def should_skip(self, feature_id: str) -> bool:
        """
        Check if feature should be skipped (failed after max retries).

        Args:
            feature_id: Unique feature identifier

        Returns:
            True if feature should be skipped
        """
        return feature_id in self.skipped_features

    def get_next_feature(self, features: list[dict]) -> dict | None:
        """
        Get next feature to work on (smart selection).

        Skips:
        - Completed features (passes: true)
        - Features that failed after max retries

        Args:
            features: List of features from feature_list.json

        Returns:
            Next feature to work on, or None if all done/skipped
        """
        for feature in features:
            feature_id = feature.get("id", feature.get("name", ""))

            # Skip completed features
            if feature.get("passes", False):
                continue

            # Skip features that failed after retries
            if self.should_skip(feature_id):
                continue

            return feature

        return None

    def get_retry_count(self, feature_id: str) -> int:
        """
        Get current retry count for a feature.

        Args:
            feature_id: Unique feature identifier

        Returns:
            Number of retry attempts (0 if first try)
        """
        return self.retry_count.get(feature_id, 0)

    def get_stats(self) -> dict[str, any]:
        """
        Get retry manager statistics.

        Returns:
            Dictionary with retry stats
        """
        total_retries = sum(self.retry_count.values())
        return {
            "features_being_retried": len(self.retry_count),
            "features_skipped": len(self.skipped_features),
            "total_retry_attempts": total_retries,
            "max_retries": self.max_retries,
            "retry_count": dict(self.retry_count),
            "skipped_features": list(self.skipped_features),
        }

    def reset(self):
        """Reset retry manager (clear all state)."""
        self.retry_count.clear()
        self.skipped_features.clear()
        self.retry_history.clear()
        self._save_state()
