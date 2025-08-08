============================
State and Context Essentials
============================

.. currentmodule:: framework.state

Master the essential state and context management patterns for Alpha Berkeley Framework development.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Understanding AgentState structure and selective persistence
   - Using StateManager for state operations and context storage
   - Working with ContextManager for data access
   - Creating CapabilityContext classes for type-safe data containers
   - Multi-step workflow patterns with progressive context building

   **Prerequisites:** Basic capability development knowledge
   
   **Time Investment:** 15-20 minutes for essential patterns

Framework Approach
===================

The Alpha Berkeley Framework uses **selective persistence**:

- **Only context data persists** across conversation turns
- **All execution fields reset** automatically
- **LangGraph-native patterns** for optimal performance

Core Components
===============

**AgentState**
  LangGraph-native state extending MessagesState

**StateManager**
  Static utilities for state creation and context storage

**ContextManager**
  Interface for accessing capability context data

**CapabilityContext**
  Pydantic base class for type-safe data containers

AgentState Structure
====================

The AgentState uses a flat structure with logical prefixes:

.. code-block:: python

   class AgentState(MessagesState):
       # ===== PERSISTENT FIELD =====
       capability_context_data: Dict[str, Dict[str, Dict[str, Any]]]
       
       # ===== EXECUTION-SCOPED FIELDS (Reset each turn) =====
       
       # Agent control
       agent_control: Dict[str, Any]
       
       # Task processing
       task_current_task: Optional[str]
       task_depends_on_chat_history: bool
       task_depends_on_user_memory: bool
       
       # Planning
       planning_active_capabilities: List[str]
       planning_execution_plan: Optional[ExecutionPlan]
       planning_current_step_index: int
       
       # Execution
       execution_step_results: Dict[str, Any]
       execution_last_result: Optional[ExecutionResult]
       
       # Control flow
       control_needs_reclassification: bool
       control_retry_count: int
       control_has_error: bool

**Key insight:** Only ``capability_context_data`` persists across conversation turns.

Context Data Structure
----------------------

Context data uses a three-level dictionary optimized for LangGraph:

.. code-block:: python

   capability_context_data = {
       "WEATHER_DATA": {           # Context type
           "step_0": {             # Context key
               "location": "San Francisco",
               "temperature": 18.5,
               "conditions": "Sunny",
               "timestamp": "2024-01-01T12:00:00Z"
           }
       },
       "PV_ADDRESSES": {
           "beam_current": {
               "pvs": ["SR:C01:BI:Current", "SR:C02:BI:Current"],
               "description": "Beam current monitoring PVs",
               "count": 2
           }
       }
   }

StateManager Essentials
=======================

Creating Fresh State
--------------------

.. code-block:: python

   from framework.state import StateManager
   
   # Create fresh state for new conversation
   state = StateManager.create_fresh_state(
       user_input="What's the weather in San Francisco?",
       current_state=None  # No previous state
   )
   
   # Create fresh state preserving context
   new_state = StateManager.create_fresh_state(
       user_input="How about New York?",
       current_state=previous_state  # Preserves context data
   )

Storing Context Data
--------------------

The essential pattern for storing capability results:

.. code-block:: python

   from framework.state import StateManager
   from my_app.context_classes import WeatherDataContext
   
   @capability_node
   class WeatherCapability(BaseCapability):
       name = "weather_data"
       description = "Retrieve current weather conditions"
       provides = ["WEATHER_DATA"]
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           # Get current execution step
           step = StateManager.get_current_step(state)
           
           # Your business logic here
           weather_data = await fetch_weather_data()
           
           # Create structured context
           context = WeatherDataContext(
               location=weather_data.location,
               temperature=weather_data.temperature,
               conditions=weather_data.conditions,
               timestamp=datetime.now().isoformat()
           )
           
           # Store and return (one-liner pattern)
           return StateManager.store_context(
               state,
               "WEATHER_DATA",              # Context type
               step.get("context_key"),     # Unique key
               context                      # Pydantic context object
           )

ContextManager Usage
====================

Access stored context data with structured interface:

.. code-block:: python

   from framework.context import ContextManager
   
   def process_with_context(state: AgentState):
       # Create context manager from state
       context_manager = ContextManager(state)
       
       # Get specific context by type and key
       weather_context = context_manager.get_context("WEATHER_DATA", "step_0")
       if weather_context:
           print(f"Weather in {weather_context.location}: {weather_context.temperature}°C")
       
       # Get all contexts of a specific type
       all_weather_data = context_manager.get_all_of_type("WEATHER_DATA")
       for key, weather in all_weather_data.items():
           print(f"{key}: {weather.location} - {weather.temperature}°C")

