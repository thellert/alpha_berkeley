==================
Production Systems
==================

.. toctree::
   :maxdepth: 2
   :caption: Production Systems
   :hidden:

   01_human-approval-workflows
   02_data-source-integration
   03_python-execution-service
   04_memory-storage-service
   05_container-and-deployment

.. dropdown:: What You'll Learn
   :color: primary
   :icon: book

   **Enterprise-Grade Production Architecture:**
   
   - LangGraph-native approval workflows with configurable security policies
   - Multi-source data integration through provider framework patterns  
   - Container-isolated Python execution with security analysis and EPICS integration
   - Persistent memory storage with cross-session context preservation
   - Complete container management and service orchestration for scalable deployment

   **Prerequisites:** Solid understanding of Infrastructure Components and production deployment concepts
   
   **Target Audience:** DevOps engineers, system administrators, and architects deploying agentic systems in production environments

The Alpha Berkeley Framework offers enterprise-grade infrastructure components designed for secure and scalable deployment of agentic systems. These production-ready systems ensure human oversight, data integration, secure execution, and orchestration capabilities essential for high-stakes environments. By implementing a Security-First, Approval-Centric Architecture, the framework delivers robust capabilities while maintaining the flexibility needed for diverse deployment scenarios.

Core Production Components
==========================

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: 🛡️ Human Approval Workflows
      :link: 01_human-approval-workflows
      :link-type: doc
      :class-header: bg-danger text-white
      :class-body: text-center
      :shadow: md
      
      LangGraph-native interrupts with configurable policies, rich context, and fail-secure defaults for production environments.

   .. grid-item-card:: 🔗 Data Source Integration
      :link: 02_data-source-integration
      :link-type: doc
      :class-header: bg-info text-white
      :class-body: text-center
      :shadow: md
      
      Data retrieval from multiple sources with provider framework and intelligent discovery mechanisms.

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: 🐍 Python Execution Service
      :link: 03_python-execution-service
      :link-type: doc
      :class-header: bg-warning text-white
      :class-body: text-center
      :shadow: md
      
      Container and local execution with security analysis, Jupyter integration, and approval workflows.

   .. grid-item-card:: 🧠 Memory Storage Service
      :link: 04_memory-storage-service
      :link-type: doc
      :class-header: bg-success text-white
      :class-body: text-center
      :shadow: md

      **Persistent User Memory**
      
      File-based storage with framework integration and cross-session context preservation.

   .. grid-item-card:: 🚀 Container & Deployment
      :link: 05_container-and-deployment
      :link-type: doc
      :class-header: bg-primary text-white
      :class-body: text-center
      :shadow: md
      
      Complete container management with template rendering and hierarchical service discovery.

Production Integration Patterns
===============================

.. tab-set::

   .. tab-item:: Orchestrator Approval

      High-level execution plan approval with planning mode integration:

      .. code-block:: python

         # Planning mode enables strategic oversight
         user_input = "/planning Analyze beam performance and adjust parameters"
         
         # Orchestrator creates complete execution plan
         execution_plan = await create_execution_plan(
             task=current_task,
             capabilities=active_capabilities
         )
         
         # Human approval of entire plan before execution
         interrupt_data = create_plan_approval_interrupt(
             execution_plan=execution_plan,
             step_objective=current_task
         )
         interrupt(interrupt_data)  # LangGraph native interrupt

      - **Strategic plan oversight** before capability execution begins
      - **Multi-capability coordination** with human validation
      - **LangGraph-native interrupts** with resumable workflow
      - **Complete context** including capability dependencies and flow

   .. tab-item:: Python Execution

      Code-specific approval with EPICS analysis and container isolation:

      .. code-block:: python

         # Security analysis determines approval requirements
         analysis = await analyze_code_security(generated_code)
         
         # Domain-specific approval policies
         approval_evaluator = get_python_execution_evaluator()
         decision = approval_evaluator.evaluate(
             has_epics_writes=analysis.has_epics_writes,
             has_epics_reads=analysis.has_epics_reads
         )
         
         if decision.needs_approval:
             approval_result = await create_code_approval_interrupt(
                 code=generated_code,
                 analysis_details=analysis,
                 execution_mode=execution_mode
             )
         
         # Container-isolated execution
         result = await execute_in_container(code, environment)

      - **Code-level security analysis** with EPICS operation detection
      - **Configurable approval modes** (disabled, epics_writes, all_code)
      - **Container isolation** for secure execution environments
      - **Domain-specific policies** for accelerator control systems

   .. tab-item:: Data Integration

      Unified data access through the provider framework:

      .. code-block:: python

         # Parallel data retrieval pattern
         data_context = await data_manager.retrieve_all_context(
             DataSourceRequest(query=task.description)
         )
         
         # Available to all capabilities automatically
         user_memory = data_context.get("core_user_memory")
         domain_data = data_context.get("custom_provider")

      - **Automatic provider discovery** through registry system
      - **Parallel retrieval** with timeout management
      - **Type-safe integration** with capability context

   .. tab-item:: Service Orchestration

      Coordinated deployment and management of production services:

      .. code-block:: python

         # Container management with service discovery
         container_manager = ContainerManager()
         
         # Deploy related services as a group
         services = await container_manager.deploy_service_group([
             "pipelines-processing-service",
             "jupyter-execution-environment", 
             "langfuse-observability"
         ])
         
         # Health monitoring and automatic recovery
         for service in services:
             await monitor_service_health(service)

      - **Hierarchical service dependencies** with automatic ordering
      - **Health monitoring** with automatic restart policies
      - **Configuration templating** for environment-specific deployments

   .. tab-item:: Memory Integration

      Persistent user context with intelligent retrieval:

      .. code-block:: python

         # Memory-enhanced capability execution
         @capability_node
         class DataAnalysisCapability(BaseCapability):
             async def execute(state: AgentState, **kwargs):
                 # Automatic memory integration
                 user_context = await memory_provider.get_user_context(
                     user_id=state.user_id,
                     context_window=30  # days
                 )
                 
                 # Enhanced analysis with historical context
                 analysis = await analyze_with_memory(
                     current_data=state.current_task,
                     historical_context=user_context
                 )

      - **Automatic context injection** into capability execution
      - **Intelligent memory retrieval** based on task relevance
      - **Cross-session learning** from user interaction patterns