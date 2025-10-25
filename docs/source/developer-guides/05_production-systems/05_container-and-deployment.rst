====================
Container Deployment
====================

**What you'll learn:** How to deploy and manage containerized services using the Alpha Berkeley Framework's deployment CLI

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Using ``framework deploy`` CLI for service deployment and orchestration
   - Configuring services in your project's ``config.yml``
   - Managing Jinja2 template rendering with ``docker-compose.yml.j2`` files
   - Understanding build directory management and source code copying
   - Implementing development vs production deployment patterns

   **Prerequisites:** Understanding of Docker/container concepts and :doc:`../../api_reference/01_core_framework/04_configuration_system`
   
   **Time Investment:** 30-45 minutes for complete understanding

Overview
========

The Alpha Berkeley Framework provides a container management system for deploying services. The system handles service discovery, Docker Compose template rendering, and container orchestration through Podman Compose.

**Core Features:**

- **Simple Service Configuration**: All services defined in a flat ``services:`` section
- **Template Rendering**: Jinja2 processing of Docker Compose templates with full configuration context
- **Build Management**: Automated build directory creation with source code and configuration copying
- **Container Orchestration**: Podman Compose integration for multi-service deployment

Architecture
============

The container management system uses a simple, flat directory structure. All services live in your project's ``services/`` directory and are configured the same way.

**Common Services:**

*Framework Infrastructure Services:*
   Core services used across applications:
   
   - ``jupyter``: Python execution environment with EPICS support
   - ``open-webui``: Web interface for agent interaction  
   - ``pipelines``: Processing pipeline infrastructure

*Application-Specific Services:*
   Custom services for your particular application. Examples from the :doc:`../../example-applications/als-assistant`:
   
   - ``mongo``: MongoDB database for ALS operations data
   - ``pv_finder``: EPICS Process Variable discovery MCP server
   - ``langfuse``: LLM observability and monitoring
   - Any custom services you create

All services are defined in the same ``services:`` section of your ``config.yml``, regardless of whether they're framework infrastructure or application-specific.

Service Configuration
=====================

Services are configured in your project's ``config.yml`` using a simple, flat structure. All services—whether framework infrastructure or application-specific—use the same configuration format.

Basic Configuration Pattern
---------------------------

Here's the standard pattern used by all framework projects:

.. code-block:: yaml

   # config.yml - Your project configuration
   
   # Define all services in a flat structure
   services:
     # Jupyter - Python execution environment
     jupyter:
       path: ./services/jupyter
       containers:
         read:
           name: jupyter-read
           hostname: jupyter-read
           port_host: 8088
           port_container: 8088
           execution_modes: ["read_only"]
         write:
           name: jupyter-write
           hostname: jupyter-write
           port_host: 8089
           port_container: 8088
           execution_modes: ["write_access"]
       copy_src: true
       render_kernel_templates: true

     # Open WebUI - User interface frontend
     open_webui:
       path: ./services/open-webui
       hostname: localhost
       port_host: 8080
       port_container: 8080

     # Pipelines - Processing infrastructure
     pipelines:
       path: ./services/pipelines
       port_host: 9099
       port_container: 9099
       copy_src: true

     # Application-specific service example (optional)
     # Example: MongoDB for your application data
     mongo:
       name: mongo
       path: ./services/mongo
       port_host: 27017
       port_container: 27017
       copy_src: false

   # Control which services to deploy
   deployed_services:
     - jupyter
     - open_webui
     - pipelines
     # - mongo  # Add your application services as needed

**Key Configuration Options:**

- ``path``: Directory containing the service's Docker Compose template (``docker-compose.yml.j2``)
- ``name``: Container name (defaults to service key if not specified)
- ``hostname``: Container hostname for networking
- ``port_host/port_container``: Port mapping between host and container
- ``copy_src``: Whether to copy ``src/`` directory into the build directory (default: false)
- ``additional_dirs``: Extra directories to copy to build environment (list)
- ``render_kernel_templates``: Process Jupyter kernel templates (for Jupyter services only)
- ``containers``: Multi-container configuration (for services like Jupyter with read/write variants)

Service Directory Organization
------------------------------

Your project organizes services in a flat directory structure:

