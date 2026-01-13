# Changelog v3.2.1 - E2E Test Enforcement

**Release Date:** 2026-01-02

## Critical Quality Fix

This release addresses a **critical quality issue** where features were being marked as passing based on "code verification" tests instead of actual end-to-end tests.

### Problem Identified

**Before v3.2.1:**
- Agent created two types of tests:
  - `test_feature_X_simple.py` - Code verification (just grepped source files)
  - `test_feature_X_e2e.py` - Real E2E test (HTTP requests to running backend)
- Agent would run ONLY the simple test and mark feature as passing
- E2E tests were created but never executed
- Result: Features marked as "passing" that didn't actually work end-to-end

**User Impact:**
- ~20-30% of "passing" features may have runtime issues
- Backend/frontend integration bugs not caught
- CORS errors, database issues, authentication failures not detected

### Fix Applied

**Strengthened STEP 12 in coding_prompt.md:**

1. **Explicit Distinction Between Test Types**
   - ❌ Code Verification: `test_*_simple.py`, `test_*_verification.py`
   - ✅ E2E Test: `test_*_e2e.py`, `test_*_api.py`, `test_*_integration.py`

2. **Mandatory E2E Test Execution**
   - Agent MUST find E2E test file (exits if not found)
   - Agent MUST verify backend is running (exits if not)
   - Agent MUST execute E2E test (not just create it)
   - Agent MUST show proof of E2E test passing

3. **Strengthened Quality Gates**
   - Added explicit checkboxes for E2E test execution
   - Made E2E test proof mandatory before marking passing
   - Clarified that code verification alone is insufficient

### Changes

**Modified Files:**
- `prompts/coding_prompt.md` - Strengthened STEP 12 (E2E test enforcement)
- `pyproject.toml` - Version bump to 3.2.1
- `VERSION` - Updated to 3.2.1

### Migration Path for Existing Projects

If you have features marked as passing from v3.2.0:

**Option 1: Validate Critical Features (Recommended)**
```bash
# Test the 10-15 most critical features manually
# If they work → high confidence
```

**Option 2: Full E2E Validation**
```bash
# Re-run all E2E tests, update status
# Keep passes=true if E2E passes
# Set passes=false if E2E fails
```

**Option 3: Add Test Quality Tracking**
```json
{
  "id": 99,
  "passes": true,
  "test_status": "code-verified",  // or "e2e-passed"
  "e2e_test_file": "test_feature_99_e2e.py"
}
```

### Breaking Changes

None - this is a prompt-only fix that strengthens validation for future features.

### Recommendations

1. **For New Development:** Use v3.2.1 - ensures E2E quality
2. **For Existing Projects:** Validate critical features at minimum
3. **Going Forward:** All features require passing E2E tests

## Version History

- v3.2.1 (2026-01-02) - E2E test enforcement
- v3.2.0 (2026-01-02) - Skills System + LSP Integration
- v3.1.0 (2025-12-30) - Triple timeout protection + retry logic
- v3.0.0 (2025-12-28) - Initial claude-harness release

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
