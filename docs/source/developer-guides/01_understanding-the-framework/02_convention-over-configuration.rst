Convention over Configuration: Configuration-Driven Registry Patterns
======================================================================

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Configuration-driven component loading and explicit registry patterns
   - Using ``@capability_node`` and ``@infrastructure_node`` decorators
   - Application registry implementation with :class:`RegistryConfigProvider`
   - Component requirements and streaming integration
   - Convention-based module loading and dependency management

   **Prerequisites:** Understanding of Python decorators and class inheritance
   
   **Time Investment:** 15-20 minutes for complete understanding

Overview
========

The Alpha Berkeley Framework eliminates boilerplate through convention-based configuration loading and explicit registry patterns. Components are declared in registry configurations and loaded using standardized naming conventions.

Core Architecture
=================

Configuration-Driven Loading System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The framework uses three key patterns:

1. **Explicit Component Registration**: Components are declared in registry configurations with full metadata
2. **Convention-Based Module Loading**: Standardized paths for loading registry configurations and components
3. **Interface-Based Registry Pattern**: `RegistryConfigProvider` ensures type-safe component declarations

This approach reduces boilerplate by ~80% while ensuring consistency and avoiding hidden dependencies.

Component Decorators
====================

@capability_node Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~

Transforms capability classes into LangGraph-compatible nodes with complete infrastructure:

.. code-block:: python

   from framework.base import BaseCapability, capability_node
   from framework.state import AgentState
   from typing import Dict, Any

   @capability_node
   class WeatherCapability(BaseCapability):
       name = "weather_data"
       description = "Retrieve current weather conditions"
       provides = ["WEATHER_DATA"]
       requires = ["LOCATION"]
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           location = state.get("location", "San Francisco")
           weather_data = await fetch_weather(location)
           
           return {
               "weather_current_conditions": weather_data,
               "weather_last_updated": datetime.now().isoformat()
           }

**Infrastructure Features Provided:**
- LangGraph node creation (`langgraph_node` attribute)
- Error handling and classification
- State management and step progression
- Streaming support via LangGraph
- Performance monitoring
- Validation of required components

@infrastructure_node Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creates infrastructure components for system operations:

.. code-block:: python

   from framework.base import BaseInfrastructureNode, infrastructure_node

   @infrastructure_node
   class TaskExtractionNode(BaseInfrastructureNode):
       name = "task_extraction"
       description = "Extract actionable tasks from conversation"
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           # Extract task from conversation
           task = await extract_task_from_messages(state["messages"])
           return {"task_current_task": task}

**Infrastructure vs Capability:**
- **Infrastructure**: System components (orchestration, routing, classification)
- **Capabilities**: Business logic components (data analysis, PV finding, etc.)
- **Same patterns**: Identical decorator and validation patterns
- **Different defaults**: Infrastructure has more conservative error handling

Registry System
===============

Application Registry Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each application provides a registry configuration:

.. code-block:: python

   # File: applications/als_expert/registry.py
   from framework.registry import (
       CapabilityRegistration, 
       RegistryConfig,
       RegistryConfigProvider
   )

   class ALSExpertRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self) -> RegistryConfig:
           return RegistryConfig(
               capabilities=[
                   CapabilityRegistration(
                       name="pv_address_finding",
                       module_path="applications.als_expert.capabilities.pv_address_finding",
                       class_name="PVAddressFindingCapability",
                       description="Find EPICS PV addresses",
                       provides=["PV_ADDRESSES"],
                       requires=[]
                   ),
                   CapabilityRegistration(
                       name="data_analysis", 
                       module_path="applications.als_expert.capabilities.data_analysis",
                       class_name="DataAnalysisCapability",
                       description="Analyze scientific data",
                       provides=["ANALYSIS_RESULTS"],
                       requires=["DATA_SOURCES"]
                   )
               ]
           )

Registry Initialization
~~~~~~~~~~~~~~~~~~~~~~~

The framework systematically:
1. Reads application list from configuration
2. Loads registry providers using naming convention (`applications.{app_name}.registry`)
3. Imports components lazily using explicit module paths to prevent circular imports
4. Validates dependencies and initialization order
5. Creates component instances ready for use

.. code-block:: python

   from framework.registry import initialize_registry, get_registry

   # Initialize the registry system
   initialize_registry()

   # Access components
   registry = get_registry()
   capability = registry.get_capability("pv_address_finding")