.. code-block:: text

   your-project/
   ├── services/
   │   ├── docker-compose.yml.j2          # Root network configuration
   │   ├── jupyter/                        # Jupyter service
   │   │   ├── docker-compose.yml.j2
   │   │   ├── Dockerfile
   │   │   ├── custom_start.sh
   │   │   └── python3-epics-readonly/
   │   ├── open-webui/                     # Web UI service
   │   │   ├── docker-compose.yml.j2
   │   │   ├── Dockerfile
   │   │   └── functions/
   │   ├── pipelines/                      # Processing pipeline service
   │   │   ├── docker-compose.yml.j2
   │   │   └── main.py
   │   └── mongo/                          # (Optional) Application services
   │       ├── docker-compose.yml.j2      # E.g., MongoDB for ALS Assistant
   │       └── Dockerfile
   ├── config.yml
   └── src/
       └── your_app/

Each service directory contains:
   - ``docker-compose.yml.j2`` (required): Jinja2 template for Docker Compose
   - ``Dockerfile`` (optional): If the service needs a custom image
   - Other service-specific files (scripts, configs, etc.)

The ``path`` field in your configuration points to these service directories.

Deployment Workflow
===================

The container management system supports both development and production deployment patterns.

.. admonition:: New in v0.7.0: Framework CLI Commands
   :class: version-070-change

   Service deployment is now managed through the ``framework deploy`` CLI command.

Development Pattern
-------------------

For development and debugging, start services incrementally:

1. **Configure services incrementally** in ``config.yml``:

   .. code-block:: yaml

      deployed_services:
        - open_webui  # Start with one service

2. **Start in non-detached mode** to monitor logs:

   .. code-block:: bash

      framework deploy up

3. **Add additional services** after verifying each one works correctly

Production Pattern
------------------

For production deployment:

1. **Configure all required services** in ``config.yml``:

   .. code-block:: yaml

      deployed_services:
        - jupyter
        - open_webui
        - pipelines

2. **Start all services in detached mode**:

   .. code-block:: bash

      framework deploy up --detached

3. **Verify services are running**:

   .. code-block:: bash

      podman ps

Docker Compose Templates
=========================

Services use Jinja2 templates for Docker Compose file generation. Templates have access to your complete configuration context.

Template Structure
------------------

Templates are located at ``{service_path}/docker-compose.yml.j2``. Here's a complete example:

.. code-block:: yaml

   # services/jupyter/docker-compose.yml.j2
   services:
     jupyter-read:
       container_name: {{services.jupyter.containers.read.name}}
       build:
         context: ./jupyter
         dockerfile: Dockerfile
       restart: unless-stopped
       ports:
         - "{{services.jupyter.containers.read.port_host}}:{{services.jupyter.containers.read.port_container}}"
       volumes:
         - ./jupyter:/jupyter
         - {{project_root}}/{{file_paths.agent_data_dir}}/{{file_paths.executed_python_scripts_dir}}:/home/jovyan/work/executed_scripts/
       environment:
         - NOTEBOOK_DIR=/home/jovyan/work
         - JUPYTER_ENABLE_LAB=yes
         - PYTHONPATH=/jupyter/repo_src
         - TZ={{system.timezone}}
         - HTTP_PROXY=${HTTP_PROXY}
         - NO_PROXY=${NO_PROXY}
       networks:
         - alpha-berkeley-network

**Template Features:**

- **Configuration Access**: Full configuration available as Jinja2 variables
  
  - Access services: ``{{services.service_name.option}}``
  - Access file paths: ``{{file_paths.agent_data_dir}}``
  - Access system config: ``{{system.timezone}}``
  - Access project root: ``{{project_root}}``

- **Environment Variables**: Reference host environment via ``${VAR_NAME}``

- **Networking**: All services automatically join the ``alpha-berkeley-network``

- **Volume Management**: Dynamic volume mounting based on configuration

Template Access Patterns
-------------------------

Common template patterns for accessing configuration:

.. code-block:: yaml

   # Access service configuration
   ports:
     - "{{services.my_service.port_host}}:{{services.my_service.port_container}}"
   
   # Access nested service config (like Jupyter containers)
   container_name: {{services.jupyter.containers.read.name}}
   
   # Access file paths
   volumes:
     - {{project_root}}/{{file_paths.agent_data_dir}}:/data
   
   # Access system configuration
   environment:
     - TZ={{system.timezone}}
   
   # Access custom configuration
   environment:
     - DATABASE_URL={{database.connection_string}}

Deployment CLI Usage
====================

Deploy services using the ``framework deploy`` command.

Basic Commands
--------------

.. code-block:: bash

   # Start services in foreground (see logs in terminal)
   framework deploy up
   
   # Start services in background (detached mode)
   framework deploy up --detached
   
   # Stop services
   framework deploy down
   
   # Restart services
   framework deploy restart
   
   # Show service status
   framework deploy status
   
   # Clean deployment (remove containers and volumes)
   framework deploy clean
   
   # Rebuild containers from scratch
   framework deploy rebuild

