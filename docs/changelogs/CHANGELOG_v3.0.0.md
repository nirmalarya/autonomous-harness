# autonomous-harness v3.0.0 Release Notes

**Release Date:** December 29, 2024
**From:** v2.3.0 (AutoGraph-proven, 658 features)
**To:** v3.0.0 (Production-hardened with cursor-harness improvements)

---

## 🎯 Overview

autonomous-harness v3.0 brings production-proven enhancements from **cursor-harness-v3** back to the canonical **Claude Agent SDK** version. This release stays **100% SDK-native** while adding critical security, validation, and automation features.

**Key Philosophy:** Port proven improvements from cursor-harness while maintaining SDK purity (no CLI workarounds).

---

## ✨ Major Features

### 1. **Dynamic MCP Auto-Configuration** ✅

**What Changed:**
- **Before (v2.3):** Hardcoded Puppeteer MCP only
- **After (v3.0):** Auto-configured MCP servers based on execution mode

**New `setup_mcp.py` module:**
- **Documentation MCP** (all modes):
  - Ref Tools (premium, token-efficient) if `REF_TOOLS_API_KEY` set
  - Context7 (free fallback) otherwise
- **Browser Automation** (greenfield/enhancement):
  - Puppeteer MCP (proven to work excellently with SDK!)
- **Azure DevOps** (backlog mode):
  - Automatic PBI fetching and state management

**Benefits:**
- Zero manual MCP configuration
- Mode-specific tool availability
- Query latest framework docs on-demand

---

### 2. **SDK Hooks for Production Security** ✅

**What Changed:**
- **Before (v2.3):** Relied on agent following prompt instructions
- **After (v3.0):** SDK hooks **enforce** quality gates

**PreToolUse Hooks (run before tool execution):**
1. **`bash_security_hook`** (existing) - Command allowlist
2. **`secrets_scan_hook`** (NEW) - Blocks git commits with secrets
   - Detects API keys, passwords, tokens, private keys
   - Scans `.py`, `.js`, `.ts`, `.env`, `.yml`, `.json` files
   - Prevents AutoGraph-style `.env.bak` leaks

**PostToolUse Hooks (run after tool execution):**
1. **`e2e_validation_hook`** (NEW) - Requires E2E tests for UI features
   - Validates screenshots exist in `.claude/verification/`
   - Validates `test_results.json` format
   - Blocks commits if E2E tests missing for user-facing features
   - Smart detection: UI features require tests, backend features don't

**Benefits:**
- Secrets CANNOT be committed (hook blocks it)
- E2E tests CANNOT be skipped (hook enforces them)
- Agent receives clear error feedback to fix issues

---

### 3. **Infrastructure Self-Healing** ✅

**What Changed:**
- **Before (v2.3):** Manual infrastructure setup
- **After (v3.0):** Auto-healing on brownfield projects

**New `infra/healer.py` module:**
- Auto-starts Docker services (postgres, redis, minio)
- Runs database migrations (`alembic upgrade head`)
- Creates MinIO buckets if missing
- Verifies service health before sessions

**Activation:**
- Runs automatically for **enhancement** and **bugfix** modes
- Skipped for greenfield (no existing infrastructure)

**Benefits:**
- Zero manual Docker/DB setup
- Continue work immediately on existing projects
- No more "connection refused" errors

---

### 4. **Prompt MCP Tool Injection** ✅

**What Changed:**
- **Before (v2.3):** Static tool documentation in prompts
- **After (v3.0):** Dynamic MCP tool injection based on mode

**Enhanced `prompts.py`:**
- `inject_mcp_tools()` - Replaces `{{PLACEHOLDERS}}` with actual tools
- Mode-aware injection (Context7 vs Ref, Puppeteer, Azure DevOps)

**Updated Prompts:**
- `initializer_prompt.md` - Added MCP tools section
- `coding_prompt.md` - Added E2E testing requirements
- `enhancement_*.md` - MCP tools documentation

**Benefits:**
- Agent sees exact MCP tools available
- Clear E2E testing instructions
- Documentation lookup guidance

---

## 📦 New Files & Directories

```
autonomous-harness/
├── setup_mcp.py                     # NEW: Auto-configure MCP servers
├── validators/                      # NEW: Validation logic
│   ├── __init__.py
│   ├── secrets_scanner.py          # Secrets detection patterns
│   ├── e2e_verifier.py             # E2E test verification
│   ├── test_runner.py              # Test execution logic
│   ├── secrets_hook.py             # PreToolUse hook (blocks secrets)
│   └── e2e_hook.py                 # PostToolUse hook (enforces E2E)
├── infra/                           # NEW: Infrastructure automation
│   ├── __init__.py
│   └── healer.py                   # Auto-heal Docker/DB/MinIO
└── prompts/
    ├── initializer_prompt.md        # Updated: MCP tools section
    └── coding_prompt.md             # Updated: E2E requirements
```

---

## 🔧 Modified Files

### **client.py**
- **Added:** `mode` parameter to `create_client()`
- **Added:** Dynamic MCP server configuration via `MCPServerSetup`
- **Added:** `secrets_scan_hook` and `e2e_validation_hook` registration
- **Updated:** Security settings printout to show active MCP servers

