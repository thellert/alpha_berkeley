"""
BOLT Beamline Context Classes.

Context classes for storing and accessing data from BOLT beamline operations
including motor positions, detector images, and photogrammetry scan results.
"""


from datetime import datetime
from typing import Dict, Any, Optional, ClassVar
from pydantic import Field
from framework.context.base import CapabilityContext

class CurrentAngleContext(CapabilityContext):
    """Structured context for motor position data from BOLT beamline.
    
    Stores current angular position of sample rotation motor for experimental setup,
    status reporting, and coordination with other beamline operations.
    """

    CONTEXT_TYPE: ClassVar[str] = "MOTOR_POSITION"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Motor position data
    motor: str = Field(description="Motor identifier (e.g., DMC01:A)")
    angle: float = Field(description="Current angle in degrees")
    condition: str = Field(description="Motor status and condition description")
    timestamp: datetime = Field(description="Timestamp when position was read")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating."""
        key_ref = key_name if key_name else "key_name"
        
        return {
            "motor_id": self.motor,
            "current_angle": f"{self.angle}°",
            "motor_status": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.angle, context.{self.CONTEXT_TYPE}.{key_ref}.motor",
            "example_usage": f"Motor {self.motor} is positioned at {{context.{self.CONTEXT_TYPE}.{key_ref}.angle}}°",
            "available_fields": ["motor", "angle", "condition", "timestamp"]
        }
    
    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of motor position data."""
        return {
            "summary": f"Motor {self.motor} positioned at {self.angle}° on {self.timestamp.strftime('%Y-%m-%d')} at {self.timestamp.strftime('%H:%M')}"
        }
    
class CurrentMoveMotorContext(CapabilityContext):
    """Structured context for motor movement operation data from BOLT beamline.
    
    Stores results of motor positioning commands including final position,
    movement status, and timing for experimental coordination and logging.
    """

    CONTEXT_TYPE: ClassVar[str] = "MOTOR_MOVEMENT"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Motor movement data
    motor: str = Field(description="Motor identifier (e.g., DMC01:A)")
    angle: float = Field(description="Final angle position in degrees")
    condition: str = Field(description="Movement completion status and condition")
    timestamp: datetime = Field(description="Timestamp when movement completed")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating."""
        key_ref = key_name if key_name else "key_name"
        
        return {
            "motor_id": self.motor,
            "final_position": f"{self.angle}°",
            "movement_status": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.angle, context.{self.CONTEXT_TYPE}.{key_ref}.condition",
            "example_usage": f"Motor {self.motor} moved to {{context.{self.CONTEXT_TYPE}.{key_ref}.angle}}°",
            "available_fields": ["motor", "angle", "condition", "timestamp"]
        }
    
    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of motor movement data."""
        return {
            "summary": f"Motor {self.motor} successfully moved to {self.angle}° on {self.timestamp.strftime('%Y-%m-%d')} at {self.timestamp.strftime('%H:%M')}"
        }

class CurrentTakeCaptureContext(CapabilityContext):
    """Structured context for detector image capture data from BOLT beamline.
    
    Stores information about images captured from the area detector
    for individual measurements, test shots, and quality verification.
    """

    CONTEXT_TYPE: ClassVar[str] = "DETECTOR_IMAGE"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Detector image data
    condition: str = Field(description="Image capture status and detector condition")
    timestamp: datetime = Field(description="Timestamp when image was captured")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating."""
        key_ref = key_name if key_name else "key_name"
        
        return {
            "capture_status": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.condition, context.{self.CONTEXT_TYPE}.{key_ref}.timestamp",
            "example_usage": f"Image captured with status: {{context.{self.CONTEXT_TYPE}.{key_ref}.condition}}",
            "available_fields": ["condition", "timestamp"]
        }
    
    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of detector image data."""
        return {
            "summary": f"Image captured at {self.timestamp.strftime('%Y-%m-%d')} at {self.timestamp.strftime('%H:%M')}"
        }
    
class CurrentRunScanContext(CapabilityContext):
    """Structured context for photogrammetry scan execution data from BOLT beamline.
    
    Stores information about completed photogrammetry scans including
    scan parameters, execution status, and data collection metadata.
    """

    CONTEXT_TYPE: ClassVar[str] = "PHOTOGRAMMETRY_SCAN"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"

    # Photogrammetry scan data
    condition: str = Field(description="Scan completion status and experimental condition")
    timestamp: datetime = Field(description="Timestamp when scan was completed")

    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating."""
        key_ref = key_name if key_name else "key_name"
        
        return {
            "scan_status": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.condition, context.{self.CONTEXT_TYPE}.{key_ref}.timestamp",
            "example_usage": f"Photogrammetry scan completed with status: {{context.{self.CONTEXT_TYPE}.{key_ref}.condition}}",
            "available_fields": ["condition", "timestamp"]
        }

    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of photogrammetry scan data."""
        return {
            "summary": f"Photogrammetry scan completed at {self.timestamp.strftime('%Y-%m-%d')} at {self.timestamp.strftime('%H:%M')}"
        }
<<<<<<< HEAD

class CurrentReconstructObjectContext(CapabilityContext):
    """Structured context for reconstruction from folder data from BOLT beamline.
    
    Stores information about completed reconstruction from folder including
    reconstruction parameters, execution status, and data collection metadata.
    """

    CONTEXT_TYPE: ClassVar[str] = "RECONSTRUCT_OBJECT"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"

    # Reconstruction from folder data
    condition: str = Field(description="Reconstruction completion status and experimental condition")
    timestamp: datetime = Field(description="Timestamp when reconstruction was completed")

    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating."""
        key_ref = key_name if key_name else "key_name"
        
        return {
            "reconstruction_status": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.condition, context.{self.CONTEXT_TYPE}.{key_ref}.timestamp",
            "example_usage": f"Reconstruction from folder completed with status: {{context.{self.CONTEXT_TYPE}.{key_ref}.condition}}",
            "available_fields": ["condition", "timestamp"]
        }

    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of reconstruction from folder data."""
        return {
            "summary": f"Reconstruction from folder completed at {self.timestamp.strftime('%Y-%m-%d')} at {self.timestamp.strftime('%H:%M')}"
        }
=======
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
