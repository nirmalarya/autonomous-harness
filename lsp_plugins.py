"""
LSP Plugin Manager for claude-harness v3.3
==========================================

Manages LSP plugins from Anthropic's official marketplace.

Uses Claude Code's plugin system instead of manual .lsp.json generation.
Installs official, tested LSP plugins via marketplace.
"""

import shutil
import subprocess
from pathlib import Path


class LSPPluginManager:
    """
    Manages LSP plugins from Anthropic's official marketplace.

    Claude Code v1.0.33+ has a plugin system with official LSP plugins.
    This manager detects project languages and provides installation commands.
    """

    # Official LSP plugins from claude-plugins-official marketplace
    OFFICIAL_LSP_PLUGINS = {
        "typescript": {
            "plugin": "typescript-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["TypeScript", "JavaScript"],
            "extensions": [".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs"],
            "server_binary": "typescript-language-server",
            "install_server": "npm install -g typescript-language-server typescript",
        },
        "python": {
            "plugin": "pyright-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Python"],
            "extensions": [".py", ".pyi"],
            "server_binary": "pyright-langserver",
            "install_server": "npm install -g pyright",
        },
        "go": {
            "plugin": "gopls-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Go"],
            "extensions": [".go"],
            "server_binary": "gopls",
            "install_server": "go install golang.org/x/tools/gopls@latest",
        },
        "rust": {
            "plugin": "rust-analyzer-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Rust"],
            "extensions": [".rs"],
            "server_binary": "rust-analyzer",
            "install_server": "rustup component add rust-analyzer",
        },
        "java": {
            "plugin": "jdtls-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Java"],
            "extensions": [".java"],
            "server_binary": "jdtls",
            "install_server": "# See https://github.com/eclipse/eclipse.jdt.ls",
        },
        "c_cpp": {
            "plugin": "clangd-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["C", "C++"],
            "extensions": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
            "server_binary": "clangd",
            "install_server": "# Install LLVM/Clang from your package manager",
        },
        "csharp": {
            "plugin": "csharp-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["C#"],
            "extensions": [".cs"],
            "server_binary": "csharp-ls",
            "install_server": "# See https://github.com/razzmatazz/csharp-language-server",
        },
        "php": {
            "plugin": "php-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["PHP"],
            "extensions": [".php"],
            "server_binary": "intelephense",
            "install_server": "npm install -g intelephense",
        },
        "swift": {
            "plugin": "swift-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Swift"],
            "extensions": [".swift"],
            "server_binary": "sourcekit-lsp",
            "install_server": "# Included with Xcode",
        },
        "lua": {
            "plugin": "lua-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Lua"],
            "extensions": [".lua"],
            "server_binary": "lua-language-server",
            "install_server": "# See https://github.com/LuaLS/lua-language-server",
        },
    }

    def __init__(self, project_dir: Path):
        """
        Initialize LSP plugin manager.

        Args:
            project_dir: Project root directory
        """
        self.project_dir = project_dir

    def detect_languages_from_spec(self, spec_file: Path | None = None) -> list[str]:
        """
        Detect languages from spec file content (for greenfield projects).

        Args:
            spec_file: Path to spec file (checks project_dir/spec/app_spec.txt if None)

        Returns:
            List of detected language identifiers based on tech stack mentions
        """
        if spec_file is None:
            spec_file = self.project_dir / "spec" / "app_spec.txt"

        if not spec_file.exists():
            return []

        try:
            spec_content = spec_file.read_text().lower()
        except Exception:
            return []

        detected = []

        # Check for tech stack keywords
        if any(
            word in spec_content
            for word in [
                "typescript",
                "react",
                "nextjs",
                "next.js",
                "vue",
                "angular",
                "node.js",
                "npm",
                "vite",
            ]
        ):
            detected.append("typescript")

        if any(
            word in spec_content
            for word in ["python", "django", "flask", "fastapi", "uvicorn", "pip", "pytest"]
        ):
            detected.append("python")

        if any(word in spec_content for word in ["golang", "go ", " go\n"]):
            detected.append("go")

        if any(word in spec_content for word in ["rust", "cargo"]):
            detected.append("rust")

        if any(word in spec_content for word in ["java", "spring", "maven", "gradle"]):
            detected.append("java")

        if any(word in spec_content for word in ["c++", "cpp", "clang", "cmake"]):
            detected.append("c_cpp")

        if any(word in spec_content for word in ["c#", "csharp", ".net", "dotnet"]):
            detected.append("csharp")

        if any(word in spec_content for word in ["php", "laravel", "symfony", "composer"]):
            detected.append("php")

        if any(word in spec_content for word in ["swift", "ios", "xcode"]):
            detected.append("swift")

        if any(word in spec_content for word in ["lua"]):
            detected.append("lua")

        return detected

    def detect_languages(self) -> list[str]:
        """
        Auto-detect languages used in project.

        First tries to detect from spec file (for greenfield),
        then from project files (for existing projects).

        Returns:
            List of detected language identifiers
        """
        detected = []

        # Try spec file first (for greenfield projects)
        spec_languages = self.detect_languages_from_spec()
        if spec_languages:
            detected.extend(spec_languages)

        # Check for common project files/patterns
        if (self.project_dir / "package.json").exists() or (
            self.project_dir / "tsconfig.json"
        ).exists():
            if "typescript" not in detected:
                detected.append("typescript")

        if (
            (self.project_dir / "requirements.txt").exists()
            or (self.project_dir / "pyproject.toml").exists()
            or (self.project_dir / "setup.py").exists()
        ):
            if "python" not in detected:
                detected.append("python")

        if (self.project_dir / "go.mod").exists():
            if "go" not in detected:
                detected.append("go")

        if (self.project_dir / "Cargo.toml").exists():
            if "rust" not in detected:
                detected.append("rust")

        if (self.project_dir / "pom.xml").exists() or (self.project_dir / "build.gradle").exists():
            if "java" not in detected:
                detected.append("java")

        if (
            (self.project_dir / "CMakeLists.txt").exists()
            or list(self.project_dir.glob("*.c"))
            or list(self.project_dir.glob("*.cpp"))
        ):
            if "c_cpp" not in detected:
                detected.append("c_cpp")

        if list(self.project_dir.glob("*.csproj")):
            if "csharp" not in detected:
                detected.append("csharp")

        if (self.project_dir / "composer.json").exists():
            if "php" not in detected:
                detected.append("php")

        if list(self.project_dir.glob("*.swift")):
            if "swift" not in detected:
                detected.append("swift")

        if list(self.project_dir.glob("*.lua")):
            if "lua" not in detected:
                detected.append("lua")

        return detected

    def check_server_installed(self, language: str) -> bool:
        """
        Check if LSP server binary is installed.

        Args:
            language: Language identifier

        Returns:
            True if installed, False otherwise
        """
        config = self.OFFICIAL_LSP_PLUGINS.get(language)
        if not config:
            return False

        server_binary = config.get("server_binary")
        return shutil.which(server_binary) is not None

    def get_plugin_install_commands(self, languages: list[str] | None = None) -> list[str]:
        """
        Get CLI commands to install LSP plugins.

        Args:
            languages: Languages to get commands for (auto-detected if None)

        Returns:
            List of claude plugin install commands
        """
        if languages is None:
            languages = self.detect_languages()

        commands = []

        for lang in languages:
            if lang in self.OFFICIAL_LSP_PLUGINS:
                config = self.OFFICIAL_LSP_PLUGINS[lang]
                plugin = config["plugin"]
                marketplace = config["marketplace"]
                commands.append(f"claude plugin install {plugin}@{marketplace}")

        return commands

    def get_installation_guide(self, languages: list[str] | None = None) -> str:
        """
        Get comprehensive installation guide for detected languages.

        Args:
            languages: Languages to check (auto-detected if None)

        Returns:
            Formatted installation guide
        """
        if languages is None:
            languages = self.detect_languages()

        if not languages:
            return "✓ No languages detected in project"

        lines = ["LSP Plugin Installation Guide", "=" * 60, ""]

        # Group by installation status
        ready = []
        needs_server = []

        for lang in languages:
            if lang not in self.OFFICIAL_LSP_PLUGINS:
                continue

            config = self.OFFICIAL_LSP_PLUGINS[lang]
            server_installed = self.check_server_installed(lang)

            if server_installed:
                ready.append((lang, config))
            else:
                needs_server.append((lang, config))

        # Show ready-to-install plugins
        if ready:
            lines.append("✅ Ready to Install (server already installed):")
            lines.append("")
            for lang, config in ready:
                lines.append(f"  {', '.join(config['languages'])} ({lang}):")
                lines.append(
                    f"    claude plugin install {config['plugin']}@{config['marketplace']}"
                )
                lines.append("")

        # Show plugins needing server installation
        if needs_server:
            lines.append("⚠️  Install Language Server First:")
            lines.append("")
            for lang, config in needs_server:
                lines.append(f"  {', '.join(config['languages'])} ({lang}):")
                lines.append(f"    1. Install server: {config['install_server']}")
                lines.append(
                    f"    2. Install plugin: claude plugin install {config['plugin']}@{config['marketplace']}"
                )
                lines.append("")

        # Add general info
        lines.append("=" * 60)
        lines.append("ℹ️  Plugin System Info:")
        lines.append("")
        lines.append("  - Requires: Claude Code v1.0.33+")
        lines.append("  - Check version: claude --version")
        lines.append("  - Browse plugins: claude (then type /plugin)")
        lines.append("  - Official marketplace: claude-plugins-official")
        lines.append("")

        return "\n".join(lines)

    def auto_install_language_servers(self, languages: list[str] | None = None) -> dict:
        """
        Automatically install language servers for detected languages.

        Args:
            languages: Languages to install servers for (auto-detected if None)

        Returns:
            Installation results with status per language
        """
        if languages is None:
            languages = self.detect_languages()

        results = {"installed": [], "failed": [], "already_installed": [], "unsupported": []}

        for lang in languages:
            if lang not in self.OFFICIAL_LSP_PLUGINS:
                continue

            config = self.OFFICIAL_LSP_PLUGINS[lang]

            # Check if server already installed
            if self.check_server_installed(lang):
                results["already_installed"].append(
                    {"language": lang, "server": config["server_binary"]}
                )
                continue

            # Get install command
            install_cmd = config["install_server"]

            # Skip if no automatic install command available (e.g., Java, C++)
            if install_cmd.startswith("#"):
                results["unsupported"].append(
                    {
                        "language": lang,
                        "reason": "Manual installation required",
                        "instructions": install_cmd,
                    }
                )
                continue

            # Parse and execute install command
            try:
                # Execute the install command
                result = subprocess.run(
                    install_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minutes for npm/go installs
                )

                if result.returncode == 0:
                    # Verify installation succeeded
                    if self.check_server_installed(lang):
                        results["installed"].append(
                            {
                                "language": lang,
                                "server": config["server_binary"],
                                "command": install_cmd,
                            }
                        )
                    else:
                        results["failed"].append(
                            {
                                "language": lang,
                                "server": config["server_binary"],
                                "error": "Installation succeeded but server not found in PATH",
                            }
                        )
                else:
                    results["failed"].append(
                        {
                            "language": lang,
                            "server": config["server_binary"],
                            "error": result.stderr.strip()[:200],  # Limit error length
                        }
                    )
            except subprocess.TimeoutExpired:
                results["failed"].append(
                    {
                        "language": lang,
                        "server": config["server_binary"],
                        "error": "Installation timeout (>2 minutes)",
                    }
                )
            except Exception as e:
                results["failed"].append(
                    {"language": lang, "server": config["server_binary"], "error": str(e)[:200]}
                )

        return results

    def auto_install_plugins(self, languages: list[str] | None = None) -> dict:
        """
        Automatically install LSP plugins for detected languages.

        Args:
            languages: Languages to install (auto-detected if None)

        Returns:
            Installation results with status per language
        """
        if languages is None:
            languages = self.detect_languages()

        results = {"installed": [], "failed": [], "skipped_no_server": [], "already_installed": []}

        for lang in languages:
            if lang not in self.OFFICIAL_LSP_PLUGINS:
                continue

            config = self.OFFICIAL_LSP_PLUGINS[lang]
            plugin_name = f"{config['plugin']}@{config['marketplace']}"

            # Check if server is installed
            if not self.check_server_installed(lang):
                results["skipped_no_server"].append(
                    {
                        "language": lang,
                        "plugin": plugin_name,
                        "install_server_cmd": config["install_server"],
                    }
                )
                continue

            # Check if plugin already installed
            check_cmd = ["claude", "plugin", "list"]
            try:
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                if config["plugin"] in check_result.stdout:
                    results["already_installed"].append({"language": lang, "plugin": plugin_name})
                    continue
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # If claude CLI not available, skip check
                pass

            # Install plugin
            install_cmd = ["claude", "plugin", "install", plugin_name]
            try:
                result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    results["installed"].append({"language": lang, "plugin": plugin_name})
                else:
                    results["failed"].append(
                        {"language": lang, "plugin": plugin_name, "error": result.stderr.strip()}
                    )
            except subprocess.TimeoutExpired:
                results["failed"].append(
                    {"language": lang, "plugin": plugin_name, "error": "Installation timeout"}
                )
            except FileNotFoundError:
                results["failed"].append(
                    {"language": lang, "plugin": plugin_name, "error": "claude CLI not found"}
                )

        return results

    def setup_lsp(
        self,
        languages: list[str] | None = None,
        auto_install: bool = True,
        auto_install_servers: bool = True,
    ) -> dict:
        """
        Setup LSP plugins for project (with optional auto-installation).

        Args:
            languages: Languages to configure (auto-detected if None)
            auto_install: Automatically install plugins if True (default)
            auto_install_servers: Automatically install language servers if True (default)

        Returns:
            Setup summary with installation results
        """
        if languages is None:
            languages = self.detect_languages()

        install_commands = self.get_plugin_install_commands(languages)
        installation_guide = self.get_installation_guide(languages)

        result = {
            "languages": languages,
            "install_commands": install_commands,
            "installation_guide": installation_guide,
            "marketplace": "claude-plugins-official",
            "requires_version": "1.0.33+",
            "enable_command": "ENABLE_LSP_TOOL=1 (automatically enabled when plugins installed)",
        }

        # Auto-install if requested
        if auto_install and languages:
            # First, install language servers if needed
            if auto_install_servers:
                server_results = self.auto_install_language_servers(languages)
                result["auto_install_server_results"] = server_results

            # Then install plugins
            install_results = self.auto_install_plugins(languages)
            result["auto_install_results"] = install_results

        return result
