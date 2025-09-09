================
Python Execution
================

Python code generation and execution service with LangGraph-based workflow, approval integration, and flexible deployment options.

.. note::
   For implementation tutorials and usage examples, see :doc:`../../../developer-guides/05_production-systems/03_python-execution-service`.

.. currentmodule:: framework.services.python_executor

Core Components
===============

.. autosummary::
   :toctree: _autosummary
   
   PythonExecutorService
   PythonExecutionRequest
   PythonServiceResult
   PythonExecutionSuccess
   PythonExecutionState
   PythonExecutionContext
   ExecutionModeConfig
   ExecutionControlConfig
   ContainerEndpointConfig
   NotebookAttempt
   NotebookType

Exception Hierarchy
===================

.. autosummary::
   :toctree: _autosummary
   
   PythonExecutorException
   CodeRuntimeError
   CodeGenerationError
   ContainerConnectivityError
   ExecutionTimeoutError
   ErrorCategory

Service Interface
=================

.. autoclass:: PythonExecutorService
   :members:
   :show-inheritance:
   :no-index:

Request and Response Models
===========================

.. autoclass:: PythonExecutionRequest
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: PythonServiceResult
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: PythonExecutionSuccess
   :members:
   :show-inheritance:
   :no-index:

State Management
================

.. autoclass:: PythonExecutionState
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: PythonExecutionContext
   :members:
   :show-inheritance:
   :no-index:

Configuration Models
====================

.. autoclass:: ExecutionModeConfig
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: ExecutionControlConfig
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: ContainerEndpointConfig
   :members:
   :show-inheritance:
   :no-index:

Notebook Management
===================

.. autoclass:: NotebookAttempt
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: NotebookType
   :members:
   :show-inheritance:
   :no-index:

Exceptions
==========

.. autoclass:: PythonExecutorException
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: CodeRuntimeError
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: CodeGenerationError
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: ContainerConnectivityError
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: ExecutionTimeoutError
   :members:
   :show-inheritance:
   :no-index:

.. autoclass:: ErrorCategory
   :members:
   :show-inheritance:
   :no-index:

Utility Functions
=================

.. currentmodule:: framework.services.python_executor.models

.. autofunction:: get_execution_control_config_from_configurable

.. autofunction:: get_execution_mode_config_from_configurable

.. autofunction:: get_container_endpoint_config_from_configurable

Serialization Utilities
=======================

.. currentmodule:: framework.services.python_executor.services

.. autofunction:: make_json_serializable

.. autofunction:: serialize_results_to_file

.. seealso::

   :doc:`../../../developer-guides/05_production-systems/03_python-execution-service`
       Complete implementation guide and examples
   
   :class:`framework.capabilities.python.PythonCapability`
       Capability interface that uses this service