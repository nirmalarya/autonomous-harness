"""
Skills Manager for claude-harness v3.2.0
========================================

Manages Claude Code Skills - reusable domain knowledge that improves code quality.

Skills are auto-loaded from:
1. Project skills: .claude/skills/ (in project directory)
2. Global skills: ~/.claude/skills/ (user's home directory)

Skills are mode-specific:
- Greenfield: autonomous-testing, code-quality, project-patterns, database-migrations
- Enhancement: code-quality, project-patterns
- Backlog: code-quality, azure-devops-workflow

Architecture:
- Skills are markdown files (SKILL.md) with YAML frontmatter
- Progressive disclosure: SKILL.md + supporting files (patterns.md, examples/, etc.)
- Auto-matched by Claude based on description
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class SkillsManager:
    """
    Manages Claude Code Skills for autonomous coding sessions.

    Responsibilities:
    1. Auto-discover skills from project and global locations
    2. Load mode-specific skills
    3. Provide skills configuration for Claude SDK client
    4. Validate skill structure (SKILL.md exists, valid YAML frontmatter)
    """

    def __init__(self, project_dir: Path, mode: str = "greenfield"):
        """
        Initialize Skills Manager.

        Args:
            project_dir: Project directory (for .claude/skills/)
            mode: Execution mode (greenfield, enhancement, backlog)
        """
        self.project_dir = project_dir
        self.mode = mode

        # Skill directories (in order of precedence)
        self.global_skills_dir = Path.home() / ".claude" / "skills"
        self.project_skills_dir = project_dir / ".claude" / "skills"

        # Harness built-in skills (bundled with claude-harness in harness_data package)
        # Try to import harness_data package to get skills location
        try:
            import harness_data
            harness_data_path = Path(harness_data.__file__).parent
            self.harness_skills_dir = harness_data_path / ".claude" / "skills"
        except (ImportError, AttributeError):
            # Fallback for development (running from source)
            self.harness_skills_dir = Path(__file__).parent / "harness_data" / ".claude" / "skills"

    def get_mode_specific_skills(self) -> List[str]:
        """
        Get recommended skills for this mode.

        Returns:
            List of skill names recommended for this mode
        """
        mode_skills = {
            "greenfield": [
                "puppeteer-testing",      # E2E testing with Puppeteer MCP
                "code-quality",           # Production code standards
                "project-patterns",       # Framework conventions (Next.js, FastAPI, etc.)
                "harness-patterns",       # claude-harness workflow patterns
                "lsp-navigation",         # Code intelligence with LSP
            ],
            "enhancement": [
                "code-quality",           # Maintain existing standards
                "project-patterns",       # Follow existing conventions
                "harness-patterns",       # Workflow patterns
                "lsp-navigation",         # Code navigation with LSP
            ],
            "bugfix": [
                "code-quality",           # Maintain code quality
                "project-patterns",       # Follow existing patterns
                "harness-patterns",       # Workflow patterns
                "lsp-navigation",         # Code navigation with LSP
            ],
            "backlog": [
                "code-quality",           # Production standards
                "project-patterns",       # Codebase conventions
                "harness-patterns",       # Workflow patterns
                "lsp-navigation",         # Code navigation with LSP
            ]
        }

        return mode_skills.get(self.mode, [])

    def discover_skills(self) -> Dict[str, Path]:
        """
        Discover all available skills from all locations.

        Precedence: Project > Global > Harness built-in

        Returns:
            Dict mapping skill name → skill directory path
        """
        discovered = {}

        # 1. Load harness built-in skills (lowest precedence)
        if self.harness_skills_dir.exists():
            for skill_dir in self.harness_skills_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    discovered[skill_dir.name] = skill_dir

        # 2. Load global skills (overrides built-in)
        if self.global_skills_dir.exists():
            for skill_dir in self.global_skills_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    discovered[skill_dir.name] = skill_dir

        # 3. Load project skills (highest precedence)
        if self.project_skills_dir.exists():
            for skill_dir in self.project_skills_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    discovered[skill_dir.name] = skill_dir

        return discovered

    def load_skills_for_mode(self) -> List[Dict]:
        """
        Load skills recommended for current mode.

        Returns:
            List of skill configurations for Claude SDK
        """
        recommended = self.get_mode_specific_skills()
        discovered = self.discover_skills()

        skills_config = []

        for skill_name in recommended:
            if skill_name in discovered:
                skill_path = discovered[skill_name]
                skill_info = self._load_skill_metadata(skill_path)

                if skill_info:
                    skills_config.append({
                        "name": skill_name,
                        "path": str(skill_path),
                        "description": skill_info.get("description", ""),
                        "allowed_tools": skill_info.get("allowed-tools", []),
                    })

        return skills_config

    def _load_skill_metadata(self, skill_path: Path) -> Optional[Dict]:
        """
        Load skill metadata from SKILL.md frontmatter.

        Args:
            skill_path: Path to skill directory

        Returns:
            Dict with skill metadata (name, description, allowed-tools, model)
        """
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            return None

        try:
            content = skill_md.read_text()

            # Extract YAML frontmatter
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not match:
                print(f"Warning: {skill_md} has no YAML frontmatter")
                return None

            frontmatter = yaml.safe_load(match.group(1))

            # Validate required fields
            if "name" not in frontmatter or "description" not in frontmatter:
                print(f"Warning: {skill_md} missing required fields (name, description)")
                return None

            return frontmatter

        except Exception as e:
            print(f"Error loading {skill_md}: {e}")
            return None

    def copy_skills_to_project(self, tech_stack: List[str]) -> None:
        """
        Copy relevant skills to project .claude/skills/ directory.

        Called during initialization to bundle skills with project.

        Args:
            tech_stack: List of technologies detected in spec (e.g., ["nextjs", "python", "postgres"])
        """
        import shutil

        # Ensure project skills directory exists
        self.project_skills_dir.mkdir(parents=True, exist_ok=True)

        # Always copy core skills
        core_skills = ["autonomous-testing", "code-quality"]

        # Add tech-specific skills
        if any(tech in ["nextjs", "react", "typescript"] for tech in tech_stack):
            core_skills.append("nextjs-patterns")

        if any(tech in ["fastapi", "python", "django", "flask"] for tech in tech_stack):
            core_skills.append("python-patterns")

        if any(tech in ["postgres", "mysql", "mongodb", "database"] for tech in tech_stack):
            core_skills.append("database-migrations")

        # Copy skills from harness built-in
        for skill_name in core_skills:
            src = self.harness_skills_dir / skill_name
            dst = self.project_skills_dir / skill_name

            if src.exists() and not dst.exists():
                shutil.copytree(src, dst)
                print(f"   ✓ Copied skill: {skill_name}")

    def get_skills_summary(self) -> str:
        """
        Get human-readable summary of available skills.

        Returns:
            Formatted string listing all available skills
        """
        discovered = self.discover_skills()

        if not discovered:
            return "No skills available"

        lines = ["Available Claude Code Skills:"]
        for skill_name, skill_path in sorted(discovered.items()):
            metadata = self._load_skill_metadata(skill_path)
            if metadata:
                desc = metadata.get("description", "No description")
                # Truncate long descriptions
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                lines.append(f"  - {skill_name}: {desc}")

        return "\n".join(lines)
