"""Python Executor Service - Comprehensive Python Code Generation and Execution Framework.

This package provides a sophisticated, LangGraph-based service for Python code generation,
static analysis, approval workflows, and secure execution with flexible deployment options.
The service integrates seamlessly with the broader agent framework to provide Python
execution capabilities with comprehensive safety controls, human oversight, and audit trails.

## **Key Features**

### **1. Flexible Execution Environments**
Switch between containerized and local execution with a single configuration line:
```yaml
framework:
  execution:
    execution_method: "container"  # or "local" - that's it!
```
- **Container Execution**: Secure, isolated Jupyter environments with full dependency management
- **Local Execution**: Direct host execution with automatic Python environment detection
- **Seamless Switching**: Same code, same results, different isolation levels

### **2. Comprehensive Jupyter Notebook Generation**
Automatic creation of rich, interactive notebooks for human evaluation and review:
- **Multi-Stage Notebooks**: Generated at code creation, analysis, and execution stages
- **Rich Metadata**: Complete execution context, analysis results, and error information
- **Direct Jupyter Access**: Click-to-open URLs for immediate notebook review
- **Audit Trails**: Complete history of execution attempts with detailed context
- **Figure Integration**: Automatic embedding of generated plots and visualizations

### **3. Human-in-the-Loop Approval System**
Production-ready approval workflows for high-stakes scientific and industrial environments:
- **LangGraph-Native Interrupts**: Seamless workflow suspension for human oversight
- **Security Analysis Integration**: Automatic detection of potentially dangerous operations
- **Rich Approval Context**: Detailed safety assessments, code analysis, and execution plans
- **Resumable Workflows**: Checkpoint-based execution resumption after approval
- **Configurable Policies**: Domain-specific approval rules for different operation types

## Architecture Overview

The service implements a sophisticated multi-stage pipeline with clean exception-based
architecture and comprehensive state management:

1. **Code Generation**: LLM-based Python code generation with context awareness and iterative improvement
2. **Static Analysis**: Security and policy analysis with configurable domain-specific rules
3. **Approval Workflows**: Human oversight system with rich context and safety assessments
4. **Flexible Execution**: Container or local execution with unified result collection
5. **Notebook Generation**: Comprehensive Jupyter notebook creation for human evaluation
6. **Result Processing**: Structured result handling with artifact management and audit trails

Core Components:
    - :class:`PythonExecutorService`: Main LangGraph service orchestrating the pipeline
    - :class:`PythonExecutionRequest`: Type-safe execution request with context data
    - :class:`PythonExecutionState`: LangGraph state management for service workflow
    - :class:`FileManager`: File operations and execution folder management
    - :class:`NotebookManager`: Jupyter notebook creation and management
    - :class:`ContainerExecutor`: Secure container-based Python execution engine

Exception Hierarchy:
    The package provides a comprehensive exception system organized by error category:
    
    - **Infrastructure Errors**: Container connectivity and configuration issues
        - :exc:`ContainerConnectivityError`: Container unreachable or connection failed
        - :exc:`ContainerConfigurationError`: Invalid container configuration
    
    - **Code-Related Errors**: Issues requiring code regeneration
        - :exc:`CodeGenerationError`: LLM failed to generate valid code
        - :exc:`CodeSyntaxError`: Generated code has syntax errors
        - :exc:`CodeRuntimeError`: Code execution failed with runtime errors
    
    - **Workflow Errors**: Service workflow and control issues
        - :exc:`ExecutionTimeoutError`: Code execution exceeded timeout limits
        - :exc:`MaxAttemptsExceededError`: Exceeded maximum retry attempts
        - :exc:`WorkflowError`: General workflow control errors

Configuration System:
    The service integrates with the framework's unified configuration system and
    supports multiple execution environments with configurable security policies.
    Execution modes range from read-only safe environments to write-enabled
    environments for EPICS control operations.

Security Features:
    - Static code analysis with security pattern detection
    - Configurable execution policies with domain-specific rules
    - Container-based execution isolation
    - Approval workflows for sensitive operations
    - Comprehensive audit logging and execution tracking

.. note::
   This service requires Docker containers for secure code execution. Container
   endpoints must be configured in the application configuration.

.. warning::
   Python code execution can perform system operations depending on the configured
   execution mode. Always review approval policies before enabling write access.

.. seealso::
   :class:`framework.capabilities.python.PythonCapability` : Main capability interface
   :class:`framework.services.python_executor.PythonExecutorService` : Core service
   :doc:`/developer-guides/python-execution` : Python execution architecture guide

## Configuration Examples

### **Execution Environment Configuration**
```yaml
# Container execution (default) - maximum security and isolation
framework:
  execution:
    execution_method: "container"
    modes:
      read_only:
        kernel_name: "python3-epics-readonly"
        allows_writes: false
      write_access:
        kernel_name: "python3-epics-write" 
        allows_writes: true
        requires_approval: true

# Local execution - direct host execution for development
framework:
  execution:
    execution_method: "local"
    python_env_path: "${LOCAL_PYTHON_VENV}"  # Optional: specific Python environment
```

### **Approval Workflow Configuration**
```yaml
# High-stakes scientific environment with strict approvals
agent_control_defaults:
  epics_writes_enabled: true  # Enable write operations with approval
  
framework:
  execution:
    modes:
      write_access:
        requires_approval: true  # Force human approval for write operations
```

## Usage Examples

### **Basic Execution with Automatic Notebook Generation**
```python
>>> from framework.capabilities.python import PythonCapability
>>> from framework.state import AgentState
>>> 
>>> state = AgentState()
>>> result = await PythonCapability.execute(
...     state, 
...     task_objective="Analyze EPICS PV trends and generate plots"
... )
>>> 
>>> # Execution results with notebook access
>>> print(f"Execution successful: {result['is_successful']}")
>>> print(f"Notebook available at: {result['PYTHON_RESULTS'].notebook_link}")
>>> print(f"Generated figures: {len(result['PYTHON_RESULTS'].figure_paths)}")
```

### **Container vs Local Execution Switching**
```python
# Same code works with both execution methods - just change config!

# Using container execution (secure, isolated)
>>> # config.yml: execution_method: "container"
>>> result = await PythonCapability.execute(state, task_objective="Process data")
>>> # Executes in secure Jupyter container

# Switch to local execution (faster, direct)  
>>> # config.yml: execution_method: "local"
>>> result = await PythonCapability.execute(state, task_objective="Process data")
>>> # Executes on local Python environment - same interface!
```

### **Human-in-the-Loop Approval Workflow**
```python
>>> # Code requiring approval automatically triggers interrupt
>>> result = await PythonCapability.execute(
...     state,
...     task_objective="Adjust EPICS setpoints for beam optimization"
... )
>>> # Execution pauses, user receives:
>>> # "⚠️ HUMAN APPROVAL REQUIRED ⚠️
>>> #  Task: Adjust EPICS setpoints for beam optimization
>>> #  Python code requires human approval for write_access mode
>>> #  📓 Review Code: [Open Jupyter Notebook](http://jupyter/notebook.ipynb)
>>> #  To proceed, respond with: **yes** to approve or **no** to cancel"

>>> # After user approves with "yes":
>>> # Execution automatically resumes and completes
>>> print(f"Approved execution result: {result['PYTHON_RESULTS'].results}")
```

### **Direct Service Usage for Advanced Integration**
```python
>>> from framework.services.python_executor import PythonExecutorService
>>> from framework.services.python_executor import PythonExecutionRequest
>>> 
>>> service = PythonExecutorService()
>>> request = PythonExecutionRequest(
...     user_query="Analyze accelerator performance data",
...     task_objective="Generate comprehensive performance report",
...     expected_results="Statistical analysis and trend visualizations"
... )
>>> result = await service.ainvoke(request, config=service_config)
>>> 
>>> # Rich result structure with notebook access
>>> print(f"Generated code: {result.generated_code}")
>>> print(f"Execution time: {result.execution_result.execution_time}s")
>>> print(f"Notebook: {result.execution_result.notebook_link}")
>>> print(f"Results: {result.execution_result.results}")
```
"""

