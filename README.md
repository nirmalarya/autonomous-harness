# claude-harness

Production-ready autonomous coding harness using Claude Code SDK. Build complete applications autonomously with a two-agent pattern (initializer + coding agents).

## Key Features

🎯 **Autonomous Development**
- Two-agent pattern (Initializer + Coding agents)
- Auto-continues between sessions with fresh context windows
- Progress persisted via feature_list.json and git commits

🔄 **Iteration Philosophy (v3.7.0 + v4.0.0)**
- **v4.0.0**: Ralph Wiggum plugin integration with auto-installation
- **v3.7.0**: Completion promises enforce genuine task completion
- **Structured retry loops** - E2E debugging (10 iterations), feature quality (8 gates)
- **Self-healing infrastructure** - Auto-restarts backend, fixes DB connections
- **Iteration metrics tracking** - Analyze which features require most iteration
- **"Iteration > Perfection"** - Keep trying until quality gates pass

🔒 **Production-Ready Quality**
- **v3.6.0**: Browser automation enforced for fullstack apps (Puppeteer MCP)
- **v3.2.2**: Mandatory E2E debugging - no workarounds allowed
- **v3.2.1**: E2E test execution enforced with proof required
- Triple timeout protection (15/10/120 min)
- Retry + skip logic (3 attempts per feature)
- Loop detection prevents infinite hangs

🧠 **Code Intelligence (v3.2.0)**
- Skills System with 5 built-in skills
- LSP integration for code navigation
- Auto-discovers patterns from existing code
- Mode-specific domain knowledge (greenfield/enhancement/bugfix)

🛡️ **Security First**
- Bash command allowlist
- Filesystem restrictions (project dir only)
- Secrets scanning
- Browser cleanup hooks
- MCP auto-configuration (Context7, Puppeteer)

## Installation

### 1. Install claude-harness

```bash
# Install from PyPI (recommended)
pip install claude-harness

# Or install from GitHub
pip install git+https://github.com/nirmalarya/claude-harness.git

# Or install from source (development)
git clone https://github.com/nirmalarya/claude-harness.git
cd claude-harness
pip install -e .
```

This automatically installs all Python dependencies including `claude-code-sdk`.

**v4.0.0 Note:** Starting with v4.0.0, the harness will auto-install Claude Code CLI and Ralph Wiggum plugin on first run. Node.js v18+ is required (harness will provide installation instructions if missing).

### 2. Authentication Setup

Choose one of the following authentication methods:

#### Option A: OAuth Token (Recommended)

Install Claude Code CLI to generate your OAuth token:

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Generate OAuth token (opens browser for authentication)
claude setup-token

# Set the token
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'
```

#### Option B: API Key

Get your API key from the Anthropic Console:

```bash
# Get API key from: https://console.anthropic.com/
# Then set it
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Note:** Both authentication methods work. OAuth tokens are generated through the Claude Code CLI and provide full CLI integration. API keys are obtained from the Anthropic Console and work directly with the SDK.

### 3. Verify Installation

```bash
claude-harness --version
```

## Contributing

We welcome contributions from the community! Whether it's bug fixes, new features, or documentation improvements - all contributions are appreciated.

### Quick Links

