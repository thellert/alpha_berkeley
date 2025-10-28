Build Your First Agent - Multi-Capability Integration Tutorial  
==============================================================

This tutorial builds on the Hello World foundations to demonstrate **orchestration integration patterns** through a wind turbine monitoring agent. You'll learn multi-step workflows, simple RAG integration, Python service integration, and human-in-the-loop workflows. The wind turbine scenario shows how to connect multiple capabilities in coordinated workflows - the techniques are intentionally straightforward to focus on the integration patterns.

.. dropdown:: **Prerequisites**
   :color: info
   :icon: list-unordered

   **Required:** Complete the :doc:`Hello World Tutorial <hello-world-tutorial>` first.

   That tutorial covers the fundamental patterns you need:

   - **Context classes** - Data flow and type safety  
   - **Basic capabilities** - Structure, execution, and error handling
   - **Mock API integration** - External service patterns
   - **Registry configuration** - Component registration
   - **Application setup** - Framework integration

   **What's New Here:** Multi-step orchestration with 6 coordinated capabilities, basic RAG integration patterns, dynamic Python execution with human approval workflows, complex data dependencies across multiple capabilities, and application-specific configuration overrides.

Getting Started - Create the Project
------------------------------------

First, create a new wind turbine project from the template using :doc:`framework init <../developer-guides/02_quick-start-patterns/00_cli-reference>`:

.. code-block:: bash

   framework init turbine-agent --template wind_turbine
   cd turbine-agent

This generates a complete, self-contained project with the following structure:

.. code-block::

   turbine-agent/                 # Your project directory
   ├── src/
   │   └── turbine_agent/         # Package name (derived from project name: turbine-agent → turbine_agent)
   │       ├── __init__.py
   │       ├── registry.py
   │       ├── context_classes.py
   │       ├── mock_apis.py
   │       ├── capabilities/
   │       │   ├── __init__.py
   │       │   ├── weather_data_retrieval.py
   │       │   ├── turbine_data_archiver.py
   │       │   ├── knowledge_retrieval.py
   │       │   └── turbine_analysis.py
   │       ├── data_sources/
   │       │   ├── __init__.py
   │       │   └── knowledge_provider.py
   │       └── framework_prompts/
   │           ├── __init__.py
   │           └── response_generation.py
   ├── services/                  # Container service configurations
   ├── config.yml                 # Complete configuration
   └── .env.example               # API key template

.. admonition:: New in v0.7+: Template-Based Projects
   :class: version-07plus-change

   Projects are now generated from templates using ``framework init``. The template code is the canonical reference - you can view it on GitHub at `src/framework/templates/apps/wind_turbine <https://github.com/thellert/alpha_berkeley/tree/main/src/framework/templates/apps/wind_turbine>`_.

🎯 What You'll Learn
--------------------

See how the framework coordinates this multi-step analysis request:

.. code-block:: text

   "Our wind farm has been underperforming lately. Can you analyze the turbine 
   performance over the past 2 weeks, identify which turbines are operating 
   below industry standards, and rank them by efficiency? I need to know which 
   ones require immediate maintenance attention."

Into a **6-step orchestrated execution plan** that looks like this:

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────────┐
   │  🔄 Task Classification → 6 capabilities identified            │
   │  📋 Execution Planning → 6-step plan generated                 │
   └─────────────────────────────────────────────────────────────────┘
   
   Step 1/6: time_range_parsing
   ├─ Input:  "past 2 weeks"
   └─ Output: 2025-07-26 to 2025-08-09 datetime range
   
   Step 2/6: turbine_data_archiver  
   ├─ Source: Mock Turbine API
   └─ Output: 1,680 turbine readings retrieved
   
   Step 3/6: weather_data_retrieval
   ├─ Source: Mock Weather API  
   └─ Output: 336 wind speed measurements retrieved
   
   Step 4/6: knowledge_retrieval
   ├─ Source: Knowledge Base (LLM processing)
   └─ Output: Performance thresholds extracted
            • >85% excellent • 75-85% good • <75% maintenance
   
   Step 5/6: turbine_analysis
   ├─ Process: LLM creates analysis plan
   ├─ Execute: Python code generation & execution  
   └─ Output:  Results calculated & ranked
   
   Step 6/6: respond
   ├─ Input:   Analysis results + knowledge thresholds
   └─ Output:  📊 Maintenance report with turbine rankings



