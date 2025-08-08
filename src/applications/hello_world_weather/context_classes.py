"""
Hello World Weather Context Classes.

Provides structured data containers for weather information exchange within the
Alpha Berkeley Agent Framework. These Pydantic-based context classes enable
type-safe data transfer between capabilities, orchestration components, and
the response generation system.

The context classes implement the framework's CapabilityContext interface,
providing automatic serialization, validation, and integration with the
state management system. This design ensures data consistency and type safety
throughout the weather information retrieval and processing workflow.

Architecture Integration:
    Context classes serve as the primary data exchange mechanism between:
    
    1. **Capability Layer**: Weather retrieval capabilities store results in contexts
    2. **State Management**: Contexts are persisted in agent state across turns
    3. **Orchestration Layer**: Planning system uses context types for dependencies
    4. **Response Generation**: LLM accesses structured context data for responses
    5. **Serialization System**: Automatic JSON conversion for persistence and streaming

Data Flow:
    Weather contexts follow this lifecycle pattern:
    
    1. **Creation**: Capabilities instantiate contexts with retrieved weather data
    2. **Validation**: Pydantic validates field types and constraints automatically
    3. **Storage**: StateManager persists contexts in agent state with unique keys
    4. **Access**: Other components access contexts via get_access_details() interface
    5. **Serialization**: Contexts convert to JSON for persistence and API responses

.. note::
   Context classes determine data structure and validation, not business logic.
   Location determination and weather retrieval logic belongs in capabilities,
   not in these data containers.

.. warning::
   Context classes must remain serializable and avoid complex Python objects.
   Use only JSON-compatible types (str, int, float, bool, datetime, lists, dicts)
   to ensure proper persistence and state management.
"""

from datetime import datetime
from typing import Dict, Any, Optional, ClassVar
from pydantic import Field
from framework.context.base import CapabilityContext

