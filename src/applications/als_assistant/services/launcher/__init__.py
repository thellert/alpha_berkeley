"""Launcher Service - Cross-Network Application Launching

This service provides LangGraph-native application launching capabilities for
environments where the agent runs on a different machine than where GUI applications
need to be launched (e.g., agent in container, applications on user's desktop).

Key Features:
    - Natural language to application launch commands
    - Cross-network execution via URI scheme
    - Support for Phoebus panels and Data Browser
    - LangGraph-native with full streaming and checkpointing
    - MCP server for external integration

Architecture:
    - Service: LangGraph workflow for command generation
    - Capability: Integration wrapper for als_assistant
    - MCP Server: External tool interface
    - URI Handler: Desktop integration (preserved from legacy)

.. note::
   This service generates launch URIs that are handled by desktop URI handlers.
   The actual command execution happens on the user's machine for security.

.. seealso::
   :class:`LauncherService` : Main LangGraph service
   :class:`LauncherCapability` : Capability wrapper
   :mod:`framework.services.launcher.mcp` : MCP server implementation
"""

from .service import LauncherService
from .models import (
    LauncherServiceRequest,
    LauncherServiceResult,
    ExecutableCommand
)

__all__ = [
    "LauncherService",
    "LauncherServiceRequest", 
    "LauncherServiceResult",
    "ExecutableCommand"
]
