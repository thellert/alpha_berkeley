Error Handling Infrastructure: Intelligent Error Recovery and Communication
============================================================================

.. currentmodule:: framework.infrastructure.error_node

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - How the framework provides centralized error handling with LLM-generated responses
   - Error classification systems and retry policies for different failure types
   - Recovery strategy implementation and graceful degradation patterns
   - Best practices for building resilient error experiences

   **Prerequisites:** Understanding of :doc:`03_classification-and-routing` and :doc:`05_message-generation`
   
   **Time Investment:** 20 minutes for complete understanding

Core Problem
------------

Agentic systems present a unique opportunity to handle errors more intelligently than traditional software applications. With capable language models at our disposal and users who are often domain experts rather than developers, we can move beyond simply throwing stack traces at users:

- **Error Context Complexity:** Errors occur at different levels with varying context
- **User Communication:** Domain experts need actionable explanations, not technical stack traces
- **Recovery Strategy Selection:** Different error types require different recovery approaches  
- **State Consistency:** Errors must be handled without corrupting execution flow
- **LLM Capabilities:** Language models excel at interpreting code errors and generating user-friendly explanations

**Framework Solution:** Centralized error processing with LLM-generated responses and classification-based recovery.

.. admonition:: 🚧 Development Note
   :class: info

   The LLM-powered error analysis system is actively being optimized. Current focus areas include refining context provision to language models and improving response quality. Users should expect that generated error messages may not always be as informative as desired while these improvements are being implemented.

Architecture Overview
---------------------

The error handling system combines intelligent classification, automated recovery, and user-friendly communication:

.. code-block:: python

   @infrastructure_node
   class ErrorNode(BaseInfrastructureNode):
       name = "error"
       description = "Error Response Generation"
       
       @staticmethod
       def classify_error(exc: Exception, context: dict):
           # FATAL classification prevents infinite loops
           return ErrorClassification(
               severity=ErrorSeverity.FATAL,
               user_message="Error node failed during error handling"
           )
       
       @staticmethod
       async def execute(state: AgentState, **kwargs):
           try:
               # Create error context from state
               error_context = _create_error_context_from_state(state)
               
               # Generate LLM response with context
               response = await _generate_error_response(error_context)
               
               return {"messages": [AIMessage(content=response)]}
               
           except Exception as e:
               # Fallback response if error handling fails
               return {"messages": [AIMessage(content=_create_fallback_response(e, state))]}

**Key Principles:**
1. **Centralized Processing:** Single error node handles all scenarios
2. **Context Preservation:** Errors don't lose conversation or execution context
3. **Graceful Degradation:** System continues functioning when components fail
4. **User-Friendly Communication:** Technical errors become actionable explanations

Error Classification System
---------------------------

Different error types trigger appropriate recovery strategies:

.. code-block:: python

   class ErrorType(Enum):
       TIMEOUT = "timeout"
       STEP_FAILURE = "step_failure"
       SAFETY_LIMIT = "safety_limit"
       RETRIABLE_FAILURE = "retriable_failure"
       RECLASSIFICATION_LIMIT = "reclassification_limit"
       CRITICAL_ERROR = "critical_error"
       INFRASTRUCTURE_ERROR = "infrastructure_error"
       EXECUTION_KILLED = "execution_killed"

**Classification Example:**

.. code-block:: python

   # Example capability error classification
   @staticmethod
   def classify_error(exc: Exception, context: dict):
       # Retry network timeouts
       if isinstance(exc, (ConnectionError, TimeoutError)):
           return ErrorClassification(
               severity=ErrorSeverity.RETRIABLE,
               user_message="Network timeout, retrying...",
               technical_details=str(exc)
           )
       
       # Don't retry validation errors
       if isinstance(exc, (ValueError, TypeError)):
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message="Configuration error",
               technical_details=str(exc)
           )

Error Context Generation
------------------------

System automatically creates comprehensive error context:

.. code-block:: python

   @dataclass
   class ErrorContext:
       error_type: ErrorType
       error_message: str
       failed_operation: str
       current_task: str
       capability_name: Optional[str] = None
       technical_details: Optional[str] = None
       total_operations: int = 0
       execution_time: Optional[float] = None
       retry_count: Optional[int] = None
       successful_steps: List[str] = None
       failed_steps: List[str] = None
       capability_suggestions: List[str] = None

**Context Creation:**

