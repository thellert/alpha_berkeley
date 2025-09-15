Installation & Setup
====================

Alpha-Berkeley - Getting Started Notes
---------------------------------------

Prerequisites
~~~~~~~~~~~~~

**Install Podman**

`Podman <https://podman.io/>`_ is a daemonless container engine that serves as an alternative to Docker. Unlike Docker, which requires a privileged daemon running as root, Podman can run containers without a daemon and supports true rootless operation. This architecture provides several security advantages: reduced attack surface, better privilege separation, and no need for a constantly running root process. While Docker can be complex to secure in enterprise environments, Podman's design makes it inherently more secure and easier to integrate into systems with strict security requirements. In a nutshell, if you want to make your sysadmin happy(ier!), use Podman for security reasons.

To get the latest installation instructions for Podman, visit the `official Podman installation guide <https://podman.io/docs/installation>`_.

After you finish the installation, check if your Podman version is at least 5.0.0 and run the "hello-world" Podman container:

.. code-block:: bash

   podman --version
   podman run hello-world

If the "hello-world" container runs successfully and displays a welcome message, you can proceed to the next step.

**Running Podman Machine (macOS/Windows only)**

After the successful installation, if you're on macOS or Windows, you need to initialize and start the podman machine:

.. code-block:: bash

   podman machine init
   podman machine start

**Note:** Linux users can skip this step as Podman runs natively on Linux.

**Environment Setup**

**Python 3.11 Requirement**

This framework requires `Python 3.11 <https://www.python.org/downloads/>`_. Verify you have the correct version:

.. code-block:: bash

   python3.11 --version

**Virtual Environment Setup**

To avoid conflicts with your system Python packages, create a virtual environment with Python 3.11:

.. code-block:: bash

   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

**Installing Dependencies**

After creating and activating the virtual environment, install the required packages:

.. code-block:: bash

   # Upgrade pip to latest version
   pip install --upgrade pip
   
   # Install main framework requirements (includes LangGraph, AI/ML tools, scientific computing)
   pip install -r requirements.txt
   
   # Optional: Install documentation requirements (only needed if building docs)
   # pip install -r docs/requirements.txt

The main `requirements.txt` file includes:

* **Core Framework**: `LangGraph <https://www.langchain.com/langgraph>`_, `LangChain <https://www.langchain.com/>`_, `Pydantic-AI <https://ai.pydantic.dev/>`_
* **AI/ML Integrations**: `Anthropic <https://www.anthropic.com/>`_, `OpenAI <https://openai.com/>`_, `Ollama <https://ollama.com/>`_
* **Scientific Computing**: `NumPy <https://numpy.org/>`_, `Pandas <https://pandas.pydata.org/>`_, SciPy, Matplotlib, Scikit-learn
* **ALS-Specific**: ALS Archiver Client, PyEPICS
* **Container Management**: `Podman <https://podman.io/>`_, Podman-compose
* **Development Tools**: `Jupyter <https://jupyter.org/>`_, Rich, NLTK

.. _Configuration:

Configuration
~~~~~~~~~~~~~

**Update config.yml**

Modify the following settings in ``config.yml``:

1. **Project Root Path**: Update ``project_root`` in ``config.yml`` to your repository path. Either set ``PROJECT_ROOT`` in your ``.env`` file (recommended for multiple machines) or hard-code the path directly in the YAML file.

2. **Ollama Base URL**: Set the base URL for `Ollama <https://ollama.com/>`_
   
   - For direct host access: ``localhost:11434``
   - For container-based agents (like OpenWebUI pipelines): ``host.containers.internal:11434``
   - See `Ollama Connection`_ for OpenWebUI-specific configuration

3. **Deployed Services**: In the deployed services section, ensure the following are uncommented:
   
   - ``framework-jupyter`` - this environment is intended to give users the capability to edit and run the alpha-berkeley generated codes
   - ``framework.open_webui`` - this is the entry point for the user, where you communicate interactively through `OpenWebUI <https://openwebui.com/>`_, a convenient web-based chat interface for LLMs
   - ``framework.pipelines`` - this is the core environment

4. **API URL**: If you are using `CBORG <https://cborg.lbl.gov/>`_ as your model provider (LBNL internal only), set the CBORG API URL to either:
   
   - Global API URL: ``https://api.cborg.lbl.gov/v1``
   - Local API URL: ``https://api-local.cborg.lbl.gov/v1`` (requires local network connection)
   
   In ``./config.yml``, update: ``api: providers:cborg:base_url: https://api-local.cborg.lbl.gov/v1``

5. **For External Users (Non-LBNL)**: If you don't have access to CBORG, you'll need to configure alternative model providers in ``config.yml`` and ``src/framework/config.yml``. Update the ``provider`` fields under the ``models`` section to use providers like ``openai``, ``anthropic``, ``ollama``, or others you have access to. Ensure corresponding API keys are set in your ``.env`` file.

**Environment Variables**

Create a ``.env`` file with API keys:

