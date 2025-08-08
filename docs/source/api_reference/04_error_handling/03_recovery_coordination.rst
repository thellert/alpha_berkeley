=====================
Recovery Coordination
=====================

Router-based recovery strategies and infrastructure error coordination.

.. currentmodule:: framework

The framework implements intelligent recovery coordination through a centralized router system that automatically determines recovery strategies based on error classification. The system coordinates between retry mechanisms, orchestrator replanning, and graceful termination.

Router Recovery System
======================

Router Conditional Edge
-----------------------

.. autofunction:: framework.infrastructure.router_node.router_conditional_edge

   Central recovery coordination implementing the complete recovery strategy.

   **Recovery Flow:**

   1. **Manual Retry Handling** (checked first):
      - RETRIABLE errors: retry with backoff if attempts remain
      - REPLANNING errors: route to orchestrator if planning attempts remain
      - CRITICAL errors: route to error node immediately

   2. **Normal Routing Logic**:
      - Check execution state and route to next capability or termination

   **RETRIABLE Error Recovery:**
   
   .. code-block:: python
   
      if retry_count < max_retries:
          # Apply exponential backoff
          delay = delay_seconds * (backoff_factor ** (retry_count - 1))
          time.sleep(delay)
          return capability_name  # Retry same capability
      else:
          return "error"  # Retries exhausted

   **REPLANNING Error Recovery:**
   
   .. code-block:: python
   
      if plans_created < max_planning_attempts:
          return "orchestrator"  # Create new execution plan
      else:
          return "error"  # Planning attempts exhausted



RouterNode Infrastructure
-------------------------

.. autoclass:: framework.infrastructure.router_node.RouterNode
   :members:
   :show-inheritance:

   Infrastructure node that coordinates routing decisions and state management.

Orchestrator Replanning
=======================

.. automethod:: framework.infrastructure.orchestration_node.OrchestrationNode.execute

   When routing to orchestrator due to REPLANNING errors:

   1. **Plan Creation**: Generate new execution plan based on current task
   2. **Capability Validation**: Ensure all planned capabilities exist
   3. **State Updates**: Clear error state and increment plan counter
   4. **Limits**: Respect maximum planning attempts to prevent infinite loops

   **Replanning Triggers:**
   
   - Missing or invalid input data requiring different approach
   - Capability execution strategy failures
   - Validation errors that can be resolved with alternative plans
   - Orchestrator capability hallucination (auto-detected and corrected)

Error Response Generation
=========================

ErrorNode System
----------------

When recovery strategies are exhausted, the system routes to the **ErrorNode** for intelligent error response generation:

.. autoclass:: framework.infrastructure.error_node.ErrorNode
   :members:
   :show-inheritance:

   Provides comprehensive error handling with LLM-powered analysis.

   **Features:**

   - **Structured Error Reports**: Automatic generation from execution state
   - **LLM Analysis**: Intelligent error explanation using framework prompts  
   - **Recovery Suggestions**: Context-aware suggestions based on error type
   - **User-Friendly Messages**: Professional error communication

**Integration with Recovery System:**

.. code-block:: python

   # Router coordinates complete recovery flow
   if error_classification.severity == ErrorSeverity.RETRIABLE:
       # ... retry logic ...
       if retries_exhausted:
           return "error"  # Route to ErrorNode
   elif error_classification.severity == ErrorSeverity.REPLANNING:
       # ... replanning logic ...
       if planning_exhausted:
           return "error"  # Route to ErrorNode
   elif error_classification.severity == ErrorSeverity.CRITICAL:
       return "error"  # Route directly to ErrorNode

Infrastructure Error Classification
===================================

Classification Node Example
---------------------------

.. automethod:: framework.infrastructure.classification_node.ClassificationNode.classify_error

   Built-in error classification for classifier operations with LLM-aware retry logic.

   .. code-block:: python

      @staticmethod
      def classify_error(exc: Exception, context: Dict[str, Any]) -> ErrorClassification:
          # Retry LLM timeouts and network errors
          if hasattr(exc, '__class__') and 'timeout' in exc.__class__.__name__.lower():
              return ErrorClassification(
                  severity=ErrorSeverity.RETRIABLE,
                  user_message="Classification service temporarily unavailable, retrying...",
                  technical_details=f"LLM timeout: {str(exc)}"
              )
          
          if isinstance(exc, (ConnectionError, TimeoutError)):
              return ErrorClassification(
                  severity=ErrorSeverity.RETRIABLE,
                  user_message="Network connectivity issues during classification, retrying...",
                  technical_details=f"Network error: {str(exc)}"
              )
          
          # Default to critical for unknown infrastructure errors
          return ErrorClassification(
              severity=ErrorSeverity.CRITICAL,
              user_message=f"Classification failed: {exc}",
              technical_details=str(exc)
          )

