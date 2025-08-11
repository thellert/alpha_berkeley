Alpha Berkeley Framework Documentation
======================================

.. admonition:: 🚧 Early Access Documentation
   :class: warning

   **Current Release**: |release| Early Access  

   This documentation is part of an early access release and is **under active development**.  
   Many sections are still being written, edited, or reorganized.  
   Expect **inconsistencies**, missing content, outdated references, and broken cross-links.

   We welcome feedback! If you find issues or have suggestions, please open an issue on our GitHub page.


What is Alpha Berkeley Framework?
----------------------------------

The **Alpha Berkeley Framework** provides a production-ready architecture for building domain-specific agentic systems. Built on :doc:`LangGraph's StateGraph foundation <developer-guides/01_understanding-the-framework/03_langgraph-integration>`, it implements a structured pipeline that transforms natural language inputs into reliable, orchestrated execution plans.

The framework addresses common challenges in agentic system development: :doc:`tool management at scale <developer-guides/03_core-framework-systems/03_registry-and-discovery>`, :doc:`structured orchestration without hallucination <developer-guides/01_understanding-the-framework/04_orchestrator-first-philosophy>`, and seamless integration of :doc:`human oversight workflows <api_reference/03_production_systems/01_human-approval>`.

Core Architecture
------------------

.. figure:: workflow_overview.png
   :alt: Alpha Berkeley Framework Architecture
   :align: center
   :width: 100%
   
   The framework architecture illustrates the process flow from natural language input to orchestrated execution, encompassing: **Task Extraction** → **Classification** → **Orchestration** → **Execution**.

The framework provides:

* **Capability-Based Architecture**: :doc:`Modular agent construction <developer-guides/02_quick-start-patterns/01_building-your-first-capability>` with selective capability activation based on task requirements
* **Orchestrator-First Design**: :doc:`Complete execution planning <developer-guides/04_infrastructure-components/04_orchestrator-planning>` prior to capability invocation, eliminating iterative tool-calling patterns
* **Secure Python Execution**: :doc:`Containerized code generation and execution <developer-guides/05_production-systems/03_python-execution-service>` with static analysis, human approval, and flexible deployment environments
* **Registry-Based Discovery**: :doc:`Convention-driven component loading <developer-guides/01_understanding-the-framework/02_convention-over-configuration>` enables seamless integration of capabilities, data sources, and services across applications
* **LangGraph Integration**: Native StateGraph workflows with :doc:`checkpoints, interrupts <developer-guides/01_understanding-the-framework/03_langgraph-integration>`, and :doc:`persistent state management <developer-guides/03_core-framework-systems/01_state-management-architecture>`
* **Human-in-the-Loop Integration**: :ref:`Transparent execution plans <planning-mode-example>` with :doc:`approval workflows <developer-guides/05_production-systems/01_human-approval-workflows>` for high-stakes operational environments
* **Domain Abstraction**: Framework patterns applicable across diverse infrastructure, from :doc:`simple agents <getting-started/hello-world-tutorial>` to complex :doc:`multi-capability systems <getting-started/build-your-first-agent>`


Documentation Structure
-----------------------

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: 🚀 Getting Started
      :link: getting-started/index
      :link-type: doc
      :class-header: bg-primary text-white
      
      Complete implementation guide from environment setup to production deployment, including tutorial applications.

   .. grid-item-card:: 🧠 Developer Guides
      :link: developer-guides/index
      :link-type: doc
      :class-header: bg-info text-white
      
      Architectural concepts and implementation patterns for building sophisticated agentic systems.

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: 📚 API Reference
      :link: api_reference/index
      :link-type: doc
      :class-header: bg-secondary text-white
      
      Complete technical reference for all framework components and interfaces.

   .. grid-item-card:: 💡 Applications
      :link: example-applications/index
      :link-type: doc
      :class-header: bg-success text-white
      
      Reference implementations demonstrating framework usage across different domains.

   .. grid-item-card:: 🤝 Contributing
      :link: contributing/index
      :link-type: doc
      :class-header: bg-warning text-white
      
      Framework internals, development guidelines, and contribution workflows.

.. toctree::
   :hidden:

   getting-started/index
   developer-guides/index
   api_reference/index
   example-applications/index
   contributing/index

