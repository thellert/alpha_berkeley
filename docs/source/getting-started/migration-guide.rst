Migration Guide: Upgrading to v0.7.0
=====================================

.. admonition:: Who Should Read This
   :class: important

   This guide is for users upgrading from the old monolithic structure 
   (applications embedded in framework repo) to the new pip-installable 
   architecture (v0.7.0+).
   
   **Fresh installations?** Skip to :doc:`installation` instead.

Overview of Changes
-------------------

The framework has transitioned from a monolithic architecture to a 
pip-installable dependency model, enabling independent application development.

**Old Structure (v0.6.x and earlier)**::

   alpha_berkeley/
   ├── src/
   │   ├── framework/              # Core framework
   │   └── applications/           # ❌ All apps embedded here
   │       ├── als_assistant/
   │       ├── wind_turbine/
   │       └── hello_world_weather/
   ├── interfaces/                 # Top-level
   ├── deployment/                 # Top-level
   └── config.yml                  # Global configuration

**New Structure (v0.7.0+)**::

   # Framework is pip-installable
   pip install alpha-berkeley-framework
   
   # Each application is now separate
   my-project/
   ├── src/my_project/
   │   ├── registry.py
   │   ├── capabilities/
   │   └── context_classes.py
   ├── services/                   # Copied from framework
   ├── config.yml                  # Self-contained
   └── pyproject.toml              # Framework as dependency

Breaking Changes
----------------

1. Import Paths Changed
~~~~~~~~~~~~~~~~~~~~~~~~

All ``applications.*`` imports must be updated:

.. code-block:: python

   # OLD ❌
   from applications.wind_turbine.capabilities import TurbineAnalysis
   from applications.wind_turbine.context_classes import TurbineDataContext
   
   # NEW ✅
   from wind_turbine.capabilities import TurbineAnalysis
   from wind_turbine.context_classes import TurbineDataContext

2. CLI Commands Unified
~~~~~~~~~~~~~~~~~~~~~~~~

New unified CLI with lazy loading:

.. code-block:: bash

   # OLD ❌
   python -m interfaces.CLI.direct_conversation
   python -m deployment.container_manager deploy_up
   
   # NEW ✅
   framework chat
   framework deploy up

See :doc:`../developer-guides/02_quick-start-patterns/00_cli-reference` for complete command reference.

3. Configuration Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Each application now has its own ``config.yml``:

.. code-block:: yaml

   # OLD: Global framework config
   applications:
     - als_assistant
     - wind_turbine
   
   # NEW: Per-application config
   registry_path: ./src/my_app/registry.py
   project_root: /path/to/my-project

**Key differences:**

- No more global framework configuration
- ``registry_path`` specifies exact location of registry file
- All settings self-contained in one config file
- See :doc:`../developer-guides/03_core-framework-systems/06_configuration-architecture`

4. Registry Discovery
~~~~~~~~~~~~~~~~~~~~~

Explicit path-based discovery replaces automatic scanning:

.. code-block:: yaml

   # config.yml
   registry_path: ./src/my_app/registry.py  # Explicit path required

**No more:**

- Automatic scanning of ``applications/`` directory
- Convention-based discovery by directory name
- Multiple applications in one configuration (advanced use case only)

5. Directory Structure
~~~~~~~~~~~~~~~~~~~~~~

Framework components moved:

.. code-block:: text

   OLD                          NEW
   interfaces/        →         src/framework/interfaces/
   deployment/        →         src/framework/deployment/
   src/configs/       →         src/framework/utils/

These are now pip-installed and not directly visible in application repos.

Migration Steps
---------------

Choose your migration path based on application type:

Production Applications
~~~~~~~~~~~~~~~~~~~~~~~

For applications with independent development teams (e.g., ``als_assistant``):

**Step 1: Install Framework**

.. code-block:: bash

   # Install as dependency
   pip install alpha-berkeley-framework
   
   # Verify installation
   framework --version
   framework --help

**Step 2: Create New Repository**

Option A - Use scaffolding (recommended):

.. code-block:: bash

   framework init my-app --template minimal
   cd my-app

Option B - Manual setup:

