Classification and Routing
===========================

.. currentmodule:: osprey.infrastructure.classifier

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - How tasks are matched to appropriate capabilities
   - LLM-based classification with few-shot examples
   - Central routing logic and execution coordination
   - Always-active capability handling

   **Prerequisites:** Understanding of :doc:`02_task-extraction-system` and :doc:`../03_core-framework-systems/03_registry-and-discovery`
   
   **Time Investment:** 15 minutes for complete understanding

Core Concept
------------

Classification determines which capabilities are needed for extracted tasks using intelligent analysis and registry configuration.

**Two-Phase Selection:**
    1. **Always-Active Capabilities** - Registry-configured capabilities selected automatically (e.g., "respond")
    2. **LLM Classification** - Remaining capabilities analyzed using few-shot examples

**Routing** provides centralized execution flow control based on agent state.

Classification Architecture
---------------------------

.. code-block:: python

   @infrastructure_node
   class ClassificationNode(BaseInfrastructureNode):
       name = "classifier"
       description = "Task Classification and Capability Selection"
       
       @staticmethod
       async def execute(state: AgentState, **kwargs):
           current_task = state.get("task_current_task")
           available_capabilities = registry.get_all_capabilities()
           
           # Detect reclassification scenario from error state
           previous_failure = _detect_reclassification_scenario(state)
           
           # Run parallel capability selection with concurrency control
           active_capabilities = await select_capabilities(
               task=current_task,
               available_capabilities=available_capabilities,
               state=state,
               logger=logger,
               previous_failure=previous_failure
           )
           
           return {
               "planning_active_capabilities": active_capabilities,
               "planning_execution_plan": None,
               "planning_current_step_index": 0
           }

**Parallel Classification Components:**

.. code-block:: python

   class CapabilityClassifier:
       """Handles individual capability classification with proper resource management."""
       
       async def classify(self, capability: BaseCapability, semaphore: asyncio.Semaphore) -> bool:
           """Classify a single capability with semaphore-controlled concurrency."""
           async with semaphore:  # Proper semaphore usage
               return await self._perform_classification(capability)

Capability Selection Process
----------------------------

**Step 1: Always-Active Capabilities**

.. code-block:: python

   # Registry configuration determines always-active capabilities
   always_active_names = registry.get_always_active_capability_names()
   
   # Add always-active capabilities first
   for capability in available_capabilities:
       if capability.name in always_active_names:
           active_capabilities.append(capability.name)

**Step 2: Parallel LLM-Based Classification**

.. code-block:: python

   # Get classification configuration for concurrency control
   classification_config = get_classification_config()
   max_concurrent = classification_config['max_concurrent_classifications']
   
   # Create classifier instance with shared context
   classifier = CapabilityClassifier(task, state, logger, previous_failure)
   
   # Create semaphore for concurrency control
   semaphore = asyncio.Semaphore(max_concurrent)
   
   # Create classification tasks with proper semaphore usage
   classification_tasks = [
       classifier.classify(capability, semaphore)
       for capability in remaining_capabilities
   ]
   
   # Execute all classifications in parallel with semaphore control
   classification_results = await asyncio.gather(*classification_tasks, return_exceptions=True)
   
   # Process results and collect active capabilities
   for capability, result in zip(remaining_capabilities, classification_results):
       if isinstance(result, Exception):
           logger.error(f"Classification failed for capability '{capability.name}': {result}")
           continue
       elif result is True:
           active_capabilities.append(capability.name)

The parallel classification system includes configurable concurrency limits to balance performance with API rate limits:

.. code-block:: yaml

   # config.yml
   execution_control:
     limits:
       max_concurrent_classifications: 5  # Maximum concurrent LLM requests

.. dropdown:: Bypass LLM-based Capability Selection
   :color: secondary

   Capability selection supports a configurable bypass mode to streamline execution. By default, bypass mode can be enabled via the :ref:`configuration system <performance-configuration-section>`, allowing the system to skip LLM-based classification and activate all registered capabilities automatically. Additionally, users can dynamically toggle capability selection at runtime using the ``/caps:off`` :ref:`slash command <slash-commands-section>`, providing flexibility for development, testing, or high-throughput scenarios.

   **Bypass Behavior:**
    - Skips LLM-based capability classification entirely  
    - Activates all available capabilities from the registry
    - Provides orchestrator with complete capability access
    - Maintains always-active capability handling

   **When to Use Bypass Mode:**
    - Exploratory R&D scenarios where capability requirements are uncertain
    - Small capability registries where classification overhead exceeds benefits
    - High-throughput applications requiring reduced LLM call latency (trades orchestrator processing cost for classification speed)
   
   **Advantages:**
    - Faster upstream pipeline (skips LLM-based capability selection)
    - No risk of missing relevant capabilities
   
   **Disadvantages:**
    - Longer orchestrator prompts (all capabilities included)
    - Slower plan generation (more tokens to process)
    - Potential for confusing or brittle execution plans
    - Orchestrator may struggle with too many capability options
   

Few-Shot Classification Examples
--------------------------------

Capabilities provide classifier guides with examples:

