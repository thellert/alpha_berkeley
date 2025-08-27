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

from applications.bolt.context_classes import CurrentRunScanContext
from applications.bolt.bolt_api import bolt_api

logger = get_logger("bolt", "photogrammetry_scan_execute")
registry = get_registry()

@capability_node
class PhotogrammetryScanExecuteCapability(BaseCapability):
    """Execute complete photogrammetry scan with multiple projections in BOLT beamline."""
    
    # Required class attributes for registry configuration
    name = "photogrammetry_scan_execute"
    description = "Execute complete photogrammetry scan with multiple projections"
    provides = ["PHOTOGRAMMETRY_SCAN"]
    requires = []
    
    def extract_scan_params(query: str) -> dict:
        # Lowercase for consistency
        q = query.lower()
        
        start_angle = None
        end_angle = None
        num_projections = None
        output_folder = None

        # Match patterns like "from 0 to 180"
        match_range = re.search(r"from\s+(-?\d+\.?\d*)\s+to\s+(-?\d+\.?\d*)", q)
        if match_range:
            start_angle = float(match_range.group(1))
            end_angle = float(match_range.group(2))

        # Match "with 10 projections"
        match_proj = re.search(r"with\s+(\d+)\s+projections?", q)
        if match_proj:
            num_projections = int(match_proj.group(1))

        # Match "save it to /some/path" or "save to /some/path"
        match_folder = re.search(r"save (?:it )?to\s+([/\w\-\.]+)", q)
        if match_folder:
            output_folder = match_folder.group(1)

        return {
            "start_angle": start_angle,
            "end_angle": end_angle,
            "num_projections": num_projections,
            "output_folder": output_folder
        }
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute complete photogrammetry scan workflow."""
        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "photogrammetry_scan_execute", state)
        
        try:
            streamer.status("Parsing scan parameters...")

            query = StateManager.get_current_task(state).lower()

            # Extract scan parameters from query
            start_angle = None
            end_angle = None
            num_projections = None
            save_folder = None
            
            # Parse angle range (e.g., "from 0 to 180")
            match_range = re.search(r"from\s+(-?\d+\.?\d*)\s+to\s+(-?\d+\.?\d*)", query)
            if match_range:
                start_angle = float(match_range.group(1))
                end_angle = float(match_range.group(2))

            # Parse number of projections (e.g., "with 10 projections")
            match_proj = re.search(r"with\s+(\d+)\s+projections?", query)
            if match_proj:
                num_projections = int(match_proj.group(1))

            # Check if sentence contains save-related keywords
            if "save" in query.lower():
                # First try to find quoted text (most reliable)
                quote_match = re.search(r"['\"]([^'\"]+)['\"]", query)
                if quote_match:
                    save_folder = quote_match.group(1)
                else:
                    # Fallback: grab the last word
                    words = query.split()
                    if words:
                        save_folder = words[-1].strip("'\"")  # Remove any quotes
                    else:
                        save_folder = "Default"
            else:
                save_folder = "Default"
            
            # Set defaults if not specified
            start_angle = start_angle if start_angle is not None else 0
            end_angle = end_angle if end_angle is not None else 180
            num_projections = num_projections if num_projections is not None else 10
            save_folder = save_folder if save_folder is not None else "Default"
            
            streamer.status(f"Starting photogrammetry scan: {start_angle}° to {end_angle}° with {num_projections} projections...")
            
            scan_data = bolt_api.run_photogrammetry_scan(start_angle, end_angle, num_projections, save_folder)
        
            # Create context object
            context = CurrentRunScanContext(
                condition=scan_data.condition,
                timestamp=scan_data.timestamp
            )
            
            # Store context in framework state
            context_updates = StateManager.store_context(
                state, 
                registry.context_types.PHOTOGRAMMETRY_SCAN, 
                step.get("context_key"), 
                context
            )
            
            streamer.status("Photogrammetry scan completed successfully!")
            return context_updates
            
        except Exception as e:
            logger.error(f"Photogrammetry scan error: {e}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify photogrammetry scan errors for intelligent retry coordination."""

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
        """Define retry policy configuration for photogrammetry scan operations."""

        return {
            "max_attempts": 2,  # Fewer retries for long scans
            "delay_seconds": 2.0,  # Longer delay for beamline recovery
            "backoff_factor": 2.0
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for photogrammetry scan execution in BOLT beamline."""

        example = OrchestratorExample(
            step=PlannedStep(
                context_key="photogrammetry_scan",
                capability="photogrammetry_scan_execute",
                task_objective="Execute complete photogrammetry scan with specified parameters",
                expected_output=registry.context_types.PHOTOGRAMMETRY_SCAN,
                success_criteria="Photogrammetry scan completed with all projections captured",
                inputs=[
                    {"name": "start_angle", "type": "float", "description": "Starting angle of scan (default: 0)"},
                    {"name": "end_angle", "type": "float", "description": "Ending angle of scan (default: 180)"},
                    {"name": "num_projections", "type": "int", "description": "Number of projections (default: 10)"},
                    {"name": "output_folder", "type": "string", "description": "Folder path to save output (optional)"}
                ]      
            ),
            scenario_description="Executing complete photogrammetry scan for 3D reconstruction",
            notes=f"Output stored as {registry.context_types.PHOTOGRAMMETRY_SCAN}. This is a complete experimental procedure."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "photogrammetry_scan_execute" steps:**
- User requests complete photogrammetry/CT scan for 3D reconstruction
- User specifies scan parameters (angles, projections)
- For full experimental data collection and research
- When comprehensive sample characterization is needed

**BOLT Beamline Context:**
- Executes complete photogrammetry experiments
- Coordinates motor rotation with detector imaging
- Generates datasets for 3D reconstruction
- Primary experimental capability for research

**Scan Parameters:**
- Angular range: start and end angles (default: 0° to 180°)
- Projections: number of images to capture (default: 10)
- Output folder: data storage location (optional)

**Output: {registry.context_types.PHOTOGRAMMETRY_SCAN}**
- Contains: scan_metadata, projection_data, reconstruction_parameters
- Available for data analysis and 3D reconstruction

**Typical Workflow Position:**
- After motor positioning and alignment checks
- After test shots to verify setup
- Final step in experimental preparation sequence
- Usually requires prior sample positioning and beam alignment""",
            examples=[example],
            order=4  # Highest priority - main experimental capability
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Provide task classification guidance for photogrammetry scan execution."""
        return TaskClassifierGuide(
            instructions="""Determine if the user wants to EXECUTE a complete photogrammetry scan with multiple projections in the BOLT beamline system.

BOLT CONTEXT: This is an imaging beamline for photogrammetry experiments. Users may request:
- Complete photogrammetry/CT scans for 3D reconstruction
- Multi-projection scans with angular parameters
- Full experimental data collection procedures
- Research-grade photogrammetry experiments""",
            examples=[
                ClassifierExample(
                    query="Run a photogrammetry scan from 0 to 180 degrees with 20 projections",
                    result=True,
                    reason="Complete photogrammetry scan request with specific parameters."
                ),
                ClassifierExample(
                    query="Start a CT scan of the sample",
                    result=True,
                    reason="Request for computed photogrammetry (CT) scan."
                ),
                ClassifierExample(
                    query="Execute photogrammetry experiment with 50 projections",
                    result=True,
                    reason="Complete photogrammetry experiment request."
                ),
                ClassifierExample(
                    query="Perform a 3D scan of the object",
                    result=True,
                    reason="3D scanning requires photogrammetry with multiple projections."
                ),
                ClassifierExample(
                    query="Run a full rotation scan from 0 to 360 degrees",
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