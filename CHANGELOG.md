# Changelog

All notable changes to autonomous-harness will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.3] - 2026-01-11

### Added
- **Auto-Install LSP Plugins**: Automatically installs LSP plugins from marketplace based on detected tech stack
- **Spec File Analysis**: Detects languages from spec file keywords for greenfield projects
- **Smart Status Output**: Shows which plugins were installed/skipped/failed with clear messages

**Full details:** [CHANGELOG_v3.3.3.md](CHANGELOG_v3.3.3.md)

---

## [3.3.2] - 2026-01-11

### Fixed
- **Dynamic Version Display**: Banner now reads version from VERSION file instead of hardcoded string, ensuring consistent version display across `--version` flag and banner

**Full details:** [CHANGELOG_v3.3.2.md](CHANGELOG_v3.3.2.md)

---

## [3.3.1] - 2026-01-11

### Fixed
- **CLI UX Improvement**: Running `claude-harness` without required `--spec` parameter now shows helpful error message instead of cryptic FileNotFoundError
- **Better Help Text**: Updated `--help` output to clearly mark `--spec` as REQUIRED and show practical examples
- **Early Validation**: Added parameter validation before agent initialization for faster feedback

**Full details:** [CHANGELOG_v3.3.1.md](CHANGELOG_v3.3.1.md)

---

## [1.0.0] - 2024-12-24

### 🎉 Initial Release - SHERPA v1.0 Success

First production-ready release of autonomous-harness (formerly autonomous-coding).
Successfully built SHERPA v1.0 - a complete production-ready application!

### Features

#### Core Harness
- Two-agent pattern (Initializer + Coding agents)
- Feature-driven development (feature_list.json)
- Session management with fresh context windows
- Auto-continue between sessions (3s delay)
- Git integration with automatic commits
- Progress tracking via claude-progress.txt
- Comprehensive security model (sandbox + allowlist)

#### Security
- OS-level bash command isolation
- Filesystem restricted to project directory
- Bash allowlist (safe commands only)
- Puppeteer MCP for browser automation
- Multi-layered defense-in-depth

#### Project Management
- feature_list.json with pass/fail tracking
- Detailed test steps per feature
- Session summaries
- Git commits per feature
- Progress notes

#### Prompts
- initializer_prompt.md - Project setup & feature generation
- coding_prompt.md - Feature implementation
- app_spec.txt - Project specification format (XML-style)

### Success Metrics - SHERPA v1.0 Build

**Built:** SHERPA - Autonomous Coding Orchestrator
- **Features:** 165/165 (100% complete)
- **Sessions:** 143 (plus polish sessions)
- **Code Quality:** A- grade (9.2/10)
- **Lines of Code:** 10,836 Python + 32 React components
- **Git Commits:** 328
- **Time:** ~15-20 hours autonomous
- **Result:** Production-ready application

**SHERPA Components:**
- FastAPI backend (35 Python files)
- React + Vite frontend (32 components)
- SQLite database (7 tables with migrations)
- AWS Bedrock KB integration
- Azure DevOps adapter
- Beautiful CLI (Click + Rich)
- Real-time SSE updates
- Dark mode UI

**Validation:**
- ✅ Application functional and running
- ✅ All 165 features passing
- ✅ Backend: http://localhost:8001
- ✅ Frontend: http://localhost:3003
- ✅ Zero critical bugs
- ✅ Professional code quality

### Technical Stack

- **Python:** 3.11+ with Claude Code SDK
- **Framework:** Based on Anthropic's autonomous-coding pattern
- **MCP Servers:** Puppeteer (browser automation)
- **Security:** Multi-layer sandbox
- **Testing:** Comprehensive feature validation

### Known Limitations

- No brownfield/enhancement mode (planned for v2.0)
- No explicit stop condition (agent continues after 100%)
- No TODO prevention in prompts
- File-based tracking only (Linear/Azure DevOps planned for v2.0)

### Repository

- **Previous name:** autonomous-coding
- **New name:** autonomous-harness
- **Remote:** git@github.com:nirmalarya/claude-quickstarts.git
- **Branch:** main

---

## [2.0.0-beta] - 2024-12-25

### 🎉 Major Release - Quality Gates & Enhancement Mode

Based on learnings from SHERPA v1.0 and AutoGraph v3.0 builds.

### Added

#### Quality Gates (8 Critical Improvements)
- **Stop Condition**: Agent exits at 100% completion (prevents scope creep)
- **Service Health Check**: Waits for all services healthy before testing
- **Database Schema Validation**: Verifies columns exist before marking passing
- **Browser Integration Testing**: Tests CORS in real browser, not just curl
- **E2E Testing**: Mandatory Puppeteer tests for UI features
- **Zero TODOs Policy**: No incomplete implementations allowed
- **Security Checklist**: Mandatory for auth/sensitive features
- **Regression Testing**: Tests random 10% every 5 sessions

