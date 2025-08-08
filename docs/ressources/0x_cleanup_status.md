# Documentation Cleanup Status Tracker

This document tracks the cleanup progress for all documentation files in the Alpha Berkeley Framework. Each file has two cleanup stages:

- **🔧 Basic Cleanup**: Technical fixes per [cleanup guide](other/cleanup.md) (RST headers, code blocks, cross-references)
- **✨ Expert Curation**: Manual review for formatting, readability, and design choices

## Legend
- ⬜ Not started  
- 🔧 Basic cleanup completed (FROM CLEANUP GUIDE) 
- ✨ HUMAN(!!!) curation completed  
- ❌ File needs major revision/rewrite

---

## 📋 Main Documentation Structure

### Root Documentation
- [ ] `index.rst` - Main landing page ⬜ ⬜

---

## 🚀 Getting Started Section

### Core Files
- [x] `getting-started/index.rst` - Section overview 🔧 ✨
- [x] `getting-started/hello-world-tutorial.rst` - First tutorial 🔧 ✨
- [x] `getting-started/build-your-first-agent.rst` - Agent building guide 🔧 ❌
- [x] `getting-started/installation.rst` - Installation instructions 🔧 ✨

---

## 🧠 Developer Guides Section

### Main Index
- [ ] `developer-guides/index.rst` - Developer guides overview 🔧 ✨

### Understanding the Framework
- [x] `developer-guides/understanding-the-framework/index.rst` - Subsection overview 🔧 ✨
- [x] `developer-guides/understanding-the-framework/convention-over-configuration.rst` - Core principles 🔧 ⬜
- [x] `developer-guides/understanding-the-framework/infrastructure-architecture.rst` - Architecture overview 🔧 ⬜
- [x] `developer-guides/understanding-the-framework/langgraph-integration.rst` - LangGraph integration 🔧 ⬜
- [x] `developer-guides/understanding-the-framework/orchestrator-first-philosophy.rst` - Design philosophy 🔧 ⬜

### Core Framework Systems
- [x] `developer-guides/core-framework-systems/index.rst` - Subsection overview 🔧 ✨
- [x] `developer-guides/core-framework-systems/context-management-system.rst` - Context management 🔧 ⬜
- [x] `developer-guides/core-framework-systems/message-and-execution-flow.rst` - Message flow 🔧 ⬜
- [x] `developer-guides/core-framework-systems/registry-and-discovery.rst` - Registry system 🔧 ⬜
- [x] `developer-guides/core-framework-systems/state-management-architecture.rst` - State management 🔧 ⬜

### Infrastructure Components
- [ ] `developer-guides/infrastructure-components/index.rst` - Subsection overview 🔧 ✨
- [ ] `developer-guides/infrastructure-components/gateway-architecture.rst` - Gateway system 🔧 ⬜
- [ ] `developer-guides/infrastructure-components/task-extraction-system.rst` - Task extraction 🔧 ⬜
- [ ] `developer-guides/infrastructure-components/classification-and-routing.rst` - Classification 🔧 ⬜
- [ ] `developer-guides/infrastructure-components/orchestrator-planning.rst` - Planning system 🔧 ⬜
- [ ] `developer-guides/infrastructure-components/message-generation.rst` - Message generation 🔧 ⬜
- [ ] `developer-guides/infrastructure-components/error-handling-infrastructure.rst` - Error handling 🔧 ⬜

### Quick Start Patterns
- [x] `developer-guides/quick-start-patterns/index.rst` - Subsection overview 🔧 ✨
- [x] `developer-guides/quick-start-patterns/building-your-first-capability.rst` - Capability building 🔧 ⬜
- [x] `developer-guides/quick-start-patterns/running-and-testing.rst` - Testing guide 🔧 ⬜
- [x] `developer-guides/quick-start-patterns/state-and-context-essentials.rst` - State essentials 🔧 ⬜

### Production Systems
- [x] `developer-guides/production-systems/index.rst` - Subsection overview 🔧 ✨
- [x] `developer-guides/production-systems/container-and-deployment.rst` - Deployment guide 🔧 ⬜
- [x] `developer-guides/production-systems/data-source-integration.rst` - Data integration 🔧 ⬜
- [x] `developer-guides/production-systems/human-approval-workflows.rst` - Approval workflows 🔧 ⬜
- [x] `developer-guides/production-systems/memory-storage-service.rst` - Memory service 🔧 ⬜
- [x] `developer-guides/production-systems/python-execution-service.rst` - Python execution 🔧 ⬜

---

## 📚 API Reference Section

### Main Index
- [ ] `api_reference/index.rst` - API reference overview 🔧 ✨

### Core Framework
- [ ] `api_reference/core_framework/index.rst` - Core framework API 🔧 ✨
- [ ] `api_reference/core_framework/base_components.rst` - Base components 🔧 ⬜
- [ ] `api_reference/core_framework/configuration_system.rst` - Configuration API 🔧 ⬜
- [ ] `api_reference/core_framework/prompt_management.rst` - Prompt API 🔧 ⬜
- [ ] `api_reference/core_framework/registry_system.rst` - Registry API 🔧 ⬜
- [ ] `api_reference/core_framework/state_and_context.rst` - State API 🔧 ⬜

### Infrastructure
- [ ] `api_reference/infrastructure/index.rst` - Infrastructure API 🔧 ✨
- [ ] `api_reference/infrastructure/gateway.rst` - Gateway API 🔧 ⬜
- [ ] `api_reference/infrastructure/classification.rst` - Classification API 🔧 ⬜
- [ ] `api_reference/infrastructure/task-extraction.rst` - Task extraction API 🔧 ⬜
- [ ] `api_reference/infrastructure/orchestration.rst` - Orchestration API 🔧 ⬜
- [ ] `api_reference/infrastructure/message-generation.rst` - Message API 🔧 ⬜
- [ ] `api_reference/infrastructure/execution-control.rst` - Execution control API 🔧 ⬜

### Production Systems
- [ ] `api_reference/production_systems/index.rst` - Production systems API 🔧 ✨
- [ ] `api_reference/production_systems/container-management.rst` - Container management API 🔧 ⬜
- [ ] `api_reference/production_systems/data-management.rst` - Data management API 🔧 ⬜
- [ ] `api_reference/production_systems/human-approval.rst` - Approval API 🔧 ⬜
- [ ] `api_reference/production_systems/memory-storage.rst` - Memory storage API 🔧 ⬜
- [ ] `api_reference/production_systems/python-execution.rst` - Python execution API 🔧 ⬜


### Error Handling 
- [ ] `api_reference/error_handling/index.rst` - Clean overview + navigation 🔧 ✨
- [ ] `api_reference/error_handling/classification_system.rst` - Core classes + classification 🔧 ⬜  
- [ ] `api_reference/error_handling/exception_reference.rst` - Complete exception catalog 🔧 ⬜
- [ ] `api_reference/error_handling/recovery_coordination.rst` - Router + infrastructure patterns 🔧 ⬜


### Framework Utilities
- [ ] `api_reference/framework_utilities/index.rst` - Utilities API 🔧 ⬜



---

## 💡 Example Applications Section
- [ ] `example-applications/index.rst` - Examples overview 🔧 ✨

---

## 🤝 Contributing Section
- [ ] `contributing/index.rst` - Contributing guide 🔧 ✨
