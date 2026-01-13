"""
E2E testing validation hook for Claude Agent SDK.

PostToolUse hook that validates E2E tests after git commit.
"""

import json
from pathlib import Path

from .e2e_verifier import E2EVerifier


def get_current_feature(project_dir: Path) -> dict | None:
    """Get the current feature being implemented."""
    # Check for spec/feature_list.json (greenfield mode)
    feature_list_path = project_dir / "spec" / "feature_list.json"
    if feature_list_path.exists():
        try:
            with open(feature_list_path) as f:
                data = json.load(f)
                features = data.get("features", [])
                # Find first feature that's not passing
                for feature in features:
                    if not feature.get("passing", False):
                        return feature
        except:
            pass

    # Check for .next_feature.json (continuation mode)
    next_feature_path = project_dir / ".next_feature.json"
    if next_feature_path.exists():
        try:
            with open(next_feature_path) as f:
                return json.load(f)
        except:
            pass

    return None


def is_user_facing(feature: dict) -> bool:
    """
    Determine if a feature is user-facing (needs E2E tests).

    User-facing features include UI components, pages, forms, etc.
    Backend-only features like database schemas, utils, etc. don't need E2E tests.
    """
    description = feature.get("description", "").lower()

    # Keywords that indicate user-facing features
    user_facing_keywords = [
        "page",
        "component",
        "form",
        "button",
        "ui",
        "interface",
        "dashboard",
        "view",
        "modal",
        "dialog",
        "navigation",
        "display",
        "show",
        "render",
        "input",
        "output",
        "chart",
        "graph",
        "table",
        "list",
        "card",
    ]

    # Keywords that indicate backend-only features
    backend_keywords = [
        "schema",
        "migration",
        "model",
        "database",
        "api endpoint",
        "utility",
        "helper",
        "config",
        "setup",
        "init",
    ]

    # Check if it's explicitly backend
    if any(keyword in description for keyword in backend_keywords):
        return False

    # Check if it's user-facing
    if any(keyword in description for keyword in user_facing_keywords):
        return True

    # Default to user-facing (better to over-test than under-test)
    return True


async def e2e_validation_hook(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """
    PostToolUse hook - validates E2E tests after git commit.

    Runs after git commit to verify:
    1. Screenshots exist (.claude/verification/*.png)
    2. test_results.json exists
    3. overall_status == "passed"
    4. No console errors or visual issues

    Args:
        input_data: Tool input (e.g., {"command": "git commit ..."})
        tool_use_id: Unique ID for this tool use
        context: Execution context (cwd, etc.)

    Returns:
        Hook result - either {} (allow) or {"permission": "deny", ...}
    """
    command = input_data.get("command", "")

    # Only run after git commits
    if "git commit" not in command:
        return {}  # Not a commit, skip validation

    # Get project directory
    project_dir = Path(context.get("cwd", "."))
    verifier = E2EVerifier(project_dir)

    # Get current feature
    current_feature = get_current_feature(project_dir)

    if not current_feature:
        # No feature tracking, allow (might be manual commit)
        return {}

    # Check if this feature needs E2E testing
    if not is_user_facing(current_feature):
        # Backend-only feature, skip E2E validation
        return {}

    # Verify E2E tests
    result = verifier.verify(current_feature)

    if not result.passed:
        feature_index = current_feature.get("index", "?")
        feature_desc = current_feature.get("description", "Unknown feature")

        return {
            "permission": "deny",
            "user_message": f"⛔ E2E tests FAILED for Feature #{feature_index}",
            "agent_message": f"""E2E testing requirement not met: {result.reason}

Feature #{feature_index}: {feature_desc}

You MUST create and run E2E tests using Puppeteer MCP tools before committing:

1. Start the development server (if not running)
2. Use Puppeteer MCP tools to test the feature:
   - puppeteer_navigate(url="http://localhost:3000/your-page")
   - puppeteer_screenshot(path=".claude/verification/step-1-loaded.png")
   - puppeteer_click(selector="#your-button")
   - puppeteer_screenshot(path=".claude/verification/step-2-clicked.png")
   - puppeteer_fill(selector="input[name='field']", value="test")
   - etc.

3. Save screenshots to .claude/verification/
   - Name them descriptively (e.g., "step-1-form-loaded.png", "step-2-form-submitted.png")

4. Create .claude/verification/test_results.json:
{{
  "feature_index": {feature_index},
  "overall_status": "passed",
  "e2e_results": [
    {{"step": "Loaded page", "status": "passed", "screenshot": "step-1-loaded.png"}},
    {{"step": "Clicked button", "status": "passed", "screenshot": "step-2-clicked.png"}}
  ],
  "console_errors": [],
  "visual_issues": []
}}

5. Verify all tests passed before committing again

Re-run E2E tests now and fix any failures.
""",
        }

    # E2E tests passed!
    return {}
