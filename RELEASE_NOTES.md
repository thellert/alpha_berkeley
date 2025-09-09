# Alpha Berkeley Framework - Latest Release (v0.3.0)

🚀 **Major interface enhancements and figure display improvements** for the Alpha Berkeley Framework!

## What's New

### 🖥️ Interface Context System
- **Multi-Interface Support**: Runtime detection for CLI, OpenWebUI, and other interfaces
- **Context-Aware Responses**: Interface-specific behavior and response customization
- **Smart Figure Handling**: Different figure display strategies based on interface capabilities

### 📊 Centralized Figure Registry
- **Capability-Agnostic Registration**: Universal figure registration system for all execution types
- **Rich Metadata**: Figure source, timestamps, and execution context tracking
- **Automatic Display**: Seamless integration with OpenWebUI for base64 figure rendering

### 🔧 Enhanced Python Executor
- **Robust Serialization**: Comprehensive JSON serialization for scientific objects (matplotlib, numpy, pandas)
- **Error Recovery**: Enhanced error handling with detailed reporting and fallback mechanisms
- **Path Resolution**: Smart figure path resolution for different execution environments

### 📝 Real-Time Log Viewer
- **OpenWebUI Integration**: `/logs` command for viewing application logs in chat
- **In-Memory Capture**: Live log streaming with configurable buffer size
- **Debug Support**: Real-time monitoring and troubleshooting through chat interface

### 🏗️ Framework Enhancements
- **State Management**: Centralized figure registry with capability source tracking
- **Configuration System**: Added `get_interface_context()` for runtime interface detection
- **Response Generation**: Interface-aware prompts and context-sensitive responses
- **UI Integration**: Enhanced figure display with metadata and creation timestamps

## Upgrade Notes

This release maintains full backward compatibility. The main changes are:
- New interface context system enables multi-interface awareness
- Centralized figure registry provides consistent figure handling across capabilities
- Enhanced OpenWebUI experience with automatic figure display and log viewer
- Robust serialization utilities available for scientific computing workflows

## Get Started

1. Update your installation: `pip install --upgrade alpha-berkeley-framework`
2. Follow the [installation guide](https://thellert.github.io/alpha_berkeley/getting-started/installation/)
3. Explore the [complete documentation](https://thellert.github.io/alpha_berkeley/)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.3.0`
3. **Title**: `Alpha Berkeley Framework v0.3.0 - Interface Enhancements & Figure Display Improvements`
4. **Description**: Copy the content above (from "🚀 Major interface enhancements" through "Get Started")

## Technical Details

- Interface context system enables runtime interface detection and customization
- Centralized figure registry provides capability-agnostic figure management
- Enhanced Python executor with comprehensive serialization for scientific objects
- Real-time log viewer with in-memory capture and chat interface integration
- Interface-aware response generation with context-sensitive prompts
- Robust error handling and recovery mechanisms for serialization failures

---

*Current Release: v0.3.0 (January 2025)*  
*Release Type: Interface Enhancements & Figure Display Improvements*  
*Previous Release: v0.2.2 with error handling enhancements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
