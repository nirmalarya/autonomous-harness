"""
Completion Promise Validator
============================

PreToolUse hook that enforces completion promises before critical operations.

This hook validates that agents output completion promises (e.g., <promise>FEATURE_COMPLETE</promise>)
before marking features as passing in feature_list.json.

Part of the Ralph Wiggum philosophy integration (v3.7.0):
- "Iteration > Perfection" principle
- Explicit completion markers
- Quality gate enforcement
"""

import json
from pathlib import Path


async def completion_promise_hook(
    input_data: dict, tool_use_id: str = None, context: dict = None
) -> dict:
    """
    PreToolUse hook - validates completion promises before marking features as passing.

    Runs before Edit tool to verify that:
    1. Feature is being marked as passing in feature_list.json
    2. Completion promise was output earlier in the session
    3. All quality gates were completed

    Args:
        input_data: Tool input (e.g., {"file_path": "...", "old_string": "...", "new_string": "..."})
        tool_use_id: Unique ID for this tool use
        context: Execution context (cwd, session_transcript, etc.)

    Returns:
        Hook result - either {} (allow) or {"permission": "deny", ...}
    """
    if context is None:
        context = {}

    file_path = input_data.get("file_path", "")
    new_string = input_data.get("new_string", "")

    # Only validate feature_list.json edits
    if "feature_list.json" not in file_path:
        return {}  # Not editing feature list, allow

    # Check if marking feature as passing
    if '"passes": true' not in new_string:
        return {}  # Not marking as passing, allow

    # Get project directory
    project_dir = Path(context.get("cwd", "."))

    # Check for completion promise in session
    # Note: The SDK may provide session transcript in context
    # If not available, we use a marker file approach
    session_transcript = context.get("session_transcript", "")

    # Primary check: Look for completion promise in transcript
    has_feature_complete_promise = "<promise>FEATURE_COMPLETE</promise>" in session_transcript
    has_e2e_passed_promise = "<promise>E2E_PASSED</promise>" in session_transcript

    # Fallback: Check for marker file (created by agent when outputting promise)
    marker_file = project_dir / ".claude" / "completion_promise.marker"
    marker_exists = marker_file.exists()

    # If either method confirms the promise was output, allow
    if has_feature_complete_promise or has_e2e_passed_promise or marker_exists:
        # Clean up marker file for next feature
        if marker_exists:
            marker_file.unlink()
        return {}  # Promise confirmed, allow

    # Get feature info for better error message
    feature_info = _get_feature_being_modified(input_data, project_dir)

    return {
        "permission": "deny",
        "user_message": "⛔ Cannot mark feature as passing without completion promise!",
        "agent_message": f"""⛔ COMPLETION PROMISE REQUIRED

You are trying to mark {feature_info} as passing, but you haven't output the required completion promise.

**Critical Rule**: You MUST output <promise>FEATURE_COMPLETE</promise> after ALL quality gates pass.

**Quality Gates Checklist** (ALL must pass):
1. ✅ Database schema validated (all columns exist)
2. ✅ Browser integration tested (F12 DevTools - zero CORS errors)
3. ✅ E2E test created and passing (Puppeteer MCP tools)
4. ✅ E2E test output shown as proof (exit code 0)
5. ✅ Screenshots saved to .claude/verification/
6. ✅ test_results.json created with "overall_status": "passed"
7. ✅ Zero TODOs in implementation code
8. ✅ Security checklist complete (if auth/security feature)

**What to do now**:
1. Review the quality gates checklist above
2. Verify ALL gates have passed (don't skip any!)
3. If any gate failed → Fix it → Re-test
4. When ALL gates pass → Output: <promise>FEATURE_COMPLETE</promise>
5. Then (and only then) mark the feature as passing

**Alternative**: If you want to use a marker file:
```bash
echo "FEATURE_COMPLETE" > .claude/completion_promise.marker
```

This signals that all quality gates have passed and the feature is genuinely complete.

**Remember**: Completion promises are not just formalities - they signal that you've genuinely completed all quality checks, not given up or taken shortcuts.
""",
    }


def _get_feature_being_modified(input_data: dict, project_dir: Path) -> str:
    """Get user-friendly description of the feature being modified."""
    try:
        # Try to identify which feature is being marked as passing
        old_string = input_data.get("old_string", "")
        new_string = input_data.get("new_string", "")

        # Extract feature description if possible
        if '"description"' in old_string:
            # Try to extract description from the old_string
            lines = old_string.split("\\n")
            for line in lines:
                if '"description"' in line:
                    # Extract the description text
                    start = line.find('"description":') + len('"description":')
                    desc_line = line[start:].strip()
                    if desc_line.startswith('"'):
                        end = desc_line.find('"', 1)
                        if end > 0:
                            description = desc_line[1:end]
                            return f'feature "{description[:50]}..."'

        return "this feature"
    except Exception:
        return "this feature"


# Alternative: Simpler version that only checks for marker file
async def completion_promise_hook_simple(
    input_data: dict, tool_use_id: str = None, context: dict = None
) -> dict:
    """
    Simplified version that only checks for marker file.

    This is used if session transcript is not available in context.

    The agent must create .claude/completion_promise.marker file when outputting the promise.
    """
    if context is None:
        context = {}

    file_path = input_data.get("file_path", "")
    new_string = input_data.get("new_string", "")

    # Only validate feature_list.json edits
    if "feature_list.json" not in file_path:
        return {}

    # Check if marking feature as passing
    if '"passes": true' not in new_string:
        return {}

    # Get project directory
    project_dir = Path(context.get("cwd", "."))

    # Check for marker file
    marker_file = project_dir / ".claude" / "completion_promise.marker"

    if marker_file.exists():
        # Clean up marker for next feature
        marker_file.unlink()
        return {}  # Promise confirmed

    return {
        "permission": "deny",
        "user_message": "⛔ Completion promise required",
        "agent_message": """⛔ COMPLETION PROMISE REQUIRED

Create the completion promise marker file:
```bash
mkdir -p .claude
echo "FEATURE_COMPLETE" > .claude/completion_promise.marker
```

This signals that all quality gates have passed. Only do this after:
- Database schema validated
- Browser integration tested (F12 - zero CORS errors)
- E2E test created and passing
- E2E test output shown as proof
- Screenshots saved
- test_results.json created
- Zero TODOs in code
- Security checklist complete

Then try marking the feature as passing again.
""",
    }
