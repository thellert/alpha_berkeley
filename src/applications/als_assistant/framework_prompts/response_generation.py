"""ALS Assistant response generation prompts."""

from typing import Optional

from framework.prompts.defaults.response_generation import DefaultResponseGenerationPromptBuilder
from framework.base import OrchestratorGuide, OrchestratorExample, PlannedStep, TaskClassifierGuide
from framework.registry import get_registry


class ALSResponseGenerationPromptBuilder(DefaultResponseGenerationPromptBuilder):
    """ALS-specific response generation prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the ALS-specific role definition."""
        return "You are an expert assistant for the Advanced Light Source (ALS) accelerator facility."
    
    def _get_conversational_guidelines(self) -> list[str]:
        """ALS-specific conversational guidelines - only override what's different."""
        return [
            "Be warm, professional, and genuine while staying focused on ALS-related assistance",
            "Answer general questions about ALS and your assistance capabilities naturally",
            "Respond to greetings and social interactions professionally",
            "Ask clarifying questions to better understand user needs when appropriate",
            "Provide helpful context about ALS operations and accelerator physics when relevant",
            "Be encouraging about the technical assistance available"
        ]
    
    def get_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create ALS-specific orchestrator snippet for respond capability."""
        registry = get_registry()
        
        technical_with_context_example = OrchestratorExample(
            step=PlannedStep(
                context_key="user_response",
                capability="respond",
                task_objective="Respond to user question about beam current analysis with statistical results",
                expected_output="user_response",
                success_criteria="Complete response using execution context data and analysis results",
                inputs=[
                    {registry.context_types.ANALYSIS_RESULTS: "beam_statistics"},
                    {registry.context_types.PV_VALUES: "current_readings"}
                ]
            ),
            scenario_description="Technical query with available execution context",
            notes="Will automatically use context-aware response generation with data retrieval."
        )
        
        conversational_example = OrchestratorExample(
            step=PlannedStep(
                context_key="user_response",
                capability="respond",
                task_objective="Respond to user question about available tools",
                expected_output="user_response",
                success_criteria="Friendly, informative response about ALS assistant capabilities",
                inputs=[]
            ),
            scenario_description="Conversational query 'What tools do you have?'",
            notes="Applies to all conversational user queries with no clear task objective."
        )
        
        mixed_query_example = OrchestratorExample(
            step=PlannedStep(
                context_key="user_response",
                capability="respond", 
                task_objective="Respond to 'What's the current status?' using available context",
                expected_output="user_response",
                success_criteria="Adaptive response using available context or explaining what's available",
                inputs=[
                    {registry.context_types.PV_VALUES: "status_readings"}
                ]
            ),
            scenario_description="Ambiguous query that might benefit from already available context",
            notes="CAUTION: be absolutely sure all relevant context is available for responding to the query!"
        )
        
        return OrchestratorGuide(
            instructions="""
                Plan "respond" as the final step for responding to user queries.
                Automatically handles both technical queries (with context) and conversational queries (without context).
                Use to provide the final response to the user's question.
                Always required unless asking clarifying questions.
                """,
            examples=[technical_with_context_example, conversational_example, mixed_query_example],
            priority=100  # Should come last in prompt ordering
        )
    
    def get_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Respond has no classifier - it's orchestrator-driven."""
        return None  # Always available, not detected from user intent
    
    def get_system_instructions(self, current_task: str = "", info=None, **kwargs) -> str:
        """Get system instructions for response generation agent configuration."""
        return self._get_dynamic_context(current_task=current_task, info=info, **kwargs)