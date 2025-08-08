Gateway Architecture: Universal Message Processing Entry Point
==============================================================

.. currentmodule:: framework.infrastructure.gateway

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - How Gateway centralizes all message processing logic
   - State lifecycle management and conversation handling
   - Slash command integration and approval workflow coordination
   - Interface implementation patterns

   **Prerequisites:** Understanding of :doc:`../03_core-framework-systems/01_state-management-architecture`
   
   **Time Investment:** 15 minutes for complete understanding

Core Concept
------------

Gateway serves as the **single entry point** for all message processing, eliminating interface duplication and ensuring consistent state management across CLI, web, and API interfaces.

**Problem Solved:** Without centralized processing, each interface duplicates message logic, state creation, and approval handling.

**Solution:** All interfaces call ``Gateway.process_message()`` - Gateway handles preprocessing, interfaces handle presentation.

Architecture
------------

.. code-block:: python

   from framework.infrastructure.gateway import Gateway
   
   # Universal pattern for all interfaces
   gateway = Gateway()
   result = await gateway.process_message(user_input, graph, config)
   
   # Execute based on result type
                   if result.resume_command:
       # Approval flow resumption
       response = await graph.ainvoke(result.resume_command, config=config)
                   elif result.agent_state:
       # Normal conversation turn
       response = await graph.ainvoke(result.agent_state, config=config)

Key Features
------------

**State Authority**
   Gateway is the only component that creates agent state, ensuring consistency.

**Slash Commands**
   Built-in parsing for ``/planning:on``, ``/approval:enabled``, ``/debug:on``.

**Approval Integration**
   Automatic detection of approval/rejection responses with LangGraph interrupt handling.

**Interface Agnostic**
   Same processing logic for CLI, OpenWebUI, APIs, or custom interfaces.

Implementation Patterns
-----------------------

**Simple Interface Integration**

.. code-block:: python

   class MyInterface:
       def __init__(self):
           self.gateway = Gateway()
           self.graph = create_graph()
           
       async def handle_message(self, message: str) -> str:
           result = await self.gateway.process_message(message, self.graph, self.config)
           
           if result.error:
               return f"Error: {result.error}"
           
           # Execute and extract response
           execution_input = result.resume_command or result.agent_state
           response = await self.graph.ainvoke(execution_input, config=self.config)
           return self._extract_response(response)

**Streaming Interface Integration**

.. code-block:: python

   async def handle_streaming(self, message: str):
       result = await self.gateway.process_message(message, self.graph, self.config)
           
           if result.error:
           yield {"error": result.error}
               return
           
       # Stream execution
           execution_input = result.resume_command or result.agent_state
           async for chunk in self.graph.astream(execution_input, config=self.config):
           yield chunk

State Management
----------------

Gateway automatically handles:

- **Fresh state creation** for new conversation turns
- **Persistent field preservation** (execution history, user preferences)
- **Slash command application** before execution
- **Approval state injection** for interrupt resumption

**State Creation Pattern:**

.. code-block:: python

   # Gateway handles this automatically
   fresh_state = StateManager.create_fresh_state(
       user_input=cleaned_message,
       current_state=current_state  # Preserves persistent fields
   )

Slash Commands
--------------

Gateway parses and applies slash commands automatically:

- ``/planning`` or ``/planning:on`` - Enable planning mode
- ``/planning:off`` - Disable planning mode  
- ``/approval:on`` - Enable approval workflows
- ``/approval:selective`` - Selective approval mode
- ``/debug:on`` - Enable debug logging

Commands are parsed from user input and applied to ``agent_control`` state before execution.

.. _planning-mode-example:

