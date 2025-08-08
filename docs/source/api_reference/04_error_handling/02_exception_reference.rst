===================
Exception Reference
===================

Complete catalog of framework exceptions with inheritance structure and usage patterns.

.. currentmodule:: framework

The framework implements a comprehensive exception hierarchy that provides precise error classification for all failure modes. The exceptions are designed to support intelligent retry logic, user-friendly error reporting, and comprehensive debugging information.

Base Framework Exceptions
=========================

FrameworkError
--------------

.. autoclass:: framework.base.errors.FrameworkError
   :members:
   :show-inheritance:

   Base exception for all framework-related errors. Root exception class for all custom exceptions within the Alpha Berkeley Framework.

RegistryError
-------------

.. autoclass:: framework.base.errors.RegistryError
   :members:
   :show-inheritance:

   Exception for registry-related errors. Raised when issues occur with component registration, lookup, or management within the framework's registry system.

ConfigurationError
------------------

.. autoclass:: framework.base.errors.ConfigurationError
   :members:
   :show-inheritance:

   Exception for configuration-related errors. Raised when configuration files are invalid, missing required settings, or contain incompatible values.

Python Executor Service Exceptions
==================================

ErrorCategory
-------------

.. autoclass:: framework.services.python_executor.exceptions.ErrorCategory
   :members:
   :undoc-members:
   :show-inheritance:

   High-level error categories that determine appropriate recovery strategies.

   .. rubric:: Categories

   .. autosummary::
      :nosignatures:

      ~ErrorCategory.INFRASTRUCTURE
      ~ErrorCategory.CODE_RELATED  
      ~ErrorCategory.WORKFLOW
      ~ErrorCategory.CONFIGURATION

PythonExecutorException
-----------------------

.. autoclass:: framework.services.python_executor.exceptions.PythonExecutorException
   :members:
   :show-inheritance:
   :special-members: __init__

   Base exception class for all Python executor service operations.

   .. rubric:: Key Methods

   .. autosummary::
      :nosignatures:

      ~PythonExecutorException.is_infrastructure_error
      ~PythonExecutorException.is_code_error
      ~PythonExecutorException.is_workflow_error
      ~PythonExecutorException.should_retry_execution
      ~PythonExecutorException.should_retry_code_generation

Infrastructure Errors
---------------------

ContainerConnectivityError
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.ContainerConnectivityError
   :members:
   :show-inheritance:
   :special-members: __init__

   Exception raised when Jupyter container is unreachable or connection fails.

   .. rubric:: Methods

   .. autosummary::
      :nosignatures:

      ~ContainerConnectivityError.get_user_message

ContainerConfigurationError
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.ContainerConfigurationError
   :members:
   :show-inheritance:
   :special-members: __init__

   Container configuration is invalid.

Code-Related Errors
-------------------

CodeGenerationError
~~~~~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.CodeGenerationError
   :members:
   :show-inheritance:
   :special-members: __init__

   LLM failed to generate valid code.

CodeSyntaxError
~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.CodeSyntaxError
   :members:
   :show-inheritance:
   :special-members: __init__

   Generated code has syntax errors.

CodeRuntimeError
~~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.CodeRuntimeError
   :members:
   :show-inheritance:
   :special-members: __init__

   Code failed during execution due to runtime errors.

Workflow Errors
---------------

ExecutionTimeoutError
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.ExecutionTimeoutError
   :members:
   :show-inheritance:
   :special-members: __init__

   Code execution exceeded timeout.

MaxAttemptsExceededError
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.MaxAttemptsExceededError
   :members:
   :show-inheritance:
   :special-members: __init__

   Maximum execution attempts exceeded.

WorkflowError
~~~~~~~~~~~~~

.. autoclass:: framework.services.python_executor.exceptions.WorkflowError
   :members:
   :show-inheritance:
   :special-members: __init__

   Unexpected workflow error (bugs in framework code, not user code).

   .. rubric:: Methods

   .. autosummary::
      :nosignatures:

      ~WorkflowError.get_user_message

Memory Operations Exceptions
============================

MemoryCapabilityError
---------------------

.. autoclass:: framework.capabilities.memory.MemoryCapabilityError
   :members:
   :show-inheritance:

   Base exception class for memory capability-specific errors.

UserIdNotAvailableError
-----------------------

.. autoclass:: framework.capabilities.memory.UserIdNotAvailableError
   :members:
   :show-inheritance:

   User identification not available for memory operations.

ContentExtractionError
----------------------

.. autoclass:: framework.capabilities.memory.ContentExtractionError
   :members:
   :show-inheritance:

   Content extraction from conversation failed.

MemoryFileError
---------------

.. autoclass:: framework.capabilities.memory.MemoryFileError
   :members:
   :show-inheritance:

   Memory file system operations failed.

MemoryRetrievalError
--------------------

.. autoclass:: framework.capabilities.memory.MemoryRetrievalError
   :members:
   :show-inheritance:

   Memory retrieval operations failed.

LLMCallError
------------

.. autoclass:: framework.capabilities.memory.LLMCallError
   :members:
   :show-inheritance:

   LLM operations for memory processing failed.

Time Parsing Exceptions
=======================

TimeParsingError
----------------

.. autoclass:: framework.capabilities.time_range_parsing.TimeParsingError
   :members:
   :show-inheritance:

   Base exception class for time parsing-related errors.

InvalidTimeFormatError
----------------------

.. autoclass:: framework.capabilities.time_range_parsing.InvalidTimeFormatError
   :members:
   :show-inheritance:

   Invalid time format in user input.

AmbiguousTimeReferenceError
---------------------------

.. autoclass:: framework.capabilities.time_range_parsing.AmbiguousTimeReferenceError
   :members:
   :show-inheritance:

   Ambiguous time reference requiring clarification.

TimeParsingDependencyError
--------------------------

.. autoclass:: framework.capabilities.time_range_parsing.TimeParsingDependencyError
   :members:
   :show-inheritance:

   Missing required dependencies for time parsing.

Exception Usage Patterns
========================

Category-Based Error Handling
-----------------------------

.. code-block:: python

   try:
       result = await executor.execute_code(code)
   except PythonExecutorException as e:
       if e.should_retry_execution():
           # Infrastructure error - retry same code
           await retry_execution(code)
       elif e.should_retry_code_generation():
           # Code error - regenerate and retry
           new_code = await regenerate_code(error_feedback=str(e))
           await execute_code(new_code)
       else:
           # Workflow error - requires intervention
           await notify_user(f"Execution failed: {e.message}")

User-Friendly Error Messages
----------------------------

.. code-block:: python

   try:
       result = await container_executor.execute_code(code)
   except ContainerConnectivityError as e:
       # Get user-friendly message abstracting technical details
       user_message = e.get_user_message()
       logger.warning(f"Container issue: {user_message}")
       # Technical details still available for debugging
       logger.debug(f"Technical details: {e.technical_details}")

Domain-Specific Error Handling
------------------------------

.. code-block:: python

   try:
       memory_result = await memory_capability.execute(state)
   except UserIdNotAvailableError:
       # Handle missing user identification
       await request_user_identification()
   except ContentExtractionError as e:
       # Handle content extraction failure
       logger.warning(f"Content extraction failed: {e}")
       # Try alternative extraction method
       await fallback_content_extraction()
   except MemoryCapabilityError as e:
       # Handle general memory errors
       logger.error(f"Memory operation failed: {e}")

.. seealso::

   :doc:`01_classification_system`
       Error classification and severity management
   
   :doc:`03_recovery_coordination`
       Recovery patterns and coordination strategies