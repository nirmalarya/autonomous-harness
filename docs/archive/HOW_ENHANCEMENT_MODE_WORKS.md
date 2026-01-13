# How Enhancement Mode Works - AutoGraph Example

**Question:** How do we use enhancement mode on AutoGraph?

**Answer:** AutoGraph already has app_spec.txt and feature_list.json - we work WITH them!

---

## 🎯 AutoGraph Current State

**Location:** `/Users/nirmalarya/Workspace/autograph/`

**Has:**
- `docs/app_spec.txt` (654 features defined, cleaned/generic)
- `docs/feature_list.json` (654 features, some passing, some broken)
- `.sessions/` (session history from cursor-harness build)

**Status:**
- Some features work (login, register, create)
- Some features broken (save, duplicate, etc.)
- Database schema incomplete
- Services unhealthy

---

## 🎯 Goal of autograph_v3.1_fixes.txt

**This is an ENHANCEMENT spec that tells the agent:**

"Fix the broken parts of AutoGraph v3.0"

**NOT a full app spec - it's a FIX spec!**

**Contents:**
- 5 critical bugfixes to apply
- Quality gates to enforce
- Regression requirements (654 features must still work!)

---

## 📋 How Enhancement Mode Will Work

### Step 1: Agent Reads Existing AutoGraph

**Enhancement initializer will:**
```bash
cd /Users/nirmalarya/Workspace/autograph

# Read existing state
cat docs/app_spec.txt          # Original spec (654 features)
cat docs/feature_list.json     # Current state (some broken)

# Scan codebase
ls -la services/
cat README.md

# Read enhancement spec (what to fix)
cat enhancement_spec.txt       # Our autograph_v3.1_fixes.txt (copied here)
```

### Step 2: Agent Analyzes

**Identifies:**
- 654 existing features in feature_list.json
- Some marked "passes": true (but actually broken!)
- Some marked "passes": false

**Reads fix spec:**
- Fix database schema
- Fix services health
- Fix save functionality
- Fix duplicate
- Fix folder creation

### Step 3: Agent Generates Fix Features

**Appends to docs/feature_list.json:**

```json
[
  ...existing 654 features from v3.0...
  
  // NEW bugfix features appended:
  {
    "id": 655,
    "category": "bugfix",
    "description": "Fix: Database schema - add retention_policy columns to files table",
    "fixes_feature": null,  // Or ID of broken feature
    "steps": [
      "Check files table schema",
      "Add missing columns: retention_policy, retention_count, retention_days",
      "Create alembic migration",
      "Apply migration",
      "Test all CRUD operations work"
    ],
    "passes": false
  },
  {
    "id": 656,
    "category": "bugfix", 
    "description": "Fix: Services unhealthy - debug and fix health checks",
    "steps": [
      "Check docker-compose ps",
      "Debug why services unhealthy",
      "Fix health check endpoints",
      "Verify all services healthy",
      "Test stay healthy for 1+ hour"
    ],
    "passes": false
  },
  ...more bugfixes (657-664)...
]
```

**Total: 654 existing + ~10 bugfixes = 664 features**

---

## 🎯 Correct Setup for Enhancement Mode

### What We Need

**In AutoGraph project directory:**
- ✅ `docs/app_spec.txt` (already there! - original spec)
- ✅ `docs/feature_list.json` (already there! - 654 features)
- ✅ `enhancement_spec.txt` (COPY our autograph_v3.1_fixes.txt here)
- ✅ `regression_tester.py` (will be copied by harness)

### Correct Command

```bash
# 1. Copy enhancement spec to AutoGraph
cp /Users/nirmalarya/Workspace/autonomous-harness/autograph_v3.1_fixes.txt \
   /Users/nirmalarya/Workspace/autograph/enhancement_spec.txt

# 2. Run autonomous-harness in enhancement mode
cd /Users/nirmalarya/Workspace/autonomous-harness

python3 autonomous_agent.py \
  --project-dir /Users/nirmalarya/Workspace/autograph \
  --mode enhancement \
  --spec /Users/nirmalarya/Workspace/autograph/enhancement_spec.txt
```

**What happens:**

**Session 1 (Enhancement Initializer):**
- Reads `docs/app_spec.txt` (understands original project)
- Reads `docs/feature_list.json` (sees 654 existing features)
- Reads `enhancement_spec.txt` (learns what to fix)
- Appends ~10 bugfix features to feature_list.json
- Creates baseline (654 features must still work!)

**Sessions 2+:**
- Implements each bugfix
- Runs quality gates
- Tests regression (654 still work!)
- Marks bugfix as passing when complete

---

## ✅ Correct File Flow

```
autonomous-harness/
├── autograph_v3.1_fixes.txt    (source spec)
└── autonomous_agent.py

            ↓ Copy spec to

autograph/
├── docs/
│   ├── app_spec.txt            (EXISTING - original 654 features)
│   └── feature_list.json       (EXISTING - 654 features, some broken)
├── enhancement_spec.txt        (COPIED from autograph_v3.1_fixes.txt)
└── regression_tester.py        (COPIED by harness)

            ↓ Agent works here

autograph/
├── docs/
│   └── feature_list.json       (UPDATED - 654 + 10 bugfixes = 664)
├── services/                    (CODE FIXED)
└── .sessions/
    └── claude-progress.txt     (NEW - enhancement progress)
```

---

## 🎯 Your Insight is Correct!

**We should NOT create new app_spec.txt for AutoGraph!**
- ✅ Use existing `docs/app_spec.txt` (AutoGraph's original spec)
- ✅ Use existing `docs/feature_list.json` (AutoGraph's 654 features)
- ✅ Add enhancement_spec.txt (our fixes)

**The enhancement spec is ADDITIONAL, not replacement!**

---

**Should I:**
1. Update the enhancement spec to be clearer about this?
2. Create a setup script to prepare AutoGraph for enhancement mode?
3. Both?

**What would you like?** 🤔

