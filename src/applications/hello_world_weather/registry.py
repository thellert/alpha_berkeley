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

class HelloWorldWeatherRegistryProvider(RegistryConfigProvider):
    """Registry configuration provider for Hello World Weather tutorial application.
    
    Implements the RegistryConfigProvider interface to provide framework integration
    for the Hello World Weather application. This provider registers all application
    components including the current weather capability and weather context class,
    enabling automatic discovery and loading by the framework's registry system.
    
    The provider follows the framework's convention-based registry pattern where
    each application provides exactly one registry configuration containing all
    necessary component registrations. This design enables loose coupling between
    applications and the framework while maintaining type safety and validation.
    
    Architecture Integration:
        The registry provider integrates with multiple framework systems:
        
        1. **Capability System**: Registers CurrentWeatherCapability for weather data retrieval
        2. **Context System**: Registers CurrentWeatherContext for structured data exchange
        3. **Discovery System**: Enables automatic component loading via module paths
        4. **Type System**: Provides context type mapping for capability dependencies
        5. **Documentation System**: Supplies descriptions for component documentation
    
    Component Registration:
        - **current_weather**: Capability for retrieving current weather conditions
        - **CURRENT_WEATHER**: Context type for weather data exchange
    
    :raises RegistryError: If component module paths are invalid or classes not found
    :raises ImportError: If application modules cannot be imported during registration
    
    .. note::
       This is a tutorial application demonstrating minimal registry configuration.
       Production applications may register additional components like data sources,
       services, and custom prompt providers.
    
    .. warning::
       All module paths must be importable and class names must exist in their
       respective modules. Invalid paths will cause framework initialization to fail.
    
    Examples:
        Registry provider usage in framework initialization::
        
            >>> from applications.hello_world_weather.registry import HelloWorldWeatherRegistryProvider
            >>> provider = HelloWorldWeatherRegistryProvider()
            >>> config = provider.get_registry_config()
            >>> print(f"Registered {len(config.capabilities)} capabilities")
            Registered 1 capabilities
        
        Accessing registered components::
        
            >>> from framework.registry import get_registry
            >>> registry = get_registry()
            >>> weather_capability = registry.capabilities.get("current_weather")
            >>> print(weather_capability.description)
            Get current weather conditions for a location
    
    .. seealso::
       :class:`framework.registry.RegistryConfigProvider` : Base interface for registry providers
       :class:`framework.registry.RegistryConfig` : Configuration structure returned by providers
       :class:`CurrentWeatherCapability` : Weather retrieval capability registered by this provider
       :class:`CurrentWeatherContext` : Weather context class registered by this provider
    """
    
    def get_registry_config(self) -> RegistryConfig:
        """Provide complete registry configuration for Hello World Weather application.
        
        Returns the complete component configuration including capability and context
        class registrations required for the Hello World Weather tutorial application.
        This configuration enables the framework to automatically discover and load
        application components using convention-based patterns.
        
        The configuration includes:
        
        **Capabilities:**
            - **current_weather**: Retrieves current weather conditions for supported locations
              (San Francisco, New York, Prague) using a mock weather API for demonstration
        
        **Context Classes:**
            - **CURRENT_WEATHER**: Structured data container for weather information including
              location, temperature, conditions, and timestamp data
        
        Component Dependencies:
            The current weather capability has no dependencies (requires=[]) and provides
            CURRENT_WEATHER context type for use by other capabilities or response generation.
            This simple dependency structure makes it ideal for tutorial purposes.
        
        :return: Complete registry configuration containing all application components
            with module paths, class names, descriptions, and dependency relationships
        :rtype: RegistryConfig
        :raises ImportError: If component module paths cannot be resolved during validation
        :raises AttributeError: If component class names are not found in their modules
        
        .. note::
           This method is called exactly once during framework initialization.
           The returned configuration is cached by the registry system for
           performance optimization.
        
        .. warning::
           All module paths must be valid Python import paths and all class names
           must exist in their respective modules. Invalid references will cause
           framework startup to fail with detailed error messages.
        
        Examples:
            Accessing the registry configuration::
            
                >>> provider = HelloWorldWeatherRegistryProvider()
                >>> config = provider.get_registry_config()
                >>> print(f"Capabilities: {[cap.name for cap in config.capabilities]}")
                Capabilities: ['current_weather']
                >>> print(f"Context types: {[ctx.context_type for ctx in config.context_classes]}")
                Context types: ['CURRENT_WEATHER']
            
            Validating component registrations::
            
                >>> config = provider.get_registry_config()
                >>> weather_cap = config.capabilities[0]
                >>> print(f"Provides: {weather_cap.provides}")
                Provides: ['CURRENT_WEATHER']
                >>> print(f"Requires: {weather_cap.requires}")
                Requires: []
        
        .. seealso::
           :class:`CapabilityRegistration` : Capability registration metadata structure
           :class:`ContextClassRegistration` : Context class registration metadata structure
           :meth:`framework.registry.RegistryManager.load_application_registry` : Registry loading process
        """
        return RegistryConfig(
            capabilities=[
                CapabilityRegistration(
                    name="current_weather",
                    module_path="applications.hello_world_weather.capabilities.current_weather",
                    class_name="CurrentWeatherCapability", 
                    description="Get current weather conditions for a location",
                    provides=["CURRENT_WEATHER"],
                    requires=[]
                )
            ],
            
            context_classes=[
                ContextClassRegistration(
                    context_type="CURRENT_WEATHER",
                    module_path="applications.hello_world_weather.context_classes", 
                    class_name="CurrentWeatherContext"
                )
            ]
        )