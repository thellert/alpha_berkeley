# Changelog

All notable changes to the Alpha Berkeley Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-10-25

### 🎉 Major Architecture Release - Framework Decoupling

This is a **major breaking release** that fundamentally changes how applications are built and deployed. The framework is now pip-installable, enabling independent application development in separate repositories.

### Added

#### Unified CLI System
- **`framework` command** - Main CLI entry point with lazy loading for fast startup
- **`framework init`** - Create new projects from templates with project scaffolding
  - Templates: minimal, hello_world_weather, wind_turbine
  - Options: `--template`, `--registry-style`, `--output-dir`, `--force`
- **`framework deploy`** - Manage Docker services (up/down/restart/status/rebuild/clean)
  - Intelligent service management with validation
  - Service health checking
- **`framework chat`** - Interactive CLI conversation interface
- **`framework health`** - Comprehensive system diagnostics
  - Validates Python version, dependencies, configuration, registry files, containers
  - ~968 lines of diagnostic code
- **`framework export-config`** - View framework default configuration template
  - Supports YAML and JSON output
  - Helps understand configuration options

#### Template System
- **3 Production-Ready Templates** - Instant project generation
  - `minimal` - Bare-bones starter with TODO placeholders
  - `hello_world_weather` - Simple weather query example
  - `wind_turbine` - Complex multi-capability monitoring system
- **Project Scaffolding** - Complete self-contained projects
  - Application code (capabilities, registry, context classes)
  - Service configurations (Jupyter, OpenWebUI, Pipelines)
  - Self-contained configuration (~320 lines)
  - Environment template (.env.example)
  - Dependencies file (pyproject.toml)
  - Getting started documentation

#### Registry Helper Functions
- **`extend_framework_registry()`** - Simplify application registries by ~70%
  - Compact style: 5-10 lines instead of 80+ lines of boilerplate
  - Automatic framework component inclusion
  - Clean exclusion syntax: `exclude_capabilities=["python"]`
  - Optional override support for advanced customization
- **`get_framework_defaults()`** - Inspect framework components
- **Progressive disclosure** - Start simple, go explicit when needed

#### Path-Based Discovery
- **Explicit registry file paths** in `config.yml`
- **`registry_path`** configuration (top-level or nested)
- **`importlib.util` based loading** - Robust module loading
- **Temporary sys.path manipulation** - Like Django, Sphinx, Airflow
- **Strict validation** - Exactly one `RegistryConfigProvider` per file
- **Rich error messages** - Comprehensive resolution hints

#### Self-Contained Configuration
- **One `config.yml` per application** - Complete transparency
- **~320 lines** - All framework settings visible and editable
- **Framework defaults included** at project creation
- **`.env` file support** - Automatic loading with python-dotenv
- **Well-organized** - Clear section comments for easy navigation

#### Documentation
- **Migration Guide** - Comprehensive upgrade documentation (~730 lines)
  - Breaking changes overview
  - Step-by-step migration instructions (10 steps)
  - Production and tutorial migration paths
  - Common issues and solutions
  - Migration progress checklist
- **Updated Getting Started** - Fresh installation and migration paths
- **CLI Reference** - Complete command documentation
- **Registry Helper Documentation** - Helper function usage and examples

### Changed

#### Breaking Changes - Repository Structure
- **Framework** → Pip-installable package (`alpha-berkeley-framework`)
- **Applications** → Separate repositories (production) or templates (tutorials)
- **`interfaces/`** → `src/framework/interfaces/` (pip-installed)
- **`deployment/`** → `src/framework/deployment/` (pip-installed)
- **`src/configs/`** → `src/framework/utils/` (merged)

#### Breaking Changes - Import Paths
```python
# OLD ❌
from applications.my_app.capabilities import MyCapability

# NEW ✅
from my_app.capabilities import MyCapability
```

All `applications.*` imports must be updated to package names.

#### Breaking Changes - CLI Commands
```bash
# OLD ❌
python -m interfaces.CLI.direct_conversation
python -m deployment.container_manager deploy_up

# NEW ✅
framework chat
framework deploy up
```

