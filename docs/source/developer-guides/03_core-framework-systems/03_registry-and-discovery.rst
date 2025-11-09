========================
Registry and Discovery
========================

.. currentmodule:: osprey.registry

The Osprey Framework implements a centralized component registration and discovery system that enables clean separation between framework infrastructure and application-specific functionality.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Understanding :class:`RegistryManager` and component access patterns
   - Implementing application registries with :class:`RegistryConfigProvider`
   - Using ``@capability_node`` decorator for LangGraph integration
   - Registry configuration patterns and best practices
   - Component loading order and dependency management

   **Prerequisites:** Understanding of :doc:`01_state-management-architecture` (AgentState) and Python decorators
   
   **Time Investment:** 20-30 minutes for complete understanding

System Overview
===============

The registry system uses a two-tier architecture:

**Framework Registry**
  Core infrastructure components (nodes, base capabilities, services)

**Application Registries**
  Domain-specific components (capabilities, context classes, data sources)

Applications register components by implementing ``RegistryConfigProvider`` in their ``registry.py`` module. The framework loads registries from the path specified in configuration:

.. code-block:: yaml

   # config.yml
   registry_path: ./src/my_app/registry.py

RegistryManager
===============

The ``RegistryManager`` provides centralized access to all framework components:

.. code-block:: python

   from osprey.registry import initialize_registry, get_registry
   
   # Initialize the registry system
   initialize_registry()
   
   # Access the singleton registry instance
   registry = get_registry()
   
   # Access components
   capability = registry.get_capability("weather_data_retrieval")
   context_class = registry.get_context_class("WEATHER_DATA")
   data_source = registry.get_data_source("knowledge_base")

**Key Methods:**

- ``get_capability(name)`` - Get capability instance by name
- ``get_context_class(context_type)`` - Get context class by type identifier
- ``get_data_source(name)`` - Get data source provider instance
- ``get_node(name)`` - Get LangGraph node function

Application Registry Implementation
===================================

Applications implement registries using the ``RegistryConfigProvider`` interface with the ``extend_framework_registry()`` helper:

.. code-block:: python

   # src/my_app/registry.py
   from osprey.registry import (
       extend_framework_registry,
       CapabilityRegistration,
       ContextClassRegistration,
       RegistryConfig,
       RegistryConfigProvider
   )
   
   class MyAppRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self) -> RegistryConfig:
           return extend_framework_registry(
               capabilities=[
                   CapabilityRegistration(
                       name="weather_data_retrieval",
                       module_path="my_app.capabilities.weather_data_retrieval",
                       class_name="WeatherDataRetrievalCapability",
                       description="Retrieve weather data for analysis",
                       provides=["WEATHER_DATA"],
                       requires=["TIME_RANGE"]
                   )
               ],
               context_classes=[
                   ContextClassRegistration(
                       context_type="WEATHER_DATA",
                       module_path="my_app.context_classes",
                       class_name="WeatherDataContext"
                   )
               ]
           )

The ``extend_framework_registry()`` helper automatically includes all framework capabilities (memory, Python execution, time parsing, etc.) while adding your application-specific components.

**Advanced Options:**

.. code-block:: python

   return extend_framework_registry(

       # Exclude generic Python capability (replaced with specialized turbine_analysis)
       exclude_capabilities=["python"],

       capabilities=[
           # Specialized analysis replaces generic Python capability
           CapabilityRegistration(
               name="turbine_analysis",
               module_path="my_app.capabilities.turbine_analysis",
               class_name="TurbineAnalysisCapability",
               description="Analyze turbine performance with domain-specific logic",
               provides=["ANALYSIS_RESULTS"],
               requires=["TURBINE_DATA", "WEATHER_DATA"]
           )
       ],
       context_classes=[...],
       
       # Add data sources
       data_sources=[
           DataSourceRegistration(
               name="knowledge_base",
               module_path="my_app.data_sources.knowledge",
               class_name="KnowledgeProvider",
               description="Domain knowledge retrieval"
           )
       ],
       
       # Add custom framework prompt providers
       framework_prompt_providers=[
           FrameworkPromptProviderRegistration(
               application_name="my_app",
               module_path="my_app.framework_prompts",
               prompt_builders={"response_generation": "CustomResponseBuilder"}
           )
       ]
   )

