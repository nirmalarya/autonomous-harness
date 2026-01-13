# autonomous-harness v3.0 Upgrade Plan

**Date:** December 28, 2024
**From:** v2.3.0 (stable, proven with AutoGraph 658 features)
**To:** v3.0.0 (production-hardened with cursor-harness improvements)

---

## 🎯 Goals

Port proven enhancements from `cursor-harness-v3` back to `autonomous-harness` while staying **100% SDK-native** (no workarounds, use Claude Agent SDK features).

**Why:** cursor-harness was a port to cursor-agent CLI. autonomous-harness uses the official Claude Agent SDK and should be the canonical version.

---

## 📊 What We're Porting (cursor-harness → autonomous-harness)

### ✅ YES - Port These Features

| Feature | Why | Status |
|---------|-----|--------|
| **MCP Auto-Configuration** | Currently hardcoded to Puppeteer only | HIGH PRIORITY |
| **E2E Test Enforcement** | Agent creates tests but doesn't validate they pass | HIGH PRIORITY |
| **Secrets Scanning** | Critical security gap (AutoGraph exposed keys) | HIGH PRIORITY |
| **Infrastructure Self-Healing** | Brownfield mode needs Docker/migrations auto-fix | MEDIUM |
| **Test Execution Validation** | Ensure tests actually run (not just created) | MEDIUM |
| **Documentation MCP** | Query latest docs for any tech stack | HIGH PRIORITY |

### ❌ NO - Don't Port (SDK Has It)

| Feature | SDK Provides | autonomous-harness Status |
|---------|-------------|---------------------------|
| Loop Detection | `max_turns=1000` | ✅ Already configured (client.py:119) |
| Session Management | `resume=session_id` | ✅ Already using |
| OAuth Token | `CLAUDE_CODE_OAUTH_TOKEN` | ✅ Already configured (client.py:57) |
| Hooks Infrastructure | `hooks={"PreToolUse": [], ...}` | ✅ Already using (client.py:114) |
| Permissions | `permission_mode`, `allow=[]` | ✅ Already configured (client.py:70-85) |

---

## 🏗️ autonomous-harness v3.0 Architecture

```
autonomous-harness/
├── agent.py                          # Core loop (minimal changes)
├── autonomous_agent.py               # CLI (add --mode backlog)
├── client.py                         # SDK client (ENHANCED with hooks)
│
├── setup_mcp.py                      # NEW: Auto-configure MCP servers
│
├── validators/                       # NEW: SDK Hook implementations
│   ├── e2e_hook.py                  # PostToolUse: E2E validation
│   ├── e2e_verifier.py              # E2E test verification logic
│   ├── secrets_hook.py              # PreToolUse: Secrets detection
│   ├── secrets_scanner.py           # Secrets scanning logic
│   ├── test_hook.py                 # PostToolUse: Test validation
│   └── test_runner.py               # Test execution logic
│
├── infra/                            # NEW: Infrastructure
│   └── healer.py                    # Self-healing (enhancement mode)
│
├── security.py                       # Bash allowlist (keep existing)
├── progress.py                       # Progress tracking (keep existing)
├── prompts.py                        # Prompt loading (ENHANCE with MCP injection)
│
├── prompts/
│   ├── initializer_prompt.md        # ENHANCE: Add MCP docs tools
│   ├── coding_prompt.md             # ENHANCE: Add E2E requirements
│   ├── enhancement_*.md             # ENHANCE: Add MCP + E2E
│   ├── backlog_*.md                 # NEW: Azure DevOps mode
│   └── system_instructions.md       # NEW: Common instructions
│
└── requirements.txt                  # No new deps (SDK has everything!)
```

---

## 📦 Component Details

### 1. MCP Auto-Configuration (`setup_mcp.py`)

**Current State** (client.py:111-113):
```python
mcp_servers={
    "puppeteer": {"command": "npx", "args": ["puppeteer-mcp-server"]}
}
```

**Enhanced**:
```python
# autonomous_harness/setup_mcp.py

class MCPServerSetup:
    def setup(self, mode: str):
        """Auto-configure MCP servers based on mode."""
        servers = {}

        # 1. Documentation MCP (ALL modes - query tech stack docs)
        if ref_api_key := os.getenv("REF_TOOLS_API_KEY"):
            # Token-efficient (premium)
            servers["ref"] = {
                "command": "npx",
                "args": ["-y", "@ref-tools/ref-tools-mcp"],
                "env": {"REF_TOOLS_API_KEY": ref_api_key}
            }
        else:
            # Free fallback
            servers["context7"] = {
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"]
            }

        # 2. Browser automation (greenfield/enhancement)
        if mode in ["greenfield", "enhancement"]:
            servers["playwright"] = {
                "command": "npx",
                "args": ["-y", "@playwright/mcp@latest"]
            }

        # 3. Azure DevOps (backlog mode)
        if mode == "backlog":
            servers["azure-devops"] = {
                "command": "npx",
                "args": ["-y", "@microsoft/azure-devops-mcp-server"],
                "env": {
                    "AZURE_DEVOPS_ORG": os.getenv("ADO_ORG"),
                    "AZURE_DEVOPS_PROJECT": os.getenv("ADO_PROJECT")
                }
            }

        return servers
```

