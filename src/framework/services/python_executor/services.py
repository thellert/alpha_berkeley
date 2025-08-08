"""File and Notebook Management Services for Python Executor.

This module provides the service layer for all file system operations and Jupyter
notebook management within the Python executor service. It implements clean
separation of concerns between domain logic and file I/O operations, providing
robust file management with proper error handling and permission management.

The module is organized around two primary service classes:

**FileManager**: Handles execution folder creation, file operations, and context
management. It provides the foundation for organizing execution artifacts and
ensuring proper file system permissions for container-based execution.

**NotebookManager**: Specializes in Jupyter notebook creation and management,
providing comprehensive notebook generation for different stages of the execution
workflow including debugging, audit trails, and result presentation.

Key Features:
    - **Container-Aware Permissions**: Automatic permission management to ensure
      container users can write to execution folders
    - **Structured Organization**: Hierarchical folder organization with date-based
      organization and unique execution identifiers
    - **Jupyter Integration**: Seamless URL generation for accessing notebooks
      and execution artifacts through Jupyter interfaces
    - **Context Management**: Comprehensive context serialization and loading
      for cross-process communication and debugging
    - **Audit Trails**: Complete tracking of execution attempts and artifacts

The services integrate with the framework's configuration system to access
Jupyter container settings and provide appropriate URL generation for external
access to execution artifacts.

.. note::
   These services handle the physical file system operations while the domain
   models in the models module provide the logical structure and data management.

.. seealso::
   :class:`framework.services.python_executor.models.PythonExecutionContext` : Execution context model
   :class:`framework.services.python_executor.models.NotebookAttempt` : Notebook tracking model
   :class:`framework.context.ContextManager` : Framework context management

Examples:
    Creating and managing execution folders::
    
        >>> file_manager = FileManager(configurable)
        >>> context = file_manager.create_execution_folder("data_analysis")
        >>> print(f"Execution folder: {context.folder_path}")
        >>> print(f"Jupyter URL: {context.folder_url}")
        
    Creating notebooks for execution tracking::
    
        >>> notebook_manager = NotebookManager(configurable)
        >>> notebook_path = notebook_manager.create_attempt_notebook(
        ...     context=execution_context,
        ...     code="import pandas as pd\ndf.describe()",
        ...     stage="execution"
        ... )
        >>> print(f"Notebook created: {notebook_path}")
"""

import json
import uuid
import nbformat
import os
from pathlib import Path
from datetime import datetime
import textwrap
from typing import Dict, Any, Optional, List

from configs.logger import get_logger
from framework.context import load_context
from .models import PythonExecutionContext, PythonExecutionState, NotebookAttempt, NotebookType

logger = get_logger("framework", "python_services")


# =============================================================================
# FILE MANAGEMENT
# =============================================================================