from .service import PythonExecutorService
from .models import (
    PythonExecutionRequest,
    PythonExecutionSuccess,
    PythonExecutionState,
    PythonServiceResult,
    ExecutionModeConfig,
    ContainerEndpointConfig,
    NotebookAttempt,
    NotebookType,
    PythonExecutionContext
)
from .execution_control import (
    ExecutionMode,
    ExecutionControlConfig,
    get_execution_control_config
)
from .services import (
    FileManager,
    NotebookManager
)
from .exceptions import (
    # Base
    PythonExecutorException,
    ErrorCategory,
    
    # Infrastructure errors (retry execution)
    ContainerConnectivityError,
    ContainerConfigurationError,
    
    # Code errors (retry code generation)
    CodeGenerationError,
    CodeSyntaxError,
    CodeRuntimeError,
    
    # Workflow errors (special handling)
    ExecutionTimeoutError,
    MaxAttemptsExceededError,
    WorkflowError
)


__all__ = [
    # Main interface
    "PythonExecutorService",
    
    # Core types
    "PythonExecutionRequest",
    "PythonExecutionSuccess",
    "PythonExecutionState",
    "PythonServiceResult",
    
    # Execution context and notebook management
    "NotebookAttempt",
    "NotebookType", 
    "PythonExecutionContext",
    "FileManager",
    "NotebookManager",
    
    # Configuration utilities
    "ExecutionModeConfig",
    "ContainerEndpointConfig",
    "ExecutionMode",
    "ExecutionControlConfig",
    "get_execution_control_config",
    
    # Exception hierarchy
    "PythonExecutorException",
    "ErrorCategory",
    "ContainerConnectivityError",
    "ContainerConfigurationError",
    "CodeGenerationError",
    "CodeSyntaxError", 
    "CodeRuntimeError",
    "ExecutionTimeoutError",
    "MaxAttemptsExceededError",
    "WorkflowError"
] 