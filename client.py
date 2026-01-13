"""
Claude SDK Client Configuration
===============================

Functions for creating and configuring the Claude Agent SDK client.
"""

import json
import os
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from lsp_plugins import LSPPluginManager
from security import bash_security_hook
from setup_mcp import MCPServerSetup
from skills_manager import SkillsManager
from validators.browser_cleanup_hook import browser_cleanup_hook
from validators.e2e_hook import e2e_validation_hook
from validators.secrets_hook import secrets_scan_hook

# Built-in tools
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def create_client(project_dir: Path, model: str, mode: str = "greenfield") -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client with multi-layered security.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        mode: Execution mode (greenfield, enhancement, bugfix, backlog)

    Returns:
        Configured ClaudeSDKClient

    Security layers (defense in depth):
    1. Sandbox - OS-level bash command isolation prevents filesystem escape
    2. Permissions - File operations restricted to project_dir only
    3. Security hooks - Bash commands validated against an allowlist
       (see security.py for ALLOWED_COMMANDS)
    4. Secrets scanning - Git commits blocked if secrets detected
    5. E2E validation - User-facing features require E2E tests
    """
    # Check for authentication (supports both OAuth token and API key)
    oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not oauth_token and not api_key:
        raise ValueError(
            "Authentication required. Set either:\n\n"
            "Option 1 - OAuth Token (recommended for CLI):\n"
            "  Generate with: claude setup-token\n"
            "  Then set: export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token'\n\n"
            "Option 2 - API Key:\n"
            "  Get from: https://console.anthropic.com/\n"
            "  Then set: export ANTHROPIC_API_KEY='your-api-key'"
        )

    # Determine which authentication method to use
    # Note: The SDK automatically reads from environment variables
    # We just validate that at least one is set
    auth_method = "API key" if api_key else "OAuth token"
    print(f"Authentication: Using {auth_method}")

    # Setup MCP servers dynamically based on mode
    mcp_setup = MCPServerSetup()
    mcp_servers = mcp_setup.setup(mode)

    # Get dynamic tool lists
    all_mcp_tools = []
    all_mcp_tools.extend(mcp_setup.get_browser_tools())
    all_mcp_tools.extend(mcp_setup.get_documentation_tools())
    if mode == "backlog":
        all_mcp_tools.extend(mcp_setup.get_azure_devops_tools())
        all_mcp_tools.extend(mcp_setup.get_linear_tools())

    # Load mode-specific skills
    skills_manager = SkillsManager(project_dir, mode)
    skills = skills_manager.load_skills_for_mode()

    # Setup LSP (Language Server Protocol) for code intelligence
    # LSP plugins are installed via official marketplace
    # Claude Code v1.0.33+ required
    lsp_manager = LSPPluginManager(project_dir)
    lsp_setup = lsp_manager.setup_lsp()

    # Create comprehensive security settings
    # Note: Using relative paths ("./**") restricts access to project directory
    # since cwd is set to project_dir
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",  # Auto-approve edits within allowed directories
            "allow": [
                # Allow all file operations within the project directory
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                # Bash permission granted here, but actual commands are validated
                # by the bash_security_hook (see security.py for allowed commands)
                "Bash(*)",
                # Allow ALL MCP tools (no prompts!)
                "mcp__*",  # Wildcard for all MCP tools
            ],
        },
    }

    # Ensure project directory exists before creating settings file
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write settings to a file in the project directory
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    print(f"Created security settings at {settings_file}")
    print("   - Sandbox enabled (OS-level bash isolation)")
    print(f"   - Filesystem restricted to: {project_dir.resolve()}")
    print("   - Bash commands restricted to allowlist (see security.py)")
    print(f"   - MCP servers: {', '.join(mcp_servers.keys())}")
    print("   - Secrets scanning enabled (blocks git commits with secrets)")
    print("   - E2E validation enabled (requires tests for user-facing features)")
    print(f"   - Skills loaded: {', '.join([s['name'] for s in skills]) if skills else 'none'}")
    print(
        f"   - LSP detected: {', '.join(lsp_setup['languages']) if lsp_setup['languages'] else 'none'}"
    )
    print(f"   - LSP marketplace: {lsp_setup['marketplace']}")

    # Print LSP auto-installation results
    if lsp_setup["languages"]:
        # Show language server installation results
        if "auto_install_server_results" in lsp_setup:
            server_results = lsp_setup["auto_install_server_results"]

            if server_results["installed"]:
                print("\n✅ Auto-installed language servers:")
                for item in server_results["installed"]:
                    config = lsp_manager.OFFICIAL_LSP_PLUGINS.get(item["language"], {})
                    langs = ", ".join(config.get("languages", [item["language"]]))
                    print(f"   - {langs}: {item['server']}")

            if server_results["failed"]:
                print("\n❌ Failed to install language servers:")
                for item in server_results["failed"]:
                    config = lsp_manager.OFFICIAL_LSP_PLUGINS.get(item["language"], {})
                    langs = ", ".join(config.get("languages", [item["language"]]))
                    error = item["error"][:100]  # Truncate long errors
                    print(f"   - {langs}: {error}")

        # Show plugin installation results
        if "auto_install_results" in lsp_setup:
            results = lsp_setup["auto_install_results"]

            if results["installed"]:
                print("\n✅ Auto-installed LSP plugins:")
                for item in results["installed"]:
                    print(f"   - {item['plugin']}")

            if results["already_installed"]:
                print("\n✓ Already installed:")
                for item in results["already_installed"]:
                    print(f"   - {item['plugin']}")

            if results["skipped_no_server"]:
                print("\nℹ️  LSP plugins skipped (optional - language server not installed):")
                for item in results["skipped_no_server"]:
                    config = lsp_manager.OFFICIAL_LSP_PLUGINS.get(item["language"], {})
                    langs = ", ".join(config.get("languages", [item["language"]]))
                    print(f"   - {langs}")
                print("   To enable LSP code intelligence (optional), install language servers:")
                for item in results["skipped_no_server"]:
                    config = lsp_manager.OFFICIAL_LSP_PLUGINS.get(item["language"], {})
                    langs = ", ".join(config.get("languages", [item["language"]]))
                    print(f"     • {langs}: {item['install_server_cmd']}")
                print("   Note: The harness works perfectly fine without LSP plugins.")

            if results["failed"]:
                print("\n❌ Failed to install LSP plugins:")
                for item in results["failed"]:
                    print(f"   - {item['plugin']}: {item['error']}")

    print()

    # Build system prompt with skills information
    system_prompt = (
        "You are an expert full-stack developer building a production-quality web application."
    )

    # Add skills as reference documentation in system prompt
    if skills:
        system_prompt += "\n\nYou have access to the following reference documentation:\n"
        for skill in skills:
            skill_path = Path(skill["path"]) / "SKILL.md"
            if skill_path.exists():
                skill_content = skill_path.read_text()
                system_prompt += f"\n---\n{skill_content}\n"

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            # Note: SDK automatically reads ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN from env
            model=model,
            system_prompt=system_prompt,
            allowed_tools=[
                *BUILTIN_TOOLS,
                *all_mcp_tools,
            ],
            mcp_servers=mcp_servers,
            hooks={
                "PreToolUse": [
                    HookMatcher(
                        matcher="Bash",
                        hooks=[
                            bash_security_hook,  # Command allowlist
                            secrets_scan_hook,  # Secrets detection
                        ],
                    ),
                ],
                "PostToolUse": [
                    HookMatcher(
                        matcher="Bash",
                        hooks=[
                            e2e_validation_hook,  # E2E test verification
                        ],
                    ),
                    HookMatcher(
                        matcher="mcp__puppeteer__*",
                        hooks=[
                            browser_cleanup_hook,  # Auto-cleanup browsers
                        ],
                    ),
                ],
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),  # Use absolute path
        )
    )
