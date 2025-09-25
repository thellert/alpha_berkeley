"""MCP Server for Launcher Service

This module provides an MCP (Model Context Protocol) server interface
for the launcher service, enabling external tools and clients to access
launcher functionality through a standardized protocol.

The MCP server exposes launcher capabilities as tools that can be called
by any MCP-compatible client, making the launcher service available
beyond the framework's internal usage.

.. note::
   The MCP server is optional and only needed for external integration.
   The main launcher service works independently of MCP.

.. seealso::
   :class:`LauncherMCPServer` : Main MCP server implementation
   :mod:`framework.services.launcher` : Core launcher service
"""

from .server import LauncherMCPServer

__all__ = ["LauncherMCPServer"]
