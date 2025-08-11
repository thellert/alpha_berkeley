"""Registry Manager for ALS Expert Agent Components.

This module provides the centralized registry management system for the ALS Expert
Agent framework, serving as the single point of access for all framework components
including capabilities, nodes, context classes, data sources, and services.

The registry manager implements a sophisticated component management system that:

Core Functionality:
    - **Centralized Access**: Single point of access for all framework components
    - **Lazy Loading**: Components are imported only when needed, preventing circular imports
    - **Dependency Management**: Automatic initialization in proper dependency order
    - **Convention-Based Loading**: Application registry loading using naming conventions
    - **Override Support**: Applications can override framework components
    - **Type Safety**: Strongly typed component registration and access

Architecture Overview:
    The registry system uses a two-tier architecture with configuration-driven loading:
    
    1. **Framework Registry**: Core infrastructure loaded from framework.registry.registry
    2. **Application Registries**: Domain-specific components from applications.{app}.registry
    
    Applications must be listed in configuration, then the system loads their registries 
    using naming conventions and merges them with the framework registry, allowing 
    applications to extend or override framework functionality.

Component Lifecycle:
    1. **Loading**: Registry configurations loaded via RegistryConfigProvider interface
    2. **Merging**: Application configs merged with framework config (applications override)
    3. **Initialization**: Components loaded in dependency order (context → data → nodes → capabilities)
    4. **Access**: Components available through typed getter methods
    5. **Export**: Registry metadata exported for external tools

Initialization Order:
    Components are initialized in strict dependency order:
    
    1. Context classes (required by capabilities)
    2. Data sources (required by capabilities)
    3. Core nodes (infrastructure components)
    4. Services (internal LangGraph service graphs)
    5. Capabilities (domain-specific functionality)
    6. Framework prompt providers (application-specific prompts)

The registry manager is typically accessed through global functions rather than
direct instantiation, providing a singleton pattern that ensures consistent
state across the entire framework.

.. note::
   The registry uses lazy loading throughout - components are imported and instantiated
   only during the initialization phase, not at module load time. This prevents
   circular import issues while maintaining full introspection capabilities.

.. warning::
   Registry initialization must complete successfully before any components can be
   accessed. Failed initialization will raise RegistryError and prevent framework
   operation. Always call initialize_registry() before accessing components.

Examples:
    Basic registry usage::
    
        >>> from framework.registry import initialize_registry, get_registry
        >>> 
        >>> # Initialize the complete registry system
        >>> initialize_registry()
        >>> 
        >>> # Access the singleton registry instance
        >>> registry = get_registry()
        >>> 
        >>> # Access framework components
        >>> capability = registry.get_capability("pv_address_finding")
        >>> context_class = registry.get_context_class("PV_ADDRESSES")
        >>> data_source = registry.get_data_source("core_user_memory")
        
    Registry statistics and debugging::
    
        >>> # Check registry status
        >>> stats = registry.get_stats()
        >>> print(f"Loaded {stats['capabilities']} capabilities")
        >>> print(f"Available: {stats['capability_names']}")
        >>> 
        >>> # Validate configuration
        >>> errors = registry.validate_configuration()
        >>> if errors:
        ...     print(f"Configuration issues: {errors}")
        
    Export registry data for external tools::
    
        >>> # Export complete registry metadata
        >>> data = registry.export_registry_to_json("/tmp/registry_export")
        >>> print(f"Exported {data['metadata']['total_capabilities']} capabilities")

.. seealso::
   :func:`get_registry` : Singleton access to the global registry instance
   :func:`initialize_registry` : Registry system initialization
   :class:`RegistryConfigProvider` : Interface for application registry implementations
   :doc:`/developer-guides/registry-system` : Complete registry system documentation
   :doc:`/developer-guides/03_core-framework-systems/03_registry-and-discovery` : Component registration patterns
"""

import logging
import importlib
import inspect
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, TYPE_CHECKING

from .base import RegistryConfig, RegistryConfigProvider
from framework.base.errors import RegistryError, ConfigurationError
from configs.logger import get_logger
from configs.config import get_config_value, get_agent_dir

# Import for prompt loading
try:
    from framework.prompts.loader import _prompt_loader, set_default_framework_prompt_provider
    from framework.prompts.defaults import DefaultPromptProvider
except ImportError:
    _prompt_loader = None
    set_default_framework_prompt_provider = None
    DefaultPromptProvider = None

if TYPE_CHECKING:
    from framework.base import BaseCapability, BaseCapabilityNode
    from framework.context import CapabilityContext

logger = get_logger(name='REGISTRY', color='sky_blue2')

