"""ALS Assistant task extraction prompts."""

import textwrap
from framework.prompts.defaults.task_extraction import DefaultTaskExtractionPromptBuilder

class ALSTaskExtractionPromptBuilder(DefaultTaskExtractionPromptBuilder):
    """ALS-specific task extraction prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the ALS-specific role definition."""
        return "You are an ALS control system task extraction specialist that analyzes conversations to extract actionable tasks."
    
    def get_instructions(self) -> str:
        """Get the ALS-specific task extraction instructions."""
        return textwrap.dedent("""
        Your job is to:
        1. Understand what the user is asking for in the context of ALS accelerator operations
        2. Extract a clear, actionable task related to ALS control systems
        3. Determine if the task depends on chat history context
        4. Determine if the task depends on user memory

        ## ALS-Specific Guidelines:
        - Create self-contained task descriptions executable without conversation context
        - Resolve temporal references ("an hour ago", "that dip at 3 AM") to specific times/values using accelerator timestamps
        - Extract specific measurements, device names, and parameters from previous responses  
        - Understand ALS device naming conventions (e.g., SR01C___BPM1__AM00, LN___LLRF_A_AMP)
        - Consider available ALS data sources when interpreting requests
        - Set depends_on_chat_history=True if task references previous messages or needs conversation context
        - Set depends_on_user_memory=True only when the task directly incorporates specific information from user memory
        - Be specific and actionable in task descriptions using ALS terminology
        """).strip()