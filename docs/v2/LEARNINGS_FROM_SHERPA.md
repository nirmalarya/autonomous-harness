# 📚 Learnings from SHERPA Build - Apply to autonomous-harness

**Source:** SHERPA v1.0 build (165/165 features, 143 sessions)
**Harness:** autonomous-coding (to become autonomous-harness v2.0)

---

## 🎯 Critical Learnings to Apply

### 1. File Organization Rules (CRITICAL!) 🔴

**Problem in SHERPA:**
- Agent created 150+ files in root directory!
- test_*.html, SESSION_*.md, debug_*.js all in root
- Messy, unprofessional

**Solution for Harness:**
Add to `coding_prompt.md`:

```markdown
## FILE ORGANIZATION (MANDATORY!)

### Directory Structure Rules

ALL projects MUST maintain clean root directory:

```
project/
├── src/ or package_name/    # Source code
├── tests/                   # ALL test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .sessions/               # Session summaries (gitignored)
│   ├── SESSION_*.md
│   ├── feature_list.json
│   └── claude-progress.txt
├── scripts/                 # Utility scripts
│   ├── debug/
│   ├── verify/
│   └── tests/              # Test verification scripts
├── docs/                    # Documentation
│
└── Root (max 15 files):
    ├── README.md
    ├── requirements.txt or package.json
    ├── init.sh
    ├── LICENSE
    ├── .gitignore
    └── (essential config files only)
```

### Enforcement

**After implementing EACH feature:**
```bash
# Check root directory file count
root_files=$(ls -1 | wc -l)

if [ "$root_files" -gt 15 ]; then
    echo "⚠️  Root has $root_files files - ORGANIZE NOW!"
    
    # Move files to proper locations
    mv test_*.* tests/
    mv SESSION_*.md .sessions/
    mv debug_*.* scripts/debug/
    mv verify_*.* scripts/verify/
    
    # Commit organization
    git add .
    git commit -m "chore: organize files"
fi
```

**NEVER create files in root if they belong elsewhere!**
```

---

### 2. Stop Condition (CRITICAL!) 🔴

**Problem in SHERPA:**
- Reached 165/165 features ✅
- But kept working! (Sessions 148-149)
- Added keyboard shortcuts, tooltips (not in spec!)
- Risk of introducing bugs

**Solution for Harness:**
Add to `coding_prompt.md` at the very beginning:

```markdown
### STEP 1: CHECK IF COMPLETE (BEFORE ANYTHING ELSE!)

```bash
# Count progress
passing=$(grep -c '"passes": true' feature_list.json)
total=$(python -c "import json; print(len(json.load(open('feature_list.json'))))")

echo "Progress: $passing/$total features"

# If complete, STOP!
if [ "$passing" -eq "$total" ]; then
    echo "🎉 ALL $total FEATURES COMPLETE!"
    echo ""
    echo "✅ Application is complete and production-ready."
    echo "❌ DO NOT add features beyond the spec."
    echo "❌ DO NOT add enhancements or polish."
    echo "❌ DO NOT continue working."
    echo ""
    echo "Session complete. All features implemented. Application ready for deployment."
    exit 0
fi
```

**IF ALL FEATURES PASS: STOP IMMEDIATELY!**
- Do NOT add features not in feature_list.json
- Do NOT "improve" or "polish"
- Do NOT add keyboard shortcuts, tooltips, etc.
- **THE SPEC DEFINES THE SCOPE. STICK TO IT.**
```

---

### 3. TODO Prevention (HIGH PRIORITY!) 🔴

**Problem in SHERPA:**
- No TODOs found (good!)

**Problem in AutoGraph:**
- 3 TODOs in passing features (email sending)
- Features marked complete despite incomplete code

**Solution for Harness:**
Add to `coding_prompt.md`:

```markdown
### BEFORE marking "passes": true:

**Zero TODOs Policy:**

```bash
# Search for TODOs in feature's code
grep -r "TODO\|FIXME\|WIP\|HACK" services/ src/ --exclude-dir=node_modules

# If TODOs found:
if [ $? -eq 0 ]; then
    echo "❌ Cannot mark passing - TODOs found!"
    echo "Either:"
    echo "  1. Implement the TODO completely, OR"
    echo "  2. Keep feature as 'passes': false"
    exit 1
fi
```

**A feature is NOT complete if:**
- ❌ Code contains TODO/FIXME/WIP
- ❌ Has "for now" or "temporary" comments
- ❌ Has placeholder implementations
- ❌ Missing integrations (even external like SMTP)

**Either:**
- ✅ Implement 100% (no TODOs), OR
- ✅ Keep "passes": false until fully done, OR
- ✅ Create separate feature for the TODO part

**Never mark incomplete work as passing!**
```

---

### 4. .gitignore Completeness 🟡

**Learning from SHERPA:**
Created comprehensive .gitignore during build

**Apply to Harness:**
Add to `initializer_prompt.md`:

```markdown
### Create .gitignore (COMPREHENSIVE!)

```
# Python
__pycache__/
*.py[cod]
venv/
.venv/
*.db
*.db-journal

# Node
node_modules/
dist/
.next/

# Build artifacts
build/
*.egg-info/

# Logs (NEVER commit logs!)
logs/
*.log

# Session artifacts (gitignored by default)
.sessions/
SESSION_*.md
claude-progress.txt

