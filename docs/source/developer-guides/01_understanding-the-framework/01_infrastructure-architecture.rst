Infrastructure Architecture: Gateway-Driven Agent Framework
===========================================================

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - How the Gateway provides a single entry point for all message processing
   - The complete message processing pipeline from user input to agent response
   - How the Router coordinates infrastructure components with state-based routing
   - The role of Task Extraction, Classification, and Orchestration in the pipeline
   - Error handling and retry logic within the infrastructure

   **Prerequisites:** Basic understanding of LangGraph and agentic frameworks
   
   **Time Investment:** 10-15 minutes for complete understanding

Overview
========

The Alpha Berkeley Framework uses a **Gateway-Driven Architecture** where all message processing flows through a centralized Gateway that coordinates with infrastructure components via a Router-controlled pipeline.

Core Components
===============

Gateway - Single Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Gateway serves as the **only entry point** for all message processing across all interfaces (CLI, OpenWebUI, etc.).

.. code-block:: python

   from framework.infrastructure.gateway import Gateway

   # All interfaces use Gateway as single entry point
   gateway = Gateway()
   result = await gateway.process_message(
       user_input="Find beam current PV addresses",
       compiled_graph=graph,
       config=config
   )

   # Gateway returns structured result ready for execution
   if result.resume_command:
       # Handle approval/interrupt flow
       await graph.ainvoke(result.resume_command, config=config)
   elif result.agent_state:
       # Handle normal conversation flow
       await graph.ainvoke(result.agent_state, config=config)
   elif result.error:
       # Handle processing errors
       print(f"Error: {result.error}")

**Gateway responsibilities:**
- State reset for new conversation turns
- Slash command parsing (`/planning`, `/approval`, `/debug`)
- Approval response detection and resume command generation
- Message preprocessing and initial state creation

Router - Central Decision Authority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Router serves as the central decision-making authority that determines what happens next based on agent state.

.. code-block:: python

   def router_conditional_edge(state: AgentState) -> str:
       """Central routing logic based on agent state."""
       
       # Check for error conditions first
       if state.get('control_has_error', False):
           return handle_error_routing(state)
       
       # Check for termination
       if state.get('control_is_killed', False):
           return "error"
       
       # Task extraction needed?
       current_task = StateManager.get_current_task(state)
       if not current_task:
           return "task_extraction"
       
       # Classification needed?
       active_capabilities = state.get('planning_active_capabilities')
       if not active_capabilities:
           return "classifier"
       
       # Orchestration needed?
       execution_plan = StateManager.get_execution_plan(state)
       if not execution_plan:
           return "orchestrator"
       
       # Execute next step in plan
       current_index = StateManager.get_current_step_index(state)
       plan_steps = execution_plan.get('steps', [])
       
       if current_index >= len(plan_steps):
           return "END"  # Execution complete
       
       # Route to next capability
       current_step = plan_steps[current_index]
       return current_step['capability']

Task Extraction - Conversation to Action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Task Extraction converts conversational input into structured, actionable tasks using LLM analysis.

.. code-block:: python

   @infrastructure_node
   class TaskExtractionNode(BaseInfrastructureNode):
       name = "task_extraction"
       description = "Task Extraction and Processing"
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           messages = state["messages"]
           
           # Extract structured task using LLM
           processed_task = await asyncio.to_thread(
               _extract_task, messages, retrieval_result, logger
           )
           
           return {
               "task_current_task": processed_task.task,
               "task_depends_on_chat_history": processed_task.depends_on_chat_history,
               "task_depends_on_user_memory": processed_task.depends_on_user_memory
           }

Classification - Capability Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Classification system analyzes tasks and selects appropriate capabilities using LLM-based analysis.

.. code-block:: python

   @infrastructure_node
   class ClassificationNode(BaseInfrastructureNode):
       name = "classifier"
       description = "Task Classification and Capability Selection"
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           current_task = state.get("task_current_task")
           
           # Get available capabilities from registry
           registry = get_registry()
           available_capabilities = registry.get_all_capabilities()
           
           # Select capabilities using LLM-based classification
           active_capabilities = await select_capabilities(
               task=current_task,
               available_capabilities=available_capabilities,
               state=state,
               logger=logger
           )
           
           return {
               "planning_active_capabilities": active_capabilities,
               "planning_execution_plan": None,  # Reset for orchestrator
               "planning_current_step_index": 0
           }

Orchestrator - Execution Planning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Orchestrator creates complete execution plans before any capability execution begins.

