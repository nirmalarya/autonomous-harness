# autonomous-harness v2.0 - Implementation Plan

**Based on:** Learnings from SHERPA v1.0 + AutoGraph v3.0 builds  
**Goal:** Production-grade harness with zero false positives  
**Timeline:** 2 weeks (Week 1-2 of master roadmap)

---

## 🎯 Core Philosophy

**v1.0 philosophy:**
> "Build features until feature_list.json is complete"

**v2.0 philosophy:**
> "Build features CORRECTLY - verified, secure, complete, then stop at 100%"

---

## 🔴 Critical Improvements (Must Have for v2.0)

### 1. Browser Integration Testing (CORS Verification)

**Problem from AutoGraph:**
- Backend tests pass (curl works)
- Frontend tests pass (UI renders)
- **Integration fails** (CORS blocks browser → backend)
- Features marked passing but broken for users!

**Solution:**

**File:** `prompts/coding_prompt.md`

**Add new step after implementation:**

```markdown
### STEP 6.5: BROWSER INTEGRATION TEST (MANDATORY)

**CRITICAL:** For ANY feature with frontend → backend communication:

#### Test with Real Browser (Not Just Curl!)

1. **Open Browser DevTools** (F12)

2. **Navigate to feature in browser:**
   ```
   http://localhost:3000/[feature-page]
   ```

3. **Click Network Tab:**
   - Clear previous requests
   - Trigger the feature (button click, form submit)
   - Watch the request

4. **Verify Success:**
   ```
   ✅ Status: 200 OK (not 0, not failed, not CORS error)
   ✅ Response has expected data
   ✅ Request completed successfully
   ```

5. **If CORS Error Found:**
   ```
   ❌ Status: (failed) net::ERR_FAILED
   ❌ Console shows: "blocked by CORS policy"
   
   FIX IMMEDIATELY:
   ```

6. **Add CORS Middleware (Backend):**
   ```python
   # For FastAPI:
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],  # Frontend URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   # For Flask:
   from flask_cors import CORS
   CORS(app, origins=["http://localhost:3000"])
   
   # For Express:
   const cors = require('cors');
   app.use(cors({
     origin: 'http://localhost:3000',
     credentials: true
   }));
   ```

7. **Re-test in Browser:**
   - Refresh page
   - Trigger feature again
   - Verify Network tab shows 200 OK
   - Verify Console has no CORS errors

8. **Check Console Tab:**
   ```
   ✅ No red errors
   ✅ No CORS warnings
   ✅ No network failures
   ```

#### MANDATORY: Do Not Mark Passing Until

- [ ] curl test passes (backend works)
- [ ] Frontend component renders (UI works)
- [ ] **Browser Network tab shows 200 OK** (integration works!)
- [ ] **Browser Console shows no CORS errors** (integration works!)
- [ ] **Feature works end-to-end in browser** (user can use it!)

**DO NOT mark "passes": true if browser test fails!**

#### Quick Reference: Common CORS Issues

**Symptom:** `fetch failed` or `Network error`
**Solution:** Add CORS middleware to backend

**Symptom:** `preflight request failed`
**Solution:** Allow OPTIONS method in CORS

**Symptom:** `credentials mode` error
**Solution:** Set `allow_credentials=True`
```

---

### 2. Security Checklist (Prevent Credential Leaks)

**Problem from AutoGraph:**
- Login form used GET request
- Credentials appeared in URL bar!
- Passwords in browser history, logs, Referer headers
- CRITICAL security vulnerability!

**Solution:**

**File:** `prompts/coding_prompt.md`

**Add new step:**

