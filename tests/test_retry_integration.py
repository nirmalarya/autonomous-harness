#!/usr/bin/env python3
"""
Test RetryManager Integration with Agent Loop

Tests the retry prioritization and tracking logic.
"""

import json
import tempfile
from pathlib import Path

import pytest

from retry_manager import RetryManager


class TestRetryPrioritization:
    """Test that features are prioritized by failure count."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project directory with retry manager."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        return project_dir

    @pytest.fixture
    def retry_manager(self, temp_project):
        """Create a retry manager for testing."""
        return RetryManager(temp_project, max_retries=3)

    def test_get_current_feature_prioritizes_fewer_failures(self, retry_manager):
        """Features with fewer failures should be prioritized."""
        # Simulate the prioritization logic from agent.py
        features = [
            {"id": "feature-1", "description": "First feature", "passes": False},
            {"id": "feature-2", "description": "Second feature", "passes": False},
            {"id": "feature-3", "description": "Third feature", "passes": False},
        ]
        
        # Record failures for feature-1 (3 failures)
        retry_manager.record_failure("feature-1", "timeout")
        retry_manager.record_failure("feature-1", "timeout")
        retry_manager.record_failure("feature-1", "timeout")
        
        # Record failures for feature-2 (1 failure)
        retry_manager.record_failure("feature-2", "error")
        
        # feature-3 has no failures
        
        # Simulate get_current_feature logic
        def get_current_feature(features_list, retry_mgr):
            incomplete = []
            for feature in features_list:
                if feature.get("passes", False):
                    continue
                feature_id = feature.get("id") or feature.get("description", "")[:50]
                retry_count = retry_mgr.get_retry_count(feature_id)
                incomplete.append((retry_count, feature))
            
            if not incomplete:
                return None
            
            incomplete.sort(key=lambda x: x[0])
            return incomplete[0][1]
        
        # Should return feature-3 (0 failures)
        next_feature = get_current_feature(features, retry_manager)
        assert next_feature["id"] == "feature-3", "Should prioritize feature with 0 failures"
        
        # Mark feature-3 as complete
        features[2]["passes"] = True
        
        # Should return feature-2 (1 failure)
        next_feature = get_current_feature(features, retry_manager)
        assert next_feature["id"] == "feature-2", "Should prioritize feature with 1 failure"
        
        # Mark feature-2 as complete
        features[1]["passes"] = True
        
        # Should return feature-1 (3 failures) - NOT skipped!
        next_feature = get_current_feature(features, retry_manager)
        assert next_feature["id"] == "feature-1", "Should NOT skip feature with many failures"

    def test_never_skips_features(self, retry_manager):
        """Features should never be skipped, even after max retries."""
        features = [
            {"id": "hard-feature", "description": "Difficult feature", "passes": False},
        ]
        
        # Record many failures (exceeding max_retries)
        for i in range(10):
            retry_manager.record_failure("hard-feature", f"failure {i}")
        
        # Simulate get_current_feature logic (same as above)
        def get_current_feature(features_list, retry_mgr):
            incomplete = []
            for feature in features_list:
                if feature.get("passes", False):
                    continue
                feature_id = feature.get("id") or feature.get("description", "")[:50]
                retry_count = retry_mgr.get_retry_count(feature_id)
                incomplete.append((retry_count, feature))
            
            if not incomplete:
                return None
            
            incomplete.sort(key=lambda x: x[0])
            return incomplete[0][1]
        
        # Should still return the feature (not None)
        next_feature = get_current_feature(features, retry_manager)
        assert next_feature is not None, "Should NOT skip features even after many failures"
        assert next_feature["id"] == "hard-feature"

    def test_completed_features_excluded(self, retry_manager):
        """Completed features should be excluded from selection."""
        features = [
            {"id": "done-feature", "description": "Completed", "passes": True},
            {"id": "pending-feature", "description": "Pending", "passes": False},
        ]
        
        def get_current_feature(features_list, retry_mgr):
            incomplete = []
            for feature in features_list:
                if feature.get("passes", False):
                    continue
                feature_id = feature.get("id") or feature.get("description", "")[:50]
                retry_count = retry_mgr.get_retry_count(feature_id)
                incomplete.append((retry_count, feature))
            
            if not incomplete:
                return None
            
            incomplete.sort(key=lambda x: x[0])
            return incomplete[0][1]
        
        next_feature = get_current_feature(features, retry_manager)
        assert next_feature["id"] == "pending-feature"
        assert next_feature["id"] != "done-feature"

    def test_all_complete_returns_none(self, retry_manager):
        """When all features are complete, should return None."""
        features = [
            {"id": "feature-1", "passes": True},
            {"id": "feature-2", "passes": True},
        ]
        
        def get_current_feature(features_list, retry_mgr):
            incomplete = []
            for feature in features_list:
                if feature.get("passes", False):
                    continue
                feature_id = feature.get("id") or feature.get("description", "")[:50]
                retry_count = retry_mgr.get_retry_count(feature_id)
                incomplete.append((retry_count, feature))
            
            if not incomplete:
                return None
            
            incomplete.sort(key=lambda x: x[0])
            return incomplete[0][1]
        
        next_feature = get_current_feature(features, retry_manager)
        assert next_feature is None

    def test_record_success_clears_retry_count(self, retry_manager):
        """Recording success should clear the retry count."""
        retry_manager.record_failure("feature-1", "error")
        retry_manager.record_failure("feature-1", "error")
        
        assert retry_manager.get_retry_count("feature-1") == 2
        
        retry_manager.record_success("feature-1")
        
        assert retry_manager.get_retry_count("feature-1") == 0

    def test_stats_show_struggling_features(self, retry_manager):
        """Stats should identify features that are struggling."""
        # Record failures for multiple features
        retry_manager.record_failure("easy-feature", "error")
        
        retry_manager.record_failure("hard-feature", "error")
        retry_manager.record_failure("hard-feature", "error")
        retry_manager.record_failure("hard-feature", "error")
        retry_manager.record_failure("hard-feature", "error")
        
        stats = retry_manager.get_stats()
        
        assert stats["features_being_retried"] == 2
        assert stats["total_retry_attempts"] == 5
        assert "hard-feature" in stats["retry_count"]
        assert stats["retry_count"]["hard-feature"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
