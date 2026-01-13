# Development Guide

This guide covers setting up your development environment and working with the claude-harness codebase.

## Prerequisites

- **Python 3.10+** - Modern Python version
- **Git** - Version control
- **Claude Code CLI** - For OAuth token generation and testing
- **Node.js & npm** (optional) - For testing LSP features with TypeScript projects

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nirmalarya/claude-harness.git
cd claude-harness
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in Editable Mode

```bash
# Install package in development mode
pip install -e .
```

This creates a symbolic link to your source code, so changes are immediately reflected.

### 4. Install Development Dependencies

```bash
pip install pytest pytest-asyncio ruff mypy types-pyyaml build
```

### 5. Set Up OAuth Token

```bash
# Generate token
claude setup-token

# Set environment variable
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export CLAUDE_CODE_OAUTH_TOKEN="your-token"' >> ~/.bashrc
```

### 6. Verify Installation

```bash
claude-harness --version
```

## Project Structure

```
claude-harness/
├── autonomous_agent.py       # CLI entry point
├── agent.py                  # Session orchestration
├── client.py                 # Claude SDK client configuration
├── security.py               # Bash command allowlist
├── skills_manager.py         # Skills discovery and loading
├── lsp_plugins.py            # LSP integration
├── progress.py               # Progress tracking
├── retry_manager.py          # Feature retry logic
├── loop_detector.py          # Infinite loop detection
├── error_handler.py          # Error logging
├── setup_mcp.py              # MCP server configuration
├── prompts/                  # System prompts and specs
│   ├── initializer_prompt.md
│   ├── coding_prompt.md
│   └── [other prompts]
├── validators/               # Quality enforcement hooks
│   ├── e2e_hook.py
│   ├── e2e_verifier.py
│   ├── secrets_hook.py
│   └── browser_cleanup_hook.py
├── infra/
│   └── healer.py             # Infrastructure self-healing
├── harness_data/             # Bundled skills
│   └── .claude/skills/
├── tests/                    # Test suite
└── docs/                     # Documentation
```

## Running Tests

### Run All Tests

```bash
pytest tests/test_*.py -v
```

### Run Specific Test File

```bash
pytest tests/test_security.py -v
pytest tests/test_skills.py -v
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=term tests/test_*.py
```

### Run Single Test

```bash
pytest tests/test_security.py::test_bash_hook_allows_safe_commands -v
```

## Linting and Formatting

### Check Code Style

```bash
# Check for linting issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Format Code

```bash
# Check formatting
ruff format --check .

# Apply formatting
ruff format .
```

### Type Checking

```bash
mypy *.py --ignore-missing-imports
```

### Run All Quality Checks

```bash
# Run before committing
ruff check .
ruff format --check .
mypy *.py --ignore-missing-imports
pytest tests/test_*.py -v
```

## Testing Changes

### Test with a Sample Project

```bash
# Create test project directory
mkdir -p test_projects/my_test

# Run harness with limited iterations
claude-harness --project-dir test_projects/my_test --max-iterations 3

# Test enhancement mode
echo "Add dark mode toggle" > test_projects/feature.txt
claude-harness --mode enhancement --project-dir test_projects/existing_app --spec test_projects/feature.txt
```

### Test CLI Options

```bash
# Test version display
claude-harness --version

# Test help
claude-harness --help

