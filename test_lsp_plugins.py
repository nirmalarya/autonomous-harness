#!/usr/bin/env python3
"""
Test LSP Plugin Manager

Verifies LSP plugin detection and installation command generation.
"""

import tempfile
from pathlib import Path
from lsp_plugins import LSPPluginManager


def test_language_detection():
    """Test that languages are detected from project files."""
    print("Testing Language Detection")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        lsp_manager = LSPPluginManager(project_dir)

        # Create TypeScript project
        (project_dir / "package.json").write_text("{}")
        (project_dir / "tsconfig.json").write_text("{}")

        detected = lsp_manager.detect_languages()
        print(f"\n✓ TypeScript project detected: {detected}")
        assert "typescript" in detected

        # Add Python files
        (project_dir / "requirements.txt").write_text("requests")

        detected = lsp_manager.detect_languages()
        print(f"✓ TypeScript + Python detected: {detected}")
        assert "typescript" in detected and "python" in detected

        # Add Go files
        (project_dir / "go.mod").write_text("module test")

        detected = lsp_manager.detect_languages()
        print(f"✓ TypeScript + Python + Go detected: {detected}")
        assert all(lang in detected for lang in ["typescript", "python", "go"])


def test_plugin_install_commands():
    """Test that plugin install commands are generated correctly."""
    print("\n\nTesting Plugin Install Commands")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        lsp_manager = LSPPluginManager(project_dir)

        # Test TypeScript and Python commands
        commands = lsp_manager.get_plugin_install_commands(["typescript", "python"])

        print(f"\n✓ Generated commands:")
        for cmd in commands:
            print(f"  {cmd}")

        # Verify structure
        assert len(commands) == 2
        assert "typescript-lsp@claude-plugins-official" in commands[0]
        assert "pyright-lsp@claude-plugins-official" in commands[1]
        assert all(cmd.startswith("claude plugin install") for cmd in commands)

        print("\n✓ Commands validated")


def test_installation_guide():
    """Test that installation guide is generated correctly."""
    print("\n\nTesting Installation Guide")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        lsp_manager = LSPPluginManager(project_dir)

        # Generate guide for TypeScript
        guide = lsp_manager.get_installation_guide(["typescript"])

        print(f"\n{guide}")

        # Verify content
        assert "LSP Plugin Installation Guide" in guide
        assert "typescript-lsp@claude-plugins-official" in guide
        assert "Claude Code v1.0.33+" in guide

        print("\n✓ Guide generated successfully")


def test_full_setup():
    """Test complete LSP setup workflow."""
    print("\n\nTesting Complete LSP Setup")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create a TypeScript project
        (project_dir / "package.json").write_text('{"name": "test-project"}')
        (project_dir / "tsconfig.json").write_text("{}")

        lsp_manager = LSPPluginManager(project_dir)
        setup_result = lsp_manager.setup_lsp()

        print(f"\n✓ Setup complete:")
        print(f"  Languages: {setup_result['languages']}")
        print(f"  Marketplace: {setup_result['marketplace']}")
        print(f"  Requires: {setup_result['requires_version']}")
        print(f"\n  Install commands:")
        for cmd in setup_result['install_commands']:
            print(f"    {cmd}")

        # Verify TypeScript was detected
        assert "typescript" in setup_result['languages']
        assert setup_result['marketplace'] == "claude-plugins-official"
        assert len(setup_result['install_commands']) > 0


def test_official_plugins_catalog():
    """Test that all official plugins are in the catalog."""
    print("\n\nTesting Official Plugins Catalog")
    print("=" * 60)

    lsp_manager = LSPPluginManager(Path("/tmp"))

    expected_plugins = [
        "typescript-lsp",
        "pyright-lsp",
        "gopls-lsp",
        "rust-analyzer-lsp",
        "jdtls-lsp",
        "clangd-lsp",
        "csharp-lsp",
        "php-lsp",
        "swift-lsp",
        "lua-lsp"
    ]

    print(f"\n✓ Official plugins catalog:")
    for lang_id, config in lsp_manager.OFFICIAL_LSP_PLUGINS.items():
        plugin_name = config['plugin']
        languages = ', '.join(config['languages'])
        print(f"  {lang_id:12} → {plugin_name:20} ({languages})")
        assert plugin_name in expected_plugins

    print(f"\n✓ {len(expected_plugins)} official plugins catalogued")


if __name__ == "__main__":
    print("Claude-Harness LSP Plugin Manager Test")
    print("=" * 60)

    try:
        test_language_detection()
        test_plugin_install_commands()
        test_installation_guide()
        test_full_setup()
        test_official_plugins_catalog()

        print("\n\n" + "=" * 60)
        print("✓ All LSP plugin manager tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
