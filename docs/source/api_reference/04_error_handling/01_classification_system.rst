=====================
Classification System
=====================

Core error classification and severity management system.

.. currentmodule:: framework.base.errors

The classification system provides the foundation for intelligent error handling by enabling automatic recovery strategy selection based on error severity and context. This system integrates seamlessly with both capability execution and infrastructure operations.

Error Severity Levels
=====================

ErrorSeverity
-------------

.. autoclass:: ErrorSeverity
   :members:
   :undoc-members:
   :show-inheritance:

   Enumeration of error severity levels with recovery strategies:

   - **RETRIABLE**: Retry execution with exponential backoff
   - **REPLANNING**: Route to orchestrator for new execution plan  
   - **CRITICAL**: Graceful termination with user notification
   - **FATAL**: Immediate system termination

   .. rubric:: Usage Pattern

   .. code-block:: python

      if isinstance(exc, ConnectionError):
          return ErrorClassification(severity=ErrorSeverity.RETRIABLE, ...)
      elif isinstance(exc, AuthenticationError):
          return ErrorClassification(severity=ErrorSeverity.CRITICAL, ...)

Classification Results
======================

ErrorClassification
-------------------

.. autoclass:: ErrorClassification
   :members:
   :show-inheritance:

   Structured error analysis result that determines recovery strategy.

   .. rubric:: Usage Pattern

   .. code-block:: python

      classification = ErrorClassification(
          severity=ErrorSeverity.RETRIABLE,
          user_message="Network connection timeout, retrying...",
          technical_details="HTTP request timeout after 30 seconds"
      )

ExecutionError
--------------

.. autoclass:: ExecutionError
   :members:
   :show-inheritance:

   Comprehensive error container with recovery coordination support.

   .. rubric:: Usage Pattern

   .. code-block:: python

      error = ExecutionError(
          severity=ErrorSeverity.RETRIABLE,
          message="Database connection failed",
          capability_name="database_query",
          suggestions=[
              "Check database server status",
              "Verify connection credentials"
          ],
          technical_details="PostgreSQL connection timeout after 30 seconds"
      )

Classification Methods
======================

Base Capability Classification
------------------------------

.. automethod:: framework.base.capability.BaseCapability.classify_error

   Domain-specific error classification for capabilities. Override this method to provide sophisticated error handling based on specific failure modes.

   .. rubric:: Classification Strategy

   .. code-block:: python

      @staticmethod
      def classify_error(exc: Exception, context: dict) -> ErrorClassification:
          if isinstance(exc, ConnectionError):
              return ErrorClassification(
                  severity=ErrorSeverity.RETRIABLE,
                  user_message="Network issue detected, retrying...",
                  technical_details=str(exc)
              )
          return ErrorClassification(
              severity=ErrorSeverity.CRITICAL,
              user_message=f"Unexpected error: {exc}",
              technical_details=str(exc)
          )

Infrastructure Node Classification
----------------------------------

.. automethod:: framework.base.nodes.BaseInfrastructureNode.classify_error

   Conservative error classification for infrastructure nodes. Infrastructure nodes handle system-critical functions, so failures typically require immediate attention.

   .. rubric:: Conservative Strategy

   .. code-block:: python

      @staticmethod
      def classify_error(exc: Exception, context: dict) -> ErrorClassification:
          # Infrastructure defaults to critical for fast failure
          return ErrorClassification(
              severity=ErrorSeverity.CRITICAL,
              user_message=f"Infrastructure error: {exc}",
              technical_details=str(exc)
          )

Retry Policy Configuration
==========================

.. automethod:: framework.base.capability.BaseCapability.get_retry_policy

   Retry policy configuration for failure recovery strategies.

   **Default Policy:**
   
   .. code-block:: python
   
      {
          "max_attempts": 3,        # Total attempts including initial
          "delay_seconds": 0.5,     # Base delay before first retry
          "backoff_factor": 1.5     # Exponential backoff multiplier
      }

.. automethod:: framework.base.nodes.BaseInfrastructureNode.get_retry_policy

   Conservative retry policy for infrastructure operations.

   **Infrastructure Policy:**
   
   .. code-block:: python
   
      {
          "max_attempts": 2,        # Fast failure for infrastructure
          "delay_seconds": 0.2,     # Quick retry attempt
          "backoff_factor": 1.0     # No backoff
      }

Integration Pattern
===================

Basic Error Handling
--------------------

.. code-block:: python

   try:
       result = await capability.execute(state)
   except Exception as exc:
       # Classify error for recovery strategy
       classification = capability.classify_error(exc, context)
       
       if classification.severity == ErrorSeverity.RETRIABLE:
           # Handle with retry policy
           policy = capability.get_retry_policy()
           await retry_with_backoff(capability, state, policy)
       elif classification.severity == ErrorSeverity.REPLANNING:
           # Route to orchestrator for new execution plan
           return "orchestrator"
       elif classification.severity == ErrorSeverity.CRITICAL:
           # End execution with clear error message
           raise ExecutionError(
               severity=ErrorSeverity.CRITICAL,
               message=classification.user_message,
               technical_details=classification.technical_details
           )

.. seealso::

   :doc:`02_exception_reference`
       Complete catalog of framework exceptions
   
   :doc:`03_recovery_coordination`
       Router coordination and recovery strategies