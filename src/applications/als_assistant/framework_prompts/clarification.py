"""ALS Assistant clarification prompts."""

import textwrap
from typing import Optional

from framework.prompts.defaults.clarification import DefaultClarificationPromptBuilder
from framework.base import OrchestratorGuide, OrchestratorExample, PlannedStep, TaskClassifierGuide


class ALSClarificationPromptBuilder(DefaultClarificationPromptBuilder):
    """ALS-specific clarification prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the ALS-specific role definition."""
        return "You are helping to clarify ambiguous user queries for the Advanced Light Source (ALS) accelerator facility."
    
    def get_task_definition(self) -> str:
        """Get the task definition."""
        return "Your task is to generate specific, targeted questions that will help clarify what the user needs."
    
    def get_instructions(self) -> str:
        """Get the ALS-specific clarification instructions."""
        return textwrap.dedent("""
            GUIDELINES:
            1. Ask about missing technical details (which system, time range, specific parameters)
            2. Clarify vague terms (what type of "data", "status", "analysis" etc.)
            3. Ask about output preferences (plot, numbers, summary, etc.)
            4. Be specific and actionable - avoid generic questions
            5. Limit to 2-3 most important questions
            6. Make questions easy to answer

            Generate targeted questions that will help get the specific information needed to provide accurate assistance.
            """).strip()
    
    def get_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create ALS-specific orchestrator snippet for clarification capability."""
        
        ambiguous_system_example = OrchestratorExample(
            step=PlannedStep(
                context_key="data_clarification",
                capability="clarify",
                task_objective="Ask user for clarification when request 'show me some data' is too vague",
                expected_output="",
                success_criteria="Specific questions about data type, system, and time range",
                inputs=[]
            ),
            scenario_description="Vague data request needing system and parameter clarification", 
        )
        
        missing_parameters_example = OrchestratorExample(
            step=PlannedStep(
                context_key="time_range_clarification", 
                capability="clarify",
                task_objective="Ask user for missing time range when they request 'beam stability trends' without specifying timeframe",
                expected_output="",
                success_criteria="Questions about specific time range and analysis scope",
                inputs=[
                    {"PV_ADDRESSES": "beam_current_pvs"}
                ]
            ),
            scenario_description="Missing time range parameters for historical data request",
            notes="Can use partial context (like found PVs) to ask more targeted questions about missing information."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent("""
                Plan "clarify" when user queries lack specific details needed for execution.
                Use instead of respond when information is insufficient.
                Replaces technical execution steps until user provides clarification.
                """).strip(),
            examples=[ambiguous_system_example, missing_parameters_example],
            priority=99  # Should come near the end, but before respond
        )
    
    def get_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Clarify has no classifier - it's orchestrator-driven."""
        return None  # Always available, not detected from user intent