.. code-block:: python

   def _create_error_context_from_state(state: AgentState) -> ErrorContext:
       # Get current task from task state
       current_task = state.get("task_current_task", "Unknown task")
       
       # Get error information that was set by the router
       error_info = state.get('control_error_info')
       if not isinstance(error_info, dict):
           error_info = {}
       
       # Extract error details from router-provided error info
       capability_name = error_info.get('capability_name') or error_info.get('node_name')
       original_error = error_info.get('original_error', 'Unknown error occurred')
       user_message = error_info.get('user_message', original_error)
       technical_details = error_info.get('technical_details', original_error)
       execution_time = error_info.get('execution_time', 0.0)
       
       # Determine error type based on classification severity
       error_classification = error_info.get('classification')
       if error_classification and hasattr(error_classification, 'severity'):
           severity_value = getattr(error_classification.severity, 'value', str(error_classification.severity))
           
           if severity_value == "retriable":
               error_type = ErrorType.RETRIABLE_FAILURE  
           elif severity_value == "replanning":
               error_type = ErrorType.RECLASSIFICATION_LIMIT
           elif severity_value == "critical":
               error_type = ErrorType.CRITICAL_ERROR
           else:
               error_type = ErrorType.CRITICAL_ERROR
       else:
           error_type = ErrorType.CRITICAL_ERROR
       
       return ErrorContext(
           error_type=error_type,
           error_message=user_message,
           failed_operation=capability_name or "Unknown operation",
           current_task=current_task,
           capability_name=capability_name,
           technical_details=technical_details,
           execution_time=execution_time,
           retry_count=state.get('control_retry_count', 0),
           total_operations=StateManager.get_current_step_index(state) + 1
       )

LLM-Generated Error Responses
-----------------------------

Error responses combine structured reports with LLM analysis:

.. code-block:: python

   async def _generate_error_response(error_context: ErrorContext) -> str:
       # Build structured error report
       error_report_sections = _build_structured_error_report(error_context)
       
       # Generate LLM explanation
       llm_explanation = await asyncio.to_thread(_generate_llm_explanation, error_context)
       
       return f"{error_report_sections}\n\n{llm_explanation}"

**Structured Report Components:**

.. code-block:: python

   def _build_structured_error_report(error_context: ErrorContext) -> str:
       timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       report_sections = [
           f"⚠️  **ERROR REPORT** - {timestamp}",
           f"**Error Type:** {error_context.error_type.value.upper()}",
           f"**Task:** {error_context.current_task}",
           f"**Failed Operation:** {error_context.failed_operation}",
           f"**Error Message:** {error_context.error_message}"
       ]
       
       # Add execution statistics
       if error_context.execution_time:
           report_sections.append(f"**Execution Time:** {error_context.execution_time:.1f}s")
       
       if error_context.retry_count:
           report_sections.append(f"**Retry Attempts:** {error_context.retry_count}")
       
       return "\n".join(report_sections)

**LLM Analysis Generation:**

.. code-block:: python

   def _generate_llm_explanation(error_context: ErrorContext) -> str:
       try:
           capabilities_overview = get_registry().get_capabilities_overview()
           
           prompt_provider = get_framework_prompts()
           error_builder = prompt_provider.get_error_analysis_prompt_builder()
           
           prompt = error_builder.get_system_instructions(
               capabilities_overview=capabilities_overview,
               error_context=error_context
           )
           
           explanation = get_chat_completion(
               model_config=get_model_config("framework", "response"),
               message=prompt,
               max_tokens=500
           )
           
           return f"**Analysis:** {explanation.strip()}"
           
       except Exception:
           return "**Analysis:** Error details are provided in the structured report above."

Retry Policy Framework
----------------------

Router handles retries embedded in conditional edge function:

.. code-block:: python

   def router_conditional_edge(state: AgentState) -> str:
       # Check for errors first
       if state.get('control_has_error', False):
           error_info = state.get('control_error_info', {})
           error_classification = error_info.get('classification')
           capability_name = error_info.get('capability_name')
           
           if error_classification and capability_name:
               retry_count = state.get('control_retry_count', 0)
               retry_policy = error_info.get('retry_policy', {})
               max_retries = retry_policy.get('max_attempts', 3)
               
               if error_classification.severity == ErrorSeverity.RETRIABLE:
                   if retry_count < max_retries:
                       # Apply exponential backoff
                       delay = retry_policy.get('delay_seconds', 1.0)
                       backoff = retry_policy.get('backoff_factor', 1.5)
                       actual_delay = delay * (backoff ** retry_count)
                       
                       time.sleep(actual_delay)
                       state['control_retry_count'] = retry_count + 1
                       
                       return capability_name  # Retry same capability
                   else:
                       return "error"  # Route to error node
               
               elif error_classification.severity == ErrorSeverity.REPLANNING:
                   return "orchestrator"  # Route for re-planning
               
               else:
                   return "error"  # Route to error node
       
       # Normal routing logic continues...

**Recovery Strategies:**
- **RETRIABLE:** Automatic retry with exponential backoff
- **REPLANNING:** Route to orchestrator for new execution plan
- **CRITICAL:** Route to error node for user communication
- **FATAL:** Terminate execution immediately

