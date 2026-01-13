# claude-harness v3.1.0 User Guide

**Production-ready autonomous coding harness using Claude Code SDK**

Build complete applications autonomously with battle-tested reliability features.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Operating Modes](#operating-modes)
- [Command Reference](#command-reference)
- [Reliability Features](#reliability-features)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Claude Code OAuth token

### Install claude-harness

```bash
# Install from source (development mode)
cd /path/to/claude-harness
pip install -e .

# Or install from git (future)
pip install git+https://github.com/nirmalarya/claude-harness.git
```

### Set Up OAuth Token

```bash
# Generate token using Claude Code CLI
claude setup-token

# Set environment variable (add to ~/.zshrc or ~/.bashrc for persistence)
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'
```

### Verify Installation

```bash
# Check version
claude-harness --version
# Output: claude-harness v3.1.0

# View help
claude-harness --help
```

---

## Quick Start

### Build a New App (Greenfield Mode)

```bash
# Create a simple todo app
claude-harness \
    --mode greenfield \
    --project-dir ./my-todo-app \
    --max-iterations 5

# The agent will:
# 1. Read prompts/app_spec.txt (or create default spec)
# 2. Generate feature_list.json with test cases
# 3. Implement features one by one
# 4. Run tests and commit each feature
```

### Add Features to Existing App (Enhancement Mode)

```bash
# Create enhancement spec
cat > enhancements.txt << 'EOF'
- Add user authentication with JWT
- Add dark mode toggle
- Add export to CSV functionality
EOF

# Run enhancement mode
claude-harness \
    --mode enhancement \
    --project-dir ./existing-app \
    --spec ./enhancements.txt
```

### Fix Bugs (Bugfix Mode)

```bash
# Create bugfix spec
cat > bugfixes.txt << 'EOF'
- Fix memory leak in WebSocket connection
- Fix race condition in user registration
- Fix XSS vulnerability in comment input
EOF

# Run bugfix mode
claude-harness \
    --mode bugfix \
    --project-dir ./existing-app \
    --spec ./bugfixes.txt
```

---

## Operating Modes

### Greenfield Mode (New Projects)

**Purpose:** Build a complete application from scratch

**How it works:**
1. **Session 1 (Initializer):** Reads app spec, creates feature_list.json, sets up project
2. **Sessions 2-N (Coding):** Implements features one by one, tests, commits

**Example:**
```bash
claude-harness \
    --mode greenfield \
    --project-dir ./my-saas-app \
    --max-iterations 10
```

**State Tracking:**
- `spec/feature_list.json` - All features with `passing: true/false`
- Git commits - One commit per feature
- `claude-progress.txt` - Session notes

---

### Enhancement Mode (Existing Projects)

**Purpose:** Add new features to an existing codebase

**How it works:**
1. Reads enhancement spec (features listed as `- Feature name`)
2. Creates `.claude/enhancement-state.json` to track progress
3. Implements each enhancement incrementally
4. Auto-runs infrastructure healing (Docker, migrations, etc.)

**Example:**
```bash
claude-harness \
    --mode enhancement \
    --project-dir ./my-existing-app \
    --spec ./enhancements.txt \
    --max-retries 5
```

**State Tracking:**
- `.claude/enhancement-state.json` - Enhancement progress
- `.claude/retry_state.json` - Retry history
- `.claude/errors.json` - Error log

---

### Bugfix Mode (Existing Projects)

**Purpose:** Fix bugs in an existing codebase

**How it works:**
1. Reads bugfix spec (bugs listed as `- Bug description`)
2. Creates `.claude/bugfix-state.json` to track progress
3. Fixes each bug with tests to prevent regression
4. Validates fixes before committing

**Example:**
```bash
claude-harness \
    --mode bugfix \
    --project-dir ./production-app \
    --spec ./critical-bugs.txt \
    --stall-timeout 15
```

**State Tracking:**
- `.claude/bugfix-state.json` - Bugfix progress
- `.claude/verification/` - E2E test screenshots
- Git commits with regression tests

---

## Command Reference

### All Options

```bash
claude-harness [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir PATH` | Project directory (relative paths placed in `generations/`) | `./autonomous_demo_project` |
| `--mode {greenfield,enhancement,bugfix}` | Development mode | `greenfield` |
| `--spec PATH` | Specification file (required for enhancement/bugfix) | None |
| `--max-iterations N` | Maximum agent iterations | Unlimited |
| `--model NAME` | Claude model to use | `claude-sonnet-4-5-20250929` |
| `--session-timeout N` | Overall session timeout (minutes) | 120 |
| `--stall-timeout N` | No-activity stall timeout (minutes) | 10 |
| `--max-retries N` | Max retry attempts per feature | 3 |
| `--version` | Show version and exit | - |
| `--help` | Show help and exit | - |

### Examples

**Quick test (3 iterations):**
```bash
claude-harness --project-dir ./test-app --max-iterations 3
```

**Production run with custom timeouts:**
```bash
claude-harness \
    --project-dir ./saas-app \
    --session-timeout 180 \
    --stall-timeout 15 \
    --max-retries 5
```

**Enhancement with spec:**
```bash
claude-harness \
    --mode enhancement \
    --project-dir ./existing-app \
    --spec ./specs/new-features.txt
```

---

## Reliability Features (v3.1.0)

### 1. Triple Timeout Protection

**Problem Solved:** Sessions hanging indefinitely when API fails

**Three-layer protection:**

| Timeout | Duration | Triggers When | Purpose |
|---------|----------|---------------|---------|
| No Initial Response | 15 min | Before first tool call | API never responded |
| Stall Timeout | 10 min | After first tool call | API stopped mid-session |
| Session Timeout | 120 min | Anytime | Overall runaway protection |

**Example:**
```bash
# Use shorter timeouts for testing
claude-harness \
    --project-dir ./test-app \
    --session-timeout 30 \
    --stall-timeout 5
```

**What happens on timeout:**
1. Session stops gracefully
2. Error logged to `.claude/errors.json`
3. Feature marked for retry
4. Fresh session starts automatically

---

### 2. Retry + Skip Logic

**Problem Solved:** Features fail randomly due to API issues, context size, transient errors

**How it works:**
- Auto-retry failed features (default: 3 attempts)
- Skip features after max retries (prevents infinite loops)
- Continue with remaining work
- Persist retry state across sessions

**Example flow:**
```
Feature 42: "Add user authentication"
  Attempt 1: Failed (context too large)
  Attempt 2: Failed (API timeout)
  Attempt 3: Failed (stalled)
  ⚠️  Feature 42 failed 3 times - SKIPPING
  Will continue with remaining features

Feature 43: "Add dashboard"
  Attempt 1: Success ✅
```

**Configure retries:**
```bash
claude-harness --project-dir ./app --max-retries 5
```

**State tracking:**
- `.claude/retry_state.json` - Retry counts, skipped features, retry history

---

### 3. Loop Detection

**Problem Solved:** Agent stuck reading same files repeatedly, burning tokens

**Detection rules:**
- Repeated file reads (max 3 times per file)
- No progress (30+ reads, 0 writes)
- Triggers timeout early (not waiting for 120-min timeout)

**What happens:**
1. Loop detected
2. Session stopped
3. Feature marked for retry with fresh context

---

### 4. Comprehensive Error Handling

**Problem Solved:** Errors swallowed silently, making debugging impossible

**Features:**
- Structured error logging to `.claude/errors.json`
- User-friendly error messages with context
- Full Python traceback capture
- Error categorization (fatal vs recoverable)
- Session error summaries

**Error log format:**
```json
{
  "timestamp": "2025-12-31T10:30:45",
  "session_start": "2025-12-31T10:00:00",
  "context": "agent_session",
  "error_type": "TimeoutError",
  "error_message": "API request timed out",
  "traceback": "...",
  "feature_id": "feature-42",
  "fatal": false
}
```

**View errors:**
```bash
cat .claude/errors.json | python3 -m json.tool
```

---

### 5. E2E Validation Enforcement

**Problem Solved:** Agent skips E2E tests, ships broken UI features

**How it works:**
1. Agent implements user-facing feature
2. Tries to commit
3. Hook checks for E2E tests:
   - Screenshots in `.claude/verification/`?
   - `test_results.json` exists?
   - All tests passed?
4. If missing → Commit BLOCKED with error
5. Agent creates E2E tests using Puppeteer
6. Commit succeeds with E2E validation ✅

**Benefits:**
- Programmatic enforcement (can't skip)
- Guaranteed E2E coverage for UI features
- Stronger than Anthropic's prompt-only approach

---

## How It Works

### Two-Agent Pattern (Anthropic's Proven System)

**Session 1: Initializer Agent**
- Reads `app_spec.txt` or user-provided spec
- Generates `spec/feature_list.json` with 100-200 test cases
- Sets up project structure (directories, git, package.json, etc.)
- Creates `init.sh` for running the app
- Configures MCP servers (Context7, Puppeteer)
- Sets up security hooks

**Sessions 2-N: Coding Agents**
- Fresh context each session (no memory from previous sessions)
- Reads `spec/feature_list.json` to find next unimplemented feature
- Implements ONE feature at a time
- Writes tests (unit + E2E for UI features)
- Runs tests until passing
- Commits feature with tests
- Updates `feature_list.json` (`passing: true`)
- Repeats for next feature

**Session Management:**
- Each session runs independently
- Progress persisted via `feature_list.json` and git commits
- Auto-continues between sessions (3-second delay)
- `Ctrl+C` to pause; run same command to resume

---

## Project Structure

### Generated by claude-harness

After running, your project contains:

```
my_project/
├── spec/
│   └── feature_list.json       # Test cases (source of truth)
├── .claude/
│   ├── verification/            # E2E test screenshots
│   │   ├── feature-1-*.png
│   │   └── test_results.json
│   ├── retry_state.json         # Retry tracking
│   ├── errors.json              # Error log
│   └── enhancement-state.json   # Enhancement progress (if applicable)
├── .claude_settings.json        # Security settings, MCP config
├── claude-progress.txt          # Session notes
├── app_spec.txt                 # Copied specification
├── init.sh                      # Environment setup script
├── .git/                        # Git repository
└── [application files]          # Generated code (src/, tests/, etc.)
```

### claude-harness Source Structure

```
claude-harness/
├── autonomous_agent.py       # CLI entry point
├── agent.py                  # Agent session orchestration
├── client.py                 # Claude SDK client + security hooks
├── loop_detector.py          # Triple timeout protection
├── retry_manager.py          # Retry + skip logic
├── error_handler.py          # Error logging + handling
├── security.py               # Bash command allowlist
├── setup_mcp.py              # MCP server auto-configuration
├── prompts.py                # Prompt loading utilities
├── progress.py               # Progress tracking
├── output_formatter.py       # Output formatting
├── prompts/
│   ├── initializer_prompt.md         # Greenfield session 1
│   ├── coding_prompt.md              # Greenfield sessions 2-N
│   ├── enhancement_initializer_prompt.md
│   ├── enhancement_coding_prompt.md
│   ├── bugfix_mode_prompt.md
│   └── app_spec.txt                  # Default app spec
├── validators/
│   ├── e2e_hook.py           # E2E validation hook
│   ├── e2e_verifier.py       # E2E test checker
│   └── secrets_scanner.py    # Secrets detection
├── infra/
│   └── healer.py             # Infrastructure self-healing
├── setup.py                  # Package configuration
├── pyproject.toml            # Modern Python packaging
├── requirements.txt          # Dependencies
├── VERSION                   # Version number (3.1.0)
└── README.md                 # Project overview
```

---

## Advanced Usage

### Custom App Specifications

**Create your own spec:**
```bash
cat > my_app_spec.txt << 'EOF'
# My SaaS Application

Build a multi-tenant SaaS platform with:
- User authentication (JWT)
- Subscription management (Stripe)
- Admin dashboard
- API rate limiting
- Email notifications
- Audit logging
EOF

# Place in project prompts directory
cp my_app_spec.txt /path/to/claude-harness/prompts/app_spec.txt

# Run
claude-harness --project-dir ./my-saas
```

### Resume After Interruption

```bash
# Start run
claude-harness --project-dir ./my-app --max-iterations 10

# Press Ctrl+C to pause
^C
Interrupted by user
To resume, run the same command again

# Resume (picks up where it left off)
claude-harness --project-dir ./my-app --max-iterations 10
```

### Monitor Progress

```bash
# Watch feature progress
cat my_project/spec/feature_list.json | python3 -c "
import json, sys
features = json.load(sys.stdin)
passing = sum(1 for f in features if f.get('passing'))
print(f'Progress: {passing}/{len(features)} features passing ({passing*100//len(features)}%)')
"

# View session notes
tail -f my_project/claude-progress.txt

# Check error log
cat my_project/.claude/errors.json | python3 -m json.tool

# View retry state
cat my_project/.claude/retry_state.json | python3 -m json.tool
```

### Test-Only Run (No Code Changes)

```bash
# Validation mode (future feature)
claude-harness \
    --mode validation \
    --project-dir ./my-app
```

---

## Troubleshooting

### "Command not found: claude-harness"

**Solution:**
```bash
# Reload shell
exec zsh  # or exec bash

# Or check PATH
echo $PATH | grep homebrew

# If missing, add to ~/.zshrc:
export PATH="/opt/homebrew/bin:$PATH"
source ~/.zshrc

# Verify
which claude-harness
```

---

### "OAuth token not set"

**Solution:**
```bash
# Generate token
claude setup-token

# Set permanently (add to ~/.zshrc)
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'
source ~/.zshrc

# Verify
echo $CLAUDE_CODE_OAUTH_TOKEN
```

---

### "Session appears to hang"

**Likely normal!** The initializer session generates 100-200 test cases, which takes time.

**How to verify it's working:**
- Watch for `[Tool: ...]` output (shows agent is active)
- Check `claude-progress.txt` for updates
- Look for file writes in the project directory

**If truly stuck (>15 minutes with no output):**
- Timeout will kick in automatically
- Session will restart with fresh context
- Check `.claude/errors.json` for details

---

### "Feature keeps failing and retrying"

**Check retry state:**
```bash
cat .claude/retry_state.json | python3 -m json.tool
```

**Common causes:**
- Context too large (reduce feature complexity in spec)
- API timeout (check network connection)
- Test failures (check test output in commits)

**Solutions:**
- Increase `--max-retries` (more attempts)
- Increase `--stall-timeout` (more time per session)
- Simplify failing feature in `feature_list.json`

---

### "E2E tests not running"

**v3.1.0 fixed this!** E2E tests are now enforced.

**Verify fix:**
```bash
# Check hook is working
python3 -c "from validators.e2e_hook import get_current_feature; print('✅ Hook works')"

# Check for E2E validation
ls -la .claude/verification/
cat .claude/verification/test_results.json
```

**If still missing:**
- Check `.claude_settings.json` has hooks enabled
- Verify feature is user-facing (UI feature)
- Check git commit messages for E2E enforcement errors

---

### "Command blocked by security hook"

**Expected behavior!** Security hooks prevent dangerous commands.

**Check what was blocked:**
```bash
# Recent git history shows blocked commands
git log --oneline -5
```

**If command is safe:**
```bash
# Edit security allowlist
vim security.py

# Add command to ALLOWED_COMMANDS
ALLOWED_COMMANDS = {
    ...
    "your-safe-command",
}

# Reinstall
pip install -e .
```

---

## Best Practices

### 1. Start Small

**Don't:**
```bash
# Requesting 500 features on first try
claude-harness --project-dir ./huge-app  # Will take days!
```

**Do:**
```bash
# Start with limited iterations
claude-harness --project-dir ./test-app --max-iterations 5

# Review output, iterate
```

---

### 2. Use Descriptive Specs

**Bad spec:**
```
Build an app
```

**Good spec:**
```
# E-commerce Platform

Build a full-stack e-commerce site with:
- Product catalog with search/filter
- Shopping cart with session persistence
- Stripe checkout integration
- Order history for users
- Admin panel for inventory management
- Email confirmations for orders

Tech stack: Next.js 15, PostgreSQL, Prisma, Tailwind
```

---

### 3. Monitor Progress Actively

```bash
# Terminal 1: Run harness
claude-harness --project-dir ./my-app

# Terminal 2: Monitor progress
watch -n 5 'cat my-app/spec/feature_list.json | python3 -c "import json, sys; f=json.load(sys.stdin); print(f\"Progress: {sum(1 for x in f if x.get(\"passing\"))}/{len(f)}\")"'

# Terminal 3: Watch errors
tail -f my-app/.claude/errors.json
```

---

### 4. Commit to Git Regularly

The harness auto-commits, but you should also:
```bash
# Tag milestones
cd my-app
git tag v0.1.0 -m "50 features complete"

# Create branches for experiments
git checkout -b feature/new-payment-gateway

# Push to remote regularly
git push origin main --tags
```

---

### 5. Review Generated Code

**Don't blindly trust!** After each session:
```bash
# Review recent commits
git log --oneline -10
git show HEAD

# Run tests manually
npm test  # or pytest, etc.

# Check code quality
npm run lint
```

---

### 6. Use Enhancement Mode for Existing Projects

**Don't:**
```bash
# Starting from scratch when you have existing code
claude-harness --mode greenfield --project-dir ./existing-app  # Will overwrite!
```

**Do:**
```bash
# Use enhancement mode
claude-harness --mode enhancement --project-dir ./existing-app --spec ./new-features.txt
```

---

### 7. Tune Timeouts for Your Use Case

**Fast iteration (development):**
```bash
claude-harness \
    --session-timeout 30 \
    --stall-timeout 5 \
    --max-retries 2
```

**Production stability:**
```bash
claude-harness \
    --session-timeout 180 \
    --stall-timeout 20 \
    --max-retries 5
```

---

## What's New in v3.1.0

### Major Features
- ✅ **Triple Timeout Protection** (15/10/120 min)
- ✅ **Retry + Skip Logic** (3 retries, then skip)
- ✅ **Loop Detection** (prevents infinite loops)
- ✅ **Comprehensive Error Logging** (`.claude/errors.json`)
- ✅ **E2E Validation Enforcement** (CRITICAL BUG FIX)
- ✅ **MCP Auto-Configuration** (Context7, Puppeteer)
- ✅ **Security Hooks** (secrets scanning)

### Breaking Changes
None! v3.1.0 is backward compatible with v3.0.0 projects.

### Upgrade from v3.0.0
```bash
# Pull latest code
cd /path/to/claude-harness
git pull

# Reinstall
pip install -e . --force-reinstall

# Verify
claude-harness --version
# Output: claude-harness v3.1.0
```

---

## Support

**Issues:** Report bugs at repository issue tracker

**Docs:**
- `README.md` - Project overview
- `USER_GUIDE.md` - This guide
- `CHANGELOG_v3.1.0.md` - Release notes
- `VALIDATION_COMPLETE.md` - Production readiness validation

**Examples:**
- `ai-trading-platform-test-v3.1/README.md` - Full test example

---

**claude-harness v3.1.0** - Production-ready autonomous coding 🚀

Built with ❤️ using Claude Agent SDK