.. code-block:: bash

   mkdir -p my-app/src/my_app/{capabilities,}
   cd my-app
   touch src/my_app/{__init__.py,registry.py,context_classes.py}

**Step 3: Copy Application Code**

.. code-block:: bash

   # From old structure
   OLD_REPO=/path/to/alpha_berkeley
   
   # Copy application code
   cp -r $OLD_REPO/src/applications/my_app/* src/my_app/
   
   # Copy custom services if any
   if [ -d "$OLD_REPO/services/applications/my_app" ]; then
       cp -r $OLD_REPO/services/applications/my_app/* services/
   fi
   
   # Copy application-specific config sections
   # (You'll merge these into new config.yml manually)

**Step 4: Update Import Paths**

Automated replacement:

.. code-block:: bash

   # Update all Python files
   find src/my_app -name "*.py" -type f -exec sed -i \
     's/from applications\.my_app/from my_app/g' {} +
   
   find src/my_app -name "*.py" -type f -exec sed -i \
     's/import applications\.my_app/import my_app/g' {} +
   
   # Verify changes
   grep -r "applications\." src/my_app/ || echo "✓ All imports updated"

**Manual verification:**

.. code-block:: python

   # Check each capability file for remaining issues
   
   # Common patterns to fix:
   # ❌ from applications.my_app.capabilities import X
   # ✅ from my_app.capabilities import X
   
   # ❌ import applications.my_app.context_classes
   # ✅ import my_app.context_classes

**Step 5: Simplify Registry with Helper**

Replace verbose registry with helper function:

.. code-block:: python

   # src/my_app/registry.py
   from framework.registry import (
       extend_framework_registry,
       CapabilityRegistration,
       ContextClassRegistration,
       RegistryConfigProvider,
       RegistryConfig
   )
   
   class MyAppRegistryProvider(RegistryConfigProvider):
       """Registry for My Application."""
       
       def get_registry_config(self) -> RegistryConfig:
           return extend_framework_registry(
               capabilities=[
                   CapabilityRegistration(
                       name="my_capability",
                       module_path="my_app.capabilities.my_capability",
                       class_name="MyCapability",
                       description="Description of capability",
                       provides=["MY_CONTEXT"],
                       requires=[]
                   ),
                   # Add all your capabilities...
               ],
               context_classes=[
                   ContextClassRegistration(
                       context_type="MY_CONTEXT",
                       module_path="my_app.context_classes",
                       class_name="MyContext"
                   ),
                   # Add all your context classes...
               ],
               # Optional: exclude framework capabilities you don't need
               exclude_capabilities=["python"],  # Example
           )

See :doc:`../developer-guides/03_core-framework-systems/03_registry-and-discovery` for details.

**Step 6: Create Configuration**

Generate base configuration:

.. code-block:: bash

   # Export framework defaults as starting point
   framework export-config > config.yml

Edit ``config.yml`` to customize:

.. code-block:: yaml

   # Essential settings to update:
   
   # 1. Project paths
   project_root: /absolute/path/to/my-app
   registry_path: ./src/my_app/registry.py
   
   # 2. Build directory
   build_dir: ./build
   
   # 3. Models (update providers and model IDs)
   models:
     orchestrator:
       provider: cborg
       model_id: anthropic/claude-sonnet
     response:
       provider: cborg
       model_id: google/gemini-flash
     # ... update all 8 models
   
   # 4. Service paths
   services:
     jupyter:
       path: ./services/jupyter
     open_webui:
       port_host: 8080
     pipelines:
       port_host: 9099

**Step 7: Setup Environment**

.. code-block:: bash

   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys
   # Required:
   # - OPENAI_API_KEY (if using OpenAI)
   # - ANTHROPIC_API_KEY (if using Claude)
   # - GOOGLE_API_KEY (if using Gemini)
   # - CBORG_API_KEY (if using CBorg)

**Step 8: Validate Setup**

.. code-block:: bash

   # Run health check
   framework health
   
   # Should report:
   # ✅ Python version
   # ✅ Framework installed
   # ✅ Dependencies available
   # ✅ Config file valid
   # ✅ Registry file found

**Step 9: Test Functionality**

.. code-block:: bash

   # Test CLI
   framework chat
   # > "Hello, can you help me test?"

   # Start services (optional)...
   framework deploy up

   # ...and test web interface
   # Browse to http://localhost:8080

**Step 10: Create Repository**

.. code-block:: bash

   # Initialize git
   git init
   git add .
   git commit -m "Initial commit: Migrated from alpha_berkeley framework"
   
   # Create remote and push
   git remote add origin <your-repo-url>
   git push -u origin main

Tutorial Applications
~~~~~~~~~~~~~~~~~~~~~

For tutorial applications (``hello_world_weather``, ``wind_turbine``), **regenerate instead of migrating**:

.. code-block:: bash

   # Weather tutorial
   framework init my-weather --template hello_world_weather
   cd my-weather
   
   # Turbine tutorial  
   framework init my-turbine --template wind_turbine
   cd my-turbine

Templates are kept up-to-date with framework changes and use latest patterns.

For detailed guidance on using these templates:

* :doc:`Hello World Tutorial <hello-world-tutorial>` - Complete walkthrough of the weather template
* :doc:`Build Your First Agent <build-your-first-agent>` - Comprehensive guide to the wind turbine template


New Features in v0.7.0
----------------------

After migration, explore new capabilities:

Unified CLI
~~~~~~~~~~~

.. code-block:: bash

   framework init <name>        # Create new project
   framework deploy up          # Start services
   framework chat               # Interactive conversation
   framework health             # System diagnostics
   framework export-config      # View framework defaults

See :doc:`../developer-guides/02_quick-start-patterns/00_cli-reference`.

Registry Helpers
~~~~~~~~~~~~~~~~

Simplify registry creation with helpers:

.. code-block:: python

   from framework.registry import extend_framework_registry
   
   # 70% less code, automatic framework updates
   return extend_framework_registry(
       capabilities=[...],
       exclude_capabilities=["python"]
   )

See :doc:`../developer-guides/03_core-framework-systems/03_registry-and-discovery`.

Self-Contained Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete transparency - all settings in one place:

.. code-block:: yaml

   # Everything visible and editable
   # ~320 lines, well-organized
   # No hidden defaults

See :doc:`../developer-guides/03_core-framework-systems/06_configuration-architecture`.

Health Diagnostics
~~~~~~~~~~~~~~~~~~

Comprehensive system validation:

.. code-block:: bash

   framework health
   
   # Checks:
   # - Python version
   # - Dependencies
   # - Configuration
   # - Registry files
   # - Container status

Template System
~~~~~~~~~~~~~~~

Quick project generation:

.. code-block:: bash

   framework init my-app --template hello_world_weather
   framework init my-app --template wind_turbine
   framework init my-app --template minimal

Getting Help
------------

If you encounter issues during migration:

**Documentation:**

- :doc:`installation` - Fresh installation guide
- :doc:`../developer-guides/index` - Developer documentation
- :doc:`../api_reference/index` - API reference

**Community:**

- GitHub Issues: https://github.com/thellert/alpha_berkeley/issues
- Discussions: https://github.com/thellert/alpha_berkeley/discussions

**Common Resources:**

- :doc:`../developer-guides/02_quick-start-patterns/00_cli-reference` - CLI commands
- :doc:`../developer-guides/03_core-framework-systems/03_registry-and-discovery` - Registry system
- :doc:`../developer-guides/03_core-framework-systems/06_configuration-architecture` - Configuration

Next Steps
----------

After successful migration:

1. **Learn Best Practices** - Follow the :doc:`Hello World Tutorial <hello-world-tutorial>` to understand v0.7.0 patterns
2. **Build Advanced Features** - Work through :doc:`Build Your First Agent <build-your-first-agent>` for multi-capability integration
3. **Explore New Features** - Try the unified CLI commands
4. **Simplify Registry** - Use ``extend_framework_registry()`` helper
5. **Update Documentation** - Document your application's new structure
6. **Set Up CI/CD** - Configure automated testing in new repo
7. **Share Feedback** - Report issues or suggest improvements

**Happy coding with Alpha Berkeley Framework v0.7.0!** 🚀

