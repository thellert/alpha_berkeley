"""ALS Assistant memory extraction prompts."""

import textwrap
from typing import List, Optional
from pydantic import BaseModel, Field

from framework.prompts.defaults.memory_extraction import DefaultMemoryExtractionPromptBuilder, MemoryContentExtraction, MemoryExtractionExample
from framework.state import ChatHistoryFormatter, UserMemories
from framework.base import OrchestratorGuide, OrchestratorExample, PlannedStep, ClassifierExample, TaskClassifierGuide, ClassifierActions
from langchain_core.messages import BaseMessage
from framework.state import MessageUtils


class ALSMemoryExtractionPromptBuilder(DefaultMemoryExtractionPromptBuilder):
    """ALS-specific memory extraction prompt builder."""
    
    def get_role_definition(self) -> str:
        """Get the role definition."""
        return "You are an expert content extraction assistant. Your task is to identify and extract content that a user wants to save to their memory from their message."
    
    def get_task_definition(self) -> str:
        """Get the task definition."""
        return "TASK: Extract content from the user's message that they want to save/store/remember."
    
    def get_instructions(self) -> str:
        """Get the memory extraction instructions."""
        return textwrap.dedent("""
            INSTRUCTIONS:
            1. Analyze the user message to identify content they explicitly want to save
            2. Look for patterns like:
               - "save this:" followed by content
               - "remember that [content]"
               - "store [content] in my memory"
               - "add to memory: [content]"
               - Content in quotes that should be saved
               - Explicit instructions to save specific information
            3. Extract the ACTUAL CONTENT to be saved, not the instruction itself
            4. If no clear content is identified for saving, set found=false
            5. Provide a brief explanation of your decision

            CRITICAL REQUIREMENTS:
            - Only extract content that is clearly intended for saving/storage
            - Do not extract questions, commands, or conversational text
            - Remove quotes and prefixes like "save this:", "remember that", etc.
            - Extract the pure content to be remembered
            - Be conservative - if unclear, set found=false
            """).strip()
    
    def _get_examples(self, **kwargs) -> List[MemoryExtractionExample]:
        """Get ALS-specific memory extraction examples."""
        return [
            # Technical operational insight - complex multi-parameter correlation
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("I've been analyzing the beam lifetime data and there's a strong correlation with vacuum pressure in sector 7"),
                    MessageUtils.create_assistant_message("That's an interesting finding. The analysis shows a 15% lifetime reduction when sector 7 vacuum exceeds 2.5e-9 Torr. This could indicate a slow leak or pump degradation."),
                    MessageUtils.create_user_message("I agree. Please remember this correlation.")
                ],
                expected_output=MemoryContentExtraction(
                    content="sector 7 vacuum above 2.5e-9 Torr correlates with 15% beam lifetime reduction, likely indicates pump issues",
                    found=True,
                    explanation="Technical operational insight about vacuum-lifetime correlation with specific thresholds and diagnosis"
                )
            ),
            
            # Maintenance procedure discovery with specific PV references
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("During the ID gap optimization today, I found that BR1_____TMP_MA__CALC needs to be monitored closely"),
                    MessageUtils.create_assistant_message("The current value of BR1_____TMP_MA__CALC is 73.0°C. Do you want me to create a monitoring sub-routine?"),
                    MessageUtils.create_user_message('Store this finding: "BR1_____TMP_MA__CALC shows thermal runaway when ID gap < 8mm during high current operations - requires 30min cooldown"')
                ],
                expected_output=MemoryContentExtraction(
                    content="BR1_____TMP_MA__CALC shows thermal runaway when ID gap < 8mm during high current operations - requires 30min cooldown",
                    found=True,
                    explanation="User explicitly requested to save a specific string of text, no conversational context should be included."
                )
            ),
            
            # Research insight with quantitative results
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("The quadrupole scan analysis revealed optimal beam size occurs at 105.3A ± 0.2A, save this for the beam physics meeting tomorrow")
                ],
                expected_output=MemoryContentExtraction(
                    content="optimal beam size occurs at quadrupole current 105.3A ± 0.2A",
                    found=True,
                    explanation="Quantitative research finding with specific parameter values and uncertainty bounds"
                )
            ),
            
            # Complex operational pattern with temporal dependency
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("Can you remember that orbit correction works best when applied 15 minutes after injection, before the beam settles into thermal equilibrium? The optimal window is between 15-45 minutes post-injection when thermal drifts are still predictable.")
                ],
                expected_output=MemoryContentExtraction(
                    content="orbit correction works best when applied 15 minutes after injection, before the beam settles into thermal equilibrium - optimal window is between 15-45 minutes post-injection when thermal drifts are still predictable",
                    found=True,
                    explanation="Complex operational timing procedure with specific time windows and physical reasoning"
                )
            ),
            
            # Safety-critical threshold with immediate action required
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("After today's beam dump analysis, please store this critical finding"),
                    MessageUtils.create_assistant_message("What would you like me to remember?"),
                    MessageUtils.create_user_message("Remember: BPM readings above 15mm in any sector indicate imminent beam loss - abort injection immediately and check for magnet power supply faults")
                ],
                expected_output=MemoryContentExtraction(
                    content="BPM readings above 15mm in any sector indicate imminent beam loss - abort injection immediately and check for magnet power supply faults",
                    found=True,
                    explanation="Safety-critical operational threshold with specific trigger values and required emergency actions"
                )
            ),
            
            # Multi-system diagnostic pattern
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("I want to save this diagnostic pattern we discovered today during troubleshooting"),
                    MessageUtils.create_assistant_message("What pattern did you identify?"),
                    MessageUtils.create_user_message('Save: "RF cavity temperature spikes precede beam lifetime drops by exactly 12 minutes - monitor SR:RF:TEMP for early warning of instabilities"')
                ],
                expected_output=MemoryContentExtraction(
                    content="RF cavity temperature spikes precede beam lifetime drops by exactly 12 minutes - monitor SR:RF:TEMP for early warning of instabilities",
                    found=True,
                    explanation="Predictive diagnostic pattern with specific timing and monitoring recommendations"
                )
            ),
            
            # Negative example - routine status check (should not save)
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("What's the current beam current and how's the machine running today?"),
                    MessageUtils.create_assistant_message("Current beam current is 482.3 mA. Machine status is normal with good beam stability."),
                    MessageUtils.create_user_message("Thanks, everything looks good for user operations today")
                ],
                expected_output=MemoryContentExtraction(
                    content="",
                    found=False,
                    explanation="This is routine operational status checking and acknowledgment, not content intended for permanent memory"
                )
            ),
            
            # Negative example - procedural question (should not save)
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("How do I access the archiver data for BPM readings from last week?")
                ],
                expected_output=MemoryContentExtraction(
                    content="",
                    found=False,
                    explanation="This is a procedural question about system usage, not content to be saved to memory"
                )
            ),
            
            # Edge case - mixed content with explicit save instruction
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("The beam dump at 14:30 was caused by a power supply trip, but don't save that. However, do remember that we found the root cause: humidity sensors in building 6 are reading 85% which triggers the HVAC overcooling cycle that affects the magnet power supplies through ground loops.")
                ],
                expected_output=MemoryContentExtraction(
                    content="humidity sensors in building 6 reading 85% triggers HVAC overcooling cycle that affects magnet power supplies through ground loops",
                    found=True,
                    explanation="User explicitly requested to save specific root cause analysis while excluding incident details"
                )
            ),
            
            # Complex calibration procedure with multiple parameters
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("Store this calibration procedure for future reference: EPU gap calibration requires setting harmonic field at 2.1T, adjusting phase offset to 15.7 degrees, then performing 3-point verification scan between 12-18mm gap range with 0.5mm steps while monitoring photon flux stability within 2% tolerance")
                ],
                expected_output=MemoryContentExtraction(
                    content="EPU gap calibration requires setting harmonic field at 2.1T, adjusting phase offset to 15.7 degrees, then performing 3-point verification scan between 12-18mm gap range with 0.5mm steps while monitoring photon flux stability within 2% tolerance",
                    found=True,
                    explanation="Detailed calibration procedure with multiple specific parameters and tolerances"
                )
            ),
            
            # Negative example - conversational acknowledgment (should not save)
            MemoryExtractionExample(
                messages=[
                    MessageUtils.create_user_message("That orbit analysis was excellent - really helped us understand the coupling resonance. The visualizations made it clear to the whole team.")
                ],
                expected_output=MemoryContentExtraction(
                    content="",
                    found=False,
                    explanation="This is positive feedback about analysis quality, not technical content to be preserved"
                )
            )
        ]
    
    def get_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create ALS-specific orchestrator snippet for memory operations."""
        
        # Define structured examples
        save_memory_example = OrchestratorExample(
            step=PlannedStep(
                context_key="memory_save",
                capability="memory",
                task_objective="Save the important finding about beam lifetime correlation to memory",
                expected_output="string",
                success_criteria="Memory entry saved successfully",
                inputs=[]
            ),
            scenario_description="Saving important information to user memory",
            notes="Content is persisted directly to user's memory file."
        )
        
        show_memory_example = OrchestratorExample(
            step=PlannedStep(
                context_key="memory_display",
                capability="memory",
                task_objective="Show all my saved memory entries",
                expected_output="string",
                success_criteria="Memory content displayed to user",
                inputs=[]
            ),
            scenario_description="Displaying stored memory content",
            notes="Returns memory content directly to user."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                When to plan "memory" steps:
                - When the user explicitly asks to save, store, or remember something for later
                - When the user asks to show, display, or view their saved memory
                - When the user explicitly mentions memory operations
                
                **IMPORTANT**: This capability has a VERY STRICT classifier. Only use when users 
                explicitly mention memory-related operations. Do NOT use for general information 
                storage or context management.
                
                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "memory_save", "memory_display")
                - task_objective: The specific memory operation to perform
                
                **Output:**
                - Save operations: Persist content directly to user's memory file
                - Show operations: Return memory content directly to user
                - No context storage needed - memory is already persisted
                
                Only plan this step when users explicitly request memory operations.
                """),
            examples=[save_memory_example, show_memory_example],
            priority=10  # Later in the prompt ordering since it's specialized
        )

    def get_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create ALS-specific classifier configuration for memory operations."""
        
        # Create memory-specific examples
        memory_examples = [
            ClassifierExample(
                query="Save this finding to my memory: vacuum pressure correlates with beam lifetime",
                result=True,
                reason="Direct memory save request with specific content to preserve"
            ),
            ClassifierExample(
                query="Remember that orbit correction works best 15 minutes after injection",
                result=True,
                reason="Memory save request using 'remember' keyword with procedural knowledge"
            ),
            ClassifierExample(
                query="What do I have saved in my memory about beam physics?",
                result=True,
                reason="Memory retrieval request asking to show stored information"
            ),
            ClassifierExample(
                query="Show me my saved notes",
                result=True,
                reason="Memory retrieval request for displaying saved content"
            ),
            ClassifierExample(
                query="Store this calibration procedure: set harmonic field at 2.1T",
                result=True,
                reason="Explicit store request with specific technical procedure to save"
            )
        ]
        
        return TaskClassifierGuide(
            instructions="Determine if the task involves saving content to memory or retrieving content from memory.",
            examples=memory_examples,
            actions_if_true=ClassifierActions()
        )