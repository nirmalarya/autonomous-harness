# Contributing to claude-harness

Thank you for your interest in contributing to claude-harness! We welcome contributions from the community, whether it's bug fixes, new features, documentation improvements, or anything else that makes the project better.

Please take a moment to review this document to make the contribution process smooth and effective for everyone involved.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior through GitHub Issues.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Claude Code CLI (for OAuth token setup)
- Node.js and npm (for TypeScript language server if testing LSP features)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-harness.git
   cd claude-harness
   ```

3. Add the upstream repository as a remote:

   ```bash
   git remote add upstream https://github.com/nirmalarya/claude-harness.git
   ```

### Development Setup

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed setup instructions.

**Quick setup:**

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio ruff mypy types-pyyaml

# Set up OAuth token (required for testing)
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'

# Verify installation
claude-harness --version
```

## Development Workflow

### Branch Naming

Create a descriptive branch name following these conventions:

- `feature/add-new-skill` - New features
- `fix/lsp-detection-bug` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/cleanup-client-code` - Code refactoring
- `test/add-security-tests` - Test additions/improvements

### Workflow Steps

1. **Create a feature branch** from `main`:

   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, focused commits

3. **Follow commit message conventions** (Conventional Commits):

   ```
   feat: add support for Rust LSP server
   fix: correct TypeScript detection in specs
   docs: update contributing guidelines
   test: add tests for skills manager
   refactor: simplify lsp_plugins module
   chore: update dependencies
   ```

4. **Run tests and linting locally**:

   ```bash
   # Run tests
   pytest test_*.py -v

   # Run linting
   ruff check .
   ruff format --check .

   # Run type checking
   mypy *.py --ignore-missing-imports
   ```

5. **Push your changes**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Pull Request Guidelines

### Before Submitting

- Ensure all tests pass locally
- Run linting and formatting checks
- Update documentation if needed
- Add tests for new features or bug fixes
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/) format

### PR Title

Use Conventional Commits format for PR titles:

- `feat: add X` - New feature
- `fix: resolve Y bug` - Bug fix
- `docs: update Z documentation` - Documentation
- `refactor: improve A` - Refactoring
- `test: add tests for B` - Tests

### PR Description

Fill out the PR template completely:

- **Description**: What changed and why
- **Related Issues**: Link to issue numbers using `Fixes #123` or `Closes #456`
- **Type of Change**: Check appropriate boxes
- **Testing**: Describe how you tested
- **Checklist**: Complete all items

### Review Process

- 1 maintainer approval is required to merge
- Address review feedback promptly
- Keep the PR scope focused (one feature/fix per PR)
- Ensure CI checks pass (all jobs must be green)

## Code Standards

### Python Version

- Target Python 3.10+ compatibility
- Use modern Python features where appropriate
- Test across multiple Python versions (3.10-3.14)

### Code Style

- Follow PEP 8 style guide (enforced by ruff)
- Use double quotes for strings (enforced by ruff format)
- Maximum line length: 100 characters
- Use type hints for function signatures where reasonable
- Write docstrings for public functions and classes

### Code Patterns

- Follow existing code patterns in the project
- Keep functions focused and testable
- Avoid deep nesting (prefer early returns)
- Use meaningful variable and function names
- Add comments for complex logic (but prefer self-documenting code)

### Type Hints

```python
from typing import Optional, List, Dict
from pathlib import Path

def process_languages(
    languages: Optional[List[str]] = None,
    project_dir: Path = Path(".")
) -> Dict[str, str]:
    """Process detected languages and return mapping.

    Args:
        languages: List of language identifiers
        project_dir: Project root directory

    Returns:
        Dictionary mapping language to server binary
    """
    ...
```

### Docstrings

```python
def auto_install_plugins(self, languages: Optional[List[str]] = None) -> Dict:
    """
    Automatically install LSP plugins for detected languages.

    Args:
        languages: Languages to install (auto-detected if None)

    Returns:
        Installation results with status per language
    """
    ...
```

## Testing Requirements

### Add Tests for Changes

- **New features**: Add unit tests covering the new functionality
- **Bug fixes**: Add tests that would have caught the bug
- **Refactoring**: Ensure existing tests still pass

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

def test_feature_name():
    """Test description in imperative mood."""
    # Arrange
    input_data = {...}
    expected = ...

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected

@pytest.mark.asyncio
async def test_async_feature():
    """Test async functionality."""
    result = await async_function()
    assert result is not None
```

### Running Tests

```bash
# Run all tests
pytest test_*.py -v

# Run specific test file
pytest test_security.py -v

# Run with coverage (optional)
pytest --cov=. --cov-report=term test_*.py
```

### Coverage

We don't enforce strict coverage percentages, but aim for:

- **High coverage**: Critical paths, security hooks, edge cases
- **Lower priority**: Prompt templates, simple utilities

## Documentation

### Update Documentation

When making changes, update:

1. **README.md**: For user-facing changes (new features, CLI options)
2. **CHANGELOG.md**: Follow Keep a Changelog format:
   - Add entry under `## [Unreleased]` section
   - Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. **Docstrings**: For API changes
4. **Examples**: Add examples for new features
5. **docs/DEVELOPMENT.md**: For development process changes

### CHANGELOG Format

```markdown
## [Unreleased]

### Added
- New LSP plugin auto-installation feature

### Fixed
- Bug in TypeScript detection from spec files

### Changed
- Improved error messages for missing dependencies
```

## Release Process

**(Maintainers Only)**

claude-harness follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. Update `VERSION` file
2. Update `pyproject.toml` version
3. Update fallback versions in `autonomous_agent.py` and `agent.py`
4. Update `CHANGELOG.md`:
   - Move `[Unreleased]` items to new version section
   - Add release date
5. Commit: `chore: bump version to X.Y.Z`
6. Create GitHub release with tag `vX.Y.Z`
7. PyPI publishes automatically via GitHub Actions

## Getting Help

### Questions and Discussions

- **Bug reports**: Use the [bug report template](https://github.com/nirmalarya/claude-harness/issues/new?template=bug_report.yml)
- **Feature requests**: Use the [feature request template](https://github.com/nirmalarya/claude-harness/issues/new?template=feature_request.yml)
- **General questions**: Open a GitHub Issue
- **Documentation issues**: Open an issue or submit a PR directly

### Response Time

We aim to respond to issues and PRs within:

- **Critical bugs**: 24-48 hours
- **Other issues/PRs**: 3-5 days
- **General questions**: 1 week

Please be patient! This is maintained by volunteers.

### Stuck?

- Check [existing issues](https://github.com/nirmalarya/claude-harness/issues)
- Review [closed PRs](https://github.com/nirmalarya/claude-harness/pulls?q=is%3Apr+is%3Aclosed) for similar changes
- Ask in your PR or issue - we're happy to help!

## Thank You!

Your contributions make claude-harness better for everyone. We appreciate your time and effort! 🙏

---

**Attribution**: claude-harness is built upon concepts from [Anthropic's autonomous coding research](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding).