Command Options
---------------

.. code-block:: bash

   # Use custom configuration file
   framework deploy up --config my-config.yml
   
   # Restart in detached mode
   framework deploy restart --detached
   
   # Rebuild and start in detached mode
   framework deploy rebuild --detached

Deployment Workflow Details
----------------------------

When you run ``framework deploy up``, the container manager follows this workflow:

1. **Configuration Loading**: Load and merge configuration files
2. **Service Discovery**: Read ``deployed_services`` list to identify active services  
3. **Build Directory Creation**: Create clean build directories for each service
4. **Template Processing**: Render Jinja2 templates with complete configuration context
5. **File Copying**: Copy service files, source code, and additional directories
6. **Configuration Flattening**: Generate self-contained config files for containers
7. **Container Orchestration**: Execute Podman Compose with generated files

**Generated Build Directory:**

.. code-block:: text

   build/services/
   ├── docker-compose.yml           # Root network configuration
   ├── jupyter/
   │   ├── docker-compose.yml       # Rendered Jupyter service config
   │   ├── Dockerfile
   │   ├── custom_start.sh
   │   ├── python3-epics-readonly/
   │   │   └── kernel.json          # Rendered kernel config
   │   ├── python3-epics-write/
   │   │   └── kernel.json
   │   ├── repo_src/                # Copied source code (if copy_src: true)
   │   │   ├── your_app/
   │   │   └── requirements.txt
   │   └── config.yml               # Flattened configuration
   ├── open-webui/
   │   ├── docker-compose.yml
   │   └── ...
   └── pipelines/
       ├── docker-compose.yml
       ├── repo_src/                # Copied source code
       └── config.yml

Container Networking
====================

Services communicate through container networks using service names as hostnames.

Service Communication
---------------------

Container-to-container communication uses service names:

- **OpenWebUI to Pipelines**: ``http://pipelines:9099``
- **Pipelines to Jupyter**: ``http://jupyter-read:8088``
- **Application to MongoDB** (ALS Assistant): ``mongodb://mongo:27017``
- **Application to PV Finder** (ALS Assistant): ``http://pv-finder:8051``

Host Access from Containers
----------------------------

For containers to access services running on the host (like Ollama):

- Use ``host.containers.internal`` instead of ``localhost``
- Example: ``http://host.containers.internal:11434`` for Ollama

.. code-block:: yaml

   # In docker-compose.yml.j2
   environment:
     - OLLAMA_BASE_URL=http://host.containers.internal:11434

Port Mapping
------------

Services expose ports to the host system for external access:

.. code-block:: yaml

   # Host access through mapped ports
   services:
     open_webui:
       ports:
         - "8080:8080"  # Access at http://localhost:8080

Common port mappings:

- **OpenWebUI**: ``8080:8080`` → ``http://localhost:8080``
- **Jupyter Read**: ``8088:8088`` → ``http://localhost:8088``
- **Jupyter Write**: ``8089:8088`` → ``http://localhost:8089``
- **Pipelines**: ``9099:9099`` → ``http://localhost:9099``

Advanced Configuration
======================

Environment Variables
---------------------

The container manager automatically loads environment variables from ``.env``:

.. code-block:: bash

   # .env file - Services will have access to these variables
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   CBORG_API_KEY=your_key_here
   PROJECT_ROOT=/absolute/path/to/project
   LOCAL_PYTHON_VENV=/path/to/venv/bin/python

These variables are:

1. Available to Docker Compose via ``${VAR_NAME}`` syntax
2. Can be passed to containers via ``environment:`` sections
3. Used by configuration system for variable expansion

Build Directory Customization
------------------------------

Change the build output directory:

.. code-block:: yaml

   # config.yml
   build_dir: "./custom_build"

Source Code Integration
-----------------------

Control whether services get a copy of your ``src/`` directory:

.. code-block:: yaml

   services:
     pipelines:
       copy_src: true  # Copies src/ to build/services/pipelines/repo_src/

This is useful for:

- Pipelines server (needs access to your application code)
- Jupyter containers (needs your application for interactive development)
- Services that execute your application code

Services that don't need source code (databases, UI-only services) should set ``copy_src: false``.

Additional Directories
----------------------

Copy extra directories into service build environments:

.. code-block:: yaml

   services:
     jupyter:
       additional_dirs:
         # Simple directory copy
         - docs
         
         # Custom source -> destination mapping
         - src: "_agent_data"
           dst: "agent_data"
         
         # Copy framework source (useful during development)
         - src: ../alpha_berkeley/src/framework
           dst: framework_src/src/framework

This is commonly used for:

- Documentation that services need
- Data directories
- Configuration files
- Framework source during development (before framework is pip-installable)

Build Directory Management
==========================

The container manager creates complete, self-contained build environments for each service.

Build Process
-------------

For each deployed service, the build process:

1. **Clean Build Directory**: Remove existing build directory for clean deployment
2. **Render Docker Compose Template**: Process Jinja2 template with configuration
3. **Copy Service Files**: Copy all files from service directory (except ``.j2`` templates)
4. **Copy Source Code**: If ``copy_src: true``, copy entire ``src/`` directory
5. **Copy Additional Directories**: Copy any directories specified in ``additional_dirs``
6. **Create Flattened Configuration**: Generate self-contained ``config.yml`` for the container
7. **Process Kernel Templates**: If ``render_kernel_templates: true``, render Jupyter kernel configs

**Source Code Handling:**

When ``copy_src: true``:

- Source code is copied to ``build/services/{service}/repo_src/``
- Global ``requirements.txt`` is automatically copied
- Project's ``pyproject.toml`` is copied as ``pyproject_user.toml``
- Containers set ``PYTHONPATH`` to include the copied source

**Configuration Flattening:**

Each service gets a ``config.yml`` with:

- All imports resolved and merged
- Complete, self-contained configuration
- Registry paths adjusted for container environment
- No import directives (everything is flattened)

Working Examples
================

Complete Wind Turbine Example
------------------------------

This example shows a complete working configuration from the Wind Turbine tutorial:

.. code-block:: yaml

   # config.yml
   build_dir: ./build
   project_root: /home/user/wind-turbine
   registry_path: ./src/wind/registry.py

   services:
     jupyter:
       path: ./services/jupyter
       containers:
         read:
           name: jupyter-read
           hostname: jupyter-read
           port_host: 8088
           port_container: 8088
           execution_modes: ["read_only"]
         write:
           name: jupyter-write
           hostname: jupyter-write
           port_host: 8089
           port_container: 8088
           execution_modes: ["write_access"]
       copy_src: true
       render_kernel_templates: true

     open_webui:
       path: ./services/open-webui
       hostname: localhost
       port_host: 8080
       port_container: 8080

     pipelines:
       path: ./services/pipelines
       port_host: 9099
       port_container: 9099
       copy_src: true

   deployed_services:
     - jupyter
     - open_webui
     - pipelines

   system:
     timezone: ${TZ:-America/Los_Angeles}

   file_paths:
     agent_data_dir: _agent_data
     executed_python_scripts_dir: executed_scripts

Deploy this configuration:

.. code-block:: bash

   framework deploy up --detached
   
   # Services available:
   # - OpenWebUI: http://localhost:8080
   # - Jupyter Read: http://localhost:8088
   # - Jupyter Write: http://localhost:8089
   # - Pipelines: http://localhost:9099

Troubleshooting
===============

