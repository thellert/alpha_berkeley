==============================
Building Your First Capability
==============================

.. currentmodule:: framework.base

Create a production-ready capability using the Alpha Berkeley Framework's core patterns.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Implement BaseCapability with @capability_node decorator
   - Work with AgentState and context storage using StateManager utilities
   - Register capabilities for framework discovery
   - Handle errors and streaming properly
   - Create CapabilityContext classes for data exchange

   **Prerequisites:** Python environment with Alpha Berkeley Framework installed
   
   **Time Investment:** 30-45 minutes for complete implementation

Core Concepts
=============

Capabilities are business logic components that:

- Extend BaseCapability and use @capability_node decorator
- Store results in Pydantic context objects
- Return state updates for LangGraph integration

Implementation Steps
====================

Step 1: Create Context Class
----------------------------

.. code-block:: python
   :caption: applications/my_app/context_classes.py

   from typing import ClassVar
   from pydantic import Field
   from framework.context.base import CapabilityContext
   
   class ProcessedDataContext(CapabilityContext):
       """Context for processed user query data."""
       
       CONTEXT_TYPE: ClassVar[str] = "PROCESSED_DATA"
       CONTEXT_CATEGORY: ClassVar[str] = "ANALYSIS_RESULTS"
       
       query: str = Field(..., description="Original user query")
       word_count: int = Field(..., description="Number of words")
       contains_numbers: bool = Field(..., description="Whether query contains numbers")
       
       def get_access_details(self, key: str) -> dict:
           return {
               "summary": f"Processed data for query: '{self.query}'",
               "word_count": self.word_count,
               "key": key
           }
       
       def get_summary(self, key: str) -> dict:
           return {
               "title": "Query Analysis Results",
               "content": f"Analyzed '{self.query}' - {self.word_count} words"
           }

Step 2: Implement Capability
----------------------------

.. code-block:: python
   :caption: applications/my_app/capabilities/data_processor.py

   from typing import Dict, Any
   from datetime import datetime
   from framework.base import BaseCapability, capability_node
   from framework.state import AgentState, StateManager
   from framework.utils.logger import get_logger
   from framework.utils.streaming import get_streamer
   from applications.my_app.context_classes import ProcessedDataContext
   
   logger = get_logger("data_processor")

   @capability_node
   class DataProcessorCapability(BaseCapability):
       """Process and analyze user data requests."""
       
       name = "data_processor"
       description = "Process and analyze user data requests"
       provides = ["PROCESSED_DATA"]
       requires = []
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           """Execute the capability's core business logic."""
           current_task = StateManager.get_current_task(state)
           streamer = get_streamer("my_app", "data_processor")
           
           try:
               streamer.status("Processing your request...")
               
               # Process the user query
               user_query = current_task.lower() if current_task else ""
               processed_data = {
                   "word_count": len(user_query.split()) if user_query else 0,
                   "contains_numbers": any(char.isdigit() for char in user_query),
               }
               
               # Create structured context
               context = ProcessedDataContext(
                   query=current_task,
                   word_count=processed_data["word_count"],
                   contains_numbers=processed_data["contains_numbers"]
               )
               
               # Store context and return state updates
               context_key = f"data_processing_{datetime.now().timestamp()}"
               context_updates = StateManager.store_context(
                   state, "PROCESSED_DATA", context_key, context
               )
               
               streamer.status("Processing completed!")
               return context_updates
               
           except Exception as e:
               logger.error(f"Processing error: {e}")
               raise

Step 3: Register Your Capability
--------------------------------

.. code-block:: python
   :caption: applications/my_app/registry.py

   from framework.registry import (
       RegistryConfigProvider, RegistryConfig, 
       CapabilityRegistration, ContextClassRegistration
   )
   
   class MyAppRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self) -> RegistryConfig:
           return RegistryConfig(
               capabilities=[
                   CapabilityRegistration(
                       name="data_processor",
                       module_path="applications.my_app.capabilities.data_processor", 
                       class_name="DataProcessorCapability",
                       description="Process and analyze user data requests",
                       provides=["PROCESSED_DATA"],
                       requires=[]
                   )
               ],
               context_classes=[
                   ContextClassRegistration(
                       context_type="PROCESSED_DATA",
                       module_path="applications.my_app.context_classes",
                       class_name="ProcessedDataContext",
                       description="Structured results from user query analysis"
                   )
               ]
           )

Step 4: Test Your Capability
----------------------------

.. code-block:: python
   :caption: test_my_capability.py

   import asyncio
   from framework.state import StateManager
   from applications.my_app.capabilities.data_processor import DataProcessorCapability
   
   async def test_capability():
       # Create test state
       state = StateManager.create_fresh_state("Hello world, this has 123 numbers!")
       
       # Execute capability
       capability = DataProcessorCapability()
       result = await capability.execute(state)
       
       print("Capability result:", result)
       print("Context data keys:", list(result.get("capability_context_data", {}).keys()))
   
   if __name__ == "__main__":
        asyncio.run(test_capability())

Essential Patterns
==================

Error Handling
--------------

Add custom error classification for domain-specific retry logic:

.. code-block:: python

   @staticmethod
   def classify_error(exc: Exception, context: dict) -> ErrorClassification:
       from framework.base.errors import ErrorClassification, ErrorSeverity
       
       if isinstance(exc, (ConnectionError, TimeoutError)):
           return ErrorClassification(
               severity=ErrorSeverity.RETRIABLE,
               user_message="Temporary service issue, retrying...",
               metadata={"technical_details": str(exc)}
           )
       
       return ErrorClassification(
           severity=ErrorSeverity.CRITICAL,
           user_message=f"Processing error: {exc}",
           metadata={"technical_details": str(exc)}
       )

Streaming Updates
-----------------

Provide progress feedback during operations:

.. code-block:: python

   @staticmethod
   async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
       streamer = get_streamer("my_app", "my_capability")
       
       streamer.status("Phase 1: Extracting data...")
       raw_data = await extract_data(state)
       
       streamer.status("Phase 2: Processing data...")
       processed_data = await process_data(raw_data)
       
       streamer.status("Phase 3: Storing results...")
       context = create_context(processed_data)
       
       return StateManager.store_context(state, "MY_DATA", "my_key", context)

Common Issues
=============

**"Capability not found in registry"**

Ensure exact name matching in registration:

.. code-block:: python

   # In capability class:
   name = "data_processor"
   
   # In registry:
   CapabilityRegistration(name="data_processor", ...)  # Must match exactly

**"execute method not found"**

Ensure execute is a static method:

.. code-block:: python

   @staticmethod  # Required
   async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
       pass

**"Context serialization error"**

Use only JSON-compatible types:

.. code-block:: python

   # ✅ Correct
   timestamp: str  # Use ISO string
   data: Dict[str, Any]
   
   # ❌ Wrong
   timestamp: datetime  # Not JSON serializable

Next Steps
==========

**Essential:**
- :doc:`03_running-and-testing` - Learn debugging and deployment
- :doc:`02_state-and-context-essentials` - Master state management

**Advanced:**
- :doc:`../03_core-framework-systems/02_context-management-system` - Advanced context patterns
- :doc:`../04_infrastructure-components/06_error-handling-infrastructure` - Comprehensive error handling

**API Reference:**
- :doc:`../../api_reference/01_core_framework/01_base_components` - BaseCapability documentation
- :doc:`../../api_reference/01_core_framework/02_state_and_context` - StateManager utilities