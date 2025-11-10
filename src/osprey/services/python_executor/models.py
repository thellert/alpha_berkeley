"""Core Models and State Management for Python Executor Service.

This module provides the foundational data structures, state management classes,
and configuration utilities that support the Python executor service's
LangGraph-based workflow. It implements a clean separation between request/response
models, internal execution state, and configuration management.

The module is organized into several key areas:

**Type Definitions**: Core data structures for execution requests, results, and
metadata tracking. These provide type-safe interfaces for service communication
and ensure consistent data handling across the execution pipeline.

**State Management**: LangGraph-compatible state classes that track execution
progress, approval workflows, and intermediate results throughout the service
execution lifecycle.

**Configuration Utilities**: Factory functions and configuration classes that
integrate with the framework's configuration system to provide execution
mode settings, container endpoints, and security policies.

**Result Structures**: Comprehensive result classes that capture execution
outcomes, performance metrics, file artifacts, and error information in a
structured format suitable for capability integration.

Key Design Principles:
    - **Type Safety**: All public interfaces use Pydantic models or dataclasses
      with comprehensive type annotations for IDE support and runtime validation
    - **LangGraph Integration**: State classes implement TypedDict patterns for
      seamless integration with LangGraph's state management and checkpointing
    - **Exception-Based Architecture**: Configuration functions raise specific
      exceptions rather than returning error states for clear error handling
    - **Immutable Results**: Result structures use frozen dataclasses to prevent
      accidental mutation and ensure data integrity

The module supports both internal service operations and external capability
integration, providing clean abstractions for different usage patterns while
maintaining consistency in data structures and error handling.

.. note::
   This module is designed for internal use by the Python executor service.
   External code should interact through the service interface rather than
   directly manipulating these models.

.. seealso::
   :class:`osprey.services.python_executor.PythonExecutorService` : Main service
   :class:`osprey.services.python_executor.PythonExecutionState` : LangGraph state
   :class:`osprey.services.python_executor.PythonExecutionRequest` : Request model
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from pydantic import BaseModel, Field

from osprey.utils.logger import get_logger

# Import for runtime use
from .exceptions import ContainerConfigurationError

if TYPE_CHECKING:
    from .execution_control import ExecutionControlConfig, ExecutionMode

logger = get_logger("python_services")

# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class NotebookType(Enum):
    """Enumeration of notebook types created during Python execution workflow.

    This enum categorizes the different types of Jupyter notebooks that are
    created throughout the Python execution lifecycle. Each notebook type
    serves a specific purpose in the execution workflow and provides different
    levels of detail for debugging and audit purposes.

    The notebooks are created at key stages to provide comprehensive visibility
    into the execution process, from initial code generation through final
    execution results or failure analysis.

    :cvar CODE_GENERATION_ATTEMPT: Notebook created after code generation but before analysis
    :cvar PRE_EXECUTION: Notebook created after analysis approval but before execution
    :cvar EXECUTION_ATTEMPT: Notebook created during or immediately after code execution
    :cvar FINAL_SUCCESS: Final notebook created after successful execution completion
    :cvar FINAL_FAILURE: Final notebook created after execution failure for debugging

    .. note::
       Each notebook type includes different metadata and context information
       appropriate for its stage in the execution workflow.

    .. seealso::
       :class:`NotebookAttempt` : Tracks individual notebook creation attempts
       :class:`NotebookManager` : Manages notebook creation and lifecycle
    """
    CODE_GENERATION_ATTEMPT = "code_generation_attempt"
    PRE_EXECUTION = "pre_execution"
    EXECUTION_ATTEMPT = "execution_attempt"
    FINAL_SUCCESS = "final_success"
    FINAL_FAILURE = "final_failure"


@dataclass
class NotebookAttempt:
    """Tracks metadata for a single notebook creation attempt during execution workflow.

    This dataclass captures comprehensive information about each notebook created
    during the Python execution process, including its type, creation context,
    file system location, and any associated error information. It provides
    audit trails and debugging support for the execution workflow.

    The class supports serialization for persistence and provides structured
    access to notebook metadata for both internal tracking and external
    reporting purposes.

    :param notebook_type: Type of notebook created (generation, execution, final, etc.)
    :type notebook_type: NotebookType
    :param attempt_number: Sequential attempt number for this execution session
    :type attempt_number: int
    :param stage: Execution stage when notebook was created
    :type stage: str
    :param notebook_path: File system path to the created notebook
    :type notebook_path: Path
    :param notebook_link: URL link for accessing the notebook in Jupyter interface
    :type notebook_link: str
    :param error_context: Optional error information if notebook creation failed
    :type error_context: str, optional
    :param created_at: Timestamp when notebook was created
    :type created_at: str, optional

    .. note::
       The `notebook_link` provides direct access to view the notebook in the
       Jupyter interface, making it easy to inspect execution results.

    .. seealso::
       :class:`NotebookType` : Enumeration of supported notebook types
       :class:`PythonExecutionContext` : Container for execution context and attempts
    """
    notebook_type: NotebookType
    attempt_number: int
    stage: str  # "code_generation", "execution", "final"
    notebook_path: Path
    notebook_link: str
    error_context: str | None = None
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert notebook attempt to dictionary for serialization and storage.

        Transforms the notebook attempt data into a serializable dictionary
        format suitable for JSON storage, logging, or transmission. All Path
        objects are converted to strings and enum values are converted to
        their string representations.

        :return: Dictionary representation with all fields as serializable types
        :rtype: Dict[str, Any]

        Examples:
            Converting attempt to dictionary for logging::

                >>> attempt = NotebookAttempt(
                ...     notebook_type=NotebookType.FINAL_SUCCESS,
                ...     attempt_number=1,
                ...     stage="execution",
                ...     notebook_path=Path("/path/to/notebook.ipynb"),
                ...     notebook_link="http://jupyter/notebooks/notebook.ipynb"
                ... )
                >>> data = attempt.to_dict()
                >>> print(f"Notebook type: {data['notebook_type']}")
                Notebook type: final_success
        """
        return {
            "notebook_type": self.notebook_type.value,
            "attempt_number": self.attempt_number,
            "stage": self.stage,
            "notebook_path": str(self.notebook_path),
            "notebook_link": self.notebook_link,
            "error_context": self.error_context,
            "created_at": self.created_at
        }


