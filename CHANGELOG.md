# Changelog

All notable changes to the Alpha Berkeley Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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