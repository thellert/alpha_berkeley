import logging
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from mem0 import Memory
import asyncio
import json
import os
import sys

from utils import get_mem0_client

load_dotenv()

# Configure logging to write to stderr
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("mem0_mcp_server")

# Default user ID for memory operations
DEFAULT_USER_ID = "user"

# Create a dataclass for our application context
@dataclass
class Mem0Context:
    """Context for the Mem0 MCP server."""
    mem0_client: Memory

@asynccontextmanager
async def mem0_lifespan(server: FastMCP) -> AsyncIterator[Mem0Context]:
    """
    Manages the Mem0 client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Mem0Context: The context containing the Mem0 client
    """
    # Create and return the Memory client with the helper function in utils.py
    mem0_client = get_mem0_client()
    
    try:
        yield Mem0Context(mem0_client=mem0_client)
    finally:
        # No explicit cleanup needed for the Mem0 client
        pass

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0",
    description="MCP server for long term memory storage and retrieval with Mem0",
    lifespan=mem0_lifespan,
    host=os.getenv("HOST", "localhost"),
    port=os.getenv("PORT", "8050")
)        

@mcp.tool()
async def save_memory(ctx: Context, text: str) -> str:
    """Save ALS-related information to long-term memory.

    This tool stores ALS-specific information such as:
    - Personal preferences regarding ALS machine interfaces, displays, and tools
    - Factual information about the ALS accelerator, beamlines, and components
    - Operational procedures and workflows
    - Machine performance observations and patterns

    The content will be processed and indexed for later retrieval through semantic search.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        text: The ALS-related content to store in memory, including any relevant details and context
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID)
        return f"Successfully saved memory: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory: {text}"
    except Exception as e:
        logger.error(f"Error saving memory: {str(e)}")
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories(ctx: Context) -> str:
    """Get all stored ALS-related memories.
    
    Call this tool when you need complete context of all previously stored ALS information,
    including machine preferences, operational procedures, and historical observations.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client

    Returns a JSON formatted list of all stored memories, including when they were created
    and their content. Results are paginated with a default of 50 items per page.
    """
    logger.info("[get_all_memories] Tool execution started.")
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        logger.info("[get_all_memories] Calling mem0_client.get_all().")
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        # Note: Be careful with logging potentially large 'memories' object directly if it can be huge.
        # Consider logging its type or length first if concerned.
        logger.debug(f"[get_all_memories] Raw result from mem0_client.get_all() (type: {type(memories)}).")


        if isinstance(memories, dict) and "results" in memories:
            logger.debug("[get_all_memories] Processing 'results' field from dict.")
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            logger.debug("[get_all_memories] Processing memories directly (not a dict with 'results').")
            flattened_memories = memories
            
        result = json.dumps(flattened_memories, indent=2)
        # Log only a snippet of the result if it can be very large
        log_result_snippet = result[:500] + "..." if len(result) > 500 else result
        logger.debug(f"[get_all_memories] JSON serialized result: {log_result_snippet}")
        
        # If the result is empty or just "[]", return a more informative message
        if result == "[]" or not result:
            final_response = "No memories found in storage. Try adding memories first using save_memory."
            logger.info(f"[get_all_memories] Returning informative message: {final_response}")
            return final_response
            
        logger.info(f"[get_all_memories] Attempting to return successful result (snippet): {log_result_snippet}")
        return result
    except Exception as e:
        # Use logger.exception to automatically include traceback information
        logger.exception(f"[get_all_memories] Exception caught during execution.")
        error_msg = f"Error retrieving memories: {str(e)}"
        logger.info(f"[get_all_memories] Returning error message: {error_msg}")
        return error_msg
    finally:
        logger.info("[get_all_memories] Tool execution finished.")

@mcp.tool()
async def search_memories(ctx: Context, query: str, limit: int = 3) -> str:
    """Search ALS-related memories using semantic search.

    IMPORTANT: This tool should ALWAYS be called when any questions are asked about the Advanced Light Source,
    regardless of the specific topic. This ensures that all relevant historical information and preferences
    are considered before providing any response about ALS operations, configuration, or procedures.

    This tool searches for relevant ALS information such as:
    - Machine configuration preferences
    - Beamline operational procedures
    - Historical performance patterns
    - Component-specific information
    - User interface preferences

    Results are ranked by relevance to your query. Always search memories before making
    decisions to ensure you leverage existing ALS knowledge.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        query: Search query string describing what you're looking for. Can be natural language.
        limit: Maximum number of results to return (default: 3)
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=limit)
        logger.debug(f"search_memories raw result for query '{query}': {memories}")
        
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
            
        result = json.dumps(flattened_memories, indent=2)
        logger.debug(f"search_memories returning: {result}")
        
        # If the result is empty or just "[]", return a more informative message
        if result == "[]" or not result:
            return f"No memories found matching the query: '{query}'"
            
        return result
    except Exception as e:
        error_msg = f"Error searching memories: {str(e)}"
        logger.error(f"search_memories error: {error_msg}")
        return error_msg

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
        logger.error(f"Error running MCP server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
