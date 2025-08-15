================
Python Execution
================

**What you'll build:** Python execution system with LangGraph workflows, human approval integration, and flexible container/local deployment

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Using :class:`PythonExecutorService` and :class:`PythonExecutionRequest` for code execution
   - Implementing :class:`PythonCapability` integration patterns in capabilities
   - Configuring container vs local execution with ``execution_method`` settings
   - Managing multi-stage analysis pipelines with checkpoint resumption
   - Exception handling with :exc:`CodeRuntimeError` and execution flow control

   **Prerequisites:** Understanding of :doc:`01_human-approval-workflows` and :doc:`../03_core-framework-systems/05_message-and-execution-flow`
   
   **Time Investment:** 60-90 minutes for complete understanding

Overview
========

The Python Execution Service provides a LangGraph-based system for Python code generation, static analysis, human approval, and secure execution. It supports both containerized and local execution environments with seamless switching through configuration.

**Key Features:**

- **Flexible Execution Environments**: Switch between container and local execution with configuration
- **Jupyter Notebook Generation**: Automatic creation of interactive notebooks for evaluation
- **Human-in-the-Loop Approval**: LangGraph-native interrupts with rich context and safety assessments
- **Exception-Based Flow Control**: Clean error handling with categorized errors for retry strategies
- **Multi-Stage Pipeline**: Code generation → analysis → approval → execution → result processing

**Execution Pipeline:**

1. **Code Generation**: LLM-based Python code generation with context awareness
2. **Static Analysis**: Security and policy analysis with configurable rules  
3. **Approval Workflows**: Human oversight system with rich context and safety assessments
4. **Flexible Execution**: Container or local execution with unified result collection
5. **Notebook Generation**: Comprehensive Jupyter notebook creation for evaluation
6. **Result Processing**: Structured result handling with artifact management

Configuration
=============

Configure your Python execution system with environment settings and approval policies:

.. code-block:: yaml

   # config.yml - Python Execution Configuration
   framework:
     execution:
       execution_method: "container"  # or "local"
       modes:
         read_only:
           kernel_name: "python3-epics-readonly"
           allows_writes: false
           requires_approval: false
         write_access:
           kernel_name: "python3-epics-write" 
           allows_writes: true
           requires_approval: true
       
       # Container execution settings
       container:
         jupyter_host: "localhost"
         jupyter_port: 8888
         execution_timeout: 300
         
       # Local execution settings  
       local:
         python_env_path: "${LOCAL_PYTHON_VENV}"
         execution_timeout: 120

   # Approval configuration for Python execution
   approval:
     global_mode: "selective"
     capabilities:
       python_execution:
         enabled: true
         mode: "epics_writes"  # disabled, all_code, epics_writes

**Configuration Options:**

- **execution_method**: "container" for secure isolation, "local" for direct host execution
- **modes**: Different execution environments with specific approval requirements
- **Container settings**: Jupyter endpoint configuration for containerized execution
- **Local settings**: Python environment path for direct execution

Integration Patterns
=====================

Using Python Execution in Capabilities
---------------------------------------

Use the Python execution service in your capabilities through the PythonCapability interface:

.. code-block:: python

   from framework.base import BaseCapability, capability_node
   from framework.state import AgentState
   from framework.context import ContextManager
   from framework.capabilities.python import PythonCapability

   @capability_node
   class DataAnalysisCapability(BaseCapability):
       """Data analysis capability using Python execution service."""
       
       async def execute(self, state: AgentState, context: ContextManager) -> dict:
           try:
               # Extract analysis requirements from context
               data_context = context.get_capability_context_data("analysis_data")
               analysis_objective = context.get_capability_context_data("task_objective") 
               
               # Prepare context data for Python execution
               execution_context = {
                   "task_objective": f"Analyze data and generate insights: {analysis_objective}",
                   "data_available": data_context is not None,
                   "analysis_requirements": [
                       "Generate statistical summary",
                       "Create visualizations", 
                       "Identify trends and patterns"
                   ],
                   "expected_results": "Statistical analysis with plots and insights"
               }
               
               # Set execution context for Python capability
               context.set_capability_context_data("python_context", execution_context)
               
               # Execute Python code generation and execution
               python_result = await PythonCapability().execute(state, context)
               
               if python_result.get("is_successful", False):
                   python_results = python_result["PYTHON_RESULTS"]
                   
                   return {
                       "success": True,
                       "analysis_completed": True,
                       "generated_code": python_results.code,
                       "execution_output": python_results.output,
                       "analysis_results": python_results.results,
                       "visualizations": python_results.figure_paths,
                       "notebook_link": python_results.notebook_link,
                       "execution_time": python_results.execution_time
                   }
               else:
                   error_message = python_result.get("error", "Python execution failed")
                   return {
                       "success": False,
                       "analysis_completed": False,
                       "error": error_message
                   }
                   
           except Exception as e:
               return {
                   "success": False,
                   "error": f"Analysis capability error: {str(e)}"
               }

