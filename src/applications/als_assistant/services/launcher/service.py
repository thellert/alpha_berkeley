"""Launcher Service - Simplified Implementation

Main service class that orchestrates application launching using direct method calls.
No LangGraph subgraph needed - keeps it simple and fast.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List

from .models import (
    LauncherServiceRequest, 
    LauncherServiceResult,
    ExecutableCommand
)
from .utils import (
    create_launch_uri_from_executable_command,
    create_advanced_databrowser_command,
    PlotConfig,
    PVConfig
)
from configs.logger import get_logger

# Import MCP client for PV finder service
from fastmcp import Client
import json
import uuid

# Import model completion for LLM-powered plot generation
from framework.models import get_chat_completion
from configs.config import get_full_configuration

logger = get_logger("framework", "launcher")


class LauncherService:
    """Simplified launcher service for Data Browser launching.
    
    This service provides a production-ready workflow for converting
    natural language queries into Phoebus Data Browser launch commands
    for live monitoring applications.
    
    Key Features:
        - Direct Data Browser launching
        - PV resolution via MCP server when needed
        - LLM-powered plot configuration generation
        - URI generation for cross-network execution
        - Direct method calls (no LangGraph overhead)
    """
    
    def __init__(self):
        """Initialize the launcher service."""
        # Get Phoebus executable from configuration system
        config = get_full_configuration()
        
        # Try to get from als_assistant external_services configuration
        als_assistant_config = config.get('applications', {}).get('als_assistant', {})
        external_services = als_assistant_config.get('external_services', {})
        phoebus_config = external_services.get('phoebus', {})
        
        self.phoebus_executable = phoebus_config.get('executable_path')
        
        # Fallback to environment variable if not in config
        if not self.phoebus_executable:
            self.phoebus_executable = os.getenv("PATH_TO_PHOEBUS_EXECUTABLE")
        
        if not self.phoebus_executable:
            raise ValueError(
                "Phoebus executable path not configured. Please set either:\n"
                "1. PATH_TO_PHOEBUS_EXECUTABLE environment variable, or\n"
                "2. applications.als_assistant.external_services.phoebus.executable_path in config"
            )
    
    async def execute(self, request: LauncherServiceRequest) -> LauncherServiceResult:
        """Execute a launcher request using direct method calls.
        
        Args:
            request: The launcher service request
            
        Returns:
            LauncherServiceResult with success status and launch URI or error
        """
        try:
            # Build Data Browser command
            command = await self._build_databrowser_command(request)
            logger.info(f"Built Data Browser command: {command['name']}")
            
            # Generate launch URI
            name, uri = create_launch_uri_from_executable_command(command)
            result = LauncherServiceResult.success_result(command, uri)
            
            logger.info(f"Generated launch URI for Data Browser: {name}")
            return result
                
        except Exception as e:
            logger.error(f"Launcher service error: {e}", exc_info=True)
            return LauncherServiceResult.error_result(f"Service error: {str(e)}")
    
    
    async def _build_databrowser_command(self, request: LauncherServiceRequest) -> ExecutableCommand:
        """Build a Data Browser command with proper PV resolution."""
        query = request.query
        
        # Check if we have explicit PV addresses from the request
        if request.pv_addresses is not None and len(request.pv_addresses) > 0:
            # Use explicitly provided PVs
            logger.info(f"Using explicit PVs from request: {request.pv_addresses}")
            pvs = request.pv_addresses
        else:
            # Try to resolve PVs using PV finder service
            logger.info(f"No explicit PVs provided, attempting PV finder resolution for: {query}")
            pvs = await self._resolve_pvs_from_query(query)
        
        # Generate plot configuration using LLM
        plot_config = await self._generate_plot_config_with_llm(query, pvs, request.runtime_config)
        return create_advanced_databrowser_command(
            executable_path=self.phoebus_executable,
            plot_config=plot_config
        )
    
    async def _resolve_pvs_from_query(self, query: str) -> List[str]:
        """Resolve PV names from natural language query using PV finder MCP server."""
        
        pv_finder_url = "http://localhost:8051/sse"
        
        try:
            logger.info(f"Connecting to PV finder MCP server at {pv_finder_url}")
            
            async with Client(pv_finder_url) as client:
                # Generate langfuse context similar to the test script
                langfuse_context = {
                    "user_id": f"launcher_service_{uuid.uuid4()}",
                    "session_id": "launcher_pv_resolution",
                    "trace_id": str(uuid.uuid4()),
                    "parent_span_id": str(uuid.uuid4())
                }
                
                # Call the PV finder tool
                result = await client.call_tool("run_pv_finder", {
                    "query": query,
                    "parameters": {
                        "langfuse_context": langfuse_context
                    }
                })
                
                # Parse the result - handle both structured_content and text content
                pvs = []
                
                # First try structured_content if available
                if hasattr(result, 'structured_content') and result.structured_content:
                    structured = result.structured_content
                    if isinstance(structured, dict) and 'result' in structured:
                        result_data = structured['result']
                        if isinstance(result_data, dict) and 'pvs' in result_data:
                            pvs = result_data['pvs']
                            logger.info(f"PV finder MCP server resolved {len(pvs)} PVs from structured_content: {pvs}")
                            return pvs
                
                # Fallback to parsing text content
                if (isinstance(result, list) and len(result) == 1 and 
                    hasattr(result[0], 'type') and result[0].type == 'text' and 
                    hasattr(result[0], 'text')):
                    
                    # Parse JSON response
                    response_data = json.loads(result[0].text)
                    pvs = response_data.get('pvs', [])
                    
                    if pvs:
                        logger.info(f"PV finder MCP server resolved {len(pvs)} PVs from text content: {pvs}")
                        return pvs
                
                logger.info(f"PV finder MCP server could not resolve any PVs for query: {query}")
                logger.debug(f"Result format: {type(result)}, content: {result}")
                return []
                    
        except Exception as e:
            logger.error(f"Error resolving PVs from query '{query}' via MCP server: {e}")
            return []
    
    async def _generate_plot_config_with_llm(self, query: str, pv_names: List[str], runtime_config: Optional[Dict[str, Any]] = None) -> PlotConfig:
        """Generate a PlotConfig using LLM with structured output."""
        logger.info(f"Generating plot configuration with LLM for query: {query}")
        
        # Create system prompt for plot generation
        system_prompt = self._create_plot_generation_prompt(query, pv_names)
        
        try:
            # Extract only the configs we need (avoid LangGraph functions)
            if runtime_config is None:
                raise ValueError("No runtime config provided - launcher service needs model configuration")
            
            # Get model config from runtime config (safely)
            model_configs = runtime_config.get('model_configs', {})
            als_assistant_models = model_configs.get('als_assistant', {})
            llm_config = als_assistant_models.get('launcher', {})
            
            # Get provider config from runtime config (safely)
            provider_configs = runtime_config.get('provider_configs', {})
            provider_config = provider_configs.get('cborg', {})
            
            logger.info(f"DEBUG: LLM config from runtime_config: {llm_config}")
            logger.info(f"DEBUG: Provider config from runtime_config: {provider_config}")
            
            if not llm_config or not llm_config.get('provider'):
                raise ValueError("No valid launcher model config found in runtime_config")
            
            if not provider_config or not provider_config.get('api_key'):
                raise ValueError("No valid cborg provider config found in runtime_config")
            
            # LLM call with structured output
            logger.info("DEBUG: Calling get_chat_completion with configs from runtime_config...")
            
            # Extract individual parameters for get_chat_completion
            provider = llm_config.get('provider')
            model_id = llm_config.get('model_id')
            max_tokens = llm_config.get('max_tokens', 2048)
            base_url = provider_config.get('base_url')
            
            # Pass provider_config directly to get_chat_completion
            plot_config = get_chat_completion(
                message=system_prompt,
                provider=provider,
                model_id=model_id,
                max_tokens=max_tokens,
                base_url=base_url,
                output_model=PlotConfig,
                provider_config=provider_config
            )
            
            if not isinstance(plot_config, PlotConfig):
                raise ValueError(f"LLM returned {type(plot_config)} instead of PlotConfig")
            
            # Ensure PV names match what was resolved
            if len(plot_config.pvs) != len(pv_names):
                logger.warning(f"LLM returned {len(plot_config.pvs)} PVs, expected {len(pv_names)}. Adjusting...")
                # Keep LLM styling but ensure PV names are correct
                for i, pv_name in enumerate(pv_names):
                    if i < len(plot_config.pvs):
                        plot_config.pvs[i].name = pv_name
                    else:
                        # Add missing PVs with default styling
                        plot_config.pvs.append(PVConfig(name=pv_name))
            
            logger.info(f"Generated plot config: '{plot_config.title}' with {len(plot_config.pvs)} PVs and {len(plot_config.annotations)} annotations")
            return plot_config
            
        except Exception as e:
            logger.error(f"LLM plot generation failed: {e}")
            raise
    
    def _create_plot_generation_prompt(self, query: str, pv_names: List[str]) -> str:
        """Create system prompt for LLM plot configuration generation."""
        
        # Default colors for multiple PVs
        default_colors = [
            (0, 100, 200),    # Blue
            (200, 0, 0),      # Red
            (0, 150, 0),      # Green  
            (200, 100, 0),    # Orange
            (150, 0, 150),    # Purple
            (0, 150, 150),    # Teal
            (150, 150, 0),    # Olive
            (100, 100, 100),  # Gray
        ]
        
        pv_list = ", ".join(pv_names) if pv_names else "No PVs provided"
        
        prompt = f"""You are an expert at creating Data Browser plot configurations for accelerator control systems.