.. code-block:: bash

   cp env.example .env

Edit the ``.env`` file and provide the API keys for the model providers you are using.

Documentation
~~~~~~~~~~~~~

**Compile Documentation (Optional)**

If you want to build and serve the documentation locally:

.. code-block:: bash

   # Install documentation dependencies
   pip install -r docs/requirements.txt
   
   # Build and serve documentation
   cd docs/
   python launch_docs.py

Once running, you can view the documentation at http://localhost:8082

Building and Running
~~~~~~~~~~~~~~~~~~~~

Once you have installed everything and compiled documentation, you can execute the build and run script. This will download all the necessary packages, run them as safe Podman containers and secure the communication between them.

**Start Services**

The framework uses a container manager to orchestrate all services. For detailed information about all container management options, see :doc:`../developer-guides/05_production-systems/05_container-and-deployment`.

.. tab-set::

    .. tab-item:: Development Mode (Recommended for starters)

        **For initial setup and debugging**, start services one by one in non-detached mode:

        1. Comment out all services except one in your ``config.yml`` under ``deployed_services``
        2. Start the first service:

        .. code-block:: bash

           python3 ./deployment/container_manager.py config.yml up

        3. Monitor the logs to ensure it starts correctly
        4. Once stable, stop with ``Ctrl+C`` and uncomment the next service
        5. Repeat until all services are working

        This approach helps identify issues early and ensures each service is properly configured before proceeding.

    .. tab-item:: Production Mode

        **Once all services are tested individually**, start everything together in detached mode:

        .. code-block:: bash

           python3 ./deployment/container_manager.py config.yml up -d

        This runs all services in the background, suitable for production deployments where you don't need to monitor individual service logs.

**Verify Services are Running**

Check that services are running properly:

.. code-block:: bash

   podman ps

**Access OpenWebUI**

Once services are running, access the web interface at:

- OpenWebUI: `http://localhost:8080 <http://localhost:8080>`_

OpenWebUI Configuration
~~~~~~~~~~~~~~~~~~~~~~~

`OpenWebUI <https://openwebui.com/>`_ is a feature-rich, self-hosted web interface for Language Models that provides a ChatGPT-like experience with extensive customization options. The framework's integration provides real-time progress tracking during agent execution, automatic display of :func:`registered figures <framework.state.StateManager.register_figure>` and :func:`notebooks <framework.state.StateManager.register_notebook>`, and session continuity across conversations.

.. _Ollama Connection:

**Ollama Connection:**

For Ollama running on localhost, use ``http://host.containers.internal:11434`` instead of ``http://localhost:11434`` because Podman containers cannot access the host's localhost directly. This should match your ``config.yml`` Ollama base URL setting (see `Configuration`_ section above).

Once the correct URL is configured and Ollama is serving, `OpenWebUI <https://openwebui.com/>`_ will automatically discover all models currently available in your Ollama installation.

**Pipeline Connection:**

The Alpha Berkeley framework provides a pipeline connection to the OpenWebUI service.

.. dropdown:: Understanding Pipelines
   :color: info
   :icon: info

   `OpenWebUI Pipelines <https://docs.openwebui.com/pipelines/>`_ are a powerful extensibility system that allows you to customize and extend OpenWebUI's functionality. Think of pipelines as plugins that can:

   - **Filter**: Process user messages before they reach the LLM and modify responses after they return
   - **Pipe**: Create custom "models" that integrate external APIs, build workflows, or implement RAG systems
   - **Integrate**: Connect with external services, databases, or specialized AI providers

   Pipelines appear as models with an "External" designation in your model selector and enable advanced functionality like real-time data retrieval, custom processing workflows, and integration with external AI services.

1. Go to **Admin Panel** → **Settings** (upper panel) → **Connections** (left panel)
2. Click the **(+)** button in **Manage OpenAI API Connections**
3. Configure the pipeline connection with these details:
   
   - **URL**: ``http://pipelines:9099`` (if using default configuration)
   - **API Key**: Found in ``services/framework/pipelines/docker-compose.yml.j2`` under ``PIPELINES_API_KEY`` (default ``0p3n-w3bu!``)
   
   **Note**: The URL uses ``pipelines:9099`` instead of ``localhost:9099`` because OpenWebUI runs inside a container and communicates with the pipelines service through the container network.





**Additional OpenWebUI Configuration:**

For optimal performance and user experience, consider these additional configuration settings:

