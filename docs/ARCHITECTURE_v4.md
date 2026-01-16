# Architecture: v4.0.0 - Claude Code Ecosystem Integration

## 🎯 Terminology (CRITICAL)

**CORRECT** ✅:
- **Claude Code CLI** - The main CLI tool from Anthropic
- **Ralph Wiggum Plugin** - A plugin FOR Claude Code CLI
- **Claude Code Marketplace** - Where plugins live (github.com/anthropics/claude-code/plugins)

**INCORRECT** ❌:
- ~~"Ralph CLI"~~ - This doesn't exist
- ~~"Ralph standalone tool"~~ - Ralph is a plugin, not standalone
- ~~"Install Ralph"~~ - You install Claude Code, THEN the Ralph plugin

---

## 📦 Dependency Chain

```
User's Machine
    └── Node.js v18+ (installed by user)
        └── Claude Code CLI (installed by harness via npm)
            └── Ralph Wiggum Plugin (installed by harness via claude plugin install)
                └── Used by claude-harness for iteration
```

**Installation Commands**:
```bash
# 1. User installs Node.js (manual)
brew install node  # or download from nodejs.org

# 2. Harness auto-installs Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. Harness auto-installs Ralph plugin INTO Claude Code
claude plugin install ralph-wiggum

# 4. Now harness can use /ralph-loop commands
claude-harness --project-dir ./project --spec spec.txt
```

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│  claude-harness (Python Package)                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  autonomous_agent.py                               │  │
│  │  ├─ Preflight checks                               │  │
│  │  ├─ Auto-install Claude Code CLI if missing        │  │
│  │  └─ Auto-install Ralph plugin if missing           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  client.py                                         │  │
│  │  ├─ Creates ClaudeSDKClient                        │  │
│  │  ├─ Configures hooks (completion promises)        │  │
│  │  └─ Sends prompts with /ralph-loop commands       │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ uses
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Claude Code SDK (Python Library)                        │
│  ├─ Communicates with Claude API                         │
│  ├─ Manages tool calls                                   │
│  └─ Processes hook responses                             │
└───────────────────────┬──────────────────────────────────┘
                        │ invokes
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Claude Code CLI (Node.js Application)                   │
│  Package: @anthropic-ai/claude-code                      │
│  Command: `claude`                                        │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Plugin System                                     │  │
│  │  ├─ Plugin discovery                               │  │
│  │  ├─ Plugin loading                                 │  │
│  │  └─ Command routing (/ralph-loop → Ralph plugin)  │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ hosts
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Ralph Wiggum Plugin                                     │
│  Location: ~/.claude/plugins/ralph-wiggum/               │
│  Source: github.com/anthropics/claude-code/              │
│          plugins/ralph-wiggum                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Commands                                          │  │
│  │  ├─ /ralph-loop                                    │  │
│  │  └─ /cancel-ralph                                  │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Hooks                                             │  │
│  │  ├─ Stop hook (intercepts exits)                  │  │
│  │  ├─ Completion promise detection                  │  │
│  │  └─ Max iterations enforcement                    │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 How It Works (v4.0.0)

### Step 1: User Runs Harness
```bash
claude-harness --project-dir ./myproject --spec spec.txt
```

### Step 2: Preflight Checks
```python
# In autonomous_agent.py
if not has_node():
    print("❌ Node.js v18+ required")
    print("Install: brew install node")
    exit(1)

if not has_claude_code_cli():
    print("📦 Installing Claude Code CLI...")
    subprocess.run(["npm", "install", "-g", "@anthropic-ai/claude-code"])

if not has_ralph_plugin():
    print("📦 Installing Ralph Wiggum plugin...")
    subprocess.run(["claude", "plugin", "install", "ralph-wiggum"])

print("✅ All dependencies satisfied")
```

### Step 3: Harness Sends Prompt with Ralph Commands
```python
# In client.py
prompt = """
Implement Feature #42.

When E2E test fails, use Ralph loop for debugging:

/ralph-loop "Debug E2E test.
1. Check backend health
2. Restart if needed
3. Re-run test
4. Output <promise>E2E_PASSED</promise> when passing
" --max-iterations 10 --completion-promise "E2E_PASSED"
"""

client.send_message(prompt)
```

### Step 4: Claude Executes /ralph-loop
```
Agent sees /ralph-loop command
    ↓
Claude Code CLI routes to Ralph plugin
    ↓
Ralph plugin activates stop hook
    ↓
Agent attempts task (iteration 1)
    ↓
Agent tries to exit
    ↓
Stop hook intercepts → Feeds prompt back
    ↓
Agent tries again (iteration 2)
    ↓
... (repeat until success or max iterations)
    ↓
Agent outputs <promise>E2E_PASSED</promise>
    ↓
Ralph plugin detects completion promise
    ↓
Stop hook allows exit → Loop completes
```

