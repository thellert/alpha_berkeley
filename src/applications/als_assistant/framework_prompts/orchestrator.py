"""ALS Assistant orchestrator prompts."""

import textwrap
from typing import Optional
from framework.prompts.defaults.orchestrator import DefaultOrchestratorPromptBuilder
from framework.registry import get_registry


class ALSOrchestratorPromptBuilder(DefaultOrchestratorPromptBuilder):
    """ALS-specific orchestrator prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the ALS-specific role definition."""
        return "You are an expert execution planner for the ALS control system assistant."
    
    def get_task_definition(self) -> str:
        """Get the task definition."""
        return "TASK: Create a detailed execution plan that breaks down the user's request into specific, actionable steps."
    
    def get_instructions(self) -> str:
        """Get the ALS-specific planning instructions."""
        registry = get_registry()
        return textwrap.dedent(f"""
            Each step must follow the PlannedStep structure:
            - context_key: Unique identifier for this step's output (e.g., "beam_current_pvs", "historical_data")
            - capability: Type of execution node (determined based on available capabilities)
            - task_objective: Complete, self-sufficient description of what this step must accomplish
            - expected_output: Context type key (e.g., "{registry.context_types.PV_ADDRESSES}", "{registry.context_types.ARCHIVER_DATA}")
            - success_criteria: Clear criteria for determining step success
            - inputs: List of input dictionaries mapping context types to context keys:
              [
                {{"{registry.context_types.PV_ADDRESSES}": "some_pv_context"}},
                {{"{registry.context_types.ANALYSIS_RESULTS}": "some_analysis_context"}}
              ]
              **CRITICAL**: Include ALL required context sources! Complex operations often need multiple inputs.
            - parameters: Optional dict for step-specific configuration (e.g., {{"precision_ms": 1000}})

            Planning Guidelines:
            1. Dependencies between steps (ensure proper sequencing)
            2. Cost optimization (avoid unnecessary expensive operations)
            3. Clear success criteria for each step
            4. Proper input/output schema definitions
            5. Always reference available context using exact keys shown in context information

            The execution plan should be an ExecutionPlan containing a list of PlannedStep json objects.

            Focus on being practical and efficient while ensuring robust execution.
            Be factual and realistic about what can be accomplished.
            Never plan for simulated or fictional data - only real ALS control system operations.
            """).strip()