class RegistryManager:
    """Centralized registry for all ALS Expert Agent components.
    
    This class provides the single point of access for capabilities, nodes, context classes,
    and data sources throughout the framework. It replaces the fragmented registry system
    with a unified approach that eliminates circular imports through lazy loading and
    provides dependency-ordered initialization.
    
    The registry system follows a strict initialization order to handle dependencies:
    1. Context classes (required by capabilities)
    2. Data sources (required by capabilities) 
    3. Core nodes (infrastructure components)
    4. Capabilities (domain-specific functionality)
    5. Framework prompt providers (application-specific prompts)
    6. Workflow templates (predefined execution patterns)
    
    All components are loaded lazily using module path and class name metadata,
    preventing circular import issues while maintaining full introspection capabilities.
    
    .. note::
       The registry is typically accessed through the global functions get_registry()
       and initialize_registry() rather than instantiated directly.
    
    .. warning::
       Registry initialization must complete successfully before any components
       can be accessed. Failed initialization will raise RegistryError.
    """
    
    def __init__(self, application_names: Optional[List[str]] = None):
        """Initialize registry manager with convention-based application loading.
        
        Creates a new registry manager instance that will load the specified
        application registries using naming conventions. The manager
        builds a merged configuration by combining the framework registry with
        all specified application registries.
        
        The initialization process follows these steps:
        1. Load framework registry from framework.registry.registry
        2. Load application registries from applications.{app_name}.registry
        3. Merge configurations with application overrides taking precedence
        4. Prepare component registries for lazy loading
        
        Applications are loaded using the convention-based pattern where each
        application name corresponds to a registry module at:
        applications.{app_name}.registry
        
        Each application registry module must contain exactly one class implementing
        the RegistryConfigProvider interface.
        
        :param application_names: List of application names to load using conventions.
            If None or empty, only the framework registry will be loaded. Application
            names should match directory names under src/applications/
        :type application_names: list[str], optional
        :raises RegistryError: If any application registry cannot be loaded
        :raises ConfigurationError: If registry configuration is invalid
        
        .. note::
           The registry manager is not initialized after construction. Call initialize()
           to perform component loading and make components available for access.
           
        .. warning:
           Invalid application names or missing registry modules will cause
           initialization to fail. Ensure all specified applications have valid
           registry modules.
        
        Examples:
            Create registry with specific applications::
            
                >>> manager = RegistryManager(["als_expert", "wind_turbine"])
                >>> manager.initialize()  # Load components
                >>> capability = manager.get_capability("pv_address_finding")
            
            Create framework-only registry::
            
                >>> manager = RegistryManager([])  # No applications
                >>> manager.initialize()
                >>> memory_cap = manager.get_capability("memory")  # Framework capability
                
            Typical usage through global functions::
            
                >>> # Preferred approach - use global functions
                >>> from framework.registry import initialize_registry, get_registry
                >>> initialize_registry()  # Uses config to determine applications
                >>> registry = get_registry()
        
        .. seealso::
           :func:`initialize_registry` : Preferred way to create and initialize registry
           :func:`get_registry` : Access the global singleton registry instance
           :meth:`initialize` : Initialize components after construction
           :class:`RegistryConfigProvider` : Interface that applications must implement
        """
        self.application_names = application_names or []
        self._initialized = False
        
        # Core registries (no circular imports - pure lookup tables)
        self._registries = {
            'capabilities': {},
            'nodes': {},
            'contexts': {},
            'data_sources': {},
            'services': {},
            'domain_analyzers': {},
            'execution_policy_analyzers': {},
            'framework_prompt_providers': {},
        }
        
        # Build complete configuration by merging framework + applications
        self.config = self._build_merged_configuration()
    
    def _build_merged_configuration(self) -> RegistryConfig:
        """Build merged configuration with application overrides using conventions.
        
        Uses conventions to locate application registries:
        - Registry module: applications.{app_name}.registry
        
        Applications override framework components with the same name/type.
        
        :return: Merged registry configuration with application overrides applied
        :rtype: RegistryConfig
        """
        # Start with framework configuration (using interface pattern)
        framework_config = self._load_registry_from_module("framework.registry.registry")
        merged = RegistryConfig(
            core_nodes=framework_config.core_nodes.copy(),
            capabilities=framework_config.capabilities.copy(),
            context_classes=framework_config.context_classes.copy(),
            data_sources=framework_config.data_sources.copy(),
            services=framework_config.services.copy(),
            framework_prompt_providers=framework_config.framework_prompt_providers.copy(),
            initialization_order=framework_config.initialization_order.copy()
        )
        
        # Load and merge each application configuration
        for app_name in self.application_names:
            try:
                app_registry_config = self._load_registry_from_module(f"applications.{app_name}.registry")
                if app_registry_config:
                    self._merge_application_with_override(merged, app_registry_config, app_name)
                    logger.info(f"Loaded application registry: {app_name}")
            except Exception as e:
                logger.error(f"Failed to load application {app_name}: {e}")
                raise RegistryError(f"Failed to load application {app_name}: {e}") from e
        
        logger.info(f"Built merged registry with {len(self.application_names)} applications")
        return merged
    
    def _load_registry_from_module(self, module_path: str) -> RegistryConfig:
        """Generic registry loader using interface pattern.
        
        Convention: Module must contain exactly one class implementing 
        RegistryConfigProvider interface. Used by both framework and applications.
        
        :param module_path: Python module path (e.g., 'framework.registry.registry')
        :type module_path: str
        :return: Registry configuration
        :rtype: RegistryConfig
        :raises RegistryError: If registry cannot be loaded or interface not implemented
        """
        # Auto-derive component name for error messages and logging
        if module_path.startswith("applications."):
            component_name = f"{module_path.split('.')[1]} application"
        elif module_path == "framework.registry.registry":
            component_name = "framework"
        else:
            component_name = f"module {module_path}"
        
        try:
            # Import the registry module
            registry_module = importlib.import_module(module_path)
            
            # Find classes implementing RegistryConfigProvider interface
            provider_classes = []
            for name in dir(registry_module):
                obj = getattr(registry_module, name)
                if (inspect.isclass(obj) and 
                    issubclass(obj, RegistryConfigProvider) and 
                    obj != RegistryConfigProvider):
                    provider_classes.append(obj)
            
            # STRICT ENFORCEMENT: Exactly one provider class required
            if len(provider_classes) == 0:
                raise RegistryError(
                    f"No RegistryConfigProvider implementation found in {module_path}. "
                    f"{component_name} must define exactly one class implementing RegistryConfigProvider. "
                    f"Import: from framework.registry import RegistryConfigProvider"
                )
            elif len(provider_classes) > 1:
                class_names = [cls.__name__ for cls in provider_classes]
                raise RegistryError(
                    f"Multiple RegistryConfigProvider implementations found in {module_path}: {class_names}. "
                    f"{component_name} must define exactly one provider class."
                )
            
            # Instantiate and get configuration
            provider_class = provider_classes[0]
            provider_instance = provider_class()
            config = provider_instance.get_registry_config()
            
            logger.debug(f"Loaded {component_name} registry via {provider_class.__name__} from {module_path}")
            return config
            
        except ImportError as e:
            raise RegistryError(
                f"Failed to import {component_name} registry module {module_path}: {e}"
            ) from e
        except Exception as e:
            raise RegistryError(
                f"Failed to load {component_name} registry from {module_path}: {e}"
            ) from e


    def _apply_framework_exclusions(self, merged: RegistryConfig, exclusions: Dict[str, List[str]], app_name: str) -> None:
        """Apply framework component exclusions to the merged registry configuration.
        
        Removes specified framework components from the merged configuration based on
        exclusion rules defined by the application. This allows applications to disable
        framework components they don't need or want to replace with custom implementations.
        
        :param merged: Merged registry configuration to modify
        :type merged: RegistryConfig
        :param exclusions: Component exclusions by type (e.g., {'capabilities': ['python']})
        :type exclusions: Dict[str, List[str]]
        :param app_name: Application name for logging purposes
        :type app_name: str
        """
        for component_type, excluded_names in exclusions.items():
            if not excluded_names:
                continue
                
            # Get the component collection from merged config
            component_collection = getattr(merged, component_type, None)
            if component_collection is None:
                logger.warning(f"Application {app_name} tried to exclude unknown component type: {component_type}")
                continue
            
            # Filter out excluded components
            original_count = len(component_collection)
            filtered_components = [comp for comp in component_collection if comp.name not in excluded_names]
            setattr(merged, component_type, filtered_components)
            
            # Log exclusions that actually occurred
            excluded_count = original_count - len(filtered_components)
            if excluded_count > 0:
                actually_excluded = [name for name in excluded_names 
                                   if name in {comp.name for comp in component_collection}]
                if actually_excluded:
                    logger.info(f"Application {app_name} excluded framework {component_type}: {actually_excluded}")

    def _merge_application_with_override(self, merged: RegistryConfig, app_config: RegistryConfig, app_name: str) -> None:
        """Merge application configuration with framework, allowing overrides.
        
        Applications can override framework components by providing components
        with the same name. This supports customization and extension patterns.
        Enhanced with robust attribute checking for missing components.
        """
        # Merge context classes (applications typically define their own)
        context_overrides = []
        existing_context_types = {cls.context_type for cls in merged.context_classes}
        
        # Safely access context_classes attribute
        app_context_classes = getattr(app_config, 'context_classes', [])
        for app_context in app_context_classes:
            if app_context.context_type in existing_context_types:
                # Remove framework context class and add application override
                merged.context_classes = [cls for cls in merged.context_classes if cls.context_type != app_context.context_type]
                context_overrides.append(app_context.context_type)
            merged.context_classes.append(app_context)
        
        if context_overrides:
            logger.info(f"Application {app_name} overrode framework context classes: {context_overrides}")
        
        # Handle framework component exclusions first (before overrides)
        framework_exclusions = getattr(app_config, 'framework_exclusions', {})
        if framework_exclusions:
            self._apply_framework_exclusions(merged, framework_exclusions, app_name)
        
        # Merge capabilities (applications typically define their own)
        capability_overrides = []
        existing_capability_names = {cap.name for cap in merged.capabilities}
        
        # Safely access capabilities attribute
        app_capabilities = getattr(app_config, 'capabilities', [])
        for app_capability in app_capabilities:
            if app_capability.name in existing_capability_names:
                # Remove framework capability and add application override
                merged.capabilities = [cap for cap in merged.capabilities if cap.name != app_capability.name]
                capability_overrides.append(app_capability.name)
            merged.capabilities.append(app_capability)
        
        if capability_overrides:
            logger.info(f"Application {app_name} overrode framework capabilities: {capability_overrides}")
        
        # Merge data sources with override support
        framework_ds_names = {ds.name for ds in merged.data_sources}
        ds_overrides = []
        
        # Safely access data_sources attribute
        app_data_sources = getattr(app_config, 'data_sources', [])
        for app_ds in app_data_sources:
            if app_ds.name in framework_ds_names:
                # Remove framework data source and add application override
                merged.data_sources = [ds for ds in merged.data_sources if ds.name != app_ds.name]
                ds_overrides.append(app_ds.name)
            merged.data_sources.append(app_ds)
        
        if ds_overrides:
            logger.info(f"Application {app_name} overrode framework data sources: {ds_overrides}")
        
        # Merge core nodes with override support (applications can override framework nodes!)
        framework_node_names = {node.name for node in merged.core_nodes}
        node_overrides = []
        
        # Safely access core_nodes attribute
        app_core_nodes = getattr(app_config, 'core_nodes', [])
        for app_node in app_core_nodes:
            if app_node.name in framework_node_names:
                # Remove framework node and add application override
                merged.core_nodes = [node for node in merged.core_nodes if node.name != app_node.name]
                node_overrides.append(app_node.name)
            merged.core_nodes.append(app_node)
        
        if node_overrides:
            logger.info(f"Application {app_name} overrode framework nodes: {node_overrides}")
        
        # Merge services with override support
        framework_service_names = {service.name for service in merged.services}
        service_overrides = []
        
        # Safely access services attribute
        app_services = getattr(app_config, 'services', [])
        for app_service in app_services:
            if app_service.name in framework_service_names:
                # Remove framework service and add application override
                merged.services = [service for service in merged.services if service.name != app_service.name]
                service_overrides.append(app_service.name)
            merged.services.append(app_service)
        
        if service_overrides:
            logger.info(f"Application {app_name} overrode framework services: {service_overrides}")
        
        # Add framework prompt providers (no override needed)
        # Safely access framework_prompt_providers attribute
        app_prompt_providers = getattr(app_config, 'framework_prompt_providers', [])
        merged.framework_prompt_providers.extend(app_prompt_providers)

    def initialize(self) -> None:
        """Initialize all component registries in dependency order.
        
        Performs complete initialization of the registry system by loading all
        registered components in the proper dependency order. This method handles
        the transition from configuration metadata to actual component instances,
        importing modules and instantiating classes as needed.
        
        The initialization process follows strict dependency order to ensure
        components are available when needed by dependent components:
        
        1. **Context Classes**: Data structures used by capabilities
        2. **Data Sources**: External data providers used by capabilities
        3. **Core Nodes**: Infrastructure components (router, orchestrator, etc.)
        4. **Services**: Internal LangGraph service graphs
        5. **Capabilities**: Domain-specific functionality
        6. **Framework Prompt Providers**: Application-specific prompt customizations
        
        During initialization, the registry:
        - Dynamically imports all component modules using lazy loading
        - Instantiates classes and functions as specified in registrations
        - Validates that all components can be loaded successfully
        - Creates proper cross-references between related components
        - Sets up prompt provider overrides and customizations
        
        Component Loading Details:
            - **Context Classes**: Imported and registered by type identifier
            - **Data Sources**: Instantiated and optionally health-checked
            - **Nodes**: Decorator-created functions registered for LangGraph
            - **Capabilities**: Instantiated with decorator-created node functions
            - **Services**: Service graphs compiled and made available
            - **Analyzers**: Policy and domain analyzers prepared for use
        
        :raises RegistryError: If any component fails to load, import, or initialize.
            This includes missing modules, invalid class names, or instantiation failures
        :raises ConfigurationError: If configuration is invalid, has circular dependencies,
            or contains inconsistent component definitions
        :raises ImportError: If any component module cannot be imported
        :raises AttributeError: If any component class or function is not found in its module
        
        .. note::
           This method is idempotent - multiple calls have no effect if the registry
           is already initialized. The initialization state is tracked internally.
           
        .. warning::
           All component imports occur during this call. Import failures, missing
           dependencies, or circular imports will prevent framework operation.
           Ensure all component modules and dependencies are available.
        
        Examples:
            Basic initialization::
            
                >>> registry = RegistryManager(["als_expert"])
                >>> registry.initialize()  # Load all components
                >>> print(registry.get_stats())  # Check what was loaded
                
            Handle initialization errors::
            
                >>> try:
                ...     registry.initialize()
                ... except RegistryError as e:
                ...     print(f"Registry initialization failed: {e}")
                ...     # Check configuration or fix missing components
                
            Check initialization status::
            
                >>> if not registry._initialized:
                ...     registry.initialize()
                >>> capability = registry.get_capability("my_capability")
        
        .. seealso::
           :meth:`validate_configuration` : Validate configuration before initialization
           :meth:`get_stats` : Check initialization results and component counts
           :meth:`clear` : Reset registry to uninitialized state
           :func:`initialize_registry` : Global function that calls this method
        """
        if self._initialized:
            logger.debug("Registry already initialized")
            return
            
        logger.info("Initializing registry system...")
        
        try:
            for component_type in self.config.initialization_order:
                self._initialize_component_type(component_type)
            
            self._initialized = True
            logger.info(self._get_initialization_summary())
            
        except (ImportError, AttributeError, ConfigurationError) as e:
            logger.error(f"Registry initialization failed: {e}")
            raise RegistryError(f"Failed to initialize registry: {e}") from e
        except Exception as e:
            logger.error(f"Registry initialization failed with unexpected error: {e}")
            raise RegistryError(f"Unexpected error during registry initialization: {e}") from e
    
    def _initialize_component_type(self, component_type: str) -> None:
        """Initialize components of a specific type.
        
        :param component_type: Type of components to initialize (context_classes, data_sources, etc.)
        :type component_type: str
        :raises ValueError: If component_type is not recognized
        """
        if component_type == "context_classes":
            self._initialize_context_classes()
        elif component_type == "data_sources":
            self._initialize_data_sources()
        elif component_type == "core_nodes":
            self._initialize_core_nodes()
        elif component_type == "services":
            self._initialize_services()
        elif component_type == "capabilities":
            self._initialize_capabilities()
        elif component_type == "framework_prompt_providers":
            self._initialize_framework_prompt_providers()
        elif component_type == "domain_analyzers":
            self._initialize_domain_analyzers()
        elif component_type == "execution_policy_analyzers":
            self._initialize_execution_policy_analyzers()

        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    def _initialize_context_classes(self) -> None:
        """Initialize context class registry with lazy loading.
        
        Dynamically imports and registers all context classes defined in the configuration.
        Context classes define the data structures used for inter-capability communication
        and must be available before capability initialization.
        
        :raises RegistryError: If any context class module cannot be imported
        :raises AttributeError: If specified class name is not found in module
        """
        logger.debug("Initializing context classes...")
        for reg in self.config.context_classes:
            try:
                # Dynamically import and get the context class
                module = __import__(reg.module_path, fromlist=[reg.class_name])
                context_class = getattr(module, reg.class_name)
                self._registries['contexts'][reg.context_type] = context_class
                logger.debug(f"Registered context class: {reg.context_type} -> {context_class.__name__}")
            except ImportError as e:
                logger.error(f"Failed to import module for context class {reg.context_type}: {reg.module_path}")
                raise RegistryError(f"Cannot import module {reg.module_path} for context class {reg.context_type}: {e}") from e
            except AttributeError as e:
                logger.error(f"Context class {reg.class_name} not found in module {reg.module_path}")
                raise RegistryError(f"Class {reg.class_name} not found in module {reg.module_path} for context {reg.context_type}: {e}") from e
        
        logger.info(f"Registered {len(self.config.context_classes)} context classes")
    
    def _initialize_data_sources(self) -> None:
        """Initialize data source provider registry with instantiation.
        
        Dynamically imports and instantiates all data source providers defined in
        the configuration. Data sources provide external data access and must be
        available before capabilities that depend on them.
        
        Failed data source initialization is logged as warning but does not fail
        the entire registry initialization, allowing partial functionality.
        
        :raises Exception: Individual data source failures are caught and logged
        """
        logger.debug("Initializing data sources...")
        for reg in self.config.data_sources:
            try:
                # Dynamically import and instantiate the data source provider
                module = __import__(reg.module_path, fromlist=[reg.class_name])
                provider_class = getattr(module, reg.class_name)
                provider_instance = provider_class()
                self._registries['data_sources'][reg.name] = provider_instance
                logger.debug(f"Registered data source: {reg.name}")
            except Exception as e:
                logger.warning(f"Failed to initialize data source {reg.name}: {e}")
        
        logger.info(f"Registered {len(self._registries['data_sources'])} data sources")
    
    def _initialize_execution_policy_analyzers(self) -> None:
        """Initialize execution policy analyzer registry with instantiation.
        
        Dynamically imports and instantiates all execution policy analyzer classes defined
        in the configuration. These analyzers make execution mode and approval decisions
        based on code analysis results.
        
        Failed analyzer initialization is logged as warning but does not fail
        the entire registry initialization, allowing fallback to default analyzer.
        
        :raises Exception: Individual analyzer failures are caught and logged
        """
        logger.debug("Initializing execution policy analyzers...")
        for reg in self.config.execution_policy_analyzers:
            try:
                # Dynamically import and instantiate the execution policy analyzer
                module = __import__(reg.module_path, fromlist=[reg.class_name])
                analyzer_class = getattr(module, reg.class_name)
                # Note: analyzer instances need configurable, but we'll handle that in the manager
                # For now, just register the class for lazy instantiation
                self._registries['execution_policy_analyzers'][reg.name] = {
                    'class': analyzer_class,
                    'registration': reg
                }
                logger.debug(f"Registered execution policy analyzer: {reg.name}")
            except Exception as e:
                logger.warning(f"Failed to initialize execution policy analyzer {reg.name}: {e}")
        
        logger.info(f"Registered {len(self._registries['execution_policy_analyzers'])} execution policy analyzers")
    
    def _initialize_domain_analyzers(self) -> None:
        """Initialize domain analyzer registry with instantiation.
        
        Dynamically imports and instantiates all domain analyzer classes defined
        in the configuration. These analyzers analyze code for domain-specific
        patterns and operations.
        
        Failed analyzer initialization is logged as warning but does not fail
        the entire registry initialization, allowing fallback to default analyzer.
        
        :raises Exception: Individual analyzer failures are caught and logged
        """
        logger.debug("Initializing domain analyzers...")
        for reg in self.config.domain_analyzers:
            try:
                # Dynamically import and instantiate the domain analyzer
                module = __import__(reg.module_path, fromlist=[reg.class_name])
                analyzer_class = getattr(module, reg.class_name)
                # Note: analyzer instances need configurable, but we'll handle that in the manager
                # For now, just register the class for lazy instantiation
                self._registries['domain_analyzers'][reg.name] = {
                    'class': analyzer_class,
                    'registration': reg
                }
                logger.debug(f"Registered domain analyzer: {reg.name}")
            except Exception as e:
                logger.warning(f"Failed to initialize domain analyzer {reg.name}: {e}")
        
        logger.info(f"Registered {len(self._registries['domain_analyzers'])} domain analyzers")
    
    def _initialize_core_nodes(self) -> None:
        """Initialize core infrastructure nodes with LangGraph-native pattern.
        
        Dynamically imports and registers all infrastructure nodes.
        All infrastructure nodes are expected to use the @infrastructure_node decorator
        which creates a LangGraph-compatible function in the 'langgraph_node' attribute.
        :raises Exception: Core node initialization failures cause registry failure
        """
        logger.debug("Initializing core nodes...")
        for reg in self.config.core_nodes:
            try:
                # Dynamically import the module
                module = __import__(reg.module_path, fromlist=[reg.function_name])
                
                # Get the node class 
                node_class = getattr(module, reg.function_name)
                
                if inspect.isclass(node_class):
                    # The @infrastructure_node decorator should create langgraph_node
                    if hasattr(node_class, 'langgraph_node'):
                        if callable(node_class.langgraph_node):
                            # Register the LangGraph-native function directly
                            self._registries['nodes'][reg.name] = node_class.langgraph_node
                            logger.debug(f"Registered infrastructure node: {reg.name}")
                        else:
                            logger.error(f"Infrastructure node {reg.name} has invalid langgraph_node attribute - expected callable from @infrastructure_node decorator")
                    else:
                        logger.error(f"Infrastructure node {reg.name} missing langgraph_node attribute - ensure @infrastructure_node decorator is applied")
                else:
                    logger.error(f"Infrastructure node {reg.name} is not a class - expected decorated class")
                    
            except Exception as e:
                logger.error(f"Failed to load core node {reg.name} from {reg.module_path}.{reg.function_name}: {e}")
                raise
        
        logger.info(f"Registered {len(self.config.core_nodes)} core nodes")
    
    def _initialize_services(self) -> None:
        """Initialize service registry with LangGraph service graphs.
        
        Services are separate LangGraph graphs that provide specialized functionality
        while maintaining their internal node flow. Services are registered as
        callable graph instances that can be invoked by capabilities.
        :raises Exception: Service initialization failures are logged but don't fail registry
        """
        logger.debug("Initializing services...")
        for reg in self.config.services:
            try:
                # Dynamically import and instantiate the service
                module = __import__(reg.module_path, fromlist=[reg.class_name])
                service_class = getattr(module, reg.class_name)
                service_instance = service_class()
                
                # Store the service instance (not just the compiled graph)
                # This preserves the service's ainvoke method for request handling
                if hasattr(service_instance, 'get_compiled_graph'):
                    # Verify the service can compile its graph
                    self._registries['services'][reg.name] = service_instance
                    logger.debug(f"Registered service instance: {reg.name} with compiled graph")
                else:
                    logger.error(f"Service {reg.name} missing get_compiled_graph method")
                
                logger.debug(f"Registered service: {reg.name}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize service {reg.name}: {e}")
        
        logger.info(f"Registered {len(self._registries['services'])} services")
    
    def _initialize_capabilities(self) -> None:
        """Initialize capability registry with LangGraph-native pattern.
        
        Dynamically imports and registers all domain-specific capabilities.
        All capabilities are expected to use the @capability_node decorator which
        creates a LangGraph-compatible function in the 'langgraph_node' attribute.
        
        Failed capability initialization is logged as warning but does not fail
        the entire registry, allowing partial system functionality.
        """
        logger.debug("Initializing capabilities...")
        for reg in self.config.capabilities:
            try:
                # Dynamically import and instantiate the capability
                module = __import__(reg.module_path, fromlist=[reg.class_name])
                capability_class = getattr(module, reg.class_name)
                capability_instance = capability_class()
                self._registries['capabilities'][reg.name] = capability_instance
                
                # All capabilities should have @capability_node decorator which creates langgraph_node
                if hasattr(capability_class, 'langgraph_node'):
                    if callable(capability_class.langgraph_node):
                        # Register the decorator-created callable function directly
                        self._registries['nodes'][reg.name] = capability_class.langgraph_node
                        logger.debug(f"Registered capability node: {reg.name}")
                    else:
                        logger.error(f"Capability {reg.name} has invalid langgraph_node attribute - expected callable from @capability_node decorator")
                else:
                    logger.error(f"Capability {reg.name} missing langgraph_node attribute - ensure @capability_node decorator is applied")
                
                logger.debug(f"Registered capability: {reg.name}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize capability {reg.name}: {e}")
        
        logger.info(f"Registered {len(self._registries['capabilities'])} capabilities")
    
    def _initialize_framework_prompt_providers(self) -> None:
        """Initialize framework prompt providers with explicit mapping.
        
        Creates prompt providers using explicit builder class mapping. This provides 
        clear, maintainable prompt
        customization for different applications while maintaining compatibility
        with the default prompt system.
        
        The first registered provider is automatically set as the default for
        the framework prompt system.
        
        :raises Exception: Individual provider failures are caught and logged
        """
        logger.debug("Initializing framework prompt providers...")
        for reg in self.config.framework_prompt_providers:
            try:
                # Create provider using explicit mapping
                provider = self._create_explicit_provider(reg)
                
                # Register the provider
                from framework.prompts.loader import _prompt_loader
                _prompt_loader._providers[reg.application_name] = provider
                
                self._registries['framework_prompt_providers'][reg.application_name] = reg
                logger.debug(f"Registered explicit provider for {reg.application_name} with {len(reg.prompt_builders)} builders")
                    
            except Exception as e:
                logger.warning(f"Failed to initialize framework prompt provider {reg.application_name}: {e}")
        
        # Set default provider - prefer application-specific providers over framework defaults
        if self.config.framework_prompt_providers:
            # Find the first non-framework provider for production-ready default selection
            default_app = None
            for provider in self.config.framework_prompt_providers:
                if provider.application_name != "framework_defaults":
                    default_app = provider.application_name
                    break
            
            # Fallback to framework defaults if no application providers exist
            if default_app is None:
                default_app = self.config.framework_prompt_providers[0].application_name
            
            from framework.prompts.loader import set_default_framework_prompt_provider
            set_default_framework_prompt_provider(default_app)
            logger.info(f"Set default framework prompt provider to: {default_app}")
        
        logger.info(f"Registered {len(self._registries['framework_prompt_providers'])} framework prompt providers")
    
    def _create_explicit_provider(self, reg):
        """Create prompt provider by overriding defaults with application-specific builders.
        
        Follows the professional dependency injection pattern: start with framework defaults,
        then override specific components based on application registry configuration.
        This approach minimizes configuration (applications only declare what they customize)
        while providing graceful fallbacks for everything else.
        
        :param reg: Framework prompt provider registration configuration
        :type reg: FrameworkPromptProviderRegistration
        :return: Configured prompt provider with application overrides
        :rtype: framework.prompts.defaults.DefaultPromptProvider
        :raises ImportError: If builder class modules cannot be imported
        :raises AttributeError: If builder classes are not found in modules
        """
        from framework.prompts.defaults import DefaultPromptProvider
        
        # Start with framework defaults for everything
        provider = DefaultPromptProvider()
        
        # Track successful/failed overrides for logging
        successful_overrides = []
        failed_overrides = []
        
        # Override specific builders based on application registry
        for prompt_type, class_name in reg.prompt_builders.items():
            try:
                # Import the application-specific builder class
                module = __import__(reg.module_path, fromlist=[class_name])
                builder_class = getattr(module, class_name)
                builder_instance = builder_class()
                
                # Override the default builder (follows established naming convention)
                attr_name = f"_{prompt_type}_builder"
                setattr(provider, attr_name, builder_instance)
                
                successful_overrides.append(prompt_type)
                logger.debug(f"  -> Overrode {prompt_type} with {class_name}")
                
            except Exception as e:
                failed_overrides.append((prompt_type, class_name, str(e)))
                logger.warning(f"Failed to load prompt builder {class_name}: {e}")
                # Continue with framework default for this builder
        
        # Log summary
        total_builders = len(reg.prompt_builders)
        if successful_overrides:
            logger.info(f"Successfully loaded {len(successful_overrides)}/{total_builders} custom prompt builders for {reg.application_name}")
        if failed_overrides:
            logger.warning(f"Failed to load {len(failed_overrides)} prompt builders for {reg.application_name} - using framework defaults")
            for prompt_type, class_name, error in failed_overrides:
                logger.debug(f"  -> {prompt_type}({class_name}): {error}")
        
        # Validate the final provider implements the complete interface
        self._validate_prompt_provider(provider, reg.application_name)
        
        return provider
    
    def _validate_prompt_provider(self, provider, application_name):
        """Validate prompt provider implements required interface methods.
        
        Ensures the provider implements all required methods for framework operation.
        Missing methods are logged as errors but do not prevent provider registration,
        allowing partial functionality with fallback to defaults.
        
        :param provider: Prompt provider instance to validate
        :type provider: framework.prompts.defaults.DefaultPromptProvider
        :param application_name: Application name for error reporting
        :type application_name: str
        """
        required_methods = [
            'get_orchestrator_prompt_builder',
            'get_task_extraction_prompt_builder',
            'get_response_generation_prompt_builder',
            'get_classification_prompt_builder',
            'get_error_analysis_prompt_builder',
            'get_clarification_prompt_builder',
            'get_memory_extraction_prompt_builder',
            'get_time_range_parsing_prompt_builder'
        ]
        
        missing_methods = []
        for method_name in required_methods:
            if not hasattr(provider, method_name) or not callable(getattr(provider, method_name)):
                missing_methods.append(method_name)
        
        if missing_methods:
            logger.error(f"Prompt provider for {application_name} is missing required methods: {missing_methods}")
        else:
            logger.debug(f"Prompt provider for {application_name} passed interface validation")

    
    # ==============================================================================
    # EXPORT FUNCTIONALITY
    # ==============================================================================
    
    def export_registry_to_json(self, output_dir: str = None) -> Dict[str, Any]:
        """Export registry metadata for external tools and plan editors.
        
        Creates comprehensive JSON export of all registered components including
        capabilities, context types, and workflow templates. This data is used by
        execution plan editors and other external tools to understand system capabilities.
        
        :param output_dir: Directory path for saving JSON files, if None returns data only
        :type output_dir: str, optional
        :return: Complete registry metadata with capabilities, context types, and templates
        :rtype: dict[str, Any]
        :raises Exception: If file writing fails when output_dir is specified
        
        Examples:
            Export to directory::
            
                >>> registry = get_registry()
                >>> data = registry.export_registry_to_json("/tmp/registry")
                >>> print(f"Exported {data['metadata']['total_capabilities']} capabilities")
                
            Get data without saving::
            
                >>> data = registry.export_registry_to_json()
                >>> capabilities = data['capabilities']
        """
        export_data = {
            "capabilities": self._export_capabilities(),
            "context_types": self._export_context_types(),
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "registry_version": "1.0",
                "total_capabilities": len(self.config.capabilities),
                "total_context_types": len(self.config.context_classes)
            }
        }
        
        if output_dir:
            self._save_export_data(export_data, output_dir)
        
        return export_data
    
    def _export_capabilities(self) -> List[Dict[str, Any]]:
        """Export capability metadata for external consumption.
        
        Transforms internal capability registrations into standardized format
        suitable for execution plan editors and documentation tools. Exports
        all registered capabilities without filtering.
        
        :return: List of capability metadata dictionaries
        :rtype: list[dict[str, Any]]
        """
        capabilities = []
        
        for cap_reg in self.config.capabilities:
                
            capability_data = {
                "name": cap_reg.name,
                "description": cap_reg.description,
                "provides": cap_reg.provides,
                "requires": cap_reg.requires,
                "module_path": cap_reg.module_path,
                "class_name": cap_reg.class_name
            }
            capabilities.append(capability_data)
        
        return capabilities
    
    def _export_context_types(self) -> List[Dict[str, Any]]:
        """Export context type metadata for external consumption.
        
        Transforms internal context class registrations into standardized format
        suitable for execution plan editors and documentation tools. Exports
        all registered context types without filtering.
        
        :return: List of context type metadata dictionaries
        :rtype: list[dict[str, Any]]
        """
        context_types = []
        
        for ctx_reg in self.config.context_classes:
            context_data = {
                "context_type": ctx_reg.context_type,
                "class_name": ctx_reg.class_name,
                "module_path": ctx_reg.module_path,
                "description": getattr(ctx_reg, 'description', f"Context class {ctx_reg.class_name}")
            }
            context_types.append(context_data)
        
        return context_types
    
    def _save_export_data(self, export_data: Dict[str, Any], output_dir: str) -> None:
        """Save registry export data to JSON files.
        
        Creates directory if needed and saves both complete export and individual
        component files for easier access by external tools.
        
        :param export_data: Complete registry export data
        :type export_data: dict[str, Any]
        :param output_dir: Target directory for JSON files
        :type output_dir: str
        :raises OSError: If directory creation or file writing fails
        :raises Exception: If JSON serialization fails
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save complete export data
            export_file = Path(output_dir) / "registry_export.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            
            # Save individual components for easier access
            components = ["capabilities", "context_types"]
            for component in components:
                if component in export_data:
                    component_file = Path(output_dir) / f"{component}.json"
                    with open(component_file, 'w', encoding='utf-8') as f:
                        json.dump(export_data[component], f, indent=2, ensure_ascii=False)
                    logger.debug(f"Saved {component} to: {component_file}")
            
            logger.info(f"Registry export saved to: {export_file}")
            logger.info(f"Export contains: {export_data['metadata']['total_capabilities']} capabilities, "
                        f"{export_data['metadata']['total_context_types']} context types")
            
        except Exception as e:
            logger.error(f"Failed to save export data: {e}")
            raise
    

    
    # ==============================================================================
    # PUBLIC ACCESS METHODS
    # ==============================================================================
    
    def get_capability(self, name: str) -> Optional['BaseCapability']:
        """Retrieve registered capability instance by name.
        
        :param name: Unique capability name from registration
        :type name: str
        :return: Capability instance if registered, None otherwise
        :rtype: framework.base.BaseCapability, optional
        """
        return self._registries['capabilities'].get(name)
    
    def get_always_active_capability_names(self) -> List[str]:
        """Get names of capabilities marked as always active.
        
        :return: List of capability names that are always active
        :rtype: List[str]
        """
        return [cap_reg.name for cap_reg in self.config.capabilities if cap_reg.always_active]
    
    def get_all_capabilities(self) -> List['BaseCapability']:
        """Retrieve all registered capability instances.
        
        :return: List of all registered capability instances
        :rtype: list[framework.base.BaseCapability]
        """
        return list(self._registries['capabilities'].values())
    
    def get_capabilities_overview(self) -> str:
        """Generate a text overview of all registered capabilities.
        
        :return: Human-readable overview of capabilities and their descriptions
        :rtype: str
        """
        capabilities = self.get_all_capabilities()
        if not capabilities:
            return "No capabilities currently available."
        
        overview_lines = ["Available Capabilities:"]
        for capability in capabilities:
            name = getattr(capability, 'name', 'Unknown')
            description = getattr(capability, 'description', 'No description available')
            overview_lines.append(f"• {name}: {description}")
        
        return "\n".join(overview_lines)
    
    def get_node(self, name: str) -> Optional['BaseCapabilityNode']:
        """Retrieve registered node instance by name.
        
        :param name: Unique node name from registration
        :type name: str
        :return: Node instance if registered, None otherwise
        :rtype: framework.base.BaseCapabilityNode, optional
        """ 
        return self._registries['nodes'].get(name)
    
    def get_all_nodes(self) -> Dict[str, Any]:
        """Retrieve all registered nodes as (name, callable) pairs.
        
        :return: Dictionary mapping node names to their callable instances
        :rtype: Dict[str, Any]
        """
        return dict(self._registries['nodes'].items())
    
    def get_context_class(self, context_type: str) -> Optional[Type['CapabilityContext']]:
        """Retrieve context class by type identifier.
        
        :param context_type: Context type identifier (e.g., 'PV_ADDRESSES')
        :type context_type: str
        :return: Context class if registered, None otherwise
        :rtype: Type[framework.base.CapabilityContext], optional
        """
        return self._registries['contexts'].get(context_type)
    
    def get_context_class_by_name(self, class_name: str):
        """Retrieve context class by class name identifier.
        
        :param class_name: Python class name (e.g., 'PVAddresses')
        :type class_name: str
        :return: Context class if found, None otherwise
        :rtype: Type[framework.base.CapabilityContext], optional
        """
        for ctx_reg in self.config.context_classes:
            if ctx_reg.class_name == class_name:
                return self.get_context_class(ctx_reg.context_type)
        return None
    
    def is_valid_context_type(self, context_type: str) -> bool:
        """Check if a context type is registered in the registry.
        
        :param context_type: Context type identifier (e.g., 'PV_ADDRESSES')
        :type context_type: str
        :return: True if context type is registered, False otherwise
        :rtype: bool
        """
        return context_type in self._registries['contexts']
    
    def get_all_context_types(self) -> List[str]:
        """Get list of all registered context types.
        
        :return: List of all registered context type identifiers
        :rtype: list[str]
        """
        return list(self._registries['contexts'].keys())
    
    def get_all_context_classes(self) -> Dict[str, Type['CapabilityContext']]:
        """Get dictionary of all registered context classes by context type.
        
        This method provides access to all registered context classes indexed by their
        context type identifiers. It enables introspection of the complete context
        system and supports dynamic context handling patterns.
        
        :return: Dictionary mapping context types to their corresponding context classes
        :rtype: Dict[str, Type[CapabilityContext]]
        
        Examples:
            Access all context classes::
            
                >>> registry = get_registry()
                >>> context_classes = registry.get_all_context_classes()
                >>> pv_class = context_classes.get("PV_ADDRESSES")
                >>> if pv_class:
                ...     instance = pv_class(pvs=["test:pv"])
        """
        return dict(self._registries['contexts'])
    
    def get_data_source(self, name: str) -> Optional[Any]:
        """Retrieve data source provider instance by name.
        
        :param name: Unique data source name from registration
        :type name: str
        :return: Data source provider instance if registered, None otherwise
        :rtype: Any, optional
        """
        return self._registries['data_sources'].get(name)
    
    def get_all_data_sources(self) -> List[Any]:
        """Retrieve all registered data source provider instances.
        
        :return: List of all registered data source provider instances
        :rtype: list[Any]
        """
        return list(self._registries['data_sources'].values())
    
    def get_service(self, name: str) -> Optional[Any]:
        """Retrieve registered service graph by name.
        
        :param name: Unique service name from registration
        :type name: str
        :return: Compiled LangGraph service instance if registered, None otherwise
        :rtype: Any, optional
        """
        return self._registries['services'].get(name)
    
    def get_all_services(self) -> List[Any]:
        """Retrieve all registered service graph instances.
        
        :return: List of all registered service graph instances
        :rtype: list[Any]
        """
        return list(self._registries['services'].values())
    
    def get_execution_policy_analyzers(self) -> List[Any]:
        """Retrieve all registered execution policy analyzer instances.
        
        Creates instances of execution policy analyzers with empty configurable.
        The actual configurable will be provided when the analyzers are used.
        
        :return: List of execution policy analyzer instances
        :rtype: list[Any]
        """
        analyzers = []
        for name, registry_entry in self._registries['execution_policy_analyzers'].items():
            try:
                analyzer_class = registry_entry['class']
                # Create instance with empty configurable - will be set properly when used
                analyzer_instance = analyzer_class({})
                analyzers.append(analyzer_instance)
            except Exception as e:
                logger.warning(f"Failed to instantiate execution policy analyzer {name}: {e}")
        return analyzers
    
    def get_domain_analyzers(self) -> List[Any]:
        """Retrieve all registered domain analyzer instances.
        
        Creates instances of domain analyzers with empty configurable.
        The actual configurable will be provided when the analyzers are used.
        
        :return: List of domain analyzer instances
        :rtype: list[Any]
        """
        analyzers = []
        for name, registry_entry in self._registries['domain_analyzers'].items():
            try:
                analyzer_class = registry_entry['class']
                # Create instance with empty configurable - will be set properly when used
                analyzer_instance = analyzer_class({})
                analyzers.append(analyzer_instance)
            except Exception as e:
                logger.warning(f"Failed to instantiate domain analyzer {name}: {e}")
        return analyzers
    
    def get_available_data_sources(self, state: Any) -> List[Any]:
        """Retrieve available data sources for current execution context.
        
        Filters all registered data sources based on their availability for the
        current agent state and returns them in registration order (framework
        providers first, then applications).
        
        :param state: Current agent state for availability checking
        :type state: framework.state.AgentState
        :return: Available data source providers in registration order
        :rtype: list[Any]
        
        .. note::
           Providers without is_available() method are assumed to be available.
        """
        available = []
        for provider in self._registries['data_sources'].values():
            try:
                if hasattr(provider, 'is_available') and provider.is_available(state):
                    available.append(provider)
                else:
                    # Fallback - assume available if no is_available method
                    available.append(provider)
            except Exception as e:
                logger.warning(f"Failed to check availability for {provider}: {e}")
        
        return available
    

    
    @property
    def context_types(self):
        """Dynamic object providing context type constants as attributes.
        
        Creates a dynamic object where each registered context type is accessible
        as an attribute with its string value.
        
        :return: Object with context types as attributes
        :rtype: object
        
        Examples:
            Access context types::
            
                >>> registry = get_registry()
                >>> pv_type = registry.context_types.PV_ADDRESSES
                >>> print(pv_type)  # "PV_ADDRESSES"
        """
        if not hasattr(self, '_context_types'):
            self._context_types = type('ContextTypes', (), {
                ctx_reg.context_type: ctx_reg.context_type 
                for ctx_reg in self.config.context_classes
            })()
        return self._context_types
    
    @property 
    def capability_names(self):
        """Dynamic object providing capability names as constants with debug fallback.
        
        Creates a dynamic object where each registered capability name is accessible
        as an uppercase constant attribute. If a capability name is not registered,
        returns the expected string and logs a warning (useful for development).
        
        :return: Object with capability names as constant attributes
        :rtype: object
        
        Examples:
            Access capability names as constants::
            
                >>> registry = get_registry()
                >>> pv_finding = registry.capability_names.PV_ADDRESS_FINDING
                >>> print(pv_finding)  # "pv_address_finding"
                
            Graceful fallback for missing capabilities::
            
                >>> viz_name = registry.capability_names.DATA_VISUALIZATION  # Not registered
                >>> print(viz_name)  # "data_visualization" (with warning logged)
        """
        if not hasattr(self, '_capability_names'):
            # Build registry of known capabilities
            registered_constants = {}
            for cap_reg in self.config.capabilities:
                # Convert to constant format: "pv_address_finding" -> "PV_ADDRESS_FINDING"
                const_name = cap_reg.name.upper().replace('-', '_')
                registered_constants[const_name] = cap_reg.name
            
            # Create proxy class with graceful fallback
            class CapabilityNamesProxy:
                def __init__(self, constants):
                    self._constants = constants
                
                def __getattr__(self, name):
                    # First check if it's a registered capability
                    if name in self._constants:
                        return self._constants[name]
                    
                    # Graceful fallback for missing capabilities
                    # Convert from constant back to capability name: "DATA_VISUALIZATION" -> "data_visualization"
                    capability_name = name.lower()
                    
                    # Log warning for debugging
                    logger.warning(f"🔧 DEBUG: Accessing unregistered capability '{capability_name}' via registry.capability_names.{name}")
                    logger.warning(f"🔧 DEBUG: Returning fallback string '{capability_name}' - this capability is not in the registry")
                    logger.warning(f"🔧 DEBUG: Registered capabilities: {list(self._constants.keys())}")
                    
                    return capability_name
                
                def __dir__(self):
                    # For introspection/debugging - show registered capabilities
                    return list(self._constants.keys())
            
            self._capability_names = CapabilityNamesProxy(registered_constants)
        return self._capability_names
    
    # ==============================================================================
    # VALIDATION AND DEBUGGING
    # ==============================================================================
    
    def validate_configuration(self) -> List[str]:
        """Validate registry configuration for consistency and completeness.
        
        Performs comprehensive validation of the registry configuration including
        duplicate name checking, dependency validation, and structural consistency.
        This method should be called before initialization to catch configuration
        errors early.
        
        :return: List of validation error messages, empty if valid
        :rtype: list[str]
        
        Examples:
            Validate before initialization::
            
                >>> registry = get_registry()
                >>> errors = registry.validate_configuration()
                >>> if errors:
                ...     print(f"Configuration errors: {errors}")
                ... else:
                ...     registry.initialize()
        """
        errors = []
        
        # Check for duplicate capability names
        capability_names = [cap.name for cap in self.config.capabilities]
        if len(capability_names) != len(set(capability_names)):
            errors.append("Duplicate capability names found")
        
        # Check for duplicate node names
        core_node_names = [node.name for node in self.config.core_nodes]
        if len(core_node_names) != len(set(core_node_names)):
            errors.append("Duplicate core node names found")
        
        # Check for duplicate context types
        context_types = [ctx.context_type for ctx in self.config.context_classes]
        if len(context_types) != len(set(context_types)):
            errors.append("Duplicate context types found")
        
        # Check for duplicate data source names
        data_source_names = [ds.name for ds in self.config.data_sources]
        if len(data_source_names) != len(set(data_source_names)):
            errors.append("Duplicate data source names found")
        
        # Note: Dependencies are tracked through context types (requires/provides)
        # rather than explicit capability dependencies
        
        return errors
    
    def _get_initialization_summary(self) -> str:
        """Generate user-friendly initialization summary.
        
        Creates a multi-line, readable summary of registry initialization
        that's much more user-friendly than the raw stats dictionary.
        
        :return: Formatted initialization summary
        :rtype: str
        """
        stats = self.get_stats()
        
        # Build the summary with better formatting
        summary_lines = [
            "Registry initialization complete!",
            f"   Components loaded:",
            f"      • {stats['capabilities']} capabilities: {', '.join(stats['capability_names'])}",
            f"      • {stats['nodes']} nodes (including {len(self.config.core_nodes)} core infrastructure)",
            f"      • {stats['context_classes']} context types: {', '.join(stats['context_types'])}",
            f"      • {stats['data_sources']} data sources: {', '.join(stats['data_source_names'])}",
            f"      • {stats['services']} services: {', '.join(stats['service_names'])}"
        ]
        
        return "\n".join(summary_lines)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retrieve comprehensive registry statistics for debugging.
        
        :return: Dictionary containing counts and lists of registered components
        :rtype: dict[str, Any]
        
        Examples:
            Check registry status::
            
                >>> registry = get_registry()
                >>> stats = registry.get_stats()
                >>> print(f"Loaded {stats['capabilities']} capabilities")
                >>> print(f"Available: {stats['capability_names']}")
        """
        return {
            'initialized': self._initialized,
            'capabilities': len(self._registries['capabilities']),
            'nodes': len(self._registries['nodes']),
            'context_classes': len(self._registries['contexts']),
            'data_sources': len(self._registries['data_sources']),
            'services': len(self._registries['services']),
            'capability_names': list(self._registries['capabilities'].keys()),
            'node_names': list(self._registries['nodes'].keys()),
            'context_types': list(self._registries['contexts'].keys()),
            'data_source_names': list(self._registries['data_sources'].keys()),
            'service_names': list(self._registries['services'].keys())
        }
    

    
    def clear(self) -> None:
        """Clear all registry data and reset initialization state.
        
        Removes all registered components and marks the registry as uninitialized.
        This method is primarily used for testing to ensure clean state between tests.
        
        .. warning::
           This method clears all registered components. Only use for testing
           or complete registry reset scenarios.
        """
        logger.debug("Clearing registry")
        for registry in self._registries.values():
            registry.clear()
        self._initialized = False

