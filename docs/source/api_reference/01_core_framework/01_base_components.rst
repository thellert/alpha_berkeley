===============
Base Components
===============

Foundation classes for capabilities and infrastructure nodes with LangGraph integration, plus decorators for seamless framework integration.

.. currentmodule:: framework.base

Base Classes
============

BaseCapability
--------------

.. autoclass:: BaseCapability
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   
   .. rubric:: Required Class Attributes
   
   .. attribute:: name
      :type: str
      
      Unique capability identifier for registration and routing (required).
   
   .. attribute:: description
      :type: str
      
      Human-readable description for documentation and logging (required).
   
   .. attribute:: provides
      :type: List[str]
      
      List of context types this capability generates (default: []).
   
   .. attribute:: requires
      :type: List[str]
      
      List of context types this capability depends on (default: []).
   
   .. rubric:: Abstract Methods
   
   .. automethod:: BaseCapability.execute
   
   .. rubric:: Optional Methods
   
   .. automethod:: BaseCapability.classify_error
   
   .. automethod:: BaseCapability.get_retry_policy
   
   .. rubric:: Template Methods
   
   .. automethod:: BaseCapability._create_orchestrator_guide
   
   .. automethod:: BaseCapability._create_classifier_guide
   
   .. rubric:: Properties
   
   .. autoproperty:: BaseCapability.orchestrator_guide
   
   .. autoproperty:: BaseCapability.classifier_guide

BaseInfrastructureNode
----------------------

.. autoclass:: BaseInfrastructureNode
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   
   .. rubric:: Required Class Attributes
   
   .. attribute:: name
      :type: str
      :no-index:
      
      Infrastructure node identifier for routing and logging (required).
   
   .. attribute:: description
      :type: str
      :no-index:
      
      Human-readable description for documentation and monitoring (required).
   
   .. rubric:: Abstract Methods
   
   .. automethod:: BaseInfrastructureNode.execute
      :no-index:
   
   .. rubric:: Error Handling Methods
   
   .. automethod:: BaseInfrastructureNode.classify_error
      :no-index:
   
   .. automethod:: BaseInfrastructureNode.get_retry_policy
      :no-index:

LangGraph Integration Decorators
=================================

capability_node
---------------

.. autofunction:: capability_node

   **Validation Requirements:**
   
   The decorator validates that the decorated class implements:
   
   - ``name`` (str): Unique capability identifier
   - ``description`` (str): Human-readable description  
   - ``execute()`` (async static method): Main business logic
   - ``classify_error()`` (static method): Error classification (inherited or custom)
   - ``get_retry_policy()`` (static method): Retry configuration (inherited or custom)
   
   **Infrastructure Features:**
   
   - Error classification with domain-specific recovery strategies
   - Manual retry system via router (no LangGraph retries)
   - State management with automatic state updates and step progression
   - Streaming support through LangGraph's streaming system
   - Development mode with raw error re-raising for debugging
   - Comprehensive timing and performance monitoring
   
   **Usage Example:**
   
   .. code-block:: python
   
      @capability_node
      class WeatherCapability(BaseCapability):
          name = "weather_data"
          description = "Retrieve current weather conditions"
          provides = ["WEATHER_DATA"]
          requires = ["LOCATION"]
          
          @staticmethod
          async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
              # Business logic implementation
              return {"weather_data": weather_info}

infrastructure_node
--------------------

.. autofunction:: infrastructure_node

   **Validation Requirements:**
   
   The decorator validates that the decorated class implements:
   
   - ``name`` (str): Infrastructure node identifier
   - ``description`` (str): Human-readable description
   - ``execute()`` (async static method): Orchestration/routing logic
   - ``classify_error()`` (static method): Error classification (inherited or custom)
   - ``get_retry_policy()`` (static method): Retry configuration (inherited or custom)
   
   **Infrastructure Features:**
   
   - Conservative error handling with fast failure detection
   - System monitoring with comprehensive timing and performance tracking
   - LangGraph native integration with streaming, configuration, and checkpoints
   - Development mode support with raw error re-raising
   - Optional quiet mode for high-frequency routing operations
   - Fatal error handling with immediate termination for system-level failures
   
   **Usage Examples:**
   
   .. code-block:: python
   
      @infrastructure_node
      class TaskExtractionNode(BaseInfrastructureNode):
          name = "task_extraction"
          description = "Extract and structure user tasks"
          
          @staticmethod
          async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
              # Task extraction logic
              return {"task_current_task": extracted_task}
      
      @infrastructure_node(quiet=True)
      class RouterNode(BaseInfrastructureNode):
          name = "router"
          description = "Dynamic routing based on agent state"
          
          @staticmethod
          async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
              # Routing logic without verbose logging
              return {"control_next_node": next_node}

Supporting Types
================

Error Classification
--------------------

.. autoclass:: ErrorSeverity
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ExecutionError
   :members:
   :undoc-members:
   :show-inheritance:

Result Types
------------

.. autoclass:: ExecutionResult
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ExecutionRecord
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CapabilityMatch
   :members:
   :undoc-members:
   :show-inheritance:

Planning Types
--------------

.. autoclass:: PlannedStep
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ExecutionPlan
   :members:
   :undoc-members:
   :show-inheritance:

Example System
==============

.. autoclass:: BaseExample
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OrchestratorExample
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OrchestratorGuide
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ClassifierExample
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: TaskClassifierGuide
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ClassifierActions
   :members:
   :undoc-members:
   :show-inheritance:

.. seealso::

   :doc:`02_state_and_context`
       State and context management systems used by components
   
   :doc:`03_registry_system`
       Registry system for component management
   
   :doc:`04_configuration_system`
       Configuration system for component settings
   
   :doc:`../../developer-guides/03_core-framework-systems/03_registry-and-discovery`
       Complete guide to component registration patterns