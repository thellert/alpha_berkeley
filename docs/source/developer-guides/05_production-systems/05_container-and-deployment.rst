========================================================================
Container and Deployment: Service Management and Container Orchestration
========================================================================

**What you'll learn:** How to deploy and manage containerized services using the Alpha Berkeley Framework's container management system

.. dropdown:: 📚 What You'll Learn
   :color: primary
   :icon: book

   **Key Concepts:**
   
   - Using ``container_manager.py`` for service deployment and orchestration
   - Configuring hierarchical services (``framework.*`` and ``applications.*``)
   - Managing Jinja2 template rendering with ``docker-compose.yml.j2`` files
   - Understanding build directory management and source code copying
   - Implementing development vs production deployment patterns

   **Prerequisites:** Understanding of Docker/container concepts and :doc:`../../api_reference/01_core_framework/04_configuration_system`
   
   **Time Investment:** 30-45 minutes for complete understanding

Overview
========

The Alpha Berkeley Framework provides a container management system for deploying framework and application services. The system handles service discovery, Docker Compose template rendering, and container orchestration through Podman Compose.

**Core Features:**

- **Hierarchical Service Discovery**: Framework services (``framework.*``) and application services (``applications.app.*``)
- **Template Rendering**: Jinja2 processing of Docker Compose templates with configuration context
- **Build Management**: Automated build directory creation with source code and configuration copying
- **Container Orchestration**: Podman Compose integration for service deployment

Architecture
============

The container management system supports two service categories:

**Framework Services**
   Core infrastructure services defined in ``src/framework/config.yml``:
   
   - ``jupyter``: Python execution environment with EPICS support
   - ``open-webui``: Web interface for agent interaction  
   - ``pipelines``: Processing pipeline infrastructure
   - ``langfuse``: Observability and tracing

**Application Services**
   Domain-specific services defined in ``src/applications/{app}/config.yml``:
   
   - ``mongo``: Database services
   - ``neo4j``: Graph databases
   - ``qdrant``: Vector databases
   - ``pv_finder``: EPICS Process Variable discovery
   - ``logbook``: Electronic logbook integration

Service Configuration
=====================

Configure services in your configuration files using the hierarchical structure.

Framework Services Configuration
--------------------------------

Framework services are configured in ``src/framework/config.yml``:

.. code-block:: yaml

   # Framework service deployment control
   deployed_services:
     - framework.jupyter
     - framework.pipelines
     - framework.open-webui

   framework:
     services:
       jupyter:
         path: ./services/framework/jupyter
         containers:
           read:
             name: jupyter-read
             port_host: 8088
             port_container: 8088
           write:
             name: jupyter-write  
             port_host: 8089
             port_container: 8088
         copy_src: true
         render_kernel_templates: true

       pipelines:
         path: ./services/framework/pipelines
         port_host: 9099
         port_container: 9099
         copy_src: true
         additional_dirs:
           - interfaces

Application Services Configuration
----------------------------------

Application services are configured in ``src/applications/{app}/config.yml``:

.. code-block:: yaml

   # ALS Expert service deployment control
   deployed_services:
     - applications.als_expert.mongo
     - applications.als_expert.pv_finder

   services:
     mongo:
       name: mongo
       path: ./services/applications/als_expert/mongo
       port_host: 27017
       port_container: 27017
       copy_src: true

     pv_finder:
       path: ./services/applications/als_expert/pv_finder
       name: pv-finder
       port_host: 8051
       port_container: 8051
       copy_src: true

**Configuration Options:**

- ``path``: Directory containing the service's Docker Compose template
- ``name``: Container name for the service
- ``port_host/port_container``: Port mapping between host and container
- ``copy_src``: Whether to copy source code into the build directory
- ``additional_dirs``: Extra directories to copy to build environment
- ``render_kernel_templates``: Process Jupyter kernel templates (for Jupyter services)

Deployment Control
==================

Control which services are deployed using the ``deployed_services`` configuration. The main ``config.yml`` can override framework and application settings:

.. code-block:: yaml

   # Main config.yml - override deployed services
   deployed_services:
     # Framework services
     - framework.jupyter
     - framework.pipelines
     
     # Application services  
     - applications.als_expert.mongo
     - applications.als_expert.pv_finder

**Service Naming Patterns:**

- Framework services: ``framework.{service_name}`` or short name ``{service_name}``
- Application services: ``applications.{app}.{service_name}`` (full path required)

Deployment Workflow
===================

The container management system supports both development and production deployment patterns.

Development Pattern
-------------------

For development and debugging, start services incrementally:

1. **Configure services incrementally** in ``config.yml``:

   .. code-block:: yaml

      deployed_services:
        - framework.pipelines  # Start with one service

2. **Start in non-detached mode** to monitor logs:

   .. code-block:: bash

      python3 deployment/container_manager.py config.yml up

