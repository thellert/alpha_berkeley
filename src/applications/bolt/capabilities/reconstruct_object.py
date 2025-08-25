"""
Photogrammetry Scan Execute Capability for BOLT Beamline System.

This capability executes complete photogrammetry scans with multiple projections
in the BOLT imaging beamline. It's used for 3D reconstruction experiments,
complete sample characterization, and research data collection.
"""
from typing import Dict, Any, Optional
import re

from framework.base import (
    BaseCapability, capability_node,
    OrchestratorGuide, OrchestratorExample, PlannedStep,
    ClassifierActions, ClassifierExample, TaskClassifierGuide
)
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.registry import get_registry
from framework.state import AgentState, StateManager
from configs.logger import get_logger
from configs.streaming import get_streamer

from applications.bolt.context_classes import CurrentReconstructObjectContext
from applications.bolt.bolt_api import bolt_api

logger = get_logger("bolt", "reconstruct_object")
registry = get_registry()

@capability_node
class ReconstructObjectCapability(BaseCapability):
    """Execute complete photogrammetry scan with multiple projections in BOLT beamline."""
    
    # Required class attributes for registry configuration
    name = "reconstruct_object"
    description = "Reconstruct object from folder"
    provides = ["RECONSTRUCT_OBJECT"]
    requires = []
    

    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute reconstruction from folder workflow."""
        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "reconstruct_object", state)
        
        try:
            streamer.status("Parsing reconstruction parameters...")

            query = StateManager.get_current_task(state).lower()

            # Extract scan parameters from query
            input_folder = None
            
            # Parse input folder from queries like "reconstruct object in folder BLANK" or "reconstruct object in BLANK"
            if "in folder" in query:
                # Extract text after "in folder"
                match_folder = re.search(r"in folder\s+([^\s]+)", query)
                if match_folder:
                    input_folder = match_folder.group(1)
            elif "in " in query:
                # Extract text after "in " (for "reconstruct object in BLANK")
                match_folder = re.search(r"in\s+([^\s]+)", query)
                if match_folder:
                    input_folder = match_folder.group(1)

            # Set defaults if not specified
            input_folder = input_folder if input_folder is not None else "Default"
            
            # Debug output
            print(f"Extracted input folder: '{input_folder}'")
            print(f"Query was: '{query}'")
            
            streamer.status(f"Starting reconstruction from folder: {input_folder}...")
            
            scan_data = bolt_api.reconstruct_object(input_folder)
            
            # Create context object
            context = CurrentReconstructObjectContext(
                condition=scan_data.condition,
                timestamp=scan_data.timestamp
            )
            
            # Store context in framework state
            context_updates = StateManager.store_context(
                state, 
                registry.context_types.RECONSTRUCT_OBJECT, 
                step.get("context_key"), 
                context
            )
            
            streamer.status("Reconstruction completed successfully!")
            return context_updates
            
        except Exception as e:
            logger.error(f"Reconstruction object error: {e}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify reconstruction object errors for intelligent retry coordination."""

        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                metadata={
                    "user_message": "Beamline communication timeout, retrying...",
                    "technical_details": str(exc)
                }
            )
        elif isinstance(exc, ValueError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                metadata={
                    "user_message": f"Invalid scan parameters: {str(exc)}",
                    "technical_details": str(exc)
                }
            )
        
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "user_message": f"Photogrammetry scan error: {str(exc)}",
                "technical_details": f"Error: {type(exc).__name__}"
            }
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Define retry policy configuration for reconstruction object operations."""

        return {
            "max_attempts": 2,  # Fewer retries for long scans
            "delay_seconds": 2.0,  # Longer delay for beamline recovery
            "backoff_factor": 2.0
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for reconstruction object execution in BOLT beamline."""

        example = OrchestratorExample(
            step=PlannedStep(
                context_key="reconstruct_object",
                capability="reconstruct_object",
                task_objective="Reconstruct object from folder",
                expected_output=registry.context_types.RECONSTRUCT_OBJECT,
                success_criteria="Reconstruction completed with all projections captured",
                inputs=[
                    {"name": "input_folder", "type": "string", "description": "Folder path to save output (optional)"}
                ]      
            ),
            scenario_description="Reconstructing object from folder",
            notes=f"Output stored as {registry.context_types.RECONSTRUCT_OBJECT}. This is a complete experimental procedure."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "reconstruct_object" steps:**
- User requests reconstruction from folder
- For full experimental data collection and research
- When comprehensive sample characterization is needed

**BOLT Beamline Context:**
- Executes reconstruction from folder
- Generates datasets for 3D reconstruction
- Primary experimental capability for research

**Scan Parameters:**
- Input folder: data storage location (optional)

**Output: {registry.context_types.RECONSTRUCT_OBJECT}**
- Contains: reconstruction_parameters
- Available for data analysis and 3D reconstruction

**Typical Workflow Position:**
- After photogrammetry scan is completed
- After test shots to verify setup
- Final step in experimental preparation sequence
- Usually requires prior sample positioning and beam alignment""",
            examples=[example],
            order=4  # Highest priority - main experimental capability
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Provide task classification guidance for executing a reconstruction plan."""
        return TaskClassifierGuide(
            instructions="""Determine if the user wants to EXECUTE a reconstruction object in the BOLT beamline system.

BOLT CONTEXT: This is an imaging beamline for photogrammetry experiments. Users may request:
- Reconstruction from folder
- Full experimental data collection procedures
- Research-grade photogrammetry experiments""",
            examples=[
                ClassifierExample(
                    query="Reconstruct object",
                    result=True,
                    reason="Complete photogrammetry scan request with specific parameters."
                ),
                ClassifierExample(
                    query="Reconstruct object",
                    result=True,
                    reason="Request for computed photogrammetry (CT) scan."
                ),
                ClassifierExample(
                    query="Reconstruct object from folder",
                    result=True,
                    reason="Complete photogrammetry experiment request."
                ),
                ClassifierExample(
                    query="Perform a reconstructiom from folder",
                    result=True,
                    reason="3D scanning requires photogrammetry with multiple projections."
                ),
                ClassifierExample(
                    query="Reconstruct object from folder",
                    result=True,
                    reason="Full rotation scan is a photogrammetry experiment."
                ),
                ClassifierExample(
                    query="Collect photogrammetry data for reconstruction",
                    result=True,
                    reason="Request for photogrammetry data collection."
                ),
                ClassifierExample(
                    query="Start the photogrammetry experiment",
                    result=True,
                    reason="Photogrammetry in this context refers to photogrammetry scanning."
                ),
                ClassifierExample(
                    query="Take a single image",
                    result=False,
                    reason="This is a single image request, not a multi-projection scan."
                ),
                ClassifierExample(
                    query="Move the motor to 45 degrees",
                    result=False,
                    reason="This is motor positioning, not scan execution."
                ),
                ClassifierExample(
                    query="What is the current motor angle?",
                    result=False,
                    reason="This is a position read request, not scan execution."
                ),
                ClassifierExample(
                    query="Take a test shot",
                    result=False,
                    reason="Test shot is single image capture, not complete scan."
                ),
                ClassifierExample(
                    query="What tools do you have?",
                    result=False,
                    reason="Request is for tool information, not scan execution."
                ),
            ],
            actions_if_true=ClassifierActions()
        )