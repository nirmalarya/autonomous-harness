# Changelog

All notable changes to autonomous-harness will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [Unreleased] - v2.0 Roadmap

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

