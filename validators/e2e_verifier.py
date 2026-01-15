"""
E2E Verification for cursor-harness v3.0.4

Lightweight verification that E2E testing was performed.
Based on Anthropic's autonomous-coding demo pattern.

Checks:
1. Screenshots exist in .cursor/verification/
2. User-facing features require E2E testing
3. Backend features can skip E2E testing

Philosophy:
- Trust the agent to do E2E testing (Anthropic pattern)
- Verify artifacts exist (production enhancement)
- Keep it simple and lightweight
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class E2EVerificationResult:
    """Result of E2E verification."""

    passed: bool
    reason: str
    screenshot_count: int


class E2EVerifier:
    """
    Lightweight E2E verification - checks that testing was performed.

    Based on Anthropic's pattern:
    - Agent performs E2E testing using Puppeteer MCP
    - Agent saves screenshots to .claude/verification/
    - Harness verifies screenshots exist (proof of testing)

    This prevents agent from marking features as passing without E2E testing.
    """

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.verification_dir = project_dir / ".claude" / "verification"

    def verify(self, work_item: dict | None) -> E2EVerificationResult:
        """
        Verify E2E testing was performed AND passed for this work item.

        Checks:
        1. Screenshots exist (proof E2E testing was performed)
        2. test_results.json exists (proof of test results)
        3. test_results.json shows all steps passed (iteration loop completed)

        Args:
            work_item: Feature from feature_list.json (or None if no work)

        Returns:
            E2EVerificationResult with pass/fail status
        """

        if not work_item:
            return E2EVerificationResult(
                passed=True, reason="No work item - skipping E2E verification", screenshot_count=0
            )

        # Only check user-facing features
        if not self._is_user_facing(work_item):
            return E2EVerificationResult(
                passed=True,
                reason="Backend/infrastructure feature - E2E not required",
                screenshot_count=0,
            )

        # Check verification directory exists
        if not self.verification_dir.exists():
            return E2EVerificationResult(
                passed=False,
                reason="No .claude/verification directory found - E2E testing not performed",
                screenshot_count=0,
            )

        # Check screenshots exist
        screenshots = (
            list(self.verification_dir.glob("*.png"))
            + list(self.verification_dir.glob("*.jpg"))
            + list(self.verification_dir.glob("*.jpeg"))
        )

        if not screenshots:
            return E2EVerificationResult(
                passed=False,
                reason="No screenshots found in .claude/verification/ - E2E testing not performed",
                screenshot_count=0,
            )

        # NEW: Check test_results.json exists and shows passing
        test_results_file = self.verification_dir / "test_results.json"
        if not test_results_file.exists():
            return E2EVerificationResult(
                passed=False,
                reason="No test_results.json found - E2E test results not documented",
                screenshot_count=len(screenshots),
            )

        # Verify test results show all steps passed
        import json

        try:
            with open(test_results_file) as f:
                test_results = json.load(f)

            overall_status = test_results.get("overall_status", "")
            if overall_status != "passed":
                # Get failed steps for error message
                failed_steps = []
                for result in test_results.get("e2e_results", []):
                    if result.get("status") != "passed":
                        step_desc = result.get("step", "Unknown step")
                        error = result.get("error", "No error details")
                        failed_steps.append(f"{step_desc}: {error}")

                failed_msg = "; ".join(failed_steps) if failed_steps else "See test_results.json"
                return E2EVerificationResult(
                    passed=False,
                    reason=f"E2E tests FAILED - Agent must fix and re-test: {failed_msg}",
                    screenshot_count=len(screenshots),
                )

            # Success: Screenshots exist AND all E2E tests passed
            iteration = test_results.get("iteration", 1)
            console_errors = test_results.get("console_errors", [])
            visual_issues = test_results.get("visual_issues", [])

            details = f"found {len(screenshots)} screenshot(s)"
            if iteration > 1:
                details += f", iteration {iteration}"
            if console_errors:
                return E2EVerificationResult(
                    passed=False,
                    reason=f"Console errors detected: {console_errors}",
                    screenshot_count=len(screenshots),
                )
            if visual_issues:
                return E2EVerificationResult(
                    passed=False,
                    reason=f"Visual issues detected: {visual_issues}",
                    screenshot_count=len(screenshots),
                )

            return E2EVerificationResult(
                passed=True,
                reason=f"E2E testing verified - {details}, all tests passed",
                screenshot_count=len(screenshots),
            )

        except json.JSONDecodeError:
            return E2EVerificationResult(
                passed=False,
                reason="test_results.json is invalid JSON - fix formatting",
                screenshot_count=len(screenshots),
            )
        except Exception as e:
            return E2EVerificationResult(
                passed=False,
                reason=f"Error reading test_results.json: {e}",
                screenshot_count=len(screenshots),
            )

    def _is_user_facing(self, work_item: dict) -> bool:
        """
        Check if feature requires E2E testing with browser automation.

        Philosophy for fullstack applications:
        - Backend APIs are implementation details of user-facing features
        - If users interact with a feature through a UI, test the UI (not just API)
        - Only pure infrastructure features skip E2E testing

        This method now prioritizes UI testing for fullstack apps.
        """
        import re

        description = work_item.get("description", "").lower()
        steps = work_item.get("steps", [])
        category = work_item.get("category", "")

        # Helper function for word boundary matching
        def contains_word(text: str, word: str) -> bool:
            """Check if word exists in text with word boundaries."""
            pattern = r"\b" + re.escape(word) + r"\b"
            return bool(re.search(pattern, text))

        # Keywords indicating PURE INFRASTRUCTURE (truly no UI, skip E2E)
        # These are features that have no user interaction at all
        infrastructure_keywords = [
            "database migration",
            "database schema",
            "schema migration",
            "create database",
            "migration script",
            "environment variable",
            "environment config",
            "config file",
            "configuration file",
            "ci/cd pipeline",
            "deployment script",
            "build script",
            "docker setup",
            "infrastructure setup",
        ]

        # Check if this is pure infrastructure (no user interaction)
        for keyword in infrastructure_keywords:
            if keyword in description:
                return False  # Pure infrastructure, no E2E needed

        # Check if category explicitly marks it as infrastructure
        if category in ["infrastructure", "deployment", "ci-cd", "build"]:
            return False

        # Keywords indicating USER-FACING features (needs browser E2E)
        ui_keywords_single = [
            "click",
            "button",
            "page",
            "form",
            "display",
            "navigate",
            "ui",
            "interface",
            "screen",
            "menu",
            "modal",
            "dialog",
            "input",
            "select",
            "dropdown",
            "view",
            "show",
            "hide",
            "toggle",
            "render",
            "layout",
            "component",
            "widget",
            "panel",
            "sidebar",
            "dashboard",
            "table",
            "list",
            "card",
            "tab",
            "upload",
            "download",
        ]
        ui_keywords_phrases = ["user can", "user sees", "user clicks", "user interface"]

        # Check description for UI keywords
        for keyword in ui_keywords_single:
            if contains_word(description, keyword):
                return True  # Has UI keyword, needs E2E
        for phrase in ui_keywords_phrases:
            if phrase in description:
                return True  # Has UI phrase, needs E2E

        # Check steps for UI keywords
        if steps:
            steps_text = " ".join(steps).lower()
            for keyword in ui_keywords_single:
                if contains_word(steps_text, keyword):
                    return True  # Steps mention UI, needs E2E
            for phrase in ui_keywords_phrases:
                if phrase in steps_text:
                    return True  # Steps mention UI, needs E2E

        # Check category
        if category in ["ui", "ux", "style", "frontend", "functional"]:
            return True  # UI/frontend category, needs E2E

        # CHANGED: Default to user-facing (True) for fullstack apps
        # Reasoning: In fullstack apps, most features are user-facing
        # If unclear, better to require E2E than skip it
        # Only pure infrastructure (matched above) should skip E2E
        return True

    def clear_screenshots(self):
        """
        Clear screenshots directory (for next session).

        Call this after successfully validating a feature
        to ensure fresh screenshots for next feature.
        """
        if self.verification_dir.exists():
            for screenshot in self.verification_dir.glob("*"):
                screenshot.unlink()
