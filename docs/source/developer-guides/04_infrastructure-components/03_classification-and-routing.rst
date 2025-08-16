Classification and Routing
===========================

.. currentmodule:: framework.infrastructure.classifier

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
           
           # Run capability selection
           active_capabilities = await select_capabilities(
               task=current_task,
               available_capabilities=available_capabilities,
               state=state
           )
           
           return {
               "planning_active_capabilities": active_capabilities,
               "planning_execution_plan": None,
               "planning_current_step_index": 0
           }

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

**Step 2: LLM-Based Classification**

.. code-block:: python

   # Classify remaining capabilities using few-shot examples
   for capability in remaining_capabilities:
       classifier = capability.classifier_guide
       
       # Build classification prompt with examples
       system_prompt = classification_builder.get_system_instructions(
           capability_instructions=classifier.instructions,
           classifier_examples=examples_string
       )
       
       # LLM classification with structured output
       response = await get_chat_completion(
           message=f"{system_prompt}\n\nUser request:\n{task}",
           output_model=CapabilityMatch
       )
       
       if response.is_match:
           active_capabilities.append(capability.name)

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

Integration Patterns
--------------------

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

Troubleshooting
---------------

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

Performance Considerations
--------------------------

**Classification Optimization:**
- Parallel capability analysis when possible
- Structured LLM output for reliable parsing
- Efficient registry lookups for always-active capabilities

**Router Efficiency:**
- Priority-based routing (errors first, then progress checks)
- Minimal state access for routing decisions
- Clean error state management

.. seealso::

   :doc:`../../api_reference/02_infrastructure/03_classification`
       API reference for classification and routing system
   
   :doc:`../03_core-framework-systems/03_registry-and-discovery`
       Capability registration and discovery patterns
   
   :doc:`02_task-extraction-system`
       Task analysis and capability selection prerequisites

Next Steps
----------

- :doc:`04_orchestrator-planning` - How selected capabilities become execution plans
- :doc:`../03_core-framework-systems/03_registry-and-discovery` - Capability registry management
- :doc:`06_error-handling-infrastructure` - Error handling patterns

Classification and Routing determines which capabilities are needed and coordinates their execution through the framework's infrastructure.