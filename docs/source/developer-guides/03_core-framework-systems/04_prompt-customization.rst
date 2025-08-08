====================
Prompt Customization
====================

This guide covers customizing framework prompts for domain-specific applications. The framework's prompt management system enables clean separation between generic framework functionality and domain-specific prompt customization through sophisticated dependency injection patterns.

Architecture Overview
=====================

The prompt system uses a provider architecture where applications register custom prompt implementations that the framework components request through dependency injection. This enables applications to provide domain-specific prompts while the framework remains generic.

Applications can override any prompt builder with domain-specific implementations while maintaining full compatibility with all framework components.

**Key Benefits:**

- **Domain Agnostic**: Framework remains generic while supporting specialized prompts
- **No Circular Dependencies**: Clean separation through dependency injection
- **Flexible Composition**: Modular prompt building with optional components
- **Development Support**: Integrated debugging and prompt inspection tools

Quick Start: Custom Prompt Provider
===================================

Here's a minimal example of creating a custom prompt provider:

.. code-block:: python

   from framework.prompts import FrameworkPromptBuilder, FrameworkPromptProvider
   from framework.prompts.defaults import DefaultPromptProvider
   
   class MyDomainPromptBuilder(FrameworkPromptBuilder):
       def get_role_definition(self) -> str:
           return "You are a domain-specific expert system."
       
       def get_instructions(self) -> str:
           return "Provide analysis using domain-specific terminology."
   
   class MyAppPromptProvider(FrameworkPromptProvider):
       def __init__(self):
           # Use custom builders for key prompts
           self._orchestrator = MyDomainPromptBuilder()
           
           # Use framework defaults for others
           self._defaults = DefaultPromptProvider()
       
       def get_orchestrator_prompt_builder(self):
           return self._orchestrator
       
       def get_classification_prompt_builder(self):
           # Delegate to framework default
           return self._defaults.get_classification_prompt_builder()
       
       # ... implement other required methods

Development and Debugging
=========================

All prompts automatically integrate with the framework's debug system for development visibility. The system provides comprehensive debugging capabilities through both console output and file persistence, making it invaluable for prompt development, troubleshooting, and optimization.

Configuration Options
---------------------

The debug system is controlled through the ``development.prompts`` configuration section in your ``config.yml`` file:

.. code-block:: yaml

   development:
     prompts:
       # Console output with detailed formatting and separators
       show_all: true
       
       # File output to prompts directory for inspection
       print_all: true
       
       # File naming strategy
       latest_only: false  # true: latest.md files, false: timestamped files

Console Output
--------------

When ``show_all: true`` is set, all generated prompts are displayed in the console with clear visual separators and metadata:

.. code-block:: text

   ================================================================================
   🔍 DEBUG PROMPT: orchestrator_system (DefaultOrchestratorPromptBuilder)
   ================================================================================
   You are an intelligent orchestration agent for the ALS Expert system...
   ================================================================================

File Persistence
----------------

When ``print_all: true`` is enabled, prompts are automatically saved to the configured ``prompts_dir`` with rich metadata headers:

- **Timestamped files** (``latest_only: false``): Each prompt generation creates a new file with timestamp
  
  - Format: ``{name}_{YYYYMMDD_HHMMSS}.md``
  - Use case: Track prompt evolution over time, compare versions, debug prompt changes
  - Example: ``orchestrator_system_20241215_143022.md``

- **Latest files** (``latest_only: true``): Overwrites the previous version, keeping only current state
  
  - Format: ``{name}_latest.md``  
  - Use case: Always see current prompt without file clutter
  - Example: ``orchestrator_system_latest.md``

Metadata Headers
----------------

All saved prompt files include comprehensive metadata for traceability:

.. code-block:: markdown

   # PROMPT METADATA
   # Generated: 2024-12-15 14:30:22
   # Name: orchestrator_system
   # Builder: DefaultOrchestratorPromptBuilder
   # File: /path/to/prompts/orchestrator_system_latest.md
   # Latest Only: true

Provider Interface Implementation
=================================

Applications implement the FrameworkPromptProvider interface to provide domain-specific prompts to framework infrastructure. All methods are required and must return FrameworkPromptBuilder instances.

.. note::
   Applications typically inherit from DefaultPromptProvider and override only the prompt builders they want to customize, using framework defaults for the rest.

Complete Provider Interface
---------------------------

