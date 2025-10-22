# Alpha Berkeley Framework - Latest Release (v0.6.2)

🐛 **Bugfix Release** - Critical fix for reclassification counter logic ensuring proper retry behavior.

## What's Fixed

### 🔧 Reclassification Counter Bug
- **Critical Bug Fixed**: `control_reclassification_count` was incorrectly incremented on initial classification
- **Correct Behavior**: Counter now only increments on actual reclassifications (when `previous_failure` context is present)
- **Impact**: With `max_reclassifications: 1`, system now correctly allows 1 reclassification (2 total attempts: initial + 1 retry)
- **Implementation**: Simplified logic by updating counter once at the top of `_create_classification_result()` function

### 📚 Documentation Updates
- **Configuration Reference**: Clarified `max_reclassifications` parameter to explicitly state it allows N reclassifications after initial classification
- **Developer Guide**: Updated classification and routing documentation for accuracy

## Previous Release (v0.6.1)

🎯 **Improved Onboarding Release** - Simplified default configuration for better new user experience with `hello_world_weather` as the default application.

## What's New

### 🚀 Enhanced Getting Started Experience
- **New Default Application**: Changed from `als_assistant` to `hello_world_weather` for immediate usability without LBNL-specific infrastructure
- **Simplified Configuration**: Removed ALS-specific service dependencies (MongoDB, PV Finder, Langfuse) from default setup
- **Clear Documentation**: Updated installation guide with explicit application selection guidance and progressive complexity path

### 📚 Documentation Improvements
- **Application Selection Guide**: New section in installation documentation explaining which application to choose
- **Progressive Learning Path**: Clear progression from `hello_world_weather` → `wind_turbine` → `als_assistant`
- **Service Clarification**: Distinguished framework services (jupyter, open_webui, pipelines) from application-specific services

### 🎯 Why This Matters
- **New Users**: Can now start immediately without complex EPICS/accelerator infrastructure setup
- **External Users**: Framework is accessible to non-LBNL users out of the box
- **LBNL Users**: Can still easily switch to `als_assistant` when needed

## Previous Release (v0.6.0)

### ⚡ Performance Optimization System
- **Task Extraction Bypass**: Skip LLM-based task extraction and use full conversation context directly in downstream processing
- **Capability Selection Bypass**: Skip LLM-based classification and activate all registered capabilities automatically
- **Runtime Control**: New slash commands (`/task:off`, `/task:on`, `/caps:off`, `/caps:on`) for dynamic performance adjustment during conversations
- **Configuration Support**: System-wide defaults via `agent_control` section in config.yml
- **Bug Fix**: Fixed user_id extraction in data source request creation

## Earlier Release (v0.5.0)

### 🔬 ALS Assistant Application
- **Complete Scientific Application**: First fully-featured domain-specific application for accelerator physics operations at Lawrence Berkeley National Laboratory's Advanced Light Source
- **PV Finder Service**: Intelligent EPICS process variable discovery using natural language queries with MCP (Model Context Protocol) integration
- **Application Launcher**: Desktop integration service with MCP protocol support for seamless tool launching
- **Comprehensive Knowledge Base**: 11,000+ process variables, accelerator objects database, and MATLAB codebase analysis

### 🧠 Advanced Capabilities
- **Data Analysis**: 7 specialized capability modules for accelerator physics operations including live monitoring, machine operations, and archiver data access
- **Data Visualization**: Advanced plotting and analysis tools specifically designed for accelerator operations
- **Machine Operations**: Direct control and monitoring capabilities for accelerator systems
- **Historical Data Access**: Integration with ALS archiver systems for historical analysis

### 🏗️ Infrastructure & Services
- **MongoDB Integration**: Database service with Docker containerization for data persistence
- **Langfuse Observability**: Enhanced monitoring and tracing with containerized Langfuse deployment
- **Container Orchestration**: Specialized Docker services for PV finder, database, and observability
- **Benchmarking Suite**: Performance analysis tools and model comparison frameworks

## Upgrade Notes

This is a **patch release** improving the new user onboarding experience:

- **Configuration Change**: Default application is now `hello_world_weather` instead of `als_assistant`
- **Service Updates**: ALS-specific services are commented out by default
- **Documentation**: Enhanced installation guide with clear application selection guidance
- **Backwards Compatibility**: Existing configurations and functionality remain unchanged
- **For LBNL Users**: Simply uncomment `als_assistant` in `config.yml` to use the full ALS Assistant application

## Get Started

1. **New Users**: Clone the repo and follow the installation guide - `hello_world_weather` works out of the box
2. **Existing Users**: Update to v0.6.1 and review your `config.yml` - if you use ALS Assistant, ensure it's uncommented
3. **Documentation**: Follow the [Getting Started Guide](https://thellert.github.io/alpha_berkeley/getting-started/) for complete setup instructions
4. **Issues**: Report any issues on [GitHub Issues](https://github.com/thellert/alpha_berkeley/issues)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.6.1`
3. **Title**: `Alpha Berkeley Framework v0.6.1 - Improved Onboarding`
4. **Description**: Copy the content above (from "🎯 Improved Onboarding Release" through "Why This Matters")

## Technical Details

- **Configuration Changes**: Updated `config.yml` to use `hello_world_weather` as default application
- **Service Configuration**: Commented out ALS-specific services (mongo, pv_finder, langfuse) in default deployment
- **Documentation Updates**: Enhanced installation.rst with application selection section
- **User Experience**: Progressive complexity path clearly documented for new users
- **Backwards Compatible**: No breaking changes; existing configurations work as before

---

*Current Release: v0.6.1 (October 2025)*  
*Release Type: Patch Release - Improved Onboarding*  
*Previous Release: v0.6.0 with performance optimization*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