class FileManager:
    """Comprehensive file system management service for Python execution workflows.
    
    This service provides robust file and folder operations specifically designed
    for the Python executor service's needs. It handles execution folder creation,
    permission management for container-based execution, context serialization,
    and Jupyter URL generation for external access to execution artifacts.
    
    The FileManager implements a structured approach to organizing execution
    artifacts with date-based hierarchical organization and unique execution
    identifiers. It automatically manages file system permissions to ensure
    compatibility with container-based execution environments.
    
    Key responsibilities include:
        - Creating and organizing execution folder structures
        - Managing file system permissions for container compatibility
        - Serializing and loading execution context data
        - Generating Jupyter-accessible URLs for execution artifacts
        - Providing robust JSON serialization for complex Python objects
    
    :param configurable: LangGraph configurable dictionary containing service configuration
    :type configurable: Dict[str, Any]
    
    .. note::
       The FileManager automatically creates the base directory structure if it
       doesn't exist and sets appropriate permissions for container access.
    
    .. seealso::
       :class:`PythonExecutionContext` : Execution context managed by this service
       :class:`NotebookManager` : Notebook-specific file operations
       :class:`framework.context.ContextManager` : Framework-level context management
    
    Examples:
        Basic file manager initialization and folder creation::
        
            >>> configurable = {"agent_data_dir": "/path/to/data"}
            >>> file_manager = FileManager(configurable)
            >>> context = file_manager.create_execution_folder("analysis_task")
            >>> print(f"Created folder: {context.folder_path}")
            >>> print(f"Jupyter URL: {context.folder_url}")
            
        Saving execution results::
        
            >>> results = {"mean": 42.0, "std": 3.14, "count": 100}
            >>> results_path = file_manager.save_results(results, context.folder_path)
            >>> print(f"Results saved to: {results_path}")
    """
    
    def __init__(self, configurable):
        """Initialize FileManager with configuration and set up base directory structure.
        
        Sets up the base directory for execution artifacts and ensures proper
        directory structure exists. The base directory is organized hierarchically
        with date-based subdirectories for efficient organization of execution
        artifacts over time.
        
        :param configurable: LangGraph configurable dictionary containing service settings
        :type configurable: Dict[str, Any]
        
        .. note::
           The base directory defaults to '_agent_data/executed_scripts' if not
           specified in the configurable dictionary.
        """
        self.configurable = configurable
        # Get agent data directory from configurable, fallback to _agent_data
        agent_data_dir = self.configurable.get('agent_data_dir', '_agent_data')
        self.base_dir = Path(agent_data_dir) / 'executed_scripts'
        self.base_dir = self.base_dir.resolve()
    
    def create_execution_folder(self, name: str = "python_executor") -> PythonExecutionContext:
        """Create a structured execution folder with proper permissions and organization.
        
        Creates a complete execution folder structure with date-based organization,
        unique identifiers, and proper permissions for container-based execution.
        The folder structure includes the main execution folder and an attempts
        subfolder for organizing multiple execution attempts.
        
        The method automatically handles permission management to ensure that
        container users (such as the jovyan user in Jupyter containers) can
        write to the created folders, solving common UID mapping issues between
        host and container environments.
        
        :param name: Descriptive name to include in the folder identifier
        :type name: str
        :return: Execution context with all folder paths and URLs configured
        :rtype: PythonExecutionContext
        :raises OSError: If folder creation fails due to permission or disk space issues
        
        .. note::
           The folder structure follows the pattern:
           `base_dir/YYYY-MM/execution_YYYYMMDD_HHMMSS_{name}_{uuid}/`
           with an `attempts/` subfolder for execution attempts.
        
        .. warning::
           This method sets very permissive permissions (0o777) to ensure container
           compatibility. Ensure the base directory is properly secured.
        
        Examples:
            Creating execution folder for data analysis::
            
                >>> file_manager = FileManager(configurable)
                >>> context = file_manager.create_execution_folder("sensor_analysis")
                >>> print(f"Main folder: {context.folder_path}")
                >>> print(f"Attempts folder: {context.attempts_folder}")
                >>> print(f"Jupyter URL: {context.folder_url}")
                
            Using the context for file operations::
            
                >>> if context.is_initialized:
                ...     results_file = context.folder_path / "results.json"
                ...     # File operations within the execution folder
        """
        # Create year-month subdirectory  
        now = datetime.now()
        month_dir = self.base_dir / now.strftime("%Y-%m")
        month_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique folder name
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        execution_id = uuid.uuid4().hex[:8]
        folder_name = f"execution_{timestamp}_{name}_{execution_id}"
        folder_path = month_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Create attempts subfolder
        attempts_folder = folder_path / "attempts"
        attempts_folder.mkdir(exist_ok=True)
        
        # Fix permissions so container user (jovyan) can write to folders
        # This solves the UID mapping issue between host and container
        try:
            # Set very permissive permissions to ensure container can write
            os.chmod(folder_path, 0o777)  # Full permissions for main folder
            os.chmod(attempts_folder, 0o777)  # Full permissions for attempts folder
            
            # Also set group sticky bit to ensure new files inherit group permissions
            current_mode = folder_path.stat().st_mode
            os.chmod(folder_path, current_mode | 0o2000)  # Add group sticky bit
            
        except Exception as e:
            logger.warning(f"Failed to fix folder permissions: {e}")
            # Don't fail folder creation just for permission issues
        
        # Create folder URL for Jupyter
        folder_url = self._create_jupyter_url(folder_path)
        
        context = PythonExecutionContext(
            folder_path=folder_path,
            folder_url=folder_url,
            attempts_folder=attempts_folder
        )
        
        logger.info(f"Created execution folder: {folder_path}")
        return context
    
    def save_results(self, results: Dict[str, Any], folder_path: Path) -> Path:
        """
        Save results dictionary to JSON file.
        
        Args:
            results: Results dictionary to save
            folder_path: Folder where to save the results
            
        Returns:
            Path to saved results file
        """
        results_file = folder_path / "results.json"
        
        try:
            # Convert to JSON-serializable format
            serializable_results = self._make_json_serializable(results)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved results to: {results_file}")
            return results_file
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    def _create_jupyter_url(self, folder_path: Path) -> str:
        """Create Jupyter Lab URL for the given folder path."""
        try:
            if folder_path.is_relative_to(self.base_dir):
                relative_path = folder_path.relative_to(self.base_dir)
                # Get Jupyter configuration from configurable
                # TODO: cleanup 
                service_configs = self.configurable.get('service_configs', {})
                framework_services = service_configs.get('framework', {})
                jupyter_config = framework_services.get('jupyter', {})
                containers = jupyter_config.get('containers', {})
                read_container = containers.get('read', {})
                port = read_container.get('port_host', 8088)
                # Always use localhost for external access, not container hostname
                hostname = 'localhost'
                return f"http://{hostname}:{port}/lab/tree/executed_scripts/{relative_path.as_posix()}"
            else:
                return folder_path.as_uri()
        except Exception as e:
            logger.warning(f"Failed to create Jupyter URL: {e}")
            return str(folder_path)
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert complex objects to JSON-serializable format using modern Python patterns."""
        import json
        
        def json_serializer(obj):
            """Custom serializer for JSON.dumps default parameter."""
            # Handle datetime objects
            if isinstance(obj, datetime):
                return obj.isoformat()
            # Handle numpy scalars
            elif hasattr(obj, 'item'):
                return obj.item()
            # Handle numpy arrays
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            # Handle pandas DataFrames and Series
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            # Default to string representation
            else:
                return str(obj)
        
        # Use json.loads(json.dumps()) to leverage Python's built-in serialization
        # This is more efficient and handles nested structures automatically
        try:
            return json.loads(json.dumps(obj, default=json_serializer, ensure_ascii=False))
        except (TypeError, ValueError):
            # Fallback to string if all else fails
            return str(obj)


# =============================================================================
# NOTEBOOK MANAGEMENT
# =============================================================================

class NotebookManager:
    """Comprehensive Jupyter notebook management service for Python execution workflows.
    
    This service specializes in creating, organizing, and managing Jupyter notebooks
    throughout the Python execution lifecycle. It provides comprehensive notebook
    generation capabilities for different stages including code generation attempts,
    pre-execution analysis, execution tracking, and final result presentation.
    
    The NotebookManager creates structured notebooks with rich metadata, execution
    context, and proper formatting for both automated processing and human review.
    It integrates with the FileManager to provide Jupyter-accessible URLs and
    maintains comprehensive audit trails of all execution attempts.
    
    Key features include:
        - **Stage-Aware Notebooks**: Different notebook types for different execution stages
        - **Rich Metadata**: Comprehensive context and execution information in each notebook
        - **Error Context**: Detailed error information and debugging context for failed attempts
        - **Approval Integration**: Notebooks formatted for human review and approval workflows
        - **URL Generation**: Jupyter-accessible URLs for direct notebook access
    
    :param configurable: LangGraph configurable dictionary containing service configuration
    :type configurable: Dict[str, Any]
    
    .. note::
       The NotebookManager relies on FileManager for URL generation and file
       system operations, ensuring consistency across the service layer.
    
    .. seealso::
       :class:`FileManager` : File system operations and URL generation
       :class:`NotebookType` : Enumeration of supported notebook types
       :class:`NotebookAttempt` : Notebook attempt tracking model
    
    Examples:
        Creating notebooks for different execution stages::
        
            >>> notebook_manager = NotebookManager(configurable)
            >>> # Create pre-execution notebook
            >>> notebook_path = notebook_manager.create_attempt_notebook(
            ...     context=execution_context,
            ...     code="import pandas as pd\ndf = pd.read_csv('data.csv')",
            ...     stage="pre_execution"
            ... )
            
        Creating notebooks with error context for debugging::
        
            >>> error_notebook = notebook_manager.create_attempt_notebook(
            ...     context=execution_context,
            ...     code=failed_code,
            ...     stage="execution",
            ...     error_context="NameError: name 'undefined_var' is not defined"
            ... )
    """
    
    def __init__(self, configurable):
        """Initialize NotebookManager with configuration and file management integration.
        
        Sets up the notebook manager with access to configuration settings and
        creates a FileManager instance for URL generation and file operations.
        This ensures consistent behavior across all file system operations.
        
        :param configurable: LangGraph configurable dictionary containing service settings
        :type configurable: Dict[str, Any]
        
        .. note::
           The NotebookManager automatically inherits FileManager capabilities
           for URL generation and file system operations.
        """
        self.configurable = configurable
        # Create a FileManager instance to reuse URL generation logic
        self._file_manager = FileManager(configurable)
    
    def create_attempt_notebook(
        self,
        context: PythonExecutionContext,
        code: str,
        stage: str = "execution",
        error_context: Optional[str] = None,
        approval_context: Optional[str] = None,
        silent: bool = False
    ) -> Path:
        """
        Create a debugging notebook for an execution attempt.
        Ensures context.json exists before creating the notebook.
        
        Args:
            context: Python execution context
            code: The Python code for this attempt
            stage: Current stage (e.g., "code_generation", "execution")
            error_context: Optional error context for failed attempts
            approval_context: Optional approval context for approval required attempts
            silent: If True, don't log creation (for cleaner logs when parent node handles logging)
            
        Returns:
            Path to created notebook
        """
        # Ensure context.json exists (should already be there, but verify)
        if not context.context_file_path:
            logger.warning("Context file not found when creating notebook - this should not happen")
        
        # Generate filename
        attempt_number = context.get_next_attempt_number()
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{attempt_number:02d}_{stage}_{timestamp}.ipynb"
        notebook_path = context.attempts_folder / filename
        
        # Create notebook content
        notebook = self._create_attempt_notebook_content(
            attempt_number=attempt_number,
            stage=stage,
            code=code,
            error_context=error_context,
            approval_context=approval_context,
            context_file_path=context.context_file_path
        )
        
        # Save notebook
        with open(notebook_path, 'w') as f:
            nbformat.write(notebook, f)
        
        # Track the attempt - use FileManager's URL generation
        attempt = NotebookAttempt(
            notebook_type=NotebookType.EXECUTION_ATTEMPT,
            attempt_number=attempt_number,
            stage=stage,
            notebook_path=notebook_path,
            notebook_link=self._file_manager._create_jupyter_url(notebook_path),
            error_context=error_context,
            created_at=datetime.now().isoformat()
        )
        context.add_notebook_attempt(attempt)
        
        if not silent:
            logger.info(f"Created attempt notebook: {notebook_path}")
        return notebook_path
    
    def create_final_notebook(
        self,
        context: PythonExecutionContext,
        code: str,
        results: Optional[Dict[str, Any]] = None,
        error_context: Optional[str] = None,
        figure_paths: List[Path] = None
    ) -> Path:
        """
        Create the final notebook in the execution folder.
        Ensures context.json exists before creating the notebook.
        
        Args:
            context: Python execution context
            code: The final Python code
            results: Optional execution results
            error_context: Optional error context for failures
            figure_paths: List of figure paths to include
            
        Returns:
            Path to created notebook
        """
        # Ensure context.json exists (should already be there, but verify)
        if not context.context_file_path:
            logger.warning("Context file not found when creating final notebook - this should not happen")
        
        notebook_path = context.folder_path / "notebook.ipynb"
        
        # Create notebook content
        notebook = self._create_final_notebook_content(
            code=code,
            results=results,
            error_context=error_context,
            context_file_path=context.context_file_path,
            figure_paths=figure_paths or [],
            execution_folder=context.folder_path
        )
        
        # Save notebook
        with open(notebook_path, 'w') as f:
            nbformat.write(notebook, f)
        
        logger.info(f"Created final notebook: {notebook_path}")
        return notebook_path
    
    def _create_attempt_notebook_content(
        self,
        attempt_number: int,
        stage: str,
        code: str,
        error_context: Optional[str] = None,
        approval_context: Optional[str] = None,
        context_file_path: Optional[Path] = None
    ) -> nbformat.NotebookNode:
        """Create notebook content for attempt notebooks."""
        cells = []
        
        # Header
        header = f"# Python Executor - Attempt #{attempt_number}\n\n"
        header += f"**Stage:** {stage}\n"
        header += f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if approval_context:    
            header += f"{approval_context}\n\n"

        if error_context:
            header += f"## Error Context\n{error_context}\n\n"
        
        cells.append(nbformat.v4.new_markdown_cell(header))
        
        # Context loading if available
        if context_file_path:
            context_code = textwrap.dedent("""
                # Load execution context
                from framework.context import load_context
                context = load_context('../context.json')
                """)
            cells.append(nbformat.v4.new_code_cell(context_code))
        
        # Main code
        cells.append(nbformat.v4.new_code_cell(code))
        
        notebook = nbformat.v4.new_notebook()
        notebook.cells = cells
        return notebook
    
    def _create_final_notebook_content(
        self,
        code: str,
        results: Optional[Dict[str, Any]] = None,
        error_context: Optional[str] = None,
        context_file_path: Optional[Path] = None,
        figure_paths: List[Path] = None,
        execution_folder: Optional[Path] = None
    ) -> nbformat.NotebookNode:
        """Create notebook content for final notebooks."""
        cells = []
        
        # Header with detailed error information
        if error_context:
            header = f"# Python Executor - Failed Execution\n\n## Error Context\n{error_context}\n\n"
        else:
            header = f"# Python Executor - Successful Execution\n\nExecution completed successfully.\n\n"
        
        cells.append(nbformat.v4.new_markdown_cell(header))
        
        # Context loading if available
        if context_file_path:
            context_code = textwrap.dedent("""
                # Load execution context
                from framework.context import load_context
                context = load_context('context.json')
                """)
            cells.append(nbformat.v4.new_code_cell(context_code))
        
        # Main code
        cells.append(nbformat.v4.new_code_cell(code))
        
        # Results section if available
        if results:
            results_md = "## Execution Results\n\nResults saved to `results.json`\n\n"
            results_md += "```python\nimport json\nwith open('results.json', 'r') as f:\n    results = json.load(f)\nprint(results)\n```"
            cells.append(nbformat.v4.new_markdown_cell(results_md))
        
        # Figures section if available
        if figure_paths and execution_folder:
            figures_md = "## Generated Figures\n\n"
            for i, fig_path in enumerate(figure_paths, 1):
                try:
                    relative_path = fig_path.relative_to(execution_folder)
                    figures_md += f"### Figure {i}\n![Figure {i}]({relative_path.as_posix()})\n\n"
                except ValueError:
                    figures_md += f"### Figure {i}\n![Figure {i}]({fig_path.name})\n\n"
            cells.append(nbformat.v4.new_markdown_cell(figures_md))
        
        notebook = nbformat.v4.new_notebook()
        notebook.cells = cells
        return notebook 