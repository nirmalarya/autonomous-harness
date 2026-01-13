#!/usr/bin/env python3
"""
Test script for claude-harness v3.1.0 reliability features.

Verifies that all new modules work correctly:
- LoopDetector (triple timeout protection)
- RetryManager (retry + skip logic)
- ErrorHandler (comprehensive error logging)
"""

import shutil
import tempfile
from pathlib import Path

from error_handler import ErrorHandler
from loop_detector import LoopDetector
from retry_manager import RetryManager


def test_loop_detector():
    """Test loop detector functionality."""
    print("\n" + "=" * 70)
    print("TEST: Loop Detector")
    print("=" * 70)

    # Test 1: Initial state
    detector = LoopDetector(session_timeout_minutes=2, stall_timeout_minutes=1)
    is_stuck, reason = detector.check()
    assert not is_stuck, "Should not be stuck initially"
    print("✅ Test 1: Initial state - PASS")

    # Test 2: Track tools
    detector.track_tool("write", "file.py")
    detector.track_tool("read", "file.py")
    detector.track_tool("read", "file.py")
    is_stuck, reason = detector.check()
    assert not is_stuck, "Should not be stuck with normal activity"
    print("✅ Test 2: Normal tool activity - PASS")

    # Test 3: Repeated reads
    detector.track_tool("read", "same_file.py")
    detector.track_tool("read", "same_file.py")
    detector.track_tool("read", "same_file.py")
    detector.track_tool("read", "same_file.py")  # 4 times total
    is_stuck, reason = detector.check()
    assert is_stuck, "Should detect repeated reads"
    assert "Reading same_file.py" in reason
    print(f"✅ Test 3: Repeated reads detected - PASS ({reason})")

    # Test 4: Reset
    detector.reset()
    is_stuck, reason = detector.check()
    assert not is_stuck, "Should not be stuck after reset"
    print("✅ Test 4: Reset works - PASS")

    # Test 5: Stats
    detector.track_tool("write")
    detector.track_tool("read", "test.py")
    stats = detector.get_stats()
    assert stats["tool_count"] == 2
    print(f"✅ Test 5: Stats tracking - PASS (tool_count={stats['tool_count']})")

    print("\n✅ All LoopDetector tests passed!\n")


def test_retry_manager():
    """Test retry manager functionality."""
    print("\n" + "=" * 70)
    print("TEST: Retry Manager")
    print("=" * 70)

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Test 1: Initial state
        manager = RetryManager(temp_dir, max_retries=3)
        assert manager.should_retry("feature-1"), "Should allow retry initially"
        print("✅ Test 1: Initial state - PASS")

        # Test 2: Record failure
        manager.record_failure("feature-1", "Test error")
        assert manager.get_retry_count("feature-1") == 1
        assert manager.should_retry("feature-1"), "Should still allow retry (1/3)"
        print("✅ Test 2: Record first failure - PASS")

        # Test 3: Max retries
        manager.record_failure("feature-1", "Test error 2")
        manager.record_failure("feature-1", "Test error 3")
        assert not manager.should_retry("feature-1"), "Should not retry after max"
        assert manager.should_skip("feature-1"), "Should skip after max retries"
        print("✅ Test 3: Max retries reached - PASS")

        # Test 4: Feature selection
        features = [
            {"id": "feature-1", "passes": False},  # Skipped (max retries)
            {"id": "feature-2", "passes": True},  # Completed
            {"id": "feature-3", "passes": False},  # Next to work on
        ]
        next_feature = manager.get_next_feature(features)
        assert next_feature["id"] == "feature-3", "Should select next incomplete, non-skipped"
        print("✅ Test 4: Smart feature selection - PASS")

        # Test 5: Stats
        stats = manager.get_stats()
        assert stats["features_skipped"] == 1
        assert stats["features_being_retried"] == 1  # feature-1 (3 retries)
        print(f"✅ Test 5: Stats tracking - PASS (skipped={stats['features_skipped']})")

        # Test 6: State persistence
        state_file = temp_dir / ".claude" / "retry_state.json"
        assert state_file.exists(), "Should create state file"
        print("✅ Test 6: State persistence - PASS")

        print("\n✅ All RetryManager tests passed!\n")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_error_handler():
    """Test error handler functionality."""
    print("\n" + "=" * 70)
    print("TEST: Error Handler")
    print("=" * 70)

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Test 1: Initial state
        handler = ErrorHandler(temp_dir)
        summary = handler.get_error_summary()
        assert summary["total_errors"] == 0
        print("✅ Test 1: Initial state - PASS")

        # Test 2: Record error
        try:
            raise ValueError("Test error")
        except Exception as e:
            handler.record_error("test_context", e, feature_id="feature-1", fatal=False)

        summary = handler.get_error_summary()
        assert summary["total_errors"] == 1
        print("✅ Test 2: Record error - PASS")

        # Test 3: Record warning
        handler.record_warning("test_warning", "This is a warning", feature_id="feature-2")
        summary = handler.get_error_summary()
        assert summary["warnings"] == 1
        print("✅ Test 3: Record warning - PASS")

        # Test 4: Session errors only
        session_errors = handler.get_session_errors()
        assert len(session_errors) == 2  # 1 error + 1 warning
        print("✅ Test 4: Session errors filtering - PASS")

        # Test 5: Error log file
        log_file = temp_dir / ".claude" / "errors.json"
        assert log_file.exists(), "Should create error log file"
        print("✅ Test 5: Error log persistence - PASS")

        # Test 6: Fatal error detection
        try:
            raise RuntimeError("Fatal error")
        except Exception as e:
            handler.record_error("fatal_test", e, fatal=True)

        assert handler.has_fatal_errors(), "Should detect fatal errors"
        print("✅ Test 6: Fatal error detection - PASS")

        print("\n✅ All ErrorHandler tests passed!\n")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  AUTONOMOUS-HARNESS v3.1.0 FEATURE TESTS")
    print("=" * 70)
    print("\nTesting newly integrated reliability features...")

    try:
        test_loop_detector()
        test_retry_manager()
        test_error_handler()

        print("\n" + "=" * 70)
        print("  ALL TESTS PASSED! ✅")
        print("=" * 70)
        print("\nv3.1.0 reliability features are working correctly!")
        print("\nNext steps:")
        print("1. Test with real project: python autonomous_agent.py --project-dir ./test")
        print("2. Verify timeout protection works")
        print("3. Verify retry logic kicks in on failures")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        raise


if __name__ == "__main__":
    main()