#### Multiple Modes
- **Greenfield Mode**: Build new projects (existing)
- **Enhancement Mode**: Add features to existing projects (NEW!)
- **Bugfix Mode**: Fix issues systematically (NEW!)

#### File Organization
- **Auto-create structure**: Proper directories from Session 1
- **Auto-organize files**: Moves misplaced files automatically
- **Enforce clean root**: < 20 files in root directory
- **Comprehensive .gitignore**: Never commit logs, sessions, secrets

#### Testing Framework
- `regression_tester.py`: Automated regression testing
- Test templates for E2E (Puppeteer)
- Database validation helper
- Service health checker

#### New Prompts
- `enhancement_initializer_prompt.md`: Scan existing, append features
- `enhancement_coding_prompt.md`: Preserve functionality while enhancing
- `bugfix_mode_prompt.md`: Test-driven bug fixing
- `quality_gates.md`: Detailed gate specifications
- `project_structure.md`: Structure requirements

### What This Prevents

Issues found in v1.0 builds (SHERPA, AutoGraph):
- ❌ Scope creep after 100% → ✅ Stop condition prevents
- ❌ 150+ files in root → ✅ Auto-organization prevents
- ❌ Missing database columns → ✅ Schema validation catches
- ❌ CORS issues → ✅ Browser testing catches
- ❌ CRUD broken in browser → ✅ E2E testing catches
- ❌ Old features breaking → ✅ Regression testing catches
- ❌ Incomplete TODOs → ✅ Zero policy enforces
- ❌ Security vulnerabilities → ✅ Checklist catches

### Testing

- Tested on: (Will test on AutoGraph v3.1, SHERPA v1.1)
- Quality improvement: v1.0 apps (B+/A-) → v2.0 apps (A/A+ expected)

---

## [2.1.0-beta] - 2024-12-25

### 🎯 Major Release - Generic E2E & Regression Testing

**Tested on:** AutoGraph v3.0 → v3.1 (revealed critical gaps!)

### Added

#### Generic Testing Framework
- **Generic E2E Requirements** (`generic_e2e_requirements.md`)
  - Project-type detection (web/API/CLI/desktop)
  - Adaptive testing strategies
  - Complete user workflow testing
  - Data persistence verification
  - Works for ANY project type!

- **Generic Regression Requirements** (`generic_regression_requirements.md`)
  - Baseline creation (enhancement mode)
  - Sampling strategy (10% of features)
  - Quick regression checks
  - Framework-agnostic

#### Enhanced Quality Gates
- Updated E2E gate to be truly generic
- Emphasizes "test complete workflows, not isolated APIs"
- Requires data persistence verification
- Adapts to project type automatically

#### Bug Fixes
- Fixed stop condition in `enhancement_coding_prompt.md`
- Fixed stop condition in `bugfix_mode_prompt.md`
- Fixed `progress.py` to check `spec/feature_list.json`
- Enhanced security allowlist (python3, docker, curl, jq, etc.)

### Critical Learnings from AutoGraph Test

**What We Discovered:**
- ❌ Agent created tests but never RAN them
- ❌ Agent marked features passing without real verification
- ❌ Tests passed in isolation but failed in browser
- ❌ Infrastructure assumptions (MinIO buckets) not validated
- ✅ Agent's CODE changes were good
- ✅ But VERIFICATION was insufficient

**What v2.1 Fixes:**
- ✅ Generic testing (not AutoGraph-specific!)
- ✅ Emphasizes "actually run the tests"
- ✅ Requires complete workflow testing
- ✅ Mandates persistence verification
- ✅ Tests in actual interface (browser/CLI/etc.)

### What's Still Needed for v2.2

- Infrastructure validation gate
- "Actually execute tests" enforcement
- Smoke test after marking complete
- Deployment verification

---

## [Unreleased] - v2.2+ Roadmap

### Planned Enhancements

#### Brownfield/Enhancement Mode
- enhancement_initializer_prompt.md
- enhancement_coding_prompt.md
- Append to feature_list.json (not replace)
- Regression testing mandatory
- Smart codebase scanning

#### Progress Trackers
- Linear integration (for personal projects)
- Azure DevOps integration (for company work)
- Keep file-based as default/fallback

#### Quality Gates
- Explicit stop condition when all features pass
- Zero TODOs policy (prevent incomplete features)
- Mandatory regression testing for enhancements
- Code quality checks

#### Documentation
- Usage guide
- Enhancement mode guide
- Tracker comparison guide
- Best practices

### Timeline

v2.0 expected: January 2025 (after AutoGraph v3 completes)

---

## Credits

- Based on: Anthropic's autonomous-coding pattern
- Inspired by: Cole's Linear harness (Linear integration idea)
- Built by: Claude Code SDK (Sonnet 4.5)
- First success: SHERPA v1.0 (production-ready!)