User Request: {query}
Resolved PV Names: {pv_list}

Your task is to create a comprehensive PlotConfig that will generate a professional-looking Data Browser plot.

CRITICAL REQUIREMENTS:
1. Create exactly {len(pv_names)} PV configurations, one for each resolved PV name
2. Use the EXACT PV names provided: {pv_names}
3. Choose appropriate trace types, colors, and styling based on the user request
4. Generate a descriptive title based on the user's intent
5. Set appropriate axis names and scaling options

STYLING GUIDELINES:
- For position measurements (BPM) or beam current: Use LINE trace type with distinct colors  
- For temperature/pressure: Use LINE trace type
- For multiple PVs: Use different colors from this palette: {default_colors}
- Use descriptive display names (not just PV names)

TRACE TYPE SELECTION:
- LINE: Good for most measurements, position data, temperatures
- AREA: Good for beam current, power measurements, filled plots
- STEP: Good for discrete state changes
- BARS: Good for discrete values or histograms

COLOR SELECTION:
- Beam current: Blue (0, 100, 200)
- Positions: Red (200, 0, 0) and Green (0, 150, 0) for X/Y
- Temperatures: Orange (200, 100, 0)  
- Pressures: Purple (150, 0, 150)
- Multiple similar PVs: Use palette colors

TIME RANGE:
- Set reasonable time range based on request (default: last 24 hours)
- Use string format like "-24 hours" for start, "now" for end

AXIS CONFIGURATION:
- Use descriptive axis names based on PV types
- Enable auto_scale for most cases
- Use appropriate axis names like "Current (mA)", "Position (mm)", "Temperature (°C)"

Generate a complete PlotConfig with professional styling that matches the user's request. 
"""

        return prompt