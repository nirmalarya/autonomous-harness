"""
Browser Cleanup Hook for claude-harness v3.1.1
==============================================

Automatically closes browser instances after Puppeteer operations.

This hook runs after any Puppeteer MCP tool is used and ensures
browsers are closed to prevent memory leaks.
"""

import asyncio
import subprocess
from pathlib import Path


async def browser_cleanup_hook(tool_name: str, tool_input: dict, tool_result: dict) -> dict:
    """
    PostToolUse hook that closes browsers after Puppeteer operations.

    This runs after every Puppeteer MCP tool call (navigate, click, screenshot, etc.)
    and attempts to close any open browser instances.

    Args:
        tool_name: Name of the tool that was just executed
        tool_input: Input parameters to the tool
        tool_result: Result returned by the tool

    Returns:
        Hook result with cleanup status
    """
    # Defensive type checking - handle case where tool_name might be a dict
    if isinstance(tool_name, dict):
        # Extract tool name from dict if present
        actual_tool_name = tool_name.get('name', '') or tool_name.get('tool_name', '')
        if not actual_tool_name:
            return {"status": "skipped", "reason": "Could not extract tool name from dict"}
        tool_name = actual_tool_name

    # Convert to string if not already
    tool_name = str(tool_name)

    # Only run for Puppeteer tools
    if "puppeteer" not in tool_name.lower():
        return {"status": "skipped", "reason": "Not a Puppeteer tool"}

    # Only cleanup after screenshot operations (end of test)
    # Don't cleanup during navigate/click/fill - those are mid-test
    cleanup_triggers = ["screenshot"]
    should_cleanup = any(trigger in tool_name.lower() for trigger in cleanup_triggers)

    if not should_cleanup:
        return {"status": "skipped", "reason": f"Not a cleanup trigger (tool: {tool_name})"}

    # Count Chrome processes before cleanup
    try:
        result_before = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        chrome_count_before = len([
            line for line in result_before.stdout.split('\n')
            if 'Google Chrome for Testing' in line or 'chrome' in line.lower()
        ])
    except:
        chrome_count_before = 0

    # Only cleanup if there are 5+ Chrome processes (indicating accumulation)
    if chrome_count_before < 5:
        return {
            "status": "skipped",
            "chrome_count": chrome_count_before,
            "reason": "Chrome count is low, no cleanup needed"
        }

    # Kill Chrome processes that are likely zombie browsers
    # Only kill "Google Chrome for Testing" which is what Puppeteer uses
    # Don't kill user's regular Chrome browser
    cleanup_commands = [
        ["pkill", "-9", "-f", "Google Chrome for Testing"],
        ["pkill", "-9", "-f", "chrome --remote-debugging-port"],
    ]

    cleanup_success = False
    for cmd in cleanup_commands:
        try:
            subprocess.run(cmd, capture_output=True, timeout=5)
            cleanup_success = True
        except:
            pass

    # Count Chrome processes after cleanup
    try:
        result_after = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        chrome_count_after = len([
            line for line in result_after.stdout.split('\n')
            if 'Google Chrome for Testing' in line or 'chrome' in line.lower()
        ])
    except:
        chrome_count_after = 0

    cleaned_count = chrome_count_before - chrome_count_after

    return {
        "status": "cleaned" if cleanup_success else "failed",
        "chrome_before": chrome_count_before,
        "chrome_after": chrome_count_after,
        "cleaned_count": cleaned_count,
        "message": f"Cleaned up {cleaned_count} Chrome processes"
    }
