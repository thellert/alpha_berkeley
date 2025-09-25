"""ALS Assistant classification prompts."""

import textwrap
from framework.prompts.defaults.classification import DefaultClassificationPromptBuilder


class ALSClassificationPromptBuilder(DefaultClassificationPromptBuilder):
    """ALS-specific classification prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the role definition."""
        return "You are an expert task classification assistant."
    
    def get_task_definition(self) -> str:
        """Get the task definition."""
        return "Your goal is to determine if a user's request requires a certain capability."
    
    def get_instructions(self) -> str:
        """Get the classification instructions."""
        return textwrap.dedent("""
            Based on the instructions and examples, you must output a JSON object with a key "is_match": A boolean (true or false) indicating if the user's request matches the capability.

            Respond ONLY with the JSON object. Do not provide any explanation, preamble, or additional text.
            """).strip()