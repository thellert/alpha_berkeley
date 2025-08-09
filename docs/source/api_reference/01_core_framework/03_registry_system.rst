===============
Registry System
===============

Centralized component registry with configuration-driven application loading, convention-based module discovery, and explicit component registration.

.. currentmodule:: framework.registry

Core Registry Classes
=====================

RegistryManager
---------------

.. autoclass:: RegistryManager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   
   .. rubric:: Component Access Methods
   
   **Capabilities:**
   
   .. automethod:: RegistryManager.get_capability
   
   .. automethod:: RegistryManager.get_all_capabilities
   
   **Context Classes:**
   
   .. automethod:: RegistryManager.get_context_class
   
   .. automethod:: RegistryManager.get_all_context_classes
   
   **Infrastructure Nodes:**
   
   .. automethod:: RegistryManager.get_node
   
   .. automethod:: RegistryManager.get_all_nodes
   
   **Data Sources:**
   
   .. automethod:: RegistryManager.get_data_source
   
   .. automethod:: RegistryManager.get_all_data_sources
   
   **Services:**
   
   .. automethod:: RegistryManager.get_service
   
   .. automethod:: RegistryManager.get_all_services
   
   .. rubric:: Registry Management
   
   .. automethod:: RegistryManager.initialize
   
   .. automethod:: RegistryManager.validate_configuration
   
   .. automethod:: RegistryManager.export_registry_to_json
   
   .. rubric:: Registry Statistics and Debugging
   
   .. automethod:: RegistryManager.get_stats

Global Registry Functions
=========================

.. autofunction:: get_registry

.. autofunction:: initialize_registry

Registration Configuration
===========================

Configuration Interface
------------------------

.. autoclass:: RegistryConfigProvider
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Abstract Methods
   
   .. automethod:: RegistryConfigProvider.get_registry_config

RegistryConfig
--------------

.. autoclass:: RegistryConfig
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Component Lists
   
   .. attribute:: capabilities
      :type: List[CapabilityRegistration]
      
      Registration entries for domain capabilities (required).
   
   .. attribute:: context_classes
      :type: List[ContextClassRegistration]
      
      Registration entries for context data classes (required).
   
   .. attribute:: core_nodes
      :type: List[NodeRegistration]
      
      Registration entries for infrastructure nodes (optional).
   
   .. attribute:: data_sources
      :type: List[DataSourceRegistration]
      
      Registration entries for external data sources (optional).
   
   .. attribute:: services
      :type: List[ServiceRegistration]
      
      Registration entries for internal service graphs (optional).

Registration Classes
====================

Component Registration
----------------------

.. autoclass:: CapabilityRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Key Fields
   
   .. attribute:: name
      :type: str
      
      Unique capability name for registration.
   
   .. attribute:: module_path
      :type: str
      
      Python module path for lazy import.
   
   .. attribute:: class_name
      :type: str
      
      Class name within the module.
   
   .. attribute:: provides
      :type: List[str]
      
      Context types this capability produces.
   
   .. attribute:: requires
      :type: List[str]
      
      Context types this capability needs as input.

.. autoclass:: ContextClassRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Key Fields
   
   .. attribute:: context_type
      :type: str
      
      String identifier for the context type (e.g., 'PV_ADDRESSES').
   
   .. attribute:: module_path
      :type: str
      
      Python module path for lazy import.
   
   .. attribute:: class_name
      :type: str
      
      Class name within the module.

.. autoclass:: NodeRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Key Fields
   
   .. attribute:: name
      :type: str
      
      Unique identifier for the node in the registry.
   
   .. attribute:: module_path
      :type: str
      
      Python module path for lazy import.
   
   .. attribute:: function_name
      :type: str
      
      Function name within the module (decorated with @infrastructure_node).

.. autoclass:: DataSourceRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Key Fields
   
   .. attribute:: name
      :type: str
      
      Unique identifier for the data source in the registry.
   
   .. attribute:: health_check_required
      :type: bool
      
      Whether provider requires health checking.

.. autoclass:: ServiceRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Key Fields
   
   .. attribute:: internal_nodes
      :type: List[str]
      
      List of node names internal to this service.

Specialized Registration
------------------------

.. autoclass:: FrameworkPromptProviderRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. rubric:: Key Fields
   
   .. attribute:: application_name
      :type: str
      
      Application identifier (e.g., 'als_expert').
   
   .. attribute:: prompt_builders
      :type: Dict[str, str]
      
      Mapping of prompt types to override with custom builder classes.

.. autoclass:: ExecutionPolicyAnalyzerRegistration
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: DomainAnalyzerRegistration
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Registry Architecture
=====================

The registry system uses a two-tier architecture with configuration-driven application loading:

**Framework Registry:** Core infrastructure loaded from ``framework.registry.registry``

**Application Registries:** Domain-specific components from ``applications.{app}.registry`` (applications must be listed in global configuration)

**Initialization Order:**

Components are initialized in strict dependency order:

1. Context classes (required by capabilities)
2. Data sources (required by capabilities)
3. Core nodes (infrastructure components)
4. Services (internal LangGraph service graphs)
5. Capabilities (domain-specific functionality)
6. Framework prompt providers (application-specific prompts)

**Lazy Loading:**

All components use lazy loading to prevent circular import issues. Components are imported and instantiated only during the initialization phase, not at module load time.

Registry Export System
======================

The registry provides comprehensive export functionality for external tool integration and debugging:

**Automatic Export:**
Registry metadata is automatically exported during :func:`initialize_registry` when ``auto_export=True`` (default).

**Manual Export:**
Use :meth:`RegistryManager.export_registry_to_json` for on-demand export of registry state.

**Export Configuration:**
Default export directory is configured via ``file_paths.registry_exports_dir`` in ``config.yml`` (defaults to ``_agent_data/registry_exports/``).

**Export Structure:**
Exports create standardized JSON files containing capability definitions, context types, and metadata suitable for consumption by external tools, execution plan editors, and debugging utilities.

**Integration Pattern:**
The export system enables air-gapped integration where external tools need component metadata but cannot execute live Python code.

.. seealso::

   :doc:`01_base_components`
       Base component classes and decorators for registered components
   
   :doc:`02_state_and_context`
       State and context management for component data
   
   :doc:`04_configuration_system`
       Configuration system used by registry initialization
   
   :doc:`../../developer-guides/03_core-framework-systems/03_registry-and-discovery`
       Complete guide to registry system and component discovery