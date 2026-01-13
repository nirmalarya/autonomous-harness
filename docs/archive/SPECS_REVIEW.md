# Enhancement & Bugfix Specs - Review

**Current specs ready to use with autonomous-harness v2.0**

---

## 📋 Spec 1: AutoGraph v3.1 Foundation Fixes

**File:** `autograph_v3.1_fixes.txt`  
**Mode:** Bugfix  
**Base:** AutoGraph v3.0 (654 features)  
**Goal:** Fix foundation issues, make core CRUD work reliably

### What Will Be Fixed

**P0 Critical (5 fixes):**
1. Database schema incomplete
   - Missing columns in files, versions tables
   - Add all missing columns
   - Test all queries work

2. Services unhealthy
   - auth-service, diagram-service, collaboration-service, integration-hub
   - Debug health checks
   - Fix startup issues

3. Save diagram fails
   - "Failed to save" error in browser
   - Fix authorization
   - E2E test: draw → save → reopen (persists!)

4. Duplicate template fails
   - Fix duplication endpoint
   - Test in browser

5. Create folder fails sometimes
   - Fix folder creation
   - 100% success rate

### How It Works

**Session 1 (Enhancement Initializer):**
- Scans AutoGraph v3.0
- Finds 654 existing features
- Reads autograph_v3.1_fixes.txt
- Generates ~10 bugfix features (655-664)
- Appends to feature_list.json
- **Preserves all 654 existing features!**

**Sessions 2+:**
- Implements each bugfix
- Runs quality gates (schema, E2E, regression!)
- Tests 654 features still work
- Marks bugfix as passing when complete

**Expected Additions:**
```json
[
  ...654 existing features preserved...
  
  {"id": 655, "category": "bugfix", "description": "Fix: Database schema - files table", "passes": false},
  {"id": 656, "category": "bugfix", "description": "Fix: Services unhealthy", "passes": false},
  {"id": 657, "category": "bugfix", "description": "Fix: Save diagram 403", "passes": false, "fixes_feature": 42},
  {"id": 658, "category": "bugfix", "description": "Fix: Duplicate template", "passes": false},
  {"id": 659, "category": "bugfix", "description": "Fix: Folder creation", "passes": false}
]
```

**Quality Gates Applied:**
- ✅ Database validation (prevents schema errors!)
- ✅ Service health (waits for healthy!)
- ✅ E2E testing (tests in browser!)
- ✅ Regression (654 features must still work!)
- ✅ Zero TODOs
- ✅ Security checklist

**Timeline:** ~5-10 sessions (depends on issues found)  
**Result:** AutoGraph v3.1 with solid foundation! ✅

---

## 📋 Spec 2: SHERPA v1.1 Enhancements

**File:** `sherpa_v1.1_enhancement_spec.txt`  
**Mode:** Enhancement  
**Base:** SHERPA v1.0 (165 features)  
**Goal:** Add new integrations and capabilities

### What Will Be Added

**P1 Critical (3 enhancements):**
1. Update embedded harness to v2.0
   - Sync sherpa/core/harness/ with autonomous-harness v2.0
   - Add all quality gates
   - Better execution engine!

2. AGENT.md generator
   - Similar to .cursor/rules/ generator
   - For agent-based workflows
   - CLI: `sherpa generate agent`

3. Local vector DB (Qdrant)
   - Replace AWS Bedrock
   - No cloud dependency
   - Works offline
   - Faster, cheaper!

**P2 High (2 integrations):**
4. GitHub Issues integration
   - Pull issues from repos
   - Sync progress back
   - CLI: `sherpa init --source github`

5. Linear integration
   - Pull from Linear workspace
   - Team visibility
   - CLI: `sherpa init --source linear`

**P3 Medium (2 features):**
6. Kubernetes manifests
   - Production-ready K8s deployment
   - Cloud-agnostic

7. Quality improvements
   - Clean up any TODOs
   - Puppeteer E2E tests
   - Performance optimization

### How It Works

**Session 1:**
- Scans SHERPA v1.0
- Finds 165 existing features
- Reads sherpa_v1.1_enhancement_spec.txt
- Generates ~40-50 new features (166-215)
- Appends to feature_list.json
- **Preserves all 165 existing!**

**Expected Additions:**
```json
[
  ...165 existing SHERPA features...
  
  {"id": 166, "category": "enhancement", "description": "Update harness to v2.0", "passes": false},
  {"id": 167, "category": "enhancement", "description": "AGENT.md generator", "passes": false},
  {"id": 168, "category": "enhancement", "description": "Qdrant vector DB integration", "passes": false},
  {"id": 169, "category": "enhancement", "description": "GitHub Issues integration", "passes": false},
  {"id": 170, "category": "enhancement", "description": "Linear integration", "passes": false},
  ...
]
```

**Quality Gates Applied:**
- ✅ All 8 quality gates
- ✅ Regression (165 features must still work!)
- ✅ No breaking changes

**Timeline:** ~30-40 sessions  
**Result:** SHERPA v1.1 with new capabilities! ✅

---

## 🎯 Recommendations

### AutoGraph Spec (autograph_v3.1_fixes.txt)

**Looks good!** Focus is right:
- Foundation fixes only
- 5 critical issues
- Preserves 654 features
- Quality gates will enforce testing

**Suggested additions:**
```xml
<critical_fixes>
  ...existing 5 fixes...
  
  <!-- Add these for completeness -->
  <fix priority="P1">
    <issue>Email TODOs not implemented</issue>
    <solution>Implement SMTP for verification, password reset, notifications</solution>
    <test>Emails actually send, users receive them</test>
  </fix>
  
  <fix priority="P1">
    <issue>Frontend console errors</issue>
    <solution>Fix any console errors found during testing</solution>
    <test>Clean console (zero red errors)</test>
  </fix>
</critical_fixes>
```

**Run this:** Week 4 (after harness testing on simple project)

---

### SHERPA Spec (sherpa_v1.1_enhancement_spec.txt)

**Comprehensive!** Covers all roadmap items:
- Harness sync to v2.0 ✅
- AGENT.md generator ✅
- GitHub, Linear ✅
- Qdrant ✅
- K8s ✅

**Perfect as-is!**

**Run this:** Week 5 (after AutoGraph proves v2.0 works)

---

## 📊 Execution Order

**Recommended sequence:**

1. **Week 1:** Test autonomous-harness v2.0 on simple project
   - Validate quality gates work
   - Fix any issues in harness
   - Document learnings

2. **Week 2:** Replicate to cursor-harness v2.0
   - Copy all improvements
   - Test on simple project

3. **Week 3:** Use autonomous-harness v2.0 on **AutoGraph**
   - Run with autograph_v3.1_fixes.txt
   - Validate: quality gates catch issues!
   - Validate: regression tests work!
   - Result: AutoGraph v3.1 working!

4. **Week 4:** Use autonomous-harness v2.0 on **SHERPA**
   - Run with sherpa_v1.1_enhancement_spec.txt
   - Add new features
   - Validate: 165 features still work!
   - Result: SHERPA v1.1 enhanced!

---

## ✅ Both Specs Ready!

**AutoGraph spec:** Foundation fixes (5-7 bugfixes)  
**SHERPA spec:** Feature additions (~40-50 enhancements)

**Both preserve existing features via regression testing!**

---

**Want to modify either spec before we start?** 🤔

Or ready to begin testing autonomous-harness v2.0? 🚀

