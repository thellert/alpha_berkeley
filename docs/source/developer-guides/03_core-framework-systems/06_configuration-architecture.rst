========================
Configuration Architecture
========================

**What you'll learn:** How the three-tier configuration system works, how settings merge and override, and where to place different types of configuration.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Three-tier hierarchy: root → framework → application
   - Import mechanism and configuration merging
   - Override patterns and precedence rules
   - Environment variable integration
   - When to use each configuration layer

   **Prerequisites:** Basic `YAML <https://yaml.org>`__ knowledge
   
   **Time Investment:** 15 minutes

Three-Tier Architecture
=======================

The framework uses three configuration layers that load and merge in sequence:

.. code-block:: text

   config.yml (root)                    ← Operator controls, final authority
       
        ↓ imports
  
   src/framework/config.yml             ← Framework defaults
  
        ↓ merged with
  
   src/applications/{app}/config.yml    ← Application-specific settings

**Loading Process:**

1. Load framework configuration
2. Load each enabled application's configuration
3. Merge applications with framework (deep merge for most sections)
4. Apply root configuration as final overrides
5. Resolve environment variables (``${VAR_NAME}``)

Configuration Files
===================

Root Configuration
------------------

**Location:** ``config.yml`` (project root)

**Purpose:** Deployment control and operator overrides

.. code-block:: yaml

   # Import framework
   import: src/framework/config.yml
   
   # Enable applications
   applications:
     - hello_world_weather
   
   # Operator controls
   approval:
     global_mode: "selective"
     capabilities:
       python_execution:
         enabled: true
         mode: "epics_writes"
   
   execution_control:
     epics:
       writes_enabled: false
   
   # Service deployment control
   deployed_services:
     - framework.jupyter
     - framework.pipelines
   
   # API providers
   api:
     providers:
       anthropic:
         api_key: ${ANTHROPIC_API_KEY}
         base_url: https://api.anthropic.com

Framework Configuration
-----------------------

**Location:** ``src/framework/config.yml``

**Purpose:** Framework defaults and core infrastructure

.. code-block:: yaml

   framework:
     services:
       jupyter:
         path: ./services/framework/jupyter
         port_host: 8088
     
     models:
       orchestrator:
         provider: cborg
         model_id: anthropic/claude-sonnet
       response:
         provider: cborg
         model_id: google/gemini-flash
   
   logging:
     framework:
       logging_colors:
         orchestrator: "cyan"
         classifier: "light_salmon1"

**Rarely modified directly** - applications override instead.

Application Configuration
--------------------------

**Location:** ``src/applications/{app}/config.yml``

**Purpose:** Application-specific settings (models, services, pipeline configuration)

.. code-block:: yaml

   # Application models
   models:
     data_analysis:
       provider: cborg
       model_id: anthropic/claude-sonnet
   
   # Application services
   services:
     mongo:
       name: mongo
       path: ./services/applications/als_assistant/mongo
       port_host: 27017
   
   # Pipeline configuration
   pipeline:
     name: "ALS Assistant"
     startup_hooks:
       - "initialization.setup_nltk_resources"
   
   # Logging colors
   logging:
     logging_colors:
       data_analysis: "deep_sky_blue1"

Merging and Precedence
=======================

Precedence Order
----------------

When the same key exists at multiple levels:

.. code-block:: text

   1. Root config.yml          ← Always wins
   2. Application config.yml   ← Overrides framework
   3. Framework config.yml     ← Provides defaults

Deep Merge Sections
-------------------

These sections **combine** values from all layers:

- ``api.providers`` - All providers available
- ``models`` - Framework + application models
- ``services`` - Framework + application services
- ``logging.logging_colors`` - All colors combined

.. code-block:: yaml

   # Framework
   models:
     orchestrator:
       provider: cborg
   
   # Application
   models:
     data_analysis:
       provider: cborg
   
   # Result: BOTH models available
   models:
     orchestrator: {...}
     data_analysis: {...}

Override Sections
-----------------

These sections **replace entirely** - highest level wins:

- ``deployed_services`` - Root config controls deployment
- ``approval`` - Root config sets policy
- ``execution_control`` - Root config sets limits

.. code-block:: yaml

   # Framework
   deployed_services:
     - framework.jupyter
     - framework.pipelines
   
   # Root
   deployed_services:
     - framework.jupyter
   
   # Result: ONLY jupyter deployed (pipelines excluded)

Environment Variables
=====================

Use ``${VAR_NAME}`` syntax with optional defaults:

.. code-block:: yaml

   # Required variable (error if undefined)
   project_root: ${PROJECT_ROOT}
   
   # With default value
   system:
     timezone: ${TZ:-America/Los_Angeles}
   
   # API keys (always use env vars)
   api:
     providers:
       anthropic:
         api_key: ${ANTHROPIC_API_KEY}

**.env File:**

.. code-block:: bash

   # .env (project root)
   PROJECT_ROOT=/home/user/alpha_berkeley
   ANTHROPIC_API_KEY=sk-ant-...
   LOCAL_PYTHON_VENV=/home/user/venv/bin/python

**Security:** Never commit ``.env`` to version control. Keep it in ``.gitignore``.

Working Examples
================

The repository contains complete working configurations:

**Root Configuration:** `config.yml <https://github.com/thellert/alpha_berkeley/blob/main/config.yml>`_
   Complete deployment configuration with operator controls

**Framework Configuration:** `src/framework/config.yml <https://github.com/thellert/alpha_berkeley/blob/main/src/framework/config.yml>`_
   Framework defaults and service definitions

**Application Examples:**
   - `ALS Assistant <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/als_assistant/config.yml>`_ - Production application
   - `Hello World Weather <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/hello_world_weather/config.yml>`_ - Minimal application

Use these as templates for your own configurations.

Next Steps
==========

- :doc:`../../api_reference/01_core_framework/04_configuration_system` - Complete reference for all configuration sections
- :doc:`03_registry-and-discovery` - How configuration integrates with the registry
- :doc:`../05_production-systems/05_container-and-deployment` - Container deployment patterns
