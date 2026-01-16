"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
"""

import json
from datetime import datetime
from pathlib import Path


def count_passing_tests(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total tests in feature_list.json.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        (passing_count, total_count)
    """
    # Check spec/ folder first (new structure), then fallback to root (old structure)
    tests_file = project_dir / "spec" / "feature_list.json"

    if not tests_file.exists():
        tests_file = project_dir / "feature_list.json"

    if not tests_file.exists():
        return 0, 0

    try:
        with open(tests_file) as f:
            tests = json.load(f)

        total = len(tests)
        passing = sum(1 for test in tests if test.get("passes", False))

        return passing, total
    except (OSError, json.JSONDecodeError):
        return 0, 0


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, total = count_passing_tests(project_dir)

    if total > 0:
        percentage = (passing / total) * 100
        print(f"\nProgress: {passing}/{total} tests passing ({percentage:.1f}%)")
    else:
        print("\nProgress: feature_list.json not yet created")


def track_iteration_metrics(
    project_dir: Path, feature_id: str, iteration_count: int, success: bool
) -> None:
    """
    Track how many iterations each feature required (v3.7.0 - Ralph Philosophy Integration).

    This helps analyze:
    - Which features required most iteration
    - Success rate of iterative debugging
    - Patterns in feature complexity

    Args:
        project_dir: Project directory
        feature_id: Feature identifier (e.g., "feature-42" or description)
        iteration_count: Number of iterations needed to complete feature
        success: Whether feature was successfully completed

    Metrics file location: .claude/iteration_metrics.json
    """
    # Ensure .claude directory exists
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    metrics_file = claude_dir / "iteration_metrics.json"

    # Load existing metrics
    metrics = {}
    if metrics_file.exists():
        try:
            with open(metrics_file) as f:
                metrics = json.load(f)
        except (OSError, json.JSONDecodeError):
            metrics = {}

    # Update metrics for this feature
    metrics[feature_id] = {
        "iterations": iteration_count,
        "success": success,
        "timestamp": datetime.now().isoformat(),
    }

    # Save updated metrics
    try:
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
    except OSError as e:
        print(f"Warning: Could not save iteration metrics: {e}")


def get_iteration_statistics(project_dir: Path) -> dict:
    """
    Get statistics about iteration counts across all features.

    Returns:
        Dict with keys:
        - total_features: Number of features tracked
        - avg_iterations: Average iterations per feature
        - max_iterations: Maximum iterations needed
        - success_rate: Percentage of successful features
    """
    metrics_file = project_dir / ".claude" / "iteration_metrics.json"

    if not metrics_file.exists():
        return {
            "total_features": 0,
            "avg_iterations": 0,
            "max_iterations": 0,
            "success_rate": 0,
        }

    try:
        with open(metrics_file) as f:
            metrics = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {
            "total_features": 0,
            "avg_iterations": 0,
            "max_iterations": 0,
            "success_rate": 0,
        }

    if not metrics:
        return {
            "total_features": 0,
            "avg_iterations": 0,
            "max_iterations": 0,
            "success_rate": 0,
        }

    total_features = len(metrics)
    iterations = [m["iterations"] for m in metrics.values()]
    successes = sum(1 for m in metrics.values() if m.get("success", False))

    return {
        "total_features": total_features,
        "avg_iterations": sum(iterations) / total_features if total_features > 0 else 0,
        "max_iterations": max(iterations) if iterations else 0,
        "success_rate": (successes / total_features * 100) if total_features > 0 else 0,
    }


def print_iteration_statistics(project_dir: Path) -> None:
    """Print iteration statistics to console."""
    stats = get_iteration_statistics(project_dir)

    if stats["total_features"] == 0:
        print("No iteration metrics available yet")
        return

    print("\n📊 Iteration Metrics (Ralph Philosophy v3.7.0):")
    print(f"  Total features tracked: {stats['total_features']}")
    print(f"  Average iterations/feature: {stats['avg_iterations']:.1f}")
    print(f"  Maximum iterations needed: {stats['max_iterations']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