@dataclass
class PythonExecutionContext:
    """Execution context container managing file system resources and notebook tracking.

    This class provides a centralized container for managing all file system
    resources, paths, and metadata associated with a Python execution session.
    It tracks the execution folder structure, notebook creation attempts, and
    provides convenient access to execution artifacts.

    The context maintains a flat, simple structure that can be easily serialized
    and passed between different components of the execution pipeline. It serves
    as the primary coordination point for file operations and artifact management.

    :param folder_path: Main execution folder path where all artifacts are stored
    :type folder_path: Path, optional
    :param folder_url: Jupyter-accessible URL for the execution folder
    :type folder_url: str, optional
    :param attempts_folder: Subfolder containing individual execution attempts
    :type attempts_folder: Path, optional
    :param context_file_path: Path to the serialized context file for the execution
    :type context_file_path: Path, optional
    :param notebook_attempts: List of all notebook creation attempts for this execution
    :type notebook_attempts: List[NotebookAttempt]

    .. note::
       The context is typically created by the FileManager during execution
       folder setup and is passed through the execution pipeline to coordinate
       file operations.

    .. seealso::
       :class:`FileManager` : Creates and manages execution contexts
       :class:`NotebookAttempt` : Individual notebook tracking records
    """
    folder_path: Path | None = None
    folder_url: str | None = None
    attempts_folder: Path | None = None
    context_file_path: Path | None = None
    notebook_attempts: list[NotebookAttempt] = field(default_factory=list)

    @property
    def is_initialized(self) -> bool:
        """Check if execution folder has been properly initialized.

        Determines whether the execution context has been set up with a valid
        folder path, indicating that the file system resources are ready for
        use by the execution pipeline.

        :return: True if folder_path is set, False otherwise
        :rtype: bool

        Examples:
            Checking context initialization before use::

                >>> context = PythonExecutionContext()
                >>> print(f"Ready: {context.is_initialized}")
                Ready: False
                >>> context.folder_path = Path("/tmp/execution")
                >>> print(f"Ready: {context.is_initialized}")
                Ready: True
        """
        return self.folder_path is not None

    def add_notebook_attempt(self, attempt: NotebookAttempt) -> None:
        """Add a notebook creation attempt to the tracking list.

        Records a new notebook attempt in the execution context, maintaining
        a complete audit trail of all notebooks created during the execution
        session. This supports debugging and provides visibility into the
        execution workflow.

        :param attempt: Notebook attempt metadata to add to tracking
        :type attempt: NotebookAttempt

        Examples:
            Adding a notebook attempt to context::

                >>> context = PythonExecutionContext()
                >>> attempt = NotebookAttempt(
                ...     notebook_type=NotebookType.FINAL_SUCCESS,
                ...     attempt_number=1,
                ...     stage="execution",
                ...     notebook_path=Path("/path/to/notebook.ipynb"),
                ...     notebook_link="http://jupyter/notebooks/notebook.ipynb"
                ... )
                >>> context.add_notebook_attempt(attempt)
                >>> print(f"Total attempts: {len(context.notebook_attempts)}")
                Total attempts: 1
        """
        self.notebook_attempts.append(attempt)

    def get_next_attempt_number(self) -> int:
        """Get the next sequential attempt number for notebook naming.

        Calculates the next attempt number based on the current number of
        tracked notebook attempts. This ensures consistent, sequential
        numbering of notebooks throughout the execution session.

        :return: Next attempt number (1-based indexing)
        :rtype: int

        Examples:
            Getting attempt number for new notebook::

                >>> context = PythonExecutionContext()
                >>> print(f"First attempt: {context.get_next_attempt_number()}")
                First attempt: 1
                >>> # After adding one attempt...
                >>> print(f"Next attempt: {context.get_next_attempt_number()}")
                Next attempt: 2
        """
        return len(self.notebook_attempts) + 1


