---
name: lsp-navigation
description: Code intelligence with Language Server Protocol. Use when exploring codebases, finding definitions, locating references, or understanding code structure. Provides IDE-like navigation (50ms vs 45s with text search).
---

# LSP Code Navigation

Navigate code with IDE-like intelligence using Claude Code's LSP plugins from the official marketplace (v1.0.33+).

## When to Use

- Finding where functions/classes are defined
- Locating all usages of a symbol
- Understanding code structure and dependencies
- Exploring unfamiliar codebases
- Refactoring code safely

## Core LSP Tools

Claude Code provides native LSP tools when `ENABLE_LSP_TOOL=1` is set:

**Available Tools:**
- `LSP` - Language Server Protocol operations (go-to-definition, find-references, hover)

## Basic Workflows

### 1. Go to Definition

Find where a symbol is defined:

```
[Tool: LSP]
Input: {
  "operation": "goToDefinition",
  "filePath": "src/services/UserService.ts",
  "line": 42,
  "character": 15
}
```

**Use Cases:**
- Understanding how a function works
- Finding implementation details
- Tracing code flow

### 2. Find References

Locate all usages of a symbol:

```
[Tool: LSP]
Input: {
  "operation": "findReferences",
  "filePath": "src/models/User.ts",
  "line": 10,
  "character": 14
}
```

**Use Cases:**
- Impact analysis before changes
- Finding all callers of a function
- Understanding dependencies

### 3. Hover Information

Get type info and documentation:

```
[Tool: LSP]
Input: {
  "operation": "hover",
  "filePath": "src/utils/formatDate.ts",
  "line": 25,
  "character": 8
}
```

**Use Cases:**
- Understanding function signatures
- Viewing type information
- Reading inline documentation

### 4. Workspace Symbols

Search for symbols across entire project:

```
[Tool: LSP]
Input: {
  "operation": "workspaceSymbol",
  "filePath": "src/index.ts",
  "line": 1,
  "character": 1
}
```

**Use Cases:**
- Finding classes/functions by name
- Exploring project structure
- Locating specific implementations

## Common Patterns

**Explore Unfamiliar Function:**
```
1. Use hover to see function signature
2. Use goToDefinition to view implementation
3. Use findReferences to see usage examples
```

**Impact Analysis Before Refactoring:**
```
1. Use findReferences to see all usages
2. Check each reference context
3. Plan changes to minimize breakage
```

**Understand Code Flow:**
```
1. Start at entry point (main, index, etc.)
2. Use goToDefinition to follow function calls
3. Build mental model of execution path
```

## Performance Benefits

**Traditional Text Search:**
- Grep through all files: ~45 seconds
- May miss dynamic references
- No type awareness

**LSP Navigation:**
- Instant results: ~50ms
- Precise, type-aware
- Finds all references (including dynamic)

## Installing LSP Plugins

LSP plugins are available from the official Anthropic marketplace.

**Install via CLI:**
```bash
# TypeScript/JavaScript
claude plugin install typescript-lsp@claude-plugins-official

# Python
claude plugin install pyright-lsp@claude-plugins-official

# Go
claude plugin install gopls-lsp@claude-plugins-official

# Rust
claude plugin install rust-analyzer-lsp@claude-plugins-official

# Java
claude plugin install jdtls-lsp@claude-plugins-official

# C/C++
claude plugin install clangd-lsp@claude-plugins-official

# C#
claude plugin install csharp-lsp@claude-plugins-official

# PHP
claude plugin install php-lsp@claude-plugins-official

# Swift
claude plugin install swift-lsp@claude-plugins-official

# Lua
claude plugin install lua-lsp@claude-plugins-official
```

**Install via UI:**
```
1. Type /plugin in Claude Code
2. Go to Discover tab
3. Search for language (e.g., "typescript-lsp")
4. Select and install
```

**Requirements:**
- Claude Code v1.0.33+ (`claude --version`)
- Language server binary installed (e.g., `typescript-language-server`, `pyright-langserver`)

## Language Support

LSP works with 10 languages via official plugins:

| Language   | Plugin              | Server Required              |
|------------|---------------------|------------------------------|
| TypeScript | `typescript-lsp`    | `typescript-language-server` |
| Python     | `pyright-lsp`       | `pyright-langserver`         |
| Go         | `gopls-lsp`         | `gopls`                      |
| Rust       | `rust-analyzer-lsp` | `rust-analyzer`              |
| Java       | `jdtls-lsp`         | `jdtls`                      |
| C/C++      | `clangd-lsp`        | `clangd`                     |
| C#         | `csharp-lsp`        | `csharp-ls`                  |
| PHP        | `php-lsp`           | `intelephense`               |
| Swift      | `swift-lsp`         | `sourcekit-lsp`              |
| Lua        | `lua-lsp`           | `lua-language-server`        |

## Best Practices

**1. Use LSP First**
- Before grepping, try LSP navigation
- Faster and more accurate
- Type-aware results

**2. Combine with Read**
- LSP shows location
- Read shows full context
- Best of both worlds

**3. Verify Language Server Running**
- LSP requires language server installed
- Check `.claude/plugins/lsp/plugin.json` exists
- Verify `ENABLE_LSP_TOOL=1` set

**4. Handle LSP Failures Gracefully**
- If LSP unavailable, fallback to Grep/Read
- Not all file types supported
- Language server may not be installed

## Workflow Examples

**Example 1: Understanding Authentication**
```
Goal: Understand how authentication works

1. Find auth entry point:
   operation: workspaceSymbol, search for "authenticate"

2. Go to definition:
   operation: goToDefinition on authenticate function

3. Find all callers:
   operation: findReferences to see where it's used

4. Check middleware:
   operation: goToDefinition on auth middleware

Result: Complete understanding of auth flow
```

**Example 2: Refactoring API Endpoint**
```
Goal: Rename /users endpoint to /accounts

1. Find endpoint handler:
   operation: workspace Symbol, search for "users"

2. Find all references:
   operation: findReferences on handler function

3. Check each usage:
   Read files with references, plan changes

4. Verify types:
   operation: hover on function params

Result: Safe refactoring plan
```

**Example 3: Debugging Bug**
```
Goal: Find where user.email is set to null

1. Find User class:
   operation: workspaceSymbol, search for "User"

2. Find email property:
   operation: goToDefinition on email property

3. Find all writes:
   operation: findReferences, filter for assignments

4. Check each write location:
   Read context, identify bug

Result: Bug located and fixed
```

## Troubleshooting

**LSP tool not available:**
- Check Claude Code version: `claude --version` (requires v1.0.33+)
- Verify LSP plugin installed: `/plugin` → Installed tab
- Install plugin if missing: `claude plugin install <lang>-lsp@claude-plugins-official`
- Ensure language server binary installed (see table above)

**Plugin installation fails:**
- Check `/plugin` → Errors tab for details
- Verify language server binary in PATH
- Try reinstalling: `/plugin uninstall <name>` then install again

**No results returned:**
- Language server may not be running
- File may not be in workspace
- Symbol may be from external library
- Check plugin status: `/plugin` → Installed tab

**Slow performance:**
- Large workspace may take time to index
- Some language servers slower than others
- Check language server logs in ~/.claude/debug/

## When NOT to Use LSP

**Use Grep instead when:**
- Searching for string literals
- Finding comments
- Language server not available for file type
- Searching across multiple file types

**Use Read instead when:**
- Need to see full file context
- Understanding overall structure
- Language server returns too many results

LSP is powerful for precise, type-aware navigation. Use it first, fallback to Grep/Read when needed.
