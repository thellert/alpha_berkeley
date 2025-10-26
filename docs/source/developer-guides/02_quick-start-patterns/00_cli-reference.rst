=============
CLI Reference
=============

**What you'll learn:** Complete reference for all Alpha Berkeley Framework CLI commands

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Using ``framework`` CLI for all framework operations
   - Creating projects with ``framework init``
   - Managing deployments with ``framework deploy``
   - Running interactive sessions with ``framework chat``
   - Exporting configuration with ``framework export-config``

   **Prerequisites:** Framework installed (``pip install framework``)
   
   **Time Investment:** 10 minutes for quick reference

Overview
========

The Alpha Berkeley Framework provides a unified CLI for all framework operations. All commands are accessed through the ``framework`` command with subcommands for specific operations.

.. admonition:: New in v0.7.0: Unified CLI
   :class: version-070-change

   The framework CLI provides a modern, unified interface for all operations. Previous Python script-based workflows have been replaced with convenient CLI commands.

**Quick Reference:**

.. code-block:: bash

   framework --version          # Show framework version
   framework --help             # Show available commands
   framework init PROJECT       # Create new project
   framework deploy COMMAND     # Manage services
   framework chat               # Start interactive chat
   framework export-config      # Export configuration

Global Options
==============

These options work with all ``framework`` commands.

``--version``
-------------

Show framework version and exit.

.. code-block:: bash

   framework --version

Output:

.. code-block:: text

   Alpha Berkeley Framework version 0.7.0

``--help``
----------

Show help message for any command.

.. code-block:: bash

   framework --help
   framework init --help
   framework deploy --help
   framework chat --help
   framework export-config --help

Commands
========

framework init
==============

Create a new project from a template.

Syntax
------

.. code-block:: bash

   framework init [OPTIONS] PROJECT_NAME

Arguments
---------

``PROJECT_NAME``
   Name of the project directory to create. Will be created in the current directory.

Options
-------

``--template <name>``
   Template to use for project initialization. Available templates:
   
   - ``minimal`` - Basic skeleton for custom development
   - ``hello_world_weather`` - Simple weather agent (recommended for learning)
   - ``wind_turbine`` - Advanced multi-capability agent

   Default: ``minimal``

``--registry-style <style>``
   Registry implementation style:
   
   - ``compact`` - Use helper functions (5-10 lines, recommended)
   - ``explicit`` - Full registry implementation (verbose, for learning)

   Default: ``compact``

Examples
--------

**Create minimal project:**

.. code-block:: bash

   framework init my-agent

**Create from hello_world_weather template:**

.. code-block:: bash

   framework init weather-demo --template hello_world_weather

**Create with explicit registry style:**

.. code-block:: bash

   framework init my-agent --template minimal --registry-style explicit

**Create advanced agent:**

.. code-block:: bash

   framework init turbine-monitor --template wind_turbine

Generated Structure
-------------------

The ``framework init`` command creates a complete, self-contained project:

.. code-block:: text

   my-agent/
   ├── src/
   │   └── my_agent/           # Application code
   │       ├── __init__.py
   │       ├── registry.py     # Component registration
   │       ├── context_classes.py
   │       └── capabilities/   # Agent capabilities
   ├── services/               # Container services
   │   ├── jupyter/           # Development environment
   │   ├── open-webui/        # Web interface
   │   └── pipelines/         # Processing pipeline
   ├── config.yml             # Complete configuration
   ├── .env.example           # Environment template
   └── README.md              # Project documentation

framework deploy
================

Manage containerized services (Jupyter, OpenWebUI, Pipelines).

Syntax
------

.. code-block:: bash

   framework deploy COMMAND [OPTIONS]

Commands
--------

``up``
   Start services defined in ``config.yml``.

   Options:
      ``--detached`` - Run services in background

   Examples:
      .. code-block:: bash

         framework deploy up              # Start in foreground
         framework deploy up --detached   # Start in background

``down``
   Stop all running services.

   Example:
      .. code-block:: bash

         framework deploy down

``restart``
   Restart all services.

   Example:
      .. code-block:: bash

         framework deploy restart

``status``
   Show status of deployed services.

   Example:
      .. code-block:: bash

         framework deploy status

``clean``
   Stop services and remove containers and volumes.

   Example:
      .. code-block:: bash

         framework deploy clean

``rebuild``
   Rebuild containers from scratch (useful after Dockerfile changes).

   Example:
      .. code-block:: bash

         framework deploy rebuild

Configuration
-------------

Services are configured in ``config.yml`` under ``deployed_services``:

.. code-block:: yaml

   deployed_services:
     - framework.jupyter        # Jupyter development environment
     - framework.open-webui     # Web chat interface
     - framework.pipelines      # Processing pipeline

Workflow
--------

**Development workflow:**

.. code-block:: bash

   # Start services in foreground to monitor logs
   framework deploy up
   
   # When done, stop with Ctrl+C or:
   framework deploy down

**Production workflow:**

.. code-block:: bash

   # Start services in background
   framework deploy up --detached
   
   # Check status
   framework deploy status
   
   # View logs with podman
   podman logs <container_name>
   
   # Stop when needed
   framework deploy down

Service Access
--------------

Once deployed, services are available at:

- **OpenWebUI**: http://localhost:8080
- **Jupyter (read-only)**: http://localhost:8088
- **Jupyter (write)**: http://localhost:8089
- **Pipelines**: http://localhost:9099

framework chat
==============

Start an interactive CLI conversation interface with your agent.

Syntax
------

.. code-block:: bash

   framework chat [OPTIONS]

Options
-------

``--config PATH``
   Path to configuration file.
   
   Default: ``config.yml``

Example
-------

.. code-block:: bash

   # Start chat with default config
   framework chat
   
   # Use custom config
   framework chat --config my-config.yml