class PythonExecutionRequest(BaseModel):
    """Type-safe, serializable request model for Python code execution services.

    This Pydantic model defines the complete interface for requesting Python code
    generation and execution through the Python executor service. It encapsulates
    all necessary information for the service to understand the user's intent,
    generate appropriate code, and execute it within the proper security context.

    The request model is designed to be fully serializable and compatible with
    LangGraph's state management system. It separates serializable request data
    from configuration objects, which are accessed through LangGraph's configurable
    system for proper dependency injection and configuration management.

    The model supports both fresh execution requests and continuation of existing
    execution sessions, with optional pre-approved code for bypassing the
    generation and analysis phases when code has already been validated.

    :param user_query: The original user query or task description that initiated this request
    :type user_query: str
    :param task_objective: Clear, specific description of what needs to be accomplished
    :type task_objective: str
    :param expected_results: Dictionary describing expected outputs, success criteria, or result structure
    :type expected_results: Dict[str, Any]
    :param capability_prompts: Additional prompts or guidance for code generation context
    :type capability_prompts: List[str]
    :param execution_folder_name: Base name for the execution folder to be created
    :type execution_folder_name: str
    :param retries: Maximum number of retry attempts for code generation and execution
    :type retries: int
    :param capability_context_data: Context data from other capabilities for cross-capability integration
    :type capability_context_data: Dict[str, Any], optional
    :param approved_code: Pre-validated code to execute directly, bypassing generation
    :type approved_code: str, optional
    :param existing_execution_folder: Path to existing execution folder for session continuation
    :type existing_execution_folder: str, optional
    :param session_context: Session metadata including user and chat identifiers
    :type session_context: Dict[str, Any], optional

    .. note::
       The request model uses Pydantic for validation and serialization. All
       Path objects are represented as strings to ensure JSON compatibility.

    .. warning::
       When providing `approved_code`, ensure it has been properly validated
       through appropriate security and policy checks before submission.

    .. seealso::
       :class:`PythonExecutorService` : Service that processes these requests
       :class:`PythonExecutionState` : LangGraph state containing request data
       :class:`PythonServiceResult` : Structured response from successful execution

    Examples:
        Basic execution request for data analysis::

            >>> request = PythonExecutionRequest(
            ...     user_query="Analyze the sensor data trends",
            ...     task_objective="Calculate statistical trends and create visualization",
            ...     expected_results={"statistics": "dict", "plot": "matplotlib figure"},
            ...     execution_folder_name="sensor_analysis"
            ... )

        Request with pre-approved code::

            >>> request = PythonExecutionRequest(
            ...     user_query="Execute validated analysis code",
            ...     task_objective="Run pre-approved statistical analysis",
            ...     execution_folder_name="approved_analysis",
            ...     approved_code="import pandas as pd\ndf.describe()"
            ... )

        Request with capability context integration::

            >>> request = PythonExecutionRequest(
            ...     user_query="Process archiver data",
            ...     task_objective="Analyze retrieved EPICS data",
            ...     execution_folder_name="epics_analysis",
            ...     capability_context_data={
            ...         "archiver_data": {"pv_data": [...], "timestamps": [...]}
            ...     }
            ... )

    """
    user_query: str = Field(..., description="The user's query or task description")
    task_objective: str = Field(..., description="Clear description of what needs to be accomplished")
    expected_results: dict[str, Any] = Field(default_factory=dict, description="Expected results or success criteria")
    capability_prompts: list[str] = Field(default_factory=list, description="Additional prompts for capability guidance")
    execution_folder_name: str = Field(..., description="Name of the execution folder to create")
    retries: int = Field(default=3, description="Maximum number of retry attempts")
    # Optional fields
    capability_context_data: dict[str, Any] | None = Field(None, description="Capability context data from capability_context_data state field")
    approved_code: str | None = Field(None, description="Pre-approved code to execute directly")
    existing_execution_folder: str | None = Field(None, description="Path as string, not Path object")
    session_context: dict[str, Any] | None = Field(None, description="Session info including chat_id, user_id for OpenWebUI links")


