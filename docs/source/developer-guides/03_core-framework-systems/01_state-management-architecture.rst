=============================
State Management Architecture
=============================

.. currentmodule:: framework.state

The Alpha Berkeley Framework implements a sophisticated state management system built on LangGraph's native patterns for optimal performance and compatibility.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - :class:`AgentState` structure and lifecycle management
   - :class:`StateManager` utilities for state creation and manipulation
   - Best practices for state persistence and context preservation
   - Integration patterns with LangGraph's checkpointing system
   - Performance optimization techniques for state management

   **Prerequisites:** Basic familiarity with LangGraph's MessagesState and Python TypedDict concepts
   
   **Time Investment:** 30-40 minutes for complete understanding

Architecture Overview
=====================

The framework uses a **selective persistence strategy** that leverages LangGraph's native patterns:

**Core Principles:**

1. **LangGraph Native**: Built on MessagesState with automatic message handling
2. **Selective Persistence**: Only capability_context_data persists across conversations  
3. **Execution Scoped**: All other fields reset automatically between graph invocations
4. **Type Safety**: Comprehensive TypedDict definitions with proper type hints
5. **Serialization Ready**: Pure dictionary structures compatible with checkpointing

**Key Components:**

- :class:`AgentState`: Main conversational state extending MessagesState
- :class:`StateManager`: Utilities for state creation and management
- :func:`merge_capability_context_data`: Custom reducer for context persistence

AgentState Structure
====================

AgentState extends LangGraph's MessagesState with framework-specific fields organized by logical prefixes:

**Field Categories:**

.. code-block:: python

   # PERSISTENT FIELD (accumulates across conversations)
   capability_context_data: Dict[str, Dict[str, Dict[str, Any]]]
   
   # EXECUTION-SCOPED FIELDS (reset each invocation)
   
   # Task processing
   task_current_task: Optional[str]
   task_depends_on_chat_history: bool
   task_depends_on_user_memory: bool
   
   # Planning and orchestration
   planning_active_capabilities: List[str]
   planning_execution_plan: Optional[ExecutionPlan]
   planning_current_step_index: int
   
   # Execution tracking
   execution_step_results: Dict[str, Any]
   execution_pending_approvals: Dict[str, ApprovalRequest]
   
   # Control flow
   control_has_error: bool
   control_retry_count: int
   control_needs_reclassification: bool
   
   # Agent control state
   agent_control: Dict[str, Any]

**State Example:**

.. code-block:: python

   state_example = {
       # Persistent context (survives conversation turns)
       "capability_context_data": {
           "PV_ADDRESSES": {
               "beam_current_pvs": {"pvs": ["SR:C01-BI:G02A:CURRENT"], "timestamp": "..."}
           }
       },
       
       # Execution-scoped fields (reset each turn)
       "task_current_task": "Find beam current PV addresses",
       "planning_active_capabilities": ["pv_address_finding"],
       "planning_execution_plan": {"steps": [...]},
       "control_has_error": False,
       "agent_control": {"max_retries": 3}
   }

StateManager
============

StateManager provides the primary interface for state creation and management throughout the framework.

**Creating Fresh State:**

.. code-block:: python

   from framework.state import StateManager
   
   # Create fresh state for new conversation
   fresh_state = StateManager.create_fresh_state(
       user_input="Find beam current PV addresses"
   )
   
   # Preserve context from previous conversation
   new_state = StateManager.create_fresh_state(
       user_input="Show me the latest data for those PVs",
       current_state=previous_state  # Contains accumulated context
   )

**Context Storage:**

.. code-block:: python

   # In a capability execute method
   @staticmethod
   async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
       # Perform capability logic
       pv_data = await find_pv_addresses(user_query)
       
       # Create context object
       pv_context = PVAddresses(
           pvs=pv_data["addresses"],
           description="Found PV addresses for beam current",
           timestamp=datetime.now()
       )
       
       # Store context and return state updates
       step = StateManager.get_current_step(state)
       return StateManager.store_context(
           state, "PV_ADDRESSES", step.get('context_key'), pv_context
       )

**Direct State Updates:**

.. code-block:: python

   # Infrastructure nodes can make direct state updates
   @staticmethod
   async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
       extracted_task = await extract_task_from_messages(state['messages'])
       
       return {
           "task_current_task": extracted_task.task,
           "task_depends_on_chat_history": extracted_task.depends_on_chat_history,
           "task_depends_on_user_memory": extracted_task.depends_on_user_memory
       }

**Accessing State Data:**

.. code-block:: python

   @capability_node
   class DataAnalysisCapability(BaseCapability):
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           current_task = StateManager.get_current_task(state)
           current_step = StateManager.get_current_step(state)
           context = ContextManager(state)
           
           # Access persistent context data
           step_inputs = current_step.get('inputs', [])
           pv_data = None
           for input_spec in step_inputs:
               if 'PV_ADDRESSES' in input_spec:
                   context_key = input_spec['PV_ADDRESSES']
                   pv_data = context.get_context('PV_ADDRESSES', context_key)
                   break
           
           if not pv_data:
               return {"error": "Required PV address data not available"}
           
           # Perform analysis
           analysis_result = await analyze_pv_data(pv_data.pvs, current_task)
           
           # Store results
           analysis_context = DataAnalysisResults(
               analysis=analysis_result,
               source_data=pv_data.pvs,
               timestamp=datetime.now()
           )
           
           return StateManager.store_context(
               state, "ANALYSIS_RESULTS", current_step.get('context_key'), analysis_context
           )

Working Example
===============

.. code-block:: python

   from framework.infrastructure.gateway import Gateway
   from framework.graph import create_graph
   
   async def process_message():
       gateway = Gateway()
       graph = create_graph()
       config = {"configurable": {"thread_id": "demo_thread"}}
       
       result = await gateway.process_message(
           "Find all beam current PV addresses", 
           graph, 
           config
       )
       
       final_state = await graph.ainvoke(result.agent_state, config=config)
       
       # Access results
       context = ContextManager(final_state)
       pv_results = context.get_all_of_type("PV_ADDRESSES")
       
       return pv_results

Best Practices
==============

**State Management:**

- Use StateManager utilities for all state operations
- Only store large data in capability_context_data (persists across conversations)
- Use proper field prefixes for organization (``task_``, ``planning_``, ``execution_``, ``control_``)
- Return state update dictionaries from execute methods

**Context Storage:**

.. code-block:: python

   # ✅ Correct - using StateManager utilities
   context_obj = MyContext(data='value')
   updates = StateManager.store_context(state, 'NEW_TYPE', 'key', context_obj)
   return updates

**Error Handling:**

.. code-block:: python

   # Use state for retry logic
   retry_count = state.get('control_current_step_retry_count', 0)
   if retry_count > 2:
       # Use fallback approach
       pass

**Performance:**

- Only `capability_context_data` persists across conversations
- All execution fields reset automatically for optimal performance
- Leverage ContextManager caching for frequently accessed data

.. seealso::
   :doc:`02_context-management-system`
       Context data management and capability integration patterns
   :doc:`../../api_reference/01_core_framework/index`
       Complete API documentation for core framework components