**5 Key Integration Patterns:**

.. tab-set::
   :class: natural-width

   .. tab-item:: 📚 Simple Knowledge Provider

      **Pattern:** Basic RAG integration that extracts structured parameters from simple text documents
      
      **What's New:** Unlike Hello World's simple data retrieval, this shows how to integrate a knowledge source into your workflow. The extraction is intentionally simple (LLM reads a small text document) to focus on the integration pattern, not RAG complexity.
      
      **How It Works:** The `WindFarmKnowledgeProvider` acts as a mock enterprise knowledge base. When capabilities need domain expertise (like performance thresholds), they request knowledge through the framework's data management system. The LLM reads static technical documents and extracts specific numerical parameters:
      
      - **Documents:** Wind turbine specifications, performance benchmarks, maintenance thresholds

      - **Extraction:** LLM converts text like "Excellent performance: Above 85% capacity factor" into structured data like `excellent_performance_threshold_percent: 85.0`

      - **Usage:** Other capabilities access this knowledge through the `TurbineKnowledgeContext` for decision-making

   .. tab-item:: 🧮 Python Analysis Capability

      **Pattern:** Multi-phase workflow with LLM planning + Dynamic code generation + Human approval
      
      **What's New:** Multi-step analysis that creates execution plans, generates Python code, and requires human oversight for sensitive operations.
      
      **How It Works:** The `TurbineAnalysisCapability` demonstrates sophisticated workflow orchestration:
      
      - **Phase 1 - Planning:** LLM creates structured analysis plan with phases like "Data Preparation," "Performance Metrics Calculation," and "Industry Benchmark Comparison"

      - **Phase 2 - Code Generation:** Framework automatically converts the plan into executable Python code, handling data access patterns and calculations

      - **Phase 3 - Human Approval:** Before execution, the system presents the generated code to humans for review and approval, ensuring safety for sensitive operations (the wind turbine tutorial specifically configures approval for ALL Python code to demonstrate this workflow)

      - **Phase 4 - Execution:** Approved code runs in a sandboxed environment, producing structured results that feed back into the agent workflow

   .. tab-item:: 🌐 Multi-Capability Data Flow

      **Pattern:** Complex dependencies where 4 capabilities feed into 1 analysis capability
      
      **What's New:** Demonstrates how context classes enable seamless data flow between multiple specialized capabilities.
      
      **How It Works:** The wind turbine agent orchestrates a sophisticated data pipeline with automatic dependency resolution:
      
      - **Data Sources:** Four capabilities (`time_range_parsing`, `turbine_data_archiver`, `weather_data_retrieval`, `knowledge_retrieval`) each produce typed context objects
  
      - **Context Classes:** Pydantic-based classes like `TurbineDataContext` and `WeatherDataContext` ensure type safety and automatic serialization
    
      - **Dependency Management:** The `TurbineAnalysisCapability` declares its requirements (`TURBINE_DATA`, `WEATHER_DATA`, `TURBINE_KNOWLEDGE`) and the framework automatically routes the correct data
      
      - **Access Patterns:** Context classes provide rich metadata about data structure, enabling the LLM to generate correct code like `pd.DataFrame({'timestamp': context.TURBINE_DATA.key.timestamps, 'power': context.TURBINE_DATA.key.power_outputs})`

   .. tab-item:: 🎨 Custom Framework Prompts

      **Pattern:** Domain-specific prompt builders that override framework defaults for specialized behavior
      
      **What's New:** Replace generic framework prompts with wind turbine-specific instructions for structured analysis, industry terminology, and formatted reporting. Shows how to customize the AI's behavior for your domain.
      
      **How It Works:** The `WindTurbineResponseGenerationPromptBuilder` demonstrates domain-specific LLM behavior customization:
      
      - **Role Specialization:** Transforms generic AI assistant into "expert wind turbine performance analyst providing detailed technical analysis and maintenance recommendations"
      
      - **Industry Standards:** Enforces use of proper terminology (capacity factor, efficiency ratio) and referencing actual knowledge base thresholds rather than making assumptions
      
      - **Structured Output:** Mandates specific formatting with performance tables, clear headings ("Performance Overview," "Rankings," "Maintenance Recommendations"), and rounded numerical values for readability
      
      - **Context Awareness:** Provides different behavior for conversational vs. technical responses, ensuring appropriate depth and formatting based on available execution context

   .. tab-item:: ⚙️ Advanced Application Setup

      **Pattern:** Complete application customization through registry management and configuration overrides
      
      **What's New:** Shows how to override framework defaults, register domain-specific components, and customize system behavior through application-specific configuration.
      
      **How It Works:** The wind turbine application demonstrates comprehensive framework customization through two key mechanisms:
      
      **Registry Customization (`WindTurbineRegistryProvider`):**
      
      - **Framework Exclusions:** Explicitly excludes the generic `python` capability via `exclude_capabilities=["python"]` parameter to prevent conflicts with the specialized `turbine_analysis` capability
      
      - **Custom Registration:** Registers 4 domain-specific capabilities, 4 context classes, 1 data source, and 1 framework prompt provider, all tailored to wind turbine monitoring
      
      - **Dependency Declaration:** Each capability declares what it `provides` and `requires`, enabling automatic workflow orchestration
      
      - **Initialization Order:** Controls component loading sequence through `initialization_order` to ensure dependencies are available when needed
      
      **Configuration Overrides (`config.yml`):**
      
      - **Approval Settings:** Overrides the main config's `python_execution.mode: "epics_writes"` with `mode: "all_code"` to require approval for ALL Python code execution (perfect for demonstrating human-in-the-loop workflows)
      
      - **Application Models:** Defines wind turbine-specific LLM configurations for `turbine_analysis` and `knowledge_retrieval`
      
      - **Logging Colors:** Customizes capability colors for better development experience
      
      - **Flat Configuration:** Application settings coexist with framework settings in a single config file using unique naming, providing transparent and explicit configuration management


