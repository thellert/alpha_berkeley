==========================
Configuration Architecture
==========================

**What you'll learn:** How the framework's self-contained configuration system works, configuration templates, and environment variable integration.

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Self-contained configuration approach
   - Configuration templates and project initialization
   - Environment variable integration
   - Viewing framework defaults with ``framework export-config``
   - Configuration organization and best practices

   **Prerequisites:** Basic `YAML <https://yaml.org>`__ knowledge
   
   **Time Investment:** 10 minutes

Self-Contained Configuration
============================

The framework uses a **single, self-contained configuration file** approach. Each project has one ``config.yml`` file at the project root that contains all settings - framework and application-specific.

.. code-block:: text

   my-project/
   ├── config.yml              ← Complete, self-contained configuration
   ├── .env                    ← Environment variables (secrets, dynamic paths)
   └── src/
       └── my_app/
           └── registry.py     ← Application code registry

**Design Philosophy:**

- **Transparency:** All settings visible in one place
- **Simplicity:** No imports, no merging, no hidden defaults
- **Self-documenting:** Every option is explicit and can be customized
- **Version control friendly:** Configuration evolves with your project

Configuration Files
===================

Project Configuration
---------------------

**Location:** ``config.yml`` (project root)

**Purpose:** Complete project configuration - all settings in one place

.. code-block:: yaml

   # ============================================================
   # My Project Configuration
   # ============================================================
   
   build_dir: ./build
   project_root: /path/to/my-project
   registry_path: ./src/my_app/registry.py
   
   # Model configuration - 8 specialized models
   models:
     orchestrator:
       provider: cborg
       model_id: anthropic/claude-sonnet
     response:
       provider: cborg
       model_id: google/gemini-flash
     # ... other models ...
   
   # Service deployment control
   deployed_services:
     - jupyter
     - open_webui
     - pipelines
   
   # Safety controls
   approval:
     global_mode: "selective"
     capabilities:
       python_execution:
         enabled: true
         mode: "epics_writes"
   
   execution_control:
     epics:
       writes_enabled: false
     limits:
       max_step_retries: 3
       graph_recursion_limit: 100
       max_concurrent_classifications: 5
   
   # API providers
   api:
     providers:
       cborg:
         api_key: ${CBORG_API_KEY}
         base_url: https://api.cborg.lbl.gov/v1
   
   # And many more sections...

Configuration Template
----------------------

**Location:** ``src/framework/templates/project/config.yml.j2``

**Purpose:** Template used by ``framework init`` to create new projects

When you run ``framework init my-project``, the template is rendered with your project-specific values to create a complete, self-contained ``config.yml``.

**View the template:**

.. code-block:: bash

   # See what a default config looks like
   framework export-config
   
   # Save to file for reference
   framework export-config --output reference.yml

Configuration Sections
======================

A complete ``config.yml`` includes these major sections:

**Project Metadata:**
   - ``build_dir`` - Where to generate deployment files
   - ``project_root`` - Absolute path to project
   - ``registry_path`` - Path to application registry

**Model Configuration:**
   - ``models`` - 8 specialized AI models for different roles
   - Each model specifies provider and model_id

**Service Configuration:**
   - ``services`` - Jupyter, Open WebUI, Pipelines services
   - ``deployed_services`` - Which services to deploy

**Safety Controls:**
   - ``approval`` - Human approval workflows
   - ``execution_control`` - Safety limits and constraints

**Execution Settings:**
   - ``execution`` - Python execution method and environment
   - ``python_executor`` - Retry limits and timeouts

**Development:**
   - ``development`` - Debug settings, prompt saving
   - ``logging`` - Log levels and colors

**API Providers:**
   - ``api.providers`` - API keys and endpoints

See :doc:`../../api_reference/01_core_framework/04_configuration_system` for complete reference.

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

Creating New Projects
=====================

**Initialize with template:**

.. code-block:: bash

   # Create new project from template
   framework init my-project
   
   # This creates:
   # my-project/
   # ├── config.yml           ← Complete, self-contained config
   # ├── .env.example         ← Example environment variables
   # ├── src/my_project/      ← Your application code
   # └── services/            ← Service definitions

**Customize your config.yml:**

1. Update ``project_root`` with absolute path
2. Configure API providers in ``api.providers``
3. Choose models for each role in ``models``
4. Set safety controls in ``approval`` and ``execution_control``
5. Create ``.env`` file with secrets

**Reference existing projects:**

View complete working configurations in the ``_legacy_applications/`` directory for examples of different configuration patterns.

.. seealso::

   :doc:`../../api_reference/01_core_framework/04_configuration_system`
       Complete reference for all configuration sections
   
   :doc:`03_registry-and-discovery`
       How configuration integrates with the registry
   
   :doc:`../05_production-systems/05_container-and-deployment`
       Container deployment patterns
