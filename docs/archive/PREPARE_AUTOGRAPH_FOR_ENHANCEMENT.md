# Prepare AutoGraph for Enhancement Mode

**Goal:** Use autonomous-harness v2.0 to fix AutoGraph v3.0 foundation issues

---

## 📊 AutoGraph Current State

**Location:** `/Users/nirmalarya/Workspace/autograph/`

**Existing files:**
- `docs/app_spec.txt` - Original spec (654 features defined, cleaned/generic) ✅
- `docs/feature_list.json` - Feature tracking (654 features, all marked "passes": true from v3.0 build) ✅
- `.sessions/` - Build history from cursor-harness

**Status:**
- Many features marked "passes": true but actually broken
- Database schema incomplete
- Services unhealthy
- CRUD operations fail

---

## 🎯 What autograph_v3.1_fixes.txt Does

**This spec tells the enhancement agent:**

"Fix these 5 critical foundation issues in AutoGraph"

**It's NOT:**
- ❌ A replacement for app_spec.txt (AutoGraph already has this!)
- ❌ A new feature list (AutoGraph has 654 features!)

**It IS:**
- ✅ A list of FIXES to apply
- ✅ An enhancement/bugfix spec
- ✅ Additional work on top of existing 654 features

---

## 🎯 How Enhancement Mode Will Work

### Step 1: Preparation (Manual - Do This First!)

```bash
# 1. Copy enhancement spec to AutoGraph
cp /Users/nirmalarya/Workspace/autonomous-harness/autograph_v3.1_fixes.txt \
   /Users/nirmalarya/Workspace/autograph/enhancement_spec.txt

# 2. Verify AutoGraph has required files
cd /Users/nirmalarya/Workspace/autograph
ls -la docs/app_spec.txt          # Should exist ✅
ls -la docs/feature_list.json     # Should exist ✅

# 3. Move them to root for agent (agent expects them in root during build)
cp docs/app_spec.txt .
cp docs/feature_list.json .

# Or update them in place
```

---

### Step 2: Run Enhancement Mode

```bash
cd /Users/nirmalarya/Workspace/autonomous-harness

python3 autonomous_agent.py \
  --project-dir /Users/nirmalarya/Workspace/autograph \
  --mode enhancement \
  --spec /Users/nirmalarya/Workspace/autograph/enhancement_spec.txt
```

---

### Step 3: What Happens (Automatic)

**Session 1 (Enhancement Initializer):**

1. Agent enters AutoGraph directory
2. Reads existing files:
   - `app_spec.txt` (original 654 features)
   - `feature_list.json` (654 features, many marked passing)
3. Reads `enhancement_spec.txt` (5 fixes to apply)
4. Analyzes current state:
   - Scans code
   - Checks what's broken
   - Reviews TODOs
5. Generates bugfix features:
   ```json
   {
     "id": 655,
     "category": "bugfix",
     "description": "Fix: Database schema incomplete",
     "passes": false
   }
   ```
6. **APPENDS to feature_list.json** (doesn't replace!)
7. Creates baseline:
   - "654 features exist, must not break them!"

**Sessions 2+:**
- Implements each bugfix (655, 656, 657...)
- Runs quality gates
- Runs regression (tests 654 features still work!)
- Marks bugfix as passing when complete

---

## 📊 Expected Outcome

**Before (v3.0):**
```
feature_list.json: 654 features
- Many marked "passes": true (but broken!)
- Database issues
- CRUD failures
```

**After Session 1 (Enhancement Initializer):**
```
feature_list.json: 664 features (654 + 10 bugfixes)
[
  {id: 1, description: "User registration", passes: true},
  ...
  {id: 654, description: "Last v3.0 feature", passes: true},
  
  // Bugfixes appended:
  {id: 655, category: "bugfix", description: "Fix: DB schema", passes: false},
  {id: 656, category: "bugfix", description: "Fix: Services", passes: false},
  {id: 657, category: "bugfix", description: "Fix: Save", passes: false},
  ...
]
```

**After All Sessions:**
```
feature_list.json: 664 features
- All 654 original still "passes": true (regression tested!)
- All 10 bugfixes now "passes": true (fixed!)
```

---

## ✅ Correct Understanding

**autograph_v3.1_fixes.txt:**
- Purpose: List of fixes to apply to AutoGraph
- Type: Enhancement/bugfix spec (not full app spec!)
- Adds: ~10 bugfix features to existing 654

**AutoGraph's app_spec.txt:**
- Purpose: Original requirements (654 features)
- Type: Full application specification
- Status: Already exists in AutoGraph!

**AutoGraph's feature_list.json:**
- Purpose: Track all features (original + fixes)
- Type: Feature tracking
- Gets: Appended with bugfixes (654 → 664)

---

## 🎯 Setup Script

Let me create a setup script:

```bash
#!/bin/bash
# prepare_autograph_for_enhancement.sh

cd /Users/nirmalarya/Workspace/autograph

echo "Preparing AutoGraph for enhancement mode..."

# Ensure files are in root (agent expects them there)
if [ ! -f "app_spec.txt" ] && [ -f "docs/app_spec.txt" ]; then
    cp docs/app_spec.txt .
    echo "✅ Copied app_spec.txt to root"
fi

if [ ! -f "feature_list.json" ] && [ -f "docs/feature_list.json" ]; then
    cp docs/feature_list.json .
    echo "✅ Copied feature_list.json to root"
fi

# Copy enhancement spec
cp /Users/nirmalarya/Workspace/autonomous-harness/autograph_v3.1_fixes.txt \
   ./enhancement_spec.txt
echo "✅ Copied enhancement spec"

# Verify
echo ""
echo "Files ready:"
ls -lh app_spec.txt feature_list.json enhancement_spec.txt

echo ""
echo "✅ AutoGraph ready for enhancement mode!"
echo ""
echo "Run:"
echo "cd /Users/nirmalarya/Workspace/autonomous-harness"
echo "python3 autonomous_agent.py \\"
echo "  --project-dir /Users/nirmalarya/Workspace/autograph \\"
echo "  --mode enhancement \\"
echo "  --spec /Users/nirmalarya/Workspace/autograph/enhancement_spec.txt"
```

---

**Should I create this setup script?** 🤔

