---
name: linear-workflow
description: Linear project management workflow for autonomous coding in backlog mode. Use when LINEAR_API_KEY is configured. Covers issue fetching, status updates, META issue tracking, and comment protocol for documenting implementation work.
allowed-tools: []
model: claude-sonnet-4-5-20250929
---

# Linear Workflow for claude-harness

Essential patterns for working with Linear in backlog mode.

## When to Use

- Working in backlog mode with LINEAR_API_KEY configured
- Fetching issues from Linear project
- Updating issue status (Todo → In Progress → Done)
- Tracking implementation progress via META issue
- Documenting work in Linear comments

## Environment Setup

**Required Environment Variable:**
```bash
export LINEAR_API_KEY='lin_api_...'
```

Get your API key from: https://linear.app/settings/api

## Project Marker File

Linear projects use `.linear_project.json` to identify the project:

```json
{
  "team_id": "team_abc123",
  "project_id": "proj_xyz789",
  "project_name": "My Project"
}
```

### Finding Team and Project IDs

**Method 1: Linear URL**
```
https://linear.app/yourworkspace/team/ENG/project/my-project
                                    ^^^         ^^^^^^^^^^
                                  team_key    project_key
```

**Method 2: Use Linear Tools**
```
1. List teams: linear_list_teams()
2. Find your team, copy id
3. List projects: linear_list_projects(team_id="team_abc123")
4. Find your project, copy id
```

## META Issue Pattern

**Purpose:** Track overall session progress across context windows

**Format:** Create issue titled `[META] Project Progress Tracker`

**Usage:**
1. Create META issue at session start (if not exists)
2. Add comment for each feature implemented
3. Update with overall status and blockers

**Example META Issue Comment:**
```
Session 3 Progress Update

Completed Issues:
- PRJ-123 User authentication ✅
- PRJ-124 Dashboard layout ✅

Currently Working On:
- PRJ-125 User profile page

Next Up:
- PRJ-126 Settings page
- PRJ-127 Notification system

Overall Progress: 15/42 issues complete (36%)

Blockers: None
```

## Issue Workflow States

**Standard Linear Workflow:**
1. **Todo** - Issue not started
2. **In Progress** - Currently implementing
3. **Done** - Implementation complete

**Get Available States:**
```
# Fetch team's workflow states
states = linear_list_issue_statuses(team_id)
# Returns: [{"id": "state_123", "name": "Todo"}, ...]
```

**Transition Pattern:**
```
# Start work on issue
linear_update_issue(issue_id, state_id="in_progress_state_id")

# Complete issue
linear_update_issue(issue_id, state_id="done_state_id")
```

## Complete Implementation Workflow

### 1. Initialize Session

```bash
# Check for project marker
cat .linear_project.json

# If missing, create it manually or use Linear tools:
# 1. linear_list_teams() to get team_id
# 2. linear_list_projects(team_id) to get project_id
# 3. Create .linear_project.json with IDs
```

### 2. Fetch Issues

```
# List all Todo issues in project
issues = linear_list_issues(project_id, status="Todo")

# Get specific issue details
issue = linear_get_issue(issue_id)
```

### 3. Implement Issue

**Complete Pattern (follow this exactly):**

1. Update issue to "In Progress"
2. Implement feature following code-quality standards
3. Test functionality (E2E for UI features)
4. Update issue to "Done"
5. Add implementation comment to issue
6. Update META issue
7. Commit to git with Linear issue reference

**Example Implementation:**
```
# 1. Start work
linear_update_issue("issue_abc123", state_id="in_progress_state_id")

# 2. Implement feature
# ... implementation following code-quality skill ...

# 3. Tests pass
# npm test or pytest (verify all tests pass)

# 4. Mark complete
linear_update_issue("issue_abc123", state_id="done_state_id")

# 5. Document implementation
linear_create_comment("issue_abc123", """
✅ Implementation Complete

**Changes:**
- Created authentication API endpoint
- Added JWT token handling
- Implemented login form component
- E2E test passed with screenshots

**Files Modified:**
- api/auth.ts
- components/LoginForm.tsx
- tests/e2e/auth.spec.ts

**Test Results:**
- E2E: ✅ Passed
- Unit: ✅ Passed

**Commit:** abc123def
""")

# 6. Update META issue
linear_create_comment("meta_issue_id", "Completed PRJ-123: User authentication ✅")

# 7. Git commit
git commit -m "feat: Implement PRJ-123 - User authentication"
```

