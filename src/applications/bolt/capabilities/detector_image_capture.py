"""
Detector Image Capture Capability for BOLT Beamline System.

This capability captures single images from the area detector
in the BOLT imaging beamline. It's used for individual measurements,
test shots, and quality checks.
"""
from typing import Dict, Any, Optional

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

from applications.bolt.context_classes import CurrentTakeCaptureContext
from applications.bolt.bolt_api import bolt_api

logger = get_logger("bolt", "detector_image_capture")
registry = get_registry()

@capability_node
class DetectorImageCaptureCapability(BaseCapability):
    """Capture single image from area detector in BOLT beamline."""
    
    # Required class attributes for registry configuration
    name = "detector_image_capture"
    description = "Capture single image from area detector"
    provides = ["DETECTOR_IMAGE"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute image capture workflow."""
        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "detector_image_capture", state)
        
        try:
            streamer.status("Preparing detector...")
            
            streamer.status("Capturing image...")
            image_data = bolt_api.take_capture()
            
            # Create context object
            context = CurrentTakeCaptureContext(
                condition=image_data.condition,
                timestamp=image_data.timestamp
            )
            
            # Store context in framework state
            context_updates = StateManager.store_context(
                state, 
                registry.context_types.DETECTOR_IMAGE, 
                step.get("context_key"), 
                context
            )
            
            streamer.status("Image captured successfully!")
            return context_updates
            
        except Exception as e:
            logger.error(f"Image capture error: {e}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify detector image capture errors for intelligent retry coordination."""

        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                metadata={
                    "user_message": "Detector communication timeout, retrying...",
                    "technical_details": str(exc)
                }
            )
        
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "user_message": f"Image capture error: {str(exc)}",
                "technical_details": f"Error: {type(exc).__name__}"
            }
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Define retry policy configuration for image capture operations."""

        return {
            "max_attempts": 3,
            "delay_seconds": 0.5,
            "backoff_factor": 1.5
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for detector image capture in BOLT beamline."""

        example = OrchestratorExample(
            step=PlannedStep(
                context_key="detector_image",
                capability="detector_image_capture",
                task_objective="Capture single image from area detector",
                expected_output=registry.context_types.DETECTOR_IMAGE,
                success_criteria="Image successfully captured",
                inputs=[]
            ),
            scenario_description="Capturing single image for measurement or quality check",
            notes=f"Output stored as {registry.context_types.DETECTOR_IMAGE}. Use for test shots and individual measurements."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "detector_image_capture" steps:**
- User asks to take a single image or measurement
- For test shots before starting photogrammetry scans
- When checking sample alignment or positioning
- For quality control and beam verification

**BOLT Beamline Context:**
- Captures images from area detector
- Used for individual measurements and test shots
- Essential for experimental verification and setup

**Image Types:**
- Single projection images
- Test shots for alignment
- Quality control measurements

**Output: {registry.context_types.DETECTOR_IMAGE}**
- Contains: image_data, capture_conditions, timestamp
- Available for analysis and experimental verification

**Typical Workflow Position:**
- After motor positioning
- Before full photogrammetry scans (for testing)
- For standalone measurements and quality checks""",
            examples=[example],
            order=3  # After positioning, before full scans
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Provide task classification guidance for detector image capture."""
        return TaskClassifierGuide(
            instructions="""Determine if the user wants to CAPTURE a single image from the area detector in the BOLT beamline system.

BOLT CONTEXT: This is a beamline where area detectors capture images for analysis. Users may request:
- Single images for measurement
- Test shots before scans
- Quality control images
- Alignment verification images""",
            examples=[
                ClassifierExample(
                    query="Take an image",
                    result=True,
                    reason="Direct request for image capture."
                ),
                ClassifierExample(
                    query="Capture a single projection",
                    result=True,
                    reason="Request for single image capture."
                ),
                ClassifierExample(
                    query="Grab a frame from the detector",
                    result=True,
                    reason="Request to capture detector image."
                ),
                ClassifierExample(
                    query="Take a test shot",
                    result=True,
                    reason="Request for test image before experiments."
                ),
                ClassifierExample(
                    query="Get an image of the sample",
                    result=True,
                    reason="Request to capture sample image."
                ),
                ClassifierExample(
                    query="Check beam alignment with an image",
                    result=True,
                    reason="Request for alignment verification image."
                ),
                ClassifierExample(
                    query="Start a photogrammetry scan",
                    result=False,
                    reason="This is a full scan request, not single image capture."
                ),
                ClassifierExample(
                    query="Move the motor to 45 degrees",
                    result=False,
                    reason="This is a motor movement command, not image capture."
                ),
                ClassifierExample(
                    query="What is the current motor position?",
                    result=False,
                    reason="This is a position read request, not image capture."
                ),
                ClassifierExample(
                    query="Show me the previous image",
                    result=False,
                    reason="Request for historical data, not new image capture."
                ),
                ClassifierExample(
                    query="What tools do you have?",
                    result=False,
                    reason="Request is for tool information, not image capture."
                ),
            ],
            actions_if_true=ClassifierActions()
        )