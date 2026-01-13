"""
Error handler for claude-harness v3.1.0.

Production-grade error handling with comprehensive logging.

Features:
- Structured error logging to .claude/errors.json
- User-friendly error messages
- Traceback capture for debugging
- Error categorization (fatal vs recoverable)
- Session error summaries
"""

import json
import traceback
from datetime import datetime
from pathlib import Path


class ErrorHandler:
    """Handle and log errors gracefully."""

    def __init__(self, project_dir: Path):
        """
        Initialize error handler.

        Args:
            project_dir: Project directory for error logs
        """
        self.project_dir = project_dir
        self.error_log_file = project_dir / ".claude" / "errors.json"
        self.errors: list[dict] = []
        self.session_start = datetime.now()

        # Load existing errors
        self._load_errors()

    def _load_errors(self):
        """Load existing error log from disk."""
        if self.error_log_file.exists():
            try:
                with open(self.error_log_file) as f:
                    self.errors = json.load(f)
            except (OSError, json.JSONDecodeError):
                self.errors = []

    def _save_errors(self):
        """Save error log to disk."""
        self.error_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.error_log_file, "w") as f:
            json.dump(self.errors, f, indent=2)

    def record_error(
        self, context: str, error: Exception, feature_id: str | None = None, fatal: bool = False
    ):
        """
        Record an error with full context.

        Args:
            context: Where the error occurred (e.g., "agent_session", "tool_execution")
            error: The exception that occurred
            feature_id: Feature being worked on (if applicable)
            fatal: Whether this error should stop execution
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_start": self.session_start.isoformat(),
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "feature_id": feature_id,
            "fatal": fatal,
        }

        self.errors.append(error_entry)
        self._save_errors()

        # Print user-friendly error
        self._print_user_error(context, error, feature_id, fatal)

    def _print_user_error(
        self, context: str, error: Exception, feature_id: str | None, fatal: bool
    ):
        """
        Print user-friendly error message.

        Args:
            context: Error context
            error: The exception
            feature_id: Feature ID if applicable
            fatal: Whether error is fatal
        """
        print("\n" + "=" * 70)
        if fatal:
            print("❌ FATAL ERROR")
        else:
            print("⚠️  ERROR (recoverable)")
        print("=" * 70)

        print(f"\nContext: {context}")
        print(f"Error: {str(error)}")

        if feature_id:
            print(f"Feature: {feature_id}")

        if fatal:
            print("\n⛔ Execution will stop")
            print("Check .claude/errors.json for full traceback")
        else:
            print("\n♻️  Will attempt to recover and continue")

        print("=" * 70 + "\n")

    def record_warning(self, context: str, message: str, feature_id: str | None = None):
        """
        Record a warning (non-error issue).

        Args:
            context: Where the warning occurred
            message: Warning message
            feature_id: Feature ID if applicable
        """
        warning_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_start": self.session_start.isoformat(),
            "type": "warning",
            "context": context,
            "message": message,
            "feature_id": feature_id,
        }

        self.errors.append(warning_entry)
        self._save_errors()

        # Print warning
        print(f"\n⚠️  Warning ({context}): {message}")
        if feature_id:
            print(f"   Feature: {feature_id}")
        print()

    def get_session_errors(self) -> list[dict]:
        """
        Get errors from current session only.

        Returns:
            List of error entries from this session
        """
        session_errors = []
        session_start_str = self.session_start.isoformat()

        for error in self.errors:
            if error.get("session_start") == session_start_str:
                session_errors.append(error)

        return session_errors

    def get_error_summary(self) -> dict[str, any]:
        """
        Get error summary for current session.

        Returns:
            Dictionary with error statistics
        """
        session_errors = self.get_session_errors()

        fatal_count = sum(1 for e in session_errors if e.get("fatal", False))
        warning_count = sum(1 for e in session_errors if e.get("type") == "warning")
        error_count = len(session_errors) - warning_count

        error_by_context = {}
        for error in session_errors:
            context = error.get("context", "unknown")
            error_by_context[context] = error_by_context.get(context, 0) + 1

        return {
            "total_errors": error_count,
            "fatal_errors": fatal_count,
            "warnings": warning_count,
            "errors_by_context": error_by_context,
            "session_start": self.session_start.isoformat(),
        }

    def print_session_summary(self):
        """Print summary of errors from current session."""
        summary = self.get_error_summary()

        if summary["total_errors"] == 0 and summary["warnings"] == 0:
            print("\n✅ No errors or warnings this session\n")
            return

        print("\n" + "=" * 70)
        print("SESSION ERROR SUMMARY")
        print("=" * 70)

        if summary["total_errors"] > 0:
            print(f"\n❌ Errors: {summary['total_errors']}")
            if summary["fatal_errors"] > 0:
                print(f"   Fatal: {summary['fatal_errors']}")

        if summary["warnings"] > 0:
            print(f"\n⚠️  Warnings: {summary['warnings']}")

        if summary["errors_by_context"]:
            print("\nBy context:")
            for context, count in summary["errors_by_context"].items():
                print(f"   {context}: {count}")

        print(f"\nFull error log: {self.error_log_file}")
        print("=" * 70 + "\n")

    def has_fatal_errors(self) -> bool:
        """
        Check if any fatal errors occurred this session.

        Returns:
            True if fatal errors exist
        """
        session_errors = self.get_session_errors()
        return any(e.get("fatal", False) for e in session_errors)

    def clear_session_errors(self):
        """Clear errors from current session (keep historical errors)."""
        session_start_str = self.session_start.isoformat()
        self.errors = [e for e in self.errors if e.get("session_start") != session_start_str]
        self._save_errors()
