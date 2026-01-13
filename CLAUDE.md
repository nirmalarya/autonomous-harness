# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**claude-harness** is a production-ready autonomous coding harness built on Claude Code SDK. It enables building complete applications autonomously using a two-agent pattern (initializer + coding agents) with continuous session management and progress persistence.

**Core Concept**: Long-running autonomous development sessions where agents auto-continue between sessions with fresh context windows, tracking progress via `feature_list.json` and git commits.

## Essential Commands

### Development Setup

```bash
# Install in editable mode
pip install -e .

# Install dev dependencies
pip install pytest pytest-asyncio ruff mypy types-pyyaml build

# Set authentication (choose one)
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'  # OAuth token
# OR
export ANTHROPIC_API_KEY='your-api-key-here'      # API key

# Verify installation
claude-harness --version
```

### Testing

```bash
# Run all tests
pytest tests/test_*.py -v

# Run specific test file
pytest tests/test_security.py -v

# Run with coverage
pytest --cov=. --cov-report=term tests/test_*.py
```

### Linting & Type Checking

```bash
# Check code style
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Check formatting without changes
ruff format --check .

# Type check
mypy *.py --ignore-missing-imports
```

### Building & Distribution

```bash
# Build package
python -m build

# Install from wheel
pip install dist/*.whl

# Verify CLI
claude-harness --version
```

### Running the Harness

```bash
# Greenfield mode (new project)
claude-harness --project-dir ./my_project --spec prompts/app_spec.txt

# Enhancement mode (existing project)
claude-harness --mode enhancement --project-dir ./existing-app --spec features.txt

# Backlog mode (with Linear or Azure DevOps)
export LINEAR_API_KEY='lin_api_...'
claude-harness --mode backlog --project-dir ./my_project

# Test with limited iterations
claude-harness --project-dir ./test_project --max-iterations 3
```

## Architecture

### Two-Agent Pattern

The harness uses a two-phase autonomous workflow:

1. **Initializer Agent (Session 1)**: Reads specification, generates comprehensive `feature_list.json` with 200 test cases, sets up project structure, initializes git
2. **Coding Agent (Sessions 2+)**: Picks up from last checkpoint, implements features sequentially, marks them complete in `feature_list.json`

**Key insight**: Each session runs with fresh context, so progress MUST be persisted via files (feature_list.json) and git commits. The agent relies on these artifacts to understand where it left off.

### Core Modules

**Entry Points**:
- `autonomous_agent.py` - CLI entry point, argument parsing, version management
- `agent.py` - Session orchestration, timeout handling, progress tracking

**Client Configuration**:
- `client.py` - Claude SDK client creation with multi-layered security, skills integration, LSP setup, MCP server configuration
- `security.py` - Bash command allowlist (ALLOWED_COMMANDS), command validation hooks
- `skills_manager.py` - Auto-discovers and loads Claude Code Skills from `.claude/skills/` (project and global)
- `lsp_plugins.py` - Language Server Protocol integration for code intelligence (goToDefinition, findReferences, etc.)

**Quality & Safety**:
- `validators/e2e_hook.py` - Enforces E2E test execution for user-facing features
- `validators/e2e_verifier.py` - Mandatory E2E debugging (v3.2.2), blocks workarounds
- `validators/secrets_hook.py` - Scans git commits for leaked credentials
- `validators/browser_cleanup_hook.py` - Cleans up zombie browser processes

**Session Management**:
- `loop_detector.py` - Detects infinite loops (repeated file reads, stuck patterns)
- `retry_manager.py` - Feature retry logic (3 attempts max), skip tracking
- `error_handler.py` - Structured error logging and recovery
- `progress.py` - Progress file management, session headers

**Infrastructure**:
- `setup_mcp.py` - Auto-configures MCP servers (Puppeteer for E2E testing, Context7 for docs)
- `infra/healer.py` - Self-healing infrastructure (restarts backend, fixes DB connections)

