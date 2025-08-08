Classification
==============

.. currentmodule:: framework.infrastructure.classification_node

Infrastructure node that handles task classification and capability selection by analyzing user tasks against available capabilities.

ClassificationNode
------------------

.. autoclass:: ClassificationNode
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __init__

Supporting Functions
--------------------

.. autofunction:: select_capabilities

Core Models
-----------

Classification uses models defined in the core framework:

.. seealso::
   
   :class:`~framework.base.CapabilityMatch`
       Classification results for capability selection
   
   :class:`~framework.base.TaskClassifierGuide`
       Classification guidance structure
   
   :class:`~framework.base.ClassifierExample`
       Few-shot examples for classification
   
   :class:`~framework.base.BaseInfrastructureNode`
       Base class for infrastructure components

Registration
------------

Automatically registered as::

    NodeRegistration(
        name="classifier",
        module_path="framework.infrastructure.classification_node",
        function_name="ClassificationNode",
        description="Task classification and capability selection"
    )

.. seealso::
   
   :doc:`../01_core_framework/05_prompt_management`
       Prompt customization system
   
   :doc:`../01_core_framework/03_registry_system`
       Component and capability management
   
   :doc:`../../developer-guides/04_infrastructure-components/03_classification-and-routing`
       Implementation details and usage patterns