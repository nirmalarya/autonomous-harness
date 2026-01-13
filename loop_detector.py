"""
Loop detector for claude-harness v3.1.0.

Ported from cursor-harness v3.0.23 - proven in production.
Detects when agent is stuck and prevents infinite loops.

Triple Timeout Protection:
1. No initial response (15 min) - API never responded
2. Stall timeout (10 min) - API stopped responding mid-session
3. Session timeout (120 min) - Overall session limit
"""

import time
from collections import defaultdict


class LoopDetector:
    """Detect when agent is stuck in a loop or hanging."""

    def __init__(
        self,
        max_repeated_reads: int = 3,
        session_timeout_minutes: int = 120,
        stall_timeout_minutes: int = 10,
    ):
        """
        Initialize loop detector with timeout thresholds.

        Args:
            max_repeated_reads: Max times same file can be read before flagging
            session_timeout_minutes: Overall session timeout (default: 120 min)
            stall_timeout_minutes: Timeout for no tool activity (default: 10 min)
        """
        self.max_repeated_reads = max_repeated_reads
        self.session_timeout = session_timeout_minutes * 60
        self.stall_timeout = stall_timeout_minutes * 60  # No tool activity timeout

        self.session_start = time.time()
        self.file_reads = defaultdict(int)
        self.tool_count = 0
        self.last_progress = None  # Don't start stall timer until first tool call

    def track_tool(self, tool_type: str, path: str = ""):
        """
        Track a tool call for progress monitoring.

        Args:
            tool_type: Type of tool used (e.g., 'read', 'write', 'bash')
            path: File path if applicable
        """
        self.tool_count += 1
        self.last_progress = time.time()

        if tool_type == "read" and path:
            self.file_reads[path] += 1

    def check(self) -> tuple[bool, str]:
        """
        Check if agent is stuck in a loop or hanging.

        Returns:
            (is_stuck, reason) - True if stuck, with explanation
        """

        # Check 1: Session timeout (overall) - 120 minutes default
        elapsed = time.time() - self.session_start
        if elapsed > self.session_timeout:
            return True, f"Session timeout ({elapsed / 60:.0f} minutes)"

        # Check 2: No initial response timeout (API never responded)
        # If no tool activity after 15 minutes from start, API likely stuck
        # This is critical - prevents waiting 120 min when API never responds
        if self.last_progress is None and elapsed > 900:  # 15 minutes
            return True, f"No initial response from API after {elapsed / 60:.0f} minutes"

        # Check 3: Stall timeout (no tool activity) - only after first tool
        # Prevents hanging when API stops responding mid-session
        if self.last_progress is not None:
            time_since_progress = time.time() - self.last_progress
            if time_since_progress > self.stall_timeout:
                return (
                    True,
                    f"No tool activity for {time_since_progress / 60:.0f} minutes (stalled)",
                )

        # Check 4: Repeated file reads - agent stuck reading same files
        for path, count in self.file_reads.items():
            if count > self.max_repeated_reads:
                return True, f"Reading {path} {count} times"

        # Check 5: No progress (only reading, no writing)
        # If agent has done 30+ tools but all reads, likely stuck
        if self.tool_count > 30:
            # Count non-read tools
            non_reads = self.tool_count - sum(self.file_reads.values())
            if non_reads == 0:
                return True, f"{self.tool_count} reads, 0 writes/edits"

        return False, ""

    def reset(self):
        """Reset detector for new session (fresh context)."""
        self.session_start = time.time()
        self.file_reads.clear()
        self.tool_count = 0
        self.last_progress = None  # Don't start stall timer until first tool call

    def get_stats(self) -> dict[str, any]:
        """
        Get current loop detector statistics.

        Returns:
            Dictionary with session stats
        """
        elapsed = time.time() - self.session_start
        time_since_progress = None
        if self.last_progress is not None:
            time_since_progress = time.time() - self.last_progress

        return {
            "session_elapsed_minutes": elapsed / 60,
            "tool_count": self.tool_count,
            "time_since_last_tool_minutes": time_since_progress / 60
            if time_since_progress
            else None,
            "repeated_reads": dict(self.file_reads),
        }