```markdown
### STEP 6.6: SECURITY VERIFICATION (MANDATORY)

**For authentication, authorization, or sensitive data features:**

#### Security Checklist

Run through this checklist BEFORE marking feature as passing:

**Authentication/Authorization:**
- [ ] **No credentials in URLs** (use POST with request body, never GET!)
  ```bash
  # Check for this anti-pattern:
  grep -r "password.*GET\|token.*GET\|credentials.*GET" .
  # Should return nothing!
  ```

- [ ] **Passwords hashed** (bcrypt cost 12+, never plaintext)
  ```python
  # Correct:
  import bcrypt
  hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
  
  # Wrong:
  password_hash = hashlib.md5(password).hexdigest()  # ❌ TOO WEAK!
  ```

- [ ] **JWT tokens have expiration** (< 24 hours for access tokens)
  ```python
  # Correct:
  exp = datetime.utcnow() + timedelta(hours=1)  # 1 hour
  
  # Wrong:
  # No expiration set  # ❌ SECURITY RISK!
  ```

- [ ] **HTTPS in production** (documented in README/deployment docs)

**Input Validation:**
- [ ] **All inputs validated** (Pydantic models, schema validation)
- [ ] **SQL injection prevention** (use ORMs only, NO raw SQL!)
  ```bash
  # Check for SQL injection risks:
  grep -r "execute.*f\"\|execute.*%s\|execute.*+" .
  # Should use parameterized queries only!
  ```

- [ ] **XSS prevention** (sanitize HTML outputs, escape user input)

**API Security:**
- [ ] **Rate limiting** on auth endpoints (prevent brute force)
  ```python
  # Example: slowapi for FastAPI
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)
  
  @app.post("/login")
  @limiter.limit("5/minute")  # 5 attempts per minute
  async def login(...):
  ```

- [ ] **CORS configured correctly** (not `allow_origins=["*"]` in production!)

**Secrets Management:**
- [ ] **No hardcoded secrets** (use environment variables)
- [ ] **No secrets in git** (check with git log)
- [ ] **.env.example** provided (not .env with real secrets!)

#### Automated Security Scan

```bash
# Run before marking security features as passing:

# Check for credential leaks
grep -r "password.*=.*['\"].*['\"]" . && echo "❌ HARDCODED PASSWORD FOUND!"

# Check for SQL injection risks  
grep -r "execute.*f\"\|execute.*%s" . && echo "⚠️ SQL INJECTION RISK!"

# Check for weak hashing
grep -r "md5\|sha1" . && echo "⚠️ WEAK HASHING ALGORITHM!"

# Check for credentials in URLs
grep -r "GET.*password\|GET.*token\|GET.*secret" . && echo "❌ CREDENTIALS IN URL!"
```

**If ANY checks fail: Fix before marking feature as passing!**

#### Manual Security Review

For critical security features:
1. Review authentication flow end-to-end
2. Check authorization logic (who can access what)
3. Verify tokens can't be forged
4. Test privilege escalation attempts
5. Document security assumptions

**DO NOT mark security features as passing without thorough review!**
```

---

### 3. Zero TODOs Policy

**Problem from AutoGraph:**
- 3 TODOs in passing features
- "TODO: Send verification email" - feature incomplete!
- Marked as passing but not fully implemented

**Solution:**

```markdown
### STEP 6.7: ZERO TODOs VERIFICATION (MANDATORY)

**Before marking ANY feature as passing:**

```bash
# Check for TODOs in files you modified this session
git diff --name-only HEAD | xargs grep -n "TODO\|FIXME\|WIP\|HACK" 

# Or check specific files:
grep -r "TODO\|FIXME\|WIP" [files-you-changed]
```

#### If TODOs Found:

**Option A: Complete the Implementation**
- Implement the TODO properly
- Remove the TODO comment
- Test the completed implementation

**Option B: Defer to Next Session**
- Leave feature as "passes": false
- Do NOT mark as passing with TODOs
- Work on a different feature

**Option C: Document as Known Limitation** (RARE!)
Only for external dependencies:
```python
# Acceptable (external service not available):
# NOTE: Email sending requires SMTP configuration
# For local dev, emails are logged to console
logger.info(f"Would send email to {user.email}")

# NOT acceptable (incomplete implementation):
# TODO: Implement this feature  # ❌ NEVER!
```

#### Exception

**Documentation TODOs are OK** in comments:
```python
# TODO: Add more examples to this docstring
def my_function():
    """Does something."""
    pass  # Implementation complete, just docs TODO
```

**Implementation TODOs are NOT OK:**
```python
def my_function():
    # TODO: Actually implement this  # ❌ NEVER MARK PASSING!
    pass
```

#### Automated Check

```bash
# This should return 0 in implementation code:
find src/ -name "*.py" -exec grep -l "TODO" {} \; | wc -l

# If > 0: Complete or defer, do NOT mark passing!
```

**ZERO TODOs in passing features!** 🛑
```

---

### 4. Stop Condition (Prevent Scope Creep)

**Problem from SHERPA:**
- Hit 165/165 features (100%)
- Agent kept working! (Sessions 148-150)
- Added keyboard shortcuts, tooltips (beyond spec!)
- Risk of introducing bugs