## Issue Comment Format

**Use this format for all implementation comments:**

```markdown
✅ Implementation Complete

**Changes:**
- [Bulleted list of what was implemented]
- [Focus on user-facing changes]
- [Include test status]

**Files Modified:**
- [List of modified files with paths]

**Test Results:**
- E2E: ✅ Passed / ⏭️ Skipped
- Unit: ✅ Passed

**Commit:** [short SHA]
```

**Example:**
```
✅ Implementation Complete

**Changes:**
- Created user profile page with avatar upload
- Added profile edit functionality
- Implemented real-time preview
- E2E test passed with screenshots

**Files Modified:**
- components/UserProfile.tsx
- api/profile.ts
- tests/e2e/profile.spec.ts

**Test Results:**
- E2E: ✅ Passed
- Unit: ✅ Passed

**Commit:** abc123d
```

## State File Management

**File:** `.cursor/linear-backlog-state.json`

**Structure:**
```json
{
  "integration": "linear",
  "team_id": "team_abc123",
  "project_id": "proj_xyz789",
  "project_name": "My SaaS App",
  "meta_issue_id": "issue_meta_1",
  "meta_issue_identifier": "PRJ-1",
  "issues": [
    {
      "id": "issue_123",
      "identifier": "PRJ-123",
      "title": "Implement user authentication",
      "description": "JWT-based auth with email/password",
      "status": "Done",
      "state_id": "state_done_id",
      "completed": true,
      "assignee": "user_abc",
      "updated_at": "2026-01-03T10:30:00Z"
    }
  ],
  "last_synced": "2026-01-03T12:00:00Z"
}
```

**Update Pattern:**
1. Load state file at session start
2. Update as issues progress
3. Write back after each change
4. Sync with Linear periodically

## Integration with feature_list.json

**Mapping Pattern:**
```json
{
  "id": 1,
  "description": "User authentication (PRJ-123)",
  "linear_issue_id": "issue_123",
  "linear_identifier": "PRJ-123",
  "passing": true
}
```

**Sync Strategy:**
- Linear issue ID stored in feature_list.json
- Issue status (Done) → feature "passing": true
- Bidirectional tracking ensures consistency

## Common Workflows

### Start New Issue

```
# 1. Get next Todo issue
issues = linear_list_issues(project_id, status="Todo")
next_issue = issues[0]

# 2. Update to In Progress
linear_update_issue(next_issue["id"], state_id="in_progress_id")

# 3. Add starting comment
linear_create_comment(next_issue["id"], "Starting implementation...")
```

### Complete Issue

```bash
# 1. Verify tests pass
npm test  # or pytest

# 2. Update status to Done
linear_update_issue(issue_id, state_id="done_id")

# 3. Document implementation (use format above)
linear_create_comment(issue_id, "...")

# 4. Update META issue
linear_create_comment(meta_issue_id, "Completed PRJ-123...")

# 5. Git commit
git commit -m "feat: Implement PRJ-123 - User auth"
```

### Handle Blocked Issue

```
# 1. Add blocker comment
linear_create_comment(issue_id, "⚠️ Blocked: Missing API documentation for OAuth integration")

# 2. Update status (if team has Blocked state)
# linear_update_issue(issue_id, state_id="blocked_state_id")

# 3. Move to next issue
# Continue with next Todo issue
```

### Session Handoff

```
# At end of session, update META issue:
linear_create_comment(meta_issue_id, """
Session Handoff - January 3, 2026

Progress This Session:
- Completed PRJ-123 (User auth) ✅
- Completed PRJ-124 (Dashboard) ✅
- Started PRJ-125 (User profile) - 60% complete

Next Session Should:
1. Finish PRJ-125 user profile page
2. Begin PRJ-126 settings page
3. Address any test failures

Blockers: None
Overall: 15/42 issues (36%)
""")
```

## Error Handling

