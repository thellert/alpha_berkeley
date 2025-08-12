"""
Hello World Weather Application Registry.

Provides registry configuration for the Hello World Weather tutorial application,
including capability and context class registrations for the Alpha Berkeley
Agent Framework. This registry demonstrates the minimal configuration required
for a functional weather information application.

The registry follows the framework's convention-based discovery pattern,
registering the current weather capability and its associated context class
for automatic loading and integration with the LangGraph execution system.

This module serves as the integration point between the application components
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
                    name="current_angle",
                    module_path="applications.bolt.capabilities.current_angle",
                    class_name="CurrentAngleCapability", 
                    description="Get current angle for a motor",
                    provides=["CURRENT_ANGLE"],
                    requires=[]
                ),
                CapabilityRegistration(
                    name="move_motor",
                    module_path="applications.bolt.capabilities.move_motor",
                    class_name="CurrentMoveMotorCapability", 
                    description="Move motor to ",
                    provides=["MOVE_MOTOR"],
                    requires=[]
                ),
            ],
            
            context_classes=[
                ContextClassRegistration(
                    context_type="CURRENT_ANGLE",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentAngleContext"
                ),
                ContextClassRegistration(
                    context_type="MOVE_MOTOR",
                    module_path="applications.bolt.context_classes", 
                    class_name="CurrentMoveMotorContext"
                ),
            ]
        )