@dataclass
class PythonExecutionSuccess:
    """Comprehensive result data from successful Python code execution.

    This dataclass encapsulates all outputs and artifacts produced by successful
    Python code execution, including computational results, execution metadata,
    performance metrics, and file system artifacts. It serves as the primary
    payload within PythonServiceResult and provides capabilities with structured
    access to execution outcomes.

    The class captures both the logical results (computed data) and physical
    artifacts (notebooks, figures) produced during execution, along with
    execution metadata for monitoring and debugging purposes.

    :param results: Dictionary containing the main computational results from code execution
    :type results: Dict[str, Any]
    :param stdout: Complete stdout output captured during code execution
    :type stdout: str
    :param execution_time: Total execution time in seconds
    :type execution_time: float
    :param folder_path: File system path to the execution folder containing all artifacts
    :type folder_path: Path
    :param notebook_path: Path to the final notebook containing executed code and results
    :type notebook_path: Path
    :param notebook_link: Jupyter-accessible URL for viewing the execution notebook
    :type notebook_link: str
    :param figure_paths: List of paths to any figures or plots generated during execution
    :type figure_paths: List[Path]

    .. note::
       The `results` dictionary contains the primary computational outputs that
       other capabilities can use for further processing or analysis.

    .. seealso::
       :class:`PythonServiceResult` : Container class that includes this execution data
       :class:`PythonExecutionEngineResult` : Internal engine result structure
    """
    results: dict[str, Any]
    stdout: str
    execution_time: float
    folder_path: Path
    notebook_path: Path
    notebook_link: str  # Proper URL generated by FileManager
    figure_paths: list[Path] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert execution success data to dictionary for serialization and compatibility.

        Transforms the execution result into a dictionary format suitable for
        JSON serialization, logging, or integration with systems that expect
        dictionary-based data structures. All Path objects are converted to
        strings for compatibility.

        :return: Dictionary representation with standardized field names
        :rtype: Dict[str, Any]

        .. note::
           This method provides backward compatibility with existing code that
           expects dictionary-based execution results.

        Examples:
            Converting execution results for logging::

                >>> success = PythonExecutionSuccess(
                ...     results={"mean": 42.0, "count": 100},
                ...     stdout="Calculation completed successfully",
                ...     execution_time=2.5,
                ...     folder_path=Path("/tmp/execution"),
                ...     notebook_path=Path("/tmp/execution/notebook.ipynb"),
                ...     notebook_link="http://jupyter/notebooks/notebook.ipynb"
                ... )
                >>> data = success.to_dict()
                >>> print(f"Execution took {data['execution_time_seconds']} seconds")
                Execution took 2.5 seconds
        """
        return {
            "results": self.results,
            "execution_stdout": self.stdout,
            "execution_time_seconds": self.execution_time,
            "execution_folder": str(self.folder_path),
            "notebook_path": str(self.notebook_path),
            "notebook_link": self.notebook_link,
            "figure_paths": [str(p) for p in self.figure_paths],
            "figure_count": len(self.figure_paths)
        }


@dataclass
class PythonExecutionEngineResult:
    """Internal result structure for the execution engine (not for external use)."""
    success: bool
    stdout: str
    result_dict: dict[str, Any] | None = None
    error_message: str | None = None
    execution_time_seconds: float | None = None
    captured_figures: list[Path] = field(default_factory=list)

    def __post_init__(self):
        if self.captured_figures is None:
            self.captured_figures = []


# =============================================================================
# SERVICE RESULT STRUCTURES
# =============================================================================

@dataclasses.dataclass(frozen=True, slots=True)
class PythonServiceResult:
    """
    Structured, type-safe result from Python executor service.

    This eliminates the need for validation and error checking in capabilities.
    The service guarantees this structure is always returned on success.
    On failure, the service raises appropriate exceptions.

    Following LangGraph patterns with frozen dataclasses for immutable results.
    """
    execution_result: PythonExecutionSuccess
    generated_code: str

    # Optional metadata
    generation_attempt: int = 1
    analysis_warnings: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Result of static code analysis."""
    passed: bool
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    severity: str = "info"  # info, warning, error
    has_epics_writes: bool = False
    has_epics_reads: bool = False
    recommended_execution_mode: ExecutionMode = None  # Will be set to READ_ONLY by default in constructor
    needs_approval: bool = False           # Whether code needs human approval before execution
    approval_reasoning: str | None = None  # Detailed explanation of why approval is required
    execution_mode_config: dict[str, Any] | None = None

    def __post_init__(self):
        # Import here to avoid circular imports
        if self.recommended_execution_mode is None:
            from .execution_control import ExecutionMode
            self.recommended_execution_mode = ExecutionMode.READ_ONLY