.. dropdown:: 💡 Planning Mode Example
   :open:
   :color: info
   :icon: light-bulb

   **Real CLI Session Showing Planning Mode**

   .. code-block:: text
   
      👤 You: /planning What's the weather in San Francisco?
      🔄 Processing: /planning What's the weather in San Francisco?
      ✅ Processed commands: ['planning']
      🔄 Extracting actionable task from conversation
      🔄 Analyzing task requirements...
      🔄 Generating execution plan...
      🔄 Requesting plan approval...
      
      ⚠️ **HUMAN APPROVAL REQUIRED** ⚠️
      
      **Planned Steps (2 total):**
      **Step 1:** Retrieve current weather conditions for San Francisco including temperature, weather conditions, and timestamp (current_weather)
      **Step 2:** Present the current weather information for San Francisco to the user in a clear and readable format (respond)
      
      **To proceed, respond with:**
      - **`yes`** to approve and execute the plan
      - **`no`** to cancel this operation
      
      👤 You: yes
      🔄 Processing: yes
      🔄 Resuming from interrupt...
      🔄 Using approved execution plan
      🔄 Executing current_weather... (10%)
      🔄 Weather retrieved: San Francisco - 18.0°C
      🔄 Executing respond... (10%)
      📊 Execution completed (execution_step_results: 2 records)
      
      🤖 Here is the current weather in San Francisco:
      As of today, the weather in San Francisco is **18.0°C and Partly Cloudy**.

   Planning mode provides transparent oversight of multi-step operations before execution begins.

Approval Workflow Integration
-----------------------------

Gateway automatically detects approval responses using LLM classification and creates resume commands:

**LLM-Powered Approval Detection:**
   Uses the configured ``approval`` model from ``framework.models`` to classify user responses as approval or rejection.

**Approval Model Configuration:**
   Configured in ``src/framework/config.yml`` under ``framework.models.approval`` (Ollama with Mistral 7B by default).

**Fail-Safe Behavior:**
   If LLM classification fails for any reason, the system defaults to "not approved" and logs a clear warning message.

**Resume Command Creation:**
   Gateway extracts interrupt payload and injects approval decision into agent state for processing.

Error Handling
--------------

Gateway provides graceful error handling:

.. code-block:: python

   # Gateway returns structured results
   @dataclass
   class GatewayResult:
       agent_state: Optional[Dict[str, Any]] = None
       resume_command: Optional[Command] = None
       error: Optional[str] = None
       slash_commands_processed: List[str] = None
       approval_detected: bool = False

Common error scenarios:
- Interrupt detection failures fall back to new message processing
- State access errors are handled gracefully
- Approval parsing failures provide clear guidance

Validation
----------

The Gateway pattern is validated by existing interfaces:

- **CLI Interface** (``interfaces/CLI/direct_conversation.py``)
- **OpenWebUI Pipeline** (``interfaces/openwebui/main.py``)

Both follow the documented patterns exactly, providing real-world validation.

Best Practices
--------------

**Do:**
- Always use Gateway for message processing
- Handle both normal and approval flows
- Implement proper error handling for Gateway results

**Don't:**
- Create agent state manually in interfaces
- Duplicate approval detection logic
- Parse slash commands outside Gateway

Integration Example
-------------------

Complete CLI interface using Gateway:

.. code-block:: python

   class CLIInterface:
       def __init__(self):
           self.gateway = Gateway()
           self.graph = create_graph()
           self.config = {"configurable": {"thread_id": "cli_session"}}
       
       async def conversation_loop(self):
           while True:
               user_input = input("You: ").strip()
               if user_input.lower() in ['exit', 'quit']:
                   break
               
               # Process through Gateway
               result = await self.gateway.process_message(
                   user_input, self.graph, self.config
               )
               
               if result.error:
                   print(f"Error: {result.error}")
                   continue
               
               # Execute appropriate flow
               if result.resume_command:
                   response = await self.graph.ainvoke(result.resume_command, self.config)
               else:
                   response = await self.graph.ainvoke(result.agent_state, self.config)
               
               print(f"Agent: {self._extract_message(response)}")

Next Steps
----------

- :doc:`02_task-extraction-system` - First step in message processing pipeline
- :doc:`../05_production-systems/01_human-approval-workflows` - Advanced approval patterns
- :doc:`../03_core-framework-systems/01_state-management-architecture` - State management details

Gateway Architecture provides the foundation for consistent, reliable message processing across all interfaces in the Alpha Berkeley Framework.