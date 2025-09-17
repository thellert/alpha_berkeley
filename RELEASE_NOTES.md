# Alpha Berkeley Framework - Latest Release (v0.4.4)

🔧 **Code refactoring and API improvements** - consolidated example formatting system with unified interface and reduced code duplication.

## What's New

### 🔧 Code Refactoring and API Improvements
- **Unified Example Formatting**: Consolidated example formatting with new `BaseExample.join()` static method
- **Code Deduplication**: Removed duplicate formatting methods from subclasses, reducing codebase by 23+ lines
- **Flexible Formatting Options**: Added support for separators, numbering, randomization, and example limits
- **Bias Prevention**: Maintained randomization for classifier examples to prevent positional bias in few-shot learning
- **API Consistency**: Unified formatting interface across all example types for better maintainability

### 🎯 Developer Experience
- **Cleaner Codebase**: Eliminated duplicate `format_examples_for_prompt()` methods across example subclasses
- **Better Maintainability**: Centralized formatting logic reduces maintenance burden for future example types
- **Consistent Interface**: All example formatting now uses the same unified API with flexible options

## Upgrade Notes

This is a patch release with code refactoring and API improvements:

- **API Changes**: Deprecated `format_examples_for_prompt()` methods - use `BaseExample.join()` instead
- **Backwards Compatibility**: All existing functionality is preserved with the new unified interface
- **Performance**: Slight performance improvement due to reduced code duplication
- **Maintainability**: Future example types will benefit from the unified formatting system

## Get Started

1. Update to v0.4.4 for improved code organization and unified example formatting
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

*Current Release: v0.4.4 (September 2025)*  
*Release Type: Patch Release*  
*Previous Release: v0.4.3 with UI and response improvements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
