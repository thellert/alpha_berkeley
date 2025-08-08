"""
Code Generator Node - LangGraph Architecture

Generates Python code using LLM with clean exception handling.
Transformed for LangGraph integration with TypedDict state management.
"""

import textwrap
from typing import List, Dict, Any

from framework.models import get_chat_completion
from configs.logger import get_logger
from configs.unified_config import get_model_config
from configs.streaming import get_streamer

from .exceptions import CodeGenerationError, MaxAttemptsExceededError
from .models import PythonExecutionState
from .services import FileManager, NotebookManager

logger = get_logger("framework", "python_generator")


class LLMCodeGenerator:
    """Clean LLM-based code generator with proper exception handling"""
    
    def __init__(self, model_config=None):
        if model_config:
            self.model_config = model_config
        else:
            # Get model config from LangGraph configurable
            self.model_config = get_model_config("framework", "python_code_generator")
    
    async def generate_code(self, request, error_chain: List[str]) -> str:
        """Generate Python code - raises exceptions on failure"""
        try:
            # Build prompt with error feedback
            prompt = self._build_code_generation_prompt(request, error_chain)
            
            logger.info(f"Generating code with prompt length: {len(prompt)} characters")
            
            # Generate code using LLM
            generated_code = get_chat_completion(
                model_config=self.model_config,
                message=prompt
            )
            
            if not generated_code or not generated_code.strip():
                raise CodeGenerationError(
                    "LLM returned empty or invalid code",
                    generation_attempt=1,
                    error_chain=error_chain
                )
            
            logger.success(f"Successfully generated {len(generated_code)} characters of code")
            return generated_code.strip()
            
        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            
            # Convert any other errors to CodeGenerationError
            raise CodeGenerationError(
                f"LLM code generation failed: {str(e)}",
                generation_attempt=1,
                error_chain=error_chain,
                technical_details={"original_error": str(e)}
            )
    
    def _build_code_generation_prompt(self, request, error_chain: List[str]) -> str:
        """Build prompt for code generation with error feedback"""
        prompt_parts = []
        
        # Generic system instructions
        prompt_parts.append("You are an expert Python developer generating high-quality, executable code.")
        prompt_parts.append(textwrap.dedent("""
            === CODE GENERATION INSTRUCTIONS ===
            1. Generate complete, executable Python code
            2. Include all necessary imports at the top
            3. Use professional coding standards and clear variable names
            4. Add brief comments explaining complex logic
            5. STAY FOCUSED: Implement exactly what's requested - avoid over-engineering simple tasks
            6. Use provided context data when available (accessible via 'context' object)
            7. IMPORTANT: Store computed results in a dictionary variable named 'results' for automatic saving
            8. Generate ONLY the Python code, without markdown code blocks or additional explanation
        """))
        
        # Add capability-specific prompts
        if request.capability_prompts:
            for prompt_section in request.capability_prompts:
                if prompt_section and isinstance(prompt_section, str):
                    prompt_parts.append(prompt_section)
        
        # Add error feedback for retries
        if error_chain:
            prompt_parts.append("\n=== PREVIOUS ERRORS TO AVOID ===")
            for i, error in enumerate(error_chain[-3:], 1):  # Last 3 errors
                prompt_parts.append(f"{i}. {error}")
            prompt_parts.append("Please fix these issues in the new code.")
        
        prompt_parts.append("Generate ONLY the Python code, without markdown code blocks or additional explanation.")
        
        return "\n".join(prompt_parts)


def create_generator_node():
    """Create the code generator node function."""
    
    async def generator_node(state: PythonExecutionState) -> Dict[str, Any]:
        """Generate Python code using LLM."""
        
        # Debug log what we received in state
        logger.debug(f"Generator node received state type: {type(state)}")
        logger.debug(f"Generator node state keys: {list(state.keys()) if hasattr(state, 'keys') else 'no keys method'}")
        if hasattr(state, 'keys') and 'request' in state:
            logger.debug(f"Request found in state: {type(state['request'])}")
        else:
            logger.error(f"NO REQUEST FOUND IN STATE! State content: {state}")
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("python_executor", "generator", state)
        streamer.status("Generating Python code...")
        
        # Use existing code generator logic - access request data via state.request
        generator = LLMCodeGenerator()
        
        try:
            # Generate code with error feedback from previous attempts
            # CRITICAL: Access original request through state.request
            generated_code = await generator.generate_code(
                state["request"],  # Pass original PythonExecutionRequest
                state.get("error_chain", [])  # Use service state for error tracking
            )
            
            streamer.status(f"Generated {len(generated_code)} characters of code")
            
            logger.info(f"Code generated successfully: {len(generated_code)} characters")
            
            # Update state with generated code
            return {
                "generated_code": generated_code,
                "generation_attempt": state.get("generation_attempt", 0) + 1,
                "current_stage": "analysis"
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            
            # Add error to chain and check retry limits
            error_chain = state.get("error_chain", []) + [str(e)]
            max_retries = state["request"].retries
            
            if len(error_chain) >= max_retries:
                return {
                    "error_chain": error_chain,
                    "is_failed": True,
                    "failure_reason": f"Code generation failed after {max_retries} attempts"
                }
            else:
                return {
                    "error_chain": error_chain,
                    "generation_attempt": state.get("generation_attempt", 0) + 1
                }
    
    return generator_node
 