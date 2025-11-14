Migration Guide: Upgrading to Osprey Framework v0.8.0
=====================================================

.. admonition:: 🦅 Framework Renamed to Osprey
   :class: important

   As of **v0.8.0**, the **Alpha Berkeley Framework** has been renamed to **Osprey Framework**.
   This guide covers both the rename migration and architectural upgrades from older versions.

Quick Navigation
----------------

**Choose your migration path:**

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 📦 Fresh Installation
      :link: installation
      :link-type: doc

      Installing Osprey for the first time? Skip this guide.

   .. grid-item-card:: 🔄 From v0.7.x → v0.8.0
      :link: migration-path-b-v0-7-x-v0-8-0-rename-only
      :link-type: ref

      Quick rename migration (15-30 min)

   .. grid-item-card:: 🏗️ From v0.6.x → v0.8.0
      :link: migration-path-a-v0-6-x-v0-8-0-full-migration
      :link-type: ref

      Architectural + rename migration (2-4 hours)

   .. grid-item-card:: 📖 Understanding Changes
      :link: overview-of-all-changes
      :link-type: ref

      What changed and why

Using Claude, Cursor, or another AI assistant? Download the AI-optimized migration guide for your version:

- **📥 From v0.7.x (Quick Rename):** :download:`Migration Guide v0.7→v0.8 </_static/resources/MIGRATION_GUIDE_v0.7_to_v0.8.md>`
- **📥 From v0.6.x (Full Migration):** :download:`Migration Guide v0.6→v0.8 </_static/resources/MIGRATION_GUIDE_v0.6_to_v0.8.md>`


.. _overview-of-all-changes:

Overview of All Changes
-----------------------

The framework has undergone two major transitions:

Version History
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Version
     - Release
     - Major Changes
   * - **v0.8.0**
     - Nov 2025
     - 🦅 **Renamed to Osprey Framework**

       - Package: ``alpha-berkeley-framework`` → ``osprey-framework``
       - Imports: ``from framework.*`` → ``from osprey.*``
       - CLI: ``framework`` → ``osprey``
       - Repository: ``als-apg/osprey``
   * - **v0.7.0**
     - Oct 2025
     - 📦 **Pip-installable Architecture**

       - Monolithic → Separate applications
       - Unified CLI system
       - Registry helpers
       - Self-contained configuration
   * - **v0.6.x**
     - Earlier
     - 🏗️ **Monolithic Structure**

       - All applications embedded in framework repo
       - Manual Python module execution

Structural Evolution
~~~~~~~~~~~~~~~~~~~~

**v0.6.x and earlier (Monolithic)**::

   alpha_berkeley/
   ├── src/
   │   ├── framework/              # Core (old name)
   │   └── applications/           # ❌ All apps embedded
   │       ├── als_assistant/
   │       └── control_assistant/
   ├── interfaces/                 # Top-level
   ├── deployment/                 # Top-level
   └── config.yml                  # Global config

**v0.7.0 (Pip-installable, old name)**::

   # Framework as dependency
   pip install alpha-berkeley-framework

   # Separate application repos
   my-project/
   ├── src/my_project/
   ├── config.yml
   └── pyproject.toml

**v0.8.0 (Current - Renamed to Osprey)**::

   # New package name
   pip install osprey-framework

   # Same structure, new imports
   my-project/
   ├── src/my_project/
   │   # from osprey.* imports
   └── pyproject.toml
       # osprey-framework dependency

.. _migration-path-b-v0-7-x-v0-8-0-rename-only:

Migration Path B: v0.7.x → v0.8.0 (Rename Only)
------------------------------------------------

.. admonition:: ✅ For Current Users
   :class: tip

   If you're already on v0.7.x with the pip-installable architecture,
   this is a **quick rename migration** (15-30 minutes).

   **No API changes** - only package name and imports change.

Step 1: Update Framework Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Uninstall old package
   pip uninstall alpha-berkeley-framework -y

   # Install new package
   pip install osprey-framework

   # Verify installation
   osprey --version  # Should show 0.8.0+

Step 2: Update Import Statements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Find and replace** in your project files (case-sensitive):

