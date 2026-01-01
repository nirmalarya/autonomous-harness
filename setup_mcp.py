"""
MCP Server Auto-Configuration for claude-harness v3.0
==========================================================

Dynamically configures MCP servers based on mode.
"""

import os


class MCPServerSetup:
    """Auto-configure MCP servers based on execution mode."""

    def setup(self, mode: str) -> dict:
        """
        Auto-configure MCP servers based on mode.

        Args:
            mode: Execution mode (greenfield, enhancement, bugfix, backlog)

        Returns:
            Dictionary of MCP server configurations
        """
        servers = {}

        # 1. Documentation MCP (ALL modes - query latest tech stack docs)
        servers.update(self._setup_documentation_mcp())

        # 2. Browser automation (greenfield, enhancement modes)
        if mode in ["greenfield", "enhancement"]:
            servers.update(self._setup_browser_mcp())

        # 3. Azure DevOps (backlog mode)
        if mode == "backlog":
            servers.update(self._setup_azure_devops_mcp())

        return servers

    def _setup_documentation_mcp(self) -> dict:
        """
        Setup documentation MCP server.

        Preference order:
        1. Ref Tools (token-efficient, premium) if REF_TOOLS_API_KEY set
        2. Context7 (free fallback)
        """
        ref_api_key = os.getenv("REF_TOOLS_API_KEY")

        if ref_api_key:
            # Premium: More token-efficient
            return {
                "ref": {
                    "command": "npx",
                    "args": ["-y", "@ref-tools/ref-tools-mcp"],
                    "env": {"REF_TOOLS_API_KEY": ref_api_key}
                }
            }
        else:
            # Free fallback
            return {
                "context7": {
                    "command": "npx",
                    "args": ["-y", "@upstash/context7-mcp"]
                }
            }

    def _setup_browser_mcp(self) -> dict:
        """
        Setup browser automation MCP.

        Uses official Puppeteer MCP server with automatic session cleanup.
        This prevents browser instances from staying open after tests complete.
        """
        return {
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
            }
        }

    def _setup_azure_devops_mcp(self) -> dict:
        """
        Setup Azure DevOps MCP for backlog mode.

        Requires environment variables:
        - ADO_ORG: Azure DevOps organization name
        - ADO_PROJECT: Azure DevOps project name
        """
        ado_org = os.getenv("ADO_ORG")
        ado_project = os.getenv("ADO_PROJECT")

        if not ado_org or not ado_project:
            print("⚠️  Warning: ADO_ORG or ADO_PROJECT not set (Azure DevOps MCP disabled)")
            return {}

        return {
            "azure-devops": {
                "command": "npx",
                "args": ["-y", "@microsoft/azure-devops-mcp-server"],
                "env": {
                    "AZURE_DEVOPS_ORG": ado_org,
                    "AZURE_DEVOPS_PROJECT": ado_project
                }
            }
        }

    def get_documentation_server_name(self) -> str:
        """Get the name of the configured documentation MCP server."""
        return "ref" if os.getenv("REF_TOOLS_API_KEY") else "context7"

    def get_browser_tools(self) -> list[str]:
        """
        Get list of browser automation tool names.

        Returns Puppeteer tools (proven to work well).
        """
        return [
            "mcp__puppeteer__puppeteer_navigate",
            "mcp__puppeteer__puppeteer_screenshot",
            "mcp__puppeteer__puppeteer_click",
            "mcp__puppeteer__puppeteer_fill",
            "mcp__puppeteer__puppeteer_select",
            "mcp__puppeteer__puppeteer_hover",
            "mcp__puppeteer__puppeteer_evaluate",
        ]

    def get_documentation_tools(self) -> list[str]:
        """Get list of documentation tool names based on configured server."""
        doc_server = self.get_documentation_server_name()

        if doc_server == "ref":
            return [
                "mcp__ref__search",
                "mcp__ref__get_docs",
            ]
        else:  # context7
            return [
                "mcp__context7__resolve_library_id",
                "mcp__context7__get_library_docs",
            ]

    def get_azure_devops_tools(self) -> list[str]:
        """Get list of Azure DevOps tool names."""
        return [
            "mcp__azure_devops__get_work_items",
            "mcp__azure_devops__update_work_item",
            "mcp__azure_devops__create_work_item",
            "mcp__azure_devops__get_work_item_comments",
            "mcp__azure_devops__add_work_item_comment",
        ]