### **agent.py**
- **Updated:** Passes `mode` to `create_client()` for mode-specific MCP configuration

### **prompts.py**
- **Added:** `inject_mcp_tools()` function for dynamic tool documentation
- **Updated:** `load_prompt()` to inject MCP tools before returning
- **Updated:** `get_initializer_prompt()` and `get_coding_prompt()` to pass mode

---

## 📊 Feature Comparison: v2.3 vs v3.0

| Feature | v2.3.0 (Before) | v3.0.0 (After) |
|---------|-----------------|----------------|
| **MCP Servers** | Hardcoded Puppeteer only | Auto-configured (Context7/Ref/Puppeteer/Azure DevOps) |
| **Secrets Protection** | ❌ None (prompt-only) | ✅ SDK PreToolUse hook blocks commits |
| **E2E Testing** | ❌ Optional (prompt-only) | ✅ SDK PostToolUse hook enforces tests |
| **Documentation Lookup** | ❌ Agent's training data | ✅ Query latest docs via MCP |
| **Infrastructure** | ❌ Manual setup | ✅ Auto-healing (Docker, migrations, MinIO) |
| **Browser Tools** | ✅ Puppeteer (proven!) | ✅ Puppeteer (kept - works great!) |
| **Mode Support** | greenfield, enhancement, bugfix | greenfield, enhancement, bugfix, **backlog** (new) |

---

## 🚀 Upgrade Guide

### **Breaking Changes**
None! v3.0 is backward compatible with v2.3 projects.

### **New Environment Variables (Optional)**

```bash
# Premium documentation MCP (optional, more token-efficient)
export REF_TOOLS_API_KEY='your-ref-api-key'

# Azure DevOps backlog mode (optional, only for backlog mode)
export ADO_ORG='your-org'
export ADO_PROJECT='your-project'
```

### **Migration Steps**

No migration needed! Existing v2.3 projects will work as-is.

**To enable new features:**
1. No code changes required
2. v3.0 automatically configures MCP servers based on mode
3. Secrets scanning and E2E validation activate automatically

---

## 🧪 Testing v3.0

```bash
cd /Users/nirmalarya/Workspace/autonomous-harness

# Set OAuth token
export CLAUDE_CODE_OAUTH_TOKEN='your-token'

# Optional: Premium docs
export REF_TOOLS_API_KEY='your-key'

# Test greenfield mode
python autonomous_agent.py --mode greenfield --project-dir ./test-project

# Test enhancement mode (with infrastructure healing)
python autonomous_agent.py --mode enhancement --project-dir ./existing-project
```

**What to Verify:**
- ✅ MCP servers auto-configure (check console output)
- ✅ Secrets hook blocks commits with API keys
- ✅ E2E hook requires tests for UI features
- ✅ Infrastructure healing runs for enhancement mode
- ✅ Documentation lookup tools available

---

## 🎓 What We Learned from cursor-harness

**Proven Enhancements (Ported to v3.0):**
- ✅ MCP auto-configuration (reduces setup friction)
- ✅ Secrets scanning (critical security)
- ✅ E2E validation enforcement (ensures quality)
- ✅ Infrastructure self-healing (brownfield reliability)

**Kept Puppeteer (Not Playwright):**
- Puppeteer MCP proven to work excellently with Claude Agent SDK
- No reason to switch - stability over novelty

**What We Didn't Port:**
- ❌ Loop detection - SDK handles with `max_turns=1000`
- ❌ Custom session management - SDK provides `resume=session_id`
- ❌ Manual OAuth handling - SDK uses `CLAUDE_CODE_OAUTH_TOKEN`

**Philosophy:** Use SDK features when available, extend only when needed.

---

## 📚 References

- **UPGRADE_TO_V3.0_PLAN.md** - Detailed implementation plan
- **cursor-harness repo** - `/Users/nirmalarya/Workspace/cursor-harness-v3`
- **Claude Agent SDK Docs** - https://platform.claude.com/docs/en/api/agent-sdk/overview
- **Context7 MCP** - https://github.com/upstash/context7
- **Ref MCP** - https://github.com/ref-tools/ref-tools-mcp
- **Puppeteer MCP** - https://github.com/puppeteer/puppeteer-mcp-server

---

## 🙏 Acknowledgments

- **Anthropic** for Claude Agent SDK and autonomous coding patterns
- **cursor-harness** for proving these patterns in production
- **AutoGraph** for validating the approach (658 features completed)

---

## 🐛 Known Issues

None at release. Please report issues to the repository.

---

## 🔮 Future Roadmap

**Planned for v3.1:**
- [ ] Azure DevOps backlog mode full implementation
- [ ] Enhanced test runner with parallel execution
- [ ] More MCP servers (GitHub, Linear, Jira)

**Long-term:**
- [ ] Multi-agent orchestration (architect + coder + tester)
- [ ] Automatic regression testing across sessions
- [ ] Cost tracking and optimization

---

**autonomous-harness v3.0.0 is production-ready!** 🚀

Built with ❤️ using Claude Agent SDK
