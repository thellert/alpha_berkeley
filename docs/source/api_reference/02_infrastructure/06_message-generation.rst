Message Generation
==================

Message generation capabilities for responding to user queries and requesting clarification when needed.

Respond Capability
------------------

.. currentmodule:: framework.infrastructure.respond_node

.. autoclass:: RespondCapability
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: ResponseContext
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Clarify Capability
------------------

.. currentmodule:: framework.infrastructure.clarify_node

.. autoclass:: ClarifyCapability
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __init__

Core Models
-----------

Message generation uses models defined in the core framework:

.. seealso::
   
   :class:`~framework.base.BaseCapability`
       Base class for all capabilities
   
   :class:`~framework.context.ContextManager`
       Context management for response generation

Registration
------------

**Respond Capability** is automatically registered as::

    CapabilityRegistration(
        name="respond",
        module_path="framework.infrastructure.respond_node",
        class_name="RespondCapability",
        provides=["FINAL_RESPONSE"]
    )

**Clarify Capability** is automatically registered as::

    CapabilityRegistration(
        name="clarify", 
        module_path="framework.infrastructure.clarify_node",
        class_name="ClarifyCapability",
        provides=[]
    )

.. seealso::
   
   :doc:`../01_core_framework/05_prompt_management`
       Prompt customization system
   
   :doc:`../01_core_framework/03_registry_system`
       Component registration system
   
   :doc:`../../developer-guides/04_infrastructure-components/05_message-generation`
       Implementation details and usage patterns