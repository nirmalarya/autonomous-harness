# Pre-Flight Checklist - Before Running v2.0 on AutoGraph

**Systematic review before execution**

---

## ✅ Checklist

### 1. Folder Structure

**autonomous-harness:**
- [ ] `specs/` exists (example specs)
- [ ] `prompts/` has only .md files (no .py, no .txt specs)
- [ ] `regression_tester.py` in root (not in prompts/)
- [ ] `prompts.py` updated to use specs/

**AutoGraph:**
- [ ] `spec/` folder exists
- [ ] `spec/app_spec.txt` exists (654 features)
- [ ] `spec/feature_list.json` exists (654 features)
- [ ] `spec/enhancement_spec.txt` exists (5 bugfixes)

---

### 2. Prompts Review

**coding_prompt.md:**
- [ ] Uses `spec/app_spec.txt` (not root)
- [ ] Uses `spec/feature_list.json` (not root)
- [ ] Has stop condition check (Step 3)
- [ ] Has service health check (Step 4)
- [ ] Has database validation (Step 8)
- [ ] Has browser integration test (Step 9)
- [ ] Has E2E test (Step 10)
- [ ] Has zero TODOs check (Step 12)
- [ ] Has security checklist (Step 13)
- [ ] Has file organization (Step 15)
- [ ] Has regression test (Step 15)

**enhancement_initializer_prompt.md:**
- [ ] Checks for existing `spec/feature_list.json`
- [ ] Reads `spec/app_spec.txt`
- [ ] Reads `spec/enhancement_spec.txt`
- [ ] Appends to feature_list (doesn't replace!)
- [ ] Creates baseline_features.txt
- [ ] Numbers new features from (last + 1)

**enhancement_coding_prompt.md:**
- [ ] Checks regression EVERY session
- [ ] Tests baseline features intact
- [ ] All quality gates apply
- [ ] References spec/ folder

---

### 3. Scripts Review

**prompts.py:**
- [ ] `copy_spec_to_project` creates `project/spec/` directory
- [ ] Copies spec to `project/spec/app_spec.txt` or `enhancement_spec.txt`
- [ ] Copies `regression_tester.py` to project root
- [ ] get_initializer_prompt() supports modes
- [ ] get_coding_prompt() supports modes

**regression_tester.py:**
- [ ] Loads from `feature_list.json` (will be in spec/)
- [ ] Tests 10% random sample
- [ ] Returns exit code 0/1 correctly
- [ ] Executable (chmod +x)

---

### 4. File Paths Audit

**Search for absolute paths:**
```bash
grep -r "/Users/nirmalarya" prompts/ specs/ *.py *.md 2>/dev/null
# Should return nothing or very few
```

**Search for hardcoded locations:**
```bash
grep -r "generations/" prompts/ 2>/dev/null
# Should reference project_dir variable, not hardcoded
```

---

### 5. AutoGraph Readiness

**Check AutoGraph has:**
```bash
cd /Users/nirmalarya/Workspace/autograph

# Must exist:
ls -la spec/app_spec.txt           # Original spec
ls -la spec/feature_list.json      # 654 features
ls -la spec/enhancement_spec.txt   # Bugfixes to apply

# Verify content:
wc -l spec/*
cat spec/feature_list.json | python3 -c "import json, sys; print(f'{len(json.load(sys.stdin))} features')"
```

---

### 6. Enhancement Spec Validation

**Check autograph enhancement spec:**
```xml
<enhancement_spec>
  <project_name>AutoGraph</project_name>
  <mode>bugfix</mode>
  <critical_fixes>
    <!-- Should have 5-7 fixes listed -->
  </critical_fixes>
  <quality_gates>
    <!-- Should reference all 8 gates -->
  </quality_gates>
  <regression_testing>
    <!-- Should require 654 features preserved -->
  </regression_testing>
</enhancement_spec>
```

---

### 7. Issues to Fix

**Found during review:**

❌ **Issue 1:** `prompts/initializer_prompt.md` doesn't create `spec/` directory
- Need to add: `mkdir -p spec`

❌ **Issue 2:** `regression_tester.py` looks for `feature_list.json` in root
- Should look in `spec/feature_list.json`

❌ **Issue 3:** Prompts reference both `spec/feature_list.json` AND `feature_list.json`
- Should ONLY reference `spec/feature_list.json`

❌ **Issue 4:** `specs/` folder might not exist in harness
- Need to verify it was created

---

### 8. What Needs Fixing NOW

Let me fix these issues before giving green light...

---

## 🔧 Fixes Needed

1. Update initializer to create `spec/` folder
2. Fix `regression_tester.py` to use `spec/feature_list.json`
3. Ensure all prompt references are consistent (`spec/`)
4. Verify `specs/` folder exists in harness with example specs
5. Test prompt loading works

---

**Fixing now before green light...**

