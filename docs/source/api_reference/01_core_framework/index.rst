==============
Core Framework
==============

.. toctree::
   :maxdepth: 2
   :caption: Core Framework APIs
   :hidden:

   01_base_components
   02_state_and_context
   03_registry_system
   04_configuration_system
   05_prompt_management

.. dropdown:: What You'll Find Here
   :color: primary
   :icon: book

   **Essential APIs for daily development:**
   
   - **BaseCapability & BaseInfrastructureNode** - Foundation classes with LangGraph integration
   - **AgentState & StateManager** - LangGraph-native state management with selective persistence
   - **ContextManager & CapabilityContext** - Type-safe data exchange between components
   - **RegistryManager & component discovery** - Convention-based component loading
   - **UnifiedConfig & environment resolution** - Seamless configuration management
   - **FrameworkPromptProvider & customization** - Domain-agnostic prompt management

   **Prerequisites:** Basic Python knowledge and agentic system concepts
   
   **Target Audience:** Framework developers, capability authors, infrastructure builders
   
The Core Framework provides the **essential foundation APIs** that enable reliable, type-safe agentic system development. These five interconnected systems form the backbone of every capability, infrastructure node, and production deployment in the Alpha Berkeley Framework.



System Architecture
===================

The Core Framework implements a **Type-Safe, Convention-Driven Architecture** with five integrated components:

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: 🏗️ Base Components
      :link: 01_base_components
      :link-type: doc
      :class-header: bg-primary text-white
      :class-body: text-center
      :shadow: md
            
      **Foundation & LangGraph Integration**
      
      BaseCapability, BaseInfrastructureNode, and decorators for seamless framework integration with error handling and planning.

   .. grid-item-card:: 🔄 State & Context Management
      :link: 02_state_and_context
      :link-type: doc
      :class-header: bg-success text-white
      :class-body: text-center
      :shadow: md
            
      **Data Persistence & Exchange**
      
      AgentState with selective persistence, ContextManager for type-safe data access, and Pydantic-based serialization.

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: 📋 Registry System
      :link: 03_registry_system
      :link-type: doc
      :class-header: bg-info text-white
      :class-body: text-center
      :shadow: md
            
      **Component Discovery & Management**
      
      Configuration-driven component loading with lazy initialization, dependency resolution, and type-safe access.

   .. grid-item-card:: ⚙️ Configuration System
      :link: 04_configuration_system
      :link-type: doc
      :class-header: bg-warning text-white
      :class-body: text-center
      :shadow: md

      **Environment & Settings Management**
      
      YAML-based configuration with environment resolution, model settings, and LangGraph integration.

.. grid:: 1 1 1 1
   :gutter: 3

   .. grid-item-card:: 💬 Prompt Management
      :link: 05_prompt_management
      :link-type: doc
      :class-header: bg-secondary text-white
      :class-body: text-center
      :shadow: md

      **Domain-Agnostic Prompt System**
      
      Dependency injection for prompt customization with builder patterns, defaults, and application-specific overrides.

Framework Integration Patterns
==============================

These systems work together to provide a unified development experience:

.. tab-set::

   .. tab-item:: Startup and Initialization

      How the framework initializes and loads components:

      .. code-block:: python

         from framework.registry import initialize_registry, get_registry
         from framework.state import StateManager
         
         # 1. Initialize the global registry system (application startup)
         initialize_registry()  # Loads all applications and components
         
         # 2. Access the initialized registry
         registry = get_registry()
         
         # 3. Components are now available for use
         capability = registry.get_capability('data_analysis')
         context_class = registry.get_context_class('ANALYSIS_RESULTS')
         data_source = registry.get_data_source('core_user_memory')

   .. tab-item:: State and Context Flow

      How state and context work together during execution:

      .. code-block:: python

         from framework.state import StateManager
         from framework.context import ContextManager
         
         # 1. Create fresh state for new conversation
         state = StateManager.create_fresh_state(
             user_input="Analyze beam performance data",
             current_state=previous_state  # Preserves context
         )
         
         # 2. Access context through ContextManager
         context = ContextManager(state)
         
         # 3. Retrieve typed context objects
         pv_data = context.get_context('PV_ADDRESSES', 'beam_current')
         
         # 4. Store new context results
         return StateManager.store_context(
             state, 'ANALYSIS_RESULTS', 'step_1', analysis_results
         )

   .. tab-item:: Configuration Access

      How to access configuration values throughout the framework:

      .. code-block:: python

         from configs.unified_config import (
             get_config_value, get_model_config, get_full_configuration
         )
         
         # Simple configuration access with defaults
         timeout = get_config_value('execution.timeout', 30)
         debug_mode = get_config_value('development.debug', False)
         
         # Model-specific configuration
         model_config = get_model_config('framework', 'orchestrator')
         
         # Full configuration for service passing
         full_config = get_full_configuration()
         service_config = {
             "configurable": {
                 **full_config,
                 "thread_id": f"my_service_{context_key}"
             }
         }

   .. tab-item:: Capability Implementation

      Real capability implementation pattern from the framework:

      .. code-block:: python

         from framework.base import BaseCapability, capability_node
         from framework.state import AgentState, StateManager
         from framework.context import ContextManager
         from configs.unified_config import get_model_config
         from applications.als_expert.context_classes import AnalysisResultsContext
         
         @capability_node
         class DataAnalysisCapability(BaseCapability):
             name = "data_analysis"
             description = "General data analysis capability"
             provides = ["ANALYSIS_RESULTS"]
             
             @staticmethod
             async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
                 # Extract current execution step
                 step = StateManager.get_current_step(state)
                 
                 # Access context manager for input data
                 context = ContextManager(state)
                 
                 # Get configuration for models/services
                 model_config = get_model_config('framework', 'python_code_generator')
                 
                 # Process data (actual implementation logic)
                 analysis_results = await process_analysis(step, context)
                 
                 # Create typed context object
                 result_context = AnalysisResultsContext(
                     analysis_summary=analysis_results.summary,
                     confidence_score=analysis_results.confidence,
                     **analysis_results.data
                 )
                 
                 # Store results in state
                 return StateManager.store_context(
                     state, 'ANALYSIS_RESULTS', 
                     step.get('context_key', 'default'), 
                     result_context
                 )

.. dropdown:: Next Steps
   :color: primary
   :icon: arrow-up-right
   
   After mastering the Core Framework APIs, explore related systems:

   .. grid:: 1 1 2 2
      :gutter: 3
      :class-container: guides-section-grid

      .. grid-item-card:: ⚡ Infrastructure APIs
         :link: ../02_infrastructure/index
         :link-type: doc
         :class-header: bg-success text-white
         :class-body: text-center
         :shadow: md
         
         Gateway, task extraction, classification, and orchestration APIs for building intelligent processing pipelines

      .. grid-item-card:: 🚀 Production Systems
         :link: ../03_production_systems/index
         :link-type: doc
         :class-header: bg-info text-white
         :class-body: text-center
         :shadow: md
         
         Human approval, data management, container deployment for production-ready agentic systems

      .. grid-item-card:: 🔧 Framework Utilities
         :link: ../05_framework_utilities/index
         :link-type: doc
         :class-header: bg-warning text-white
         :class-body: text-center
         :shadow: md
         
         Model factory, logging, streaming, and developer tools for advanced framework customization

      .. grid-item-card:: 📖 Developer Guides
         :link: ../../developer-guides/03_core-framework-systems/index
         :link-type: doc
         :class-header: bg-primary text-white
         :class-body: text-center
         :shadow: md
         
         Learning-oriented guides for understanding core framework architecture and advanced patterns