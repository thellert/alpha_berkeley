"""
PV Address Finding Capability

This capability searches for Process Variable addresses based on user descriptions.
It helps users find the correct PV names when they know what they want to measure
but don't know the exact EPICS address.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import json
import asyncio
import textwrap

if TYPE_CHECKING:
    from framework.state import AgentState

# Framework imports
from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.planning import PlannedStep
from framework.base.examples import OrchestratorGuide, OrchestratorExample, TaskClassifierGuide, ClassifierExample, ClassifierActions
from framework.state import StateManager
from framework.registry import get_registry

# Application imports
from applications.als_assistant.context_classes import PVAddresses
from applications.als_assistant.services.pv_finder.agent import run_pv_finder_graph
from applications.als_assistant.services.pv_finder.core import PVSearchResult

# Model and configuration
from framework.models import get_chat_completion
from configs.config import get_model_config
from configs.streaming import get_streamer
from configs.logger import get_logger

logger = get_logger("als_assistant", "pv_address_finding")


registry = get_registry()

# ===================================================================
# PV Address Finding Errors
# ===================================================================

class PVAddressError(Exception):
    """Base class for all PV address finding errors."""
    pass

class PVAddressNotFoundError(PVAddressError):
    """Raised when no PV addresses can be found for the given query."""
    pass

class PVFinderServiceError(PVAddressError):
    """Raised when the PV finder service is unavailable or fails."""
    pass

# ===================================================================
# PV Address Extraction Logic
# ===================================================================

from pydantic import BaseModel

class PVExtractionResult(BaseModel):
    """Result from PV address extraction."""
    has_explicit_pv: bool
    pv_addresses: List[str]
    needs_pv_finder: bool

async def extract_pv_addresses_from_query(user_query: str) -> PVExtractionResult:
    """
    Use a lightweight LLM to determine if the user query contains explicit PV addresses
    and extract them if present.
    """
    system_prompt = textwrap.dedent("""
        You are a PV address extraction assistant. Your job is to identify if a user query contains explicit EPICS Process Variable (PV) addresses and extract them.

        PV addresses typically follow patterns like:
        - SR01S___BM1_X____AC00
        - BR1_____TMP_MA__CALC
        - SR:DCCT
        - LINAC:GUN:TEMP
        - Some:PV:Name

        Respond with a JSON object containing:
        {
        "has_explicit_pv": boolean (true if explicit PV addresses found),
        "pv_addresses": [list of extracted PV addresses],
        "needs_pv_finder": boolean (true if natural language search is needed)
        }

        Examples:
        User: "What is the 'SR:DCCT' PV reading right now?"
        Response: {"has_explicit_pv": true, "pv_addresses": ["SR:DCCT"], "needs_pv_finder": false}

        User: "Get the value of BR1_____TMP_MA__CALC"
        Response: {"has_explicit_pv": true, "pv_addresses": ["BR1_____TMP_MA__CALC"], "needs_pv_finder": false}

        User: "What is the beam current?"
        Response: {"has_explicit_pv": false, "pv_addresses": [], "needs_pv_finder": true}

        User: "Read values for 'PV1:TEST' and find beam position PVs"
        Response: {"has_explicit_pv": true, "pv_addresses": ["PV1:TEST"], "needs_pv_finder": true}

        Respond ONLY with the JSON object.
        """)

    try:
        # Use LangGraph configuration for model access
        model_config = get_model_config("als_assistant", "pv_finder", "keyword")
        
        response = await asyncio.to_thread(
            get_chat_completion,
            model_config=model_config,
            message=f"{system_prompt}\n\nUser query: {user_query}",
            output_model=PVExtractionResult,
        )
        
        if isinstance(response, PVExtractionResult):
            return response
        else:
            logger.warning(f"PV extraction did not return expected type, got: {type(response)}")
            return PVExtractionResult(has_explicit_pv=False, pv_addresses=[], needs_pv_finder=True)
            
    except Exception as e:
        logger.error(f"Error during PV address extraction: {e}")
        # Fallback to PV finder on error
        return PVExtractionResult(has_explicit_pv=False, pv_addresses=[], needs_pv_finder=True)

# ===================================================================
# Capability Implementation
# ===================================================================

@capability_node
class PVAddressFindingCapability(BaseCapability):
    """PV address finding capability for resolving descriptions to PV addresses."""
    
    name = "pv_address_finding"
    description = "Find Process Variable addresses based on descriptions or search terms, or extract explicit PV addresses from user queries"
    provides = ["PV_ADDRESSES"]
    requires = []
    
    @staticmethod
    async def execute(
        state: AgentState, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Enhanced PV address finding that handles both explicit PV extraction
        and natural language PV finding.
        """
        
        # Define streaming helper here for step awareness
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        search_query = step.get('task_objective', 'unknown')
        
        streamer = get_streamer("als_assistant", "pv_address_finding", state)
        
        logger.info(f"Starting PV address finding for task: {search_query}")
        streamer.status("Finding PV addresses...")
        
        logger.debug(f"PV address search for task: '{search_query}'")
        streamer.status("Extracting explicit PV addresses...")
        
        # First, try to extract explicit PV addresses from the task objective
        extraction_result = await extract_pv_addresses_from_query(search_query)
        
        logger.debug(f"PV extraction result for task '{search_query}': {extraction_result}")
        
        streamer.status("Processing PV search results...")
                
        if extraction_result.has_explicit_pv and not extraction_result.needs_pv_finder:
            # User provided explicit PV addresses, use them directly
            explicit_pvs = [pv.strip() for pv in extraction_result.pv_addresses if pv.strip()]
            response = PVSearchResult(
                pvs=explicit_pvs,
                description=f"Extracted PV addresses from task: {', '.join(explicit_pvs)}"
            )
            logger.info(f"Using explicit PV addresses: {explicit_pvs}")
        else:
            # Use the PV finder graph with focused search query
            streamer.status("Searching PV database...")
            
            try:
                response = await run_pv_finder_graph(user_query=search_query)
            except Exception as e:
                error_msg = f"PV finder service failed for query '{search_query}': {str(e)}"
                logger.error(error_msg)
                raise PVFinderServiceError(error_msg) from e
            
            # If we also found explicit PVs, add them to the result
            if extraction_result.has_explicit_pv:
                # Strip whitespace from both explicit and searched PVs
                explicit_pvs = [pv.strip() for pv in extraction_result.pv_addresses if pv.strip()]
                searched_pvs = [pv.strip() for pv in response.pvs if pv.strip()]
                all_pvs = list(set(explicit_pvs + searched_pvs))
                response = PVSearchResult(
                    pvs=all_pvs,
                    description=f"Combined explicit and searched PVs for task '{search_query}': {response.description}"
                )
                
        logger.info(f"PV address finding completed for task: '{search_query}' - found {len(response.pvs)} PVs")
        logger.debug(f"PV Finder response: {json.dumps(response.model_dump(), indent=2)}")
        
        streamer.status("Creating PV context...")
        
        # Convert service layer response to framework context
        cleaned_pvs = [pv.strip() for pv in response.pvs if pv.strip()]
        
        # Check if no PVs were found and raise appropriate error for re-planning
        if not cleaned_pvs:
            # Use the detailed description from PV finder response, which may contain validation errors
            detailed_description = response.description if response.description else "This likely indicates the search terms need refinement or the requested PVs don't exist in the database."
            error_msg = f"No PV addresses found for query: '{search_query}'. {detailed_description}"
            logger.warning(f"PV address not found: {error_msg}")
            raise PVAddressNotFoundError(error_msg)
        
        # Create framework context object
        pv_finder_context = PVAddresses(
            pvs=cleaned_pvs,
            description=response.description,
        )
        
        # Store context using StateManager
        state_updates = StateManager.store_context(
            state, 
            registry.context_types.PV_ADDRESSES, 
            step.get("context_key"), 
            pv_finder_context
        )
        
        streamer.status("PV address finding complete")
        
        return state_updates
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """PV address finding error classification with defensive approach."""
        
        if isinstance(exc, PVAddressNotFoundError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"No PV addresses found: {str(exc)}",
                metadata={
                    "technical_details": str(exc),
                    "replanning_reason": f"PV search failed to find matches: {exc}",
                    "suggestions": [
                        "Try refining the search terms to be more specific",
                        "Check if the requested PVs exist in the system",
                        "Consider using different keywords or system names",
                    ]
                }
            )
        
        elif isinstance(exc, PVFinderServiceError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"PV finder service unavailable: {str(exc)}",
                metadata={
                    "technical_details": str(exc),
                    "safety_abort_reason": f"PV finder service failure: {exc}",
                    "suggestions": [
                        "Check if the PV finder service is running and accessible",
                        "Verify network connectivity to PV database systems",
                        "Contact system administrator if the service appears down",
                    ]
                }
            )
    
        else:
            # Default: critical for unknown errors (defensive approach)
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Unexpected error in PV address finding: {exc}",
                metadata={
                    "technical_details": str(exc),
                    "safety_abort_reason": f"Unhandled PV address finding error: {exc}"
                }
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for PV address finding."""
        
        # Define structured examples
        natural_language_example = OrchestratorExample(
            step=PlannedStep(
                context_key="beam_current_pvs",
                capability="pv_address_finding",
                task_objective="Find PV addresses for beam current measurement",
                expected_output="PV_ADDRESSES",
                success_criteria="Relevant PV addresses found and validated",
                inputs=[]
            ),
            scenario_description="Natural language search for measurement types",
            notes="Output stored under PV_ADDRESSES context type."
        )
        
        explicit_pv_example = OrchestratorExample(
            step=PlannedStep(
                context_key="validated_pvs",
                capability="pv_address_finding",
                task_objective="Extract and validate PV address 'SR:BSC:HLC:ok' mentioned in the user query",
                expected_output="PV_ADDRESSES",
                success_criteria="PV addresses extracted and validated",
                inputs=[]
            ),
            scenario_description="Extraction of explicit PV addresses from task objective",
            notes="Output stored under PV_ADDRESSES context type. Processes the task_objective to find explicit PV names like 'EPICS:DCCT' or 'BR1_____TMP_MA__CALC'"
        )
        
        system_location_example = OrchestratorExample(
            step=PlannedStep(
                context_key="epu_gap_pvs",
                capability="pv_address_finding",
                task_objective="Find PV addresses for booster ring quadrupole readback values in all sectors",
                expected_output="PV_ADDRESSES",
                success_criteria="System-specific PV addresses located",
                inputs=[]
            ),
            scenario_description="System and location-based PV discovery",
            notes="Output stored under PV_ADDRESSES context type. The task_objective contains a focused, specific description that enables targeted PV search through natural language processing."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent("""
                **When to plan "pv_address_finding" steps:**
                - When the user mentions hardware, measurements, sensors, or devices without providing specific PV addresses
                - When fuzzy or descriptive names need to be resolved to exact PV addresses
                - When users provide explicit PV addresses that need to be extracted and validated
                - As a prerequisite step before PV value retrieval or data analysis
                - When users reference systems or locations but not complete PV names

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "beam_current_pvs", "validated_pvs")
                - task_objective: The specific and self-contained pv address search task to perform
                
                **Output: PV_ADDRESSES**
                - Contains: List of PV addresses with description
                - Available to downstream steps via context system

                **Dependencies and sequencing:**
                - This step typically comes first when PV addresses are needed
                - Results feed into subsequent "pv_value_retrieval" or "get_archiver_data" steps
                - May require user clarification if multiple matches are found

                ALWAYS plan this step when any PV-related operations are needed, regardless of whether 
                the user provides explicit PV addresses or natural language descriptions.
                """),
            examples=[natural_language_example, explicit_pv_example, system_location_example],
            priority=1  # Should come early in the prompt ordering
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for PV address finding."""
        
        return TaskClassifierGuide(
            instructions="Determine if the task involves finding, extracting, or identifying PV addresses. This applies if the user is searching for PVs based on descriptions, OR if they provide explicit PV addresses that need to be extracted, OR if they need any PV-related operations.",
            examples=[
                ClassifierExample(
                    query="Which tools do you have?", 
                    result=False, 
                    reason="This is a question about the AI's capabilities."
                ),
                ClassifierExample(
                    query="Find PVs related to booster BPMs.", 
                    result=True, 
                    reason="The query asks to find PVs based on a description."
                ),
                ClassifierExample(
                    query="Get the value of BR1_____TMP_MA__CALC.", 
                    result=True, 
                    reason="The query provides an explicit PV name that needs to be extracted before value retrieval."
                ),
                ClassifierExample(
                    query="I need the PV for the linac gun temperature.", 
                    result=True, 
                    reason="The query asks to find a PV based on a description ('linac gun temperature')."
                ),
                ClassifierExample(
                    query="Can you plot the beam current for the last hour?", 
                    result=True, 
                    reason="The query asks to plot data from the control system, which requires PV address finding first."
                ),
                ClassifierExample(
                    query="What's the beam current right now?", 
                    result=True, 
                    reason="The query asks for a current value without a specific PV address, which requires PV address finding first."
                ),
                ClassifierExample(
                    query="What is the 'SR:DCCT' PV reading right now?", 
                    result=True, 
                    reason="The query contains an explicit PV address 'SR:DCCT' that needs to be extracted."
                ),
                ClassifierExample(
                    query="Read the current value of SR01S___BM1_X____AC00", 
                    result=True, 
                    reason="The query contains an explicit PV address that needs to be extracted before value retrieval."
                ),
                ClassifierExample(
                    query="Can you launch the orbit display application?", 
                    result=False, 
                    reason="The query is about launching an application, not about PVs."
                )
            ],
            actions_if_true=ClassifierActions()
        )

