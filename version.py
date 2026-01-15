"""Version information for claude-harness."""

from pathlib import Path

# Single source of truth for version
__version__ = "3.6.2"


def get_version() -> str:
    """
    Get the package version.

    Tries to read from VERSION file first (for development),
    falls back to hardcoded version.

    Returns:
        Version string (e.g., "3.6.0")
    """
    try:
        version_file = Path(__file__).parent / "VERSION"
        return version_file.read_text().strip()
    except Exception:
        return __version__