# =============================================================================
# CONFIGURATION UTILITIES
# =============================================================================

@dataclass
class ExecutionModeConfig:
    """Simple execution mode configuration."""
    mode_name: str
    kernel_name: str
    allows_writes: bool
    requires_approval: bool
    description: str
    environment: dict[str, str]
    epics_gateway: dict[str, Any] | None = None


@dataclass
class ContainerEndpointConfig:
    """Container endpoint configuration."""
    host: str
    port: int
    kernel_name: str
    use_https: bool = False

    @property
    def base_url(self) -> str:
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"


def get_execution_control_config_from_configurable(configurable: dict[str, Any]) -> ExecutionControlConfig:
    """Get execution control configuration from LangGraph configurable - raises exceptions on failure.

    This provides a consistent way to access EPICS execution control settings from the configurable
    that is passed to the Python executor service, ensuring security-critical settings like
    epics_writes_enabled are accessed consistently.

    Args:
        configurable: The LangGraph configurable dictionary

    Returns:
        ExecutionControlConfig: Execution control configuration

    Raises:
        ContainerConfigurationError: If configuration is missing or invalid
    """
    from .execution_control import ExecutionControlConfig

    try:
        # Get agent control defaults from configurable (built by ConfigAdapter)
        agent_control_defaults = configurable.get('agent_control_defaults', {})

        if not agent_control_defaults:
            raise ContainerConfigurationError(
                "No agent_control_defaults found in configurable",
                technical_details={"configurable_keys": list(configurable.keys())}
            )

        # Extract EPICS execution control settings
        epics_writes_enabled = agent_control_defaults.get('epics_writes_enabled', False)

        # Create execution control config
        config = ExecutionControlConfig(
            epics_writes_enabled=epics_writes_enabled
        )

        return config

    except ContainerConfigurationError:
        # Re-raise configuration errors
        raise
    except Exception as e:
        raise ContainerConfigurationError(
            f"Failed to parse execution control configuration: {str(e)}",
            technical_details={"original_error": str(e)}
        ) from e


def get_execution_mode_config_from_configurable(configurable: dict[str, Any], mode_name: str) -> ExecutionModeConfig:
    """Create execution mode config from LangGraph configurable - raises exceptions on failure"""
    try:
        # Navigate to framework execution modes in configurable
        # This should be available through the service configs or similar structure
        execution_config = configurable.get('execution', {})
        modes_config = execution_config.get('modes', {})

        mode_config = modes_config.get(mode_name)
        if not mode_config:
            # Try fallback path structure that might be in configurable
            mode_config = configurable.get('execution_modes', {}).get(mode_name)

        if not mode_config:
            raise ContainerConfigurationError(
                f"Execution mode '{mode_name}' not found in configuration",
                technical_details={"mode_name": mode_name, "available_modes": list(modes_config.keys())}
            )

        # Get EPICS gateway configuration if specified
        gateway_config = None
        if mode_config.get('gateway'):
            gateway_name = mode_config['gateway']
            epics_config = execution_config.get('epics', {})
            gateways_config = epics_config.get('gateways', {})
            gateway_config = gateways_config.get(gateway_name)

        # Create configuration with defaults
        config = ExecutionModeConfig(
            mode_name=mode_name,
            kernel_name=mode_config['kernel_name'],
            allows_writes=mode_config.get('allows_writes', False),
            requires_approval=mode_config.get('requires_approval', False),
            description=mode_config.get('description', ''),
            environment=mode_config.get('environment', {}),
            epics_gateway=gateway_config
        )

        # Add EPICS environment variables if gateway is specified
        if gateway_config:
            epics_env = {
                'EPICS_CA_ADDR_LIST': gateway_config['address'],
                'EPICS_CA_SERVER_PORT': str(gateway_config['port']),
                'EPICS_CA_AUTO_ADDR_LIST': 'NO'
            }
            config.environment.update(epics_env)

        return config

    except ContainerConfigurationError:
        raise
    except Exception as e:
        raise ContainerConfigurationError(
            f"Failed to parse execution mode configuration: {str(e)}",
            technical_details={"mode_name": mode_name, "error": str(e)}
        ) from e