# ==============================================================================
# GLOBAL REGISTRY INSTANCE
# ==============================================================================

_registry: Optional[RegistryManager] = None

def get_registry() -> RegistryManager:
    """Retrieve the global registry manager singleton instance.
    
    Returns the global registry manager instance, creating it automatically if it
    doesn't exist. This function provides the primary access point for the registry
    system throughout the framework, ensuring consistent access to the same registry
    instance across all framework components.
    
    The registry instance is created from the global configuration. Applications 
    are loaded from the 'applications' configuration key and their registries 
    are loaded using the pattern: applications.{app_name}.registry
    
    Singleton Behavior:
        - First call creates the registry instance from configuration
        - Subsequent calls return the same instance
        - Registry persists for the lifetime of the application
        - Thread-safe access to the global instance
    
    Registry Creation Process:
        1. Read 'applications' list from global configuration
        2. Create RegistryManager with configured application names
        3. Build merged configuration (framework + applications)
        4. Return uninitialized registry instance
    
    :return: The global registry manager singleton instance. The instance may not
        be initialized - call initialize_registry() or registry.initialize() to
        load components before accessing them
    :rtype: RegistryManager
    :raises ConfigurationError: If global configuration is invalid or applications
        configuration is malformed
    :raises RuntimeError: If registry creation fails due to configuration issues
    
    .. note::
       The returned registry instance may not be initialized. Components are not
       available until initialize_registry() or registry.initialize() is called.
       
    .. warning::
       This function creates the registry from global configuration on first access.
       Ensure configuration is properly set before calling this function.
    
    Examples:
        Basic registry access::
        
            >>> from framework.registry import get_registry, initialize_registry
            >>> 
            >>> # Initialize first, then access
            >>> initialize_registry()
            >>> registry = get_registry()
            >>> capability = registry.get_capability("pv_address_finding")
        
        Check if registry is initialized::
        
            >>> registry = get_registry()
            >>> if not registry._initialized:
            ...     registry.initialize()
            >>> stats = registry.get_stats()
            
        Access registry from different modules::
        
            >>> # Same instance returned everywhere
            >>> from framework.registry import get_registry
            >>> registry1 = get_registry()
            >>> registry2 = get_registry()
            >>> assert registry1 is registry2  # Same instance
    
    .. seealso::
       :func:`initialize_registry` : Initialize the registry system with components
       :func:`reset_registry` : Reset the global registry instance
       :class:`RegistryManager` : The registry manager class returned by this function
       :doc:`/developer-guides/03_core-framework-systems/03_registry-and-discovery` : Registry access patterns
    """
    global _registry
    
    if _registry is None:
        logger.debug("Creating new registry instance...")
        _registry = _create_registry_from_config()
    else:
        logger.debug("Using existing registry instance...")
    
    return _registry

