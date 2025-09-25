# ALS Assistant Launcher Service

A modern, LangGraph-native service for launching ALS applications across network boundaries. This service enables users to launch Phoebus control panels and CSS Data Browser applications on their local machines while the ALS Assistant agent runs in a containerized environment.

## Overview

The launcher service solves the cross-network application launching problem by converting natural language requests into desktop-executable launch URIs. This maintains security (no direct command execution from server) while providing seamless user experience.

## Architecture

```
launcher/
├── service.py              # Main LangGraph service
├── models.py              # Data models and state definitions  
├── utils.py               # URI generation utilities
├── capabilities/
│   └── launcher.py        # ALS Assistant capability integration
├── mcp/
│   ├── server.py          # MCP server for external integration
│   └── __init__.py
├── desktop_handler/
│   ├── launch_tool.sh     # Desktop URI handler script
│   └── launcher-handler.desktop  # Desktop integration
└── test_launcher.py       # Testing script
```

## Key Components

### 1. LauncherService (LangGraph)
- **Rule-based intent detection** (no API calls needed)
- **Command generation** for Phoebus panels and Data Browser
- **URI generation** for cross-network execution
- **Full LangGraph integration** with streaming and checkpointing

### 2. LauncherCapability 
- **ALS Assistant integration** via capability system
- **Query extraction** from conversation state
- **Result processing** and state updates

### 3. MCP Server (Optional)
- **External tool interface** following MCP protocol
- **Standalone operation** independent of ALS Assistant
- **Tool-based API** for launch_phoebus_panel, launch_databrowser

### 4. Desktop Handler
- **URI scheme handler** (`myapp://`) for desktop integration
- **Command execution** in user's terminal
- **Cross-platform support** via xdg-mime

## Usage

### Within ALS Assistant
The launcher capability automatically detects launcher-related queries in conversation:

```
User: "Launch the ML Control Panel"
User: "Open Data Browser for PV SR:DCCT"  
User: "Show me the phoebus panel"
```

### Direct Service Usage
```python
from applications.als_assistant.services.launcher import LauncherService, LauncherServiceRequest

service = LauncherService()
request = LauncherServiceRequest(query="Launch Data Browser with PV SR:DCCT")
result = await service.execute(request)

if result.success:
    print(f"Launch URI: {result.launch_uri}")
```

### MCP Server
```python
from applications.als_assistant.services.launcher.mcp import LauncherMCPServer

server = LauncherMCPServer()
result = await server.handle_tool_call("launch_databrowser", {"pvs": ["SR:DCCT"]})
```


## Desktop Setup

1. Make the handler script executable:
   ```bash
   chmod +x desktop_handler/launch_tool.sh
   ```

2. Update the .desktop file with correct path:
   ```bash
   # Edit desktop_handler/launcher-handler.desktop
   Exec=/full/path/to/launch_tool.sh %u
   ```

3. Register the URI handler:
   ```bash
   cp desktop_handler/launcher-handler.desktop ~/.local/share/applications/
   xdg-mime default launcher-handler.desktop x-scheme-handler/myapp
   update-desktop-database ~/.local/share/applications/
   ```

## Testing

Run the test script:
```bash
cd src/applications/als_assistant/services/launcher
python test_launcher.py
```

## Design Principles

- **Simplicity**: Rule-based intent detection, no unnecessary LLM calls
- **Security**: Commands execute on user's machine with full visibility  
- **Modularity**: Service can be used independently or via capability
- **Extensibility**: Easy to add new applications and command types
- **Standards**: MCP server for external integration

## Migration from Legacy

This service replaces the PydanticAI-based launcher_agent with:
- ✅ LangGraph-native workflow
- ✅ Simplified rule-based processing  
- ✅ Better error handling and logging
- ✅ Modular architecture
- ✅ MCP server support
- ✅ Preserved URI scheme innovation
