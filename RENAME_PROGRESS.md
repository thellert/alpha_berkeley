# Rename Progress Tracker: Framework → Osprey

**Status Legend:**
- ⬜ Not Started
- 🔄 Working On
- ✅ Completed

---

## Core Framework Files (113 files)

### Root & Approval (6 files)
- ✅ `src/osprey/__init__.py`
- ✅ `src/osprey/approval/__init__.py`
- ✅ `src/osprey/approval/approval_manager.py`
- ✅ `src/osprey/approval/approval_system.py`
- ✅ `src/osprey/approval/config_models.py`
- ✅ `src/osprey/approval/evaluators.py`

### Base (8 files)
- ✅ `src/osprey/base/__init__.py`
- ✅ `src/osprey/base/capability.py`
- ✅ `src/osprey/base/decorators.py`
- ✅ `src/osprey/base/errors.py`
- ✅ `src/osprey/base/examples.py`
- ✅ `src/osprey/base/nodes.py`
- ✅ `src/osprey/base/planning.py`
- ✅ `src/osprey/base/results.py`

### Capabilities (3 files)
- ✅ `src/osprey/capabilities/memory.py`
- ✅ `src/osprey/capabilities/python.py`
- ✅ `src/osprey/capabilities/time_range_parsing.py`

### CLI (10 files)
- ✅ `src/osprey/cli/__init__.py`
- ✅ `src/osprey/cli/chat_cmd.py`
- ✅ `src/osprey/cli/deploy_cmd.py`
- ✅ `src/osprey/cli/export_config_cmd.py`
- ✅ `src/osprey/cli/health_cmd.py`
- ✅ `src/osprey/cli/init_cmd.py`
- ✅ `src/osprey/cli/interactive_menu.py`
- ✅ `src/osprey/cli/main.py`
- ✅ `src/osprey/cli/project_utils.py`
- ✅ `src/osprey/cli/templates.py`

### Commands (5 files)
- ✅ `src/osprey/commands/__init__.py`
- ✅ `src/osprey/commands/categories.py`
- ✅ `src/osprey/commands/completer.py`
- ✅ `src/osprey/commands/registry.py`
- ✅ `src/osprey/commands/types.py`

### Context (4 files)
- ✅ `src/osprey/context/__init__.py`
- ✅ `src/osprey/context/base.py`
- ✅ `src/osprey/context/context_manager.py`
- ✅ `src/osprey/context/loader.py`

### Data Management (4 files)
- ✅ `src/osprey/data_management/__init__.py`
- ✅ `src/osprey/data_management/manager.py`
- ✅ `src/osprey/data_management/providers.py`
- ✅ `src/osprey/data_management/request.py`

### Deployment (3 files)
- ✅ `src/osprey/deployment/__init__.py`
- ✅ `src/osprey/deployment/container_manager.py`
- ✅ `src/osprey/deployment/loader.py`

### Graph (2 files)
- ✅ `src/osprey/graph/__init__.py`
- ✅ `src/osprey/graph/graph_builder.py`

### Infrastructure (8 files)
- ✅ `src/osprey/infrastructure/clarify_node.py`
- ✅ `src/osprey/infrastructure/classification_node.py`
- ✅ `src/osprey/infrastructure/error_node.py`
- ✅ `src/osprey/infrastructure/gateway.py`
- ✅ `src/osprey/infrastructure/orchestration_node.py`
- ✅ `src/osprey/infrastructure/respond_node.py`
- ✅ `src/osprey/infrastructure/router_node.py`
- ✅ `src/osprey/infrastructure/task_extraction_node.py`

### Interfaces (3 files)
- ✅ `src/osprey/interfaces/__init__.py`
- ✅ `src/osprey/interfaces/cli/__init__.py`
- ✅ `src/osprey/interfaces/cli/direct_conversation.py`

### Models (10 files)
- ✅ `src/osprey/models/__init__.py`
- ✅ `src/osprey/models/completion.py`
- ✅ `src/osprey/models/factory.py`
- ✅ `src/osprey/models/providers/__init__.py`
- ✅ `src/osprey/models/providers/anthropic.py`
- ✅ `src/osprey/models/providers/base.py`
- ✅ `src/osprey/models/providers/cborg.py`
- ✅ `src/osprey/models/providers/google.py`
- ✅ `src/osprey/models/providers/ollama.py`
- ✅ `src/osprey/models/providers/openai.py`