Creating Context Classes
========================

Context classes provide type-safe data containers:

.. code-block:: python

   from datetime import datetime
   from typing import ClassVar
   from pydantic import Field
   from framework.context.base import CapabilityContext
   
   class WeatherDataContext(CapabilityContext):
       """Context for weather data with validation."""
       
       # Framework integration constants
       CONTEXT_TYPE: ClassVar[str] = "WEATHER_DATA"
       CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
       
       # Data fields with validation
       location: str = Field(..., description="Location name")
       temperature: float = Field(..., description="Temperature in Celsius")
       conditions: str = Field(..., description="Weather conditions")
       timestamp: str = Field(..., description="ISO timestamp")
       
       def get_access_details(self, key: str) -> dict:
           return {
               "summary": f"Weather data for {self.location}",
               "temperature": f"{self.temperature}°C",
               "conditions": self.conditions,
               "context_key": key
           }
       
       def get_human_summary(self, key: str) -> dict:
           return {
               "title": "Weather Data",
               "content": f"Current weather in {self.location}: {self.temperature}°C, {self.conditions}",
               "metadata": {"context_key": key, "timestamp": self.timestamp}
           }

Best Practices
==============

State Management
----------------

.. code-block:: python

   @staticmethod
   async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
       # ✅ Use StateManager utilities
       step = StateManager.get_current_step(state)
       task = StateManager.get_current_task(state)
       
       # Process data and create context
       result_context = MyDataContext(
           processed_data=processed_results,
           timestamp=datetime.now().isoformat()
       )
       
       # ✅ Store context with one-liner
       return StateManager.store_context(
           state, "MY_DATA", step.get("context_key"), result_context
       )

Context Design
--------------

.. code-block:: python

   class MyDataContext(CapabilityContext):
       # ✅ Use descriptive context types
       CONTEXT_TYPE: ClassVar[str] = "PROCESSED_DATA"  # Not "DATA"
       CONTEXT_CATEGORY: ClassVar[str] = "ANALYSIS_RESULTS"
       
       # ✅ Include validation and metadata
       data: Dict[str, Any] = Field(..., description="Processed data")
       timestamp: str = Field(..., description="ISO timestamp")
       count: int = Field(..., ge=0, description="Number of records")

Multi-Step Workflows
--------------------

Handle progressive context building:

.. code-block:: python

   @staticmethod
   async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
       context_manager = ContextManager(state)
       
       # Get existing partial results
       partial_results = context_manager.get_context("PARTIAL_ANALYSIS", "working")
       
       if partial_results:
           current_data = partial_results.accumulated_data
       else:
           current_data = []
       
       # Add new data and store updated results
       new_data = await process_current_step()
       current_data.extend(new_data)
       
       updated_context = PartialAnalysisContext(
           accumulated_data=current_data,
           steps_completed=len(current_data),
           last_updated=datetime.now().isoformat()
       )
       
       return StateManager.store_context(
           state, "PARTIAL_ANALYSIS", "working", updated_context
       )

Common Issues
=============

**"Context not found"**

Handle missing context gracefully:

.. code-block:: python

   context_manager = ContextManager(state)
   required_data = context_manager.get_context("REQUIRED_TYPE", "key")
   
   if not required_data:
       return {"error": "Required data not available"}

**"Context serialization failed"**

Use only JSON-compatible types:

.. code-block:: python

   # ✅ Correct - JSON compatible
   timestamp: str = Field(..., description="ISO timestamp")
   data: Dict[str, Any] = Field(default_factory=dict)
   
   # ❌ Wrong - not serializable
   # timestamp: datetime = Field(...)
   # custom_obj: MyClass = Field(...)

**"State updates not persisting"**

Always return StateManager.store_context() result:

.. code-block:: python

   # ✅ Correct - return the state updates
   return StateManager.store_context(state, "MY_DATA", key, context)
   
   # ❌ Wrong - updates are lost
   # StateManager.store_context(state, "MY_DATA", key, context)
   # return {}

Next Steps
==========

**Essential:**
- :doc:`03_running-and-testing` - Learn to test your state-aware capabilities

**Advanced:**
- :doc:`../03_core-framework-systems/01_state-management-architecture` - Complete state lifecycle
- :doc:`../03_core-framework-systems/02_context-management-system` - Advanced context patterns

**API Reference:**
- :doc:`../../api_reference/01_core_framework/02_state_and_context` - StateManager documentation
- :doc:`../../api_reference/01_core_framework/02_state_and_context` - ContextManager reference