Component Registration
======================

**Capability Registration:**

.. code-block:: python

   # In registry.py
   CapabilityRegistration(
       name="weather_data_retrieval",
       module_path="my_app.capabilities.weather_data_retrieval",
       class_name="WeatherDataRetrievalCapability",
       description="Retrieve weather data for analysis",
       provides=["WEATHER_DATA"],
       requires=["TIME_RANGE"]
   )

   # Implementation in src/my_app/capabilities/weather_data_retrieval.py
   from osprey.base import BaseCapability, capability_node
   
   @capability_node
   class WeatherDataRetrievalCapability(BaseCapability):
       name = "weather_data_retrieval"
       description = "Retrieve weather data for analysis"
       provides = ["WEATHER_DATA"]
       requires = ["TIME_RANGE"]
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           # Implementation here
           return {"weather_data": data}

**Context Class Registration:**

.. code-block:: python

   # In registry.py
   ContextClassRegistration(
       context_type="WEATHER_DATA",
       module_path="my_app.context_classes",
       class_name="WeatherDataContext"
   )

   # Implementation in src/my_app/context_classes.py
   from osprey.context.base import CapabilityContext
   
   class WeatherDataContext(CapabilityContext):
       CONTEXT_TYPE: ClassVar[str] = "WEATHER_DATA"
       CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
       
       location: str
       temperature: float
       conditions: str
       timestamp: datetime

**Data Source Registration:**

.. code-block:: python

   # In registry.py
   DataSourceRegistration(
       name="knowledge_base",
       module_path="my_app.data_sources.knowledge",
       class_name="KnowledgeProvider",
       description="Domain knowledge retrieval"
   )

**AI Provider Registration:**

Applications can register custom AI providers for institutional services or commercial providers not included in the framework.

**Basic Provider Registration:**

.. code-block:: python

   # In src/my_app/registry.py
   from osprey.registry import RegistryConfigProvider, ProviderRegistration
   from osprey.registry.helpers import extend_framework_registry
   
   class MyAppRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self):
           return extend_framework_registry(
               capabilities=[...],
               context_classes=[...],
               providers=[
                   ProviderRegistration(
                       module_path="my_app.providers.azure",
                       class_name="AzureOpenAIProviderAdapter"
                   ),
                   ProviderRegistration(
                       module_path="my_app.providers.institutional",
                       class_name="InstitutionalAIProvider"
                   )
               ]
           )

**Excluding Framework Providers:**

You can exclude framework providers if you want to use only custom providers:

.. code-block:: python

   return extend_framework_registry(
       capabilities=[...],
       providers=[
           ProviderRegistration(
               module_path="my_app.providers.custom",
               class_name="CustomProvider"
           )
       ],
       exclude_providers=["anthropic", "google"]  # Exclude specific framework providers
   )

**Replacing Framework Providers:**

To replace a framework provider with a custom implementation:

.. code-block:: python

   return extend_framework_registry(
       capabilities=[...],
       override_providers=[
           ProviderRegistration(
               module_path="my_app.providers.custom_openai",
               class_name="CustomOpenAIProvider"
           )
       ],
       exclude_providers=["openai"]  # Remove framework version
   )

**Provider Implementation:**

.. code-block:: python

   # Implementation in src/my_app/providers/azure.py
   from osprey.models.providers.base import BaseProvider
   from typing import Optional
   import httpx
   
   class AzureOpenAIProviderAdapter(BaseProvider):
       """Azure OpenAI provider with institutional configuration."""
       
       # Provider metadata (single source of truth)
       name = "azure_openai"
       requires_api_key = True
       requires_base_url = True
       requires_model_id = True
       supports_proxy = True
       default_base_url = None
       
       def create_model(
           self,
           model_id: str,
           api_key: Optional[str],
           base_url: Optional[str],
           timeout: Optional[float],
           http_client: Optional[httpx.AsyncClient]
       ):
           """Create PydanticAI model instance."""
           # Implementation for Azure-specific model creation
           pass
       
       def execute_completion(
           self,
           message: str,
           model_id: str,
           api_key: Optional[str],
           base_url: Optional[str],
           max_tokens: int = 1024,
           temperature: float = 0.0,
           **kwargs
       ):
           """Execute direct API completion."""
           # Implementation for Azure-specific completions
           pass
       
       def check_health(
           self,
           api_key: Optional[str],
           base_url: Optional[str],
           timeout: float = 5.0
       ):
           """Test connectivity and authentication."""
           # Implementation for Azure health check
           return (True, "Connected successfully")

