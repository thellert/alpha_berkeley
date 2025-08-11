"""
Component Logger Framework

Provides colored logging for framework and application components with:
- Unified API for all components (capabilities, infrastructure, pipelines)
- Rich terminal output with component-specific colors
- Explicit source identification (framework vs application)
- Graceful fallbacks when configuration is unavailable
- Simple, clear interface

Usage:
    # Framework components
    logger = get_logger("framework", "orchestrator")
    logger.key_info("Starting orchestration")
    
    # Application components
    logger = get_logger("my_app", "data_processor")
    logger.info("Processing data")
    logger.debug("Detailed trace")
    logger.success("Operation completed")
    logger.warning("Something to note")
    logger.error("Something went wrong")
    logger.timing("Execution took 2.5 seconds")
    logger.approval("Waiting for user approval")
"""

import logging
import os
from rich.logging import RichHandler
from rich.console import Console
from typing import Optional, Dict, Any, Union

from configs.config import get_config_value


class ComponentLogger:
    """
    Rich-formatted logger for framework and application components with color coding and message hierarchy.
    
    Message Types:
    - key_info: Important operational information
    - info: Normal operational messages
    - debug: Detailed tracing information
    - warning: Warning messages
    - error: Error messages
    - success: Success messages
    - timing: Timing information
    - approval: Approval messages
    - resume: Resume messages
    """
    
    def __init__(self, base_logger: logging.Logger, component_name: str, color: str = "white"):
        """
        Initialize component logger.
        
        Args:
            base_logger: Underlying Python logger
            component_name: Name of the component (e.g., 'data_analysis', 'router', 'mongo')
            color: Rich color name for this component
        """
        self.base_logger = base_logger
        self.component_name = component_name
        self.color = color
        

    
    def _format_message(self, message: str, style: str, emoji: str = '') -> str:
        """Format message with Rich markup and emoji prefix."""
        try:
            prefix = f"{emoji}{self.component_name.title()}: "
            if style:
                return f"[{style}]{prefix}{message}[/{style}]"
            else:
                return f"{prefix}{message}"
        except Exception:
            # Graceful degradation for environments where Rich markup fails
            return f"{emoji}{self.component_name.title()}: {message}"
    
    def key_info(self, message: str) -> None:
        """Important operational information."""
        style = f"bold {self.color}" if self.color != "white" else "bold white"
        formatted = self._format_message(message, style, '')
        self.base_logger.info(formatted)
    
    def info(self, message: str) -> None:
        """Normal operational information."""
        formatted = self._format_message(message, self.color, '')
        self.base_logger.info(formatted)
    
    def debug(self, message: str) -> None:
        """Detailed tracing information."""
        style = f"dim {self.color}" if self.color != "white" else "dim white"
        formatted = self._format_message(message, style, '🔍 ')
        self.base_logger.debug(formatted)
    
    def warning(self, message: str) -> None:
        """Warning messages."""
        formatted = self._format_message(message, "bold yellow", '⚠️  ')
        self.base_logger.warning(formatted)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Error messages."""
        formatted = self._format_message(message, "bold red", '❌ ')
        self.base_logger.error(formatted, exc_info=exc_info)
    
    def success(self, message: str) -> None:
        """Success messages."""
        formatted = self._format_message(message, "bold green", '✅ ')
        self.base_logger.info(formatted)
    
    def timing(self, message: str) -> None:
        """Timing messages."""
        formatted = self._format_message(message, "bold white", '🕒 ')
        self.base_logger.info(formatted)
    
    def approval(self, message: str) -> None:
        """Approval messages."""
        formatted = self._format_message(message, "bold yellow", '🔍⚠️ ')
        self.base_logger.info(formatted)
    
    def resume(self, message: str) -> None:
        """Resume messages."""
        formatted = self._format_message(message, "bold green", '🔄 ')
        self.base_logger.info(formatted)
    
    # Compatibility methods - delegate to base logger
    def critical(self, message: str, *args, **kwargs) -> None:
        formatted = self._format_message(message, "bold red", '❌ ')
        self.base_logger.critical(formatted, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        formatted = self._format_message(message, "bold red", '❌ ')
        self.base_logger.exception(formatted, *args, **kwargs)
    
    def log(self, level: int, message: str, *args, **kwargs) -> None:
        self.base_logger.log(level, message, *args, **kwargs)
    
    # Properties for compatibility
    @property
    def level(self) -> int:
        return self.base_logger.level
    
    @property
    def name(self) -> str:
        return self.base_logger.name
    
    def setLevel(self, level: int) -> None:
        self.base_logger.setLevel(level)
    
    def isEnabledFor(self, level: int) -> bool:
        return self.base_logger.isEnabledFor(level)




def _setup_rich_logging(level: int = logging.INFO) -> None:
    """Configure Rich logging for the root logger (called once)."""
    root_logger = logging.getLogger()
    
    # Prevent duplicate handler registration for consistent logging behavior
    for handler in root_logger.handlers:
        if isinstance(handler, RichHandler):
            return
    
    # Ensure clean handler state to prevent duplicate log messages
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    root_logger.setLevel(level)
    
    # Load user-configurable display preferences from config
    try:
        # Security-conscious defaults: hide locals to prevent sensitive data exposure
        rich_tracebacks = get_config_value("logging.rich_tracebacks", True)
        show_traceback_locals = get_config_value("logging.show_traceback_locals", False)
        show_full_paths = get_config_value("logging.show_full_paths", False)
        
    except Exception:
        # Secure defaults when configuration system is unavailable
        rich_tracebacks = True
        show_traceback_locals = False
        show_full_paths = False
    
    # Optimize console for containerized and CI/CD environments
    console = Console(
        force_terminal=True,    # Ensure color output in Docker containers and CI systems
        width=120,              # Prevent line wrapping in standard terminal sizes
        color_system="truecolor",  # Enable full color spectrum for component identification
    )
    
    handler = RichHandler(
        console=console,                    # Use our custom console
        rich_tracebacks=rich_tracebacks,    # Configurable rich tracebacks
        markup=True,                        # Enable [bold], [green], etc. in log messages
        show_path=show_full_paths,          # Configurable path display
        show_time=True,                     # Show timestamp
        show_level=True,                    # Show log level
        tracebacks_show_locals=show_traceback_locals,  # Configurable local variables
    )
    
    root_logger.addHandler(handler)
    
    # Reduce third-party library noise to focus on application-specific issues
    for lib in ["httpx", "httpcore", "requests", "urllib3"]:
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(source: str = None, 
               component_name: str = None,
               level: int = logging.INFO,
               *,
               name: str = None,
               color: str = None) -> ComponentLogger:
    """
    Get a colored logger for any component with support for both structured and explicit APIs.
    
    Structured API (recommended):
        source: Source type - either 'framework' or an application name (e.g., 'als_expert')
        component_name: Name of the component (e.g., 'data_analysis', 'router', 'pv_finder')
        level: Logging level
        
    Explicit API (for custom loggers):
        name: Direct logger name (keyword-only)
        color: Direct color specification (keyword-only)
        level: Logging level
        
    Returns:
        ComponentLogger instance
        
    Examples:
        # Structured API (recommended for framework/application components)
        logger = get_logger("framework", "orchestrator")
        logger = get_logger("als_expert", "pv_finder")
        
        # Explicit API (for custom loggers or tests)
        logger = get_logger(name="test_graph_execution", color="white")
        logger = get_logger(name="custom_component", color="blue", level=logging.DEBUG)
    """
    # Initialize logging infrastructure with Rich formatting support
    _setup_rich_logging(level)
    
    # Handle explicit API for custom logger creation (tests, utilities)
    if name is not None:
        # Direct logger creation bypasses convention-based color assignment
        base_logger = logging.getLogger(name)
        actual_color = color or 'white'
        return ComponentLogger(base_logger, name, actual_color)
    
    # Validate structured API parameters for framework/application components
    if source is None or component_name is None:
        raise ValueError("Either provide 'name' (explicit API) or both 'source' and 'component_name' (structured API)")
    
    # Use component name as logger identifier for hierarchical organization
    base_logger = logging.getLogger(component_name)
    
    # Retrieve component-specific color for visual component identification
    try:
        if source == 'framework':
            # Framework components use centralized color scheme
            config_path = f"logging.framework.logging_colors.{component_name}"
        else:
            # Application components: config wraps app configs under applications.{app_name}
            config_path = f"applications.{source}.logging.logging_colors.{component_name}"
        color = get_config_value(config_path)
            
        if not color:
            color = 'white'
        
    except Exception as e:
        # Graceful degradation ensures logging continues even with config issues
        color = 'white'
        print(f"⚠️  WARNING: Failed to load color config for {source}.{component_name}: {e}. Using white as fallback.")
    
    return ComponentLogger(base_logger, component_name, color)