class CurrentWeatherContext(CapabilityContext):
    """Structured context for current weather condition data.
    
    Provides a type-safe container for current weather information including location,
    temperature, conditions, and timestamp data. This context class implements the
    framework's CapabilityContext interface with automatic Pydantic validation,
    serialization support, and integration with the state management system.
    
    The context serves as the primary data exchange format for weather information
    throughout the framework, enabling structured data flow between weather retrieval
    capabilities, orchestration components, and response generation systems.
    
    Data Structure:
        The context contains essential weather information fields:
        
        - **location**: Human-readable location name (e.g., "San Francisco")
        - **temperature**: Current temperature in Celsius as floating-point value
        - **conditions**: Descriptive weather conditions (e.g., "Sunny", "Rainy")
        - **timestamp**: Data retrieval timestamp for freshness tracking
    
    Framework Integration:
        - **Context Type**: CURRENT_WEATHER (used for capability dependencies)
        - **Context Category**: LIVE_DATA (indicates real-time data characteristics)
        - **Serialization**: Automatic JSON conversion via Pydantic
        - **Validation**: Type checking and constraint enforcement
        - **State Management**: Compatible with StateManager storage operations
    
    :param location: Human-readable name of the weather location
    :type location: str
    :param temperature: Current temperature in degrees Celsius
    :type temperature: float
    :param conditions: Descriptive weather conditions string
    :type conditions: str
    :param timestamp: Data retrieval timestamp for freshness tracking
    :type timestamp: datetime
    
    :raises ValidationError: If field types don't match expected types
    :raises ValueError: If required fields are missing or invalid
    
    .. note::
       This context is designed for current weather conditions only.
       Historical or forecast weather data would require separate context classes
       with appropriate field structures and validation rules.
    
    .. warning::
       Temperature values are stored in Celsius. Applications requiring different
       units should perform conversion in capabilities or response generation,
       not in the context class itself.
    
    Examples:
        Creating weather context from API data::
        
            >>> from datetime import datetime
            >>> weather_context = CurrentWeatherContext(
            ...     location="San Francisco",
            ...     temperature=18.5,
            ...     conditions="Partly Cloudy",
            ...     timestamp=datetime.now()
            ... )
            >>> print(f"Weather: {weather_context.temperature}°C, {weather_context.conditions}")
            Weather: 18.5°C, Partly Cloudy
        
        JSON serialization for persistence::
        
            >>> weather_data = weather_context.model_dump()
            >>> print(weather_data["location"])
            San Francisco
            >>> restored_context = CurrentWeatherContext.model_validate(weather_data)
        
        Integration with state management::
        
            >>> updates = StateManager.store_context(
            ...     state, "CURRENT_WEATHER", "weather_sf", weather_context
            ... )
            >>> # Context is now available for other capabilities and responses
    
    .. seealso::
       :class:`framework.context.base.CapabilityContext` : Base class for all context types
       :class:`framework.state.StateManager` : State management utilities for context storage
       :class:`CurrentWeatherCapability` : Capability that creates instances of this context
       :doc:`/developer-guides/context-classes` : Complete context class development guide
    """
    
    CONTEXT_TYPE: ClassVar[str] = "CURRENT_WEATHER"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Basic weather data
    location: str = Field(description="Location name")
    temperature: float = Field(description="Temperature in Celsius")
    conditions: str = Field(description="Weather conditions description")
    timestamp: datetime = Field(description="Timestamp of weather data")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating.
        
        Generates comprehensive access details that enable LLMs and templating systems
        to understand and utilize the weather context data effectively. This method
        provides both human-readable summaries and programmatic access patterns for
        integration with response generation and orchestration systems.
        
        The access details include formatted data summaries, template access patterns,
        usage examples, and field metadata that guide proper context utilization
        throughout the framework's response generation pipeline.
        
        Access Pattern Generation:
            The method generates template-style access patterns that can be used in:
            
            - **LLM Prompts**: Direct context data access in prompt templates
            - **Response Generation**: Structured data insertion in responses
            - **Orchestration**: Context availability checking and planning
            - **Documentation**: Usage examples for capability development
        
        :param key_name: Optional context key name for access pattern generation.
            If provided, generates specific access patterns using this key.
            If None, uses generic "key_name" placeholder for documentation.
        :type key_name: str, optional
        :return: Dictionary containing access details with the following structure:
            - location: Human-readable location name
            - current_temp: Formatted temperature string with units
            - conditions: Weather conditions description
            - access_pattern: Template access pattern for programmatic use
            - example_usage: Complete usage example with context substitution
            - available_fields: List of all accessible field names
        :rtype: Dict[str, Any]
        
        .. note::
           The access patterns use dot notation compatible with most templating
           systems and can be adapted for specific template engines as needed.
           
        .. warning::
           The generated access patterns assume the context is stored under the
           CURRENT_WEATHER context type. Verify context storage patterns match
           the generated access instructions.
        
        Examples:
            Basic access details generation::
            
                >>> weather_context = CurrentWeatherContext(
                ...     location="New York",
                ...     temperature=22.0,
                ...     conditions="Sunny",
                ...     timestamp=datetime.now()
                ... )
                >>> details = weather_context.get_access_details()
                >>> print(details["current_temp"])
                22.0°C
                >>> print(details["access_pattern"])
                context.CURRENT_WEATHER.key_name.temperature, context.CURRENT_WEATHER.key_name.conditions
            
            Specific key access pattern::
            
                >>> details = weather_context.get_access_details("nyc_weather")
                >>> print(details["example_usage"])
                The temperature in New York is {context.CURRENT_WEATHER.nyc_weather.temperature}°C with {context.CURRENT_WEATHER.nyc_weather.conditions} conditions
            
            Available fields inspection::
            
                >>> fields = weather_context.get_access_details()["available_fields"]
                >>> print(f"Available fields: {', '.join(fields)}")
                Available fields: location, temperature, conditions, timestamp
        
        .. seealso::
           :meth:`get_human_summary` : Human-readable summary generation
           :class:`framework.state.StateManager` : Context storage and retrieval utilities
           :doc:`/developer-guides/response-generation` : Response templating guide
        """
        key_ref = key_name if key_name else "key_name"
        
        return {
            "location": self.location,
            "current_temp": f"{self.temperature}°C",
            "conditions": self.conditions,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.temperature, context.{self.CONTEXT_TYPE}.{key_ref}.conditions",
            "example_usage": f"The temperature in {self.location} is {{context.{self.CONTEXT_TYPE}.{key_ref}.temperature}}°C with {{context.{self.CONTEXT_TYPE}.{key_ref}.conditions}} conditions",
            "available_fields": ["location", "temperature", "conditions", "timestamp"]
        }
    
    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of weather context data.
        
        Creates a concise, human-friendly summary of the weather context suitable
        for display in user interfaces, logging, debugging, and documentation.
        The summary provides essential weather information in a natural language
        format that can be directly presented to users or used in system outputs.
        
        This method complements get_access_details() by focusing on human consumption
        rather than programmatic access, making it ideal for user-facing displays,
        conversation logs, and administrative interfaces.
        
        Summary Format:
            The summary includes key weather information in natural language:
            
            - Location identification
            - Date of weather data
            - Temperature with units
            - Weather conditions description
        
        :param key: Context key identifier used for this weather data instance.
            While not used in the current summary format, it's required by the
            CapabilityContext interface and may be used for enhanced summaries
            in future versions.
        :type key: str
        :return: Dictionary containing human-readable summary with the following structure:
            - summary: Complete natural language description of weather conditions
        :rtype: dict
        
        .. note::
           The summary format is designed for direct user presentation and
           maintains consistency with other framework context summaries.
           
        .. warning::
           The summary uses the stored timestamp for date formatting. Ensure
           timestamps are current and in the expected timezone for accurate
           user presentation.
        
        Examples:
            Basic summary generation::
            
                >>> from datetime import datetime
                >>> weather_context = CurrentWeatherContext(
                ...     location="Prague",
                ...     temperature=15.0,
                ...     conditions="Rainy",
                ...     timestamp=datetime(2024, 3, 15, 14, 30)
                ... )
                >>> summary = weather_context.get_human_summary("prague_current")
                >>> print(summary["summary"])
                Weather in Prague on 2024-03-15: 15.0°C, Rainy
            
            Summary for user interface display::
            
                >>> context_summaries = []
                >>> for key, weather_ctx in stored_weather_contexts.items():
                ...     summary = weather_ctx.get_human_summary(key)
                ...     context_summaries.append(summary["summary"])
                >>> print("\n".join(context_summaries))
            
            Integration with logging systems::
            
                >>> summary_info = weather_context.get_human_summary("debug_weather")
                >>> logger.info(f"Retrieved weather data: {summary_info['summary']}")
        
        .. seealso::
           :meth:`get_access_details` : Programmatic access information for templates
           :class:`framework.context.base.CapabilityContext` : Base interface requirements
           :doc:`/user-guides/context-summaries` : Context summary formatting guidelines
        """
        return {
            "summary": f"Weather in {self.location} on {self.timestamp.strftime('%Y-%m-%d')}: {self.temperature}°C, {self.conditions}"
        }