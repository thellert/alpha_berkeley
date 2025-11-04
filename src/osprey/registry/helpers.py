"""Registry helper functions for application development.

This module provides utilities that simplify application registry creation
by handling the common pattern of extending the framework registry with
application-specific components.

The helper functions eliminate boilerplate code and provide a clean,
intuitive API for application developers to define their registries.
"""

from typing import List, Optional
from .base import (
    RegistryConfig,
    NodeRegistration,
    CapabilityRegistration,
    ContextClassRegistration,
    DataSourceRegistration,
    ServiceRegistration,
    FrameworkPromptProviderRegistration
)


def extend_framework_registry(
    capabilities: Optional[List[CapabilityRegistration]] = None,
    context_classes: Optional[List[ContextClassRegistration]] = None,
    data_sources: Optional[List[DataSourceRegistration]] = None,
    services: Optional[List[ServiceRegistration]] = None,
    framework_prompt_providers: Optional[List[FrameworkPromptProviderRegistration]] = None,
    core_nodes: Optional[List[NodeRegistration]] = None,
    exclude_capabilities: Optional[List[str]] = None,
    exclude_nodes: Optional[List[str]] = None,
    exclude_context_classes: Optional[List[str]] = None,
    exclude_data_sources: Optional[List[str]] = None,
    override_capabilities: Optional[List[CapabilityRegistration]] = None,
    override_nodes: Optional[List[NodeRegistration]] = None,
) -> RegistryConfig:
    """Create application registry configuration that extends the framework.

    This is the recommended way to create application registries. It simplifies
    registry creation by automatically handling framework component exclusions
    and overrides through clean, declarative parameters.

    The function returns an application registry configuration that will be
    merged with the framework registry by the RegistryManager. You only need
    to specify your application-specific components and any framework components
    you want to exclude or replace.

    Most applications will only need to specify capabilities and context_classes.

    Args:
        capabilities: Application capabilities to add to framework defaults
        context_classes: Application context classes to add to framework defaults
        data_sources: Application data sources to add to framework defaults
        services: Application services to add to framework defaults
        framework_prompt_providers: Application prompt providers to add
        exclude_capabilities: Names of framework capabilities to exclude
        exclude_nodes: Names of framework nodes to exclude
        exclude_context_classes: Context types to exclude from framework
        exclude_data_sources: Names of framework data sources to exclude
        override_capabilities: Capabilities that replace framework versions (by name)
        override_nodes: Nodes that replace framework versions (by name)

    Returns:
        Complete RegistryConfig with framework + application components

    Examples:
        Simple application (most common)::

            def get_registry_config(self) -> RegistryConfig:
                return extend_framework_registry(
                    capabilities=[
                        CapabilityRegistration(
                            name="weather",
                            module_path="my_app.capabilities.weather",
                            class_name="WeatherCapability",
                            description="Get weather information",
                            provides=["WEATHER_DATA"],
                            requires=[]
                        ),
                    ],
                    context_classes=[
                        ContextClassRegistration(
                            context_type="WEATHER_DATA",
                            module_path="my_app.context_classes",
                            class_name="WeatherContext"
                        ),
                    ]
                )

        Exclude framework component::

            def get_registry_config(self) -> RegistryConfig:
                return extend_framework_registry(
                    capabilities=[...],
                    exclude_capabilities=["python"],  # Don't need framework Python
                )

        Override framework component::

            def get_registry_config(self) -> RegistryConfig:
                return extend_framework_registry(
                    capabilities=[...],
                    override_capabilities=[
                        CapabilityRegistration(
                            name="memory",  # Replace framework memory
                            module_path="my_app.capabilities.custom_memory",
                            class_name="CustomMemoryCapability",
                            description="Custom memory implementation",
                            provides=["MEMORY_CONTEXT"],
                            requires=[]
                        ),
                    ]
                )

    .. note::
       The returned configuration contains only application components. The
       framework registry system automatically merges this with framework defaults
       during initialization. Exclusions are handled internally via the
       framework_exclusions field.

    .. seealso::
       :func:`get_framework_defaults` : Inspect framework components
       :class:`RegistryConfig` : The returned configuration structure
    """
    # Build framework exclusions dict for the merge process
    framework_exclusions = {}

    if exclude_capabilities:
        framework_exclusions["capabilities"] = exclude_capabilities

    if exclude_nodes:
        framework_exclusions["nodes"] = exclude_nodes

    if exclude_context_classes:
        framework_exclusions["context_classes"] = exclude_context_classes

    if exclude_data_sources:
        framework_exclusions["data_sources"] = exclude_data_sources

    # Combine override and regular components
    all_capabilities = list(capabilities or [])
    if override_capabilities:
        all_capabilities.extend(override_capabilities)

    all_nodes = list(core_nodes or [])
    if override_nodes:
        all_nodes.extend(override_nodes)

    # Return APPLICATION-ONLY config (framework will be merged by RegistryManager)
    return RegistryConfig(
        core_nodes=all_nodes,
        capabilities=all_capabilities,
        context_classes=list(context_classes or []),
        data_sources=list(data_sources or []),
        services=list(services or []),
        framework_prompt_providers=list(framework_prompt_providers or []),
        framework_exclusions=framework_exclusions if framework_exclusions else None
    )


def get_framework_defaults() -> RegistryConfig:
    """Get the default framework registry configuration.

    This function returns the complete framework registry without any
    application modifications. Useful for inspecting what components
    the framework provides or for manual registry merging.

    Returns:
        Complete framework RegistryConfig with all core components

    Examples:
        Inspect framework components::

            >>> framework = get_framework_defaults()
            >>> print(f"Framework provides {len(framework.capabilities)} capabilities")
            >>> for cap in framework.capabilities:
            ...     print(f"  - {cap.name}: {cap.description}")

        Manual merging (advanced)::

            >>> framework = get_framework_defaults()
            >>> my_config = RegistryConfig(
            ...     core_nodes=framework.core_nodes,
            ...     capabilities=framework.capabilities + my_capabilities,
            ...     context_classes=framework.context_classes + my_context_classes,
            ...     data_sources=framework.data_sources,
            ...     services=framework.services,
            ...     framework_prompt_providers=framework.framework_prompt_providers,
            ...     initialization_order=framework.initialization_order
            ... )

    .. note::
       Most applications should use :func:`extend_framework_registry` instead
       of manually merging. This function is provided for inspection and
       advanced use cases.

    .. seealso::
       :func:`extend_framework_registry` : Recommended way to extend framework
       :class:`FrameworkRegistryProvider` : The provider that generates this config
    """
    from .registry import FrameworkRegistryProvider
    provider = FrameworkRegistryProvider()
    return provider.get_registry_config()