### Prompts (12 files)
- ✅ `src/osprey/prompts/__init__.py`
- ✅ `src/osprey/prompts/base.py`
- ✅ `src/osprey/prompts/defaults/__init__.py`
- ✅ `src/osprey/prompts/defaults/clarification.py`
- ✅ `src/osprey/prompts/defaults/classification.py`
- ✅ `src/osprey/prompts/defaults/error_analysis.py`
- ✅ `src/osprey/prompts/defaults/memory_extraction.py`
- ✅ `src/osprey/prompts/defaults/orchestrator.py`
- ✅ `src/osprey/prompts/defaults/python.py`
- ✅ `src/osprey/prompts/defaults/response_generation.py`
- ✅ `src/osprey/prompts/defaults/task_extraction.py`
- ✅ `src/osprey/prompts/defaults/time_range_parsing.py`
- ✅ `src/osprey/prompts/loader.py`

### Registry (5 files)
- ✅ `src/osprey/registry/__init__.py`
- ✅ `src/osprey/registry/base.py`
- ✅ `src/osprey/registry/helpers.py`
- ✅ `src/osprey/registry/manager.py`
- ✅ `src/osprey/registry/registry.py`

### Services (18 files)
- ✅ `src/osprey/services/__init__.py`
- ✅ `src/osprey/services/memory_storage/__init__.py`
- ✅ `src/osprey/services/memory_storage/memory_provider.py`
- ✅ `src/osprey/services/memory_storage/models.py`
- ✅ `src/osprey/services/memory_storage/storage_manager.py`
- ✅ `src/osprey/services/python_executor/__init__.py`
- ✅ `src/osprey/services/python_executor/analyzer_node.py`
- ✅ `src/osprey/services/python_executor/approval_node.py`
- ✅ `src/osprey/services/python_executor/config.py`
- ✅ `src/osprey/services/python_executor/container_engine.py`
- ✅ `src/osprey/services/python_executor/exceptions.py`
- ✅ `src/osprey/services/python_executor/execution_control.py`
- ✅ `src/osprey/services/python_executor/execution_policy_analyzer.py`
- ✅ `src/osprey/services/python_executor/execution_wrapper.py`
- ✅ `src/osprey/services/python_executor/executor_node.py`
- ✅ `src/osprey/services/python_executor/generator_node.py`
- ✅ `src/osprey/services/python_executor/models.py`
- ✅ `src/osprey/services/python_executor/service.py`
- ✅ `src/osprey/services/python_executor/services.py`

### State (7 files)
- ✅ `src/osprey/state/__init__.py`
- ✅ `src/osprey/state/control.py`
- ✅ `src/osprey/state/execution.py`
- ✅ `src/osprey/state/messages.py`
- ✅ `src/osprey/state/session.py`
- ✅ `src/osprey/state/state_manager.py`
- ✅ `src/osprey/state/state.py`

### Templates (13 files)
- ✅ `src/osprey/templates/__init__.py`
- ✅ `src/osprey/templates/apps/__init__.py`
- ✅ `src/osprey/templates/apps/hello_world_weather/__init__.py`
- ✅ `src/osprey/templates/apps/hello_world_weather/capabilities/__init__.py`
- ✅ `src/osprey/templates/apps/hello_world_weather/mock_weather_api.py`
- ✓ `src/osprey/templates/apps/minimal/__init__.py`
- ✅ `src/osprey/templates/apps/minimal/capabilities/__init__.py`
- ✅ `src/osprey/templates/apps/wind_turbine/__init__.py`
- ✅ `src/osprey/templates/apps/wind_turbine/capabilities/__init__.py`
- ✅ `src/osprey/templates/apps/wind_turbine/data_sources/__init__.py`
- ✅ `src/osprey/templates/apps/wind_turbine/framework_prompts/__init__.py`
- ✅ `src/osprey/templates/apps/wind_turbine/mock_apis.py`
- ✅ `src/osprey/templates/services/jupyter/startup_script.py`

### Template Service Functions (4 files)
- ✅ `src/osprey/templates/services/open-webui/functions/agent_context_button.py`
- ✅ `src/osprey/templates/services/open-webui/functions/execution_history_button.py`
- ✅ `src/osprey/templates/services/open-webui/functions/execution_plan_editor.py`
- ✅ `src/osprey/templates/services/open-webui/functions/memory_button.py`

### Template Pipelines (2 files)
- ✅ `src/osprey/templates/services/pipelines/__init__.py`
- ✅ `src/osprey/templates/services/pipelines/main.py`

### Utils (5 files)
- ✅ `src/osprey/utils/__init__.py`
- ✅ `src/osprey/utils/config.py`
- ✅ `src/osprey/utils/log_filter.py`
- ✅ `src/osprey/utils/logger.py`
- ✅ `src/osprey/utils/streaming.py`

---

## Progress Summary

- **Total Files:** 136
- **Not Started:** 1
- **Working On:** 1
- **Completed:** 134

---

## Instructions for Sub-Agents

Each agent should:
1. Change status from ⬜ to 🔄 at the start
2. Apply renaming guidelines from `renaming_guidelines.md`
3. Change status from 🔄 to ✅ when complete
4. Report summary of changes made

---

**Last Updated:** Auto-generated on 2025-11-02
