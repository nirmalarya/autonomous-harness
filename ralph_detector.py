"""
Ralph Wiggum Plugin Detection
==============================

Detects if Ralph Wiggum plugin is available for use in the current environment.
Provides graceful fallback to bash loops if Ralph not available.

This is separate from preflight.py - preflight installs Ralph on first run,
this module detects Ralph availability during session initialization.
"""

import json
from pathlib import Path


def is_ralph_available(verbose: bool = False) -> bool:
    """
    Check if Ralph Wiggum plugin is currently available.

    This checks the installed_plugins.json file to see if Ralph is installed
    and ready to use. Unlike preflight checks, this does NOT attempt installation.

    Args:
        verbose: Print detection status messages

    Returns:
        True if Ralph plugin is installed and ready to use

    Example:
        >>> if is_ralph_available():
        ...     use_ralph_loops()
        ... else:
        ...     fallback_to_bash_loops()
    """
    try:
        # Check Claude's installed plugins registry
        plugins_file = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
        if not plugins_file.exists():
            if verbose:
                print("ℹ️  Claude plugins registry not found - Ralph not available")
            return False

        with open(plugins_file) as f:
            data = json.load(f)

        # Check if ralph-wiggum is in the plugins dict (any marketplace)
        plugins = data.get("plugins", {})
        for plugin_key in plugins.keys():
            if "ralph-wiggum" in plugin_key:
                if verbose:
                    print("✅ Ralph Wiggum plugin detected and available")
                return True

        if verbose:
            print("ℹ️  Ralph Wiggum plugin not installed")
        return False

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        if verbose:
            print(f"⚠️  Error detecting Ralph plugin: {e}")
        return False


def get_iteration_mode(force_ralph: bool = False, force_bash: bool = False) -> str:
    """
    Determine which iteration mode to use: ralph or bash.

    Args:
        force_ralph: If True, require Ralph plugin (error if not available)
        force_bash: If True, use bash loops even if Ralph available

    Returns:
        "ralph" or "bash"

    Raises:
        RuntimeError: If force_ralph=True but Ralph not available

    Example:
        >>> mode = get_iteration_mode(force_ralph=False, force_bash=False)
        >>> if mode == "ralph":
        ...     print("Using Ralph Wiggum plugin for iteration")
        ... else:
        ...     print("Using bash loops for iteration (v3.7.0 compatibility)")
    """
    if force_ralph and force_bash:
        raise ValueError("Cannot specify both --force-ralph and --force-bash")

    # Force bash mode (explicit user request)
    if force_bash:
        return "bash"

    # Check Ralph availability
    ralph_available = is_ralph_available()

    # Force Ralph mode (error if not available)
    if force_ralph:
        if not ralph_available:
            raise RuntimeError(
                "Ralph Wiggum plugin required (--force-ralph) but not installed!\n\n"
                "Install with: claude plugin install ralph-wiggum\n"
                "Or run preflight checks: python -m preflight"
            )
        return "ralph"

    # Auto-detect (default behavior)
    if ralph_available:
        return "ralph"
    else:
        return "bash"


def print_iteration_mode_status(mode: str, verbose: bool = True) -> None:
    """
    Print informational message about which iteration mode is being used.

    Args:
        mode: "ralph" or "bash"
        verbose: Print status message
    """
    if not verbose:
        return

    if mode == "ralph":
        print("\n" + "=" * 70)
        print("🔄 Iteration Mode: Ralph Wiggum Plugin (v4.0.0)")
        print("=" * 70)
        print("Using /ralph-loop commands for E2E debugging and feature quality loops")
        print("SDK-level stop hooks will handle iteration automatically")
        print("=" * 70 + "\n")
    else:
        print("\n" + "=" * 70)
        print("🔄 Iteration Mode: Bash Loops (v3.7.0 Compatibility)")
        print("=" * 70)
        print("Ralph Wiggum plugin not detected - using bash loops as fallback")
        print("To use Ralph plugin: claude plugin install ralph-wiggum")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    # CLI usage for testing
    import sys

    print("Ralph Wiggum Plugin Detection\n")

    available = is_ralph_available(verbose=True)
    mode = get_iteration_mode()

    print(f"\nDetection result: {'Available' if available else 'Not available'}")
    print(f"Iteration mode: {mode}")

    print_iteration_mode_status(mode)

    sys.exit(0 if available else 1)
