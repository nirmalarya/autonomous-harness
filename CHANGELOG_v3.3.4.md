# CHANGELOG - v3.3.4

**Release Date:** January 11, 2026

**Type:** Feature Release (Full LSP Auto-Installation)

---

## ✨ Feature: Auto-Install Language Servers + LSP Plugins

### User Request

> "My point is the harness must install LSP automatically if not installed already."

**100% agreed!** Now claude-harness automatically installs **BOTH** language servers AND LSP plugins.

### What Changed

**v3.3.3 (Previous):**
- ✅ Auto-installed LSP plugins
- ❌ Required manual language server installation

**v3.3.4 (Current):**
- ✅ Auto-installs language servers
- ✅ Auto-installs LSP plugins
- ✅ **Completely zero-setup!**

### Before (v3.3.3)

```bash
❯ claude-harness --spec app.txt --project-dir ./app

ℹ️  LSP plugins skipped (optional - language server not installed):
   - TypeScript, JavaScript
   To enable LSP code intelligence (optional), install language servers:
     • TypeScript, JavaScript: npm install -g typescript-language-server typescript
   Note: The harness works perfectly fine without LSP plugins.
```

**User had to manually:**
```bash
npm install -g typescript-language-server typescript  # Manual step!
```

### After (v3.3.4)

```bash
❯ claude-harness --spec app.txt --project-dir ./app

✅ Auto-installed language servers:
   - TypeScript, JavaScript: typescript-language-server

✅ Auto-installed LSP plugins:
   - typescript-lsp@claude-plugins-official

Sending prompt to Claude Agent SDK...
```

**Fully automatic!** Both server and plugin install without any user intervention.

### How It Works

**1. Detect Languages** (from spec file or project files)
```
Detected: typescript
```

**2. Auto-Install Language Server**
```bash
# Automatically runs:
npm install -g typescript-language-server typescript
```

**3. Verify Installation**
```bash
# Checks that binary exists:
which typescript-language-server
```

**4. Auto-Install LSP Plugin**
```bash
# Automatically runs:
claude plugin install typescript-lsp@claude-plugins-official
```

**5. Continue to Agent**
```
Sending prompt to Claude Agent SDK...
```

### Supported Auto-Installations

**Language servers that auto-install:**
- ✅ **TypeScript/JavaScript**: `npm install -g typescript-language-server typescript`
- ✅ **Python**: `npm install -g pyright`
- ✅ **PHP**: `npm install -g intelephense`
- ✅ **Go**: `go install golang.org/x/tools/gopls@latest`
- ✅ **Rust**: `rustup component add rust-analyzer`

**Language servers requiring manual install:**
- ⚠️ **Java**: Requires JDT.LS setup
- ⚠️ **C/C++**: Install LLVM/Clang from package manager
- ⚠️ **C#**: Requires manual setup
- ⚠️ **Swift**: Included with Xcode
- ⚠️ **Lua**: Requires manual build

### Example Outputs

**Successful auto-installation:**
```
✅ Auto-installed language servers:
   - TypeScript, JavaScript: typescript-language-server

✅ Auto-installed LSP plugins:
   - typescript-lsp@claude-plugins-official
```

**Already installed:**
```
✓ Language server already installed:
   - TypeScript, JavaScript: typescript-language-server

✓ Already installed:
   - typescript-lsp@claude-plugins-official
```

**Installation failed:**
```
❌ Failed to install language servers:
   - TypeScript, JavaScript: npm ERR! EACCES permission denied

   To fix: Run with sudo or fix npm permissions
```

**Manual installation required:**
```
ℹ️  Some language servers require manual installation:
   - Java: See https://github.com/eclipse/eclipse.jdt.ls
   - C/C++: Install LLVM/Clang from your package manager
```

### Technical Details

**New Functions:**

**lsp_plugins.py:346-436** - `auto_install_language_servers()`
- Detects which language servers need installation
- Executes install commands (npm, go, rustup, etc.)
- Verifies installation succeeded
- Returns detailed status per language

**lsp_plugins.py:528-566** - Updated `setup_lsp()`
- Added `auto_install_servers` parameter (default: True)
- Calls server installation before plugin installation
- Returns both server and plugin installation results

**client.py:128-181** - Enhanced output display
- Shows language server installation results
- Shows plugin installation results
- Clear success/failure messages

### Configuration

Auto-installation is **enabled by default**. To disable:

```python
# In client.py
lsp_setup = lsp_manager.setup_lsp(
    auto_install=True,          # Install plugins
    auto_install_servers=False  # But don't install servers
)
```

### Benefits

- ✅ **Zero manual setup** - both servers and plugins install automatically
- ✅ **Works out of the box** - no npm/go/rustup commands needed
- ✅ **Idempotent** - safe to run multiple times
- ✅ **Fast** - installs in parallel during startup
- ✅ **Clear feedback** - know exactly what was installed
- ✅ **Graceful fallback** - works even if installation fails

### Requirements

**For TypeScript/JavaScript:**
- Node.js and npm installed
- Network access for npm registry

**For Python:**
- Node.js and npm installed (pyright is npm package)
- Network access

**For Go:**
- Go toolchain installed
- `$GOPATH/bin` in PATH

**For Rust:**
- Rust toolchain with rustup installed

### Security Considerations

Language servers are installed **globally** using standard package managers:
- npm packages: `~/.npm`
- Go binaries: `$GOPATH/bin`
- Rust components: `~/.rustup`

No sudo/root access required if package managers are properly configured.

### Limitations

1. **Requires package managers** - npm, go, rustup must be installed
2. **Network required** - downloads from registries
3. **Manual install for some** - Java, C/C++, C#, Swift, Lua
4. **Timeout: 2 minutes** - fails if install takes longer

### Future Enhancements

- Add support for more language servers
- Detect and use alternative package managers (yarn, pnpm)
- Cache downloaded servers for offline use
- Progress bars for long installations

---

## 🔧 Files Changed

### Modified

**lsp_plugins.py** (lines 346-566)
- Added `auto_install_language_servers()` - installs npm/go/rust servers
- Updated `setup_lsp()` - added `auto_install_servers` parameter
- Comprehensive error handling and status tracking

**client.py** (lines 128-181)
- Enhanced output to show server installation results
- Separated server and plugin installation messages
- Better error display

**VERSION** (line 1)
- Updated to 3.3.4

**pyproject.toml** (line 7)
- Updated version to 3.3.4

**autonomous_agent.py** (line 128)
- Updated fallback version to 3.3.4

**agent.py** (line 166)
- Updated fallback version to 3.3.4

---

## 📝 Version Info

- **Previous:** v3.3.3
- **Current:** v3.3.4
- **Release Type:** Feature (minor version bump)

---

## ⚡ Upgrade Instructions

```bash
# Upgrade via pip
pip install --upgrade claude-harness

# Verify version
claude-harness --version
# Should show: claude-harness v3.3.4

# Run with spec - EVERYTHING installs automatically!
claude-harness --spec app.txt --project-dir ./app
```

### First Run (TypeScript project, nothing installed):
1. Detects TypeScript from spec
2. Installs typescript-language-server (1-2 min)
3. Installs typescript-lsp plugin (5-10 sec)
4. Starts agent with LSP enabled

### Subsequent Runs:
1. Detects servers already installed
2. Detects plugins already installed
3. Starts agent immediately

---

**Status:** ✅ READY FOR RELEASE

This achieves truly zero-setup LSP integration - exactly what the user requested!
