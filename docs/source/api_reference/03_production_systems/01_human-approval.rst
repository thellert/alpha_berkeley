==============
Human Approval
==============

LangGraph-native approval system for production-ready human-in-the-loop workflows with configurable security policies.

.. note::
   For implementation guides and examples, see :doc:`../../../developer-guides/05_production-systems/01_human-approval-workflows`.

.. currentmodule:: framework.approval

Core Components
===============

.. autosummary::
   :toctree: _autosummary
   
   ApprovalManager
   GlobalApprovalConfig
   PythonExecutionApprovalConfig
   MemoryApprovalConfig
   ApprovalMode
   PythonExecutionApprovalEvaluator
   MemoryApprovalEvaluator
   ApprovalDecision

System Functions
================

.. autosummary::
   :toctree: _autosummary
   
   create_approval_type
   create_code_approval_interrupt
   create_plan_approval_interrupt
   create_memory_approval_interrupt
   get_approval_resume_data
   get_approval_manager

Configuration Management
========================

.. autoclass:: ApprovalManager
   :members:
   :show-inheritance:

.. autoclass:: GlobalApprovalConfig
   :members:
   :show-inheritance:

Configuration Models
====================

.. autoclass:: PythonExecutionApprovalConfig
   :members:
   :show-inheritance:

.. autoclass:: MemoryApprovalConfig
   :members:
   :show-inheritance:

.. autoclass:: ApprovalMode
   :members:
   :show-inheritance:

Business Logic Evaluators
==========================

.. autoclass:: PythonExecutionApprovalEvaluator
   :members:
   :show-inheritance:

.. autoclass:: MemoryApprovalEvaluator
   :members:
   :show-inheritance:

.. autoclass:: ApprovalDecision
   :members:
   :show-inheritance:

Approval System Functions
=========================

.. autofunction:: create_approval_type

.. autofunction:: create_code_approval_interrupt

.. autofunction:: create_plan_approval_interrupt

.. autofunction:: create_memory_approval_interrupt

.. autofunction:: get_approval_resume_data

Utility Functions
=================

.. autofunction:: get_approval_manager

.. seealso::

   :doc:`../../../developer-guides/05_production-systems/01_human-approval-workflows`
       Complete implementation guide and examples
   
   :class:`framework.services.python_executor.PythonExecutorService`
       Service that integrates with approval system