- [Contributing Guide](CONTRIBUTING.md) - Full contribution guidelines
- [Development Setup](docs/DEVELOPMENT.md) - Detailed setup instructions
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community standards
- [Issue Tracker](https://github.com/nirmalarya/claude-harness/issues) - Report bugs or request features

### Quick Start for Contributors

1. **Fork and clone** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and add tests
4. **Run tests and linting**: `pytest tests/test_*.py -v && ruff check .`
5. **Commit** with conventional format: `feat: add feature description`
6. **Push and create PR** with a clear description

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete details.

### Development Setup

```bash
# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio ruff mypy types-pyyaml

# Run tests
pytest tests/test_*.py -v

# Run linting
ruff check .
```

## Quick Start

```bash
# 1. Install
pip install claude-harness

# 2. Set up authentication (choose one)
# Option A: OAuth Token
npm install -g @anthropic-ai/claude-code && claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'
# Option B: API Key
export ANTHROPIC_API_KEY='your-api-key-here'

# 3. Create a spec file
echo "Build a todo list web app with React" > app_spec.txt

# 4. Run the harness
claude-harness --project-dir ./my_project --spec app_spec.txt

# Or test with limited iterations
claude-harness --project-dir ./my_project --spec app_spec.txt --max-iterations 3
```

**Other modes:**

```bash
# Enhancement mode (add features to existing project)
claude-harness --mode enhancement --project-dir ./existing-app --spec features.txt

# Backlog mode with Linear (NEW in v3.3.0)
export LINEAR_API_KEY='lin_api_...'
claude-harness --mode backlog --project-dir ./my_project
```

📖 **[Read the full User Guide →](docs/USER_GUIDE.md)**

## Backlog Mode Integrations (NEW in v3.3.0)

claude-harness now supports automated issue tracking with Linear or Azure DevOps in backlog mode. The agent fetches issues, implements features, and updates status automatically.

### Linear Integration

**Setup:**
```bash
# 1. Get API key from https://linear.app/settings/api
export LINEAR_API_KEY='lin_api_...'

# 2. Create project marker file in your project
cat > .linear_project.json <<EOF
{
  "team_id": "your_team_id",
  "project_id": "your_project_id",
  "project_name": "My Project"
}
EOF

# 3. Run in backlog mode
claude-harness --mode backlog --project-dir ./my_project
```

**Workflow:**
1. Agent fetches issues from Linear project
2. Picks next "Todo" issue
3. Updates to "In Progress"
4. Implements feature with E2E tests
5. Updates to "Done"
6. Adds implementation comment to issue
7. Tracks progress via META issue

**Features:**
- 20 Linear tools for issue management
- Auto-syncs status (Todo → In Progress → Done)
- Implementation comments with file changes and test results
- META issue tracking for session progress
- State persistence in `.cursor/linear-backlog-state.json`

**Finding Team/Project IDs:**
```bash
# Method 1: From Linear URL
# https://linear.app/workspace/team/ENG/project/my-project
#                                  ^^^         ^^^^^^^^^^
#                                team_key    project_key

# Method 2: Use Linear tools
# Run: linear_list_teams() to get team_id
# Run: linear_list_projects(team_id) to get project_id
```

### Azure DevOps Integration

**Setup:**
```bash
# Set environment variables
export ADO_ORG='your-organization'
export ADO_PROJECT='your-project'

# Run in backlog mode
claude-harness --mode backlog --project-dir ./my_project
```

**Note:** Both integrations can be configured simultaneously. The agent will use whichever is available based on environment variables.

## Release History

### v4.0.0 (2026-01-15) - Ralph Wiggum Plugin Integration

**Anthropic Native Iteration - SDK-Level Stop Hooks**

Making the Ralph Wiggum plugin foundational for iteration with automatic fallback to v3.7.0 bash loops:

✨ **Auto-Installation System:**
- **Preflight Dependency Checks** - Auto-verifies Node.js v18+, Claude Code CLI, and Ralph plugin
- **One-Command Setup** - Harness auto-installs Claude Code CLI and Ralph plugin if missing
- **Platform-Specific Guidance** - Detailed Node.js installation instructions for macOS, Linux, Windows
- **Zero Manual Configuration** - Dependencies handled automatically on first run

🔄 **Ralph Loop Integration:**
- **Native `/ralph-loop` Commands** - Use official Ralph plugin for E2E debugging and feature iteration
- **SDK-Level Stop Hooks** - Ralph intercepts exits, feeds prompts back until completion
- **Self-Referential Learning** - Agent reads own previous work from files/git to improve
- **Completion Promises** - `<promise>FEATURE_COMPLETE</promise>` markers signal genuine completion
- **Max Iterations Safety** - Built-in bounds prevent infinite loops (10 for E2E, 20 for features)

🔀 **Backward Compatibility:**
- **Graceful Fallback** - Automatically uses bash loops if Ralph plugin not available
- **CLI Flags** - `--force-ralph` requires Ralph, `--force-bash` forces v3.7.0 mode
- **Auto-Detection** - Checks `~/.claude/plugins/installed_plugins.json` for Ralph
- **Zero Breaking Changes** - v3.7.0 users unaffected

📖 **Documentation:** [v4.0.0 Roadmap](ROADMAP_v4.0.0.md) | [Architecture Guide](docs/ARCHITECTURE_v4.md)

**Phases Completed:** Phase 1 (auto-installation), Phase 2 (Ralph loop integration), Phase 3 (backward compatibility)

---

### v3.7.0 (2026-01-15) - Ralph Philosophy Integration

**Iteration > Perfection - Structured Retry Loops**

✅ **Completion Promises System:**
- **Explicit Success Markers** - `<promise>E2E_PASSED</promise>`, `<promise>FEATURE_COMPLETE</promise>`
- **Validation Hooks** - Blocks feature marking until completion promise output
- **Quality Gate Enforcement** - Can't skip to next feature without all 8 gates passing
- **Marker File Fallback** - `.claude/completion_promise.marker` for manual override

🔄 **E2E Debugging Iteration Loop:**
- **Structured 10-Iteration Loop** - Automatic debugging with diagnostics, fixes, and re-tests
- **Self-Healing Infrastructure** - Auto-restarts backend, fixes DB connections, kills zombies
- **No Premature Exits** - Loop continues until E2E passes or max iterations reached
- **Completion Promise Required** - Must output promise before marking feature as passing

📊 **Iteration Metrics Tracking:**
- **Per-Feature Metrics** - Track iteration count, success rate, timestamps
- **Statistics API** - `get_iteration_statistics()` for analysis
- **JSON Storage** - `.claude/iteration_metrics.json` for historical data
- **Pattern Learning** - Identify which features require most iteration

📖 **Full changelog:** [v3.7.0](CHANGELOG_v3.7.0.md)

---

### v3.6.0 - Browser Automation Enforcement

**Fullstack Apps Must Test Through UI**

✅ **Browser Automation Required:**
- **Philosophy Change** - Backend APIs are implementation details; test the UI users interact with
- **Puppeteer MCP Integration** - Navigate, click, fill forms, take screenshots
- **Verification Artifacts** - Screenshots saved to `.claude/verification/`, `test_results.json` required
- **Infrastructure Detection** - Auto-determines if E2E needed based on feature description

🚫 **Forbidden Workarounds:**
- **No API-Only Testing** - curl/requests insufficient for fullstack features
- **No JavaScript Evaluation** - Must use actual UI interactions
- **No Screenshot Faking** - Real browser automation required
- **Mandatory Debugging** - Can't skip E2E failures to code verification

---

### v3.3.0 - Backlog Mode Integrations

**Automated Issue Tracking with Linear and Azure DevOps**

✅ **Linear Integration:**
- **20 Linear Tools** - Full issue management API (fetch, update, comment, create)
- **Auto-Status Sync** - Todo → In Progress → Done workflow
- **Implementation Comments** - Auto-posts file changes and test results to issues
- **META Issue Tracking** - Session progress tracked in dedicated meta issue
- **State Persistence** - `.cursor/linear-backlog-state.json` for resume

✅ **Azure DevOps Integration:**
- **Work Item Fetch** - Pull PBIs, Features, Epics from ADO
- **Status Updates** - Auto-updates work item state as features complete
- **PR Creation** - Automatic PR creation with work item linking
- **Query Support** - Fetch by query, iteration path, or work item ID

---

### v3.2.2 - Mandatory E2E Debugging

**No More Skipping Failed Tests**

✅ **Critical Quality Fix:**
- **Mandatory E2E Debugging** - Agents can't skip to code verification when E2E tests fail
- **Debugging Scripts Provided** - Step-by-step scripts for backend timeout, DB issues, zombies
- **Forbidden Workarounds** - Explicitly blocks shortcuts that bypass real testing
- **Self-Healing** - Agent fixes infrastructure (restart backend, start DB, create test users)
- **Quality Gate** - "If E2E failed: Debugged, fixed, re-ran until passing" is MANDATORY

📖 **Full changelog:** [v3.2.2](CHANGELOG_v3.2.2.md)

---

### v3.2.1 - E2E Test Enforcement

**Proof of Passing Required**

✅ **E2E Enforcement:**
- **Mandatory E2E Execution** - All user-facing features must pass E2E tests
- **Proof Required** - Agent must show test output with exit code 0
- **No More "Trust Me" Commits** - Code verification alone is insufficient
- **Git Commit Blocked** - Hook prevents commits without E2E proof

📖 **Full changelog:** [v3.2.1](CHANGELOG_v3.2.1.md)

---

### v3.2.0 - Skills System & LSP Integration

**Code Intelligence and Domain Knowledge**

✅ **Skills System:**
- **5 Built-in Skills** - puppeteer-testing, code-quality, project-patterns, harness-patterns, lsp-navigation
- **Auto-Discovery** - Skills loaded from `.claude/skills/`, `~/.claude/skills/`, and bundled harness skills
- **Mode-Specific Loading** - Different skills for greenfield, enhancement, and bugfix modes
- **Progressive Disclosure** - SKILL.md + supporting files (patterns.md, examples/)

✅ **LSP Integration:**
- **Code Intelligence** - goToDefinition, findReferences, hover, documentSymbol, workspace search
- **Auto-Installation** - Detects tech stack, installs language servers (TypeScript, Python, etc.)
- **Context-Aware Navigation** - Agent understands existing patterns before making changes
- **LSP Marketplace Plugins** - Uses official Anthropic LSP plugins

📖 **Full changelog:** [v3.2.0](CHANGELOG_v3.2.0.md)

---

### v3.1.0 - Triple Timeout Protection

**Prevents Infinite Hangs**

✅ **Timeout System:**
- **No-Response Timeout** - 15 minutes (agent not producing output)
- **Stall Timeout** - 10 minutes (no progress detected)
- **Session Timeout** - 120 minutes (overall session limit)
- **Loop Detection** - Detects repeated file reads and stuck patterns

📖 **Full changelog:** [v3.1.0](CHANGELOG_v3.1.0.md)

---

### Earlier Versions

- **v3.0.0** - Two-agent pattern, auto-continuation, progress persistence
- **v2.x** - MCP integration, security hooks, retry logic
- **v1.x** - Initial autonomous agent implementation

📖 **Full release history:** [All Changelogs](https://github.com/nirmalarya/claude-harness/tree/main)

## Important Timing Expectations

> **Warning: This demo takes a long time to run!**

- **First session (initialization):** The agent generates a `feature_list.json` with 200 test cases. This takes several minutes and may appear to hang - this is normal. The agent is writing out all the features.

- **Subsequent sessions:** Each coding iteration can take **5-15 minutes** depending on complexity.

- **Full app:** Building all 200 features typically requires **many hours** of total runtime across multiple sessions.

**Tip:** The 200 features parameter in the prompts is designed for comprehensive coverage. If you want faster demos, you can modify `prompts/initializer_prompt.md` to reduce the feature count (e.g., 20-50 features for a quicker demo).

## How It Works

### Two-Agent Pattern

1. **Initializer Agent (Session 1):** Reads `app_spec.txt`, creates `feature_list.json` with 200 test cases, sets up project structure, and initializes git.

2. **Coding Agent (Sessions 2+):** Picks up where the previous session left off, implements features one by one, and marks them as passing in `feature_list.json`.

### Session Management

- Each session runs with a fresh context window
- Progress is persisted via `feature_list.json` and git commits
- The agent auto-continues between sessions (3 second delay)
- Press `Ctrl+C` to pause; run the same command to resume

## Security Model

This demo uses a defense-in-depth security approach (see `security.py` and `client.py`):

1. **OS-level Sandbox:** Bash commands run in an isolated environment
2. **Filesystem Restrictions:** File operations restricted to the project directory only
3. **Bash Allowlist:** Only specific commands are permitted:
   - File inspection: `ls`, `cat`, `head`, `tail`, `wc`, `grep`
   - Node.js: `npm`, `node`
   - Version control: `git`
   - Process management: `ps`, `lsof`, `sleep`, `pkill` (dev processes only)

Commands not in the allowlist are blocked by the security hook.

## Project Structure

```
claude-harness/
├── autonomous_agent.py       # Main entry point
├── agent.py                  # Agent session logic
├── client.py                 # Claude SDK client with skills integration
├── preflight.py              # Dependency checks & auto-installation (v4.0.0)
├── security.py               # Bash command allowlist and validation
├── skills_manager.py         # Skills discovery and loading (v3.2.0)
├── lsp_plugins.py            # LSP code intelligence plugins (v3.2.0)
├── progress.py               # Progress tracking utilities (v3.7.0: iteration metrics)
├── retry_manager.py          # Feature retry and skip logic
├── loop_detector.py          # Infinite loop prevention
├── error_handler.py          # Structured error logging
├── setup_mcp.py              # MCP server auto-configuration
├── prompts/
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   ├── coding_prompt.md      # Continuation session prompt (v3.7.0: iteration loops)
│   └── [other prompts]       # Enhancement, bugfix, validation modes
├── harness_data/             # Bundled package data (v3.2.0)
│   └── .claude/skills/       # Built-in skills
│       ├── puppeteer-testing/
│       ├── code-quality/
│       ├── project-patterns/
│       ├── harness-patterns/
│       └── lsp-navigation/
├── validators/               # Quality enforcement hooks
│   ├── completion_promise_validator.py  # Completion promise enforcement (v3.7.0)
│   ├── e2e_hook.py           # E2E test enforcement (v3.2.1)
│   ├── e2e_verifier.py       # E2E debugging enforcement (v3.2.2)
│   ├── secrets_hook.py       # Secrets scanning
│   └── browser_cleanup_hook.py
├── infra/
│   └── healer.py             # Infrastructure self-healing
├── docs/
│   ├── ARCHITECTURE_v4.md    # v4.0.0 architecture & terminology (v4.0.0)
│   ├── USER_GUIDE.md         # Comprehensive user documentation
│   └── DEVELOPMENT.md        # Development setup guide
├── ROADMAP_v4.0.0.md         # v4.0.0 implementation plan (v4.0.0)
├── CHANGELOG_v3.7.0.md       # v3.7.0 release notes
└── requirements.txt          # Python dependencies
```

## Generated Project Structure

After running, your project directory will contain:

```
my_project/
├── feature_list.json         # Test cases (source of truth)
├── app_spec.txt              # Copied specification
├── init.sh                   # Environment setup script
├── claude-progress.txt       # Session progress notes
├── .claude_settings.json     # Security settings
└── [application files]       # Generated application code
```

## Running the Generated Application

After the agent completes (or pauses), you can run the generated application:

```bash
cd generations/my_project

# Run the setup script created by the agent
./init.sh

# Or manually (typical for Node.js apps):
npm install
npm run dev
```

The application will typically be available at `http://localhost:3000` or similar (check the agent's output or `init.sh` for the exact URL).

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the project | `./autonomous_demo_project` |
| `--mode` | Mode: greenfield/enhancement/bugfix | `greenfield` |
| `--spec` | Specification file path | None |
| `--max-iterations` | Max agent iterations | Unlimited |
| `--model` | Claude model to use | `claude-sonnet-4-5-20250929` |
| `--session-timeout` | Session timeout (minutes) | 120 |
| `--stall-timeout` | Stall timeout (minutes) | 10 |
| `--max-retries` | Max retry attempts per feature | 3 |
| `--version` | Show version and exit | - |
| `--help` | Show help and exit | - |

📖 **[Full command reference in User Guide →](USER_GUIDE.md#command-reference)**

## Customization

### Changing the Application

Edit `prompts/app_spec.txt` to specify a different application to build.

### Adjusting Feature Count

Edit `prompts/initializer_prompt.md` and change the "200 features" requirement to a smaller number for faster demos.

### Modifying Allowed Commands

Edit `security.py` to add or remove commands from `ALLOWED_COMMANDS`.

## Troubleshooting

**"Appears to hang on first run"**
This is normal. The initializer agent is generating 200 detailed test cases, which takes significant time. Watch for `[Tool: ...]` output to confirm the agent is working.

**"Command blocked by security hook"**
The agent tried to run a command not in the allowlist. This is the security system working as intended. If needed, add the command to `ALLOWED_COMMANDS` in `security.py`.

**"OAuth token not set"**
Run `claude setup-token` to generate your token, then ensure `CLAUDE_CODE_OAUTH_TOKEN` is exported in your shell environment.

## Attribution

This project is built upon concepts from Anthropic's autonomous coding research:
- **Quickstart Template:** [claude-quickstarts/autonomous-coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- **Engineering Blog:** [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## License

MIT License - see [LICENSE](LICENSE) file for details.
