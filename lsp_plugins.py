"""
LSP Plugin Manager for claude-harness v3.2
==========================================

Manages LSP plugins from Anthropic's official marketplace.

Uses Claude Code's plugin system instead of manual .lsp.json generation.
Installs official, tested LSP plugins via marketplace.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


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
            "install_server": "npm install -g typescript-language-server typescript"
        },
        "python": {
            "plugin": "pyright-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Python"],
            "extensions": [".py", ".pyi"],
            "server_binary": "pyright-langserver",
            "install_server": "npm install -g pyright"
        },
        "go": {
            "plugin": "gopls-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Go"],
            "extensions": [".go"],
            "server_binary": "gopls",
            "install_server": "go install golang.org/x/tools/gopls@latest"
        },
        "rust": {
            "plugin": "rust-analyzer-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Rust"],
            "extensions": [".rs"],
            "server_binary": "rust-analyzer",
            "install_server": "rustup component add rust-analyzer"
        },
        "java": {
            "plugin": "jdtls-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Java"],
            "extensions": [".java"],
            "server_binary": "jdtls",
            "install_server": "# See https://github.com/eclipse/eclipse.jdt.ls"
        },
        "c_cpp": {
            "plugin": "clangd-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["C", "C++"],
            "extensions": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
            "server_binary": "clangd",
            "install_server": "# Install LLVM/Clang from your package manager"
        },
        "csharp": {
            "plugin": "csharp-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["C#"],
            "extensions": [".cs"],
            "server_binary": "csharp-ls",
            "install_server": "# See https://github.com/razzmatazz/csharp-language-server"
        },
        "php": {
            "plugin": "php-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["PHP"],
            "extensions": [".php"],
            "server_binary": "intelephense",
            "install_server": "npm install -g intelephense"
        },
        "swift": {
            "plugin": "swift-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Swift"],
            "extensions": [".swift"],
            "server_binary": "sourcekit-lsp",
            "install_server": "# Included with Xcode"
        },
        "lua": {
            "plugin": "lua-lsp",
            "marketplace": "claude-plugins-official",
            "languages": ["Lua"],
            "extensions": [".lua"],
            "server_binary": "lua-language-server",
            "install_server": "# See https://github.com/LuaLS/lua-language-server"
        }
    }

    def __init__(self, project_dir: Path):
        """
        Initialize LSP plugin manager.

        Args:
            project_dir: Project root directory
        """
        self.project_dir = project_dir

    def detect_languages(self) -> List[str]:
        """
        Auto-detect languages used in project.

        Returns:
            List of detected language identifiers
        """
        detected = []

        # Check for common project files/patterns
        if (self.project_dir / "package.json").exists() or \
           (self.project_dir / "tsconfig.json").exists():
            detected.append("typescript")

        if (self.project_dir / "requirements.txt").exists() or \
           (self.project_dir / "pyproject.toml").exists() or \
           (self.project_dir / "setup.py").exists():
            detected.append("python")

        if (self.project_dir / "go.mod").exists():
            detected.append("go")

        if (self.project_dir / "Cargo.toml").exists():
            detected.append("rust")

        if (self.project_dir / "pom.xml").exists() or \
           (self.project_dir / "build.gradle").exists():
            detected.append("java")

        if (self.project_dir / "CMakeLists.txt").exists() or \
           list(self.project_dir.glob("*.c")) or \
           list(self.project_dir.glob("*.cpp")):
            detected.append("c_cpp")

        if list(self.project_dir.glob("*.csproj")):
            detected.append("csharp")

        if (self.project_dir / "composer.json").exists():
            detected.append("php")

        if list(self.project_dir.glob("*.swift")):
            detected.append("swift")

        if list(self.project_dir.glob("*.lua")):
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

    def get_plugin_install_commands(self, languages: Optional[List[str]] = None) -> List[str]:
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

    def get_installation_guide(self, languages: Optional[List[str]] = None) -> str:
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
                lines.append(f"    claude plugin install {config['plugin']}@{config['marketplace']}")
                lines.append("")

        # Show plugins needing server installation
        if needs_server:
            lines.append("⚠️  Install Language Server First:")
            lines.append("")
            for lang, config in needs_server:
                lines.append(f"  {', '.join(config['languages'])} ({lang}):")
                lines.append(f"    1. Install server: {config['install_server']}")
                lines.append(f"    2. Install plugin: claude plugin install {config['plugin']}@{config['marketplace']}")
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

    def setup_lsp(self, languages: Optional[List[str]] = None) -> Dict:
        """
        Generate LSP setup information.

        Args:
            languages: Languages to configure (auto-detected if None)

        Returns:
            Setup summary with installation commands
        """
        if languages is None:
            languages = self.detect_languages()

        install_commands = self.get_plugin_install_commands(languages)
        installation_guide = self.get_installation_guide(languages)

        return {
            "languages": languages,
            "install_commands": install_commands,
            "installation_guide": installation_guide,
            "marketplace": "claude-plugins-official",
            "requires_version": "1.0.33+",
            "enable_command": "ENABLE_LSP_TOOL=1 (automatically enabled when plugins installed)"
        }