3. **Add additional services** after verifying each one works correctly

Production Pattern
------------------

For production deployment:

1. **Configure all required services** in ``config.yml``:

   .. code-block:: yaml

      deployed_services:
        - framework.jupyter
        - framework.open-webui
        - framework.pipelines
        - applications.als_expert.mongo

2. **Start all services in detached mode**:

   .. code-block:: bash

      python3 deployment/container_manager.py config.yml up -d

3. **Verify services are running**:

   .. code-block:: bash

      podman ps

Docker Compose Templates
========================

Services use Jinja2 templates for Docker Compose file generation.

Template Structure
------------------

Templates are located at ``{service_path}/docker-compose.yml.j2`` and have access to the complete configuration context:

.. code-block:: yaml

   # services/framework/jupyter/docker-compose.yml.j2
   services:
     jupyter-read:
       container_name: jupyter-read
       build:
         context: ./framework/jupyter
         dockerfile: Dockerfile
       ports:
         - "{{framework.services.jupyter.containers.read.port_host}}:{{framework.services.jupyter.containers.read.port_container}}"
       volumes:
         - {{project_root}}/{{file_paths.agent_data_dir}}/{{file_paths.executed_python_scripts_dir}}:/home/jovyan/work/executed_scripts/
       environment:
         - PYTHONPATH=/jupyter/repo_src
         - HTTP_PROXY=${HTTP_PROXY}
       networks:
         - alpha-berkeley-network

**Template Features:**

- **Configuration Access**: Full configuration available as Jinja2 variables
- **Environment Variables**: Access to environment variables via ``${VAR_NAME}``
- **Networking**: Automatic network configuration
- **Volume Management**: Dynamic volume mounting based on configuration

Container Manager Usage
=======================

Deploy services using the container manager script.

Basic Commands
--------------

.. code-block:: bash

   # Generate compose files only (for review)
   python3 deployment/container_manager.py config.yml
   
   # Start services in foreground
   python3 deployment/container_manager.py config.yml up
   
   # Start services in background  
   python3 deployment/container_manager.py config.yml up -d
   
   # Stop services
   python3 deployment/container_manager.py config.yml down

Deployment Workflow
-------------------

The container manager follows this workflow:

1. **Configuration Loading**: Load and merge configuration files with imports
2. **Service Discovery**: Process ``deployed_services`` list to identify active services  
3. **Template Processing**: Render Jinja2 templates with configuration context
4. **Build Directory Setup**: Create build directories and copy necessary files
5. **Container Orchestration**: Execute Podman Compose with generated files

**Generated Files:**

.. code-block:: bash

   build/services/
   ├── docker-compose.yml                                    # Root network configuration
   ├── framework/
   │   └── jupyter/
   │       ├── docker-compose.yml                           # Jupyter service
   │       ├── repo_src/                                    # Copied source code
   │       └── config.yml                                   # Flattened configuration
   └── applications/
       └── als_expert/
           └── mongo/
               ├── docker-compose.yml                       # MongoDB service
               └── repo_src/                                # Copied source code

Container Networking
====================

Service Communication
----------------------

Services communicate through container networks using service names as hostnames:

- **OpenWebUI to Pipelines**: ``http://pipelines:9099``
- **Framework to Databases**: ``mongodb://mongo:27017``, ``http://neo4j:7474``
- **Host to Services**: ``http://localhost:<mapped_port>``

Host Access from Containers
---------------------------

For containers to access services running on the host (like Ollama):

- Use ``host.containers.internal`` instead of ``localhost``
- Example: ``http://host.containers.internal:11434`` for Ollama

Port Mapping
------------

Services expose ports to the host system:

- **OpenWebUI**: ``8080:8080``
- **Jupyter**: ``8888:8888`` (read-only), ``8889:8888`` (write access)
- **Pipelines**: ``9099:9099``

Check your service configurations for specific port mappings.

Advanced Configuration
======================

Environment Variables
---------------------

The container manager automatically loads environment variables from ``.env``:

.. code-block:: bash

   # .env file - Services will have access to these variables
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here

Build Directory Customization
------------------------------

Generated files are placed in the ``build/`` directory by default. This can be configured:

.. code-block:: yaml

   build_dir: "./custom_build"

Source Code Integration
-----------------------

Services can be configured to include source code:

.. code-block:: yaml

   framework:
     services:
       pipelines:
         copy_src: true  # Copies src/ to repo_src/ in container

Additional Directories
----------------------

Services can copy additional directories into containers:

.. code-block:: yaml

   framework:
     services:
       jupyter:
         additional_dirs:
           - src_dir: "_agent_data"
             dest_dir: "agent_data"
           - docs  # Simple directory copy

Build Directory Management
==========================

The container manager creates complete build environments for each service.