.. code-block:: python

   # Example capability classifier guide
   return TaskClassifierGuide(
       instructions="Activate when user requests weather information",
       examples=[
           ClassifierExample(
               query="What's the weather like?",
               result=True,
               reason="Direct weather request"
           ),
           ClassifierExample(
               query="What time is it?",
               result=False,
               reason="Time request, not weather"
           )
       ]
   )

Central Router Architecture
---------------------------

Router serves as the central decision point for execution flow:

.. code-block:: python

   def router_conditional_edge(state: AgentState) -> str:
       """Central routing logic with error handling."""
       
       # 1. Handle errors first
       if state.get('control_has_error', False):
           return handle_error_routing(state)
       
       # 2. Check execution progress
       if not state.get("task_current_task"):
           return "task_extraction"
       
       if not state.get('planning_active_capabilities'):
           return "classifier"
       
       if not StateManager.get_execution_plan(state):
           return "orchestrator"
       
       # 3. Execute next step
       return get_next_step_capability(state)

**Routing Priority:**
1. Error handling (highest priority)
2. Task availability check
3. Capability selection check
4. Execution plan check
5. Step execution

Error Handling and Retry
-------------------------

**Retry Logic in Router:**

.. code-block:: python

   # Router handles retries for RETRIABLE errors
   if error_classification.severity == ErrorSeverity.RETRIABLE:
       if retry_count < max_retries:
           # Apply exponential backoff
           delay = delay_seconds * (backoff_factor ** retry_count)
           time.sleep(delay)
           
           state['control_retry_count'] = retry_count + 1
           return capability_name  # Retry same capability
       else:
           return "error"  # Route to error node

**Classification Error Handling:**

.. code-block:: python

   @staticmethod
   def classify_error(exc: Exception, context: dict):
       # Retry LLM timeouts
       if isinstance(exc, (ConnectionError, TimeoutError)):
           return ErrorClassification(
               severity=ErrorSeverity.RETRIABLE,
               user_message="Classification service temporarily unavailable, retrying..."
           )
       
       # Don't retry validation errors
       if isinstance(exc, (ValueError, TypeError)):
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message="Classification configuration error"
           )

Reclassification Support
------------------------

System supports reclassification when initial selection fails:

.. code-block:: python

   # Triggered by RECLASSIFICATION severity errors from capabilities
   if error_classification.severity == ErrorSeverity.RECLASSIFICATION:
       return {
           "control_needs_reclassification": True,
           "control_reclassification_reason": f"Capability {capability_name} requested reclassification: {error_classification.user_message}"
       }

**Reclassification Handling:**
- Triggered by capabilities returning ErrorSeverity.RECLASSIFICATION
- Router checks reclassification count against configured limits
- Uses same selection logic with previous failure context
- Increments reclassification counter
- Clears previous state for fresh analysis
- Routes to error node when limits exceeded

Usage Examples
--------------

**Basic Classification Flow:**

.. code-block:: python

   # Task: "What's the weather like?"
   # Result: ["current_weather", "respond"] (always-active + classified)
   
   state = {"task_current_task": "What's the weather like?"}
   result = await ClassificationNode.execute(state)
   capabilities = result["planning_active_capabilities"]

**Router Decision Flow:**

.. code-block:: python

   # State progression through router
   state = {"task_current_task": "Check weather"}
   
   # Router decisions:
   # 1. No capabilities → "classifier"
   # 2. No execution plan → "orchestrator"  
   # 3. Has plan → next step capability

.. tab-set::

   .. tab-item:: Integration Patterns
   
      **Registry Integration:**
          - Always-active capabilities configured in registry
          - Capability classifier guides provide examples
          - Dynamic capability discovery supported
      
      **State Management:**
          - Classification results stored in ``planning_active_capabilities``
          - Router tracks retry counts and error states
          - State updates use LangGraph-compatible patterns
      
      **Error Recovery:**
          - Automatic retry for network issues
          - Reclassification for capability selection problems (RECLASSIFICATION severity)
          - Replanning for execution strategy issues (REPLANNING severity)
          - Router coordination for failed executions

   .. tab-item:: Troubleshooting
   
      **No Capabilities Selected:**
          - Check always-active capability configuration in registry
          - Verify capability classifier guides are implemented
          - Review few-shot examples for relevance
      
      **Classification Errors:**
          - Enable debug logging to see LLM decisions
          - Check capability classifier guide examples
          - Verify model configuration for classification
      
      **Router Loops:**
          - Ensure execution plans end with "respond" or "clarify"
          - Check state field values at each routing decision
          - Verify all referenced capabilities are registered

.. seealso::

   :doc:`../../api_reference/02_infrastructure/03_classification`
       API reference for classification and routing system
   
   :doc:`../03_core-framework-systems/03_registry-and-discovery`
       Capability registration and discovery patterns
   
   :doc:`02_task-extraction-system`
       Task analysis and capability selection prerequisites

   :doc:`04_orchestrator-planning`
       How selected capabilities become execution plans
   
   :doc:`../03_core-framework-systems/03_registry-and-discovery`
       Capability registry management
   
   :doc:`06_error-handling-infrastructure`
       Error handling patterns

Classification and Routing determines which capabilities are needed and coordinates their execution through the framework's infrastructure.