#### Breaking Changes - Configuration
- **Per-application config** - Each app has own `config.yml`
- **No global framework config** - Self-contained configuration
- **`registry_path` required** - Explicit registry file location
- **All settings visible** - Complete transparency (~320 lines)

#### Breaking Changes - Discovery
- **Explicit path-based discovery** - No automatic `applications/` scanning
- **Registry must be importable** - Proper Python package structure required
- **Exactly one provider per file** - Strict enforcement

### Enhanced

#### Performance
- **Lazy Loading CLI** - Heavy dependencies loaded only when needed
- **Fast Help Display** - `framework --help` loads instantly
- **Immediate Code Changes** - No reinstall/rebuild required

#### Developer Experience
- **Template-Based Generation** - New projects in seconds
- **Registry Helpers** - 70% less boilerplate code
- **Health Diagnostics** - Comprehensive validation with one command
- **Self-Contained Config** - All settings in one place
- **Natural Imports** - Module paths match package structure

#### Backward Compatibility
- **Legacy entry points maintained** - `alpha-berkeley`, `alpha-berkeley-deploy` still work
- **Registry interface preserved** - `RegistryConfigProvider` unchanged
- **Core functionality maintained** - All framework features work as before

### Migration Guide

#### For Production Applications
1. Install framework: `pip install alpha-berkeley-framework`
2. Create new repository structure
3. Copy application code to new structure
4. Update import paths (find-and-replace `applications.` → ``)
5. Simplify registry with `extend_framework_registry()`
6. Create self-contained `config.yml`
7. Setup `.env` file with API keys
8. Validate with `framework health`
9. Test functionality with `framework chat`
10. Initialize git repository and push

#### For Tutorial Applications
Regenerate from templates:
```bash
framework init my-weather --template hello_world_weather
framework init my-turbine --template wind_turbine
```

#### Complete Instructions
See comprehensive migration guide:
https://thellert.github.io/alpha_berkeley/getting-started/migration-guide

### Implementation Stats
- **100+ tasks completed** across 6 implementation phases
- **CLI infrastructure** - 5 commands with lazy loading (~2000 lines)
- **Template system** - 3 app templates + project + services
- **Registry helpers** - `extend_framework_registry()` (~200 lines)
- **Migration guide** - Comprehensive documentation (~730 lines)
- **Health diagnostics** - System validation (~968 lines)

