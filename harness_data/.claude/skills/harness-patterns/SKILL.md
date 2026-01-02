---
name: harness-patterns
description: claude-harness workflow patterns for autonomous coding sessions. Use when working within claude-harness greenfield/enhancement/backlog modes. Covers feature_list.json management, git workflows, session continuity, and validation requirements.
---

# Claude-Harness Workflow Patterns

Essential patterns for autonomous coding with claude-harness.

## When to Use

- Working in greenfield/enhancement/backlog mode
- Implementing features from feature_list.json
- Committing changes with E2E validation
- Managing session state and progress

## feature_list.json Structure

**Greenfield mode:**
```json
[
  {
    "id": 1,
    "description": "User authentication with email/password",
    "passing": false
  },
  {
    "id": 2,
    "description": "Dashboard showing user profile",
    "passing": false
  }
]
```

**After implementing feature 1:**
```json
[
  {
    "id": 1,
    "description": "User authentication with email/password",
    "passing": true  // ✅ Marked as passing
  },
  {
    "id": 2,
    "description": "Dashboard showing user profile",
    "passing": false
  }
]
```

## Session Workflow

**1. Read feature_list.json**
```bash
cat feature_list.json
```
Identify next feature where `"passing": false`

**2. Implement Feature**
- Write code following code-quality standards
- Test functionality (E2E for UI features)
- Ensure tests pass

**3. Update feature_list.json**

Mark feature as passing:
```json
{"id": 1, "description": "...", "passing": true}
```

**4. Create test_results.json** (for UI features)

Document E2E test results:
```json
{
  "feature_id": 1,
  "test_status": "passed",
  "test_steps": [...]
}
```

**5. Commit Changes**
```bash
git add .
git commit -m "feat: Implement feature #1 - User authentication

- Added login form with email/password
- Implemented auth API endpoint
- E2E test passed

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Commit message format:**
- First line: `feat: Implement feature #{ID} - {description}`
- Body: Bullet points of what changed
- Footer: Claude Code attribution

## Enhancement Mode

**State file:** `.cursor/enhancement-state.json`

```json
{
  "features": [
    {
      "id": 1,
      "description": "Add dark mode toggle",
      "completed": false
    }
  ]
}
```

**Workflow:**
1. Read `.cursor/enhancement-state.json`
2. Implement next incomplete feature
3. Mark as `"completed": true`
4. Commit with `feat: Add {feature}` message

## Backlog Mode

**State file:** `.cursor/backlog-state.json`

```json
{
  "org": "MyOrg",
  "project": "MyProject",
  "work_items": [
    {
      "id": 12345,
      "title": "Implement user search",
      "state": "Active",
      "completed": false
    }
  ]
}
```

**Workflow:**
1. Read backlog-state.json
2. Implement next incomplete work item
3. Mark as `"completed": true`
4. Update Azure DevOps (harness handles this)
5. Commit

## Git Workflow

**Before committing:**
- [ ] Feature implemented completely
- [ ] Tests pass (E2E for UI features)
- [ ] No console.log or debug code
- [ ] feature_list.json updated
- [ ] test_results.json created (if applicable)

**Commit command:**
```bash
git add .
git commit -m "$(cat <<'EOF'
feat: Implement feature #42 - Login functionality

- Created login form component
- Added authentication API endpoint
- Stored JWT token in localStorage
- E2E test passed with screenshots

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**After commit:**
- Session ends or continues with next feature
- Harness validates commit exists
- Progress tracked in cursor-progress.txt

## Session Continuity

**cursor-progress.txt:**
```
Session 2: Implementing feature #1 - User authentication
Status: Completed
Files modified: src/Login.tsx, api/auth.ts
Tests: E2E passed
Commit: abc123

Session 3: Implementing feature #2 - Dashboard
Status: In progress
```

**Fresh context pattern:**
- Each session starts fresh (no memory of previous session)
- Read feature_list.json to see what's done
- Read cursor-progress.txt for context
- Continue from next incomplete feature

## Validation Requirements

**For ALL features:**
- Code follows code-quality standards
- No errors/warnings in console
- Feature marked as passing in feature_list.json

**For UI features (additionally):**
- E2E test with Puppeteer MCP
- Screenshots showing functionality
- test_results.json documenting test

**For API features (additionally):**
- Test with curl or Postman
- Return proper status codes
- Handle errors gracefully

## Common Patterns

**Check next feature:**
```bash
cat feature_list.json | jq '.[] | select(.passing == false) | .id, .description' | head -2
```

**Update feature as passing:**
```bash
# Manually edit feature_list.json to set "passing": true
```

**Verify tests pass:**
```bash
npm test  # or pytest, or appropriate test command
```

**Check git status before commit:**
```bash
git status
git diff
```

## Troubleshooting

**Feature not marked as passing:**
- Did tests pass?
- Did E2E test pass (for UI features)?
- Is test_results.json created?
- Is code complete?

**Git commit fails:**
- Check for secrets in code (.env, API keys)
- Verify hooks allow commit
- Ensure commit message format is correct

**Session seems stuck:**
- Check cursor-progress.txt for context
- Verify feature_list.json is updated
- Check if all tests pass

## Best Practices

- **One feature at a time** - Never implement multiple features in one session
- **Test before marking passing** - Don't mark passing without validation
- **Clear commit messages** - Future you will thank you
- **Update state files immediately** - Don't wait until end of session
- **Document E2E tests** - Screenshots prove it works

These patterns ensure smooth autonomous development with claude-harness.