**Prompts**: `prompts/` directory contains mode-specific system prompts and quality gates

### Defense-in-Depth Security

The harness uses 5 layers of security (see `client.py`):

1. **Sandbox**: OS-level bash command isolation prevents filesystem escape
2. **Permissions**: File operations restricted to project directory only (`"./**"` paths)
3. **Bash Allowlist**: Only commands in `ALLOWED_COMMANDS` can execute (see `security.py`)
4. **Secrets Scanning**: Git commits blocked if API keys/tokens detected
5. **E2E Validation**: User-facing features require passing E2E tests

**Security Hook Pattern**: Hooks run BEFORE tools execute, can block dangerous operations. See `bash_security_hook()`, `secrets_scan_hook()`, `e2e_validation_hook()`.

### Skills System (v3.2.0+)

Skills are reusable domain knowledge loaded from:
1. Harness built-ins: `harness_data/.claude/skills/` (bundled with package)
2. Global skills: `~/.claude/skills/`
3. Project skills: `.claude/skills/` (in project directory)

**Mode-specific skills**:
- **Greenfield**: puppeteer-testing, code-quality, project-patterns, harness-patterns, lsp-navigation
- **Enhancement**: code-quality, project-patterns, lsp-navigation
- **Backlog**: code-quality, azure-devops-workflow, lsp-navigation

Skills use progressive disclosure: `SKILL.md` + supporting files (patterns.md, examples/, etc.). Claude auto-matches skills based on description in frontmatter.

### LSP Integration (v3.2.0+)

Language Server Protocol provides code intelligence:
- **Auto-installation**: Detects tech stack, installs language servers (TypeScript, Python, etc.)
- **LSP Plugins**: Official marketplace plugins for goToDefinition, findReferences, hover, documentSymbol
- **Context-aware**: Agent can navigate codebases, understand existing patterns before changes

Enable LSP: `lsp_manager = LSPPluginManager(project_dir)` in `client.py`

### MCP Servers

Auto-configured based on mode:
- **Puppeteer** (greenfield, enhancement): E2E testing with browser automation
- **Context7** (all modes): Documentation search (Next.js, React, FastAPI, etc.)
- **Azure DevOps** (backlog mode): Fetch/update work items, create PRs
- **Linear** (backlog mode): Issue tracking integration

MCP setup in `setup_mcp.py`, integrated via `client.py`.

## Key Patterns

### Progress Persistence

**Critical**: Agents have fresh context each session. Progress MUST be written to disk:
- `feature_list.json` - Source of truth for feature status
- `claude-progress.txt` - Session notes and decisions
- Git commits - Atomic progress checkpoints

**Anti-pattern**: Don't rely on conversation history. Always check files for current state.

### Timeout Protection (v3.1.0+)

Triple timeout system prevents hangs:
1. **No-response timeout** (15 min): Agent not producing output
2. **Stall timeout** (10 min): No progress detected (loop detector)
3. **Session timeout** (120 min): Overall session limit

Implemented in `loop_detector.py`, checked in `agent.py`.

### Retry & Skip Logic

Features can fail. The retry manager (`retry_manager.py`) tracks:
- **Max retries**: 3 attempts per feature
- **Skip tracking**: After max retries, feature marked as "skipped"
- **Progress**: Never re-attempt completed features

This prevents infinite retry loops on impossible tasks.

### E2E Debugging Enforcement (v3.2.2+)

**Mandatory quality gate**: If E2E tests fail, agent MUST debug and fix, cannot skip to code verification.

**Forbidden workarounds**:
- Skipping E2E test execution
- Marking features complete without proof
- Trust-based verification without test output

See `validators/e2e_verifier.py` and `prompts/coding_prompt.md`.

### Hook Architecture

Hooks intercept tool calls before execution. Pattern:

```python
def my_hook(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """
    Returns:
        (allowed, message) - allowed=False blocks execution
    """
    if dangerous_operation(tool_input):
        return False, "Operation blocked: reason"
    return True, ""
```