Common use cases for custom providers include:

- **Institutional AI Services**: Stanford AI Playground, LBNL CBorg, national lab endpoints
- **Commercial Providers**: Cohere, Mistral AI, Together AI, etc.
- **Custom Endpoints**: Self-hosted models with OpenAI-compatible APIs

Once registered, custom providers work seamlessly with :func:`osprey.models.get_model` and :func:`osprey.models.get_chat_completion`, and are automatically discovered by the health check system (``osprey health``).

Registry Initialization and Usage
=================================

.. code-block:: python

   from osprey.registry import initialize_registry, get_registry
   
   # Initialize registry (loads framework + application components)
   initialize_registry()
   
   # Access registry throughout application
   registry = get_registry()
   
   # Get capabilities
   capability = registry.get_capability("weather_data_retrieval")
   all_capabilities = registry.get_all_capabilities()
   
   # Get context classes
   weather_context_class = registry.get_context_class("WEATHER_DATA")
   
   # Get data sources
   knowledge_provider = registry.get_data_source("knowledge_base")

**Registry Export for External Tools:**

The registry system automatically exports metadata during initialization for use by external tools and debugging:

.. code-block:: python

   # Export happens automatically during initialization
   initialize_registry(auto_export=True)  # Default behavior
   
   # Manual export for debugging or integration
   registry = get_registry()
   export_data = registry.export_registry_to_json("/path/to/export")
   
   # Export creates standardized JSON files:
   # - registry_export.json (complete metadata)
   # - capabilities.json (capability definitions)
   # - context_types.json (context type definitions)

**Export Configuration:**

The default export directory is configured in ``config.yml``:

.. code-block:: yaml

   file_paths:
     agent_data_dir: _agent_data
     registry_exports_dir: registry_exports

This creates exports in ``_agent_data/registry_exports/`` relative to the project root. The path can be customized through the configuration system.

Component Loading Order
=======================

Components are loaded lazily during registry initialization:

1. **Context classes** - Required by capabilities
2. **Data sources** - Required by capabilities  
3. **Providers** - AI model providers
4. **Core nodes** - Infrastructure components
5. **Services** - Internal LangGraph service graphs
6. **Capabilities** - Domain-specific functionality
7. **Framework prompt providers** - Application-specific prompts

Best Practices and Troubleshooting
===================================

.. tab-set::

   .. tab-item:: Best Practices

      **Registry Configuration:**
         - Keep registrations simple and focused
         - Use clear, descriptive names and descriptions
         - Define ``provides`` and ``requires`` accurately for dependency tracking

      **Capability Implementation:**
         - Always use ``@capability_node`` decorator
         - Implement required attributes: ``name``, ``description``
         - Make ``execute()`` method static and async
         - Return dictionary of state updates

      **Application Structure:**
         - Place registry in ``src/{app_name}/registry.py``
         - Implement exactly one ``RegistryConfigProvider`` class per application
         - Organize capabilities in ``src/{app_name}/capabilities/`` directory
         - Configure registry location in ``config.yml`` via ``registry_path``

   .. tab-item:: Common Issues

      **Component Not Found:**
         1. Verify component is registered in ``RegistryConfigProvider``
         2. Check module path and class name are correct
         3. Ensure ``initialize_registry()`` was called

      **Missing @capability_node:**
         1. Ensure ``@capability_node`` decorator is applied
         2. Verify ``name`` and ``description`` class attributes exist
         3. Check that ``execute()`` method is implemented as static method

      **Registry Export Issues:**
         1. Check that export directory is writable and accessible
         2. Verify ``auto_export=True`` during initialization for automatic exports
         3. Use manual ``export_registry_to_json()`` for debugging specific states

.. seealso::
   :doc:`05_message-and-execution-flow`
       Complete message processing pipeline using registered components
   :doc:`01_state-management-architecture`
       State management integration with registry system