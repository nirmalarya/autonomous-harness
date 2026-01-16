# Roadmap: v4.0.0 - Ralph Wiggum Plugin Foundational

**Strategic Decision**: Make the Ralph Wiggum plugin (for Claude Code) the PRIMARY iteration mechanism (not optional).

**Terminology**:
- **Claude Code CLI** = `@anthropic-ai/claude-code` (the host/main tool)
- **Ralph Wiggum Plugin** = Plugin that runs inside Claude Code CLI
- **Installation**: `npm install -g @anthropic-ai/claude-code` then `claude plugin install ralph-wiggum`

**Philosophy**: "Anthropic Native" - Use official Claude Code plugins, benefit from upstream improvements, align with Anthropic's vision.

---

## 🎯 Vision

**v3.7.0** (Current): Ralph philosophy via bash prompts (universal, zero deps)
**v4.0.0** (Target): Ralph Wiggum plugin (via Claude Code) as foundational implementation (Anthropic native)

### Why This Change?

1. **Official Plugin**: Ralph Wiggum is maintained by Anthropic, not us
2. **Claude Code Integration**: Uses Claude Code's plugin system and stop hooks
3. **Upstream Benefits**: Get improvements automatically from Anthropic
4. **Consistent Vision**: Align with Claude Code ecosystem
5. **Battle-Tested**: Ralph plugin used in production by Anthropic
6. **Stop Reinventing**: Focus on harness logic, not iteration mechanics
7. **Plugin Ecosystem**: Access to other Claude Code plugins (LSP, MCP, etc.)

---

## 📋 Implementation Plan

### Phase 1: Auto-Installation System (Week 1)

**Goal**: Seamlessly install Node.js + Claude Code CLI + Ralph Wiggum plugin on first run

**Dependencies Chain**:
1. Node.js v18+ (user installs manually)
2. Claude Code CLI (we auto-install via npm)
3. Ralph Wiggum plugin (we auto-install via `claude plugin install`)

#### 1.1 Pre-flight Check Module (`preflight.py`)

```python
"""Pre-flight checks for v4.0.0 dependencies."""

import shutil
import subprocess
from pathlib import Path


class PreflightChecker:
    """Check and install required dependencies."""

    def __init__(self):
        self.checks = {
            "node": self.check_node,
            "claude_cli": self.check_claude_cli,
            "ralph_plugin": self.check_ralph_plugin,
        }

    def check_all(self) -> tuple[bool, list[str]]:
        """Run all checks, return (all_passed, missing_items)."""
        missing = []
        for name, check_fn in self.checks.items():
            if not check_fn():
                missing.append(name)
        return len(missing) == 0, missing

    def check_node(self) -> bool:
        """Check if Node.js is installed (v18+ required)."""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                version = result.stdout.strip().lstrip('v')
                major = int(version.split('.')[0])
                return major >= 18
        except FileNotFoundError:
            pass
        return False

    def check_claude_cli(self) -> bool:
        """Check if Claude CLI is installed."""
        return shutil.which("claude") is not None

    def check_ralph_plugin(self) -> bool:
        """Check if Ralph Wiggum plugin is installed."""
        try:
            # Check global plugins directory
            result = subprocess.run(
                ["claude", "plugin", "list"],
                capture_output=True,
                text=True,
            )
            return "ralph-wiggum" in result.stdout
        except:
            return False

    def install_claude_code_cli(self) -> bool:
        """Install Claude Code CLI via npm."""
        try:
            print("📦 Installing Claude Code CLI (@anthropic-ai/claude-code)...")
            subprocess.run(
                ["npm", "install", "-g", "@anthropic-ai/claude-code"],
                check=True,
            )
            print("✅ Claude Code CLI installed successfully")
            print("   You can now use 'claude' command")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Claude Code CLI: {e}")
            return False

    def install_ralph_plugin(self) -> bool:
        """Install Ralph Wiggum plugin into Claude Code."""
        try:
            print("📦 Installing Ralph Wiggum plugin...")
            print("   (This is a plugin FOR Claude Code, not a standalone tool)")
            subprocess.run(
                ["claude", "plugin", "install", "ralph-wiggum"],
                check=True,
            )
            print("✅ Ralph Wiggum plugin installed successfully")
            print("   Plugin is now available within Claude Code")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Ralph Wiggum plugin: {e}")
            return False

    def auto_install_missing(self, missing: list[str]) -> bool:
        """Attempt to auto-install missing dependencies."""
        if "node" in missing:
            print("\n❌ Node.js v18+ is required but not found.")
            print("\n📖 Installation instructions:")
            print("   • macOS:   brew install node")
            print("   • Ubuntu:  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
            print("              sudo apt-get install -y nodejs")
            print("   • Windows: Download from https://nodejs.org/")
            print("\nAfter installing Node.js, run claude-harness again.")
            return False

        if "claude_cli" in missing:
            if not self.install_claude_cli():
                return False

        if "ralph_plugin" in missing:
            if not self.install_ralph_plugin():
                return False

        return True


def run_preflight() -> bool:
    """
    Run pre-flight checks and auto-install if possible.

    Returns:
        True if all dependencies satisfied, False otherwise
    """
    print("🔍 Running pre-flight checks for v4.0.0...")
    print()

    checker = PreflightChecker()
    all_passed, missing = checker.check_all()

    if all_passed:
        print("✅ All dependencies satisfied!")
        return True

    print(f"⚠️  Missing dependencies: {', '.join(missing)}")
    print()

    # Attempt auto-installation
    if checker.auto_install_missing(missing):
        # Re-check after installation
        all_passed, still_missing = checker.check_all()
        if all_passed:
            print("\n✅ All dependencies installed successfully!")
            return True
        else:
            print(f"\n❌ Still missing: {', '.join(still_missing)}")
            return False
    else:
        return False
```

