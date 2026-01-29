#!/usr/bin/env python3
"""
Test Iteration Mode Prompt Injection

Tests that iteration_mode affects prompt loading correctly.
"""

import pytest

from prompts import get_coding_prompt, get_initializer_prompt, inject_iteration_loops


class TestIterationMode:
    """Test iteration mode affects prompts correctly."""

    def test_inject_iteration_loops_bash_mode(self):
        """Bash mode should inject loop templates."""
        prompt = "Test prompt {{E2E_DEBUGGING_LOOP}} more text {{FEATURE_QUALITY_LOOP}} end"
        
        result = inject_iteration_loops(prompt, "bash")
        
        # Should have replaced placeholders with bash loop content
        assert "{{E2E_DEBUGGING_LOOP}}" not in result
        assert "{{FEATURE_QUALITY_LOOP}}" not in result
        # Bash loops contain these markers
        assert "E2E Debugging" in result or "#!/bin/bash" in result

    def test_inject_iteration_loops_ralph_mode(self):
        """Ralph mode should remove placeholders (Ralph handles iteration)."""
        prompt = "Test prompt {{E2E_DEBUGGING_LOOP}} more text {{FEATURE_QUALITY_LOOP}} end"
        
        result = inject_iteration_loops(prompt, "ralph")
        
        # Should have removed placeholders
        assert "{{E2E_DEBUGGING_LOOP}}" not in result
        assert "{{FEATURE_QUALITY_LOOP}}" not in result
        # Should NOT have bash loop content
        assert "#!/bin/bash" not in result

    def test_get_coding_prompt_accepts_iteration_mode(self):
        """get_coding_prompt should accept iteration_mode parameter."""
        # Should not raise
        prompt_ralph = get_coding_prompt(mode="greenfield", iteration_mode="ralph")
        prompt_bash = get_coding_prompt(mode="greenfield", iteration_mode="bash")
        
        assert isinstance(prompt_ralph, str)
        assert isinstance(prompt_bash, str)
        assert len(prompt_ralph) > 0
        assert len(prompt_bash) > 0

    def test_get_initializer_prompt_accepts_iteration_mode(self):
        """get_initializer_prompt should accept iteration_mode parameter."""
        # Should not raise
        prompt_ralph = get_initializer_prompt(mode="greenfield", iteration_mode="ralph")
        prompt_bash = get_initializer_prompt(mode="greenfield", iteration_mode="bash")
        
        assert isinstance(prompt_ralph, str)
        assert isinstance(prompt_bash, str)

    def test_bash_mode_appends_loops_if_no_placeholders(self):
        """Bash mode should append loops at end if no placeholders found."""
        # Simulate a prompt without placeholders
        prompt = "Simple prompt with no placeholders"
        
        result = inject_iteration_loops(prompt, "bash")
        
        # Should have appended loop content at the end
        assert len(result) > len(prompt)

    def test_ralph_mode_unchanged_if_no_placeholders(self):
        """Ralph mode should return unchanged if no placeholders."""
        prompt = "Simple prompt with no placeholders"
        
        result = inject_iteration_loops(prompt, "ralph")
        
        # Should be unchanged
        assert result == prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