.. code-block:: python

   # FIND:    from framework.
   # REPLACE: from osprey.

**Before:**

.. code-block:: python

   from framework.state import AgentState
   from framework.base.capability import BaseCapability
   from framework.base.node import BaseNode
   from framework.registry.manager import RegistryManager

**After:**

.. code-block:: python

   from osprey.state import AgentState
   from osprey.base.capability import BaseCapability
   from osprey.base.node import BaseNode
   from osprey.registry.manager import RegistryManager

Step 3: Update String Module References
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Find and replace** string-based module paths:

.. code-block:: python

   # FIND:    "framework.
   # REPLACE: "osprey.

**Before:**

.. code-block:: python

   module_path = "framework.capabilities.my_capability"
   __module__ = "framework.services.my_service"

**After:**

.. code-block:: python

   module_path = "osprey.capabilities.my_capability"
   __module__ = "osprey.services.my_service"

Step 4: Update Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**requirements.txt:**

.. code-block:: text

   # OLD:
   alpha-berkeley-framework>=0.7.0

   # NEW:
   osprey-framework>=0.8.0

**pyproject.toml:**

.. code-block:: toml

   # OLD:
   dependencies = [
       "alpha-berkeley-framework>=0.7.0",
   ]

   # NEW:
   dependencies = [
       "osprey-framework>=0.8.0",
   ]

Step 5: Test Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Verify imports work
   python -c "from osprey.state import AgentState; print('✅ Imports working')"

   # Run your tests
   pytest

   # Try the CLI
   osprey chat --project /path/to/your/project

**That's it!** Your migration is complete. See the :ref:`verification-checklist` below.

.. _migration-path-a-v0-6-x-v0-8-0-full-migration:

Migration Path A: v0.6.x → v0.8.0 (Full Migration)
---------------------------------------------------

.. admonition:: 🏗️ For Legacy Users
   :class: important

   If you're on v0.6.x or earlier with the monolithic structure,
   you need **both migrations** (2-4 hours):

   1. Architectural migration (monolithic → pip-installable)
   2. Rename migration (Alpha Berkeley → Osprey)

Overview
~~~~~~~~

This migration combines:

- **Structural changes**: Moving from embedded applications to standalone repos
- **Import updates**: ``applications.my_app`` → ``my_app`` AND ``framework`` → ``osprey``
- **CLI updates**: Python modules → unified ``osprey`` command
- **Configuration**: Global config → per-application config

Step 1: Install Osprey Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install new package (skip old framework)
   pip install osprey-framework

   # Verify installation
   osprey --version  # Should show 0.8.0+
   osprey --help

Step 2: Create New Application Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option A - Use scaffolding (recommended):**

.. code-block:: bash

   osprey init my-app --template minimal
   cd my-app

**Option B - Manual setup:**

.. code-block:: bash

   mkdir -p my-app/src/my_app/capabilities
   cd my-app
   touch src/my_app/{__init__.py,registry.py,context_classes.py}

