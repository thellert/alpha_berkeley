=============
Prompt System
=============

Framework prompt system with dependency injection for domain-specific prompt customization.

.. currentmodule:: framework.prompts

Core Prompt Builder Interface
=============================

.. autoclass:: FrameworkPromptBuilder
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   .. rubric:: Required Abstract Methods

   .. autosummary::
      :nosignatures:
      
      ~FrameworkPromptBuilder.get_role_definition
      ~FrameworkPromptBuilder.get_instructions

   .. rubric:: Optional Composition Methods

   .. autosummary::
      :nosignatures:
      
      ~FrameworkPromptBuilder.get_task_definition
      ~FrameworkPromptBuilder.get_dynamic_context
      ~FrameworkPromptBuilder.get_examples

   .. rubric:: Prompt Assembly Methods

   .. autosummary::
      :nosignatures:
      
      ~FrameworkPromptBuilder.get_system_instructions
      ~FrameworkPromptBuilder.debug_print_prompt
      ~FrameworkPromptBuilder.format_examples

Framework Access
================

.. autofunction:: get_framework_prompts

Application Provider Interface
==============================

.. currentmodule:: framework.prompts.loader

.. autoclass:: FrameworkPromptProvider
   :members:
   :undoc-members:
   :show-inheritance:

Provider Registry System
========================

.. autoclass:: FrameworkPromptLoader
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Provider Registration
=====================

.. autofunction:: register_framework_prompt_provider

Framework Default Implementations
=================================

.. currentmodule:: framework.prompts.defaults

.. autoclass:: DefaultPromptProvider
   :members:
   :undoc-members:
   :show-inheritance:

.. seealso::

   :doc:`03_registry_system`
       Registry system for component management
   
   :doc:`../../developer-guides/03_core-framework-systems/04_prompt-customization`
       Complete guide for customizing and developing prompts