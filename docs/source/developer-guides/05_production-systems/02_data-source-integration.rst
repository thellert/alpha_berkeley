=======================================================
Data Source Integration: Unified Data Management System
=======================================================

**What you'll build:** Data source provider for integrating external data into agent workflows

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Implementing :class:`DataSourceProvider` and :class:`DataSourceContext` for custom providers
   - Using :func:`get_data_source_manager()` and :func:`create_data_source_request()` functions
   - Configuring provider registration with :class:`DataSourceRegistration` in registries
   - Managing parallel data retrieval with :class:`DataRetrievalResult` handling
   - Understanding data source discovery and response filtering patterns

   **Prerequisites:** Understanding of :doc:`../03_core-framework-systems/03_registry-and-discovery` and async programming patterns
   
   **Time Investment:** 30-45 minutes for complete understanding

Overview
========

The Data Source Integration system provides a unified architecture for accessing external data sources in agent workflows. The system supports both core framework data sources (like user memory) and application-specific data sources through a registry-based architecture.

**Key Features:**

- **Unified Manager**: Single orchestration layer for data source operations
- **Parallel Retrieval**: Concurrent data fetching from multiple sources with timeout handling
- **Registry Integration**: Automatic provider discovery through the framework registry
- **LLM Formatting**: Standardized formatting for prompt integration

Architecture Components
=======================

The data source system has three main components:

**1. DataSourceProvider (Interface)**
   Abstract base class defining the contract for all data source providers

**2. DataSourceManager (Orchestrator)**  
   Unified manager coordinating parallel retrieval from registered providers

**3. Registry Integration (Discovery)**
   Automatic provider loading through the framework registry system

Step-by-Step Implementation
===========================

Step 1: Create a Custom Data Source Provider
--------------------------------------------

Create a data source provider by extending the base provider interface:

.. code-block:: python

   """Custom Data Source Provider Example"""
   
   from typing import Optional
   from framework.data_management.providers import DataSourceProvider, DataSourceContext
   from framework.data_management.request import DataSourceRequest
   import logging
   
   logger = logging.getLogger(__name__)
   
   class CustomDatabaseProvider(DataSourceProvider):
       """Data source provider for application-specific database access."""
       
       def __init__(self):
           """Initialize the provider."""
           self._connection = None
       
       @property
       def name(self) -> str:
           """Unique identifier for this data source provider."""
           return "custom_database"
       
       @property  
       def context_type(self) -> str:
           """Context type for framework integration."""
           return "CUSTOM_DATABASE_CONTEXT"
       
       @property
       def description(self) -> str:
           """Human-readable description."""
           return "Custom application database access"
       
       async def retrieve_data(self, request: DataSourceRequest) -> Optional[DataSourceContext]:
           """Retrieve data based on request context."""
           try:
               # Example data retrieval logic
               data = await self._fetch_data(request.query)
               
               if not data:
                   return None
               
               return DataSourceContext(
                   source_name=self.name,
                   context_type=self.context_type,
                   data=data,
                   metadata={
                       "record_count": len(data),
                       "source_description": self.description
                   },
                   provider=self
               )
               
           except Exception as e:
               logger.warning(f"Failed to retrieve data from {self.name}: {e}")
               return None
       
       def should_respond(self, request: DataSourceRequest) -> bool:
           """Determine if this provider should respond to the request."""
           # Example: respond to requests from specific components
           return request.requester.component_type == "capability"
       
       async def _fetch_data(self, query: Optional[str]) -> list:
           """Fetch data from the database."""
           # Simplified example - implement your data fetching logic
           return [{"id": 1, "data": "example"}]

**Key Implementation Points:**

- **Required Properties**: Implement `name`, `context_type` properties
- **Required Methods**: Implement `retrieve_data()` and `should_respond()` methods
- **Error Handling**: Return `None` on failures rather than raising exceptions
- **Context Creation**: Structure data with metadata for LLM integration

Step 2: Register Your Provider with the Framework
-------------------------------------------------

Register your provider in your application's registry:

.. code-block:: python

   """Provider Registration in Application Registry"""
   
   from framework.registry.base import (
       RegistryConfig, RegistryConfigProvider, DataSourceRegistration
   )
   
   class MyApplicationRegistry(RegistryConfigProvider):
       """Application registry with custom data sources."""
       
       def get_registry_config(self) -> RegistryConfig:
           """Return registry configuration with data sources."""
           return RegistryConfig(
               capabilities=[
                   # Your capabilities here
               ],
               context_classes=[
                   # Your context classes here
               ],
               data_sources=[
                   DataSourceRegistration(
                       name="custom_database",
                       module_path="applications.myapp.data_sources.database",
                       class_name="CustomDatabaseProvider",
                       description="Custom application database access"
                   )
               ]
           )

**Registration Notes:**

- Register providers in your application's registry class
- Use the exact `name` from your provider implementation
- Provide correct `module_path` and `class_name` for lazy loading

Step 3: Use Data Sources in Capabilities
-----------------------------------------

Access your data sources through the unified manager:

.. code-block:: python

   """Using Data Sources in Capabilities"""
   
   from framework.base import BaseCapability, capability_node
   from framework.state import AgentState
   from framework.context import ContextManager
   from framework.data_management import (
       get_data_source_manager, create_data_source_request, DataSourceRequester
   )
   from typing import Dict, Any
   import logging
   
   logger = logging.getLogger(__name__)
   
   @capability_node
   class DataIntegratedCapability(BaseCapability):
       """Capability with data source integration."""
       
       async def execute(self, state: AgentState, context: ContextManager) -> Dict[str, Any]:
           """Execute with data source integration."""
           
           try:
               # Create data source request
               requester = DataSourceRequester(
                   component_type="capability",
                   component_name="data_integrated"
               )
               
               data_request = create_data_source_request(
                   state=state,
                   requester=requester,
                   query="example query"
               )
               
               # Retrieve data from all responding providers
               data_manager = get_data_source_manager()
               retrieval_result = await data_manager.retrieve_all_context(
                   request=data_request,
                   timeout_seconds=10.0
               )
               
               # Process retrieved data
               if retrieval_result.has_data:
                   logger.info(f"Retrieved data from {len(retrieval_result.successful_sources)} sources")
                   
                   # Access specific data sources by name
                   custom_data = retrieval_result.context_data.get("custom_database")
                   memory_data = retrieval_result.context_data.get("core_user_memory")
                   
                   # Use the data in your capability logic
                   result = self._process_with_data(custom_data, memory_data)
                   
                   return {
                       "success": True,
                       "result": result,
                       "data_sources_used": retrieval_result.successful_sources
                   }
               else:
                   logger.info("No data sources available - proceeding without external context")
                   return {"success": True, "result": "processed without data"}
                   
           except Exception as e:
               logger.error(f"Data source integration failed: {e}")
               return {"success": False, "error": str(e)}
       
       def _process_with_data(self, custom_data, memory_data) -> str:
           """Process capability logic with retrieved data."""
           # Implement your data processing logic
           return "processed with integrated data"

**Integration Patterns:**

- **Request Creation**: Use `create_data_source_request(state, requester, ...)` 
- **Parallel Retrieval**: Manager automatically retrieves from all responding providers
- **Error Resilience**: Individual provider failures don't affect overall retrieval
- **Fallback Handling**: Handle scenarios with no available data sources

Available Data Sources
======================

**Framework Data Sources:**

- **core_user_memory**: User memory and preferences (always available)

**Application Data Sources:**

The following data sources are available in specific applications:

- **experiment_database** (ALS Expert): Experimental data and maintenance logs
- **wind_farm_knowledge** (Wind Turbine): Wind farm domain knowledge

Working Example: Simple Data Integration
========================================

Complete working example:

.. code-block:: python

   from framework.base import BaseCapability, capability_node
   from framework.state import AgentState
   from framework.context import ContextManager
   from framework.data_management import (
       get_data_source_manager, create_data_source_request, DataSourceRequester
   )
   
   @capability_node
   class SimpleDataCapability(BaseCapability):
       """Simple capability demonstrating data source integration."""
       
       async def execute(self, state: AgentState, context: ContextManager) -> dict:
           """Execute with basic data integration."""
           
           # Create request
           requester = DataSourceRequester("capability", "simple_data")
           request = create_data_source_request(state, requester)
           
           # Get data manager and retrieve context
           data_manager = get_data_source_manager()
           result = await data_manager.retrieve_all_context(request, timeout_seconds=5.0)
           
           return {
               "success": result.has_data,
               "sources_used": result.successful_sources,
               "data_available": bool(result.context_data)
           }

Testing Your Data Source Integration
====================================

Test your data source integration:

.. code-block:: python

   async def test_data_source():
       """Test data source integration."""
       from framework.data_management import (
           get_data_source_manager, create_data_source_request, DataSourceRequester
       )
       from framework.state import AgentState
       
       # Create test state and request
       state: AgentState = {"messages": []}
       requester = DataSourceRequester("test", "test_component")
       request = create_data_source_request(state, requester, query="test query")
       
       # Test retrieval
       manager = get_data_source_manager()
       result = await manager.retrieve_all_context(request, timeout_seconds=5.0)
       
       print(f"Sources attempted: {result.total_sources_attempted}")
       print(f"Sources successful: {len(result.successful_sources)}")
       print(f"Success rate: {result.success_rate:.1%}")
       
       return result.has_data

**Production Deployment Checklist:**

- [ ] Custom providers implement required methods correctly
- [ ] Provider registration works in application registry
- [ ] Error handling manages provider failures gracefully
- [ ] Timeout values are appropriate for your data sources
- [ ] Testing validates data retrieval functionality

Troubleshooting
===============

**Common Issues:**

**Issue**: Provider not being discovered by the manager
   - **Cause**: Provider not registered in application registry
   - **Solution**: Verify provider is in `data_sources` list in registry config

**Issue**: `create_data_source_request` failing
   - **Cause**: Incorrect function signature
   - **Solution**: Use `create_data_source_request(state, requester, ...)` format

**Issue**: Provider errors affecting other sources
   - **Cause**: Provider raising exceptions instead of returning None
   - **Solution**: Handle all errors in provider and return None

**Debugging Data Sources:**

.. code-block:: python

   # Enable detailed logging
   import logging
   logging.getLogger("framework.data_management").setLevel(logging.DEBUG)
   
   # Test individual provider
   from framework.data_management import get_data_source_manager
   manager = get_data_source_manager()
   provider = manager.get_provider("custom_database")
   
   if provider:
       print(f"Provider found: {provider.name}")
   else:
       print("Provider not found - check registration")

Next Steps
==========

After implementing data source integration:

- :doc:`04_memory-storage-service` - Understand the user memory system
- :doc:`03_python-execution-service` - Integrate with code execution
- :doc:`../03_core-framework-systems/03_registry-and-discovery` - Advanced registry patterns