Let's explore the integration patterns step by step.

Step 1: Multi-Capability Context Classes
----------------------------------------

The wind turbine application uses **4 specialized context classes** that demonstrate data flow patterns for multi-capability coordination.

**Reference:** See :ref:`hello-world-tutorial-context-classes` for basic context class structure (``CapabilityContext``, required methods, field definitions).

**What's New Here:** Complex data relationships and LLM-optimized access patterns:

.. code-block:: python

   # Advanced pattern: Parallel lists optimized for Python DataFrame creation
   class TurbineDataContext(CapabilityContext):
       timestamps: List[datetime] = Field(description="List of timestamps for data points")
       turbine_ids: List[str] = Field(description="List of turbine IDs")  
       power_outputs: List[float] = Field(description="List of power outputs in MW")
       
       def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           # Teaches LLM how to create DataFrames from parallel lists
           return {
               "example_usage": f"pd.DataFrame({{'timestamp': context.TURBINE_DATA.{key_ref}.timestamps, 'turbine_id': context.TURBINE_DATA.{key_ref}.turbine_ids, 'power_output': context.TURBINE_DATA.{key_ref}.power_outputs}})"
           }

**Key Design Choices:**

- **Parallel Lists**: ``timestamps``, ``turbine_ids``, ``power_outputs`` align by index for easy DataFrame creation
- **Knowledge Containers**: ``TurbineKnowledgeContext`` holds structured parameters extracted by LLM from unstructured docs
- **Analysis Results**: ``AnalysisResultsContext`` stores Python execution outputs with flexible schema

**File Locations:**
- Full implementations: ``src/turbine_agent/context_classes.py``
- Basic patterns explained in: :doc:`Hello World Tutorial <hello-world-tutorial>`

Step 2: Mock APIs
-----------------

The wind turbine application includes basic mock APIs for tutorial purposes:

- **`TurbineSensorAPI`** - Returns turbine power output data
- **`WeatherAPI`** - Provides wind speed measurements  

These follow the same patterns covered in :ref:`hello-world-tutorial-mock-apis` (type-safe models, async methods, realistic data structures). Nothing special here - just supporting infrastructure to demonstrate the framework's integration patterns.

**File Location:** ``src/turbine_agent/mock_apis.py``

Step 3: Simple Knowledge Integration
------------------------------------

**Reference:** Basic data source provider patterns are covered in :ref:`hello-world-tutorial-data-sources`.

**What's New Here:** **Basic RAG integration** that shows how to include knowledge sources in your workflow. The extraction itself is deliberately simple to focus on the integration pattern:

**Core Implementation:**