#### 1.2 Integration into `autonomous_agent.py`

```python
# In autonomous_agent.py main()

from preflight import run_preflight

def main() -> None:
    # ... existing arg parsing ...

    # NEW: Pre-flight checks (v4.0.0)
    if not run_preflight():
        print("\n❌ Pre-flight checks failed. Cannot start harness.")
        print("Please install missing dependencies and try again.")
        return

    # ... rest of main() ...
```

---

### Phase 2: Ralph Loop Integration (Week 2)

**Goal**: Replace bash loops with `/ralph-loop` commands

#### 2.1 Enhanced Prompts with Ralph Commands

**File**: `prompts/coding_prompt_v4.md`

```markdown
## ITERATION PHILOSOPHY (v4.0.0 - Ralph CLI Native)

This harness uses the **Ralph Wiggum plugin** for iteration.

You have access to the `/ralph-loop` command for all iterative tasks.

### Completion Promises

Same as v3.7.0:
- `<promise>E2E_PASSED</promise>`
- `<promise>FEATURE_COMPLETE</promise>`
- `<promise>SERVICE_HEALTHY</promise>`
- `<promise>SCHEMA_READY</promise>`

### E2E Debugging with Ralph Loop

Instead of bash loops, use `/ralph-loop`:

```
/ralph-loop "Debug E2E test for Feature #X.