.. tab-set::

   .. tab-item:: Orchestrator

      Controls execution planning and coordination:

      .. code-block:: python

         def get_orchestrator_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for orchestration operations.
             
             Used by the orchestrator node to create execution plans
             and coordinate capability execution sequences.
             """

   .. tab-item:: Task Extraction

      Handles task parsing and structuring:

      .. code-block:: python

         def get_task_extraction_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for task extraction operations.
             
             Used by task extraction node to parse user requests
             into structured, actionable tasks.
             """

   .. tab-item:: Classification

      Manages request classification and routing:

      .. code-block:: python

         def get_classification_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for classification operations.
             
             Used by classification node to determine which capabilities
             should handle specific user requests.
             """

   .. tab-item:: Response Generation

      Controls final response formatting:

      .. code-block:: python

         def get_response_generation_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for response generation.
             
             Used by response generation to format final answers
             using capability results and conversation context.
             """

   .. tab-item:: Error Analysis

      Handles error classification and recovery:

      .. code-block:: python

         def get_error_analysis_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for error analysis operations.
             
             Used by error handling system to classify errors
             and determine recovery strategies.
             """

   .. tab-item:: Clarification

      Manages clarification requests:

      .. code-block:: python

         def get_clarification_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for clarification requests.
             
             Used when the system needs additional information
             from users to complete tasks.
             """

   .. tab-item:: Memory Extraction

      Controls memory operations:

      .. code-block:: python

         def get_memory_extraction_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for memory extraction operations.
             
             Used by memory capability to extract and store
             relevant information from conversations.
             """

   .. tab-item:: Time Range Parsing

      Handles temporal query parsing:

      .. code-block:: python

         def get_time_range_parsing_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for time range parsing.
             
             Used by time parsing capability to understand
             temporal references in user queries.
             """

   .. tab-item:: Python

      Controls code generation and execution:

      .. code-block:: python

         def get_python_prompt_builder(self) -> FrameworkPromptBuilder:
             """
             Return prompt builder for Python operations.
             
             Used by Python capability for code generation,
             analysis, and execution guidance.
             """

Default Builder Reference
=========================

The framework provides individual default prompt builder implementations organized by framework node. Each node has its own specialized prompt builder that applications can use directly or extend.

.. dropdown:: View Default Implementation Examples
   :animate: fade-in-slide-down

   .. tab-set::

      .. tab-item:: Orchestrator
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/orchestrator.py
            :language: python

      .. tab-item:: Task Extraction
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/task_extraction.py
            :language: python

      .. tab-item:: Classification
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/classification.py
            :language: python

      .. tab-item:: Response Generation
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/response_generation.py
            :language: python

      .. tab-item:: Error Analysis
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/error_analysis.py
            :language: python

      .. tab-item:: Clarification
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/clarification.py
            :language: python

      .. tab-item:: Memory Extraction
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/memory_extraction.py
            :language: python

      .. tab-item:: Time Range Parsing
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/time_range_parsing.py
            :language: python

      .. tab-item:: Python
      
         .. literalinclude:: ../../../../src/framework/prompts/defaults/python.py
            :language: python

Registration Patterns
=====================

Applications register their prompt providers during initialization using the registry system:

Basic Registration
------------------

.. code-block:: python

   from framework.prompts.loader import register_framework_prompt_provider
   from applications.myapp.framework_prompts import MyAppPromptProvider
   
   # During application initialization
   register_framework_prompt_provider("myapp", MyAppPromptProvider())

Registry-Based Registration
---------------------------

For automatic discovery, include prompt providers in your application registry:

.. code-block:: python

   # In applications/myapp/registry.py
   from framework.registry import RegistryConfig, FrameworkPromptProviderRegistration
   
   class MyAppRegistryProvider(RegistryConfigProvider):
       def get_registry_config(self) -> RegistryConfig:
           return RegistryConfig(
               # ... other registrations
               framework_prompt_providers=[
                   FrameworkPromptProviderRegistration(
                       application_name="myapp",
                       module_path="applications.myapp.framework_prompts",
                       class_name="MyAppPromptProvider",
                       description="Domain-specific prompt provider",
                       prompt_builders={
                           "orchestrator": "MyOrchestratorPromptBuilder",
                           "classification": "MyClassificationPromptBuilder"
                           # Others use framework defaults
                       }
                   )
               ]
           )

Advanced Patterns
=================

Multi-Application Deployments
-----------------------------

For deployments with multiple applications, you can access specific providers:

.. code-block:: python

   from framework.prompts import get_framework_prompts
   
   # Access specific application's prompts
   als_provider = get_framework_prompts("als_expert")
   wind_provider = get_framework_prompts("wind_turbine")
   
   # Use default provider (first registered)
   default_provider = get_framework_prompts()

Selective Override Pattern
--------------------------

Override only specific builders while inheriting others:

.. code-block:: python

   from framework.prompts.defaults import DefaultPromptProvider
   
   class MyAppPromptProvider(DefaultPromptProvider):
       def __init__(self):
           super().__init__()
           # Override specific builders
           self._custom_orchestrator = MyOrchestratorPromptBuilder()
       
       def get_orchestrator_prompt_builder(self):
           return self._custom_orchestrator
       
       # All other methods inherited from DefaultPromptProvider

Testing Strategies
------------------

Test your custom prompts in isolation:

.. code-block:: python

   def test_custom_orchestrator_prompt():
       builder = MyOrchestratorPromptBuilder()
       
       # Test role definition
       role = builder.get_role_definition()
       assert "domain-specific" in role.lower()
       
       # Test full prompt generation
       system_prompt = builder.get_system_instructions(
           capabilities=["test_capability"],
           context_manager=mock_context
       )
       assert len(system_prompt) > 0

.. seealso::

   :doc:`../../api_reference/01_core_framework/05_prompt_management`
       API reference for prompt system classes and functions
   
   :doc:`03_registry-and-discovery`
       Component registration and discovery patterns
   
   :doc:`../01_understanding-the-framework/02_convention-over-configuration`
       Framework conventions and patterns