.. code-block:: python

   class WindFarmKnowledgeProvider(DataSourceProvider):
       async def retrieve_data(self, request: DataSourceRequest) -> Optional[DataSourceContext]:
           # LLM processes knowledge base → structured output
           knowledge_result = get_chat_completion(
               message=retrieval_prompt,
               output_model=KnowledgeRetrievalResult  # Structured extraction
           )
           
           # Returns typed parameters, not raw text
           return DataSourceContext(data=TurbineKnowledgeContext(
               knowledge_data=knowledge_result.knowledge_data  # e.g., {"excellent_efficiency_percent": 85.0}
           ))

**Example Output:** Instead of text like "Excellent performance: Above 85% capacity factor", you get ``{"excellent_efficiency_percent": 85.0}`` ready for Python calculations.

**File Location:** ``src/turbine_agent/data_sources/knowledge_provider.py``

Step 4: Multi-Capability Coordination
-------------------------------------

**Reference:** Basic capability patterns (``@capability_node``, ``execute()``, error handling, guides) are covered in :ref:`hello-world-tutorial-capabilities`.

**What's New Here:** **Context storage and retrieval patterns** that enable data flow between capabilities:

.. tab-set::

   .. tab-item:: 📤 Context Storage

      **Pattern:** How capabilities store their results for other capabilities to use
      
      **Implementation:** All capabilities follow the same storage pattern using `StateManager.store_context()`:
      
      .. code-block:: python
      
         # Create typed context object
         turbine_data = TurbineDataContext(
             timestamps=timestamps,
             turbine_ids=turbine_ids,
             power_outputs=power_outputs,
             time_range=f"{start_date} to {end_date}",
             total_records=len(readings)
         )
         
         # Store using StateManager - makes data available to other capabilities
         return StateManager.store_context(
             state, 
             registry.context_types.TURBINE_DATA,  # What type of data this is
             step.get("context_key"),              # Unique key from execution plan
             turbine_data                          # The actual data object
         )

   .. tab-item:: 📥 Context Retrieval

      **Pattern:** How capabilities access data from previous steps
      
      **Implementation:** Use `ContextManager.extract_from_step()` to get required dependencies:
      
      .. code-block:: python
      
         # Get context manager
         context_manager = ContextManager(state)
         
         # Extract required contexts based on execution plan dependencies
         contexts = context_manager.extract_from_step(
             step, state,
             constraints=["TURBINE_DATA", "WEATHER_DATA"],  # What we need
             constraint_mode="hard"                         # Fail if missing
         )
         
         # Access the typed context objects
         turbine_data = contexts[registry.context_types.TURBINE_DATA]
         weather_data = contexts[registry.context_types.WEATHER_DATA]
         
         # Use the data (already typed and validated)
         timestamps = turbine_data.timestamps
         power_outputs = turbine_data.power_outputs

   .. tab-item:: 🔗 Context Coordination

      **Pattern:** How complex capabilities coordinate multiple data sources
      
      **Implementation:** The `turbine_analysis` capability demonstrates multi-source coordination:
      
      .. code-block:: python
      
         # Declared dependencies in registry
         provides = [registry.context_types.ANALYSIS_RESULTS]
         requires = [registry.context_types.TURBINE_DATA, 
                    registry.context_types.WEATHER_DATA, 
                    registry.context_types.TURBINE_KNOWLEDGE]
         
         # Framework automatically ensures all dependencies are available
         # before this capability executes
         contexts = context_manager.extract_from_step(
             step, state,
             constraints=["TURBINE_DATA", "WEATHER_DATA"],
             constraint_mode="hard"
         )
         
         # All three context types are available and type-safe
         turbine_data = contexts[registry.context_types.TURBINE_DATA]    # From step 2
         weather_data = contexts[registry.context_types.WEATHER_DATA]    # From step 3
         # knowledge_data automatically accessible through execution plan  # From step 4

**Key Insight:** The framework's dependency resolution ensures capabilities execute in the correct order and have access to exactly the data they need.

**File Locations:** ``src/turbine_agent/capabilities/``

Step 5: Multi-Component Registry Configuration
----------------------------------------------

**Reference:** Basic registry patterns (``RegistryConfigProvider``, component registration) are covered in :ref:`hello-world-tutorial-registry`.

**What's New Here:** **Specialized configurations** with framework exclusions:

.. code-block:: python

   class WindTurbineRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self) -> RegistryConfig:
           return extend_framework_registry(
               # Register 4 capabilities with complex dependencies
               capabilities=[
                   CapabilityRegistration(
                       name="turbine_analysis",
                       module_path="turbine_agent.capabilities.turbine_analysis",
                       class_name="TurbineAnalysisCapability",
                       description="Analyze turbine performance",
                       provides=["ANALYSIS_RESULTS"],
                       requires=["TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE"]
                   ),
                   # ... 3 other CapabilityRegistration objects
               ],
               
               # Register context classes, data sources, prompt providers
               context_classes=[...],
               data_sources=[...],
               framework_prompt_providers=[...],
               
               # Advanced: Exclude framework Python capability
               exclude_capabilities=["python"]  # Use specialized turbine_analysis instead
           )

**Integration Features:**
- **Framework Exclusions**: Override default Python capability with specialized analysis
- **Complex Dependencies**: Multi-input capabilities requiring coordination
- **Data Source Integration**: Knowledge providers for domain expertise
- **Custom Framework Prompts**: Domain-specific prompt builders for specialized AI behavior

**File Location:** ``src/turbine_agent/registry.py``

Step 6: Custom Framework Prompts
--------------------------------

**What's New Here:** **Domain-specific LLM behavior** through custom prompt builders that override framework defaults.

The framework uses generic prompts by default, but you can replace them with domain-specific instructions. In this wind turbine example, we override the response generation default framework prompt:

.. dropdown:: **Custom Response Generation** - Wind turbine-specific LLM behavior
   :color: info
   :icon: paintbrush

   **The Problem:** Generic framework responses don't understand your domain's terminology, formatting needs, or industry standards.
   
   **The Solution:** Custom prompt builders that inject domain expertise into the LLM's responses.

   .. code-block:: python

      # src/turbine_agent/framework_prompts/response_generation.py
      class WindTurbineResponseGenerationPromptBuilder(DefaultResponseGenerationPromptBuilder):
          
          def get_role_definition(self) -> str:
              return "You are an expert wind turbine performance analyst providing detailed technical analysis and maintenance recommendations."
          
          def _get_guidelines_section(self, info) -> str:
              guidelines = [
                  "ALWAYS present turbine performance data in well-formatted tables for clarity",
                  "Include capacity factor percentages rounded to 1 decimal place for readability", 
                  "Reference specific industry standards from knowledge base when available",
                  "Use proper turbine industry terminology (capacity factor, efficiency ratio, etc.)",
                  "Structure analysis with clear headings: Performance Overview, Rankings, Maintenance Recommendations"
              ]
              return "GUIDELINES:\n" + "\n".join(f"{i+1}. {g}" for i, g in enumerate(guidelines))

   **Registration in Registry:**

   .. code-block:: python

      # In your RegistryConfig
      framework_prompt_providers=[
          FrameworkPromptProviderRegistration(
              application_name="wind_turbine",
              module_path="turbine_agent.framework_prompts",
              prompt_builders={
                  "response_generation": "WindTurbineResponseGenerationPromptBuilder"
              }
          )
      ]

   **Result:** The AI now responds with wind turbine expertise - structured tables, industry terminology, proper formatting, and domain-specific analysis patterns.

**File Locations:** ``src/turbine_agent/framework_prompts/response_generation.py``, ``src/turbine_agent/registry.py``

Integration Patterns Mastered
-----------------------------

**Building on the Hello World foundation**, you now understand **workflow integration patterns**:

✅ **Multi-Capability Orchestration** - 6-step execution plans with dependencies  

✅ **Basic RAG Integration** - Simple knowledge extraction that shows how to connect knowledge sources  

✅ **Human-in-the-Loop Workflows** - Approval systems for sensitive operations  

✅ **Dynamic Python Generation** - LLM planning + Code execution + Human oversight  

✅ **Context Flow Management** - Data flow across multiple capabilities  

✅ **Custom Framework Prompts** - Domain-specific AI behavior through prompt customization  


.. _planning-mode-demonstration:

Interactive Planning Mode Demonstration
---------------------------------------

The Alpha Berkeley Framework's planning mode provides full transparency into multi-step execution plans before they execute. This is especially powerful for complex analysis tasks where you want to understand and approve the approach before execution begins.

