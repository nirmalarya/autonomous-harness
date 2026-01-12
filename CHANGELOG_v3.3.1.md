# CHANGELOG - v3.3.1

**Release Date:** January 11, 2026

**Type:** Bugfix Release

---

## 🐛 Bugfix: Improved CLI UX - Helpful Error Messages

### Issue

Running `claude-harness` without required `--spec` parameter crashed with a cryptic error:

```
Fatal error: [Errno 2] No such file or directory: '/Users/.../specs/simple_example_spec.txt'
Traceback (most recent call last):
  ...
  FileNotFoundError: [Errno 2] No such file or directory
```

This provided a poor user experience, especially for first-time users who didn't know the `--spec` parameter was required.

### Root Cause

1. The CLI didn't validate required parameters early in execution
2. When `--spec` was omitted, it tried to use a default spec file that doesn't exist
3. The error occurred deep in the code during file copying, not at the argument parsing stage
4. No helpful guidance was provided to users on correct usage

### Fix

**Three-part solution for better UX:**

**Part 1: Early Validation** (`autonomous_agent.py:147-158`)

Added validation check immediately after parsing arguments, before any agent initialization:

```python
# Validate spec file for greenfield mode too
if args.mode == "greenfield" and not args.spec:
    # Check if default spec exists
    default_spec = Path(__file__).parent / "specs" / "simple_example_spec.txt"
    if not default_spec.exists():
        print("Error: No spec file provided")
        print("\nUsage:")
        print("  claude-harness --spec <path-to-spec-file> --project-dir <directory>")
        print("\nExample:")
        print("  claude-harness --spec /path/to/app_spec.txt --project-dir ./my_project")
        print("\nFor more information, run: claude-harness --help")
        return
```

**Part 2: Better Error Messages** (`prompts/__init__.py:129-137`)

Added defensive error handling with helpful message:

```python
# Check if default spec exists
if not spec_source.exists():
    raise FileNotFoundError(
        f"\nError: No spec file provided and default spec not found.\n\n"
        f"Usage: claude-harness --spec <path-to-spec-file>\n\n"
        f"Example:\n"
        f"  claude-harness --spec /path/to/app_spec.txt --project-dir ./my_project\n\n"
        f"For greenfield mode, you need an app specification file.\n"
        f"See the claude-harness documentation for spec file format."
    )
```

**Part 3: Improved Help Text** (`autonomous_agent.py:32-49`)

Updated `--help` output to:
- Mark `--spec` as REQUIRED in the parameter description
- Show practical examples with the spec parameter included
- Use `claude-harness` command name instead of `python autonomous_agent_demo.py`

### Impact

**Before:**
```bash
❯ claude-harness
Fatal error: [Errno 2] No such file or directory: '/Users/.../specs/simple_example_spec.txt'
Traceback (most recent call last):
  ...
```

**After:**
```bash
❯ claude-harness
Error: No spec file provided

Usage:
  claude-harness --spec <path-to-spec-file> --project-dir <directory>

Example:
  claude-harness --spec /path/to/app_spec.txt --project-dir ./my_project

For more information, run: claude-harness --help
```

**Benefits:**
- ✅ Clear, actionable error message
- ✅ Shows correct usage immediately
- ✅ Guides users to `--help` for more information
- ✅ No confusing stack traces for missing parameters
- ✅ Better first-time user experience

### Testing

Test the improved UX:

```bash
# Test without arguments
claude-harness
# Expected: Helpful error message with usage example

# Test help
claude-harness --help
# Expected: Clear documentation with examples

# Test correct usage
claude-harness --spec app_spec.txt --project-dir ./my_project
# Expected: Agent starts normally
```

---

## 🔧 Files Changed

### Modified

**autonomous_agent.py** (lines 82-86, 123-130, 147-158)
- Updated `--spec` help text to mark as REQUIRED
- Updated fallback version to 3.3.1
- Added early validation for missing spec file
- Improved help examples to show `claude-harness` command

**prompts/__init__.py** (lines 129-137)
- Added defensive error handling with helpful message
- Validates default spec file exists before attempting to copy

---

## 📝 Version Info

- **Previous:** v3.3.0
- **Current:** v3.3.1
- **Release Type:** Bugfix (patch release)

---

## ⚡ Upgrade Instructions

```bash
# Upgrade via pip
pip install --upgrade claude-harness

# Or if installed from source
cd /path/to/claude-harness
git pull origin main
pip install -e .
```

**No breaking changes** - This is a drop-in replacement with improved error handling.

---

**Status:** ✅ READY FOR RELEASE

This bugfix significantly improves the CLI user experience by providing clear, actionable error messages instead of confusing stack traces.
