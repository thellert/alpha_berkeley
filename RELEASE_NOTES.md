# Alpha Berkeley Framework - Latest Release (v0.4.0)

🚀 **Major feature release with critical bug fixes** - a comprehensive update to the Alpha Berkeley Framework.

## What's New

### 🎯 Major New Features
- **Context Memory Optimization**: Intelligent data summarization with `recursively_summarize_data()` to prevent context window overflow
- **Configurable Python Executor**: Complete configuration system with `PythonExecutorConfig` for centralized timeout and retry settings
- **Enhanced Figure Registration**: Batch figure registration support for improved performance
- **OpenWebUI Performance**: Response chunking for large outputs and static URL serving for figures

### 🐛 Critical Bug Fixes
- **Infinite Loop Fix**: Resolved critical infinite reclassification loop that occurred when orchestrator hallucinated non-existent capabilities
- **Limit Enforcement**: Router now properly enforces `max_reclassifications` limit across all reclassification paths
- **Dependency Issues**: Fixed OpenTelemetry version constraints and compatibility issues

### 🏗️ Architecture Improvements
- **Unified Error System**: Consolidated dual reclassification paths into single, consistent error-based approach
- **Exception-Based Design**: Infrastructure nodes now use proper `ReclassificationRequiredError` exceptions
- **Context Method Refactoring**: Renamed `get_human_summary()` to `get_summary()` with backwards compatibility
- **State Cleanup**: Removed obsolete `control_needs_reclassification` field for cleaner state management

### ⚡ Performance & Usability
- **Python Executor Enhancements**: Configurable timeouts, better error handling, improved figure collection
- **Context Window Management**: Automatic truncation of large results to manage LLM context limits
- **Enhanced Error Classification**: Better distinction between retriable and configuration errors

## Upgrade Notes

This is a major release with significant new features and critical bug fixes:

- **Critical Bug Fix**: Resolves infinite loop during task classification
- **New Configuration**: Python executor now supports configurable timeouts and retry limits
- **API Changes**: Context classes now use `get_summary()` instead of `get_human_summary()` (backwards compatible)
- **Performance**: Improved memory usage and response times for large outputs
- **Backwards Compatibility**: All changes maintain backwards compatibility with deprecation warnings

## Get Started

1. Update to v0.4.0 for critical bug fixes and improved stability
2. View the [complete documentation](https://thellert.github.io/alpha_berkeley/)
3. Report any issues on [GitHub Issues](https://github.com/thellert/alpha_berkeley/issues)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.4.0`
3. **Title**: `Alpha Berkeley Framework v0.4.0 - Major Feature Release`
4. **Description**: Copy the content above (from "🚀 Major feature release" through "Get Started")

## Technical Details

- Added `ReclassificationRequiredError` exception to framework error system
- Enhanced router error handling with consistent reclassification limit enforcement
- Unified reclassification system eliminating dual state/error paths
- Removed obsolete `control_needs_reclassification` agent state field
- Added `PythonExecutorConfig` class for centralized Python execution settings
- Implemented `recursively_summarize_data()` utility for context window management
- Enhanced figure registration with batch processing capabilities
- Added response chunking for large outputs in OpenWebUI interface

---

*Current Release: v0.4.0 (September 2025)*  
*Release Type: Major Feature Release*  
*Previous Release: v0.3.1 with documentation workflow improvements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