def get_container_endpoint_config_from_configurable(configurable: dict[str, Any], execution_mode: str) -> ContainerEndpointConfig:
    """Create container endpoint config from LangGraph configurable - raises exceptions on failure"""
    try:
        # Get execution mode config first
        mode_config = get_execution_mode_config_from_configurable(configurable, execution_mode)

        # Find the container that supports this execution mode
        service_configs = configurable.get("service_configs", {})
        jupyter_config = service_configs.get("jupyter", {})
        containers_config = jupyter_config.get("containers", {})

        target_container = None
        for _container_key, container_config in containers_config.items():
            execution_modes = container_config.get("execution_modes", [])
            if execution_mode in execution_modes:
                target_container = container_config
                break

        if not target_container:
            raise ContainerConfigurationError(
                f"No Jupyter container found supporting execution mode '{execution_mode}'",
                technical_details={
                    "execution_mode": execution_mode,
                    "available_containers": list(containers_config.keys())
                }
            )

        # Extract container connection details
        hostname = target_container.get("hostname")
        port = target_container.get("port_host")

        if not hostname or not port:
            raise ContainerConfigurationError(
                f"Invalid container configuration for execution mode '{execution_mode}': missing hostname or port",
                technical_details={
                    "execution_mode": execution_mode,
                    "container_config": target_container
                }
            )

        endpoint_config = ContainerEndpointConfig(
            host=hostname,
            port=port,
            kernel_name=mode_config.kernel_name,
            use_https=False
        )

        return endpoint_config

    except ContainerConfigurationError:
        # Re-raise configuration errors
        raise
    except Exception as e:
        raise ContainerConfigurationError(
            f"Failed to create container endpoint config: {str(e)}",
            technical_details={
                "execution_mode": execution_mode,
                "original_error": str(e)
            }
        ) from e





# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class PythonExecutionState(TypedDict):
    """LangGraph state for Python executor service.

    This state is used internally by the service and includes both the
    original request and execution tracking fields.

    CRITICAL: The 'request' field preserves the existing interface, allowing
    service nodes to access all original request data via state.request.field_name

    NOTE: capability_context_data is extracted to top level for ContextManager compatibility
    """
    # Original request (preserves interface)
    request: PythonExecutionRequest

    # Capability context data (extracted from request for ContextManager compatibility)
    capability_context_data: dict[str, dict[str, dict[str, Any]]] | None

    # Execution tracking
    generation_attempt: int
    error_chain: list[str]
    current_stage: str  # "generation", "analysis", "approval", "execution", "complete"

    # Approval state (improved pattern)
    requires_approval: bool | None
    approval_interrupt_data: dict[str, Any] | None  # LangGraph interrupt data with all approval details
    approval_result: dict[str, Any] | None   # Response from interrupt
    approved: bool | None                    # Final approval status

    # Runtime data
    generated_code: str | None
    analysis_result: Any | None
    analysis_failed: bool | None
    execution_failed: bool | None
    execution_result: Any | None
    execution_folder: Any | None

    # Control flags
    is_successful: bool
    is_failed: bool
    failure_reason: str | None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_result_structure(code: str) -> bool:
    """
    Validate that generated code has proper result structure.

    Args:
        code: Python code to validate

    Returns:
        bool: True if structure is valid
    """
    # Basic validation - check if 'results' variable is assigned
    logger.warning("Results validation currently just a placeholder")
    return 'results' in code