.. tab-set::

    .. tab-item:: Model Management

        **Making Models Public:**

        To use Ollama models for OpenWebUI features like chat tagging, title generation, and other automated tasks, you must configure them as public models:

        1. Go to **Admin Panel** → **Settings** → **Models**
        2. Find the Ollama model you want to use (e.g., ``mistral:7b``, ``llama3:8b``)
        3. Click the **edit button** (pencil icon) next to the model
        4. Ensure the model is **activated** (enabled)
        5. Set the model visibility to **Public** (not Private)
        6. Click **Save** to apply the changes

        **Deactivating Unused Models:**

        - Deactivate unused (Ollama-)models in **Admin Panel** → **Settings** → **Models** to reduce clutter
        - This helps keep your model selection interface clean and focused on the models you actually use
        - You can always reactivate models later if needed

    .. tab-item:: Chat Augmentation

        OpenWebUI automatically generates titles and tags for conversations, which can interfere with your main agent's processing. It's recommended to use a dedicated local model for this:

        1. Go to **Admin Panel** → **Settings** → **Interface** 
        2. Find **Task Model** setting
        3. Change from **Current Model** to any local Ollama model (e.g., ``mistral:7b``, ``llama3:8b``)
        4. This prevents title generation from consuming your main agent's resources

        Note that this model needs to be public as well (see `Model Management`_ section to the left).

    .. tab-item:: Buttons

        **Adding Custom Function Buttons:**

        OpenWebUI allows you to add custom function buttons to enhance the user interface. For comprehensive information about functions, see the `official OpenWebUI functions documentation <https://docs.openwebui.com/features/plugin/>`_.

        **Installing Functions:**

        1. Navigate to **Admin Panel** → **Functions**
        2. Add a function using the plus sign (UI details may vary between OpenWebUI versions)
        3. Copy and paste function code from our repository's pre-built functions

        **Available Functions in Repository:**

        The framework includes several pre-built functions located in ``services/framework/open-webui/functions/``:

        - ``execution_history_button.py`` - View and manage execution history
        - ``agent_context_button.py`` - Access agent context information  
        - ``memory_button.py`` - Memory management functionality
        - ``execution_plan_editor.py`` - Edit and manage execution plans

        **Activation Requirements:**

        After adding a function:

        1. **Enable the function** - Activate it in the functions interface
        2. **Enable globally** - Use additional options to enable the function globally
        3. **Refresh the page** - The button should appear on your OpenWebUI interface after refresh

        These buttons provide quick access to advanced agent capabilities and debugging tools.

    .. tab-item:: Debugging

        **Real-time Log Viewer:**

        For debugging and monitoring, use the ``/logs`` command in chat to view application logs without accessing container logs directly:

        - ``/logs`` - Show last 100 log entries
        - ``/logs 50`` - Show last 50 log entries  
        - ``/logs help`` - Show available options

        This is particularly useful for troubleshooting when OpenWebUI provides minimal feedback by design.

    .. tab-item:: Default Prompts

        **Customizing Default Prompt Suggestions:**

        OpenWebUI provides default prompt suggestions that you can customize for your specific use case:

        **Accessing Default Prompts:**

        1. Go to **Admin Panel** → **Settings** → **Interface**
        2. Scroll down to find **Default Prompt Suggestions** section
        3. Here you can see the built-in OpenWebUI prompt suggestions

        **Customizing Prompts:**

        1. **Remove Default Prompts**: Clear the existing default prompts if they don't fit your workflow
        2. **Add Custom Prompts**: Replace them with prompts tailored to your agent's capabilities
        3. **Use Cases**:
           
           - **Production**: Set prompts that guide users toward your agent's core functionalities
           - **R&D Testing**: Create prompts that help test specific features or edge cases
           - **Domain-Specific**: Add prompts relevant to your application domain (e.g., ALS operations, data analysis)

        **Example Custom Prompts:**

        - "Analyze the recent beam performance data from the storage ring"
        - "Find PV addresses related to beam position monitors"
        - "Generate a summary of today's logbook entries"
        - "Help me troubleshoot insertion device issues"

        **Benefits:**

        - Guides users toward productive interactions with your agent
        - Reduces cognitive load for new users
        - Enables consistent testing scenarios during development
        - Improves user adoption by showcasing agent capabilities


Troubleshooting
~~~~~~~~~~~~~~~

**Common Issues:**

- If you encounter connection issues with Ollama, ensure you're using ``host.containers.internal`` instead of ``localhost`` when connecting from containers
- Verify that all required services are uncommented in ``config.yml``
- Check that API keys are properly set in the ``.env`` file
- Ensure podman machine is running before starting services (macOS/Windows)
- If containers fail to start, check logs with: ``podman logs <container_name>``

**Verification Steps:**

1. Check Python version: ``python --version`` (should be 3.11.x)
2. Check Podman version: ``podman --version`` (should be 5.0.0+)
3. Verify virtual environment is active (should see ``(venv)`` in your prompt)
4. Test core framework imports: ``python -c "import langgraph; print('LangGraph installed successfully')"``
5. Test container connectivity: ``podman run --rm alpine ping -c 1 host.containers.internal``
6. Check service status: ``podman ps``

**Common Installation Issues:**

- **Python version mismatch**: Ensure you're using Python 3.11 with ``python3.11 -m venv venv``
- **Package conflicts**: If you get dependency conflicts, try creating a fresh virtual environment
- **Missing dependencies**: The main requirements.txt should install everything needed; avoid mixing with system packages