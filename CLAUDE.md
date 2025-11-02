# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Osprey Framework** (formerly Alpha Berkeley Framework) is a domain-agnostic, capability-based architecture for building intelligent agents. It uses LangGraph for orchestration and provides a modular system for creating specialized capabilities that can be combined to solve complex tasks.

**⚠️ IMPORTANT - Ongoing Rename**: This repository is currently being renamed from `alpha-berkeley-framework` to `osprey-framework`. See OSPREY_RENAME_TODO.md for complete details. The codebase is mid-transition:
- Source directory: `src/osprey/` (renamed from `src/framework/`)
- Package name: Will be `osprey-framework` on PyPI
- Import path: `from osprey.*` (changing from `from osprey.*`)
- CLI command: Will be `osprey` (changing from `framework`)

## Common Commands

### Development & Testing
```bash
# Run tests
pytest

# Run tests with specific markers
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "not slow"              # Skip slow tests
pytest -m requires_openai         # Tests requiring OpenAI API

# Run specific test file
pytest tests/path/to/test_file.py

# Run with verbose output
pytest -v

# Install package in development mode
pip install -e .

# Install with all optional dependencies
pip install -e ".[all]"

# Install docs dependencies
pip install -e ".[docs]"
```

### Documentation
```bash
# Build documentation
cd docs
make html

# Test documentation build (like CI)
cd docs
make test-build

# Live documentation with auto-rebuild
cd docs
make livehtml

# Clean documentation build
cd docs
make clean
```

### Code Quality
```bash
# Format code
black src/ --line-length 100
isort src/

# Lint with ruff
ruff check src/

# Type checking
mypy src/
```

### CLI Commands
```bash
# Create new project from template
osprey init my-project --template hello_world_weather

# Start interactive chat
osprey chat

# Deploy services
osprey deploy up

# Check system health
osprey health

# Export configuration
osprey export-config
```

### Container Management
The framework uses **Podman** (not Docker) for container orchestration:
```bash
# Deploy services defined in config
python src/osprey/deployment/container_manager.py config.yml up -d

# View service status
osprey deploy status

# Stop services
osprey deploy down
```

## Architecture Overview

### Core Components

**State Management** (`src/osprey/state/`)
- `state.py`: LangGraph-native state using `MessagesState` foundation
- `state_manager.py`: State creation and management utilities
- `AgentState`: TypedDict-based state with automatic checkpointing
- Only `capability_context_data` persists across conversation turns
- All execution fields reset automatically between invocations

**Graph System** (`src/osprey/graph/`)
- `graph_builder.py`: Creates LangGraph workflow from registry components
- Router-based execution flow using conditional edges
- Async-first architecture (use `ainvoke`, `astream`)
- Default: in-memory checkpointer for R&D, PostgreSQL for production

**Registry System** (`src/osprey/registry/`)
- `manager.py`: Centralized component registry (capabilities, nodes, services)
- `registry.py`: Framework-level component definitions
- Two-tier: framework registry + application registries
- Lazy loading prevents circular imports
- Initialization order: context → data sources → nodes → services → capabilities

**Capabilities** (`src/osprey/base/capability.py`)
- Convention-based base class for all capabilities
- Must define: `name`, `description`, `execute()`
- Optional: `provides`, `requires`, error classification, retry policy
- Use `@capability_node` decorator for LangGraph integration

**Infrastructure Nodes** (`src/osprey/infrastructure/`)
- `gateway.py`: Entry point, handles input processing
- `classification_node.py`: Routes to appropriate capabilities
- `orchestration_node.py`: Creates execution plans
- `router_node.py`: Dynamic routing based on state
- `respond_node.py`: Formats responses to users
- `error_node.py`: Handles errors and recovery

### Key Concepts

**Execution Flow**:
1. Gateway receives user input
2. Task extraction parses requirements
3. Classifier selects appropriate capabilities
4. Orchestrator creates execution plan
5. Router executes planned steps
6. Capabilities perform work
7. Response node formats output

**Context Management**:
- Context data structure: `{context_type: {context_key: {field: value}}}`
- Persists across conversation turns
- Enables memory and multi-turn conversations

**Template System** (`src/osprey/templates/`):
- Project templates: `minimal`, `hello_world_weather`, `wind_turbine`
- Service templates: `jupyter`, `open-webui`, `pipelines`
- Jinja2-based rendering with configuration context

