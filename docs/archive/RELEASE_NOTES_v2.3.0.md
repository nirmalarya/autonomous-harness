# autonomous-harness v2.3.0 - Stable Release

**Released:** December 27, 2025

## Overview

Stable, production-tested autonomous coding harness using Claude Agent SDK.

## Proven Track Record

✅ **AutoGraph Project:** 658/658 features implemented
- Full microservices architecture
- Frontend + 9 backend services
- Docker orchestration
- Complete feature implementation

## Core Capabilities

### 1. Greenfield Mode
- Creates new projects from scratch
- Follows feature_list.json pattern
- Iterative development with progress tracking

### 2. Enhancement Mode
- Adds features to existing projects
- Maintains code quality
- Respects existing architecture

### 3. Bugfix Mode
- Identifies and fixes bugs
- Regression testing
- Safe code modifications

## Architecture

- **Agent:** Claude 3.5 Sonnet via Agent SDK
- **Tools:** Read, Write, Edit, Bash
- **Pattern:** Initializer + Coder sessions
- **State:** feature_list.json progress tracking

## Known Limitations

❌ No E2E browser testing (missed CSS errors)
❌ No secrets scanning (exposed keys)
❌ Assumes tests = working app

## Usage

```bash
python agent.py greenfield ./my-app --spec app_spec.txt
python agent.py enhancement ./existing-app
python agent.py bugfix ./existing-app
```

## Key Files

- `agent.py` - Main autonomous loop
- `client.py` - Claude SDK integration
- `prompts/` - Initializer and coder prompts
- `security.py` - Command allowlist
- `progress.py` - Progress tracking

## Why This Release?

**Checkpoint before v3.0 rewrite:**
- v2.3.0 is STABLE and PROVEN
- v3.0 will be fresh implementation
- This tag preserves working code

## Recommendation

**Use for:** Production greenfield projects
**Avoid for:** Projects requiring E2E validation

---

**This version WORKS. Keep it!** ✅
