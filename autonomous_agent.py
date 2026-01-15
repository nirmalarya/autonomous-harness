#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo
============================

A minimal harness demonstrating long-running autonomous coding with Claude.
This script implements the two-agent pattern (initializer + coding agent) and
incorporates all the strategies from the long-running agents guide.

Example Usage:
    python autonomous_agent_demo.py --project-dir ./claude_clone_demo
    python autonomous_agent_demo.py --project-dir ./claude_clone_demo --max-iterations 5
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent import run_autonomous_agent

# Configuration
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent Demo - Long-running agent harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start fresh project (greenfield mode)
  claude-harness --spec app_spec.txt --project-dir ./my_project

  # Limit iterations for testing
  claude-harness --spec app_spec.txt --project-dir ./my_project --max-iterations 5

  # Enhancement mode (add features to existing project)
  claude-harness --mode enhancement --spec new_features.txt --project-dir ./existing_app

  # Use a specific model
  claude-harness --spec app_spec.txt --project-dir ./my_project --model claude-sonnet-4-5-20250929

Environment Variables:
  CLAUDE_CODE_OAUTH_TOKEN    Your Claude Code OAuth token (REQUIRED)
                             Generate with: claude setup-token
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./autonomous_demo_project"),
        help="Directory for the project (default: generations/autonomous_demo_project). Relative paths automatically placed in generations/ directory.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["greenfield", "enhancement", "bugfix"],
        default="greenfield",
        help="Development mode: greenfield (new project), enhancement (add features), bugfix (fix issues)",
    )

    parser.add_argument(
        "--spec",
        type=str,
        default=None,
        help="Path to specification file (REQUIRED). Example: --spec /path/to/app_spec.txt",
    )

    parser.add_argument(
        "--session-timeout",
        type=int,
        default=120,
        help="Overall session timeout in minutes (default: 120)",
    )

    parser.add_argument(
        "--stall-timeout",
        type=int,
        default=10,
        help="No-activity stall timeout in minutes (default: 10)",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts per feature (default: 3)",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Handle --version flag (no OAuth token required)
    if args.version:
        try:
            from importlib.metadata import version

            pkg_version = version("claude-harness")
        except Exception:
            from version import get_version

            pkg_version = get_version()
        print(f"claude-harness v{pkg_version}")
        return

    # Check for authentication (supports both OAuth token and API key)
    oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not oauth_token and not api_key:
        print("Error: Authentication required")
        print("\nOption 1 - OAuth Token (recommended for CLI):")
        print("  1. Generate with: claude setup-token")
        print("  2. Then set: export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token'")
        print("\nOption 2 - API Key:")
        print("  1. Get from: https://console.anthropic.com/")
        print("  2. Then set: export ANTHROPIC_API_KEY='your-api-key'")
        return

    # Validate spec file for enhancement/bugfix modes
    if args.mode in ["enhancement", "bugfix"] and not args.spec:
        print(f"Error: --spec is required for {args.mode} mode")
        print("\nExample: --spec specs/autograph_bugfix_spec.txt")
        return

    # Validate spec file for greenfield mode too
    if args.mode == "greenfield" and not args.spec:
        # Check if default spec exists
        default_spec = Path(__file__).parent / "specs" / "simple_example_spec.txt"
        if not default_spec.exists():
            print("Error: No spec file provided")
            print("\nUsage:")
            print("  claude-harness --spec <path-to-spec-file> --project-dir <directory>")
            print("\nExample:")
            print("  claude-harness --spec /path/to/app_spec.txt --project-dir ./my_project")
            print("\nFor more information, run: claude-harness --help")
            return

    # Automatically place projects in generations/ directory unless already specified
    project_dir = args.project_dir
    if not str(project_dir).startswith("generations/"):
        # Convert relative paths to be under generations/
        if project_dir.is_absolute():
            # If absolute path, use as-is
            pass
        else:
            # Prepend generations/ to relative paths
            project_dir = Path("generations") / project_dir

    # Run the agent
    try:
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                model=args.model,
                max_iterations=args.max_iterations,
                mode=args.mode,
                spec_file=args.spec,
                session_timeout_minutes=args.session_timeout,
                stall_timeout_minutes=args.stall_timeout,
                max_retries=args.max_retries,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("To resume, run the same command again")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
