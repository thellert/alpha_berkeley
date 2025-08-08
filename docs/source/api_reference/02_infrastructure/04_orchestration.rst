Orchestration
=============

.. currentmodule:: framework.infrastructure.orchestration_node

Infrastructure node that creates execution plans from active capabilities and task requirements with native LangGraph interrupt support for human-in-the-loop approval.

OrchestrationNode
-----------------

.. autoclass:: OrchestrationNode
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __init__

Core Models
-----------

Orchestration uses models defined in the core framework:

.. seealso::
   
   :class:`~framework.base.ExecutionPlan`
       Structured execution plan model
   
   :class:`~framework.base.PlannedStep`
       Individual step within execution plans
   
   :class:`~framework.base.BaseInfrastructureNode`
       Base class for infrastructure components

Approval System Integration
---------------------------

.. currentmodule:: framework.approval.approval_system

.. autofunction:: create_plan_approval_interrupt

.. autofunction:: clear_approval_state

.. autofunction:: create_approval_type

Registration
------------

Automatically registered as::

    NodeRegistration(
        name="orchestrator",
        module_path="framework.infrastructure.orchestration_node",
        function_name="OrchestrationNode",
        description="Execution planning and orchestration"
    )

.. seealso::
   
   :doc:`../01_core_framework/05_prompt_management`
       Prompt customization system
   
   :doc:`../03_production_systems/01_human-approval`
       Complete approval system architecture
   
   :doc:`../../developer-guides/04_infrastructure-components/04_orchestrator-planning`
       Implementation details and usage patterns