**Integration** (client.py):
```python
from setup_mcp import MCPServerSetup

def create_client(project_dir: Path, model: str, mode: str):
    mcp_setup = MCPServerSetup()
    mcp_servers = mcp_setup.setup(mode)  # Dynamic!

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            mcp_servers=mcp_servers,
            ...
        )
    )
```

---

### 2. E2E Test Enforcement (SDK Hooks)

**Use SDK's native hook system** - no manual validation loop needed!

```python
# autonomous_harness/validators/e2e_hook.py

from claude_agent_sdk.types import HookCallback
from .e2e_verifier import E2EVerifier

async def e2e_validation_hook(input_data, tool_use_id, context) -> dict:
    """
    PostToolUse hook - validates E2E tests after git commit.

    Runs after git commit to verify:
    1. Screenshots exist (.claude/verification/*.png)
    2. test_results.json exists
    3. overall_status == "passed"
    4. No console errors or visual issues
    """
    command = input_data.get("command", "")

    # Check if this was a git commit
    if "git commit" in command:
        project_dir = Path(context.get("cwd", "."))
        verifier = E2EVerifier(project_dir)

        # Get current feature from spec/feature_list.json
        current_feature = get_current_feature(project_dir)

        if current_feature and is_user_facing(current_feature):
            result = verifier.verify(current_feature)

            if not result.passed:
                # BLOCK - inject error, agent must fix
                return {
                    "permission": "deny",
                    "user_message": f"⛔ E2E tests FAILED: {result.reason}",
                    "agent_message": f"""
E2E testing requirement not met: {result.reason}

You MUST:
1. Run E2E tests using Playwright MCP tools:
   - playwright_navigate(url="http://localhost:3000")
   - playwright_screenshot(path=".claude/verification/step-1.png")
   - playwright_click(selector="#submit-button")

2. Save screenshots to .claude/verification/

3. Create .claude/verification/test_results.json:
{{
  "feature_index": {current_feature['index']},
  "overall_status": "passed",
  "e2e_results": [
    {{"step": "...", "status": "passed", "screenshot": "..."}}
  ],
  "console_errors": [],
  "visual_issues": []
}}

4. Fix any failures before marking feature complete

Re-run E2E tests now.
"""
                }

    return {}  # Allow if passed or not applicable
```

**Integration** (client.py):
```python
from validators.e2e_hook import e2e_validation_hook

hooks={
    "PreToolUse": [
        HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
    ],
    "PostToolUse": [
        # NEW: E2E validation after git commits
        HookMatcher(matcher="Bash", hooks=[e2e_validation_hook]),
    ],
}
```

---

### 3. Secrets Scanning (SDK Hooks)

```python
# autonomous_harness/validators/secrets_hook.py

from claude_agent_sdk.types import HookCallback
from .secrets_scanner import SecretsScanner

async def secrets_scan_hook(input_data, tool_use_id, context) -> dict:
    """
    PreToolUse hook - blocks git commits if secrets detected.
    """
    command = input_data.get("command", "")

    if "git commit" in command or "git add" in command:
        project_dir = Path(context.get("cwd", "."))
        scanner = SecretsScanner(project_dir)

        violations = scanner.scan()
        if violations:
            return {
                "permission": "deny",
                "user_message": "⛔ SECRETS DETECTED - Commit blocked",
                "agent_message": f"""
Security violation: Secrets detected in code!

Found {len(violations)} violations:
{chr(10).join(f"- {v}" for v in violations[:5])}

NEVER commit:
- API keys, passwords, tokens
- .env files or credentials
- Private keys or certificates

Use environment variables instead. Remove the secrets and try again.
"""
            }

    return {}  # Allow if no secrets
```

**Integration** (client.py):
```python
from validators.secrets_hook import secrets_scan_hook

hooks={
    "PreToolUse": [
        # Stack multiple hooks!
        HookMatcher(matcher="Bash", hooks=[
            bash_security_hook,      # Existing: command allowlist
            secrets_scan_hook,        # NEW: secrets detection
        ]),
    ],
    ...
}
```

---

### 4. Infrastructure Self-Healing

