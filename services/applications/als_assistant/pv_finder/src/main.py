"""FastMCP Server for Advanced Light Source PV Finder Service.

This module provides a Model Context Protocol (MCP) server for the PV (Process Variable)
Finder service, which helps users locate and identify process variables in the
Advanced Light Source control system. The server exposes PV finding functionality
as standardized MCP tools for integration with AI agents and LLM applications.

The PV Finder service specializes in:
- Interpreting natural language queries about ALS control system components
- Mapping user requests to specific process variable addresses
- Providing context and descriptions for identified PVs
- Supporting complex queries about accelerator subsystems and instrumentation

Key Features:
    - MCP tool interface for standardized AI integration
    - Natural language processing for PV identification
    - Integration with ALS control system knowledge base
    - Comprehensive error handling and logging
    - Configurable transport protocols (stdio/SSE)
    - NLTK resource initialization for text processing

Architecture:
    The server acts as an MCP protocol adapter for the underlying PV Finder agent,
    which utilizes advanced language models and domain-specific knowledge to
    interpret queries and identify relevant process variables in the ALS control system.

Dependencies:
    - FastMCP for MCP server framework
    - ALS Assistant PV Finder agent for core functionality
    - NLTK for natural language processing
    - Asyncio for asynchronous operations

Usage:
    Run as a standalone MCP server supporting both stdio and SSE transport protocols.
    The server automatically initializes NLTK resources and provides PV finding
    capabilities through the run_pv_finder MCP tool.

    Example MCP tool calls:
        run_pv_finder("What is the beam current PV?")
        run_pv_finder("Show me storage ring lifetime PVs")

.. note::
   This server requires access to the ALS Assistant application modules and
   proper configuration of the underlying PV Finder agent components.

.. seealso::
   :mod:`applications.als_assistant.services.pv_finder.agent` : Core PV finder functionality
   :class:`FastMCP` : MCP server framework
"""

from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Ensure the repository src is importable for application modules
# Default mount path for repo src inside container is /repo/src (set in docker-compose)
REPO_SRC = os.getenv("REPO_SRC", "/repo/src")
if REPO_SRC and os.path.isdir(REPO_SRC) and REPO_SRC not in sys.path:
    sys.path.insert(0, REPO_SRC)

# Also add this service's src to sys.path for local runs
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_SRC = CURRENT_DIR
if SERVICE_SRC and SERVICE_SRC not in sys.path:
    sys.path.insert(0, SERVICE_SRC)

# Import the PV finder agent from the application package
from applications.als_assistant.services.pv_finder.agent import run_pv_finder_graph
from applications.als_assistant.services.pv_finder.util import initialize_nltk_resources

initialize_nltk_resources()


# Create a dataclass for our application context
@dataclass
class AppContext:
    """Context for the PV Finder MCP server."""
    debug: bool = False

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manages the application lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        AppContext: The context containing debug setting
    """
    try:
        yield
    finally:
        pass

# Initialize FastMCP server
mcp = FastMCP(
    "[MCP] PV Finder",
    lifespan=app_lifespan,
    host=os.getenv("HOST", "localhost"),
    port=int(os.getenv("PORT", "8051"))
)        

@mcp.tool()
async def run_pv_finder(query: str) -> Dict[str, Any]:
    """
    Send a query to the PV Finder Agent to handle queries about the ALS control system.
    
    Use this tool when you need a PV address.

    Args:
        query: The user's query about the ALS control system
        
    Returns:
        JSON-serializable dict from the PV finder agent with fields {"pvs": [...], "description": "..."}
    """
    logger.debug("Entered run_pv_finder function.")
    try:
        result = await run_pv_finder_graph(user_query=query)
        logger.debug("pv_finder returned.")
        # Normalize to dict for MCP response
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if isinstance(result, dict):
            return result
        # Fallback best-effort
        return {"pvs": getattr(result, "pvs", []), "description": getattr(result, "description", "")}
    except Exception as e:
        logger.error(f"Exception in run_pv_finder: {e}")
        return {"pvs": [], "description": f"Error in run_pv_finder: {str(e)}"}

async def main():
    transport = os.getenv("TRANSPORT", "stdio")  # Default to stdio
    try:
        if transport == 'stdio':
            # Run the MCP server with stdio transport
            await mcp.run_stdio_async()
        else:
            # Run the MCP server with sse transport
            await mcp.run_sse_async()
    except Exception as e:
        print(f"Error running MCP server: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 