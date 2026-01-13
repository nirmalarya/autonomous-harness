"""
Secrets scanning hook for Claude Agent SDK.

PreToolUse hook that blocks git commits if secrets are detected.
"""

from pathlib import Path

from .secrets_scanner import SecretsScanner


async def secrets_scan_hook(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """
    PreToolUse hook - blocks git commits if secrets detected.

    Args:
        input_data: Tool input (e.g., {"command": "git commit ..."})
        tool_use_id: Unique ID for this tool use
        context: Execution context (cwd, etc.)

    Returns:
        Hook result - either {} (allow) or {"permission": "deny", "user_message": ..., "agent_message": ...}
    """
    command = input_data.get("command", "")

    # Check if this is a git commit or git add (both can stage secrets)
    if "git commit" not in command and "git add" not in command:
        return {}  # Not a git operation, allow

    # Get project directory from context
    project_dir = Path(context.get("cwd", "."))
    scanner = SecretsScanner(project_dir)

    # Scan for secrets
    violations = scanner.scan()

    if violations:
        # Format violations for display
        violation_list = []
        for v in violations[:10]:  # Show max 10
            violation_list.append(f"  - {v.file}:{v.line} ({v.type}): {v.match}")

        violations_str = "\n".join(violation_list)
        if len(violations) > 10:
            violations_str += f"\n  ...and {len(violations) - 10} more"

        return {
            "permission": "deny",
            "user_message": f"⛔ SECRETS DETECTED - Commit blocked ({len(violations)} violations)",
            "agent_message": f"""Security violation: Secrets detected in code!

Found {len(violations)} potential secret(s):
{violations_str}

NEVER commit:
- API keys, passwords, tokens
- .env files or credentials
- Private keys or certificates

Actions to take:
1. Remove the secrets from the files
2. Use environment variables instead (process.env.API_KEY, os.getenv("API_KEY"), etc.)
3. Add sensitive files to .gitignore
4. Try the commit again after fixing

Do NOT bypass this check. Security is critical.
""",
        }

    return {}  # No secrets found, allow the operation
