#!/usr/bin/env python3
"""
Test Browser Cleanup Hook

Tests that the hook correctly handles the SDK input format.
"""

import asyncio

import pytest

from validators.browser_cleanup_hook import browser_cleanup_hook


class TestBrowserCleanupHook:
    """Test browser cleanup hook signature and behavior."""

    def test_correct_signature_with_dict_input(self):
        """Hook should accept input_data dict as first argument."""
        input_data = {
            "tool_name": "mcp__puppeteer__screenshot",
            "tool_input": {"path": "/tmp/test.png"},
            "tool_result": {"success": True},
        }
        
        # Should not raise - correct signature
        result = asyncio.run(browser_cleanup_hook(input_data))
        
        assert isinstance(result, dict)
        # Screenshot triggers cleanup check
        assert "status" in result

    def test_extracts_tool_name_from_input_data(self):
        """Hook should extract tool_name from input_data dict."""
        input_data = {
            "tool_name": "mcp__puppeteer__navigate",
            "tool_input": {"url": "http://localhost:3000"},
        }
        
        result = asyncio.run(browser_cleanup_hook(input_data))
        
        # Navigate is not a cleanup trigger, should skip
        assert result.get("status") == "skipped"
        assert "Not a cleanup trigger" in result.get("reason", "")

    def test_handles_name_key(self):
        """Hook should also check 'name' key if 'tool_name' missing."""
        input_data = {
            "name": "mcp__puppeteer__screenshot",
            "tool_input": {},
        }
        
        result = asyncio.run(browser_cleanup_hook(input_data))
        
        assert "status" in result

    def test_skips_non_puppeteer_tools(self):
        """Hook should skip non-Puppeteer tools."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
        }
        
        result = asyncio.run(browser_cleanup_hook(input_data))
        
        assert result.get("status") == "skipped"
        assert "Not a Puppeteer tool" in result.get("reason", "")

    def test_handles_empty_input(self):
        """Hook should handle empty input gracefully."""
        input_data = {}
        
        result = asyncio.run(browser_cleanup_hook(input_data))
        
        assert result.get("status") == "skipped"
        assert "Could not extract tool name" in result.get("reason", "")

    def test_handles_optional_params(self):
        """Hook should work with optional tool_use_id and context."""
        input_data = {
            "tool_name": "mcp__puppeteer__click",
            "tool_input": {"selector": "#button"},
        }
        
        # Should work without optional params
        result = asyncio.run(browser_cleanup_hook(input_data))
        assert "status" in result
        
        # Should also work with optional params
        result = asyncio.run(browser_cleanup_hook(input_data, "tool-123", {"cwd": "/tmp"}))
        assert "status" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
