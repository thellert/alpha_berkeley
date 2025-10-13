# Alpha Berkeley Framework - Latest Release (v0.5.1)

🔧 **Bug Fix Release** - Enhanced task extraction data integration for improved LLM context quality and better agent performance.

## What's Fixed

### 🔧 Task Extraction Improvements
- **Enhanced Data Integration**: Task extraction now properly formats retrieved data content from external sources
- **Improved LLM Context**: Better quality context provided to language models for more accurate task understanding
- **Robust Error Handling**: Added fallback mechanisms for data source content formatting

## Previous Release (v0.5.0)

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

This is a **major feature release** introducing the first complete domain-specific application:

- **New Application Structure**: ALS Assistant application added under `src/applications/als_assistant/`
- **New Services**: MongoDB, Langfuse, and PV Finder services with Docker containerization
- **Enhanced Dependencies**: Added MCP protocol support, enhanced container execution capabilities
- **Backwards Compatibility**: All existing framework functionality is preserved and enhanced
- **Documentation**: Complete RST documentation with setup guides and architectural diagrams

## Get Started with ALS Assistant

1. **Framework Setup**: Update to v0.5.1 for enhanced task extraction capabilities
2. **Service Deployment**: Use Docker compose templates for MongoDB, Langfuse, and PV Finder services
3. **Configuration**: Configure ALS-specific settings in `src/applications/als_assistant/config.yml`
4. **Documentation**: View the [ALS Assistant guide](https://thellert.github.io/alpha_berkeley/example-applications/als-assistant.html)
5. **Issues**: Report any issues on [GitHub Issues](https://github.com/thellert/alpha_berkeley/issues)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.5.1`
3. **Title**: `Alpha Berkeley Framework v0.5.1 - Task Extraction Improvements`
4. **Description**: Copy the content above (from "🚀 Major Release: ALS Assistant Application" through "Get Started with ALS Assistant")

## Technical Details

- **Massive Integration**: Added 144 new files with 430,647 lines of code
- **MCP Protocol**: Model Context Protocol integration for external service communication
- **Container Execution**: Enhanced WebSocket connectivity, proxy handling, and error recovery
- **Database Integration**: MongoDB service with comprehensive ALS accelerator data
- **Knowledge Base**: 11,000+ EPICS process variables, accelerator objects database
- **Service Architecture**: PV Finder service, launcher service with desktop integration
- **Documentation**: Complete RST documentation with architectural diagrams
- **Benchmarking**: Performance analysis tools and model comparison frameworks

---

*Current Release: v0.5.1 (October 2025)*  
*Release Type: Major Feature Release*  
*Previous Release: v0.4.5 with enhanced UI capabilities and infrastructure improvements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
