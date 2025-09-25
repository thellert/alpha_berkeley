"""
PV Finder Service Implementation

Service layer that coordinates the PV finder agent and provides
the public API. Database access is handled directly by the tools.
"""

import asyncio
from typing import Dict, Any, Optional
from .core import (
    IPVFinderService, 
    PVSearchResult,
    handle_pv_finder_error, 
    ServiceUnavailableError
)
from .examples_loader import example_loader
from .tools import list_systems
from .agent import run_pv_finder_graph
from .util import initialize_nltk_resources

# Use global logger
from configs.logger import get_logger
logger = get_logger("als_assistant", "pv_finder")


# ==============================================================================
# SERVICE IMPLEMENTATION
# ==============================================================================

class PVFinderService(IPVFinderService):
    """Main PV finder service implementation."""
    
    def __init__(
        self,
        example_provider = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.example_provider = example_provider or example_loader
        self.config = config or {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the service and its dependencies."""
        try:
            # Test database connectivity through tools
            await self._run_tool_in_executor(list_systems)
            self._initialized = True
            logger.success("PV Finder service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PV Finder service: {e}", exc_info=True)
            raise ServiceUnavailableError(f"Service initialization failed: {str(e)}")
    
    async def _run_tool_in_executor(self, tool_func, *args):
        """Run a synchronous tool function in an executor."""
        return await asyncio.get_event_loop().run_in_executor(None, tool_func, *args)
    
    async def find_pvs(self, query: str) -> PVSearchResult:
        """Find PVs based on natural language query."""
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.key_info(f"Processing PV finder query: {query}")
            result = await run_pv_finder_graph(query)
            logger.success(f"Found {len(result.pvs)} PVs for query: {query}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}", exc_info=True)
            error = handle_pv_finder_error(e)
            
            # Return error response instead of raising
            return PVSearchResult(
                pvs=[],
                description=f"Error processing query: {error.message}"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health and dependencies."""
        health_status = {
            "service": "pv_finder",
            "status": "unknown",
            "checks": {}
        }
        
        try:
            # Check database connectivity through tools
            systems = await self._run_tool_in_executor(list_systems)
            health_status["checks"]["database"] = {
                "status": "healthy",
                "systems_count": len(systems)
            }
            
            # Check example provider
            examples_stats = self.example_provider.get_statistics()
            health_status["checks"]["examples"] = {
                "status": "healthy",
                **examples_stats
            }
            
            # Check NLTK resources
            try:
                initialize_nltk_resources()
                health_status["checks"]["nltk"] = {"status": "healthy"}
            except Exception as e:
                health_status["checks"]["nltk"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # Overall status
            all_healthy = all(
                check.get("status") == "healthy" 
                for check in health_status["checks"].values()
            )
            health_status["status"] = "healthy" if all_healthy else "degraded"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            
        return health_status