Step 3: Copy Application Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # From old monolithic structure
   OLD_REPO=/path/to/alpha_berkeley

   # Copy application code
   cp -r $OLD_REPO/src/applications/my_app/* src/my_app/

   # Copy custom services if any
   if [ -d "$OLD_REPO/services/applications/my_app" ]; then
       cp -r $OLD_REPO/services/applications/my_app/* services/
   fi

Step 4: Update ALL Import Paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need **two sets of replacements**:

**First: Remove applications prefix**

.. code-block:: bash

   # Update all Python files
   find src/my_app -name "*.py" -type f -exec sed -i \
     's/from applications\.my_app/from my_app/g' {} +

   find src/my_app -name "*.py" -type f -exec sed -i \
     's/import applications\.my_app/import my_app/g' {} +

**Second: Update framework to osprey**

.. code-block:: bash

   # Update framework imports to osprey
   find src/my_app -name "*.py" -type f -exec sed -i \
     's/from framework\./from osprey./g' {} +

   # Update string module references
   find src/my_app -name "*.py" -type f -exec sed -i \
     's/"framework\./"osprey./g' {} +

**Verify changes:**

.. code-block:: bash

   # Should find NOTHING:
   grep -r "applications\." src/my_app/
   grep -r "from framework\." src/my_app/

   # Should find your osprey imports:
   grep -r "from osprey\." src/my_app/

**Manual verification:**

.. code-block:: python

   # Check each capability file

   # ❌ OLD (v0.6.x):
   from applications.my_app.capabilities import X
   from framework.state import AgentState

   # ✅ NEW (v0.8.0):
   from my_app.capabilities import X
   from osprey.state import AgentState

Step 5: Update Registry
~~~~~~~~~~~~~~~~~~~~~~~~

Replace verbose registry with helper function:

.. code-block:: python

  # src/my_app/registry.py
  from osprey.registry import (
      extend_framework_registry,
      CapabilityRegistration,
      ContextClassRegistration,
      RegistryConfigProvider,
      ExtendedRegistryConfig
  )

  class MyAppRegistryProvider(RegistryConfigProvider):
      """Registry for My Application."""

      def get_registry_config(self) -> ExtendedRegistryConfig:
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
           )

Step 6: Create Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate base configuration:

.. code-block:: bash

   # Export framework defaults as starting point
   osprey export-config > config.yml

Edit ``config.yml`` to customize:

.. code-block:: yaml

   # Essential settings to update:

   project_name: "my-app"
   project_root: /absolute/path/to/my-app
   registry_path: ./src/my_app/registry.py
   build_dir: ./build

   models:
     orchestrator:
       provider: openai
       model_id: gpt-4
     # ... update all models

Step 7: Update Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create or update ``requirements.txt``:

.. code-block:: text

   osprey-framework>=0.8.0
   # Add your other dependencies

Or ``pyproject.toml``:

.. code-block:: toml

   [project]
   name = "my-app"
   version = "1.0.0"
   dependencies = [
       "osprey-framework>=0.8.0",
       # Add other dependencies
   ]

Step 8: Setup Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Copy environment template
   cp .env.example .env

   # Edit .env with your API keys

Step 9: Validate Setup
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run health check
   osprey health

   # Should report:
   # ✅ Python version
   # ✅ Osprey framework installed
   # ✅ Dependencies available
   # ✅ Config file valid
   # ✅ Registry file found

Step 10: Test Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test CLI
   osprey chat
   # > "Hello, can you help me test?"

   # Start services (optional)
   osprey deploy up

Step 11: Create Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Initialize git
   git init
   git add .
   git commit -m "Initial commit: Migrated to Osprey Framework v0.8.0"

   # Create remote and push
   git remote add origin <your-repo-url>
   git push -u origin main

**Migration complete!** See the :ref:`verification-checklist` below.

Legacy Breaking Changes Reference
----------------------------------

For users migrating from v0.6.x, here are all the breaking changes:

1. Import Paths Changed (Architectural)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All ``applications.*`` imports must be updated:

.. code-block:: python

   # OLD ❌
   from applications.control_assistant.capabilities import ChannelFinding
   from applications.control_assistant.context_classes import ChannelAddressesContext

   # NEW ✅
   from control_assistant.capabilities import ChannelFinding
   from control_assistant.context_classes import ChannelAddressesContext

2. Framework Import Paths Changed (Rename)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All ``framework.*`` imports must be updated to ``osprey.*``:

.. code-block:: python

   # OLD ❌
   from framework.state import AgentState
   from framework.base.capability import BaseCapability

   # NEW ✅
   from osprey.state import AgentState
   from osprey.base.capability import BaseCapability

3. CLI Commands Unified
~~~~~~~~~~~~~~~~~~~~~~~~

New unified CLI with lazy loading:

.. code-block:: bash

   # OLD ❌
   python -m interfaces.CLI.direct_conversation
   python -m deployment.container_manager deploy_up

   # NEW ✅
   osprey chat
   osprey deploy up

See :doc:`../developer-guides/02_quick-start-patterns/00_cli-reference` for complete command reference.

4. Package Name Changed
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # OLD ❌
   pip install alpha-berkeley-framework

   # NEW ✅
   pip install osprey-framework

5. Configuration Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Each application now has its own ``config.yml``:

.. code-block:: yaml

   # OLD: Global framework config
   applications:
     - als_assistant
     - accelerator_assistant

   # NEW: Per-application config
   project_name: "my-app"
   registry_path: ./src/my_app/registry.py
   project_root: /path/to/my-project

**Key differences:**

- No more global framework configuration
- ``registry_path`` specifies exact location of registry file
- All settings self-contained in one config file
- See :doc:`../developer-guides/03_core-framework-systems/06_configuration-architecture`

6. Registry Discovery
~~~~~~~~~~~~~~~~~~~~~

Explicit path-based discovery replaces automatic scanning:

.. code-block:: yaml

   # config.yml
   registry_path: ./src/my_app/registry.py  # Explicit path required

**No more:**

- Automatic scanning of ``applications/`` directory
- Convention-based discovery by directory name
- Multiple applications in one configuration (advanced use case only)

7. Directory Structure
~~~~~~~~~~~~~~~~~~~~~~

Framework components moved:

.. code-block:: text

   OLD                          NEW
   interfaces/        →         src/osprey/interfaces/
   deployment/        →         src/osprey/deployment/
   src/configs/       →         src/osprey/utils/

These are now pip-installed and not directly visible in application repos.

.. _verification-checklist:

Verification & Testing
----------------------

After completing your migration, use this checklist:

Import Verification
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create test_migration.py
   """Test that all imports work."""

   def test_core_imports():
       """Test core framework imports."""
       from osprey.state import AgentState
       from osprey.base.capability import BaseCapability
       from osprey.base.node import BaseNode
       from osprey.registry.manager import RegistryManager
       print("✅ Core imports working")

   def test_app_imports():
       """Test your application imports."""
       from my_app.capabilities.my_capability import MyCapability
       from my_app.registry import registry
       print("✅ Application imports working")

   if __name__ == "__main__":
       test_core_imports()
       test_app_imports()
       print("\n✅ All imports successful!")

CLI Verification
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test basic CLI commands
   osprey --version      # Should show 0.8.0+
   osprey health         # Should pass all checks

   # Test with your project
   osprey export-config --project /path/to/your/project
   osprey chat --project /path/to/your/project --dry-run

Search for Old References
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Should find NOTHING (or only comments):
   grep -r "from framework\." src/
   grep -r "alpha-berkeley-framework" .

   # Should find your new imports:
   grep -r "from osprey\." src/
   grep -r "osprey-framework" requirements.txt pyproject.toml

Run Tests
~~~~~~~~~

.. code-block:: bash

   # Run your existing test suite
   pytest -v

   # Should all pass with new imports

Complete Checklist
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 50 10

   * - Status
     - Task
     - Path
   * - ☐
     - Package installed: ``osprey-framework>=0.8.0``
     - Both
   * - ☐
     - All ``from framework.*`` → ``from osprey.*``
     - Both
   * - ☐
     - All ``"framework.*`` → ``"osprey.*``
     - Both
   * - ☐
     - Updated ``requirements.txt`` / ``pyproject.toml``
     - Both
   * - ☐
     - All ``applications.my_app`` → ``my_app``
     - Path A only
   * - ☐
     - Created separate application repo
     - Path A only
   * - ☐
     - Updated registry with helpers
     - Path A only
   * - ☐
     - Created ``config.yml``
     - Path A only
   * - ☐
     - CLI command works: ``osprey --help``
     - Both
   * - ☐
     - Health check passes: ``osprey health``
     - Both
   * - ☐
     - Tests pass: ``pytest``
     - Both
   * - ☐
     - Application runs successfully
     - Both

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Issue: "ModuleNotFoundError: No module named 'framework'"**

*Solution:* You have old import statements that weren't updated:

.. code-block:: bash

   # Find remaining old imports
   grep -r "from framework\." src/ --include="*.py"

   # Replace them with:
   # from framework.X → from osprey.X

**Issue: "ModuleNotFoundError: No module named 'osprey'"**

*Solution:* New package not installed:

.. code-block:: bash

   pip uninstall alpha-berkeley-framework -y
   pip install osprey-framework
   python -c "import osprey; print(osprey.__version__)"

**Issue: "command not found: osprey"**

*Solution:* Package installed in wrong environment:

.. code-block:: bash

   # Activate correct virtual environment
   source venv/bin/activate

   # Reinstall
   pip install osprey-framework

   # Verify
   which osprey

**Issue: Tests fail after migration**

*Solution:* Check test files for old imports:

.. code-block:: bash

   grep -r "from framework\." tests/ --include="*.py"
   grep -r "applications\." tests/ --include="*.py"

For more help, see:

- GitHub Issues: https://github.com/als-apg/osprey/issues
- Discussions: https://github.com/als-apg/osprey/discussions

Tutorial Applications
~~~~~~~~~~~~~~~~~~~~~

For tutorial applications (``hello_world_weather``, ``control_assistant``), **regenerate instead of migrating**:

.. code-block:: bash

   # Weather tutorial
   osprey init my-weather --template hello_world_weather
   cd my-weather

   # Control Assistant tutorial
   osprey init my-assistant --template control_assistant
   cd my-assistant

Templates are kept up-to-date with framework changes and use latest patterns.

For detailed guidance on using these templates:

* :doc:`Hello World Tutorial <hello-world-tutorial>` - Complete walkthrough of the weather template
* :doc:`Control Systems Tutorial <control-assistant-entry>` - Comprehensive guide to the control assistant template


What's New in v0.8.0
--------------------

Rename to Osprey Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The framework has been renamed to better reflect its evolution:

- **New name**: Osprey Framework 🦅
- **New package**: ``osprey-framework`` (on PyPI)
- **New repository**: https://github.com/als-apg/osprey
- **New docs**: https://als-apg.github.io/osprey

**Why Osprey?**

- Domain-agnostic identity (beyond Berkeley)
- Memorable and distinctive
- Reflects the framework's vision

**Backward compatibility:**

- GitHub automatically redirects old URLs
- All APIs remain the same (import paths only change)

Features from v0.7.0
~~~~~~~~~~~~~~~~~~~~

If you're coming from v0.6.x, you also get:

**Unified CLI:**

.. code-block:: bash

   osprey init <name>        # Create new project
   osprey deploy up          # Start services
   osprey chat               # Interactive conversation
   osprey health             # System diagnostics
   osprey export-config      # View framework defaults

**Registry Helpers:**

.. code-block:: python

   from osprey.registry import extend_framework_registry

   # 70% less code, automatic framework updates
   return extend_framework_registry(
       capabilities=[...],
       exclude_capabilities=["python"]
   )

**Self-Contained Configuration:**

.. code-block:: yaml

   # Everything visible and editable
   # ~320 lines, well-organized
   # No hidden defaults

**Health Diagnostics:**

.. code-block:: bash

   osprey health

   # Comprehensive system validation

**Template System:**

.. code-block:: bash

   osprey init my-app --template hello_world_weather
   osprey init my-app --template control_assistant
   osprey init my-app --template minimal

Getting Help
------------

If you encounter issues during migration:

**Documentation:**

- :doc:`installation` - Fresh installation guide
- :doc:`../developer-guides/index` - Developer documentation
- :doc:`../api_reference/index` - API reference

**Community:**

- GitHub Issues: https://github.com/als-apg/osprey/issues
- Discussions: https://github.com/als-apg/osprey/discussions

**Common Resources:**

- :doc:`../developer-guides/02_quick-start-patterns/00_cli-reference` - CLI commands
- :doc:`../developer-guides/03_core-framework-systems/03_registry-and-discovery` - Registry system
- :doc:`../developer-guides/03_core-framework-systems/06_configuration-architecture` - Configuration

Next Steps
----------

After successful migration:

1. **Learn Best Practices** - Follow the :doc:`Hello World Tutorial <hello-world-tutorial>`
2. **Build Advanced Features** - Work through :doc:`Control Systems Tutorial <control-assistant-entry>`
3. **Explore CLI** - Try all the unified ``osprey`` commands
4. **Update Documentation** - Document your application's new structure
5. **Set Up CI/CD** - Configure automated testing with new imports
6. **Share Feedback** - Report issues at https://github.com/als-apg/osprey/issues

**Happy coding with Osprey Framework v0.8.0!** 🦅

