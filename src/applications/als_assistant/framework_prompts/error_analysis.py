"""ALS Assistant error analysis prompts."""

import textwrap
from typing import Optional

from framework.prompts.defaults.error_analysis import DefaultErrorAnalysisPromptBuilder


class ALSErrorAnalysisPromptBuilder(DefaultErrorAnalysisPromptBuilder):
    """ALS-specific error analysis prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the ALS-specific role definition."""
        return "You are providing error analysis for the Advanced Light Source (ALS) accelerator facility control system."
    
    def get_instructions(self) -> str:
        """Get the ALS-specific error analysis instructions."""
        return textwrap.dedent("""
            A structured error report has already been generated with the following information:
            - Error type and timestamp
            - Task description and failed operation
            - Error message and technical details
            - Execution statistics and summary
            - Capability-specific recovery options
            
            Your role is to provide a brief explanation that adds value beyond the structured data:
            
            Requirements:
            - Write 2-3 sentences explaining what likely went wrong
            - Focus on the "why" rather than repeating the "what" 
            - Do NOT repeat the error message, recovery options, or execution details
            - Be specific to ALS accelerator operations when relevant
            - Consider the system capabilities context when suggesting alternatives
            - Keep it under 100 words
            - Use a professional, technical tone
            """).strip()