Custom Retry Policies
---------------------

.. automethod:: framework.infrastructure.classification_node.ClassificationNode.get_retry_policy

   Custom retry policy for LLM-based classification operations.

   .. code-block:: python

      @staticmethod
      def get_retry_policy() -> Dict[str, Any]:
          return {
              "max_attempts": 4,        # More attempts for LLM classification
              "delay_seconds": 1.0,     # Moderate delay for parallel LLM calls
              "backoff_factor": 1.8     # Moderate backoff to handle rate limiting
          }

Recovery Strategy Examples
==========================

Network-Aware Classification
----------------------------

.. code-block:: python

   @staticmethod
   def classify_error(exc: Exception, context: dict) -> ErrorClassification:
       """Network-aware error classification."""
       if isinstance(exc, (ConnectionError, TimeoutError)):
           return ErrorClassification(
               severity=ErrorSeverity.RETRIABLE,
               user_message="Network issue detected, retrying...",
               technical_details=str(exc)
           )
       elif isinstance(exc, AuthenticationError):
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message="Authentication failed",
               technical_details=str(exc)
           )
       return ErrorClassification(
           severity=ErrorSeverity.CRITICAL,
           user_message=f"Unexpected error: {exc}",
           technical_details=str(exc)
       )

Data Validation with Replanning
-------------------------------

.. code-block:: python

   @staticmethod
   def classify_error(exc: Exception, context: dict) -> ErrorClassification:
       """Data validation with intelligent replanning."""
       if isinstance(exc, KeyError) and "context" in str(exc):
           return ErrorClassification(
               severity=ErrorSeverity.REPLANNING,
               user_message="Required data not available, trying different approach",
               technical_details=f"Missing context data: {str(exc)}"
           )
       elif isinstance(exc, ValidationError):
           return ErrorClassification(
               severity=ErrorSeverity.REPLANNING,
               user_message="Invalid input format, generating new plan",
               technical_details=str(exc)
           )
       return ErrorClassification(
           severity=ErrorSeverity.CRITICAL,
           user_message=f"Data processing error: {exc}",
           technical_details=str(exc)
       )

Custom Retry Policies
---------------------

.. code-block:: python

   # Aggressive retry for network-dependent operations
   @staticmethod
   def get_retry_policy() -> Dict[str, Any]:
       return {
           "max_attempts": 5,
           "delay_seconds": 2.0,
           "backoff_factor": 2.0
       }
   
   # Conservative retry for expensive operations  
   @staticmethod
   def get_retry_policy() -> Dict[str, Any]:
       return {
           "max_attempts": 2,
           "delay_seconds": 0.1,
           "backoff_factor": 1.0
       }

Complete Recovery Flow
======================

The framework implements a three-tier recovery strategy coordinated by the router:

.. code-block:: python

   # Router coordinates all recovery strategies
   if error_classification.severity == ErrorSeverity.RETRIABLE:
       if retry_count < max_retries:
           # Apply exponential backoff: delay * (backoff_factor ** retry_count)
           actual_delay = delay_seconds * (backoff_factor ** (retry_count - 1))
           time.sleep(actual_delay)
           return capability_name  # Retry same capability
       else:
           return "error"  # Retries exhausted → ErrorNode
   
   elif error_classification.severity == ErrorSeverity.REPLANNING:
       if plans_created < max_planning_attempts:
           return "orchestrator"  # Create new execution plan
       else:
           return "error"  # Planning attempts exhausted → ErrorNode
   
   elif error_classification.severity == ErrorSeverity.CRITICAL:
       return "error"  # Immediate termination → ErrorNode

**Final Error Handling**: When all recovery strategies are exhausted, the **ErrorNode** generates intelligent error responses with LLM-powered analysis and recovery suggestions.

.. seealso::
   
   :doc:`01_classification_system`
       Error classification and severity management
   
   :doc:`02_exception_reference`
       Complete exception hierarchy with inheritance structure
   
   :doc:`../02_infrastructure/05_execution-control`
       **ErrorNode**, **RouterNode**, and complete execution control flow