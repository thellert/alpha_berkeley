"""
Configuration System

Professional configuration system that works seamlessly both inside and outside 
LangGraph contexts. Features:
- YAML loading, merging, environment resolution, robust file handling
- LangGraph integration, pre-computed structures, context awareness
- Single source of truth with automatic context detection

Clean, modern configuration architecture supporting both standalone and graph execution.
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

try:
    from langgraph.config import get_config
except (RuntimeError, ImportError):
    get_config = None

logger = logging.getLogger(__name__)

# Enable environment-based configuration for deployment flexibility
try:
    from dotenv import load_dotenv
    # Use consistent project structure for reliable environment discovery
    env_file = Path(__file__).parent.parent.parent / ".env"  
    if env_file.exists():
        load_dotenv(env_file)
        logger.debug(f"Loaded environment variables from {env_file}")
    else:
        # Support deployment scenarios where .env is in working directory
        load_dotenv()
        logger.debug("Attempted to load .env file from current directory")
except ImportError:
    logger.warning("python-dotenv not available, skipping .env file loading")


class ConfigBuilder:
    """
    Configuration builder with clean, modern architecture.
    
    Features:
    - YAML loading with validation and error handling
    - Recursive config merging with special handling
    - Environment variable resolution
    - Convention-based application loading
    - Pre-computed nested dictionaries for performance
    - Explicit fail-fast behavior for required configurations
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
            config_path: Path to the config.yml file. If None, uses default path.
        """
        if config_path is None:
            # Use predictable path resolution for consistent behavior across environments
            current_dir = Path(__file__).parent
            # Standard project layout: config.yml at project root (two levels up)
            config_path = current_dir.parent.parent / "config.yml"
        
        self.config_path = Path(config_path)
        self.raw_config = self._load_config()
        
        # Pre-compute nested structures for efficient runtime access
        self.configurable = self._build_configurable()
    
    def _find_config_file(self, config_path: str) -> Path:
        """Find configuration file for import processing."""
        path = Path(config_path)
        
        if not path.is_absolute():
            path = self.config_path.parent / path
        
        if path.exists():
            logger.debug(f"Found config file at: {path}")
            return path
        
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
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
    
    def _merge_configs(self, base_config: Dict[str, Any], overlay_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries."""
        merged = base_config.copy()
        
        for key, value in overlay_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            elif key == 'deployed_services':
                # Preserve service deployment configuration from base when overlay is empty
                if value and (isinstance(value, list) and len(value) > 0):
                    merged[key] = value
                elif not value and merged.get(key):
                    pass  # Maintain existing service configuration
                else:
                    merged[key] = value
            else:
                merged[key] = value
        
        return merged
    
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
        """Load and process the complete configuration."""
        # Start with application-specific configuration
        config = self._load_yaml_file(self.config_path)
               
        # Enable framework configuration inheritance through imports
        if 'import' in config:
            framework_path = self._find_config_file(config['import'])
            framework_config = self._load_yaml_file(framework_path)
            
            # Layer application config over framework defaults for customization
            config = self._merge_configs(framework_config, config)
            
            # Clean up processed directive to avoid confusion
            config.pop('import', None)
            logger.info(f"Imported framework configuration from {framework_path}")
        
        # Load application configurations using convention-based patterns
        if 'applications' in config and isinstance(config['applications'], list):
            for app_name in config['applications']:
                conventional_app_path = f"src/applications/{app_name}/config.yml"
                
                try:
                    app_path = self._find_config_file(conventional_app_path)
                    app_config = self._load_yaml_file(app_path)
                    
                    # Namespace application config to prevent conflicts with framework settings
                    wrapped_app_config = {
                        "applications": {
                            app_name: app_config
                        }
                    }
                    config = self._merge_configs(config, wrapped_app_config)
                    logger.info(f"Loaded application configuration via convention: '{app_name}' from {app_path}")
                    
                except FileNotFoundError:
                    logger.debug(f"No configuration file found for application '{app_name}' at {conventional_app_path} (optional)")
        
        # Apply environment variable substitution after configuration assembly
        # Ensures consistent environment resolution across all config sources
        config = self._resolve_env_vars(config)
        
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
            "framework": self.get('framework', {}),
            
            # ===== LOGGING CONFIGURATION =====
            "logging": self.get('logging', {}),
            
            # ===== SIMPLE FLAT CONFIGS =====
            "development": self.get('development', {}),
            "epics_config": self.get('framework.execution.epics', {}),
            "approval_config": self.get('approval', {}),
            
            # ===== PROJECT CONFIGURATION ===== 
            # Essential for absolute path resolution across deployment environments
            "project_root": self.get('project_root'),
            
            # ===== RUNTIME CONTEXT =====
            "langfuse_enabled": self.get('langfuse.enabled', False),
            
            # ===== APPLICATION CONTEXT =====
            "applications": self.get('applications', []),
            "current_application": self._get_current_application(),
        }
        
        return configurable
    
    def _build_model_configs(self) -> Dict[str, Any]:
        """Build nested model config structure."""
        configs = {}
        
        # Framework models
        framework_models = self.get('framework.models', {})
        if framework_models:
            configs["framework"] = {}
            for model_name, model_config in framework_models.items():
                configs["framework"][model_name] = model_config
        
        # Application models
        applications = self.get('applications', [])
        
        if isinstance(applications, dict):
            for app_name in applications.keys():
                app_models = self.get(f'applications.{app_name}.models', {})
                if app_models:
                    configs[app_name] = {}
                    for service_name, service_config in app_models.items():
                        if isinstance(service_config, dict) and any(
                            key in service_config for key in ['provider', 'model_id', 'retries']
                        ):
                            configs[app_name][service_name] = service_config
                        else:
                            configs[app_name][service_name] = service_config
        
        return configs
    
    def _build_provider_configs(self) -> Dict[str, Any]:
        """Build provider configs."""
        return self.get('api.providers', {})
    
    def _build_service_configs(self) -> Dict[str, Any]:
        """Build service configs."""
        services = {
            "framework": self.get('framework.services', {}),
            "applications": {}
        }
        
        applications = self.get('applications', [])
        if isinstance(applications, dict):
            for app_name in applications.keys():
                app_services = self.get(f'applications.{app_name}.services', {})
                if app_services:
                    services["applications"][app_name] = app_services
        
        return services
    
    def _build_execution_limits(self) -> Dict[str, Any]:
        """Build execution limits"""
        
        return {
            "graph_recursion_limit": self._require_config('execution_control.limits.graph_recursion_limit', 100),
            "max_reclassifications": self._require_config('execution_control.limits.max_reclassifications', 1),
            "max_planning_attempts": self._require_config('execution_control.limits.max_planning_attempts', 2),
            "max_step_retries": self._require_config('execution_control.limits.max_step_retries', 0),
            "max_execution_time_seconds": self._require_config('execution_control.limits.max_execution_time_seconds', 300),
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

# Global configuration instance
_config: Optional[ConfigBuilder] = None
_global_configurable: Optional[Dict[str, Any]] = None


def _get_config() -> ConfigBuilder:
    """Get the global configuration instance (singleton pattern)."""
    global _config, _global_configurable
    
    if _config is None:
        # Check for environment variable override
        config_file = os.environ.get('CONFIG_FILE')
        if config_file:
            _config = ConfigBuilder(config_file)
        else:
            _config = ConfigBuilder()
        
        # Cache configurable for efficient non-LangGraph contexts
        _global_configurable = _config.configurable.copy()
        
        logger.info("Initialized configuration system")
    
    return _config


def _get_configurable() -> Dict[str, Any]:
    """Get configurable dict with automatic context detection."""
    try:
        # Prefer LangGraph context for runtime-injected configuration
        if get_config:
            config = get_config()
            return config.get("configurable", {})
        else:
            raise ImportError("LangGraph not available")
    except (RuntimeError, ImportError):
        # Use cached global configurable for standalone execution
        if _global_configurable is None:
            _get_config()
        return _global_configurable


# =============================================================================
# CONTEXT-AWARE UTILITY FUNCTIONS
# =============================================================================

def get_model_config(app_or_framework: str, service: str = None, model_type: str = None) -> Dict[str, Any]:
    """
    Get model configuration with automatic context detection.
    
    Works both inside and outside LangGraph contexts.
    
    Args:
        app_or_framework: Application name or 'framework' for framework models
        service: Service name or model name for framework models
        model_type: Model type for nested services (optional)
        
    Returns:
        Dictionary with model configuration
    """
    configurable = _get_configurable()
    model_configs = configurable.get("model_configs", {})
    
    # Handle framework models
    if app_or_framework == "framework":
        framework_models = model_configs.get("framework", {})
        return framework_models.get(service, {})
    
    # Handle application models
    app_models = model_configs.get(app_or_framework, {})
    if service and model_type:
        service_models = app_models.get(service, {})
        return service_models.get(model_type, {})
    elif service:
        return app_models.get(service, {})
    else:
        return {}


def get_provider_config(provider_name: str) -> Dict[str, Any]:
    """Get API provider configuration with automatic context detection."""
    configurable = _get_configurable()
    provider_configs = configurable.get("provider_configs", {})
    return provider_configs.get(provider_name, {})


def get_framework_service_config(service_name: str) -> Dict[str, Any]:
    """Get framework service configuration with automatic context detection."""
    configurable = _get_configurable()
    service_configs = configurable.get("service_configs", {})
    framework_services = service_configs.get("framework", {})
    return framework_services.get(service_name, {})


def get_application_service_config(app_name: str, service_name: str) -> Dict[str, Any]:
    """Get application service configuration with automatic context detection."""
    configurable = _get_configurable()
    service_configs = configurable.get("service_configs", {})
    app_services = service_configs.get("applications", {}).get(app_name, {})
    return app_services.get(service_name, {})


def get_logging_color(capability_name: str) -> str:
    """Get capability color with automatic context detection."""
    configurable = _get_configurable()
    logging_colors = configurable.get("logging_colors", {})
    return logging_colors.get(capability_name, "white")


def get_pipeline_config(app_name: str = None) -> Dict[str, Any]:
    """Get pipeline configuration with automatic context detection."""
    configurable = _get_configurable()
    
    if app_name is None:
        app_name = configurable.get("current_application")
    
    if app_name:
        # Try to get from raw config since pipeline configs aren't pre-computed
        config = _get_config()
        app_path = f"applications.{app_name}.pipeline"
        app_config = config.get(app_path, {})
        
        if app_config:
            return app_config
    
    # Fall back to framework pipeline config
    framework = configurable.get("framework", {})
    return framework.get("pipeline", {})


def get_langfuse_enabled() -> bool:
    """Get Langfuse configuration with automatic context detection."""
    configurable = _get_configurable()
    return configurable.get("langfuse_enabled", False)


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


def get_current_application() -> Optional[str]:
    """Get current application with automatic context detection."""
    configurable = _get_configurable()
    return configurable.get("current_application")


def get_agent_dir(sub_dir: str) -> str:
    """
    Get the target directory path within the agent data directory using absolute paths.
    
    Args:
        sub_dir: Subdirectory name (e.g., 'user_memory_dir', 'execution_plans_dir')
        
    Returns:
        Absolute path to the target directory
    """
    config = _get_config()
    
    # Get project root and file paths configuration
    project_root = config.get("project_root")
    file_paths = config.get("file_paths", {})
    agent_data_dir = file_paths.get("agent_data_dir", "_agent_data")
    
    # Get the specific subdirectory path, fallback to the sub_dir name itself
    sub_dir_path = file_paths.get(sub_dir, sub_dir)
    
    # Construct absolute path with explicit validation
    
    if project_root:
        project_root_path = Path(project_root)
        
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

def get_config_value(path: str, default: Any = None) -> Any:
    """
    Get a specific configuration value by dot-separated path.
    
    This function provides context-aware access to configuration values,
    working both inside and outside LangGraph execution contexts.
    
    Args:
        path: Dot-separated configuration path (e.g., "execution.timeout")
        default: Default value to return if path is not found
        
    Returns:
        The configuration value at the specified path, or default if not found
        
    Raises:
        ValueError: If path is empty or None
        
    Examples:
        >>> timeout = get_config_value("execution.timeout", 30)
        >>> debug_mode = get_config_value("development.debug", False)
    """
    if not path:
        raise ValueError("Configuration path cannot be empty or None")
    
    configurable = _get_configurable()
    
    # Navigate through dot-separated path
    keys = path.split('.')
    value = configurable
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def get_full_configuration() -> Dict[str, Any]:
    """
    Get the complete configuration dictionary.
    
    This function provides access to the entire configurable dictionary,
    working both inside and outside LangGraph execution contexts.
    
    Returns:
        Complete configuration dictionary with all configurable values
        
    Examples:
        >>> config = get_full_configuration()
        >>> user_id = config.get("user_id")
        >>> models = config.get("model_configs", {})
    """
    return _get_configurable()

# Initialize the global configuration on import
_get_config() 