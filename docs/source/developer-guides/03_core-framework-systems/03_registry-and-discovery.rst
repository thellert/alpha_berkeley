========================
Registry and Discovery
========================

.. currentmodule:: framework.registry

The Alpha Berkeley Framework implements a centralized component registration and discovery system that enables clean separation between framework infrastructure and application-specific functionality.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Understanding :class:`RegistryManager` and component access patterns
   - Implementing application registries with :class:`RegistryConfigProvider`
   - Using ``@capability_node`` decorator for LangGraph integration
   - Registry configuration patterns and best practices
   - Component loading order and dependency management

   **Prerequisites:** Understanding of :doc:`01_state-management-architecture` (AgentState) and Python decorators
   
   **Time Investment:** 20-30 minutes for complete understanding

System Overview
===============

The registry system uses a two-tier architecture:

**Framework Registry**
  Core infrastructure components (nodes, base capabilities, services)

**Application Registries**
  Domain-specific components (capabilities, context classes, data sources)

Applications register components by implementing ``RegistryConfigProvider`` in their ``registry.py`` module. The framework automatically discovers and loads these using the convention ``applications.{app_name}.registry``.

RegistryManager
===============

The ``RegistryManager`` provides centralized access to all framework components:

.. code-block:: python

   from framework.registry import initialize_registry, get_registry
   
   # Initialize the registry system
   initialize_registry()
   
   # Access the singleton registry instance
   registry = get_registry()
   
   # Access components
   capability = registry.get_capability("pv_address_finding")
   context_class = registry.get_context_class("PV_ADDRESSES")
   data_source = registry.get_data_source("experiment_database")

**Key Methods:**

- ``get_capability(name)`` - Get capability instance by name
- ``get_context_class(context_type)`` - Get context class by type identifier
- ``get_data_source(name)`` - Get data source provider instance
- ``get_node(name)`` - Get LangGraph node function

Application Registry Implementation
===================================

Applications implement ``RegistryConfigProvider`` to define their components:

.. code-block:: python

   # applications/my_app/registry.py
   from framework.registry import (
       RegistryConfigProvider, RegistryConfig,
       CapabilityRegistration, ContextClassRegistration
   )
   
   class MyAppRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self) -> RegistryConfig:
           return RegistryConfig(
               capabilities=[
                   CapabilityRegistration(
                       name="my_capability",
                       module_path="applications.my_app.capabilities.my_capability",
                       class_name="MyCapability",
                       description="My application capability",
                       provides=["MY_CONTEXT"],
                       requires=[]
                   )
               ],
               context_classes=[
                   ContextClassRegistration(
                       context_type="MY_CONTEXT",
                       module_path="applications.my_app.context_classes",
                       class_name="MyContext"
                   )
               ]
           )

Component Registration
======================

**Capability Registration:**

.. code-block:: python

   # Registration in registry.py
   CapabilityRegistration(
       name="pv_address_finding",
       module_path="applications.als_expert.capabilities.pv_address_finding",
       class_name="PVAddressFindingCapability",
       description="Find Process Variable addresses",
       provides=["PV_ADDRESSES"],
       requires=[]
   )

   # Implementation in capability file
   @capability_node
   class PVAddressFindingCapability(BaseCapability):
       name = "pv_address_finding"
       description = "Find Process Variable addresses"
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           # Implementation here
           return {"success": True}

**Context Class Registration:**

.. code-block:: python

   # Registration
   ContextClassRegistration(
       context_type="PV_ADDRESSES",
       module_path="applications.als_expert.context_classes",
       class_name="PVAddresses"
   )

   # Implementation
   class PVAddresses(CapabilityContext):
       CONTEXT_TYPE = "PV_ADDRESSES"
       
       pvs: List[str]
       search_query: str
       timestamp: datetime

**Data Source Registration:**

.. code-block:: python

   DataSourceRegistration(
       name="experiment_database",
       module_path="applications.als_expert.database.experiment_database",
       class_name="ExperimentDatabaseProvider",
       description="Experiment database access",
       health_check_required=True
   )

Registry Initialization and Usage
=================================

.. code-block:: python

   from framework.registry import initialize_registry, get_registry
   
   # Initialize registry (loads framework + application components)
   initialize_registry()
   
   # Access registry throughout application
   registry = get_registry()
   
   # Get capabilities
   capability = registry.get_capability("pv_address_finding")
   all_capabilities = registry.get_all_capabilities()
   
   # Get context classes
   pv_context_class = registry.get_context_class("PV_ADDRESSES")
   
   # Get data sources
   db_provider = registry.get_data_source("experiment_database")

Component Loading Order
=======================

Components are loaded lazily during registry initialization:

1. **Context classes** - Required by capabilities
2. **Data sources** - Required by capabilities  
3. **Core nodes** - Infrastructure components
4. **Services** - Internal LangGraph service graphs
5. **Capabilities** - Domain-specific functionality

Best Practices
==============

**Registry Configuration:**
- Keep registrations simple and focused
- Use clear, descriptive names and descriptions
- Define ``provides`` and ``requires`` accurately for dependency tracking

**Capability Implementation:**
- Always use ``@capability_node`` decorator
- Implement required attributes: ``name``, ``description``
- Make ``execute()`` method static and async
- Return dictionary of state updates

**Application Structure:**
- Place registry in ``applications/{app_name}/registry.py``
- Implement exactly one ``RegistryConfigProvider`` class
- Organize capabilities in ``capabilities/`` directory

Common Issues
=============

**Component Not Found:**
1. Verify component is registered in ``RegistryConfigProvider``
2. Check module path and class name are correct
3. Ensure ``initialize_registry()`` was called

**Missing @capability_node:**
1. Ensure ``@capability_node`` decorator is applied
2. Verify ``name`` and ``description`` class attributes exist
3. Check that ``execute()`` method is implemented as static method

.. seealso::
   :doc:`05_message-and-execution-flow`
       Complete message processing pipeline using registered components
   :doc:`01_state-management-architecture`
       State management integration with registry system