Error Context Enhancement
-------------------------

System automatically enhances context with execution history:

.. code-block:: python

   def _populate_error_context(error_context: ErrorContext, state: AgentState):
       # Generate execution summary from execution_step_results (ordered by step_index)
       step_results = state.get("execution_step_results", {})
       if step_results:
           # Sort by step_index for proper ordering
           ordered_results = sorted(step_results.items(), key=lambda x: x[1].get('step_index', 0))
           
           for step_key, result in ordered_results:
               step_index = result.get('step_index', 0)
               capability_name = result.get('capability', 'unknown')
               task_objective = result.get('task_objective', capability_name)
               
               if result.get('success', False):
                   error_context.successful_steps.append(f"Step {step_index + 1}: {task_objective}")
               else:
                   error_context.failed_steps.append(f"Step {step_index + 1}: {task_objective} - Failed")
       
       # Use capability-specific suggestions if available, otherwise generate generic ones
       if not error_context.capability_suggestions:
           error_context.capability_suggestions = _generate_generic_suggestions(error_context.error_type)

**Generic Recovery Suggestions:**

.. code-block:: python

   def _generate_generic_suggestions(error_type: ErrorType) -> List[str]:
       generic_suggestions_map = {
           ErrorType.TIMEOUT: [
               "Reduce request complexity or scope",
               "Specify narrower time ranges for data queries"
           ],
           ErrorType.STEP_FAILURE: [
               "Rephrase request with clearer parameters",
               "Simplify query complexity"
           ],
           ErrorType.SAFETY_LIMIT: [
               "Reduce request scope to single operation",
               "Break complex tasks into sequential steps"
           ],
           ErrorType.RETRIABLE_FAILURE: [
               "Retry request (temporary service issue)",
               "Check system service status"
           ],
           ErrorType.RECLASSIFICATION_LIMIT: [
               "Clarify request with specific technical parameters",
               "Use domain-specific terminology"
           ],
           ErrorType.CRITICAL_ERROR: [
               "Contact user support for assistance",
               "Verify system prerequisites and permissions"
           ],
           ErrorType.INFRASTRUCTURE_ERROR: [
               "Contact user support for assistance",
               "Verify access permissions for requested resources"
           ],
           ErrorType.EXECUTION_KILLED: [
               "Reduce operation scope or complexity",
               "Review request against system constraints"
           ]
       }
       
       return generic_suggestions_map.get(error_type, [
           "Rephrase request with clearer parameters",
           "Simplify operation complexity"
       ])

Integration Patterns
--------------------

**Capability Error Classification:**

.. code-block:: python

   class MyCapability(BaseCapability):
       @staticmethod
       def classify_error(exc: Exception, context: dict):
           # Retry network timeouts
           if isinstance(exc, (ConnectionError, TimeoutError)):
               return ErrorClassification(
                   severity=ErrorSeverity.RETRIABLE,
                   user_message="Network issue detected, retrying..."
               )
           
           # Default to critical for unknown errors
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message=f"Unexpected error: {exc}"
           )

**Custom Retry Policies:**

.. code-block:: python

   @staticmethod
   def get_retry_policy() -> Dict[str, Any]:
       return {
           "max_attempts": 5,      # More attempts for network operations
           "delay_seconds": 2.0,   # Longer delay for external services
           "backoff_factor": 2.0   # Exponential backoff
       }

Best Practices
--------------

**Error Classification Guidelines:**
- Use RETRIABLE for network/temporary issues
- Use CRITICAL for configuration/validation errors  
- Use REPLANNING for capability selection issues
- Use FATAL only for error node failures

**State Management:**
- Use ``control_error_info`` for error details
- Use ``control_retry_count`` for tracking attempts
- Use ``control_has_error`` as the error state flag

**User Communication:**
- Provide structured error reports with timestamps
- Include execution context and recovery suggestions
- Use LLM-generated explanations for clarity

Troubleshooting
---------------

**Error Node Infinite Loops:**
ErrorNode uses FATAL classification to prevent loops when error handling fails.

**Missing Error Context:**
System provides fallback responses when error context creation fails.

**Router Retry Issues:**
Retry handling is embedded in ``router_conditional_edge()`` - check state field consistency.

Next Steps
----------

- :doc:`../05_production-systems/01_human-approval-workflows` - Error integration with approval systems
- :doc:`../03_core-framework-systems/01_state-management-architecture` - State management during errors
- :doc:`05_message-generation` - How error responses are formatted

Error Handling Infrastructure provides the resilience and user-friendly error communication that makes the Alpha Berkeley Framework production-ready, ensuring graceful failure handling while keeping users informed and engaged.