def _create_registry_from_config() -> RegistryManager:
    """Create registry manager from global configuration.
    
    Expects simple application list in the format:
    applications:
      - als_expert
      - wind_turbine
    
    Uses conventions:
    - Config: src/applications/{app}/config.yml
    - Registry: applications.{app}.registry
    
    :return: Configured registry manager
    :rtype: RegistryManager
    """
    logger.debug("Creating registry from config...")
    try:
        # Extract application list
        applications = get_config_value('applications', [])
        
        if isinstance(applications, list):
            application_names = applications
            logger.debug(f"Using applications from list: {application_names}")
        elif isinstance(applications, dict):
            # Handle case where applications is a dict with application configs
            application_names = list(applications.keys())
            logger.debug(f"Using applications from dict keys: {application_names}")
        else:
            # Configuration error - applications must be a list or dict
            raise ConfigurationError(
                f"Configuration 'applications' must be a list of application names or "
                f"a dict with application configurations, got {type(applications).__name__}: {applications}"
            )
        
        if not application_names:
            logger.warning("No applications configured - using framework-only configuration")
        
        return RegistryManager(application_names)
        
    except Exception as e:
        logger.error(f"Failed to create registry from config: {e}")
        raise RuntimeError(f"Registry creation failed: {e}") from e

def initialize_registry(auto_export: bool = True) -> None:
    """Initialize the global registry system with all components.
    
    Performs complete initialization of the global registry system, including
    loading of application registries, component loading in dependency order,
    and optional export of registry metadata for external tools. This function
    should be called once during application startup before accessing any
    framework components.
    
    The initialization process:
    1. Gets or creates the global registry singleton instance
    2. Loads all components in proper dependency order
    3. Validates that all components loaded successfully
    4. Optionally exports registry metadata to JSON files
    5. Sets up the registry for component access throughout the application
    
    Component Loading Order:
        - Context classes (data structures)
        - Data sources (external data providers)
        - Core nodes (infrastructure components)
        - Services (internal LangGraph service graphs)
        - Capabilities (domain-specific functionality)
        - Framework prompt providers (application customizations)
    
    Auto-Export Functionality:
        When auto_export is True, the function automatically exports complete
        registry metadata to JSON files for use by external tools, execution
        plan editors, and documentation systems. Export includes capability
        definitions, context types, and component relationships.
    
    :param auto_export: Whether to automatically export registry metadata to JSON
        files after successful initialization. Export files are saved to the
        configured registry_exports_dir location
    :type auto_export: bool
    :raises RegistryError: If registry initialization fails due to component loading
        errors, missing modules, or invalid component definitions
    :raises ConfigurationError: If global configuration is invalid, application
        configurations are malformed, or dependencies are inconsistent
    :raises ImportError: If any component module cannot be imported
    :raises AttributeError: If any component class or function is not found
    
    .. note::
       This function is idempotent - multiple calls have no effect if the registry
       is already initialized. The initialization state persists for the application
       lifetime.
       
    .. warning::
       This function must be called before accessing any framework components.
       Attempting to access components before initialization will result in
       empty or incomplete results.
    
    Examples:
        Basic application startup::
        
            >>> from framework.registry import initialize_registry, get_registry
            >>> 
            >>> # Initialize during application startup
            >>> initialize_registry()
            >>> 
            >>> # Now components are available
            >>> registry = get_registry()
            >>> capability = registry.get_capability("pv_address_finding")
            
        Initialize without metadata export::
        
            >>> # Skip JSON export for faster initialization
            >>> initialize_registry(auto_export=False)
            
        Handle initialization errors::
        
            >>> try:
            ...     initialize_registry()
            ...     print("Registry initialized successfully")
            ... except RegistryError as e:
            ...     print(f"Registry initialization failed: {e}")
            ...     # Handle missing components or configuration issues
            
        Check initialization results::
        
            >>> initialize_registry()
            >>> registry = get_registry()
            >>> stats = registry.get_stats()
            >>> print(f"Loaded {stats['capabilities']} capabilities")
    
    .. seealso::
       :func:`get_registry` : Access the initialized registry instance
       :func:`reset_registry` : Reset registry for testing or reconfiguration
       :meth:`RegistryManager.initialize` : Core initialization method called by this function
       :meth:`RegistryManager.export_registry_to_json` : Export functionality used when auto_export=True
    """
    registry = get_registry()
    registry.initialize()
    
    # Auto-export registry data if requested
    if auto_export:
        try:
            # Load app config to get proper paths
            # Build export directory path from config
            export_dir = Path(get_agent_dir('registry_exports_dir'))
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Export registry data
            registry.export_registry_to_json(str(export_dir))
            

            
        except Exception as e:
            logger.warning(f"Failed to auto-export registry data: {e}")
            # Don't fail initialization if export fails

