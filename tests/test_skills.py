#!/usr/bin/env python3
"""
Test Skills Integration

Verifies that skills are discovered and loaded correctly.
"""

from pathlib import Path

from skills_manager import SkillsManager


def test_skills_discovery():
    """Test that skills are discovered from harness directory."""
    print("Testing Skills Discovery")
    print("=" * 60)

    # Create skills manager for a test project
    test_project = Path("/tmp/test-project")
    manager = SkillsManager(test_project, mode="greenfield")

    # Discover skills
    discovered = manager.discover_skills()

    print(f"\n✓ Discovered {len(discovered)} skills:")
    for name, path in discovered.items():
        print(f"  - {name}: {path}")

    # Check that our 4 skills exist
    expected_skills = ["puppeteer-testing", "code-quality", "harness-patterns", "project-patterns"]

    print("\n✓ Checking for expected skills:")
    for skill in expected_skills:
        if skill in discovered:
            print(f"  ✓ {skill} found")
        else:
            print(f"  ✗ {skill} NOT FOUND")

    return discovered


def test_mode_specific_loading():
    """Test that mode-specific skills are loaded correctly."""
    print("\n\nTesting Mode-Specific Loading")
    print("=" * 60)

    test_project = Path("/tmp/test-project")

    for mode in ["greenfield", "enhancement", "backlog"]:
        manager = SkillsManager(test_project, mode=mode)
        skills = manager.load_skills_for_mode()

        print(f"\n✓ {mode.upper()} mode:")
        print(f"  Skills loaded: {len(skills)}")
        for skill in skills:
            print(f"    - {skill['name']}: {skill['description'][:60]}...")


def test_skill_metadata():
    """Test that skill metadata is loaded correctly."""
    print("\n\nTesting Skill Metadata")
    print("=" * 60)

    test_project = Path("/tmp/test-project")
    manager = SkillsManager(test_project, mode="greenfield")

    discovered = manager.discover_skills()

    for skill_name, skill_path in discovered.items():
        metadata = manager._load_skill_metadata(skill_path)
        if metadata:
            print(f"\n✓ {skill_name}:")
            print(f"  Name: {metadata.get('name')}")
            print(f"  Description: {metadata.get('description')[:80]}...")
        else:
            print(f"\n✗ {skill_name}: Failed to load metadata")


if __name__ == "__main__":
    print("Claude-Harness Skills Integration Test")
    print("=" * 60)

    try:
        discovered = test_skills_discovery()
        test_mode_specific_loading()
        test_skill_metadata()

        print("\n\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