.. code-block:: python

   @infrastructure_node
   class OrchestrationNode(BaseInfrastructureNode):
       name = "orchestrator"
       description = "Execution Planning and Orchestration"
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           current_task = StateManager.get_current_task(state)
           active_capability_names = state.get('planning_active_capabilities')
           
           # Create execution plan using LLM
           execution_plan = await asyncio.to_thread(
               get_chat_completion,
               message=system_prompt,
               model_config=model_config,
               output_model=ExecutionPlan
           )
           
           # Validate plan (check capabilities exist, ensure response step)
           validated_plan = _validate_and_fix_execution_plan(
               execution_plan, current_task, logger
           )
           
           return {
               "planning_execution_plan": validated_plan,
               "planning_current_step_index": 0
           }

Message Processing Flow
=======================

A user message flows through the complete architecture:

1. **Gateway** receives message and creates initial state
2. **Router** determines next action → "task_extraction" (no task yet)
3. **Task Extraction** analyzes conversation → returns structured task
4. **Router** checks state again → "classifier" (has task, no capabilities)
5. **Classification** selects relevant capabilities → returns capability list
6. **Router** checks state again → "orchestrator" (has capabilities, no plan)
7. **Orchestrator** creates execution plan → returns validated plan
8. **Router** executes plan step by step → routes through each capability → "END"

Graph Construction
==================

The framework uses LangGraph with router-controlled flow:

.. code-block:: python

   from framework.graph.graph_builder import create_graph
   from framework.registry import get_registry

   # Initialize registry and create graph
   registry = get_registry()
   graph = create_graph(registry, use_postgres=True)

   # Graph structure:
   # - Entry point: "router"
   # - Router uses conditional edges to route to any registered node
   # - All nodes route back to router except terminal nodes (respond, error)
   # - Terminal nodes route to END

Error Handling and Retry Logic
==============================

The framework includes sophisticated error handling with node-specific retry policies:

.. code-block:: python

   @infrastructure_node
   class TaskExtractionNode(BaseInfrastructureNode):
       @staticmethod
       def classify_error(exc: Exception, context: dict):
           # Retry on network/API timeouts
           if isinstance(exc, (ConnectionError, TimeoutError)):
               return ErrorClassification(
                   severity=ErrorSeverity.RETRIABLE,
                   user_message="Network timeout, retrying...",
                   technical_details=str(exc)
               )
           # Critical errors don't retry
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message="Task extraction failed",
               technical_details=str(exc)
           )
       
       @staticmethod
       def get_retry_policy() -> Dict[str, Any]:
           return {
               "max_attempts": 3,
               "delay_seconds": 1.0,
               "backoff_factor": 1.5
           }

Approval Workflows
==================

The framework supports human-in-the-loop approval for sensitive operations:

.. code-block:: python

   # Enable planning mode with slash command
   user_input = "/planning Find and modify beam parameters"
   gateway_result = await gateway.process_message(user_input, graph, config)

   # Orchestrator will interrupt for approval
   # User responds with "yes" or "no"
   approval_result = await gateway.process_message("yes", graph, config)
   # Execution resumes with approved plan

Interface Integration
=====================

All interfaces use the same Gateway pattern:

.. code-block:: python

   # CLI Interface
   class CLI:
       async def _process_user_input(self, user_input: str):
           result = await self._gateway.process_message(
               user_input, self._graph, self._config
           )
           # Handle result...

   # OpenWebUI Pipeline
   class Pipeline:
       def _execute_pipeline(self, user_message: str, ...):
           result = loop.run_until_complete(
               self._gateway.process_message(user_message, self._graph, config)
           )
           # Handle result...

Architecture Benefits
=====================

**Reliability Through Single Entry Point**
   - All message processing centralized in Gateway
   - Consistent preprocessing and state management
   - Single point of error handling and logging

**Performance Through State-Based Routing**
   - Router makes decisions based on current state
   - No redundant processing or state checks
   - Efficient execution plan following

**Maintainability Through Clear Separation**
   - Gateway handles preprocessing only
   - Router handles routing decisions only
   - Infrastructure nodes handle specific processing steps
   - Capabilities handle business logic

Next Steps
==========

1. **Learn State Management**: :doc:`../03_core-framework-systems/01_state-management-architecture` - How state flows through the system
2. **Explore Registry System**: :doc:`../03_core-framework-systems/03_registry-and-discovery` - How components are discovered and registered
3. **Build Your First Capability**: :doc:`../02_quick-start-patterns/01_building-your-first-capability` - Hands-on implementation
4. **Understand Error Handling**: :doc:`../04_infrastructure-components/06_error-handling-infrastructure` - Comprehensive error management

Related API Reference
=====================

- :doc:`../../api_reference/02_infrastructure/01_gateway` - Complete Gateway API
- :doc:`../../api_reference/02_infrastructure/05_execution-control` - Router and routing logic
- :doc:`../../api_reference/02_infrastructure/02_task-extraction` - Task extraction methods
- :doc:`../../api_reference/02_infrastructure/03_classification` - Capability selection API