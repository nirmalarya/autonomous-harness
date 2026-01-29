#!/usr/bin/env python3
"""
Security Hook Tests
===================

Tests for the bash command security validation logic.
Compatible with both pytest and direct execution.
"""

import asyncio
import sys

import pytest

from security import (
    bash_security_hook,
    extract_commands,
    validate_chmod_command,
    validate_init_script,
)


def _check_hook(command: str, should_block: bool) -> bool:
    """Helper: Test a single command against the security hook."""
    input_data = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = asyncio.run(bash_security_hook(input_data))
    was_blocked = result.get("decision") == "block"
    return was_blocked == should_block


# Pytest-compatible test functions
class TestSecurityHook:
    """Pytest test class for security hook validation."""

    @pytest.mark.parametrize("command,should_block", [
        # Commands that SHOULD be blocked
        ("shutdown now", True),
        ("reboot", True),
        ("dd if=/dev/zero of=/dev/sda", True),
        ("pkill bash", True),
        ("pkill python", True),
        ('eval "pkill node"', True),
        ("chmod 777 file.sh", True),
        ("chmod 755 file.sh", True),
        ("chmod +w file.sh", True),
        ("chmod -R +x dir/", True),
        ("./setup.sh", True),
        ("./malicious.sh", True),
        # Commands that SHOULD be allowed
        ("ls -la", False),
        ("cat README.md", False),
        ("npm install", False),
        ("npm run build", False),
        ("git status", False),
        ("git commit -m 'test'", False),
        ("pkill node", False),
        ("pkill npm", False),
        ("chmod +x init.sh", False),
        ("./init.sh", False),
        ("npm install && npm run build", False),
    ])
    def test_security_hook(self, command: str, should_block: bool):
        """Test security hook blocks/allows commands correctly."""
        input_data = {"tool_name": "Bash", "tool_input": {"command": command}}
        result = asyncio.run(bash_security_hook(input_data))
        was_blocked = result.get("decision") == "block"
        
        expected = "blocked" if should_block else "allowed"
        actual = "blocked" if was_blocked else "allowed"
        reason = result.get("reason", "")
        
        assert was_blocked == should_block, (
            f"Command {command!r}: expected {expected}, got {actual}"
            + (f" (reason: {reason})" if reason else "")
        )


def test_extract_commands():
    """Test the command extraction logic."""
    test_cases = [
        ("ls -la", ["ls"]),
        ("npm install && npm run build", ["npm", "npm"]),
        ("cat file.txt | grep pattern", ["cat", "grep"]),
        ("/usr/bin/node script.js", ["node"]),
        ("VAR=value ls", ["ls"]),
        ("git status || git init", ["git", "git"]),
    ]

    for cmd, expected in test_cases:
        result = extract_commands(cmd)
        assert result == expected, f"extract_commands({cmd!r}): expected {expected}, got {result}"


def test_validate_chmod():
    """Test chmod command validation."""
    # Allowed cases
    allowed_cases = [
        ("chmod +x init.sh", "basic +x"),
        ("chmod +x script.sh", "+x on any script"),
        ("chmod u+x init.sh", "user +x"),
        ("chmod a+x init.sh", "all +x"),
        ("chmod ug+x init.sh", "user+group +x"),
        ("chmod +x file1.sh file2.sh", "multiple files"),
    ]
    
    for cmd, description in allowed_cases:
        allowed, reason = validate_chmod_command(cmd)
        assert allowed, f"chmod should allow {description}: {cmd!r} (reason: {reason})"

    # Blocked cases
    blocked_cases = [
        ("chmod 777 init.sh", "numeric mode"),
        ("chmod 755 init.sh", "numeric mode 755"),
        ("chmod +w init.sh", "write permission"),
        ("chmod +r init.sh", "read permission"),
        ("chmod -x init.sh", "remove execute"),
        ("chmod -R +x dir/", "recursive flag"),
        ("chmod +x", "missing file"),
    ]
    
    for cmd, description in blocked_cases:
        allowed, reason = validate_chmod_command(cmd)
        assert not allowed, f"chmod should block {description}: {cmd!r}"


def test_validate_init_script():
    """Test init.sh script execution validation."""
    # Allowed cases
    allowed_cases = [
        ("./init.sh", "basic ./init.sh"),
        ("./init.sh arg1 arg2", "with arguments"),
        ("/path/to/init.sh", "absolute path"),
    ]
    
    for cmd, description in allowed_cases:
        allowed, reason = validate_init_script(cmd)
        assert allowed, f"init.sh should allow {description}: {cmd!r} (reason: {reason})"

    # Blocked cases
    blocked_cases = [
        ("./setup.sh", "different script name"),
        ("./init.py", "python script"),
        ("bash init.sh", "bash invocation"),
        ("sh init.sh", "sh invocation"),
        ("./malicious.sh", "malicious script"),
    ]
    
    for cmd, description in blocked_cases:
        allowed, reason = validate_init_script(cmd)
        assert not allowed, f"init.sh should block {description}: {cmd!r}"


# Legacy main() for direct execution
def main():
    """Run all tests (for direct execution: python test_security.py)."""
    print("=" * 70)
    print("  SECURITY HOOK TESTS")
    print("=" * 70)

    passed = 0
    failed = 0

    # Test extract_commands
    print("\nTesting command extraction:\n")
    test_cases = [
        ("ls -la", ["ls"]),
        ("npm install && npm run build", ["npm", "npm"]),
        ("cat file.txt | grep pattern", ["cat", "grep"]),
    ]
    for cmd, expected in test_cases:
        result = extract_commands(cmd)
        if result == expected:
            print(f"  PASS: {cmd!r} -> {result}")
            passed += 1
        else:
            print(f"  FAIL: {cmd!r} - expected {expected}, got {result}")
            failed += 1

    # Test security hook
    print("\nTesting security hook:\n")
    
    # Should be blocked
    blocked = [
        "shutdown now",
        "pkill bash",
        "chmod 777 file.sh",
        "./setup.sh",
    ]
    for cmd in blocked:
        if _check_hook(cmd, should_block=True):
            print(f"  PASS: {cmd!r} (blocked)")
            passed += 1
        else:
            print(f"  FAIL: {cmd!r} should be blocked")
            failed += 1

    # Should be allowed
    allowed = [
        "ls -la",
        "npm install",
        "git status",
        "chmod +x init.sh",
        "./init.sh",
    ]
    for cmd in allowed:
        if _check_hook(cmd, should_block=False):
            print(f"  PASS: {cmd!r} (allowed)")
            passed += 1
        else:
            print(f"  FAIL: {cmd!r} should be allowed")
            failed += 1

    # Summary
    print("\n" + "-" * 70)
    print(f"  Results: {passed} passed, {failed} failed")
    print("-" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