### Related Issues
- Implements [#8 - Decouple Applications from Framework Repository](https://github.com/thellert/alpha_berkeley/issues/8)

## [0.6.0] - 2025-10-14

### Added
- **Performance Optimization System**: Configurable bypass modes for task extraction and capability selection
- **Task Extraction Bypass**: Skip LLM-based task extraction and use full conversation context for downstream processing
- **Capability Selection Bypass**: Skip LLM-based classification and activate all registered capabilities
- **Runtime Slash Commands**: Added `/task:off`, `/task:on`, `/caps:off`, `/caps:on` for dynamic performance control
- **Configuration Support**: New `agent_control` section in config.yml with bypass settings and system-wide defaults
- **Comprehensive Documentation**: Added bypass mode documentation with use cases, tradeoffs, and real CLI examples

### Enhanced
- **Gateway**: Parse and apply new performance bypass slash commands with readable command formatting
- **Task Extraction Node**: Implement bypass logic that formats full chat history and data sources without LLM processing
- **Classification Node**: Implement bypass logic that activates all capabilities without LLM analysis
- **State Manager**: Add bypass configuration defaults to agent_control state
- **Documentation**: Cross-referenced gateway, task extraction, and classification docs with performance configuration section

### Fixed
- **Data Source Request Creation**: Fixed user_id extraction to properly use session info instead of non-existent state field

### Performance Benefits
- Reduced LLM call overhead in preprocessing pipeline (1-2 fewer LLM calls per request)
- Flexible performance tuning for R&D, debugging, and high-throughput scenarios
- Trade orchestration complexity for extraction/classification speed based on use case
- Configurable via both system defaults and runtime slash commands

## [0.5.1] - 2025-10-13

### Fixed
- **Task Extraction Data Integration**: Enhanced task extraction to properly format retrieved data content from external sources
- **LLM Context Quality**: Improved the quality of context provided to task extraction for better results
- **Data Source Formatting**: Added robust fallback handling for data source content formatting

## [0.5.0] - 2025-09-26

### Added
- **ALS Assistant Application**: Complete domain-specific application for Advanced Light Source operations
- **PV Finder Service**: Intelligent EPICS process variable discovery with MCP integration
- **Application Launcher Service**: Desktop integration with MCP protocol support
- **Comprehensive Knowledge Base**: ALS accelerator objects database, PV naming structures, and MATLAB codebase analysis
- **Observability Integration**: Langfuse support with Docker containerization
- **Data Analysis Capabilities**: 7 new capability modules for accelerator physics operations
- **Infrastructure Services**: MongoDB database service, container orchestration for specialized services

### Enhanced
- **Container Execution**: Improved WebSocket connectivity, proxy handling, and error recovery
- **UI State Management**: Renamed `ui_notebook_links` to `ui_captured_notebooks` for clarity
- **Documentation**: Complete RST documentation with architectural diagrams and setup guides
- **Benchmarking Suite**: Performance analysis tools and model comparison frameworks

### Technical Details
- Added 144 new files with 430,647 lines of code
- Integrated MCP (Model Context Protocol) for external service communication
- Enhanced Docker compose templates with Langfuse environment variables
- Added comprehensive test coverage for core ALS services
- Implemented specialized databases for accelerator operations (11k+ PVs, AO structures)
- Enhanced framework capabilities with domain-specific prompt engineering

This release represents the framework's first complete domain-specific application, demonstrating the capability-based architecture's effectiveness for specialized scientific computing environments.

## [0.4.5] - 2025-09-23

### Added
- **Centralized Launchable Commands System**: New infrastructure for registering and displaying executable commands (web apps, desktop tools) through both CLI and OpenWebUI interfaces
- **Enhanced UI Result Display**: Comprehensive display system for figures, commands, and notebooks with rich formatting and metadata
- **MCP Protocol Support**: Added `fastmcp` dependency for Model Context Protocol integrations

### Enhanced
- **CLI Interface**: Added comprehensive result display methods with formatted output for figures, commands, and notebooks
- **OpenWebUI Interface**: Refactored result extraction with improved command and notebook handling
- **Configuration Management**: Enhanced path resolution with host/container awareness and application-specific file paths
- **State Management**: New `ui_launchable_commands` registry and `StateManager.register_command()` method
- **Response Generation**: Updated prompts to handle command display with interface-aware formatting

### Improved
- **Documentation**: Reorganized static resources following Sphinx best practices
- **Service Configuration**: Streamlined deployed services configuration with better maintainability
- **Error Handling**: Enhanced logging and fallback mechanisms throughout UI components

### Technical Details
- Added `ui_launchable_commands` field to AgentState for centralized command registry
- Implemented command registration system for capability-agnostic command handling  
- Enhanced `get_agent_dir()` with `host_path` parameter for container/host path control
- Updated response context with `commands_available` field for UI awareness
- Improved container environment detection and path resolution

## [0.4.4] - 2025-09-17

### Refactored
- **Example Formatting System**: Consolidated example formatting with unified `BaseExample.join()` static method
- **Code Deduplication**: Removed duplicate `format_examples_for_prompt()` methods from `OrchestratorExample` and `ClassifierExample` subclasses
- **Flexible Formatting Options**: Added configurable formatting with support for separators, numbering, randomization, and example limits
- **Bias Prevention**: Maintained randomization for classifier examples to prevent positional bias in few-shot learning
- **API Consistency**: Unified formatting interface reduces maintenance burden for future example types

### Technical Details
- Added `BaseExample.join()` with parameters: `separator`, `max_examples`, `randomize`, `add_numbering`
- Updated `classification_node.py` to use `join()` with randomization for bias prevention
- Updated prompt builders (`memory_extraction.py`, `orchestrator.py`) to use `join()` with numbering
- Maintains all existing formatting behavior while reducing code duplication by 23 lines

## [0.4.3] - 2025-09-13

### Enhanced
- **OpenWebUI Interface**: Added notebook link display functionality with comprehensive response integration
- **Response Generation**: Enhanced prompts with notebook awareness and interface-specific guidance for better user experience
- **Context Loading**: Improved logging and registry initialization for better debugging and error handling

### Improved
- **Wind Turbine Application**: Refactored response generation guidelines with streamlined structure and cleaner code organization
- **User Experience**: Better integration of text responses, figures, and clickable notebook links in OpenWebUI
- **Debugging**: Replaced print statements with proper logging throughout context loading system

### Technical Details
- Added notebook link extraction and display in OpenWebUI response pipeline
- Enhanced response prompts with conversational guidelines and notebook availability context
- Improved context loader with registry initialization for proper context reconstruction

## [0.4.2] - 2025-09-13

### Enhanced
- **Python Execution Integration**: Python capability now registers notebooks using centralized StateManager.register_notebook() with rich metadata
- **Notebook Link Generation**: Improved notebook URL generation in both local and container execution modes with FileManager integration
- **Notebook Structure**: Enhanced notebook cell organization with separate markdown headers and executable code blocks

### Technical Details
- Added notebook registration with execution time, context key, and code metrics to Python capability
- Standardized notebook naming to 'notebook.ipynb' across execution modes
- Improved notebook generation with cleaner separation of results documentation and executable code

## [0.4.1] - 2025-09-13

### Enhanced
- **Centralized Notebook Registry**: Added structured notebook registry system replacing simple link list with rich metadata support
- **StateManager Enhancements**: Added `register_notebook()` method for capability-agnostic notebook registration with timestamps and metadata
- **Response Context Tracking**: Enhanced ResponseContext to track notebook availability for improved user guidance

### Technical Details
- Replaced `ui_notebook_links` with structured `ui_captured_notebooks` registry in agent state
- Added notebook registration method supporting display names, metadata, and automatic timestamp generation
- Updated state reset logic to use new registry format for better notebook management

## [0.4.0] - 2025-09-12

### Major Features
- **Context Memory Optimization**: Added recursive data summarization with `recursively_summarize_data()` utility to prevent context window overflow
- **Configurable Python Executor**: Complete Python executor configuration system with `PythonExecutorConfig` class for centralized settings
- **Enhanced Figure Registration**: Added batch figure registration support with accumulation for improved performance
- **OpenWebUI Performance Optimizations**: Response chunking for large outputs (>50KB) and static URL serving for figures

### Fixed
- **Critical Infinite Loop Bug**: Fixed infinite reclassification loop when orchestrator hallucinated non-existent capabilities
- **Reclassification Limit Enforcement**: Router now properly enforces `max_reclassifications` limit for all reclassification paths
- **Dependency Issues**: Fixed OpenTelemetry version constraints to resolve compatibility issues
- **Error Handling**: Enhanced retry logic and error classification in infrastructure nodes

### Changed
- **Unified Error Handling**: Consolidated reclassification system to use single error-based path instead of dual state/error approaches
- **Context Method Naming**: Renamed `get_human_summary()` to `get_summary()` across all context classes with backwards compatibility
- **Infrastructure Node Improvements**: Infrastructure nodes now raise `ReclassificationRequiredError` exceptions instead of directly manipulating state
- **State Cleanup**: Removed obsolete `control_needs_reclassification` field from agent state

### Enhanced
- **Python Executor Improvements**: Configurable execution timeouts, better error handling, and improved figure collection in both local and container modes
- **Context Window Management**: Automatic truncation of large execution results and code outputs to manage LLM context limits
- **Deployment Configuration**: Updated for static file serving with proper environment variable support
- **Error Classification**: Better distinction between retriable LLM failures and configuration errors

### Technical Details
- Added `ReclassificationRequiredError` exception to framework error system
- Enhanced router error handling to enforce limits consistently across all reclassification triggers
- Updated orchestrator and classifier to use proper exception-based error handling
- Improved architecture with cleaner separation between error handling and state management
- Added python_executor configuration section with sensible defaults
- Implemented graceful fallback for legacy method names with deprecation warnings

## [0.3.1] - 2025-09-10

### Enhancements
- **Documentation Workflow Improvements**: Added manual trigger capability to GitHub Actions documentation workflow
- **Tag-based Documentation Rebuilds**: Documentation now automatically rebuilds when version tags are created or moved
- **Enhanced Build Controls**: Documentation workflow now supports both automatic (tag/push) and manual triggering

### Bug Fixes  
- **Documentation Version Sync**: Fixed issue where moving git tags didn't trigger documentation rebuilds, ensuring docs always reflect current version
- **Gitignore Cleanup**: Added `.nfs*` pattern to gitignore and fixed malformed entries

### Technical Details
- Added `workflow_dispatch` trigger to `.github/workflows/docs.yml` for manual execution
- Added `tags: ['v*']` trigger for automatic rebuilds on version tag changes  
- Updated deployment conditions to support manual and tag-based triggers
- Improved build artifact and deployment logic for consistent documentation updates

## [0.3.0] - 2025-09-09

### Features
- **Interface Context System**: Added runtime interface detection for multi-interface support (CLI, OpenWebUI)
- **Centralized Figure Registry**: Implemented capability-agnostic figure registration system with rich metadata
- **Enhanced Figure Display**: Added automatic base64 figure conversion for OpenWebUI with interface-aware rendering
- **Real-time Log Viewer**: Added `/logs` command to OpenWebUI for in-memory log viewing and debugging
- **Robust JSON Serialization**: Comprehensive serialization utilities for scientific objects (matplotlib, numpy, pandas)

### Framework Enhancements
- **Interface-Aware Response Generation**: Context-sensitive prompts and responses based on interface capabilities
- **Python Executor Improvements**: Enhanced error handling and metadata serialization with fallback mechanisms
- **State Management Updates**: Centralized figure registry with capability source tracking and timestamps
- **Configuration System**: Added `get_interface_context()` for runtime interface detection

### Technical Improvements
- **Serialization Utilities**: Added `make_json_serializable()` and `serialize_results_to_file()` for robust data handling
- **Path Resolution**: Capability-agnostic figure path resolution for different execution environments
- **Error Handling**: Enhanced Python executor with detailed error reporting and serialization failure recovery
- **UI Integration**: Seamless figure display with metadata and creation timestamps

## [0.2.2] - 2025-08-16

### Major Features
- **New RECLASSIFICATION Error Severity**: Added `RECLASSIFICATION` severity level to ErrorSeverity enum for improved task-capability matching
- **Enhanced Error Classification Workflow**: Capabilities can now request reclassification when receiving inappropriate tasks
- **Reclassification Routing Logic**: Router node now properly handles reclassification errors with configurable attempt limits

### Breaking Changes
- **ErrorClassification Metadata Migration**: Replaced custom error fields with unified metadata field in ErrorClassification
  - `format_for_llm()` now generically processes all metadata keys
  - Enhanced error context richness for better LLM understanding
  - All infrastructure nodes and capabilities updated to use metadata field
  - Maintains backward compatibility through systematic migration

### Framework Enhancements
- **Enhanced Classification Node**: Improved reclassification workflow with proper failure context handling
- **Router Node Improvements**: Added reclassification attempt tracking and routing logic
- **Execution Limits Configuration**: Added support for configurable reclassification limits
- **Error Node Enhancements**: Comprehensive error handling improvements with better metadata processing

### Documentation & Examples
- **Major Documentation Cleanup**: Removed outdated markdown files and enhanced RST documentation structure
- **Enhanced Hello World Weather Example**: Added comprehensive classifier examples and improved context access details
- **Error Handling Documentation**: Complete documentation updates for new reclassification workflow
- **API Reference Updates**: Enhanced error handling API documentation with examples and usage patterns
- **Developer Guide Improvements**: Updated infrastructure components documentation

### Infrastructure Improvements
- **Framework-wide Capability Updates**: All capabilities updated to use new ErrorClassification metadata approach
- **Enhanced Time Range Parsing**: Improved time range parsing capability with better error handling
- **Configuration System Updates**: Enhanced config system to support execution limits and reclassification controls

### Technical Details
- Enhanced error classification system enables better task-capability matching
- Unified metadata approach provides richer context for error analysis and recovery
- Reclassification workflow prevents infinite loops with configurable attempt limits
- Complete migration maintains backward compatibility across the entire framework

## [0.2.1] - 2025-08-11

### Critical Fixes
- **Containerized Python Execution**: Fixed critical bug where execution metadata wasn't being created in mounted volumes
- **Container Build Failures**: Removed obsolete python3-epics-simulation kernel mounts that caused build failures
- **Path Mapping**: Fixed hardcoded path patterns in container execution using config-driven approach
- **Timezone Consistency**: Standardized timezone across all services with centralized configuration

### Security & Stability  
- **Repository Security**: Updated .gitignore to exclude development services and sensitive configurations
- **Network Security**: Renamed container network from als-agents-network to alpha-berkeley-network for consistency
- **Service Cleanup**: Removed mem0 service references and cleaned up leftover container code

### Developer Experience Improvements
- **Configuration System Refactoring**: Renamed `unified_config` module to `config` for improved developer experience
- **Professional Naming**: Replaced `UnifiedConfigBuilder` with `ConfigBuilder` to eliminate confusing terminology
- **Automatic Environment Detection**: Added container-aware Python environment detection for convenience
- **Graceful Ollama Fallback**: Implemented automatic URL fallback for development workflows
- **Documentation**: Updated all references across 43+ files to use consistent naming conventions

### Infrastructure Enhancements
- **Git-based Versioning**: Added automatic version detection from git tags in documentation
- **Path Resolution**: Replaced hardcoded paths with configuration-driven approach using `get_agent_dir()`
- **Container Integration**: Improved container execution reliability and error handling
- **Documentation Cleanup**: Enhanced error handling documentation and API references

### Technical Details
- Fixed 'Failed to read execution metadata from container' error through proper volume mounting
- Eliminated manual reconfiguration when switching between local and containerized execution
- Complete refactoring eliminates confusing "unified" terminology from LangGraph migration era
- Added proper timezone data (tzdata) package in Jupyter containers for accurate timestamps
- Maintains backward compatibility through systematic import updates across entire codebase

## [0.2.0] - 2025-01-31

### Added
- Enhanced execution plan editor with file-based persistence
- Comprehensive approval system with human-in-the-loop workflows
- Complete advanced wind turbine tutorial application
- Improved documentation with execution plan viewer
- Execution plan viewer JavaScript support for interactive documentation

### Changed
- Modernized docker-compose configurations
- Enhanced framework robustness and capabilities
- Improved documentation build system and content

### Fixed
- Repository hygiene improvements with better .gitignore
- Removed deprecated version fields from docker-compose files
- Cleaned up PID files from repository

## [0.1.1] - 2025-08-08

### Fixed
- Remove invalid retry_count parameter from ErrorClassification calls in infrastructure nodes
- Fix runtime error: `ErrorClassification.__init__() got an unexpected keyword argument 'retry_count'`
- Update documentation examples to reflect correct ErrorClassification API usage
- Complete migration from dual retry tracking to state-only retry tracking

## [0.1.0] - 2024-12-XX

### Added
- Core capability-based agent architecture
- LangGraph integration for structured orchestration
- Complete hello world weather agent tutorial
- Framework installation and setup documentation
- API reference documentation (actively being developed)
- Developer guides covering infrastructure components
- Container-based deployment system
- Basic CLI interface for direct conversation
- Memory storage and context management systems
- Human approval workflow integration
- Error handling and recovery infrastructure

### Documentation
- Getting started guide with installation instructions
- Complete hello world tutorial with working weather agent
- Early access documentation warnings across all sections
- API reference for core framework components
- Developer guides for infrastructure understanding

### Known Limitations
- Documentation is under active development
- Some advanced tutorials not yet included
- APIs may evolve before 1.0.0 release

---

*This is an early access release. We welcome feedback and contributions!*