def reset_registry() -> None:
    """Reset the global registry instance to uninitialized state.
    
    Completely clears the global registry instance and resets it to None,
    forcing the next call to get_registry() to create a fresh instance.
    This function is primarily used for testing scenarios where clean
    registry state is required between test runs.
    
    The reset process:
    1. Clears all component registries in the current instance
    2. Resets the initialization state to False
    3. Sets the global registry instance to None
    4. Next get_registry() call will create a new instance from configuration
    
    This function provides a clean slate for testing different registry
    configurations or ensuring test isolation when registry state might
    affect test outcomes.
    
    .. warning::
       This function completely destroys all registry data and component
       references. Only use for testing scenarios or complete application
       reset. Production code should never call this function.
       
    .. note::
       After calling this function, initialize_registry() must be called
       again before accessing any framework components.
    
    Examples:
        Reset for unit testing::
        
            >>> # At the start of each test
            >>> reset_registry()
            >>> initialize_registry()  # Fresh registry for this test
            >>> registry = get_registry()
            >>> # Test registry functionality
            
        Reset between test configurations::
        
            >>> # Test with framework-only configuration
            >>> reset_registry()
            >>> # Modify global config to have no applications
            >>> initialize_registry()
            >>> registry = get_registry()
            >>> assert len(registry.get_all_capabilities()) == framework_count
            >>> 
            >>> # Reset and test with applications
            >>> reset_registry()
            >>> # Modify global config to include applications
            >>> initialize_registry()
            >>> registry = get_registry()
            >>> assert len(registry.get_all_capabilities()) > framework_count
            
        Complete application reset::
        
            >>> # Nuclear option - complete reset
            >>> reset_registry()
            >>> # Registry must be reinitialized before use
            >>> initialize_registry()
    
    .. seealso::
       :func:`get_registry` : Access the global registry (creates new after reset)
       :func:`initialize_registry` : Must be called after reset to use components
       :meth:`RegistryManager.clear` : Method called internally to clear registry data
    """
    global _registry
    if _registry:
        _registry.clear()
    _registry = None

# ==============================================================================
# GLOBAL REGISTRY INSTANCE EXPORT
# ==============================================================================

class _LazyRegistryProxy:
    """Proxy that creates registry only when first accessed to avoid circular imports."""
    
    def __getattr__(self, name):
        # Always use the global singleton instance from get_registry()
        return getattr(get_registry(), name)
    
    def __call__(self, *args, **kwargs):
        # Always use the global singleton instance from get_registry()
        return get_registry()(*args, **kwargs)

# Export the global registry instance
registry = _LazyRegistryProxy()