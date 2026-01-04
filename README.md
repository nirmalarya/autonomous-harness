# claude-harness

Production-ready autonomous coding harness using Claude Code SDK. Build complete applications autonomously with a two-agent pattern (initializer + coding agents).

## Key Features

🎯 **Autonomous Development**
- Two-agent pattern (Initializer + Coding agents)
- Auto-continues between sessions with fresh context windows
- Progress persisted via feature_list.json and git commits

🔒 **Production-Ready Quality**
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

## Prerequisites

**Required:** Install the latest versions of both Claude Code and the Claude Agent SDK:

```bash
# Install Claude Code CLI (latest version required)
npm install -g @anthropic-ai/claude-code

# Install Python dependencies
pip install -r requirements.txt
```

Verify your installations:
```bash
claude --version  # Should be latest version
pip show claude-code-sdk  # Check SDK is installed
```

**OAuth Token:** Generate and set your Claude Code OAuth token:
```bash
# Generate the token using Claude Code CLI
claude setup-token

# Set the environment variable
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'
```

## Installation

```bash
# Install from PyPI (recommended)
pip install claude-harness

# Or install from GitHub
pip install git+https://github.com/nirmalarya/claude-harness.git

# Or install from source (development)
git clone https://github.com/nirmalarya/claude-harness.git
cd claude-harness
pip install -e .

# Verify installation
claude-harness --version
```

## Quick Start

```bash
# Set OAuth token (required)
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'

# Build a new app
claude-harness --project-dir ./my_project

# Test with limited iterations
claude-harness --project-dir ./my_project --max-iterations 3

# Enhancement mode (existing projects)
claude-harness --mode enhancement --project-dir ./existing-app --spec ./features.txt

# Backlog mode with Linear (NEW in v3.3.0)
export LINEAR_API_KEY='lin_api_...'
claude-harness --mode backlog --project-dir ./my_project
```

📖 **[Read the full User Guide →](USER_GUIDE.md)**

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

## What's New in v3.2.2

✅ **Critical Quality Fix - Mandatory E2E Debugging:**
- **E2E Test Failures Now Require Debugging** - Agents can't skip to code verification when E2E tests fail
- **Debugging Scripts Provided** - Step-by-step scripts for common issues (backend timeout, DB connection, zombie processes)
- **Forbidden Workarounds** - Explicitly blocked shortcuts that bypass real testing
- **Self-Healing** - Agent fixes infrastructure issues (restart backend, start DB, create test users)
- **Quality Gate** - "If E2E failed: Debugged, fixed, re-ran until passing" is now MANDATORY

✅ **Skills System (v3.2.0):**
- **5 Built-in Skills** - puppeteer-testing, code-quality, project-patterns, harness-patterns, lsp-navigation
- **Auto-Discovery** - Skills loaded from `.claude/skills/` and `~/.claude/skills/`
- **Mode-Specific** - Different skills for greenfield, enhancement, and bugfix modes
- **Progressive Disclosure** - SKILL.md + supporting files for rich domain knowledge

✅ **LSP Integration (v3.2.0):**
- **Code Intelligence** - goToDefinition, findReferences, hover, documentSymbol, etc.
- **Navigate Codebases** - Find usages, jump to definitions, explore call hierarchies
- **Context-Aware** - Understand existing patterns before making changes

✅ **E2E Enforcement (v3.2.1):**
- **Mandatory E2E Execution** - All user-facing features must pass E2E tests
- **Proof Required** - Agent must show test output with exit code 0
- **No More "Trust Me" Commits** - Code verification alone is insufficient

📖 **Full changelogs:** [v3.2.2](CHANGELOG_v3.2.2.md) | [v3.2.1](CHANGELOG_v3.2.1.md) | [v3.2.0](CHANGELOG_v3.2.0.md) | [v3.1.0](CHANGELOG_v3.1.0.md)

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
├── security.py               # Bash command allowlist and validation
├── skills_manager.py         # Skills discovery and loading (v3.2.0)
├── lsp_plugins.py            # LSP code intelligence plugins (v3.2.0)
├── progress.py               # Progress tracking utilities
├── retry_manager.py          # Feature retry and skip logic
├── loop_detector.py          # Infinite loop prevention
├── error_handler.py          # Structured error logging
├── setup_mcp.py              # MCP server auto-configuration
├── prompts/
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   ├── coding_prompt.md      # Continuation session prompt (with v3.2.2 E2E debugging)
│   └── [other prompts]       # Enhancement, bugfix, validation modes
├── harness_data/             # Bundled package data (v3.2.0)
│   └── .claude/skills/       # Built-in skills
│       ├── puppeteer-testing/
│       ├── code-quality/
│       ├── project-patterns/
│       ├── harness-patterns/
│       └── lsp-navigation/
├── validators/               # Quality enforcement hooks
│   ├── e2e_hook.py           # E2E test enforcement (v3.2.1)
│   ├── e2e_verifier.py       # E2E debugging enforcement (v3.2.2)
│   ├── secrets_hook.py       # Secrets scanning
│   └── browser_cleanup_hook.py
├── infra/
│   └── healer.py             # Infrastructure self-healing
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
