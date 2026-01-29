#!/usr/bin/env python3
"""
Test E2E Hook Schema Handling

Tests that the e2e_hook correctly handles both JSON formats.
"""

import json
import tempfile
from pathlib import Path

import pytest

from validators.e2e_hook import get_current_feature


class TestE2EHookSchema:
    """Test that e2e_hook handles different feature_list.json schemas."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project directory."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        spec_dir = project_dir / "spec"
        spec_dir.mkdir()
        return project_dir

    def test_flat_array_format(self, temp_project):
        """Test handling of flat array format [...] (Anthropic standard)."""
        features = [
            {"id": "1", "description": "Feature 1", "passes": True},
            {"id": "2", "description": "Feature 2", "passes": False},
            {"id": "3", "description": "Feature 3", "passes": False},
        ]
        
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump(features, f)
        
        current = get_current_feature(temp_project)
        
        assert current is not None
        assert current["id"] == "2"  # First non-passing feature

    def test_wrapped_format(self, temp_project):
        """Test handling of wrapped format {"features": [...]} (legacy)."""
        data = {
            "features": [
                {"id": "1", "description": "Feature 1", "passing": True},
                {"id": "2", "description": "Feature 2", "passing": False},
            ]
        }
        
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump(data, f)
        
        current = get_current_feature(temp_project)
        
        assert current is not None
        assert current["id"] == "2"

    def test_passes_key(self, temp_project):
        """Test handling of 'passes' key (Anthropic standard)."""
        features = [
            {"id": "1", "passes": True},
            {"id": "2", "passes": False},
        ]
        
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump(features, f)
        
        current = get_current_feature(temp_project)
        
        assert current is not None
        assert current["id"] == "2"

    def test_passing_key(self, temp_project):
        """Test handling of 'passing' key (legacy)."""
        features = [
            {"id": "1", "passing": True},
            {"id": "2", "passing": False},
        ]
        
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump(features, f)
        
        current = get_current_feature(temp_project)
        
        assert current is not None
        assert current["id"] == "2"

    def test_all_passing_returns_none(self, temp_project):
        """When all features pass, should return None."""
        features = [
            {"id": "1", "passes": True},
            {"id": "2", "passes": True},
        ]
        
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump(features, f)
        
        current = get_current_feature(temp_project)
        
        assert current is None

    def test_missing_file_returns_none(self, temp_project):
        """When feature_list.json doesn't exist, should return None."""
        current = get_current_feature(temp_project)
        assert current is None

    def test_invalid_json_returns_none(self, temp_project):
        """When feature_list.json is invalid, should return None."""
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            f.write("not valid json {{{")
        
        current = get_current_feature(temp_project)
        assert current is None

    def test_empty_array_returns_none(self, temp_project):
        """When feature list is empty, should return None."""
        feature_list_path = temp_project / "spec" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump([], f)
        
        current = get_current_feature(temp_project)
        assert current is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