STEPS:
1. Check backend health (curl http://localhost:8100/health)
2. Check database (docker ps | grep postgres)
3. Check for zombie processes (ps aux | grep uvicorn)
4. If backend down: pkill -f uvicorn && cd backend && python -m uvicorn main:app --reload --port 8100 &
5. If database down: docker-compose up -d postgres
6. Re-run E2E test: python3 test_feature_X_e2e.py
7. If test passes: Output <promise>E2E_PASSED</promise>

Keep iterating until test passes or max iterations reached." \
--max-iterations 10 \
--completion-promise "E2E_PASSED"
```

**Benefits**:
- SDK-level stop hooks (more reliable)
- Automatic retry without manual loops
- Cleaner prompt structure
- Maintained by Anthropic

### Feature Quality Loop with Ralph

```
/ralph-loop "Run feature quality checklist for Feature #X.

QUALITY GATES:
1. Services healthy (backend responding)
2. Database schema validated
3. Browser integration tested (F12 DevTools)
4. E2E test created and passing
5. Screenshots saved to .claude/verification/
6. Zero TODOs in implementation code
7. Security checklist complete (if applicable)

After ALL gates pass: Output <promise>FEATURE_COMPLETE</promise>

Keep checking gates and fixing issues until all pass." \
--max-iterations 20 \
--completion-promise "FEATURE_COMPLETE"
```

### Infrastructure Healing with Ralph

```
/ralph-loop "Heal backend service.

STEPS:
1. Check if backend responds: curl -f http://localhost:8100/health
2. If fails: Check logs (tail -20 backend/logs/app.log)
3. Kill zombies: pkill -f uvicorn
4. Restart: cd backend && python -m uvicorn main:app --reload --port 8100 &
5. Wait 5 seconds
6. Re-check health
7. If healthy: Output <promise>SERVICE_HEALTHY</promise>

Keep healing until service is healthy." \
--max-iterations 5 \
--completion-promise "SERVICE_HEALTHY"
```
```

#### 2.2 Prompt Migration Script

```python
# scripts/migrate_prompts_v4.py
"""Convert v3.7.0 bash loops to v4.0.0 Ralph loops."""

def migrate_prompt_to_ralph(prompt_file: Path) -> None:
    """
    Convert bash while loops to /ralph-loop commands.

    Detects patterns like:
    - while [ $iteration -le $max_iterations ]
    - Replaces with /ralph-loop command
    """
    content = prompt_file.read_text()

    # Pattern: Bash iteration loop
    bash_loop_pattern = r'```bash\s*#!/bin/bash\s*# .*Loop.*\s*iteration=1.*?```'

    # Replace with Ralph command equivalent
    # ... (implementation details)

    prompt_file.write_text(migrated_content)
```

---

### Phase 3: Backward Compatibility Bridge (Week 3)

**Goal**: Smooth migration for existing v3.7.0 users

#### 3.1 Deprecation Warnings

```python
# In v3.7.1 (bridge release)
import warnings

def check_ralph_availability():
    """Warn if Ralph not available in v3.7.1."""
    if not has_ralph_plugin():
        warnings.warn(
            "v4.0.0 will require Ralph Wiggum plugin. "
            "Install now: npm install -g @anthropic-ai/claude-code && "
            "claude plugin install ralph-wiggum",
            FutureWarning,
        )
```

#### 3.2 Migration Guide

**File**: `MIGRATION_v3_to_v4.md`

```markdown
# Migration Guide: v3.7.x → v4.0.0

## Breaking Changes

v4.0.0 requires Node.js and Ralph Wiggum plugin.

### Before You Upgrade

1. **Check Node.js version**: `node --version` (v18+ required)
2. **Install Claude CLI**: `npm install -g @anthropic-ai/claude-code`
3. **Install Ralph plugin**: `claude plugin install ralph-wiggum`

### Auto-Installation

v4.0.0 will attempt to auto-install Claude CLI and Ralph plugin.
Node.js must be installed manually.

### What Changes

| v3.7.0 | v4.0.0 |
|--------|--------|
| Bash loops in prompts | `/ralph-loop` commands |
| Zero dependencies | Node.js required |
| Manual iteration | SDK-level stop hooks |

### Benefits of Upgrading

- More reliable iteration (SDK-level hooks)
- Maintained by Anthropic (upstream improvements)
- Cleaner prompt structure
- Better debugging capabilities

### If You Can't Install Node.js

Stay on v3.7.x - we'll maintain it for 6 months after v4.0.0 release.
```

---

### Phase 4: Testing & Validation (Week 4)

#### 4.1 Test Matrix

| Environment | Node.js | Claude CLI | Ralph | Expected Result |
|-------------|---------|------------|-------|-----------------|
| Fresh macOS | ❌ | ❌ | ❌ | Install Claude CLI + Ralph |
| macOS with Node | ✅ | ❌ | ❌ | Install Claude CLI + Ralph |
| macOS with CLI | ✅ | ✅ | ❌ | Install Ralph only |
| Full setup | ✅ | ✅ | ✅ | Run immediately |

#### 4.2 Integration Tests

```python
# tests/test_ralph_integration.py

import pytest

@pytest.mark.integration
async def test_ralph_loop_e2e_debugging():
    """Test E2E debugging via Ralph loop."""
    # Simulate E2E test failure
    # Trigger Ralph loop
    # Verify auto-healing
    # Verify completion promise
    pass

@pytest.mark.integration
async def test_ralph_loop_feature_quality():
    """Test feature quality loop via Ralph."""
    # Simulate feature with some gates failing
    # Trigger Ralph loop
    # Verify iterative gate checking
    # Verify completion promise
    pass

@pytest.mark.integration
async def test_preflight_auto_install():
    """Test auto-installation of missing dependencies."""
    # Mock missing Claude CLI
    # Run preflight
    # Verify installation attempted
    # Verify success message
    pass
```

---

### Phase 5: Documentation Updates (Week 5)

#### 5.1 README.md

```markdown
## Installation (v4.0.0)

### Prerequisites

- **Node.js v18+** (required)
- **Python 3.10+**

### Quick Install

```bash
# 1. Install Node.js (if not already installed)
# macOS:
brew install node

# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows:
# Download from https://nodejs.org/

# 2. Install claude-harness
pip install claude-harness

# 3. First run auto-installs Claude CLI + Ralph plugin
claude-harness --version
# Will prompt for auto-installation if needed

# 4. Run the harness
claude-harness --project-dir ./my_project --spec spec.txt
```

### What Gets Auto-Installed

On first run, claude-harness will install:
- Claude CLI (`@anthropic-ai/claude-code`)
- Ralph Wiggum plugin (`ralph-wiggum`)

You only need to install Node.js manually.
```

#### 5.2 CLAUDE.md

Update essential commands section:

```markdown
## Essential Commands (v4.0.0)

### Pre-flight Check

```bash
# Check if all dependencies are installed
node --version  # v18+ required
claude --version  # Should be installed by harness
claude plugin list  # Should show ralph-wiggum
```

### Manual Installation (if auto-install fails)

```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Install Ralph plugin
claude plugin install ralph-wiggum

# Verify
claude plugin list | grep ralph-wiggum
```
```

---

### Phase 6: Release Strategy

#### 6.1 Version Sequence

```
v3.7.0 (Current)  → Ralph philosophy via bash prompts
v3.7.1            → Add deprecation warnings for v4.0.0
v3.7.2            → Add preflight checker (non-blocking)
v3.8.0 (LTS)      → Last v3.x release with extended support
v4.0.0-beta.1     → Ralph CLI foundational (beta testing)
v4.0.0-beta.2     → Bug fixes + feedback
v4.0.0            → Official release with Ralph CLI required
```

#### 6.2 Support Timeline

| Version | Support End | Notes |
|---------|-------------|-------|
| v3.7.x | 2026-07-15 | Bug fixes only |
| v3.8.0 LTS | 2026-12-31 | Extended support for users without Node.js |
| v4.0.0+ | Ongoing | Active development |

---

## 🎯 Success Criteria

### Technical

- ✅ Auto-installation works on macOS, Linux, Windows
- ✅ Pre-flight checks are fast (<5 seconds)
- ✅ Ralph loops successfully replace bash loops
- ✅ Completion promises still enforced
- ✅ All existing features work with Ralph CLI

### User Experience

- ✅ Clear error messages when Node.js missing
- ✅ Seamless auto-installation of Claude CLI + Ralph
- ✅ Migration guide is clear and comprehensive
- ✅ Performance is same or better than v3.7.0

### Quality

- ✅ 90%+ test coverage for new code
- ✅ All integration tests pass
- ✅ Documentation is complete and accurate
- ✅ No regressions from v3.7.0 functionality

---

## 🚧 Risks & Mitigations

### Risk 1: Node.js Installation Barrier

**Risk**: Users without Node.js can't use harness
**Mitigation**:
- Clear error messages with install instructions
- Maintain v3.8.0 LTS for 6+ months
- Auto-detect Node.js and provide platform-specific instructions

### Risk 2: Claude CLI Installation Failures

**Risk**: npm install fails due to network/permissions
**Mitigation**:
- Retry logic with exponential backoff
- Fallback to manual instructions
- Log detailed error messages for debugging

### Risk 3: Ralph Plugin Compatibility

**Risk**: Ralph plugin changes breaking our integration
**Mitigation**:
- Pin to specific Ralph plugin version initially
- Monitor Anthropic's plugin releases
- Add version compatibility checks

### Risk 4: Breaking Change Backlash

**Risk**: Users upset about Node.js requirement
**Mitigation**:
- Clear communication in v3.7.1 deprecation warnings
- Extended v3.8.0 LTS support timeline
- Comprehensive migration guide
- Benefits clearly documented

---

## 📊 Migration Metrics

Track these during rollout:

- **Auto-install success rate**: Target 95%+
- **Manual installation rate**: Target <5%
- **Node.js already installed**: Expected 70%+
- **Upgrade adoption**: Target 80% within 3 months
- **Support tickets**: Monitor for common issues

---

## 🎓 Philosophy

**v3.7.0**: "Ralph philosophy, universal implementation"
**v4.0.0**: "Ralph philosophy, Anthropic native implementation"

We're not abandoning the bash approach because it was wrong.
We're embracing the official tool because it's **better maintained and more powerful**.

---

## 📅 Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Auto-installation | preflight.py, integration into autonomous_agent.py |
| 2 | Ralph integration | Updated prompts, /ralph-loop commands |
| 3 | Backward compat | Deprecation warnings, migration guide |
| 4 | Testing | Integration tests, manual testing |
| 5 | Documentation | README, CLAUDE.md, migration guide |
| 6 | Beta release | v4.0.0-beta.1 |
| 7-8 | Feedback & fixes | v4.0.0-beta.2 |
| 9 | Final release | v4.0.0 |

**Target Release**: ~2 months from now

---

## ✅ Next Actions

1. Create `preflight.py` module
2. Update `autonomous_agent.py` with pre-flight checks
3. Create `prompts/coding_prompt_v4.md` with Ralph commands
4. Write migration guide
5. Add deprecation warnings to v3.7.1
6. Begin testing on different environments

---

**Decision Maker**: Nirmalarya
**Date**: 2026-01-16
**Status**: Approved - Moving forward with Anthropic Native approach
