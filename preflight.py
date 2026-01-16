"""
Pre-flight Dependency Checker for v4.0.0
=========================================

Checks and auto-installs required dependencies:
1. Node.js v18+ (user must install manually)
2. Claude Code CLI (auto-install via npm)
3. Ralph Wiggum Plugin (auto-install via claude plugin install)

This ensures v4.0.0 can use the Ralph Wiggum plugin for iteration.
"""

import shutil
import subprocess
import sys
from pathlib import Path


class PreflightChecker:
    """Check and install required dependencies for v4.0.0."""

    def __init__(self, verbose: bool = True):
        """
        Initialize preflight checker.

        Args:
            verbose: Print detailed status messages
        """
        self.verbose = verbose
        self.checks = {
            "node": self.check_node,
            "claude_code_cli": self.check_claude_code_cli,
            "ralph_plugin": self.check_ralph_plugin,
        }

    def _print(self, message: str) -> None:
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(message)

    def check_all(self) -> tuple[bool, list[str]]:
        """
        Run all dependency checks.

        Returns:
            Tuple of (all_passed, list_of_missing_dependencies)
        """
        missing = []
        for name, check_fn in self.checks.items():
            if not check_fn():
                missing.append(name)
        return len(missing) == 0, missing

    def check_node(self) -> bool:
        """
        Check if Node.js v18+ is installed.

        Returns:
            True if Node.js v18+ is available
        """
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip().lstrip("v")
                major = int(version.split(".")[0])
                if major >= 18:
                    self._print(f"   ✅ Node.js {version} (v18+ required)")
                    return True
                else:
                    self._print(f"   ❌ Node.js {version} too old (v18+ required)")
                    return False
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass
        return False

    def check_claude_code_cli(self) -> bool:
        """
        Check if Claude Code CLI is installed.

        Returns:
            True if 'claude' command is available
        """
        if shutil.which("claude") is not None:
            try:
                result = subprocess.run(
                    ["claude", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self._print(f"   ✅ Claude Code CLI {version}")
                    return True
            except subprocess.TimeoutExpired:
                pass
        return False

    def check_ralph_plugin(self) -> bool:
        """
        Check if Ralph Wiggum plugin is installed.

        Returns:
            True if ralph-wiggum plugin is installed in Claude Code
        """
        import json

        try:
            # Check installed_plugins.json in Claude's config directory
            plugins_file = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
            if not plugins_file.exists():
                return False

            with open(plugins_file) as f:
                data = json.load(f)

            # Check if ralph-wiggum is in the plugins dict (any marketplace)
            plugins = data.get("plugins", {})
            for plugin_key in plugins.keys():
                if "ralph-wiggum" in plugin_key:
                    self._print("   ✅ Ralph Wiggum plugin installed")
                    return True

            return False
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return False

    def install_claude_code_cli(self) -> bool:
        """
        Install Claude Code CLI via npm.

        Returns:
            True if installation succeeded
        """
        try:
            self._print("\n📦 Installing Claude Code CLI...")
            self._print("   Running: npm install -g @anthropic-ai/claude-code")

            result = subprocess.run(
                ["npm", "install", "-g", "@anthropic-ai/claude-code"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self._print("   ✅ Claude Code CLI installed successfully")
                self._print("   Command 'claude' is now available")
                return True
            else:
                self._print(f"   ❌ Installation failed: {result.stderr[:200]}")
                return False

        except subprocess.TimeoutExpired:
            self._print("   ❌ Installation timed out (>2 minutes)")
            return False
        except FileNotFoundError:
            self._print("   ❌ npm command not found (Node.js not installed?)")
            return False
        except Exception as e:
            self._print(f"   ❌ Unexpected error: {e}")
            return False

    def install_ralph_plugin(self) -> bool:
        """
        Install Ralph Wiggum plugin into Claude Code.

        Returns:
            True if installation succeeded
        """
        try:
            self._print("\n📦 Installing Ralph Wiggum plugin...")

            # First, ensure the claude-code marketplace is added
            self._print("   Step 1: Adding claude-code marketplace (if needed)...")
            marketplace_result = subprocess.run(
                ["claude", "plugin", "marketplace", "add", "anthropics/claude-code"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Don't fail if marketplace already exists
            if marketplace_result.returncode != 0:
                if "already exists" not in marketplace_result.stderr.lower():
                    self._print(f"   ⚠️  Marketplace add warning: {marketplace_result.stderr[:100]}")

            # Now install the plugin
            self._print("   Step 2: Installing ralph-wiggum plugin...")
            self._print("   Running: claude plugin install ralph-wiggum")

            result = subprocess.run(
                ["claude", "plugin", "install", "ralph-wiggum"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self._print("   ✅ Ralph Wiggum plugin installed successfully")
                self._print("   /ralph-loop command is now available")
                return True
            else:
                # Check if already installed
                if "already installed" in result.stderr.lower():
                    self._print("   ✅ Ralph Wiggum plugin already installed")
                    return True
                self._print(f"   ❌ Installation failed: {result.stderr[:200]}")
                return False

        except subprocess.TimeoutExpired:
            self._print("   ❌ Installation timed out (>1 minute)")
            return False
        except FileNotFoundError:
            self._print("   ❌ claude command not found")
            return False
        except Exception as e:
            self._print(f"   ❌ Unexpected error: {e}")
            return False

    def auto_install_missing(self, missing: list[str]) -> bool:
        """
        Attempt to auto-install missing dependencies.

        Args:
            missing: List of missing dependency names

        Returns:
            True if all missing dependencies were installed successfully
        """
        if "node" in missing:
            self._print("\n" + "=" * 70)
            self._print("❌ Node.js v18+ is REQUIRED but not found")
            self._print("=" * 70)
            self._print("\nNode.js must be installed manually before using v4.0.0.")
            self._print("\n📖 Installation Instructions:\n")

            # Platform-specific instructions
            if sys.platform == "darwin":
                self._print("   macOS:")
                self._print("      brew install node")
                self._print("      # or download from: https://nodejs.org/")
            elif sys.platform.startswith("linux"):
                self._print("   Linux (Ubuntu/Debian):")
                self._print("      curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
                self._print("      sudo apt-get install -y nodejs")
                self._print("\n   Linux (Fedora/RHEL):")
                self._print("      curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -")
                self._print("      sudo dnf install -y nodejs")
            elif sys.platform == "win32":
                self._print("   Windows:")
                self._print("      Download installer from: https://nodejs.org/")
                self._print("      Or use winget: winget install OpenJS.NodeJS")
            else:
                self._print("   Download from: https://nodejs.org/")

            self._print("\nAfter installing Node.js, run claude-harness again.")
            self._print("=" * 70)
            return False

        # Auto-install Claude Code CLI if missing
        if "claude_code_cli" in missing:
            if not self.install_claude_code_cli():
                self._print("\n⚠️  Claude Code CLI installation failed")
                self._print("\nTry manual installation:")
                self._print("   npm install -g @anthropic-ai/claude-code")
                return False

        # Auto-install Ralph plugin if missing
        if "ralph_plugin" in missing:
            if not self.install_ralph_plugin():
                self._print("\n⚠️  Ralph Wiggum plugin installation failed")
                self._print("\nTry manual installation:")
                self._print("   claude plugin install ralph-wiggum")
                return False

        return True


def run_preflight(verbose: bool = True) -> bool:
    """
    Run pre-flight checks and auto-install dependencies if possible.

    This is the main entry point for preflight checks. Call this before
    starting the autonomous agent in v4.0.0.

    Args:
        verbose: Print detailed status messages

    Returns:
        True if all dependencies are satisfied, False otherwise

    Example:
        >>> if not run_preflight():
        ...     print("Cannot start harness - missing dependencies")
        ...     sys.exit(1)
    """
    if verbose:
        print("\n" + "=" * 70)
        print("🔍 v4.0.0 Pre-flight Dependency Check")
        print("=" * 70)
        print("\nChecking required dependencies...\n")

    checker = PreflightChecker(verbose=verbose)
    all_passed, missing = checker.check_all()

    if all_passed:
        if verbose:
            print("\n" + "=" * 70)
            print("✅ All dependencies satisfied!")
            print("=" * 70)
            print("\nReady to use Ralph Wiggum plugin for iteration.")
            print("You can now run the harness.\n")
        return True

    if verbose:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}\n")

    # Attempt auto-installation
    if checker.auto_install_missing(missing):
        # Re-check after installation
        if verbose:
            print("\n🔄 Re-checking dependencies after installation...\n")

        all_passed, still_missing = checker.check_all()

        if all_passed:
            if verbose:
                print("\n" + "=" * 70)
                print("✅ All dependencies installed successfully!")
                print("=" * 70)
                print("\nReady to use Ralph Wiggum plugin for iteration.")
                print("You can now run the harness.\n")
            return True
        else:
            if verbose:
                print(f"\n❌ Still missing after installation: {', '.join(still_missing)}")
            return False
    else:
        return False


def check_preflight_silent() -> bool:
    """
    Run preflight checks without printing output.

    Useful for scripts that want to check dependencies without
    verbose output.

    Returns:
        True if all dependencies satisfied
    """
    checker = PreflightChecker(verbose=False)
    all_passed, _ = checker.check_all()
    return all_passed


if __name__ == "__main__":
    # Allow running preflight checks standalone
    success = run_preflight()
    sys.exit(0 if success else 1)