Register hooks in `client.py` via `ClaudeCodeOptions(preToolUse=[...])`.

## Testing Philosophy

**Pragmatic coverage**:
- **High priority**: Critical paths, security hooks, edge cases
- **Lower priority**: Prompt templates, simple utilities

**Test patterns** (from `tests/test_security.py`):
```python
def test_feature():
    """Test description."""
    # Arrange
    input_data = {...}
    expected = ...

    # Act
    result = asyncio.run(async_function(input_data))

    # Assert
    assert result == expected
```

Use `@pytest.mark.asyncio` for async code. Mock external dependencies (Claude SDK calls).

## Common Modifications

### Adding Security Commands

Edit `security.py` → add to `ALLOWED_COMMANDS` set:
```python
ALLOWED_COMMANDS = {
    # ... existing commands ...
    "your_new_command",  # Description
}
```

### Adding Skills

Create skill directory in `harness_data/.claude/skills/my-skill/`:
```
my-skill/
├── SKILL.md          # Main skill file with YAML frontmatter
├── patterns.md       # Optional: code patterns
└── examples/         # Optional: example code
```

Update `skills_manager.py` → add to mode-specific skills list.

### Adding Validators

Create hook in `validators/my_validator.py`:
```python
def my_validation_hook(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    if should_block(tool_input):
        return False, "Blocked: reason"
    return True, ""
```

Register in `client.py`:
```python
from validators.my_validator import my_validation_hook

options = ClaudeCodeOptions(
    preToolUse=[
        my_validation_hook,
        # ... other hooks
    ]
)
```

### Modifying Prompts

Prompts in `prompts/` are templates with placeholders. Key prompts:
- `initializer_prompt.md` - First session (generates feature_list.json)
- `coding_prompt.md` - Continuation sessions (implements features)
- `enhancement_*.md` - Enhancement mode variants
- `*_gate.md` - Quality gates injected into prompts

Change feature count: Edit `initializer_prompt.md`, modify "200 features" requirement.

## Release Process (Maintainers)

1. Update `VERSION` file
2. Update `pyproject.toml` version
3. Update fallback `__version__` in `autonomous_agent.py` and `agent.py`
4. Update `CHANGELOG.md` (move Unreleased → versioned section)
5. Commit: `chore: bump version to X.Y.Z`
6. Create GitHub release with tag `vX.Y.Z`
7. PyPI publishes automatically via `.github/workflows/publish-to-pypi.yml`

## Important Conventions

**Commit messages**: Use Conventional Commits format (feat:, fix:, docs:, refactor:, test:, chore:)

**Branch naming**: `feature/*`, `fix/*`, `docs/*`, `refactor/*`, `test/*`

**Type hints**: Use for function signatures where reasonable. Import from `typing` module.

**Line length**: 100 characters max (enforced by ruff)

**String quotes**: Double quotes (enforced by ruff format)

## Troubleshooting

**"Authentication required"**: Set either `CLAUDE_CODE_OAUTH_TOKEN` (run `claude setup-token`) or `ANTHROPIC_API_KEY` (from https://console.anthropic.com/)

**"Command blocked"**: Check `security.py` → add to `ALLOWED_COMMANDS` if legitimate

**"Session appears stuck"**: Normal during initialization (writing 200 features). Watch for `[Tool: ...]` output.

**LSP not working**: Ensure Claude Code CLI v1.0.33+, check language server installed correctly

**Skills not loading**: Verify `SKILL.md` exists with valid YAML frontmatter, check `skills_manager.py` logs

## Additional Resources

- [User Guide](docs/USER_GUIDE.md) - Full feature documentation
- [Contributing](CONTRIBUTING.md) - Development workflow, PR guidelines
- [Anthropic Blog](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) - Harness design philosophy
- [Claude Code SDK](https://github.com/anthropics/claude-code-sdk) - SDK documentation