# Test artifacts (generated, not source)
test_results*/
playwright-report/
*_verification.html

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

**Logs, sessions, test artifacts should NEVER be in git!**
```

---

### 5. Session Artifacts Organization 🟡

**Learning:**
Session summaries created in root → messy

**Apply to Harness:**
```markdown
### Session Documentation

**Location:** `.sessions/` directory (gitignored)

```bash
# Create .sessions directory
mkdir -p .sessions

# Store session artifacts there
# - SESSION_*.md
# - claude-progress.txt
# - feature_list.json (or symlink)
# - NEXT_SESSION_*.md

# Keep root clean!
```
```

---

### 6. Test File Organization 🟡

**Problem in SHERPA:**
100+ test files created in root!

**Solution:**
```markdown
### Test Files

**ALL test files go in tests/ directory!**

```
tests/
├── unit/              # Unit tests (*.test.py, *.spec.js)
├── integration/       # Integration tests
├── e2e/              # E2E tests (Playwright, etc.)
└── manual/           # Manual test scripts
    ├── verify_*.html
    └── test_*.html
```

**NEVER create test files in root directory!**
```

---

### 7. Python Package Structure 🟢

**Learning:**
`sherpa/sherpa/` structure is CORRECT Python packaging

**Document in Harness:**
```markdown
### Python Projects

Use standard package structure:
```
project-name/              # Repo root
├── package_name/         # Python package (same name)
│   ├── __init__.py
│   ├── module1.py
│   └── subpackage/
├── tests/
├── README.md
└── setup.py or pyproject.toml
```

This allows: `pip install .` and `import package_name`
```

---

### 8. Continuous Improvement Trap 🔴

**Problem:**
Agent didn't know when to stop → kept "improving"

**Already covered in Stop Condition above**, but emphasize:

```markdown
**The spec is the contract.**
**The feature list is the scope.**
**When all features pass: STOP.**

Do NOT:
- Add features not in spec
- "Improve" completed work
- Polish or enhance beyond requirements
- Add "nice to have" features

The human can request enhancements later.
Your job: Implement the spec, no more, no less.
```

---

### 9. Git Commit Organization 🟢

**Learning:**
328 commits but all in main branch

**Enhancement:**
```markdown
### Git Strategy

**During initial build:**
- Commits in main branch (linear history)

**For enhancements (brownfield):**
- Create feature branch: `enhancement/v1.1`
- Implement enhancements
- Human reviews and merges

**Commit messages:**
- Follow conventional commits
- One feature per commit
- Clear, descriptive messages
```

---

### 10. Documentation Structure 🟢

**Learning:**
SHERPA has great docs structure

**Apply to Harness:**
```markdown
### Documentation Organization

```
docs/
├── ARCHITECTURE.md       # System design
├── DEPLOYMENT.md         # Deployment options
├── API.md               # API reference
├── CONTRIBUTING.md      # Contribution guide
└── examples/            # Example configs
```

**Not in root!**
```

---

## 📋 Implementation Checklist for autonomous-harness v2.0

**Incorporate these learnings:**

### Critical (Must Have)
- [ ] 🔴 File organization enforcement
- [ ] 🔴 Stop condition (when all features pass)
- [ ] 🔴 TODO prevention policy
- [ ] 🔴 Comprehensive .gitignore template

### High Priority
- [ ] 🟡 .sessions/ directory (not root)
- [ ] 🟡 tests/ directory enforcement
- [ ] 🟡 scripts/ directory for utilities
- [ ] 🟡 docs/ directory for documentation

### Nice to Have
- [ ] 🟢 Python package structure guidance
- [ ] 🟢 Git branching for enhancements
- [ ] 🟢 Commit message standards

---

## 🔄 Sync Process

**When autonomous-harness v2.0 is released:**

### Step 1: Update SHERPA's Harness Code
```bash
cd sherpa

# Copy updated harness code
cp auto-harness/autonomous-harness/agent.py \
   sherpa/core/harness/agent_client.py

cp auto-harness/autonomous-harness/prompts/* \
   sherpa/core/harness/prompts/

# Test
pytest tests/
sherpa serve  # Verify works

# Commit
git add sherpa/core/harness/
git commit -m "chore: sync with autonomous-harness v2.0

Updated harness code to include:
- Brownfield/enhancement mode
- Stop condition
- TODO prevention
- File organization rules

SHERPA now has all autonomous-harness v2.0 improvements."

git push
```

### Step 2: Version Bump
```bash
# SHERPA v1.1 or v2.0 (depending on changes)
```

---

## 🎯 Future: SHERPA as Package Using Harness

**Ideal architecture (v3.0?):**

```python
# SHERPA becomes a wrapper around autonomous-harness
from autonomous_harness import AutonomousHarness

class SherpaHarness(AutonomousHarness):
    """SHERPA-specific enhancements to base harness."""
    
    def inject_knowledge(self, prompt):
        # Add SHERPA's knowledge layer
        snippets = self.kb.query(prompt)
        return super().run(prompt + snippets)
    
    def track_progress(self, feature):
        # Add to base tracking
        super().track_progress(feature)
        # Also: Azure DevOps, Linear, etc.
```

**Benefits:**
- ✅ No code duplication
- ✅ Automatic harness updates
- ✅ SHERPA adds value on top

---

**Action Required:** Track autonomous-harness improvements, sync to SHERPA!

