# Changelog v3.2.3 - Documentation and Packaging Fixes

**Release Date:** 2026-01-02

## Fixes for PyPI Package Distribution

This release fixes packaging issues discovered during the first PyPI publish attempt.

### Changes

**Fixed:**
- ✅ Include `requirements.txt` in source distribution (MANIFEST.in)
- ✅ Fix skills path in MANIFEST.in (`.claude/skills` → `harness_data/.claude/skills`)
- ✅ Add GitHub Actions workflow for automated PyPI publishing (Trusted Publishers)

**Documentation:**
- ✅ Updated README with comprehensive v3.2.2 features
- ✅ Added Key Features section highlighting all v3.2.x capabilities
- ✅ Updated Project Structure to show all new modules
- ✅ Added PyPI installation as recommended method
- ✅ Links to all version changelogs

### Files Changed

**Modified:**
- `MANIFEST.in` - Added requirements.txt, fixed skills path
- `README.md` - Comprehensive feature documentation
- `VERSION` - 3.2.2 → 3.2.3
- `pyproject.toml` - Version bump
- `agent.py` - Version banner update

**Added:**
- `.github/workflows/publish-to-pypi.yml` - Automated PyPI publishing

### Breaking Changes

None - this is a documentation and packaging-only release.

### Installation

```bash
# From PyPI (now works correctly!)
pip install claude-harness

# From GitHub
pip install git+https://github.com/nirmalarya/claude-harness.git@v3.2.3
```

### Why v3.2.3 Instead of Re-publishing v3.2.2?

Best practice is to bump the version for any changes after a release tag, even documentation fixes. This ensures:
- Clear version history
- No confusion about which v3.2.2 someone has installed
- Proper semantic versioning

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