**Solution:**

```markdown
### STEP 3.5: CHECK COMPLETION STATUS (FIRST!)

**CRITICAL: Check if ALL features are complete BEFORE doing ANY work!**

```bash
# Count total features
total=$(cat feature_list.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")

# Count passing features
passing=$(cat feature_list.json | python3 -c "import json, sys; print(len([f for f in json.load(sys.stdin) if f.get('passes')]))")

echo "Progress: $passing/$total features"

# Check if complete
if [ "$passing" = "$total" ]; then
    echo ""
    echo "🎉🎉🎉 PROJECT 100% COMPLETE! 🎉🎉🎉"
    echo ""
    echo "All $total features are passing!"
    echo ""
    echo "✅ STOP WORKING - Do not add features beyond spec!"
    echo "✅ Commit final state"
    echo "✅ Update cursor-progress.txt with completion"
    echo "✅ Exit this session"
    echo ""
    echo "Project is DONE. Do not continue."
    exit 0
fi

# If not complete, show what's left
echo "Remaining: $((total - passing)) features"
echo "Continue with feature implementation..."
```

**When 100% complete:**

1. ✅ Commit final state
2. ✅ Update progress notes: "PROJECT COMPLETE - 100%"
3. ✅ **STOP WORKING!**
4. ✅ Exit session

**DO NOT:**
- ❌ Add features beyond spec
- ❌ Implement "nice to have" improvements  
- ❌ Refactor working code
- ❌ Polish existing features
- ❌ Add enhancements

**Scope creep prevention!** If you want improvements, create an enhancement spec and run enhancement mode separately.
```

---

### 5. File Organization Rules

**Problem from SHERPA:**
- 150+ files in root directory!
- test_*.html, SESSION_*.md, debug_*.js all scattered
- Required manual cleanup (2 hours!)

**Solution:**

```markdown
### STEP 8.5: FILE ORGANIZATION CHECK (EVERY SESSION)

**Before committing, enforce clean structure:**

```bash
# Count root directory files (excluding hidden and dirs)
root_files=$(ls -1 | grep -v "^\." | wc -l)

if [ "$root_files" -gt 20 ]; then
    echo "⚠️  Root directory has $root_files files (max: 20)"
    echo "ORGANIZE NOW before committing!"
fi
```

#### Required Project Structure

```
project/
├── src/ or package_name/      # Source code ONLY
├── tests/                     # ALL test files here
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                   # Utility scripts
├── .sessions/                 # Session summaries (gitignored)
│   ├── SESSION_*.md
│   ├── feature_list.json
│   └── cursor-progress.txt
├── docs/                      # Documentation
└── (< 20 config files)       # README, package.json, etc.
```

#### File Placement Rules

**Move misplaced files:**
```bash
# All test files → tests/
mv test_*.html test_*.py test_*.js tests/ 2>/dev/null

# All session files → .sessions/
mv SESSION_*.md .sessions/ 2>/dev/null

# All debug scripts → scripts/
mv debug_*.* check_*.* verify_*.* scripts/ 2>/dev/null

# All docs → docs/
mv *.md docs/ 2>/dev/null
# (Keep README.md, CHANGELOG.md in root)
```

#### Automated Organization

```bash
# Run this before every commit:
./scripts/organize-files.sh

# Or manually check:
if [ "$(ls -1 | wc -l)" -gt 20 ]; then
    echo "❌ Too many root files - organize first!"
    exit 1
fi
```

**Root directory should have < 20 essential files!**
```

---

### 6. Puppeteer E2E Testing (Mandatory)

**Success from SHERPA:**
- Caught visual bugs (white-on-white text)
- Verified real user workflows
- Screenshot-based validation
- **Should be MANDATORY!**

**Solution:**

```markdown
### STEP 7: END-TO-END TESTING WITH PUPPETEER (MANDATORY)

**For features with user interface:**

#### Use Puppeteer MCP for Browser Automation

**Available tools:**
- `mcp__puppeteer__puppeteer_navigate` - Go to URL
- `mcp__puppeteer__puppeteer_screenshot` - Visual verification
- `mcp__puppeteer__puppeteer_click` - Interact with elements
- `mcp__puppeteer__puppeteer_type` - Fill forms
- `mcp__puppeteer__puppeteer_snapshot` - Get page state

#### E2E Test Template

```python
# 1. Navigate to feature
[Tool: mcp__puppeteer__puppeteer_navigate]
   Input: {'url': 'http://localhost:3000/login'}

# 2. Take before screenshot
[Tool: mcp__puppeteer__puppeteer_screenshot]
   Input: {'name': 'login-before'}

# 3. Interact (fill form)
[Tool: mcp__puppeteer__puppeteer_type]
   Input: {'element': 'email input', 'ref': '#email', 'text': 'test@example.com'}

[Tool: mcp__puppeteer__puppeteer_type]
   Input: {'element': 'password input', 'ref': '#password', 'text': 'SecurePass123!'}

# 4. Submit
[Tool: mcp__puppeteer__puppeteer_click]
   Input: {'element': 'submit button', 'ref': 'button[type="submit"]'}

# 5. Wait for result
[Tool: mcp__puppeteer__puppeteer_wait_for]
   Input: {'text': 'Welcome', 'time': 5}

# 6. Take after screenshot
[Tool: mcp__puppeteer__puppeteer_screenshot]
   Input: {'name': 'login-after-success'}

# 7. Verify success state
[Tool: mcp__puppeteer__puppeteer_snapshot]
   # Check page shows logged-in state
```

#### When to Use Puppeteer

**MANDATORY for:**
- Login/register flows
- Form submissions
- Multi-step workflows
- Critical user paths
- Features with complex UI interactions

**Optional for:**
- Simple API endpoints (curl sufficient)
- Backend-only features
- Internal utilities

#### Verification Checklist

Before marking feature as passing:
- [ ] Puppeteer test created
- [ ] Screenshots verify visual correctness
- [ ] No console errors during workflow
- [ ] Success state reached
- [ ] User workflow complete end-to-end

**Puppeteer catches what curl misses!** 🎯
```

---

### 7. Agent Skills Integration

**Game-changer from agentskills.io!**

**Solution:**

**File:** `client.py` (new function)

```python
def load_agent_skills():
    """
    Load Agent Skills from standard directories.
    
    Agent Skills is an open standard (agentskills.io) supported by:
    - Claude Code, Cursor, GitHub Copilot, VS Code, and more!
    
    Skills are SKILL.md files in:
    - ~/.skills/ (user skills)
    - <project>/.skills/ (project skills)
    """
    from pathlib import Path
    
    skills_dirs = [
        Path.home() / ".skills",           # User-level skills
        Path.cwd() / ".skills",            # Project-level skills
    ]
    
    skills_content = []
    
    for skills_dir in skills_dirs:
        if not skills_dir.exists():
            continue
            
        for skill_folder in skills_dir.iterdir():
            if not skill_folder.is_dir():
                continue
                
            skill_file = skill_folder / "SKILL.md"
            if skill_file.exists():
                skill_content = skill_file.read_text()
                skills_content.append(f"\n## Skill: {skill_folder.name}\n\n{skill_content}\n")
    
    if skills_content:
        return "\n".join(skills_content)
    
    return ""


def build_system_prompt_with_skills(base_prompt: str) -> str:
    """Inject Agent Skills into system prompt."""
    skills = load_agent_skills()
    
    if skills:
        skills_section = f"""

---

## AVAILABLE SKILLS

You have access to these skills to guide your development:

{skills}

**Use these skills to ensure:**
- Best practices are followed
- Security patterns are implemented correctly
- Code organization is clean
- Testing is comprehensive

Consult relevant skills when implementing features in those domains.

---

"""
        return base_prompt + skills_section
    
    return base_prompt
```

**File:** `prompts/coding_prompt.md` (update)

```markdown
### STEP 1.5: REVIEW AVAILABLE SKILLS

**If skills are available, they will be shown above.**

**Before implementing features:**
1. Review relevant skills
2. Follow patterns from skills
3. Use best practices from skills
4. Security guidelines from skills

**Skills guide you to write better code!** ✨
```

---

### 8. Comprehensive .gitignore

**Problem:** Logs, sessions, test artifacts committed by accident

**Solution:**

**File:** `.gitignore` (enhanced)

```gitignore
# Generated projects
generations/

# Python
__pycache__/
*.py[cod]
*.so
.venv/
venv/
*.egg-info/

# Logs (NEVER commit!)
logs/
*.log
*.log.*

# Session artifacts (build-time, not source)
.sessions/
SESSION_*.md
cursor-progress.txt
claude-progress.txt

# Test artifacts (generated, not source)
TEST_*.md
test_results/
*_verification.html
playwright-report/
screenshots/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
.next/
dist/

# Databases
*.db
*.db-journal
```

---

## 🟡 High Priority Improvements

### 9. Enhanced Progress Tracking

**File:** `progress.py`

```python
def generate_progress_report(feature_list_path):
    """Generate detailed progress report."""
    features = json.loads(Path(feature_list_path).read_text())
    
    passing = [f for f in features if f.get('passes')]
    
    by_category = {}
    for f in features:
        cat = f.get('category', 'unknown')
        by_category[cat] = by_category.get(cat, {'total': 0, 'passing': 0})
        by_category[cat]['total'] += 1
        if f.get('passes'):
            by_category[cat]['passing'] += 1
    
    report = f"""
Progress Report
===============

Overall: {len(passing)}/{len(features)} ({len(passing)*100//len(features)}%)

By Category:
"""
    
    for cat, stats in sorted(by_category.items()):
        pct = stats['passing'] * 100 // stats['total'] if stats['total'] > 0 else 0
        report += f"  {cat}: {stats['passing']}/{stats['total']} ({pct}%)\n"
    
    return report
```

---

### 10. Enhancement Mode (Brownfield Support)

**New capability!**

**Files to create:**
- `prompts/enhancement_initializer_prompt.md`
- `prompts/enhancement_coding_prompt.md`

**Main script update:**

```python
# In cursor_autonomous_agent.py

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-dir', required=True)
    parser.add_argument('--mode', choices=['greenfield', 'enhancement'], default='greenfield')
    parser.add_argument('--spec', help='Enhancement spec file')
    args = parser.parse_args()
    
    if args.mode == 'enhancement':
        # Use enhancement prompts
        initializer_prompt = load_prompt('enhancement_initializer_prompt.md')
        coding_prompt = load_prompt('enhancement_coding_prompt.md')
    else:
        # Use greenfield prompts
        initializer_prompt = load_prompt('initializer_prompt.md')
        coding_prompt = load_prompt('coding_prompt.md')
    
    # Rest of code...
```

---

## 🟢 Nice-to-Have Improvements

### 11. Linear Tracker Integration
### 12. GitHub Issues Integration  
### 13. Performance Optimizations
### 14. Better Error Handling
### 15. Session Recovery

---

## 📋 Implementation Checklist

### Week 1: Critical Quality Gates

- [ ] Add browser integration testing step
- [ ] Add security checklist step
- [ ] Add zero TODOs verification
- [ ] Add stop condition check
- [ ] Add file organization rules
- [ ] Update .gitignore (comprehensive)
- [ ] Test on simple project
- [ ] Document changes

### Week 2: Enhanced Testing & Skills

- [ ] Make Puppeteer E2E mandatory
- [ ] Add E2E test templates to prompts
- [ ] Implement Agent Skills loading
- [ ] Inject skills into prompts
- [ ] Create organization skill (file structure)
- [ ] Create security skill (checklist)
- [ ] Create CORS skill (always configure)
- [ ] Test on SHERPA v1.1 enhancement

---

## 🧪 Testing Strategy

**Test v2.0 improvements on:**

1. **Simple project** (greenfield) - Verify basics work
2. **SHERPA v1.1** (enhancement) - Prove enhancement mode works
3. **New project** (greenfield) - Verify quality gates enforce quality
4. **Comparison** - v1.0 vs v2.0 built apps (measure improvement)

---

## 📊 Success Metrics

**v2.0 is ready when:**

- ✅ All 8 critical improvements implemented
- ✅ Tested on 3 projects (simple, SHERPA, new)
- ✅ Zero false positives (all passing features actually work)
- ✅ Security issues: 0 (gates catch them)
- ✅ CORS issues: 0 (browser testing catches them)
- ✅ TODOs in passing features: 0 (policy enforced)
- ✅ Scope creep: 0 (stops at 100%)
- ✅ File organization: Clean (< 20 root files)
- ✅ Apps built are A/A+ grade (no cleanup needed!)

**Target:** Apps built with v2.0 are production-ready immediately! 🎯

---

**Timeline:** 2 weeks to v2.0, then replicate to cursor-harness v2.0!