Component Requirements
======================

Registry Declaration Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All components must be explicitly declared in registry configurations and implement required patterns:

.. code-block:: python

   @capability_node  # or @infrastructure_node
   class MyComponent(BaseCapability):  # or BaseInfrastructureNode
       # REQUIRED: Validated at decoration time
       name: str = "my_component"
       description: str = "Component description"
       
       # REQUIRED: Main execution logic
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           return {"result": "success"}
       
       # OPTIONAL: Custom error handling (inherits defaults)
       @staticmethod
       def classify_error(exc: Exception, context: dict) -> ErrorClassification:
           if isinstance(exc, ConnectionError):
               return ErrorClassification(
                   severity=ErrorSeverity.RETRIABLE,
                   user_message="Connection lost, retrying...",
                   metadata={"technical_details": str(exc)}
               )
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message=f"Error: {exc}",
               metadata={"technical_details": str(exc)}
           )

Error Classification Levels
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The framework provides sophisticated error handling:

- **CRITICAL**: End execution immediately
- **RETRIABLE**: Retry execution with same parameters  
- **REPLANNING**: Create new execution plan
- **FATAL**: System-level failure requiring immediate termination

Always-Active Capabilities
~~~~~~~~~~~~~~~~~~~~~~~~~~

Some capabilities are always included in execution:

.. code-block:: python

   # In registry configuration:
   CapabilityRegistration(
       name="respond",
       module_path="framework.infrastructure.respond_node",
       class_name="RespondCapability",
       always_active=True  # Always included in active capabilities
   )

Streaming Integration
=====================

Framework components use LangGraph's native streaming:

.. code-block:: python

   @capability_node
   class MyCapability(BaseCapability):
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           from configs.streaming import get_streamer
           
           # Get framework streaming support
           streamer = get_streamer("framework", "my_capability", state)
           
           streamer.status("Processing data...")
           result = await process_data()
           streamer.status("Processing complete")
           
           return {"processed_data": result}

Benefits
========

Reduced Boilerplate
~~~~~~~~~~~~~~~~~~~

**Configuration-driven approach** (Component: 5 lines + Registry: 8 lines):

.. code-block:: python

   # Component implementation
   @capability_node
   class MyCapability(BaseCapability):
       name = "my_capability"
       description = "What it does"
       # Implementation handles infrastructure

   # Registry declaration (required)
   CapabilityRegistration(
       name="my_capability",
       module_path="applications.myapp.capabilities.my_capability",
       class_name="MyCapability",
       description="What it does",
       provides=[], requires=[]
   )

Consistency Guarantee
~~~~~~~~~~~~~~~~~~~~~

- All components have identical infrastructure integration via decorators
- Error handling follows same patterns across components
- State management is consistent through framework patterns
- Performance monitoring is standardized
- Registry declarations ensure complete metadata

Easy Testing
~~~~~~~~~~~~

.. code-block:: python

   # Test individual capability without framework overhead
   capability = MyCapability()
   result = await capability.execute(mock_state)

   # Test with full framework integration (requires registry declaration)
   @capability_node
   class TestCapability(BaseCapability):
       # Gets framework integration via decorator
       # Must still be declared in registry for framework use

Troubleshooting
===============

Common Issues
~~~~~~~~~~~~~

**Missing required attributes:**

.. code-block:: python

   # Problem: Missing required convention
   @capability_node
   class MyCapability(BaseCapability):
       # Missing 'name' attribute - will fail at decoration time
       description = "Does something"

   # Solution: Add required attributes
   @capability_node
   class MyCapability(BaseCapability):
       name = "my_capability"
       description = "Does something"

**Registry path mismatch:**

.. code-block:: python

   # Problem: Registry registration doesn't match file structure
   CapabilityRegistration(
       module_path="applications.myapp.capabilities.missing",  # Wrong path
       class_name="MyCapability"
   )

   # Solution: Match file structure exactly
   CapabilityRegistration(
       module_path="applications.myapp.capabilities.my_capability",  # Correct
       class_name="MyCapability"
   )

Development Utilities Integration
=================================

The framework's development utilities follow the same convention-over-configuration patterns, providing consistent interfaces that reduce boilerplate and integrate seamlessly with the configuration system.