**NOT a hook** - runs during setup for enhancement/bugfix modes:

```python
# autonomous_harness/infra/healer.py
# Port directly from cursor-harness (no changes needed)

class InfrastructureHealer:
    def heal(self, project_dir: Path):
        """Auto-fix common infrastructure issues."""

        # 1. Check Docker services (postgres, redis, minio)
        # 2. Run database migrations (alembic upgrade head)
        # 3. Create MinIO buckets (if missing)
        # 4. Verify service health
```

**Integration** (agent.py):
```python
# In run_autonomous_agent() during setup
if mode in ["enhancement", "bugfix"]:
    from infra.healer import InfrastructureHealer
    healer = InfrastructureHealer()
    healer.heal(project_dir)
    print("✅ Infrastructure healed")
```

---

### 5. Prompt Enhancements

**Add MCP documentation tools** to prompts:

```markdown
# prompts/initializer_prompt.md (additions)

## DOCUMENTATION LOOKUP (MCP)

You have access to up-to-date documentation via MCP:

{{DOCUMENTATION_MCP_TOOLS}}

Use these tools to query latest framework documentation:
- Query for validation patterns (e.g., "How to lint Next.js 15?")
- Get current best practices for the tech stack
- Learn framework-specific testing approaches

**Example:**
If building a Next.js 15 app, query Context7 for:
- Latest linting configuration
- Current testing patterns
- Recommended validation tools

Then create appropriate hooks/validation in your implementation plan.
```

**Dynamic Injection** (prompts.py):
```python
def inject_mcp_tools(prompt: str, mcp_setup: MCPServerSetup) -> str:
    """Inject MCP tool names into prompt templates."""

    # Documentation tools
    doc_server = mcp_setup.get_documentation_server()
    if doc_server == "context7":
        doc_tools = """- context7_resolve_library_id(library_name)
- context7_get_library_docs(library_id, topic)"""
    elif doc_server == "ref":
        doc_tools = """- ref_search(query)
- ref_get_docs(path)"""
    else:
        doc_tools = "⚠️ No documentation MCP configured"

    prompt = prompt.replace("{{DOCUMENTATION_MCP_TOOLS}}", doc_tools)

    # Browser tools
    browser_tools = mcp_setup.get_browser_tools()
    if "playwright" in browser_tools:
        browser_doc = """- playwright_navigate(url)
- playwright_screenshot(path)
- playwright_click(selector)
- playwright_fill(selector, text)"""
    prompt = prompt.replace("{{BROWSER_MCP_TOOLS}}", browser_doc)

    return prompt
```

---

## 🔄 Implementation Checklist

### **Phase 1: MCP & Hooks** (Week 1)

- [ ] Create `setup_mcp.py`
  - [ ] Auto-configure Context7/Ref (docs)
  - [ ] Auto-configure Playwright (browser)
  - [ ] Auto-configure Azure DevOps (backlog mode)

- [ ] Create `validators/e2e_hook.py`
  - [ ] PostToolUse hook (runs after git commit)
  - [ ] Validates screenshots exist
  - [ ] Validates test_results.json format
  - [ ] Blocks commit if E2E failed

- [ ] Create `validators/secrets_hook.py`
  - [ ] PreToolUse hook (runs before git commit)
  - [ ] Scans for API keys, passwords, tokens
  - [ ] Blocks commit if secrets found

- [ ] Update `client.py`
  - [ ] Import `setup_mcp`, get dynamic servers
  - [ ] Register e2e_hook in PostToolUse
  - [ ] Register secrets_hook in PreToolUse

- [ ] Test Phase 1
  - [ ] Verify MCP servers auto-configure
  - [ ] Verify hooks block bad commits
  - [ ] Verify agent receives error feedback

### **Phase 2: Validators & Infrastructure** (Week 1)

- [ ] Port `validators/e2e_verifier.py`
  - [ ] Copy from cursor-harness (no changes)
  - [ ] Test verification logic

- [ ] Port `validators/secrets_scanner.py`
  - [ ] Copy from cursor-harness (no changes)
  - [ ] Test scanning patterns

- [ ] Port `validators/test_runner.py`
  - [ ] Copy from cursor-harness (no changes)
  - [ ] Test pytest/npm test detection

- [ ] Port `infra/healer.py`
  - [ ] Copy from cursor-harness (no changes)
  - [ ] Test Docker health checks

- [ ] Integrate healer into `agent.py`
  - [ ] Run during setup (enhancement/bugfix modes)
  - [ ] Log healing operations

- [ ] Test Phase 2
  - [ ] Verify E2E verifier logic
  - [ ] Verify secrets scanner patterns
  - [ ] Verify infrastructure healing

### **Phase 3: Prompts & MCP Integration** (Week 2)