.. tab-set::

   .. tab-item:: Common Issues

      **Services fail to start:**

      1. Check individual service logs: ``podman logs <container_name>``
      2. Verify configuration syntax in ``config.yml``
      3. Ensure required environment variables are set in ``.env``
      4. Try starting services individually to isolate issues
      5. Check that service paths exist and contain ``docker-compose.yml.j2``

      **Port conflicts:**

      1. Check for processes using required ports: ``lsof -i :8080``
      2. Update port mappings in service configurations
      3. Ensure no other containers are using the same ports
      4. Verify ``deployed_services`` doesn't have duplicate services

      **Container networking issues:**

      1. Verify service names match configuration
      2. Use container network names (e.g., ``pipelines``) not ``localhost``
      3. Check firewall settings if accessing from external systems
      4. Ensure all services use the ``alpha-berkeley-network``

      **Template rendering errors:**

      1. Verify Jinja2 syntax in template files (``{{variable}}`` not ``{variable}``)
      2. Check that configuration values exist before accessing them
      3. Review template paths in error messages
      4. Inspect generated files in ``build/`` directory

      **Service not found in configuration:**

      - Verify service is defined in ``services:`` section
      - Check service name matches between ``services:`` and ``deployed_services:``
      - Ensure ``deployed_services`` list uses correct service names

      **Template file not found:**

      - Verify ``docker-compose.yml.j2`` exists at the ``path`` location
      - Check that the service ``path`` is correct relative to your project root
      - Ensure you haven't accidentally specified a directory that doesn't exist

      **Copy source failures:**

      - Verify ``src/`` directory exists if ``copy_src: true``
      - Check permissions on source directories
      - Ensure additional_dirs paths exist

   .. tab-item:: Debugging Commands

      **List running containers:**

      .. code-block:: bash

         podman ps

      **View container logs:**

      .. code-block:: bash

         podman logs <container_name>
         podman logs -f <container_name>  # Follow logs in real-time

      **Inspect container configuration:**

      .. code-block:: bash

         podman inspect <container_name>

      **Network inspection:**

      .. code-block:: bash

         podman network ls
         podman network inspect alpha-berkeley-network

      **Check generated configuration:**

      .. code-block:: bash

         # Review rendered Docker Compose files
         cat build/services/jupyter/docker-compose.yml
         
         # Check flattened configuration
         cat build/services/pipelines/config.yml

      **Check for port conflicts:**

      .. code-block:: bash

         lsof -i :8080  # Check specific port
         netstat -tulpn | grep :8080  # Alternative method

      **Test network connectivity:**

      .. code-block:: bash

         # Test container-to-container communication
         podman exec pipelines ping jupyter-read
         podman exec pipelines curl http://open-webui:8080

      **Rebuild after configuration changes:**

      .. code-block:: bash

         # Full rebuild (safest after config changes)
         framework deploy clean
         framework deploy up --detached
         
         # Or use rebuild command (clean + up in one step)
         framework deploy rebuild --detached

   .. tab-item:: Quick Reference

      **Common Commands:**

      .. code-block:: bash

         # Start services
         framework deploy up
         framework deploy up --detached

         # Stop services
         framework deploy down

         # Check status
         framework deploy status
         podman ps

         # View logs
         podman logs <container_name>
         podman logs -f <container_name>

         # Clean restart
         framework deploy clean
         framework deploy up --detached

      **Common Service Names:**

      - ``jupyter-read`` - Jupyter read-only container
      - ``jupyter-write`` - Jupyter write-access container
      - ``open-webui`` - Web interface
      - ``pipelines`` - Processing pipeline
      - ``mongo`` - MongoDB (ALS Assistant)
      - ``pv-finder`` - PV Finder MCP (ALS Assistant)

      **Common Ports:**

      - ``8080`` - OpenWebUI
      - ``8088`` - Jupyter (read-only)
      - ``8089`` - Jupyter (write-access)
      - ``9099`` - Pipelines
      - ``27017`` - MongoDB
      - ``8051`` - PV Finder

   .. tab-item:: Best Practices

      **Development:**

      - **Start minimal**: Begin with one service, verify it works, then add more
      - **Use foreground mode**: Run ``framework deploy up`` (not detached) during development to see logs
      - **Test services individually**: Deploy services one at a time to isolate issues
      - **Keep build directory in .gitignore**: Build artifacts shouldn't be version controlled
      - **Use meaningful container names**: Makes logs and debugging easier

      **Production:**

      - **Use detached mode**: Run ``framework deploy up --detached`` for production
      - **Monitor container resources**: Use ``podman stats`` to watch resource usage
      - **Implement health checks**: Add health check configurations to your docker-compose templates
      - **Plan restart policies**: Use ``restart: unless-stopped`` in production templates
      - **Regular backups**: Back up data volumes for database services
      - **Document deployment**: Keep notes on deployment procedures and configurations

      **Configuration:**

      - **Keep secrets in .env**: Never commit API keys or passwords to version control
      - **Use absolute paths**: Set ``project_root`` as absolute path in config
      - **Test changes incrementally**: Test configuration changes in development first
      - **Version control configs**: Track ``config.yml`` and templates in git
      - **Document custom modifications**: Comment any non-standard template changes
      - **Validate before deploying**: Check YAML syntax before running deploy commands

      **Template Development:**

      - **Test templates incrementally**: Verify each configuration value exists
      - **Use descriptive variable names**: Clear naming makes templates maintainable
      - **Add comments**: Document non-obvious template logic
      - **Check rendered output**: Review files in ``build/`` after changes
      - **Handle missing values gracefully**: Use Jinja2 defaults: ``{{value|default('fallback')}}``

.. seealso::

   :doc:`../../api_reference/01_core_framework/04_configuration_system`
       Advanced configuration patterns and variable expansion
   
   :doc:`../../api_reference/03_production_systems/05_container-management`
       Container management API reference