Usage
-----

The chat interface provides an interactive session with your agent:

.. code-block:: text

   Agent Configuration loaded successfully.
   Registry initialized with 25 capabilities
   ⚡ Use slash commands (/) for quick actions - try /help
   
   You: What's the weather in San Francisco?
   
   Agent: [Processing request...]
   The current weather in San Francisco is 18°C with partly cloudy conditions.

Slash Commands
--------------

The CLI supports slash commands for agent control and interface operations:

**Agent Control Commands:**

.. code-block:: bash

   /planning:on          # Enable planning mode
   /planning:off         # Disable planning mode
   /approval:enabled     # Enable approval workflows
   /approval:disabled    # Disable approval workflows
   /approval:selective   # Enable selective approval

**Performance Commands:**

.. code-block:: bash

   /task:off            # Bypass task extraction
   /caps:off            # Bypass capability selection

**CLI Commands:**

.. code-block:: bash

   /help                # Show available commands
   /help <command>      # Show help for specific command
   /exit                # Exit the chat session
   /clear               # Clear the screen

.. seealso::
   :doc:`../../api_reference/01_core_framework/06_command_system`
       Complete API reference for the centralized command system

Prerequisites
-------------

Before using ``framework chat``:

1. Services must be deployed: ``framework deploy up --detached``
2. Configuration must be valid: ``config.yml`` with proper model settings
3. API keys must be set: ``.env`` file with required credentials

framework export-config
=======================

Export the framework's default configuration for reference.

Syntax
------

.. code-block:: bash

   framework export-config [OPTIONS]

Options
-------

``--output PATH``
   Save configuration to file instead of printing to console.

Examples
--------

**View configuration:**

.. code-block:: bash

   framework export-config

**Save to file:**

.. code-block:: bash

   framework export-config --output framework-defaults.yml

**Use as reference when customizing:**

.. code-block:: bash

   # Export defaults
   framework export-config --output reference.yml
   
   # Compare with your config
   diff reference.yml config.yml

Use Cases
---------

1. **Discover available options** - See all configuration fields and their defaults
2. **Reference template** - Use as starting point for custom configurations
3. **Troubleshooting** - Compare your config with framework defaults
4. **Documentation** - Understand configuration structure

Configuration Structure
-----------------------

The exported configuration includes:

- **Models**: LLM provider configurations (orchestrator, classifier, code generator)
- **Services**: Jupyter, OpenWebUI, Pipelines settings
- **Execution Control**: Timeouts, retry policies, safety limits
- **File Paths**: Directory structures and artifact locations
- **Logging**: Log levels and output settings


Environment Variables
=====================

The framework uses environment variables for API keys, paths, and deployment-specific configuration.

For a **complete list of all supported environment variables** with descriptions and examples, see the :ref:`Environment Variables section <environment-variables>` in the Installation Guide.

**Quick Reference:**

.. code-block:: bash

   # Required
   PROJECT_ROOT=/path/to/your/project
   OPENAI_API_KEY=sk-...          # Or ANTHROPIC_API_KEY, GOOGLE_API_KEY, CBORG_API_KEY
   
   # Optional
   LOCAL_PYTHON_VENV=/path/to/venv
   TZ=America/Los_Angeles
   CONFIG_FILE=custom-config.yml
   
   # Proxy settings (if needed)
   HTTP_PROXY=http://proxy:8080
   NO_PROXY=localhost,127.0.0.1

Common Workflows
================

Complete Project Setup
----------------------

.. code-block:: bash

   # 1. Install framework
   pip install framework
   
   # 2. Create project
   framework init weather-agent --template hello_world_weather
   cd weather-agent
   
   # 3. Configure environment
   cp .env.example .env
   # Edit .env with your API keys
   
   # 4. Update config (optional)
   # Edit config.yml as needed
   
   # 5. Deploy services
   framework deploy up --detached
   
   # 6. Start chat
   framework chat

Development Workflow
--------------------

.. code-block:: bash

   # Start services for development
   framework deploy up
   
   # In another terminal, make changes to your code
   # Test with chat interface
   framework chat
   
   # Rebuild containers if needed
   framework deploy rebuild
   
   # Clean up
   framework deploy clean

Configuration Reference
-----------------------

.. code-block:: bash

   # View framework defaults
   framework export-config
   
   # Export to file for reference
   framework export-config --output defaults.yml
   
   # Create new project and compare configs
   framework init test-project
   diff defaults.yml test-project/config.yml

Troubleshooting
===============

Command Not Found
-----------------

If ``framework`` command is not found:

.. code-block:: bash

   # Verify installation
   pip show framework
   
   # Reinstall if needed
   pip install --upgrade framework
   
   # Check pip bin directory is in PATH
   python -m pip show framework

Services Won't Start
--------------------

.. code-block:: bash

   # Check podman is running
   podman --version
   podman ps
   
   # Check for port conflicts
   lsof -i :8080
   lsof -i :9099
   
   # Try starting services in foreground to see errors
   framework deploy up

Configuration Errors
--------------------

.. code-block:: bash

   # Validate against framework defaults
   framework export-config --output defaults.yml
   
   # Check your config syntax
   cat config.yml
   
   # Ensure environment variables are set
   cat .env

Chat Not Responding
-------------------

.. code-block:: bash

   # Verify services are running
   framework deploy status
   podman ps
   
   # Check API keys are set
   cat .env
   
   # Verify model configuration
   grep -A 10 "models:" config.yml

.. seealso::

   :doc:`../01_understanding-the-framework/02_convention-over-configuration`
       Framework architecture and conventions
   
   :doc:`../../getting-started/installation`
       Installation and setup guide
   
   :doc:`../05_production-systems/05_container-and-deployment`
       Container deployment details



