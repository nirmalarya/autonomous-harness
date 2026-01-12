# CHANGELOG - v3.3.2

**Release Date:** January 11, 2026

**Type:** Bugfix Release

---

## 🐛 Bugfix: Dynamic Version Display in Banner

### Issue

The banner displayed a hardcoded version number that didn't update when the package version changed:

```bash
❯ pip install claude-harness
Successfully installed claude-harness-3.3.1

❯ claude-harness --version
claude-harness v3.3.1

❯ claude-harness --spec app.txt --project-dir ./app
======================================================================
  AUTONOMOUS CODING AGENT v3.3.0  ❌ Wrong version!
======================================================================
```

This caused confusion as the `--version` flag showed the correct version, but the banner showed an outdated hardcoded version.

### Root Cause

The banner version in `agent.py:162` was hardcoded as a string literal instead of being read dynamically from the VERSION file:

```python
print("  AUTONOMOUS CODING AGENT v3.3.0")  # Hardcoded!
```

This meant the banner version had to be manually updated in multiple places for each release, and was easy to forget.

### Fix

**Dynamic Version Loading** (`agent.py:161-170`)

Modified the banner printing code to read the version dynamically from the VERSION file:

```python
# Read version from VERSION file
try:
    version_file = Path(__file__).parent / "VERSION"
    version = version_file.read_text().strip()
except Exception:
    version = "3.3.2"  # Fallback version

print("\n" + "=" * 70)
print(f"  AUTONOMOUS CODING AGENT v{version}")
print("=" * 70)
```

### Benefits

- ✅ Banner version always matches package version automatically
- ✅ Single source of truth (VERSION file)
- ✅ No need to manually update banner version in releases
- ✅ Consistent versioning across all display points:
  - `--version` flag
  - Banner header
  - Package metadata

### Impact

**Before:**
- Had to update version in 4 places: VERSION, pyproject.toml, autonomous_agent.py, agent.py
- Easy to forget agent.py banner version
- Confusing for users when versions don't match

**After:**
- Update version in 3 places: VERSION, pyproject.toml, autonomous_agent.py (fallback)
- Banner reads from VERSION automatically
- Consistent version display everywhere

### Testing

Test the fix:

```bash
# Install latest version
pip install --upgrade claude-harness

# Check version
claude-harness --version
# Output: claude-harness v3.3.2

# Run with spec
claude-harness --spec app.txt --project-dir ./app
# Banner should show: AUTONOMOUS CODING AGENT v3.3.2
```

---

## 🔧 Files Changed

### Modified

**agent.py** (lines 161-170)
- Changed from hardcoded version string to dynamic VERSION file reading
- Added try/except for graceful fallback
- Uses Path to locate VERSION file relative to module

**VERSION** (line 1)
- Updated to 3.3.2

**pyproject.toml** (line 7)
- Updated version to 3.3.2

**autonomous_agent.py** (line 128)
- Updated fallback version to 3.3.2

---

## 📝 Version Info

- **Previous:** v3.3.1
- **Current:** v3.3.2
- **Release Type:** Bugfix (patch release)

---

## ⚡ Upgrade Instructions

```bash
# Upgrade via pip
pip install --upgrade claude-harness

# Verify version
claude-harness --version
# Should show: claude-harness v3.3.2

# Verify banner
claude-harness --spec app.txt --project-dir ./app
# Banner should show: AUTONOMOUS CODING AGENT v3.3.2
```

**No breaking changes** - This is a drop-in replacement with corrected version display.

---

## Related Issues

- Fixes: Banner version inconsistency discovered in v3.3.1
- Related to: v3.3.1 CLI UX improvements

---

**Status:** ✅ READY FOR RELEASE

This bugfix ensures version numbers are consistent across all user-facing displays.
