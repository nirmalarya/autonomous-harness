#!/usr/bin/env python3
"""Setup configuration for claude-harness."""

from setuptools import setup, find_packages
from pathlib import Path

# Read VERSION file
version_file = Path(__file__).parent / "VERSION"
version = version_file.read_text().strip()

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text()

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = [
    line.strip()
    for line in requirements_file.read_text().splitlines()
    if line.strip() and not line.startswith("#")
]

setup(
    name="claude-harness",
    version=version,
    description="Production-ready autonomous coding harness using Claude Code SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nirmalarya",
    author_email="hello@nirmalarya.com",
    url="https://github.com/nirmalarya/claude-harness",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "specs", "venv", "path"]),
    py_modules=[
        "agent",
        "autonomous_agent",
        "client",
        "error_handler",
        "loop_detector",
        "lsp_plugins",
        "output_formatter",
        "progress",
        "prompts",
        "retry_manager",
        "security",
        "setup_mcp",
        "skills_manager",
    ],
    package_data={
        "prompts": ["*.md", "*.txt"],
        "harness_data": [".claude/skills/**/*.md"],
        "": ["VERSION"],
    },
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "claude-harness=autonomous_agent:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="claude autonomous coding agent ai sdk",
    project_urls={
        "Documentation": "https://github.com/nirmalarya/claude-harness/blob/main/README.md",
        "Source": "https://github.com/nirmalarya/claude-harness",
        "Tracker": "https://github.com/nirmalarya/claude-harness/issues",
    },
)