**Model Providers** (`src/osprey/models/providers/`):
- Supports: OpenAI, Anthropic, Google, Ollama, CBORG
- Factory pattern for provider instantiation
- Configuration-driven model selection

## Development Patterns

### Creating a New Capability

1. Inherit from `BaseCapability`
2. Define class attributes: `name`, `description`, `provides`, `requires`
3. Implement `execute()` as static async method
4. Add `@capability_node` decorator
5. Register in application registry

Example:
```python
from osprey.base.capability import BaseCapability
from osprey.base.decorators import capability_node

@capability_node
class MyCapability(BaseCapability):
    name = "my_capability"
    description = "Does something useful"
    provides = ["OUTPUT_DATA"]
    requires = ["INPUT_DATA"]
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        # Business logic here
        return {"result_field": result_value}
```

### Working with State

State is a TypedDict that gets automatically checkpointed:
```python
# Access state fields
user_input = state.get("user_input")
messages = state.get("messages", [])

# Return state updates (gets merged by LangGraph)
return {
    "execution_result": result,
    "capability_context_data": updated_context
}
```

### Adding Custom Prompts

Place in `src/osprey/prompts/defaults/` or application-specific prompts directory:
```python
from osprey.prompts.base import BasePrompt

class MyPrompt(BasePrompt):
    prompt_name = "my_prompt"
    
    def get_system_prompt(self, **kwargs) -> str:
        return "System instructions here"
```

## File Structure

```
src/osprey/
├── approval/           # Human-in-the-loop approval system
├── base/               # Base classes (capability, nodes, errors)
├── capabilities/       # Built-in capabilities (memory, python, time)
├── cli/                # CLI interface (init, chat, deploy commands)
├── commands/           # Command registry and completer
├── context/            # Context management system
├── data_management/    # Data source providers
├── deployment/         # Container orchestration
├── graph/              # LangGraph builder
├── infrastructure/     # Core nodes (gateway, classifier, etc.)
├── interfaces/         # User interfaces (CLI chat)
├── models/             # LLM provider integrations
├── prompts/            # Prompt templates
├── registry/           # Component registry system
├── services/           # Internal services (python_executor, memory)
├── state/              # State management
├── templates/          # Project and service templates
└── utils/              # Utilities (config, logging, streaming)
```

## Configuration

Configuration files use YAML format with import support:
- Framework config: `src/osprey/config.yml`
- Application configs: Can import and override framework settings
- Environment variables: `.env` file
- Config access: `from osprey.utils.config import get_config`

## Testing Strategy

- Unit tests: Mock external dependencies, fast execution
- Integration tests: Real services, may require API keys
- Markers: `unit`, `integration`, `slow`, `requires_api`, `requires_openai`, etc.
- Async support: `asyncio_mode = auto` in pytest.ini
- VCR: Record/replay API interactions for consistent testing

## Important Notes

- **Async-first**: All graph operations use `await graph.ainvoke()` or `async for chunk in graph.astream()`
- **Podman not Docker**: Container management uses Podman Compose
- **TypedDict state**: No Pydantic models in state (for LangGraph serialization)
- **No circular imports**: Registry uses lazy loading pattern
- **Convention over configuration**: Capabilities discovered by naming patterns

## API Keys & Environment

Required environment variables (in `.env`):
```bash
OPENAI_API_KEY=...           # For OpenAI models
ANTHROPIC_API_KEY=...        # For Claude models
GOOGLE_API_KEY=...           # For Gemini models
OLLAMA_BASE_URL=...          # For local Ollama (optional)
```

## Common Issues

**Import errors after rename**: The rename is in progress. Use `from osprey.*` for new code, but existing code may still reference `from osprey.*` until fully migrated.

**Test collection errors**: Run from repository root, ensure virtual environment is activated.

**Container errors**: Use `podman` commands, not `docker`. Install with `pip install podman podman-compose`.

**State serialization issues**: Use pure Python types in state, no Pydantic models at top level.

## Documentation

- Full docs: https://als-apg.github.io/osprey (after rename completes)
- Current: https://thellert.github.io/alpha_berkeley
- Source: `docs/source/`
- Built with Sphinx using pydata-sphinx-theme
