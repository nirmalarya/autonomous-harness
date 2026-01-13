# CHANGELOG - v3.3.3

**Release Date:** January 11, 2026

**Type:** Feature Release (LSP Auto-Installation)

---

## ✨ Feature: Auto-Install LSP Plugins

### User Request

> "Why should user install LSP manually? Based on the tech stack in the specs, can the claude-harness not install required LSP from the marketplace automatically?"

**Absolutely right!** The harness now automatically installs LSP plugins based on the detected tech stack.

### What's New

**Automatic LSP Plugin Installation**

claude-harness now:
1. **Detects tech stack from spec file** (for greenfield projects)
2. **Auto-installs LSP plugins** from claude-plugins-official marketplace
3. **Shows clear status** for each plugin (installed/already installed/skipped/failed)
4. **No manual intervention needed** - plugins install automatically on first run

### Before (v3.3.2)

```bash
❯ claude-harness --spec app.txt --project-dir ./app

Created security settings...
   - LSP detected: typescript
   - LSP marketplace: claude-plugins-official

LSP Plugin Installation Guide
============================================================

⚠️  Install Language Server First:

  TypeScript, JavaScript (typescript):
    1. Install server: npm install -g typescript-language-server typescript
    2. Install plugin: claude plugin install typescript-lsp@claude-plugins-official

============================================================
```

**User had to manually:**
1. Stop the agent
2. Install language server
3. Install plugin
4. Restart agent

### After (v3.3.3)

```bash
❯ claude-harness --spec app.txt --project-dir ./app

Created security settings...
   - LSP detected: typescript
   - LSP marketplace: claude-plugins-official

✅ Auto-installed LSP plugins:
   - typescript-lsp@claude-plugins-official

Sending prompt to Claude Agent SDK...
```

**Fully automated!** The plugin installs automatically and the agent continues.

### How It Works

**1. Spec File Analysis (New!)**

Detects tech stack from spec file keywords:
- **TypeScript/JavaScript**: react, nextjs, vue, angular, vite, typescript
- **Python**: django, flask, fastapi, python, pytest
- **Go**: golang, go
- **Rust**: rust, cargo
- **Java**: java, spring, maven, gradle
- **C/C++**: c++, cpp, clang, cmake
- **C#**: c#, csharp, .net, dotnet
- **PHP**: php, laravel, symfony, composer
- **Swift**: swift, ios, xcode
- **Lua**: lua

**2. Project File Detection**

Also checks existing project files:
- TypeScript: `package.json`, `tsconfig.json`
- Python: `requirements.txt`, `pyproject.toml`, `setup.py`
- Go: `go.mod`
- Rust: `Cargo.toml`
- Java: `pom.xml`, `build.gradle`
- etc.

**3. Auto-Installation**

For each detected language:
1. Check if language server is installed
2. Check if plugin already installed
3. Auto-install plugin if server present
4. Show clear status message

**4. Status Output**

Organized by status:
- ✅ **Auto-installed**: Newly installed plugins
- ✓ **Already installed**: Plugins previously installed
- ⚠️ **Skipped**: Server not installed (shows install command)
- ❌ **Failed**: Installation errors

### Example Outputs

**TypeScript project (server already installed):**
```
✅ Auto-installed LSP plugins:
   - typescript-lsp@claude-plugins-official
```

**TypeScript project (server not installed):**
```
⚠️  Skipped (language server not installed):
   - TypeScript, JavaScript: npm install -g typescript-language-server typescript
```

**Multi-language project:**
```
✅ Auto-installed LSP plugins:
   - typescript-lsp@claude-plugins-official
   - pyright-lsp@claude-plugins-official

⚠️  Skipped (language server not installed):
   - Go: go install golang.org/x/tools/gopls@latest
```

### Benefits

- ✅ **Zero manual setup** - plugins install automatically
- ✅ **Detects from spec** - works for greenfield projects (no files yet)
- ✅ **Detects from files** - works for existing projects
- ✅ **Clear status** - know exactly what happened
- ✅ **Idempotent** - safe to run multiple times
- ✅ **Fast** - runs in parallel during client setup

### Technical Details

**Files Modified:**

**lsp_plugins.py** (lines 118-237, 272-393)
- Added `detect_languages_from_spec()` - analyzes spec file for tech stack keywords
- Updated `detect_languages()` - checks spec first, then project files
- Added `auto_install_plugins()` - automatically installs plugins via `claude plugin install`
- Updated `setup_lsp()` - now includes `auto_install=True` by default

**client.py** (lines 128-154)
- Updated LSP output to show auto-installation results
- Organized output by status (installed/already installed/skipped/failed)
- Shows installation commands for skipped plugins

### Configuration

Auto-installation is **enabled by default**. To disable:

```python
# In client.py
lsp_setup = lsp_manager.setup_lsp(auto_install=False)
```

### Requirements

- Claude Code v1.0.33+ (for plugin system)
- Language servers must be installed separately
  - TypeScript: `npm install -g typescript-language-server typescript`
  - Python: `npm install -g pyright`
  - Go: `go install golang.org/x/tools/gopls@latest`
  - etc.

### Future Enhancements

Potential improvements:
- Auto-install language servers too (with user consent)
- Detect from `package.json` dependencies
- Support custom LSP configurations
- Plugin version pinning

---

## 🔧 Files Changed

### Modified

**lsp_plugins.py** (lines 118-393)
- Added spec file tech stack detection
- Added auto-installation with status tracking
- Enhanced language detection logic

**client.py** (lines 128-154)
- Replaced manual installation guide with auto-install results
- Improved status output formatting

**VERSION** (line 1)
- Updated to 3.3.3

**pyproject.toml** (line 7)
- Updated version to 3.3.3

**autonomous_agent.py** (line 128)
- Updated fallback version to 3.3.3

**agent.py** (line 166)
- Updated fallback version to 3.3.3

---

## 📝 Version Info

- **Previous:** v3.3.2
- **Current:** v3.3.3
- **Release Type:** Feature (minor version bump)

---

## ⚡ Upgrade Instructions

```bash
# Upgrade via pip
pip install --upgrade claude-harness

# Verify version
claude-harness --version
# Should show: claude-harness v3.3.3

# Run with spec - LSP plugins install automatically
claude-harness --spec app.txt --project-dir ./app
```

**Note:** Make sure language servers are installed for plugins to auto-install. See [LSP Setup Guide](https://github.com/nirmalarya/claude-harness#lsp-setup) for details.

---

**Status:** ✅ READY FOR RELEASE

This feature dramatically improves the developer experience by eliminating manual LSP plugin setup!
