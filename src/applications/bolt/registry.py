"""
BOLT Beamline Application Registry.

Provides registry configuration for the BOLT imaging beamline application,
including capability and context class registrations for the Alpha Berkeley
Agent Framework. This registry enables motor control, detector imaging, and
photogrammetry scan execution for the BOLT beamline system.

The registry follows the framework's convention-based discovery pattern,
registering BOLT beamline capabilities and their associated context classes
for automatic loading and integration with the LangGraph execution system.

This module serves as the integration point between the BOLT beamline components
and the framework's registry system, enabling automatic discovery of capabilities
and context classes without manual configuration.
"""

from framework.registry import (
    CapabilityRegistration, 
    ContextClassRegistration, 
    RegistryConfig,
    RegistryConfigProvider
)

class BoltRegistryProvider(RegistryConfigProvider):
    
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[
                CapabilityRegistration(
                    name="motor_position_read",
                    module_path="applications.bolt.capabilities.motor_position_read",
                    class_name="MotorPositionReadCapability", 
                    description="Read current angular position of sample rotation motor",
                    provides=["MOTOR_POSITION"],
                    requires=[]
                ),
                CapabilityRegistration(
                    name="motor_position_set",
                    module_path="applications.bolt.capabilities.motor_position_set",
                    class_name="MotorPositionSetCapability", 
                    description="Move sample rotation motor to specified angular position",
                    provides=["MOTOR_MOVEMENT"],
                    requires=[]
                ),
                CapabilityRegistration(
                    name="detector_image_capture",
                    module_path="applications.bolt.capabilities.detector_image_capture",
                    class_name="DetectorImageCaptureCapability", 
                    description="Capture single image from area detector",
                    provides=["DETECTOR_IMAGE"],
                    requires=[]
                ),
                CapabilityRegistration(
                    name="photogrammetry_scan_execute",
                    module_path="applications.bolt.capabilities.photogrammetry_scan_execute",
                    class_name="PhotogrammetryScanExecuteCapability", 
                    description="Execute complete photogrammetry scan with multiple projections",
                    provides=["PHOTOGRAMMETRY_SCAN"],
                    requires=[]
                ),
                CapabilityRegistration(
                    name="reconstruct_object",
                    module_path="applications.bolt.capabilities.reconstruct_object",
                    class_name="ReconstructObjectCapability", 
                    description="Reconstruct object from folder",
                    provides=["RECONSTRUCT_OBJECT"],
                    requires=[]
                ),
            ],
            
            context_classes=[
                ContextClassRegistration(
                    context_type="MOTOR_POSITION",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentAngleContext"
                ),
                ContextClassRegistration(
                    context_type="MOTOR_MOVEMENT",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentMoveMotorContext"
                ),
                ContextClassRegistration(
                    context_type="DETECTOR_IMAGE",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentTakeCaptureContext"
                ),
                ContextClassRegistration(
                    context_type="PHOTOGRAMMETRY_SCAN",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentRunScanContext"
                ),
                ContextClassRegistration(
                    context_type="RECONSTRUCT_OBJECT",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentReconstructObjectContext"
                ),
            ]
        )