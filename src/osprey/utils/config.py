"""
Configuration System

Professional configuration system that works seamlessly both inside and outside 
LangGraph contexts. Features:
- Single-file YAML loading with environment resolution
- LangGraph integration, pre-computed structures, context awareness
- Single source of truth with automatic context detection
- Flat structure: framework and application settings coexist via unique naming

Clean, modern configuration architecture supporting both standalone and graph execution.
"""

import os
import re
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

try:
    from langgraph.config import get_config
except (RuntimeError, ImportError):
    get_config = None

logger = logging.getLogger(__name__)


class ConfigBuilder:
    """
    Configuration builder with clean, modern architecture.

    Features:
    - Single-file YAML loading with validation and error handling
    - Environment variable resolution
    - Pre-computed nested dictionaries for performance
    - Explicit fail-fast behavior for required configurations
    - Flat structure supporting framework + application settings via unique naming
    """

    # Sentinel object to distinguish between "no default provided" and "default is None"
    _REQUIRED = object()

    def _require_config(self, path: str, default: Any = _REQUIRED) -> Any:
        """
        Get configuration value with explicit control over required vs. optional settings.

        This helper function provides three levels of configuration handling:
        1. Required settings (no default) - fail fast if missing
        2. Optional settings with visibility (default provided) - warn when default is used
        3. Silent optional settings - use standard self.get() for truly optional configs

        Args:
            path: Dot-separated configuration path (e.g., "execution.limits.max_retries")
            default: Default value to use if config is missing. If not provided,
                    the configuration is considered required and will raise ValueError.
                    If provided, logs a warning when the default is used.

        Returns:
            The configuration value, or default if provided and config is missing

        Raises:
            ValueError: If required configuration (no default) is missing or None

        Examples:
            # Required configuration - will fail if missing
            recursion_limit = self._require_config('execution_control.limits.graph_recursion_limit')

            # Optional configuration with explicit default and visibility
            max_retries = self._require_config('execution_control.limits.max_step_retries', 0)

            # Silent optional configuration - use standard get() for noise-free defaults
            debug_mode = self.get('development.debug', False)
        """
        value = self.get(path)

        if value is None:
            if default is self._REQUIRED:
                # No default provided - this is a required configuration
                raise ValueError(
                    f"Missing required configuration: '{path}' must be explicitly set in config.yml. "
                    f"This setting has no default value and must be configured explicitly."
                )
            else:
                # Default provided - use it but warn for visibility
                logger.warning(f"Using default value for '{path}' = {default}. ")
                return default
        return value

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration builder.

        Args:
            config_path: Path to the config.yml file. If None, looks in current directory.

        Raises:
            FileNotFoundError: If config.yml is not found and no path is provided.
        """
        # Load .env file from current working directory
        # This ensures environment variables are available for config resolution
        try:
            from dotenv import load_dotenv
            dotenv_path = Path.cwd() / ".env"
            if dotenv_path.exists():
                load_dotenv(dotenv_path, override=False)  # Don't override existing env vars
                logger.debug(f"Loaded .env file from {dotenv_path}")
            else:
                logger.debug(f"No .env file found at {dotenv_path}")
        except ImportError:
            logger.warning("python-dotenv not available, skipping .env file loading")

        if config_path is None:
            # Check current working directory (where user ran the command)
            cwd_config = Path.cwd() / "config.yml"
            if cwd_config.exists():
                config_path = cwd_config
            else:
                # NO FALLBACK - Fail fast with clear error
                raise FileNotFoundError(
                    f"No config.yml found in current directory: {Path.cwd()}\n\n"
                    f"Please run this command from a project directory containing config.yml,\n"
                    f"or set CONFIG_FILE environment variable to point to your config file.\n\n"
                    f"Example: export CONFIG_FILE=/path/to/your/config.yml"
                )

        self.config_path = Path(config_path)
        self.raw_config = self._load_config()

        # Pre-compute nested structures for efficient runtime access
        self.configurable = self._build_configurable()


    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and validate a YAML configuration file."""
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)

            if config is None:
                logger.warning(f"Configuration file is empty: {file_path}")
                return {}

            if not isinstance(config, dict):
                error_msg = f"Configuration file must contain a dictionary/mapping: {file_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Loaded configuration from {file_path}")
            return config
        except yaml.YAMLError as e:
            error_msg = f"Error parsing YAML configuration: {e}"
            logger.error(error_msg)
            raise yaml.YAMLError(error_msg)


    def _resolve_env_vars(self, data: Any) -> Any:
        """Recursively resolve environment variables in configuration data."""
        if isinstance(data, dict):
            return {key: self._resolve_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        elif isinstance(data, str):
            def replace_env_var(match):
                var_name = match.group(1) or match.group(2)
                env_value = os.environ.get(var_name)
                if env_value is None:
                    logger.warning(f"Environment variable '{var_name}' not found, keeping original value")
                    return match.group(0)
                return env_value

            pattern = r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
            return re.sub(pattern, replace_env_var, data)
        else:
            return data

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from single file."""
        # Load the config file
        config = self._load_yaml_file(self.config_path)

        # Apply environment variable substitution
        config = self._resolve_env_vars(config)

        logger.info(f"Loaded configuration from {self.config_path}")
        return config

    def _build_configurable(self) -> Dict[str, Any]:
        """Build the configurable dictionary with pre-computed nested structures."""
        configurable = {
            # ===== SESSION INFORMATION =====
            "user_id": None,
            "chat_id": None,
            "session_id": None,
            "thread_id": None,
            "session_url": None,

            # ===== EXECUTION LIMITS =====
            "execution_limits": self._build_execution_limits(),

            # ===== AGENT CONTROL DEFAULTS =====
            "agent_control_defaults": self._build_agent_control_defaults(),

            # ===== COMPLEX NESTED STRUCTURES =====
            "model_configs": self._build_model_configs(),
            "provider_configs": self._build_provider_configs(),
            "service_configs": self._build_service_configs(),

            # ===== FRAMEWORK CONFIGURATION =====
            "framework": self.get('osprey', {}),

            # ===== LOGGING CONFIGURATION =====
            "logging": self.get('logging', {}),

            # ===== SIMPLE FLAT CONFIGS =====
            "development": self.get('development', {}),
            "epics_config": self.get('execution.epics', {}),
            "approval_config": self.get('approval', {}),

            # ===== PROJECT CONFIGURATION ===== 
            # Essential for absolute path resolution across deployment environments
            "project_root": self.get('project_root'),

            # ===== APPLICATION CONTEXT =====
            "applications": self.get('applications', []),
            "current_application": self._get_current_application(),
            "registry_path": self.get('registry_path'),
        }

        return configurable

    def _build_model_configs(self) -> Dict[str, Any]:
        """Get model configs from flat structure."""
        return self.get('models', {})

    def _build_provider_configs(self) -> Dict[str, Any]:
        """Build provider configs."""
        return self.get('api.providers', {})

    def _build_service_configs(self) -> Dict[str, Any]:
        """Get service configs from flat structure."""
        return self.get('services', {})

    def _build_execution_limits(self) -> Dict[str, Any]:
        """Build execution limits"""

        return {
            "graph_recursion_limit": self._require_config('execution_control.limits.graph_recursion_limit', 100),
            "max_reclassifications": self._require_config('execution_control.limits.max_reclassifications', 1),
            "max_planning_attempts": self._require_config('execution_control.limits.max_planning_attempts', 2),
            "max_step_retries": self._require_config('execution_control.limits.max_step_retries', 0),
            "max_execution_time_seconds": self._require_config('execution_control.limits.max_execution_time_seconds', 300),
            "max_concurrent_classifications": self._require_config('execution_control.limits.max_concurrent_classifications', 5),
        }

    def _build_agent_control_defaults(self) -> Dict[str, Any]:
        """Build agent control defaults with explicit configuration control."""

        return {
            # Planning control
            "planning_mode_enabled": False,

            # EPICS control
            "epics_writes_enabled": self._require_config('execution_control.epics.writes_enabled', False),

            # Approval control
            "approval_global_mode": self._require_config('approval.global_mode', 'selective'),
            "python_execution_approval_enabled": self._require_config('approval.capabilities.python_execution.enabled', True),
            "python_execution_approval_mode": self._require_config('approval.capabilities.python_execution.mode', 'all_code'),
            "memory_approval_enabled": self._require_config('approval.capabilities.memory.enabled', True),

            # Performance bypass configuration (configurable via YAML)
            "task_extraction_bypass_enabled": self._require_config('execution_control.agent_control.task_extraction_bypass_enabled', False),
            "capability_selection_bypass_enabled": self._require_config('execution_control.agent_control.capability_selection_bypass_enabled', False),

            # Note: Execution limits (max_reclassifications, max_planning_attempts, etc.) 
            # are now centralized in get_execution_limits() utility function
        }

    def _get_current_application(self) -> Optional[str]:
        """Get the current/primary application name."""
        applications = self.get('applications', [])
        if isinstance(applications, dict) and applications:
            return list(applications.keys())[0]
        elif isinstance(applications, list) and applications:
            return applications[0]
        return None

    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation path."""
        keys = path.split('.')
        value = self.raw_config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default


# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

# Global configuration instances
# Default config (singleton pattern for backward compatibility)
_default_config: Optional[ConfigBuilder] = None
_default_configurable: Optional[Dict[str, Any]] = None

# Per-path config cache for explicit config paths
_config_cache: Dict[str, ConfigBuilder] = {}


def _get_config(config_path: Optional[str] = None, set_as_default: bool = False) -> ConfigBuilder:
    """Get configuration instance (singleton pattern with optional explicit path).

    This function supports two modes:
    1. Default singleton: When no config_path provided, uses CONFIG_FILE env var or cwd/config.yml
    2. Explicit path: When config_path provided, caches and returns config for that specific path

    Args:
        config_path: Optional explicit path to configuration file. If provided,
                    this path is used instead of the default singleton behavior.
        set_as_default: If True and config_path is provided, also set this config as the
                       default singleton so future calls without config_path use it.

    Returns:
        ConfigBuilder instance for the specified or default configuration

    Examples:
        >>> # Default singleton behavior (backward compatible)
        >>> config = _get_config()

        >>> # Explicit config path
        >>> config = _get_config("/path/to/config.yml")

        >>> # Explicit path that becomes the default
        >>> config = _get_config("/path/to/config.yml", set_as_default=True)
    """
    global _default_config, _default_configurable

    # If no explicit path, use default singleton behavior
    if config_path is None:
        if _default_config is None:
            # Check for environment variable override
            config_file = os.environ.get('CONFIG_FILE')
            if config_file:
                _default_config = ConfigBuilder(config_file)
            else:
                _default_config = ConfigBuilder()

            # Cache configurable for efficient non-LangGraph contexts
            _default_configurable = _default_config.configurable.copy()

            logger.info("Initialized default configuration system")

        return _default_config

    # For explicit path, cache per path to avoid reloading
    resolved_path = str(Path(config_path).resolve())

    if resolved_path not in _config_cache:
        logger.info(f"Loading configuration from explicit path: {resolved_path}")
        _config_cache[resolved_path] = ConfigBuilder(resolved_path)

    # If requested, also set this as the default config
    if set_as_default and _default_config is None:
        _default_config = _config_cache[resolved_path]
        _default_configurable = _default_config.configurable.copy()
        logger.debug(f"Set explicit config as default: {resolved_path}")

    return _config_cache[resolved_path]


def _get_configurable(config_path: Optional[str] = None, set_as_default: bool = False) -> Dict[str, Any]:
    """Get configurable dict with automatic context detection.

    This function supports both LangGraph execution contexts and standalone execution,
    with optional explicit configuration path support.

    Args:
        config_path: Optional explicit path to configuration file
        set_as_default: If True and config_path is provided, set as default config

    Returns:
        Complete configuration dictionary with all configurable values
    """
    try:
        # Prefer LangGraph context for runtime-injected configuration
        # (only when no explicit config_path is provided)
        if config_path is None and get_config:
            config = get_config()
            return config.get("configurable", {})
        else:
            raise ImportError("LangGraph not available or explicit path provided")
    except (RuntimeError, ImportError):
        # Use cached configurable for standalone execution
        config = _get_config(config_path, set_as_default=set_as_default)

        # For default config, use cached configurable for performance
        if config_path is None:
            global _default_configurable
            if _default_configurable is None:
                _default_configurable = config.configurable.copy()
            return _default_configurable

        # For explicit paths, return configurable directly
        return config.configurable


# =============================================================================
# CONTEXT-AWARE UTILITY FUNCTIONS
# =============================================================================

def get_model_config(app_or_framework: str, service: str = None, model_type: str = None, 
                     config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get model configuration with automatic context detection.

    Works both inside and outside LangGraph contexts.
    Supports both legacy nested format and new flat format.

    Args:
        app_or_framework: Application name or 'framework' for framework models
        service: Service name or model name for framework models
        model_type: Model type for nested services (optional)
        config_path: Optional explicit path to configuration file

    Returns:
        Dictionary with model configuration
    """
    configurable = _get_configurable(config_path)
    model_configs = configurable.get("model_configs", {})

    # Handle framework models
    if app_or_framework == "osprey":
        # Try new flat format first (single-config)
        if service in model_configs:
            return model_configs.get(service, {})
        # Fall back to legacy nested format
        logger.warning(
            f"DEPRECATED: Using legacy nested config format for osprey.models.{service}. "
            f"Please migrate to flat config structure with models at top level."
        )
        framework_models = model_configs.get("osprey", {})
        return framework_models.get(service, {})

    # Handle application models
    # Try flat format first
    if service and not model_type and service in model_configs:
        return model_configs.get(service, {})
    # Try nested application format
    if service and model_type and service in model_configs:
        service_models = model_configs.get(service, {})
        return service_models.get(model_type, {})
    # Fall back to legacy nested format
    logger.warning(
        f"DEPRECATED: Using legacy nested config format for applications.{app_or_framework}.models.{service}. "
        f"Please migrate to flat config structure with models at top level."
    )
    app_models = model_configs.get(app_or_framework, {})
    if service and model_type:
        service_models = app_models.get(service, {})
        return service_models.get(model_type, {})
    elif service:
        return app_models.get(service, {})
    else:
        return {}


def get_provider_config(provider_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get API provider configuration with automatic context detection.

    Args:
        provider_name: Name of the provider (e.g., 'openai', 'anthropic')
        config_path: Optional explicit path to configuration file

    Returns:
        Dictionary with provider configuration
    """
    configurable = _get_configurable(config_path)
    provider_configs = configurable.get("provider_configs", {})
    return provider_configs.get(provider_name, {})


def get_framework_service_config(service_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get framework service configuration with automatic context detection.

    Args:
        service_name: Name of the framework service
        config_path: Optional explicit path to configuration file

    Returns:
        Dictionary with service configuration
    """
    configurable = _get_configurable(config_path)
    service_configs = configurable.get("service_configs", {})
    # Try new flat format first (single-config)
    if service_name in service_configs:
        return service_configs.get(service_name, {})
    # Fall back to legacy nested format
    logger.warning(
        f"DEPRECATED: Using legacy nested config format for osprey.services.{service_name}. "
        f"Please migrate to flat config structure with services at top level."
    )
    framework_services = service_configs.get("osprey", {})
    return framework_services.get(service_name, {})


def get_application_service_config(app_name: str, service_name: str) -> Dict[str, Any]:
    """Get application service configuration with automatic context detection."""
    configurable = _get_configurable()
    service_configs = configurable.get("service_configs", {})
    # Try new flat format first (single-config)
    if service_name in service_configs:
        return service_configs.get(service_name, {})
    # Fall back to legacy nested format
    logger.warning(
        f"DEPRECATED: Using legacy nested config format for applications.{app_name}.services.{service_name}. "
        f"Please migrate to flat config structure with services at top level."
    )
    app_services = service_configs.get("applications", {}).get(app_name, {})
    return app_services.get(service_name, {})


def get_pipeline_config(app_name: str = None) -> Dict[str, Any]:
    """Get pipeline configuration with automatic context detection."""
    configurable = _get_configurable()
    config = _get_config()

    # Try new flat format first (single-config)
    pipeline_config = config.get('pipeline', {})
    if pipeline_config:
        return pipeline_config

    # Fall back to legacy nested format
    if app_name is None:
        app_name = configurable.get("current_application")

    if app_name:
        logger.warning(
            f"DEPRECATED: Using legacy nested config format for applications.{app_name}.pipeline. "
            f"Please migrate to flat config structure with pipeline at top level."
        )
        app_path = f"applications.{app_name}.pipeline"
        app_config = config.get(app_path, {})
        if app_config:
            return app_config

    # Fall back to framework pipeline config
    logger.warning(
        f"DEPRECATED: Using legacy nested config format for osprey.pipeline. "
        f"Please migrate to flat config structure with pipeline at top level."
    )
    framework = configurable.get("osprey", {})
    return framework.get("pipeline", {})


def get_execution_limits() -> Dict[str, Any]:
    """Get execution limits with automatic context detection."""
    configurable = _get_configurable()
    execution_limits = configurable.get("execution_limits")

    if execution_limits is None:
        raise RuntimeError(
            "Execution limits configuration not found. Please ensure 'execution_limits' is properly "
            "configured in your config.yml or environment settings with the following required fields: "
            "max_reclassifications, max_planning_attempts, max_step_retries, max_execution_time_seconds, graph_recursion_limit"
        )

    return execution_limits


def get_agent_control_defaults() -> Dict[str, Any]:
    """Get agent control defaults with automatic context detection."""
    configurable = _get_configurable()
    return configurable.get("agent_control_defaults", {})


def get_session_info() -> Dict[str, Any]:
    """Get session information with automatic context detection."""
    configurable = _get_configurable()
    return {
        "user_id": configurable.get("user_id"),
        "chat_id": configurable.get("chat_id"),
        "session_id": configurable.get("session_id"),
        "thread_id": configurable.get("thread_id"),
        "session_url": configurable.get("session_url"),
    }

def get_interface_context() -> str:
    """
    Get interface context indicating which user interface is being used.

    The interface context determines how responses are formatted and which
    features are available (e.g., figure rendering, notebook links, command buttons).

    Returns:
        str: The interface type, one of:
            - "openwebui": Open WebUI interface with rich rendering capabilities
            - "cli": Command-line interface with text-only output
            - "unknown": Interface type not detected or not set

    Example:
        >>> interface = get_interface_context()
        >>> if interface == "openwebui":
        ...     print("Rich UI features available")

    Note:
        This is set automatically by each interface implementation during initialization.
        The value is used by response generators to provide interface-appropriate
        guidance about figures, notebooks, and executable commands.
    """
    configurable = _get_configurable()
    return configurable.get("interface_context", "unknown")


def get_current_application() -> Optional[str]:
    """Get current application with automatic context detection."""
    configurable = _get_configurable()
    return configurable.get("current_application")


def get_agent_dir(sub_dir: str, host_path: bool = False) -> str:
    """
    Get the target directory path within the agent data directory using absolute paths.

    Args:
        sub_dir: Subdirectory name (e.g., 'user_memory_dir', 'execution_plans_dir')
        host_path: If True, force return of host filesystem path even when running in container

    Returns:
        Absolute path to the target directory
    """
    config = _get_config()

    # Get project root and file paths configuration
    project_root = config.get("project_root")
    main_file_paths = config.get("file_paths", {})
    agent_data_dir = main_file_paths.get("agent_data_dir", "_agent_data")

    # Check both main config and current application config for file paths
    current_app = get_current_application()
    sub_dir_path = None

    # First check main config file_paths
    if sub_dir in main_file_paths:
        sub_dir_path = main_file_paths[sub_dir]
        logger.debug(f"Found {sub_dir} in main file_paths: {sub_dir_path}")

    # Then check current application's file_paths (takes precedence)
    if current_app:
        app_file_paths = config.get(f"applications.{current_app}.file_paths", {})
        if sub_dir in app_file_paths:
            sub_dir_path = app_file_paths[sub_dir]
            logger.debug(f"Found {sub_dir} in {current_app} file_paths: {sub_dir_path}")

    # Fallback to the sub_dir name itself if not found anywhere
    if sub_dir_path is None:
        sub_dir_path = sub_dir
        logger.debug(f"Using fallback path for {sub_dir}: {sub_dir_path}")

    # Construct absolute path with explicit validation

    if project_root:
        project_root_path = Path(project_root)

        # Handle host_path override
        if host_path:
            # Force host path regardless of current environment
            logger.debug(f"Forcing host path resolution for: {sub_dir}")
            path = project_root_path / agent_data_dir / sub_dir_path
        else:
            # Container-aware path resolution
            if not project_root_path.exists():
                # Detect if we're running in a container environment
                container_project_roots = ["/app", "/pipelines", "/jupyter"]
                detected_container_root = None

                for container_root in container_project_roots:
                    container_path = Path(container_root)
                    if container_path.exists() and (container_path / agent_data_dir).exists():
                        detected_container_root = container_path
                        break

                if detected_container_root:
                    # Container environment detected - use container project root
                    logger.debug(f"Container environment detected: using {detected_container_root} instead of {project_root}")
                    path = detected_container_root / agent_data_dir / sub_dir_path
                else:
                    # Not in a known container environment - fall back to relative paths
                    logger.warning(f"Configured project root does not exist: {project_root}")
                    logger.warning("Falling back to relative path resolution")
                    path = Path(agent_data_dir) / sub_dir_path
                    path = path.resolve()
            else:
                # Host environment - use configured project root
                path = project_root_path / agent_data_dir / sub_dir_path
    else:
        # Support development environments without explicit project root configuration
        logger.warning("No project root configured, using relative path for agent data directory")
        path = Path(agent_data_dir) / sub_dir_path
        path = path.resolve()  # Ensure absolute path for consistent behavior

    return str(path)


# =============================================================================
# LANGGRAPH NATIVE ACCESS
# =============================================================================

def get_config_value(path: str, default: Any = None, config_path: Optional[str] = None) -> Any:
    """
    Get a specific configuration value by dot-separated path.

    This function provides context-aware access to configuration values,
    working both inside and outside LangGraph execution contexts. Optionally,
    an explicit configuration file path can be provided.

    Args:
        path: Dot-separated configuration path (e.g., "execution.timeout")
        default: Default value to return if path is not found
        config_path: Optional explicit path to configuration file

    Returns:
        The configuration value at the specified path, or default if not found

    Raises:
        ValueError: If path is empty or None

    Examples:
        >>> timeout = get_config_value("execution.timeout", 30)
        >>> debug_mode = get_config_value("development.debug", False)

        >>> # With explicit config path
        >>> timeout = get_config_value("execution.timeout", 30, "/path/to/config.yml")
    """
    if not path:
        raise ValueError("Configuration path cannot be empty or None")

    configurable = _get_configurable(config_path)

    # Navigate through dot-separated path in configurable dict
    keys = path.split('.')
    value = configurable

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            # Not found in configurable, try raw config as fallback
            config = _get_config(config_path)
            return config.get(path, default)

    return value


def get_classification_config() -> Dict[str, Any]:
    """
    Get classification configuration with sensible defaults.

    Controls parallel LLM-based capability classification to prevent API flooding
    while maintaining reasonable performance during task analysis.

    Returns:
        Dictionary with classification configuration including concurrency limits

    Examples:
        >>> config = get_classification_config()
        >>> max_concurrent = config.get('max_concurrent_classifications', 5)
    """
    configurable = _get_configurable()

    # Get classification concurrency limit from execution_control.limits (consistent with other limits)
    max_concurrent = configurable.get("execution_limits", {}).get("max_concurrent_classifications", 5)

    return {
        "max_concurrent_classifications": max_concurrent
    }


def get_full_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the complete configuration dictionary.

    This function provides access to the entire configurable dictionary,
    working both inside and outside LangGraph execution contexts. Optionally,
    an explicit configuration file path can be provided.

    When an explicit config_path is provided, it is also set as the default
    configuration so that subsequent config access without explicit path will
    use this configuration.

    Args:
        config_path: Optional explicit path to configuration file. If provided,
                    loads configuration from this path and sets it as the default.

    Returns:
        Complete configuration dictionary with all configurable values

    Examples:
        >>> # Default configuration (backward compatible)
        >>> config = get_full_configuration()
        >>> user_id = config.get("user_id")
        >>> models = config.get("model_configs", {})

        >>> # Explicit configuration path (also becomes default)
        >>> config = get_full_configuration("/path/to/my-config.yml")
        >>> models = config.get("model_configs", {})
        >>> # Subsequent calls without path use this config
        >>> other_value = get_config_value("some.setting")
    """
    # If explicit path provided, set as default for future access
    set_as_default = config_path is not None
    return _get_configurable(config_path, set_as_default=set_as_default)

# Initialize the global configuration on import (skip for documentation/tests)
# This provides convenience for module-level logger initialization, but is not
# strictly required since logger.py has graceful fallbacks for missing config.
try:
    if 'sphinx' not in sys.modules and not os.environ.get('SPHINX_BUILD'):
        _get_config()
except FileNotFoundError:
    # Allow deferred initialization if config not available at import time
    # Config will be initialized on first access via the singleton pattern
    pass 