"""Command-line interface for Osprey Framework.

This package provides the unified CLI interface for the framework,
organizing all commands under a single 'osprey' entry point.

Commands:
    - init: Create new projects from templates
    - deploy: Manage Docker/Podman services
    - chat: Interactive conversation interface
    - export-config: View framework default configuration

Architecture:
    Uses Click for command-line parsing with a group-based structure.
    Each command is implemented in its own module for maintainability.
"""

from .main import cli, main

__all__ = ['cli', 'main']

