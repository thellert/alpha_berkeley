"""Default classification prompt implementation."""

import json
import textwrap
from typing import Optional, Dict
from framework.prompts.base import FrameworkPromptBuilder


class DefaultClassificationPromptBuilder(FrameworkPromptBuilder):
    """Default classification prompt builder."""
    
    PROMPT_TYPE = "classification"
    
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
    
    def get_dynamic_context(self, 
                          capability_instructions: str = "",
                          classifier_examples: str = "",
                          context: Optional[Dict] = None,
                          previous_failure: Optional[str] = None,
                          **kwargs) -> str:
        """Build dynamic context with capability info and context."""
        sections = []
        
        # Capability instructions
        if capability_instructions:
            sections.append(f"Here is the capability you need to assess:\n{capability_instructions}")
        
        # Examples
        if classifier_examples:
            sections.append(f"Examples:\n{classifier_examples}")
        
        # Previous execution context
        if context:
            sections.append(f"Previous execution context:\n{json.dumps(context, indent=4)}")
        
        # Previous failure context
        if previous_failure:
            sections.append(f"Previous approach failed: {previous_failure}")
        
        return "\n\n".join(sections)
    
    def get_system_instructions(self, 
                          capability_instructions: str = "",
                          classifier_examples: str = "",
                          context: Optional[Dict] = None,
                          previous_failure: Optional[str] = None,
                          **kwargs) -> str:
        """Get system instructions for task classification agent configuration."""
        sections = []
        
        # Role and instructions
        sections.append(self.get_role_definition())
        sections.append(self.get_task_definition())
        sections.append(self.get_instructions())
        
        # Dynamic context
        dynamic_context = self.get_dynamic_context(
            capability_instructions=capability_instructions,
            classifier_examples=classifier_examples,
            context=context,
            previous_failure=previous_failure,
            **kwargs
        )
        if dynamic_context:
            sections.append(dynamic_context)
        
        final_prompt = "\n\n".join(sections)
        
        # Debug: Print prompt if enabled
        self.debug_print_prompt(final_prompt)
        
        return final_prompt