Direct Service Usage
--------------------

For advanced use cases, interact directly with the PythonExecutorService:

.. code-block:: python

   from framework.services.python_executor import PythonExecutorService, PythonExecutionRequest
   from framework.services.python_executor.exceptions import CodeRuntimeError
   from langgraph.types import Command

   class AdvancedPythonIntegration:
       """Advanced integration with Python executor service."""
       
       def __init__(self):
           self.service = PythonExecutorService()
       
       async def execute_analysis_workflow(self, analysis_request: dict) -> dict:
           """Execute analysis workflow with direct service control."""
           
           try:
               # Create structured execution request
               execution_request = PythonExecutionRequest(
                   user_query=analysis_request["user_query"],
                   task_objective=analysis_request["task_objective"],
                   expected_results=analysis_request.get("expected_results", "Analysis results"),
                   execution_folder_name=analysis_request.get("folder_name", "analysis"),
                   capability_context_data=analysis_request.get("context_data", {})
               )
               
               # Configure service execution
               service_config = {
                   "thread_id": f"analysis_{analysis_request.get('session_id', 'default')}",
                   "configurable": {
                       "execution_mode": analysis_request.get("execution_mode", "readonly"),
                       "max_execution_time": analysis_request.get("timeout", 300)
                   }
               }
               
               # Execute with comprehensive error handling
               result = await self.service.ainvoke(execution_request, service_config)
               
               return await self._process_service_result(result)
               
           except CodeRuntimeError as e:
               return await self._handle_code_error(e, analysis_request)
               
           except Exception as e:
               return {
                   "success": False,
                   "error": f"Service execution failed: {str(e)}",
                   "error_type": "service_error"
               }

Execution Environment Management
================================

Container vs Local Execution
-----------------------------

Switch between execution environments seamlessly:

.. code-block:: python

   class FlexiblePythonExecution:
       """Demonstrate flexible execution environment switching."""
       
       def _select_execution_environment(self, code_request: dict) -> str:
           """Select optimal execution environment based on request characteristics."""
           
           requires_isolation = code_request.get("requires_isolation", False)
           has_dependencies = code_request.get("has_special_dependencies", False)
           is_long_running = code_request.get("estimated_time", 0) > 300
           security_level = code_request.get("security_level", "medium")
           
           # Decision logic for environment selection
           if security_level == "high" or requires_isolation:
               return "container"
           elif has_dependencies or is_long_running:
               return "container"
           else:
               return "local"  # Faster for simple operations

Environment Selection Strategies
--------------------------------

- **Security-based**: High-security operations use container isolation
- **Performance-based**: Simple operations use local execution for speed
- **Dependency-based**: Complex dependencies require containerized environments
- **Resource-based**: Long-running operations benefit from container resource management

Advanced Patterns
=================

Multi-Stage Analysis Pipeline
-----------------------------

Chain multiple Python executions for complex analysis workflows:

.. code-block:: python

   async def multi_stage_analysis(self, data_context: dict) -> dict:
       """Execute multi-stage analysis pipeline."""
       
       # Stage 1: Data preprocessing
       preprocessing_request = PythonExecutionRequest(
           user_query="Data preprocessing stage",
           task_objective="Clean and prepare data for analysis",
           execution_folder_name="stage1_preprocessing"
       )
       
       stage1_result = await self.python_service.ainvoke(preprocessing_request, config)
       
       # Stage 2: Statistical analysis (using results from stage 1)
       analysis_request = PythonExecutionRequest(
           user_query="Statistical analysis stage",
           task_objective="Perform statistical analysis on preprocessed data",
           execution_folder_name="stage2_analysis",
           capability_context_data={
               "preprocessing_results": stage1_result.execution_result.results
           }
       )
       
       stage2_result = await self.python_service.ainvoke(analysis_request, config)
       
       return {
           "pipeline_completed": True,
           "stages": {
               "preprocessing": stage1_result,
               "analysis": stage2_result
           }
       }

Adaptive Execution Strategy
---------------------------

Adapt execution strategy based on data quality assessment:

.. code-block:: python

   async def adaptive_execution(self, data_context: dict) -> dict:
       """Adapt execution strategy based on data quality."""
       
       # Assess data quality first
       quality_score = self._assess_data_quality(data_context)
       
       if quality_score > 0.8:
           execution_mode = "advanced_analysis"
           task_objective = "Perform comprehensive advanced statistical analysis"
       elif quality_score > 0.5:
           execution_mode = "standard_with_preprocessing" 
           task_objective = "Preprocess data and perform standard analysis"
       else:
           execution_mode = "basic_with_cleaning"
           task_objective = "Extensive data cleaning and basic analysis"
       
       request = PythonExecutionRequest(
           user_query=f"Adaptive analysis: {execution_mode}",
           task_objective=task_objective,
           execution_folder_name=f"adaptive_{execution_mode}",
           capability_context_data={
               "data_quality_score": quality_score,
               "execution_mode": execution_mode
           }
       )
       
       return await self.python_service.ainvoke(request, config)

Testing and Validation
======================

Test your Python execution integration with various scenarios:

.. code-block:: python

   async def test_python_execution_integration():
       """Test Python execution service integration."""
       
       # Test 1: Container execution
       container_request = PythonExecutionRequest(
           user_query="Test container execution",
           task_objective="Generate simple plot and statistical analysis",
           execution_folder_name="test_container"
       )
       
       container_config = {
           "thread_id": "test_container",
           "configurable": {"execution_method": "container"}
       }
       
       service = PythonExecutorService()
       container_result = await service.ainvoke(container_request, container_config)
       
       assert hasattr(container_result, 'execution_result')
       assert container_result.execution_result.success
       
       # Test 2: Local execution
       local_request = PythonExecutionRequest(
           user_query="Test local execution",
           task_objective="Simple mathematical calculation",
           execution_folder_name="test_local"
       )
       
       local_config = {
           "thread_id": "test_local", 
           "configurable": {"execution_method": "local"}
       }
       
       local_result = await service.ainvoke(local_request, local_config)
       
       # Test 3: Error handling
       try:
           error_request = PythonExecutionRequest(
               user_query="Test error handling",
               task_objective="Generate code with intentional error",
               execution_folder_name="test_error"
           )
           error_result = await service.ainvoke(error_request, {"thread_id": "test_error"})
       except CodeRuntimeError as e:
           print(f"Properly caught CodeRuntimeError: {e.message}")

**Production Deployment Checklist:**

- [ ] Container endpoints configured and accessible
- [ ] Python execution environments properly set up
- [ ] Approval policies configured for your security requirements
- [ ] Error handling covers all execution failure scenarios
- [ ] Resource management (timeouts, memory limits) configured
- [ ] Notebook generation and access working correctly

Troubleshooting
===============

**Common Issues:**

**Issue**: Python execution service not available
   - **Cause**: Service not registered in framework registry
   - **Solution**: Verify PythonExecutorService is registered in registry configuration

**Issue**: Container execution failing with connection errors
   - **Cause**: Jupyter container not accessible or misconfigured
   - **Solution**: Check container endpoints and ensure Jupyter is running

**Issue**: Approval workflows not triggering
   - **Cause**: Approval configuration not properly set
   - **Solution**: Verify approval policies in config.yml and ApprovalManager setup

**Issue**: Generated notebooks not accessible
   - **Cause**: File path or URL generation issues
   - **Solution**: Check execution folder configuration and notebook link generation

**Debugging Python Execution Issues:**

.. code-block:: python

   # Enable detailed Python execution logging
   import logging
   logging.getLogger("framework.services.python_executor").setLevel(logging.DEBUG)
   
   # Test service availability
   from framework.services.python_executor import PythonExecutorService
   service = PythonExecutorService()
   print(f"Service initialized: {service is not None}")
   
   # Verify approval configuration
   from framework.approval import get_approval_manager
   manager = get_approval_manager()
   python_config = manager.get_python_execution_config()
   print(f"Python approval enabled: {python_config.enabled}")

Next Steps
==========

After implementing Python execution service integration:

- :doc:`04_memory-storage-service` - Integrate memory storage with Python execution
- :doc:`05_container-and-deployment` - Advanced container orchestration

**Related API Reference:**

- :doc:`../../api_reference/03_production_systems/03_python-execution` - Complete Python execution API
- :doc:`../../api_reference/03_production_systems/01_human-approval` - Approval system integration
- :doc:`../../api_reference/01_core_framework/02_state_and_context` - State management for execution workflows