.. dropdown:: **The Power of Planning Mode**
   :open:
   :color: primary
   :icon: tools

   In the wind turbine example above, when a user asks: *"Our wind farm has been underperforming lately. Can you analyze the turbine performance over the past 2 weeks, identify which turbines are operating below industry standards, and rank them by efficiency? I need to know which ones require immediate maintenance attention."*, the orchestrator creates a complete execution plan that shows exactly how it will approach this complex task.

   .. tab-set::

      .. tab-item:: 📄 Execution Plan JSON

         The execution plan below shows the exact 6-step approach the orchestrator designed for the wind turbine analysis task. This is the real plan that gets generated and reviewed before execution:

         .. literalinclude:: /_static/resources/execution_plans/wind_turbine_analysis.json
            :language: json
            :caption: Wind Turbine Analysis - Orchestrator Generated Execution Plan
            :linenos:

         **Key Planning Features Demonstrated:**

         📊 **Dependency Visualization**: Notice how steps 2-3 depend on step 1's TIME_RANGE output (lines 23, 35), and step 5 requires outputs from steps 2, 3, and 4 (lines 45-51).

         🔗 **Context Flow Management**: The orchestrator ensures data flows correctly: TIME_RANGE → TURBINE_DATA + WEATHER_DATA + TURBINE_KNOWLEDGE → ANALYSIS_RESULTS → Response.

         🎯 **Task Decomposition**: A complex request is automatically broken into 6 logical, manageable steps that build upon each other.

         🛡️ **Human Oversight**: In the actual Open Web UI, this plan would require approval before execution, allowing you to review and modify the approach.

         **Plan Structure Explanation:**

         - **Metadata** (lines 2-7): Contains both the extracted task, original user query, creation timestamp, and plan version
         - **Steps Array**: Each step defines a specific capability execution with clear objectives
         - **Dependencies**: The ``inputs`` field shows which previous steps' outputs this step requires
         - **Context Keys**: Unique identifiers for data that flows between steps
         - **Success Criteria**: Clear definitions of what constitutes successful completion

         **In the Open Web UI Interface:**

         When you use planning mode (``/planning`` command), you'll see this exact plan structure with additional functionality:

         - **Edit Individual Steps**: Modify task objectives, success criteria, or dependencies
         - **Add/Remove Steps**: Insert new capabilities or remove unnecessary steps
         - **Approve/Reject**: Decide whether to execute the plan as-is or request modifications
         - **Real-time Validation**: The editor validates dependencies and highlights potential issues

         This transparency ensures you understand exactly what your agent will do before it starts, providing confidence in complex multi-step operations.

         **Production Benefits:**

         - **Auditability**: Every execution has a clear, reviewable plan
         - **Optimization**: Identify inefficient step sequences before execution
         - **Learning**: Understand how the orchestrator approaches different types of problems
         - **Control**: Modify the approach when domain expertise suggests better alternatives

      .. tab-item:: 🖥️ Execution Plan CLI Example

         **Planning Mode in Action**

         Here's what the actual CLI interaction looks like when using planning mode:

         .. code-block:: text

            👤 You: /planning Our wind farm has been underperforming lately. Can you analyze the turbine performance over the past 2 weeks, identify which turbines are operating below industry standards, and rank them by efficiency? I need to know which ones require immediate maintenance attention.

            🔄 Processing: /planning Our wind farm has been underperforming lately...
            ✅ Processed commands: ['planning']
            🔄 Extracting actionable task from conversation
            🔄 Analyzing task requirements...
            🔄 Generating execution plan...
            🔄 Requesting plan approval...

            ⚠️ **HUMAN APPROVAL REQUIRED** ⚠️

            **Planned Steps (6 total):**
            **Step 1:** Parse "past 2 weeks" timeframe → TIME_RANGE
            **Step 2:** Retrieve historical turbine data → TURBINE_DATA  
            **Step 3:** Retrieve weather data for correlation → WEATHER_DATA
            **Step 4:** Get industry performance benchmarks → TURBINE_KNOWLEDGE
            **Step 5:** Analyze performance against standards → ANALYSIS_RESULTS
            **Step 6:** Present findings and maintenance recommendations → Response

            **To proceed, respond with:**
            - **`yes`** to approve and execute the plan
            - **`edit`** to modify the plan in the interactive editor
            - **`no`** to cancel this operation

            👤 You: 

         The execution plan editor provides unprecedented transparency into agentic system behavior, making complex multi-step operations both understandable and controllable. This is especially valuable in production environments where understanding the approach is as important as getting results.
