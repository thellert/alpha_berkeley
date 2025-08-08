Gateway
=======

.. currentmodule:: framework.infrastructure.gateway

The Gateway provides the single entry point for all message processing in the Alpha Berkeley Framework. All interfaces (CLI, OpenWebUI, etc.) should call ``Gateway.process_message()``.

.. note::
   The Gateway operates external to the compiled graph by design, enabling it to perform
   meta-operations such as approval response processing, state lifecycle management, and
   interrupt detection. This centralized approach simplifies interface implementation by
   removing the need for interfaces to handle complex state management, slash commands,
   or approval workflow logic directly.

Gateway Class
-------------

.. autoclass:: Gateway
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   
   .. rubric:: Key Methods
   
   .. autosummary::
      :nosignatures:
      
      ~Gateway.process_message
      
   .. rubric:: Private Methods
   
   .. autosummary::
      :nosignatures:
      
      ~Gateway._handle_interrupt_flow
      ~Gateway._handle_new_message_flow
      ~Gateway._has_pending_interrupts
      ~Gateway._detect_approval_response
      ~Gateway._extract_resume_payload
      ~Gateway._clear_approval_state
      ~Gateway._parse_slash_commands
      ~Gateway._apply_slash_commands

Gateway Result
--------------

.. autoclass:: GatewayResult
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Registration & Configuration
----------------------------

Gateway is not registered in the framework registry as it serves as the entry point that interfaces call directly. It operates independently of the node execution system and manages state transitions for the framework.

Gateway uses LLM-powered approval detection through the configured ``approval`` model for robust natural language understanding of user approval responses. All other operations are deterministic.

Architecture Overview
---------------------

The Gateway handles:

- State reset for new conversation turns
- Slash command parsing and application
- Approval response detection and resume commands
- Message preprocessing and state updates

**Key Principles:**

- Gateway is the only component that creates state updates
- Interfaces handle presentation only
- Clean separation of concerns with single responsibility

.. seealso::
   
   :class:`~framework.state.AgentState`
       Core state management system used by Gateway
   
   :class:`~framework.state.StateManager`
       Factory functions for creating fresh state instances