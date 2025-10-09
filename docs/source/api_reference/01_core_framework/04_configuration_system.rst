====================
Configuration System
====================

Configuration system with YAML loading, environment resolution, and seamless LangGraph integration.

.. currentmodule:: configs.config

Core Classes
============

ConfigBuilder
-------------

.. autoclass:: ConfigBuilder
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   
   Main configuration builder with YAML loading, environment resolution, and LangGraph integration.

Primary Access Functions
========================

.. autofunction:: get_config_value

.. autofunction:: get_full_configuration

.. autofunction:: get_agent_dir

Specialized Configuration Functions
===================================

Model and Provider Access
-------------------------

.. autofunction:: get_model_config

.. autofunction:: get_provider_config

.. dropdown:: Need Support for Additional Providers?
    :color: info
    :icon: people   

    The framework's provider system is designed for extensibility. Many research institutions and national laboratories now operate their own AI/LM services similar to LBNL's CBorg system. We're happy to work with you to implement native support for your institution's internal AI services or other providers you need. Contact us to discuss integration requirements.

Service Configuration
---------------------

.. autofunction:: get_framework_service_config

.. autofunction:: get_application_service_config

Runtime Information
-------------------

.. autofunction:: get_session_info

.. autofunction:: get_interface_context

.. autofunction:: get_current_application

.. autofunction:: get_execution_limits

.. autofunction:: get_agent_control_defaults

Development Utilities
---------------------

.. autofunction:: get_logging_color

.. autofunction:: get_pipeline_config

Internal Implementation
=======================

.. autofunction:: _get_config

.. autofunction:: _get_configurable

.. seealso::

   :class:`framework.state.StateManager`
       State management utilities that use configuration
   
   :doc:`02_state_and_context`
       State and context systems that depend on configuration
   
   :doc:`../../developer-guides/03_core-framework-systems/04_prompt-customization`
       Complete guide to configuration management patterns