Framework Logging Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Component logging follows the structured API pattern used throughout the framework:

.. code-block:: python

   from configs.logger import get_logger
   
   # Framework components (follows component naming conventions)
   logger = get_logger("framework", "orchestrator")
   logger = get_logger("framework", "task_extraction")
   
   # Application components (matches registry declarations)
   logger = get_logger("hello_world_weather", "current_weather")
   logger = get_logger("als_expert", "data_analysis")
   
   # Rich message hierarchy for development
   logger.key_info("Starting capability execution")
   logger.info("Processing user request")
   logger.debug("Detailed trace information") 
   logger.warning("Configuration fallback used")
   logger.error("Processing failed", exc_info=True)
   logger.success("Capability completed successfully")
   logger.timing("Execution completed in 2.3 seconds")
   logger.approval("Awaiting human approval")

**Configuration Integration**: Color schemes are automatically loaded from the configuration using the same paths as component registration:

.. code-block:: yaml

   # Framework component colors (in src/framework/config.yml)
   logging:
     framework:
       logging_colors:
         orchestrator: "cyan"
         task_extraction: "thistle1"
   
   # Application component colors (in src/applications/{app_name}/config.yml)
   # Note: These get automatically namespaced under applications.{app_name} by config
   logging:
     logging_colors:
       current_weather: "blue"
       data_analysis: "magenta"

**Graceful Fallbacks**: When configuration is unavailable, logging gracefully falls back to white, maintaining functionality during development and testing.

LangGraph Streaming Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Streaming events integrate with LangGraph's native streaming and follow the same component naming conventions:

.. code-block:: python

   from configs.streaming import get_streamer
   
   @capability_node
   class MyCapability(BaseCapability):
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           # Follows same naming pattern as get_logger
           streamer = get_streamer("als_expert", "my_capability", state)
           
           streamer.status("Processing data...")
           result = await process_data()
           streamer.status("Processing complete")
           
           return {"processed_data": result}

**Automatic Step Detection**: The streaming system automatically determines execution context:

- **Task Preparation Phase**: Hard-coded mapping for infrastructure components (task_extraction, classifier, orchestrator)
- **Execution Phase**: Dynamic extraction from StateManager and execution plans  
- **Fallback**: Component name formatting for unknown components

Model Factory Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The model factory integrates with the configuration system following the same provider configuration patterns:

.. code-block:: python

   from framework.models import get_model
   from configs.config import get_provider_config
   
   # Configuration-driven model creation
   provider_config = get_provider_config("anthropic")
   model = get_model(
       provider="anthropic",
       model_id=provider_config.get("model_id"),
       api_key=provider_config.get("api_key")  # Auto-loaded from config
   )
   
   # Direct model configuration for development/testing
   model = get_model(
       provider="anthropic", 
       model_id="claude-3-5-sonnet-20241022",
       api_key="explicit-key-for-testing"
   )

**Provider Conventions**: All providers follow the same configuration structure with provider-specific requirements automatically validated:

.. code-block:: yaml

   # Provider configuration (in main config.yml)
   api:
     providers:
       anthropic:
         api_key: "${ANTHROPIC_API_KEY}"
         base_url: "https://api.anthropic.com"
       openai:
         api_key: "${OPENAI_API_KEY}" 
         base_url: "https://api.openai.com/v1"
       ollama:
         base_url: "http://localhost:11434"     # Required for Ollama
         # No api_key needed for local models

**Enterprise Integration**: HTTP proxy configuration follows environment variable conventions with automatic detection and validation.

Consistency Benefits
~~~~~~~~~~~~~~~~~~~~

Development utilities provide the same benefits as component registration:

- **Standardized Interfaces**: All utilities use the same source/component naming pattern
- **Configuration Integration**: Automatic loading from configuration system  
- **Graceful Degradation**: Continue functioning when configuration is unavailable
- **Type Safety**: Full type hints and validation for development-time error detection
- **Performance Optimization**: Caching and lazy loading reduce overhead

.. seealso::

   :doc:`../../api_reference/01_core_framework/03_registry_system`
       API reference for registry management and component discovery
   
   :doc:`../03_core-framework-systems/03_registry-and-discovery`
       Registry patterns and component registration workflows
   
   :doc:`../02_quick-start-patterns/01_building-your-first-capability`
       Hands-on guide to implementing components with decorators