# Test different models
claude-harness --project-dir ./test --model claude-sonnet-4-5-20250929 --max-iterations 1
```

## Making Changes

### Common Patterns

#### Adding a New Security Command

1. Edit `security.py`
2. Add command to `ALLOWED_COMMANDS` set
3. Add tests in `tests/test_security.py`

```python
# In security.py
ALLOWED_COMMANDS = {
    # ... existing commands ...
    "your_command",  # Description
}
```

#### Adding a New Validator Hook

1. Create file in `validators/my_hook.py`
2. Implement hook function
3. Register in `client.py`
4. Add tests

```python
# validators/my_hook.py
def my_validation_hook(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    if should_block(tool_input):
        return False, "Blocked: reason"
    return True, ""
```

#### Adding a New Skill

1. Create skill directory: `harness_data/.claude/skills/my-skill/`
2. Create `SKILL.md` with YAML frontmatter
3. Add supporting files (patterns.md, examples/, etc.)
4. Update `skills_manager.py` mode-specific skills

#### Modifying Prompts

1. Edit prompt files in `prompts/` directory
2. Test with `--max-iterations 1` to verify prompt works
3. Check for placeholder replacements

## Debugging

### Enable Verbose Logging

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run harness
claude-harness --project-dir ./test
```

### Debug Session Timeouts

Check `loop_detector.py` for timeout settings:
- No-response timeout: 15 minutes
- Stall timeout: 10 minutes
- Session timeout: 120 minutes

### Debug Progress Tracking

Progress is saved to `claude-progress.txt` in the project directory. Read this file to see what the agent has completed.

```bash
cat test_projects/my_test/claude-progress.txt
```

### Debug Feature List

The `feature_list.json` is the source of truth for feature status:

```bash
cat test_projects/my_test/feature_list.json | jq '.features[] | select(.status == "failing")'
```

### Debug Security Hooks

Security hooks log to console. Look for:
- "Command blocked by security hook"
- "Secrets detected in commit"

### Debug Skills Loading

Skills manager logs which skills are loaded. Check console output for:
- "Loading skills for mode: greenfield"
- "Loaded skill: puppeteer-testing"

## Common Development Tasks

### Update Version

1. Update `VERSION` file
2. Update `pyproject.toml` version
3. Update fallback `__version__` in `autonomous_agent.py` and `agent.py`

### Update Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Update pyproject.toml dependencies
# Edit manually based on requirements
```

### Build Package

```bash
# Build wheel and source distribution
python -m build

# Check build artifacts
ls -lh dist/

# Install locally to test
pip install dist/*.whl
```

### Test Package Installation

```bash
# Create fresh venv
python -m venv test_venv
source test_venv/bin/activate

# Install from dist
pip install dist/claude_harness-3.3.4-py3-none-any.whl

# Verify
claude-harness --version
```

## Release Checklist (Maintainers)

1. [ ] Update `VERSION` file
2. [ ] Update `pyproject.toml` version
3. [ ] Update `__version__` in `autonomous_agent.py` and `agent.py`
4. [ ] Update `CHANGELOG.md` (move Unreleased → versioned section)
5. [ ] Run all tests: `pytest tests/test_*.py -v`
6. [ ] Run linting: `ruff check . && ruff format --check .`
7. [ ] Build package: `python -m build`
8. [ ] Test installation: `pip install dist/*.whl && claude-harness --version`
9. [ ] Commit: `chore: bump version to X.Y.Z`
10. [ ] Create GitHub release with tag `vX.Y.Z`
11. [ ] GitHub Actions auto-publishes to PyPI

## Tips

- Use `--max-iterations 1-3` for quick testing
- Test both greenfield and enhancement modes
- Check `claude-progress.txt` for agent decisions
- Review git history in generated projects
- Use `ps aux | grep node` to check for zombie processes
- Monitor `feature_list.json` for progress tracking

## Getting Help

- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Review [README.md](../README.md) for usage examples
- Open an issue on GitHub for questions
- Review closed PRs for similar changes

## Useful Commands Reference

```bash
# Development
pip install -e .
pytest tests/test_*.py -v
ruff check . && ruff format --check .
mypy *.py --ignore-missing-imports

# Testing
claude-harness --project-dir ./test --max-iterations 3
claude-harness --mode enhancement --spec features.txt --project-dir ./app

# Building
python -m build
pip install dist/*.whl
claude-harness --version

# Cleanup
rm -rf dist/ build/ *.egg-info/
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
```