### Missing LINEAR_API_KEY

**Symptom:** Linear tools not available

**Fix:**
1. Set LINEAR_API_KEY environment variable
2. Verify key starts with 'lin_api_'
3. Check key from https://linear.app/settings/api
4. Restart session

### Issue Not Found

**Symptom:** Error when fetching issue

**Fix:**
1. Verify project_id in .linear_project.json
2. Check issue hasn't been archived/deleted in Linear
3. Refresh state file from Linear
4. Use linear_list_issues to see available issues

### Status Update Fails

**Symptom:** linear_update_issue returns error

**Fix:**
1. Check workflow state IDs are correct
2. Use linear_list_issue_statuses to get valid states
3. Verify API key has write permissions
4. Ensure issue belongs to correct project

### Authentication Errors

**Symptom:** HTTP 401 errors

**Fix:**
1. Verify API key format (starts with 'lin_api_')
2. Check key hasn't been revoked in Linear settings
3. Test key in Linear API playground
4. Generate new key if needed

## Best Practices

### One Issue at a Time
- Complete current issue before moving to next
- Update status immediately (don't batch updates)
- Mark as Done only after tests pass

### Detailed Comments
- Document implementation thoroughly
- Include file paths and test results
- Explain any gotchas or trade-offs

### META Issue Sync
- Update after each completed issue
- Keep it current with overall progress
- Note blockers and dependencies

### Test Before Done
- Always verify E2E tests pass for UI features
- Run unit tests before marking complete
- Include test screenshots in .claude/verification/

### State File Backup
- Git commit .cursor/linear-backlog-state.json
- Sync periodically from Linear
- Keep feature_list.json in sync

### Git Commit Messages
- Reference Linear issue: "feat: PRJ-123 - Feature name"
- Use conventional commits format
- Link to Linear issue in commit body if needed

## Troubleshooting

### Tools Not Appearing

**Check:**
- LINEAR_API_KEY is set
- Backlog mode is active (`--mode backlog`)
- Harness startup logs show Linear MCP loaded

**Fix:**
```bash
# Verify env var
echo $LINEAR_API_KEY

# Restart with backlog mode
claude-harness --mode backlog --project-dir ./project
```

### Can't Update Issues

**Check:**
- API key has write permissions
- Issue belongs to correct project
- State IDs are valid for team workflow

**Fix:**
```
# Get valid state IDs
states = linear_list_issue_statuses(team_id)
# Use the correct state_id for your workflow
```

### State File Corruption

**Recovery:**
1. Re-sync from Linear: linear_list_issues
2. Rebuild from feature_list.json
3. Check git history for last good version
4. Create new state file if needed

### Network Errors

**Check:**
- Internet connection active
- Linear API status (https://linear.app/status)
- API key not rate limited

**Fix:**
- Wait and retry
- Check Linear status page
- Verify API key hasn't been revoked

## Advanced Patterns

### Custom Workflow States

If your team uses custom states beyond Todo/In Progress/Done:

```
# Get your team's states
states = linear_list_issue_statuses(team_id)

# Store in .linear_project.json
{
  "workflow_states": {
    "todo": "state_abc_todo",
    "in_progress": "state_abc_inprog",
    "review": "state_abc_review",
    "done": "state_abc_done"
  }
}
```

### Multiple Projects

Use separate project directories:

```bash
# Project A
cd project-a
cat .linear_project.json  # team_id: "team_1", project_id: "proj_a"

# Project B
cd ../project-b
cat .linear_project.json  # team_id: "team_1", project_id: "proj_b"
```

### Issue Labels

Filter by labels:

```
# Get labeled issues
issues = linear_list_issues(project_id)
frontend_issues = [i for i in issues if "frontend" in i.get("labels", [])]
```

## Summary

Linear workflow in claude-harness:

1. **Setup:** Set LINEAR_API_KEY, create .linear_project.json
2. **Initialize:** Create META issue for session tracking
3. **Implement:** Fetch issue → In Progress → Implement → Done → Comment
4. **Document:** Detailed comments, META updates, git commits
5. **Sync:** Keep state file and feature_list.json in sync

Follow this workflow for consistent, trackable autonomous development with Linear.
