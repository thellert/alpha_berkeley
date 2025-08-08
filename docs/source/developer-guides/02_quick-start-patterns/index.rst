====================
Quick Start Patterns
====================

.. toctree::
   :maxdepth: 2
   :caption: Quick Start Patterns
   :hidden:

   01_building-your-first-capability
   02_state-and-context-essentials
   03_running-and-testing

.. dropdown:: What You'll Learn
   :color: primary
   :icon: book

   **Essential Development Skills:**
   
   - Building production-ready capabilities with @capability_node decorator patterns
   - Working with AgentState, StateManager, and ContextManager for data flow
   - Creating type-safe Pydantic context classes for component communication
   - Testing and debugging workflows using Gateway architecture
   - Registry-based component discovery and framework integration

   **Prerequisites:** Python development experience and basic framework understanding
   
   **Target Audience:** Developers building their first agentic system capabilities

Get productive immediately with the Alpha Berkeley Framework's essential development patterns. Each guide focuses on specific skills you need to build effective agent capabilities.

.. grid:: 1 1 1 3
   :gutter: 3

   .. grid-item-card:: 🏗️ Build Your First Capability
      :link: 01_building-your-first-capability
      :link-type: doc
      :class-header: bg-success text-white
      :class-body: text-center
      :shadow: md

      **Start here for hands-on development**
      
      Step-by-step implementation of BaseCapability with @capability_node decorator and framework integration.
      
      *30-45 minutes*

   .. grid-item-card:: 🔄 State and Context Essentials  
      :link: 02_state-and-context-essentials
      :link-type: doc
      :class-header: bg-info text-white
      :class-body: text-center
      :shadow: md

      **Master data management patterns**
      
      AgentState, StateManager utilities, ContextManager, and type-safe data exchange between capabilities.
      
      *15-20 minutes*

   .. grid-item-card:: 🧪 Running and Testing
      :link: 03_running-and-testing
      :link-type: doc
      :class-header: bg-warning text-white
      :class-body: text-center
      :shadow: md

      **Test and deploy your work**
      
      Gateway architecture, CLI interface, debugging workflows, and production deployment patterns.
      
      *15-20 minutes*

**Recommended order:** Build → State → Testing, but each guide stands alone for specific needs.

.. dropdown:: 🚀 Next Steps
   
   After mastering these patterns, explore advanced framework topics:

   - :doc:`../03_core-framework-systems/index` - Deep framework internals and sophisticated patterns
   - :doc:`../04_infrastructure-components/index` - Gateway architecture and processing pipeline
   - :doc:`../05_production-systems/index` - Enterprise deployment and approval workflows