- [ ] Update `prompts.py`
  - [ ] Add `inject_mcp_tools()` function
  - [ ] Replace {{placeholders}} with actual tools

- [ ] Update `prompts/initializer_prompt.md`
  - [ ] Add {{DOCUMENTATION_MCP_TOOLS}} section
  - [ ] Add instructions to query docs

- [ ] Update `prompts/coding_prompt.md`
  - [ ] Add {{BROWSER_MCP_TOOLS}} section
  - [ ] Add E2E testing requirements
  - [ ] Add test_results.json format

- [ ] Create `prompts/backlog_initializer.md`
  - [ ] Azure DevOps PBI fetching
  - [ ] Backlog state management

- [ ] Create `prompts/backlog_coding.md`
  - [ ] Implement PBI features
  - [ ] Update Azure DevOps state

- [ ] Test Phase 3
  - [ ] Verify agent queries documentation
  - [ ] Verify agent uses browser tools
  - [ ] Verify E2E testing happens

### **Phase 4: Testing & Release** (Week 2)

- [ ] Test greenfield mode
  - [ ] New project from scratch
  - [ ] Verify MCP auto-config
  - [ ] Verify E2E enforcement

- [ ] Test enhancement mode
  - [ ] Continue ai-trading-platform from feature #23
  - [ ] Verify infrastructure healing
  - [ ] Verify E2E validation

- [ ] Test backlog mode (if Azure DevOps available)
  - [ ] Fetch PBIs
  - [ ] Implement features
  - [ ] Update work item state

- [ ] Documentation
  - [ ] Update CHANGELOG.md
  - [ ] Create migration guide (v2.3 → v3.0)
  - [ ] Document new features

- [ ] Release v3.0.0
  - [ ] Tag release
  - [ ] Update VERSION file
  - [ ] Create release notes

---

## 📋 Key Differences: v2.3 vs v3.0

| Aspect | v2.3.0 (Current) | v3.0.0 (Planned) |
|--------|------------------|------------------|
| **MCP Servers** | Hardcoded Puppeteer | Auto-configured (Context7/Ref/Playwright/Azure DevOps) |
| **E2E Testing** | Prompts only (agent may skip) | **Enforced via SDK hooks** |
| **Secrets Scanning** | ❌ None | ✅ PreToolUse hook blocks commits |
| **Infrastructure** | Manual setup | Auto-healing (Docker, migrations, MinIO) |
| **Documentation** | Agent's training data | **Query latest docs via MCP** |
| **Validation** | Trust agent follows prompts | **SDK hooks enforce quality gates** |
| **Modes** | greenfield, enhancement, bugfix | greenfield, enhancement, **backlog** |

---

## 🎯 Success Criteria

After v3.0 upgrade, autonomous-harness will:

✅ **Auto-configure MCP** based on mode (no manual setup)
✅ **Enforce E2E tests** (agent cannot skip - SDK hooks block)
✅ **Prevent secrets** (commits blocked if API keys detected)
✅ **Self-heal infrastructure** (Docker, migrations auto-fixed)
✅ **Query latest docs** (Context7/Ref MCP for any tech stack)
✅ **Support Azure DevOps** (backlog mode for enterprise workflows)
✅ **Stay SDK-native** (no workarounds, use Claude Agent SDK properly)

---

## 📚 References

- **Claude Agent SDK Docs**: https://platform.claude.com/docs/en/api/agent-sdk/overview
- **cursor-harness repo**: /Users/nirmalarya/Workspace/cursor-harness-v3
- **autonomous-harness repo**: /Users/nirmalarya/workspace/autonomous-harness
- **Anthropic's demo**: https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding
- **Context7 MCP**: https://github.com/upstash/context7
- **Ref MCP**: https://github.com/ref-tools/ref-tools-mcp
- **Playwright MCP**: https://github.com/microsoft/playwright-mcp

---

## 🚀 Getting Started After v3.0

```bash
# 1. OAuth token (use Claude Code subscription)
export CLAUDE_CODE_OAUTH_TOKEN='your-token'

# 2. Optional: Ref API key (more token-efficient than Context7)
export REF_TOOLS_API_KEY='your-ref-key'

# 3. Run greenfield mode (MCP auto-configures)
python autonomous_agent.py --mode greenfield --project-dir ./my-app

# 4. Run enhancement mode (infra auto-heals)
python autonomous_agent.py --mode enhancement --project-dir ./existing-app

# 5. Run backlog mode (Azure DevOps integration)
export ADO_ORG='your-org'
export ADO_PROJECT='your-project'
python autonomous_agent.py --mode backlog --project-dir ./project
```

---

**Ready to build autonomous-harness v3.0!** 🚀
