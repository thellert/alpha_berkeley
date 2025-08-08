"""Default response generation prompt implementation."""

import textwrap
from typing import Optional, Dict, Any

from framework.prompts.base import FrameworkPromptBuilder
from framework.base import OrchestratorGuide, OrchestratorExample, PlannedStep, TaskClassifierGuide


class DefaultResponseGenerationPromptBuilder(FrameworkPromptBuilder):
    """Default response generation prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the generic role definition."""
        return "You are an expert assistant for workflow automation and data analysis."
    
    def get_task_definition(self) -> Optional[str]:
        """Task definition is embedded dynamically in instructions."""
        return None
    
    def get_instructions(self) -> str:
        """Instructions are completely dynamic based on execution context."""
        # This will be handled in get_dynamic_context
        return ""
    
    def get_dynamic_context(self, current_task: str = "", info=None, **kwargs) -> str:
        """Build dynamic response generation prompt based on execution context."""
        sections = []
        
        # Base role with current task
        sections.append(f"You are an expert assistant for workflow automation and data analysis.\n\nCURRENT TASK: {current_task}")
        
        if info:
            # Context prioritization: Show specific context if available, otherwise show all execution context
            if hasattr(info, 'relevant_context') and info.relevant_context:
                # Specific execution context provided as input to response node - show only this
                sections.append(self._get_data_section(info.relevant_context))
            elif hasattr(info, 'execution_history') and info.execution_history:
                # No specific context, but execution history available - show all execution context
                sections.append(self._get_execution_section(info))
            
            # Capabilities section for conversational responses
            if (not hasattr(info, 'execution_history') or not info.execution_history) and hasattr(info, 'capabilities_overview') and info.capabilities_overview:
                sections.append(self._get_capabilities_section(info.capabilities_overview))
            
            # Guidelines section
            sections.append(self._get_guidelines_section(info))
        
        return "\n\n".join(sections)
    
    def _get_execution_section(self, info) -> str:
        """Get execution summary - keep concise but informative."""
        if hasattr(info, 'is_killed') and info.is_killed:
            # Handle terminated execution
            partial_results = []
            for record in info.execution_history:
                if record.get("success", False):
                    task_objective = record.get("step", {}).get("task_objective", "Unknown task")
                    partial_results.append(f"✓ {task_objective}")
                else:
                    task_objective = record.get("step", {}).get("task_objective", "Unknown task")
                    error_msg = record.get("result_summary", "Unknown error")
                    partial_results.append(f"✗ {task_objective}: {error_msg}")
            
            partial_summary = "\n".join(partial_results) if partial_results else "No steps completed"
            
            return textwrap.dedent(f"""
                EXECUTION STATUS: Terminated
                TERMINATION REASON: {getattr(info, 'kill_reason', None) or "Unknown termination reason"}

                PARTIAL SUMMARY:
                {partial_summary}

                EXECUTION STATS:
                - Total steps executed: {getattr(info, 'total_steps_executed', 0)}
                - Execution time: {getattr(info, 'execution_start_time', 'Unknown')}
                - Reclassifications: {getattr(info, 'reclassification_count', 0)}
                """).strip()
        else:
            # Handle successful execution
            summary_parts = []
            for i, record in enumerate(info.execution_history, 1):
                if record.get("success", False):
                    task_objective = record.get("step", {}).get("task_objective", "Unknown task")
                    summary_parts.append(f"Step {i}: {task_objective} - Completed")
                else:
                    task_objective = record.get("step", {}).get("task_objective", "Unknown task")
                    error_msg = record.get("result_summary", "Unknown error")
                    summary_parts.append(f"Step {i}: {task_objective} - Failed: {error_msg}")
            
            summary_text = "\n".join(summary_parts) if summary_parts else "No execution steps completed"
            
            return textwrap.dedent(f"""
                EXECUTION SUMMARY:
                {summary_text}
                """).strip()
    
    def _get_data_section(self, relevant_context: Dict[str, Any]) -> str:
        """Get retrieved data section."""
        formatted_context = self._format_context_data(relevant_context)
        
        return textwrap.dedent(f"""
            RETRIEVED DATA:
            {formatted_context}
            """).strip()
    
    def _format_context_data(self, context_data: Dict[str, Any]) -> str:
        """Format retrieved context data for the response.
        
        :param context_data: Dictionary of context_type.context_key -> data
        :type context_data: Dict[str, Any]
        :return: Formatted string with the context data
        :rtype: str
        """
        if not context_data:
            return "No context data was retrieved."
        
        formatted_lines = []
        formatted_lines.append("-" * 30)

        for data_key, data in context_data.items():
            formatted_lines.append(f"\n[{data_key}]")
            
            try:
                # Format as clean JSON for readability
                import json
                formatted_data = json.dumps(data, indent=2, default=str)
                formatted_lines.append(formatted_data)
            except Exception as e:
                # Fallback to string representation
                formatted_lines.append(f"<Could not format as JSON: {str(e)}>")
                formatted_lines.append(str(data))
            
            formatted_lines.append("-" * 30)
        
        return "\n".join(formatted_lines)
    
    def _get_capabilities_section(self, capabilities_overview: str) -> str:
        """Get capabilities overview for conversational responses."""
        return textwrap.dedent(f"""
            SYSTEM CAPABILITIES:
            {capabilities_overview}
            """).strip()
    
    def _get_guidelines_section(self, info) -> str:
        """Get contextually appropriate guidelines to avoid conflicts."""
        guidelines = ["Provide a clear, accurate response"]
        
        # Add current date context for temporal awareness
        if hasattr(info, 'current_date') and info.current_date:
            guidelines.append(f"Today's date is {info.current_date} - use this for temporal context and date references")
        
        if not hasattr(info, 'execution_history') or not info.execution_history:
            # Conversational response
            guidelines.extend([
                "Be warm, professional, and genuine while staying focused on providing assistance",
                "Answer general questions about the system and your capabilities naturally",
                "Respond to greetings and social interactions professionally",
                "Ask clarifying questions to better understand user needs when appropriate",
                "Provide helpful context about system operations when relevant",
                "Be encouraging about the technical assistance available"
            ])
        elif hasattr(info, 'relevant_context') and info.relevant_context:
            # Technical response with relevant context
            guidelines.extend([
                "Be very accurate but use reasonable judgment when rounding or abbreviating numerical data for readability",
                "NEVER make up, estimate, or fabricate any data - only use what is actually retrieved",
                "Explain any data limitations or warnings", 
                "Be specific about time ranges and data sources"
            ])
        
        if hasattr(info, 'is_killed') and info.is_killed:
            # Execution terminated
            guidelines.extend([
                "Clearly explain why execution was terminated",
                "Acknowledge any partial progress that was made", 
                "Suggest practical alternatives (simpler query, different approach, etc.)",
                "Be helpful and encouraging, not apologetic",
                "Offer to help with a modified or simpler version of the request",
                "NEVER make up or fabricate any results that weren't actually obtained"
            ])
        elif hasattr(info, 'execution_history') and info.execution_history and (not hasattr(info, 'relevant_context') or not info.relevant_context):
            # Technical response with no relevant context
            guidelines.extend([
                "Explain what was accomplished during execution",
                "Note any limitations in accessing detailed results",
                "NEVER make up or fabricate any technical data - only describe what actually happened"
            ])
        
        return "GUIDELINES:\n" + "\n".join(f"{i+1}. {g}" for i, g in enumerate(guidelines))
    
    def get_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create generic orchestrator guide for respond capability."""
        
        technical_with_context_example = OrchestratorExample(
            step=PlannedStep(
                context_key="user_response",
                capability="respond",
                task_objective="Respond to user question about data analysis with statistical results",
                expected_output="user_response",
                success_criteria="Complete response using execution context data and analysis results",
                inputs=[
                    {"ANALYSIS_RESULTS": "data_statistics"},
                    {"DATA_VALUES": "current_readings"}
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
                success_criteria="Friendly, informative response about assistant capabilities",
                inputs=[]
            ),
            scenario_description="Conversational query 'What tools do you have?'",
            notes="Applies to all conversational user queries with no clear task objective."
        )
        
        return OrchestratorGuide(
            instructions="""
                Plan "respond" as the final step to deliver results to the user.
                Always include respond as the last step in execution plans.
                """,
            examples=[technical_with_context_example, conversational_example],
            priority=100  # Should come last in prompt ordering (same as final_response)
        )
    
    def get_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Respond has no classifier guide - it's orchestrator-driven."""
        return None  # Always available, not detected from user intent
    