### Step 5: Harness Hook Validates
```python
# In validators/completion_promise_validator.py
if marking_feature_as_passing():
    if "<promise>FEATURE_COMPLETE</promise>" not in session_log:
        return DENY("Output completion promise first!")
    return ALLOW
```

---

## 🆚 v3.7.0 vs v4.0.0

| Aspect | v3.7.0 (Current) | v4.0.0 (Target) |
|--------|------------------|-----------------|
| **Philosophy** | Ralph philosophy ✅ | Ralph philosophy ✅ |
| **Implementation** | Bash loops in prompts | /ralph-loop commands |
| **Stop Hooks** | Manual (bash while loop) | Automatic (Ralph plugin) |
| **Dependencies** | Zero (pure bash) | Node.js + Claude Code + Ralph |
| **Maintenance** | We maintain loops | Anthropic maintains Ralph |
| **Commands** | `while [ $i -le 10 ]` | `/ralph-loop "..." --max-iterations 10` |
| **Host** | Any shell | Claude Code CLI |
| **Universality** | Works everywhere | Requires Node.js |

---

## 📚 Key Sources

### Official Ralph Wiggum Plugin
- **GitHub**: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- **README**: Contains usage examples and philosophy
- **Commands**: `/ralph-loop`, `/cancel-ralph`

### Claude Code CLI
- **Package**: `@anthropic-ai/claude-code`
- **GitHub**: https://github.com/anthropics/claude-code
- **Install**: `npm install -g @anthropic-ai/claude-code`

### Claude Code Marketplace
- **Location**: https://github.com/anthropics/claude-code/tree/main/plugins
- **Official Plugins**: ralph-wiggum, LSP plugins, MCP integrations

---

## 🎓 Mental Model

Think of it like browser extensions:

```
Chrome Browser (Host)
    └── uBlock Origin Extension (Plugin)
    └── React DevTools Extension (Plugin)
    └── Grammarly Extension (Plugin)

Claude Code CLI (Host)
    └── Ralph Wiggum Plugin (Iteration)
    └── LSP Plugins (Code intelligence)
    └── MCP Servers (External tools)
```

**Ralph is NOT a browser - it's an extension FOR Claude Code!**

---

## ⚠️ Common Misconceptions

### Misconception 1: "Ralph is a separate tool"
**Reality**: Ralph is a plugin that runs INSIDE Claude Code CLI

### Misconception 2: "Install Ralph directly"
**Reality**: Install Claude Code CLI first, THEN install Ralph plugin INTO it

### Misconception 3: "Ralph CLI"
**Reality**: No such thing. It's "Ralph Wiggum Plugin for Claude Code"

### Misconception 4: "Ralph has its own commands"
**Reality**: Ralph adds commands to Claude Code CLI (`/ralph-loop` becomes available)

---

## ✅ Correct References

**When talking about it**:
- "We're using the Ralph Wiggum plugin"
- "Ralph plugin for Claude Code"
- "Install Claude Code CLI and the Ralph plugin"

**When documenting**:
- "Claude Code CLI with Ralph Wiggum plugin"
- "Ralph plugin (github.com/anthropics/claude-code/plugins/ralph-wiggum)"

**When coding**:
```python
# Check if Ralph plugin is installed
subprocess.run(["claude", "plugin", "list"])  # Should show ralph-wiggum

# Install Ralph plugin
subprocess.run(["claude", "plugin", "install", "ralph-wiggum"])

# Use Ralph loop (via Claude Code)
prompt = '/ralph-loop "..." --max-iterations 10 --completion-promise "DONE"'
```

---

## 🎯 Summary

**v4.0.0 Architecture**:
```
Python (claude-harness)
    → Python (Claude Code SDK)
        → Node.js (Claude Code CLI)
            → Plugin (Ralph Wiggum)
                → Feature (iteration loops)
```

**Dependency Installation Order**:
1. User installs Node.js (manual)
2. Harness installs Claude Code CLI (automatic via npm)
3. Harness installs Ralph plugin (automatic via claude plugin install)
4. Harness uses Ralph features (automatic in prompts)

**The Correct Statement**:
> "v4.0.0 makes the **Ralph Wiggum plugin** (for Claude Code) foundational. This requires **Claude Code CLI**, which requires **Node.js**. We auto-install Claude Code and Ralph, but users must install Node.js manually."

---

**Last Updated**: 2026-01-16
**Status**: Corrected terminology - Ralph is a plugin, not a CLI