Build Process
-------------

For each deployed service:

1. **Clean Build Directory**: Remove existing build directory for clean deployment
2. **Render Templates**: Process Docker Compose template with configuration context
3. **Copy Service Files**: Copy all service files except templates
4. **Copy Source Code**: Copy ``src/`` directory if ``copy_src: true``
5. **Copy Additional Directories**: Copy directories specified in ``additional_dirs``
6. **Create Flattened Configuration**: Generate merged configuration file for containers
7. **Process Kernel Templates**: Render Jupyter kernel configurations if enabled

**Source Code Handling:**

- Source code is copied to ``repo_src/`` in the build directory
- Global ``requirements.txt`` is automatically copied to ``repo_src/requirements.txt``
- ``PYTHONPATH`` is configured to include the copied source code

Working Examples
================

Deploy Jupyter Development Environment
--------------------------------------

Configure and deploy Jupyter service:

.. code-block:: yaml

   # config.yml
   deployed_services:
     - framework.jupyter

.. code-block:: bash

   python3 deployment/container_manager.py config.yml up -d
   # Access at http://localhost:8088 (read-only) or http://localhost:8089 (write access)

Deploy Application Services
---------------------------

Configure and deploy application stack:

.. code-block:: yaml

   # config.yml  
   deployed_services:
     - applications.als_expert.mongo
     - applications.als_expert.pv_finder
     - applications.als_expert.qdrant

.. code-block:: bash

   python3 deployment/container_manager.py config.yml up -d
   # Services available at: MongoDB (27017), PV Finder (8051), Qdrant (6333)

Troubleshooting
===============

Common Issues
-------------

**Services fail to start:**

1. Check individual service logs: ``podman logs <container_name>``
2. Verify configuration syntax in ``config.yml``
3. Ensure required environment variables are set in ``.env``
4. Try starting services individually to isolate issues

**Port conflicts:**

1. Check for processes using required ports: ``lsof -i :8080``
2. Update port mappings in service configurations
3. Ensure no other containers are using the same ports

**Container networking issues:**

1. Verify service names match configuration
2. Use container network names (e.g., ``pipelines``) not ``localhost``
3. Check firewall settings if accessing from external systems

**Template rendering errors:**

1. Verify Jinja2 syntax in template files
2. Check that all required configuration values are provided
3. Review template paths in error messages

**Service not found in configuration**
   - Verify service is defined in the appropriate config file
   - Check service naming (framework vs application services)
   - Ensure ``deployed_services`` includes the service

**Template file not found**  
   - Verify ``docker-compose.yml.j2`` exists in the service path
   - Check that the service ``path`` configuration is correct

Debugging Commands
------------------

**List running containers:**

.. code-block:: bash

   podman ps

**View container logs:**

.. code-block:: bash

   podman logs <container_name>
   podman logs -f <container_name>  # Follow logs

**Inspect container configuration:**

.. code-block:: bash

   podman inspect <container_name>

**Network inspection:**

.. code-block:: bash

   podman network ls
   podman network inspect <network_name>

**Generate compose files without starting:**

.. code-block:: bash

   python3 deployment/container_manager.py config.yml

This generates files in ``build/`` for manual inspection.

**Check for port conflicts:**

.. code-block:: bash

   lsof -i :8080  # Check specific port
   netstat -tulpn | grep :8080  # Alternative method

**Test network connectivity:**

.. code-block:: bash

   podman exec <container_name> ping <other_container>
   podman exec <container_name> curl http://other_container:port

System Capabilities
===================

**Current Features:**
- Service discovery and template rendering
- Docker Compose orchestration  
- Build directory management
- Configuration flattening

**Production Considerations:**
- Health monitoring and automated recovery
- Rolling deployments or blue-green deployments
- Service dependency management beyond Docker Compose
- Production monitoring and alerting
- Automated scaling or load balancing

For production deployments, consider implementing additional monitoring and management tooling.

Best Practices
==============

Development
-----------

- Start with minimal service configurations
- Use non-detached mode during development
- Test services individually before deploying together
- Keep build directory in ``.gitignore``
- Use meaningful service names in logs

Production
----------

- Use detached mode for production deployments
- Monitor container resource usage
- Implement health checks for critical services
- Plan for service restart policies
- Regular backup of data volumes

Configuration
-------------

- Keep sensitive data in ``.env`` files
- Use meaningful names for custom networks
- Document any custom template modifications
- Version control configuration files
- Test configuration changes in development first

Next Steps
==========

After setting up container deployment:

- :doc:`../../api_reference/01_core_framework/04_configuration_system` - Advanced configuration patterns

**Related API Reference:**
- :doc:`../../api_reference/03_production_systems/05_container-management` - Container management API
- :doc:`../../api_reference/01_core_framework/04_configuration_system` - Configuration system reference