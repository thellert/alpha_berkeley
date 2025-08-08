"""Example Framework - Few-Shot Learning and Prompt Engineering System

This module provides the comprehensive example and prompt engineering system
for the ALS Expert framework. It implements sophisticated few-shot learning
patterns, orchestration guidance, and classification training examples that
enable intelligent LLM-based components throughout the framework.

The example system serves as the foundation for consistent prompt engineering
and few-shot learning across all framework components. It provides structured
patterns for capability orchestration, task classification, and LLM guidance
that ensure reliable and predictable behavior from language model components.

Key Example System Components:
    1. **BaseExample**: Abstract foundation for all example types
    2. **OrchestratorExample**: Rich examples for execution planning guidance
    3. **ClassifierExample**: Training examples for task classification
    4. **Guide Systems**: Structured guidance for orchestration and classification
    5. **Formatting Utilities**: Consistent prompt formatting and bias prevention

Example Type Hierarchy:
    - **BaseExample**: Abstract base with common formatting interface
    - **OrchestratorExample**: Detailed planning examples with context requirements
    - **ClassifierExample**: Query/result/reason triplets for classification training
    - **OrchestratorGuide**: Complete orchestration guidance with priority ordering
    - **TaskClassifierGuide**: Classification guidance with few-shot examples

The example system emphasizes bias prevention through randomization, consistent
formatting for reliable LLM consumption, and comprehensive context provision
for effective few-shot learning. All examples are designed to work seamlessly
with the framework's prompt building and LLM integration systems.

.. note::
   The example system uses randomization in ClassifierExample formatting to
   prevent positional bias in few-shot learning. OrchestratorExample provides
   rich context to ensure effective execution planning.

.. warning::
   Example quality directly impacts LLM performance. Ensure examples are
   accurate, representative, and properly formatted to maintain system
   reliability and predictable behavior.

.. seealso::
   :class:`BaseCapability` : Capability integration with example guides
   :mod:`framework.prompts` : Prompt building and LLM integration systems
   :mod:`framework.infrastructure.classifier` : Classification system integration
"""

import dataclasses
import json
import random
import textwrap
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from .planning import PlannedStep


@dataclass
class BaseExample(ABC):
    """Abstract base class for all few-shot examples with consistent formatting interface.
    
    This abstract base class establishes the foundational interface for all example
    types used in few-shot learning and prompt engineering throughout the ALS Expert
    framework. It enforces consistent formatting patterns that ensure reliable LLM
    consumption and predictable behavior across all example implementations.
    
    The BaseExample class serves multiple critical functions:
    1. **Interface Standardization**: Common format_for_prompt() method across all examples
    2. **Type Safety**: Clear inheritance hierarchy for example type checking
    3. **Consistency Enforcement**: Uniform presentation patterns for LLM consumption
    4. **Framework Integration**: Seamless integration with prompt building systems
    5. **Extensibility**: Clear extension points for domain-specific example types
    
    All concrete example classes must inherit from this base and implement the
    format_for_prompt() method to define their specific formatting behavior.
    This ensures that examples can be used polymorphically throughout the
    framework while maintaining consistent output formats.
    
    .. note::
       This is an abstract base class that cannot be instantiated directly.
       Subclasses must implement the format_for_prompt() method to provide
       their specific formatting logic.
    
    .. warning::
       Example formatting directly impacts LLM performance. Ensure implementations
       produce consistent, well-structured output that follows established patterns
       for reliable model consumption.
    
    Example::
    
        @dataclass
        class CustomExample(BaseExample):
            content: str
            category: str
            
            def format_for_prompt(self) -> str:
                return f"Category: {self.category}\nContent: {self.content}"
    
    
    .. seealso::
       :class:`OrchestratorExample` : Planning examples for capability orchestration
       :class:`ClassifierExample` : Training examples for task classification
    """
    
    @abstractmethod
    def format_for_prompt(self) -> str:
        """Format this example for inclusion in LLM prompts with consistent structure.
        
        This is the core formatting method that all example subclasses must implement.
        It transforms the example data into a string format optimized for LLM consumption
        and few-shot learning. The method should produce consistent, well-structured
        output that follows established formatting patterns for reliable model performance.
        
        Implementation guidelines:
        1. **Consistency**: Use consistent formatting patterns across similar examples
        2. **Clarity**: Ensure output is clear and unambiguous for LLM interpretation
        3. **Completeness**: Include all necessary context for effective few-shot learning
        4. **Efficiency**: Generate concise but comprehensive example representations
        
        :return: Formatted string representation optimized for LLM prompt inclusion
        :rtype: str
        :raises NotImplementedError: This is an abstract method that must be implemented
        
        .. note::
           The formatted output will be directly included in LLM prompts, so it should
           be optimized for model consumption and follow consistent patterns to ensure
           reliable few-shot learning performance.
        
        .. warning::
           Poorly formatted examples can significantly impact LLM performance. Test
           formatting output thoroughly to ensure it produces the expected behavior
           in few-shot learning scenarios.
        """
        pass


@dataclass
class OrchestratorExample(BaseExample):
    """Structured example for orchestrator prompt showing how to plan steps with this capability.
    
    This class provides rich examples that demonstrate how to plan execution steps
    with specific capabilities. Each example includes the planned step, scenario
    context, requirements, and optional notes to guide the orchestrator in
    creating effective execution plans.
    
    :param step: The planned execution step demonstrating capability usage
    :type step: PlannedStep
    :param scenario_description: Human-readable description of when/why to use this capability
    :type scenario_description: str
    :param context_requirements: What data needs to be available in execution context
    :type context_requirements: Optional[Dict[str, str]]
    :param notes: Additional guidance, caveats, or usage tips
    :type notes: Optional[str]
    """
    step: PlannedStep
    scenario_description: str  # Human-readable description of when/why to use this
    context_requirements: Optional[Dict[str, str]] = None  # What needs to be in context
    notes: Optional[str] = None  # Additional guidance or caveats
    
    def format_for_prompt(self) -> str:
        """Format this orchestrator example for execution planning with comprehensive context.
        
        This method transforms the orchestrator example into a rich, structured format
        suitable for guiding execution planning in orchestration systems. It provides
        complete context including scenario descriptions, step specifications, context
        requirements, and additional notes to enable effective capability planning.
        
        The formatting dynamically adapts to the PlannedStep structure and includes:
        1. **Scenario Description**: Clear context for when to use this capability
        2. **Context Requirements**: Prerequisites for successful execution
        3. **Step Specification**: Complete PlannedStep details with all parameters
        4. **Additional Notes**: Supplementary guidance and usage tips
        
        :return: Formatted string with complete orchestration context for planning guidance
        :rtype: str
        
        .. note::
           The formatting dynamically adapts to the PlannedStep structure, only
           including fields that have values. This ensures clean, focused examples
           without unnecessary null or empty fields.
        
        .. warning::
           The step formatting accesses PlannedStep fields dynamically. Ensure the
           step object is properly constructed with valid field values to avoid
           formatting issues.
        
        Examples:
            Formatted orchestrator example output::
            
                example = OrchestratorExample(
                    step=PlannedStep(
                        context_key="weather_data",
                        capability="weather_retrieval",
                        task_objective="Get current weather",
                        success_criteria="Weather data retrieved"
                    ),
                    scenario_description="When user requests weather information",
                    context_requirements={"location": "User location data"}
                )
                formatted = example.format_for_prompt()
                # Returns formatted example with scenario, requirements, and step details
        
        .. seealso::
           :func:`_format_field_value` : Field value formatting helper method
           :class:`PlannedStep` : Execution step structure and field definitions
        """
        formatted_text = f"**{self.scenario_description}**\n"
        
        # Add context requirements if specified
        if self.context_requirements:
            formatted_text += "   - Context requirements:\n"
            for key, desc in self.context_requirements.items():
                formatted_text += f"     * {key}: {desc}\n"
        
        # Format the step dynamically based on actual PlannedStep structure
        formatted_text += f"   PlannedStep(\n"
        
        # Get all fields from the PlannedStep TypedDict dynamically
        step_fields = PlannedStep.__annotations__.keys()
        
        for field_name in step_fields:
            field_value = getattr(self.step, field_name, None)
            
            # Skip fields that are None or empty
            if field_value is None or (isinstance(field_value, (list, dict)) and not field_value):
                continue
            
            # Format the field
            formatted_value = self._format_field_value(field_name, field_value)
            formatted_text += f"       {field_name}={formatted_value},\n"
        
        # Remove the trailing comma and newline, then close the parenthesis
        formatted_text = formatted_text.rstrip(",\n") + "\n"
        formatted_text += "   )\n"
        
        # Add notes if specified
        if self.notes:
            formatted_text += f"   - Note: {self.notes}\n"
        
        return formatted_text
    
    def _format_field_value(self, field_name: str, value: Any) -> str:
        """Format a field value for consistent display in orchestrator prompt examples.
        
        This helper method transforms various Python data types into string
        representations suitable for inclusion in LLM prompts. It handles common
        data types with appropriate formatting to ensure consistent and readable
        example presentation in orchestration guidance.
        
        Supported formatting patterns:
        - None values: "None"
        - Strings: Quoted with double quotes
        - Dictionaries: JSON format or empty braces
        - Lists/Sets: JSON format or empty brackets
        - Other types: Python repr() representation
        
        :param field_name: Name of the field being formatted (for context)
        :type field_name: str
        :param value: The value to format for prompt inclusion
        :type value: Any
        :return: Formatted string representation suitable for LLM consumption
        :rtype: str
        
        .. note::
           The formatting prioritizes readability and consistency for LLM consumption
           while maintaining valid Python-like syntax where applicable.
        
        Examples:
            Various value formatting::
            
                formatter._format_field_value("name", "weather_data")  # Returns: '"weather_data"'
                formatter._format_field_value("params", {"key": "value"})  # Returns: '{"key": "value"}'
                formatter._format_field_value("items", [1, 2, 3])  # Returns: '[1, 2, 3]'
                formatter._format_field_value("empty", None)  # Returns: 'None'
        """
        if value is None:
            return "None"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, dict):
            return json.dumps(value) if value else "{}"
        elif isinstance(value, (list, set)):
            return json.dumps(list(value)) if value else ("[]" if isinstance(value, list) else "set()")
        else:
            return repr(value)
    
    @staticmethod
    def format_examples_for_prompt(examples: List['OrchestratorExample']) -> str:
        """Format multiple orchestrator examples for LLM prompt inclusion with consistent structure.
        
        This method transforms a collection of OrchestratorExample objects into a
        formatted string suitable for inclusion in LLM prompts. It provides numbered
        examples with consistent spacing and section headers to ensure reliable
        consumption by orchestration systems.
        
        The formatting follows established patterns for orchestration guidance:
        1. **Section Header**: Clear identification of example content
        2. **Numbered Examples**: Sequential numbering for easy reference
        3. **Consistent Spacing**: Uniform formatting for reliable parsing
        4. **Complete Context**: Full example details including scenarios and requirements
        
        :param examples: List of orchestrator examples to format for prompt inclusion
        :type examples: List[OrchestratorExample]
        :return: Formatted string with numbered examples and section headers
        :rtype: str
        
        .. note::
           Returns empty string if no examples are provided. The formatting preserves
           all example details including scenario descriptions, context requirements,
           and additional notes for comprehensive orchestration guidance.
        
        Examples:
            Formatting orchestrator examples::
            
                examples = [example1, example2, example3]
                formatted = OrchestratorExample.format_examples_for_prompt(examples)
                # Returns: "\n\n**Example Step Planning:**\n\n1. **Scenario...**\n..."
        
        .. seealso::
           :func:`format_for_prompt` : Individual example formatting method
        """
        if not examples:
            return ""
        
        formatted_text = "\n\n**Example Step Planning:**\n"
        
        for i, example in enumerate(examples, 1):
            example_formatted = example.format_for_prompt()
            formatted_text += f"\n{i}. {example_formatted}"
        
        return formatted_text


@dataclass
class ClassifierExample(BaseExample):
    """Example for few-shot learning in classifiers.
    
    This class represents training examples used for few-shot learning in
    classification tasks. Each example contains a query, expected result,
    and reasoning to help the classifier learn decision patterns.
    
    :param query: Input query text to be classified
    :type query: str
    :param result: Expected boolean classification result
    :type result: bool
    :param reason: Explanation of why this classification is correct
    :type reason: str
    """
    query: str
    result: bool
    reason: str
    
    def format_for_prompt(self) -> str:
        """Format this classifier example for few-shot learning with complete context.
        
        This method transforms the classifier example into the standard format used
        for few-shot learning in classification tasks. It provides the complete
        query/result/reason triplet that enables LLM-based classifiers to learn
        effective decision patterns through example-based training.
        
        The formatting follows the established pattern for classifier training:
        - Query: The input text to be classified
        - Expected Output: The correct boolean classification result
        - Reason: The logical justification for the classification decision
        
        :return: Formatted string with query, expected result, and reasoning for few-shot learning
        :rtype: str
        
        .. note::
           The format is specifically optimized for LLM consumption in few-shot
           learning scenarios. The consistent structure enables reliable pattern
           recognition and classification performance.
        
        Examples:
            Formatted classifier example output::
            
                example = ClassifierExample(
                    query="What's the weather like?",
                    result=True,
                    reason="Direct weather information request"
                )
                formatted = example.format_for_prompt()
                # Returns: 'User Query: "What\'s the weather like?" -> Expected Output: True -> Reason: Direct weather information request'
        
        .. seealso::
           :func:`format_examples_for_prompt` : Batch formatting with bias prevention
        """
        return f'User Query: "{self.query}" -> Expected Output: {self.result} -> Reason: {self.reason}'
    
    @staticmethod
    def format_examples_for_prompt(examples: List['ClassifierExample']) -> str:
        """Format multiple classifier examples with randomization for bias-free few-shot learning.
        
        This method transforms a collection of ClassifierExample objects into a
        formatted string optimized for few-shot learning in classification tasks.
        It includes automatic randomization to prevent positional bias, ensuring
        that classifiers learn from content rather than example ordering patterns.
        
        The formatting implements bias prevention strategies:
        1. **Automatic Randomization**: Examples are shuffled to prevent position-based learning
        2. **Consistent Format**: Uniform query/result/reason structure for reliable learning
        3. **Complete Context**: Full reasoning provided for each classification decision
        4. **Optimal Presentation**: Format optimized for LLM few-shot learning performance
        
        :param examples: List of classifier examples to format with bias prevention
        :type examples: List[ClassifierExample]
        :return: Formatted string with randomized examples for reliable classification learning
        :rtype: str
        
        .. note::
           The randomization creates a shallow copy of the input list, leaving the
           original list unchanged. This ensures thread safety and prevents side
           effects in concurrent usage scenarios.
        
        .. warning::
           The randomization is applied each time this method is called. For
           deterministic behavior in testing, consider using a fixed seed or
           pre-shuffled examples.
        
        Example::
        
            examples = [example1, example2, example3]
            formatted = ClassifierExample.format_examples_for_prompt(examples)
            # Returns randomized examples like:
            # "  - User Query: \"...\" -> Expected Output: True -> Reason: ...\n"
        
        
        .. seealso::
           :func:`format_for_prompt` : Individual example formatting method
           :mod:`random` : Randomization implementation for bias prevention
        """
        # Create a copy and randomize to prevent bias
        randomized_examples = examples.copy()
        random.shuffle(randomized_examples)
        
        return "\n".join(f"  - {ex.format_for_prompt()}" for ex in randomized_examples)


class ClassifierActions(BaseModel):
    """Action specification for classifier match responses with extensible design.
    
    This Pydantic model defines actions that should be executed when a task
    classifier returns a positive match for a capability. It provides an
    extensible framework for defining automated responses to classification
    results, enabling sophisticated workflow automation based on task analysis.
    
    The ClassifierActions system enables:
    1. **Automated Workflows**: Define actions triggered by positive classifications
    2. **Response Coordination**: Specify how the system should respond to matches
    3. **Future Extensibility**: Placeholder for advanced action specifications
    4. **Integration Points**: Clear interfaces for action execution systems
    
    Currently serves as a foundational placeholder that can be extended with
    specific action types as the classification system evolves. Future implementations
    may include routing specifications, parameter configurations, or execution
    priority settings.
    
    .. note::
       This is currently a placeholder class designed for future extensibility.
       The structure provides a foundation for implementing sophisticated action
       systems based on classification results.
    
    .. seealso::
       :class:`TaskClassifierGuide` : Classification guidance using action specifications
       :class:`CapabilityMatch` : Classification results that trigger actions
    """
    pass


class TaskClassifierGuide(BaseModel):
    """Comprehensive guide for task classification with few-shot learning support.
    
    This Pydantic model provides complete guidance for task classification systems
    including classification instructions, training examples, and action specifications.
    It serves as the primary configuration mechanism for capability-specific
    classification that enables intelligent routing and task analysis throughout
    the framework.
    
    TaskClassifierGuide enables sophisticated classification by providing:
    1. **Classification Instructions**: Clear guidance on when to activate capabilities
    2. **Few-Shot Training**: Curated examples for reliable classification learning
    3. **Action Specification**: Automated responses to positive classifications
    4. **Bias Prevention**: Randomized example presentation to prevent positional bias
    5. **Framework Integration**: Seamless integration with classification infrastructure
    
    The guide system ensures consistent and accurate capability selection by
    providing LLM-based classifiers with comprehensive context and training
    examples. This enables reliable task routing and reduces classification
    errors that could lead to incorrect capability activation.
    
    :param instructions: Detailed classification instructions specifying when to activate
    :type instructions: str
    :param examples: Training examples for few-shot learning with query/result/reason triplets
    :type examples: List[ClassifierExample]
    :param actions_if_true: Action specifications for positive classification results
    :type actions_if_true: ClassifierActions
    
    .. note::
       The examples list is automatically randomized during prompt formatting to
       prevent positional bias in few-shot learning. This ensures more reliable
       classification performance.
    
    .. warning::
       Classification accuracy directly impacts system behavior through capability
       routing. Ensure instructions are clear and examples are representative to
       maintain reliable task classification.
    
    Examples:
        Weather capability classification guide::
        
            guide = TaskClassifierGuide(
                instructions="Activate when user requests weather information or forecasts",
                examples=[
                    ClassifierExample(
                        query="What's the weather like today?",
                        result=True,
                        reason="Direct weather information request"
                    ),
                    ClassifierExample(
                        query="Should I bring an umbrella?",
                        result=True,
                        reason="Weather-dependent decision requiring forecast"
                    ),
                    ClassifierExample(
                        query="What time is it?",
                        result=False,
                        reason="Time request, not weather-related"
                    )
                ]
            )
    
    .. seealso::
       :class:`ClassifierExample` : Individual training examples for few-shot learning
       :class:`ClassifierActions` : Action specifications for positive matches
       :mod:`framework.infrastructure.classifier` : Classification system integration
    """
    instructions: str
    examples: List[ClassifierExample] = Field(default_factory=list)
    actions_if_true: ClassifierActions = Field(default_factory=ClassifierActions)


class OrchestratorGuide(BaseModel):
    """Comprehensive orchestration guide with examples and priority-based ordering.
    
    This Pydantic model provides complete guidance for orchestration systems on
    how to effectively plan and execute capabilities. It includes detailed
    instructions, rich examples, and priority settings that enable sophisticated
    execution planning and capability coordination throughout the framework.
    
    OrchestratorGuide enables intelligent orchestration by providing:
    1. **Planning Instructions**: Clear guidance on when and how to use capabilities
    2. **Rich Examples**: Detailed execution step examples with context requirements
    3. **Priority Ordering**: Configurable priority for guide concatenation and selection
    4. **Context Specification**: Clear requirements for successful capability execution
    5. **Framework Integration**: Seamless integration with orchestration infrastructure
    
    The guide system ensures effective execution planning by providing orchestrators
    with comprehensive context about capability usage patterns, requirements, and
    best practices. This enables more accurate execution plan generation and
    reduces planning errors that could impact system performance.
    
    :param instructions: Detailed orchestration instructions for capability usage
    :type instructions: str
    :param examples: Rich examples demonstrating effective capability execution planning
    :type examples: List[OrchestratorExample]
    :param priority: Priority for guide ordering during concatenation (lower values first)
    :type priority: int
    
    .. note::
       Priority values control the order in which guides are presented when multiple
       capabilities provide orchestration guidance. Lower values appear first,
       allowing critical capabilities to provide primary guidance.
    
    .. warning::
       Orchestration guidance directly impacts execution plan quality. Ensure
       instructions are comprehensive and examples represent realistic usage
       patterns to maintain effective execution planning.
    
    Examples:
        Data analysis capability orchestration guide::
        
            guide = OrchestratorGuide(
                instructions="Use for statistical analysis of numerical data sets",
                examples=[
                    OrchestratorExample(
                        step=PlannedStep(
                            context_key="analysis_results",
                            capability="statistical_analysis",
                            task_objective="Analyze sensor data for trends and anomalies",
                            success_criteria="Statistical summary with trend analysis complete",
                            expected_output="ANALYSIS_RESULTS",
                            inputs=[{"SENSOR_DATA": "sensor_readings"}]
                        ),
                        scenario_description="When user requests data analysis or trend identification",
                        context_requirements={"SENSOR_DATA": "Numerical time series data"}
                    )
                ],
                priority=10
            )
    
    .. seealso::
       :class:`OrchestratorExample` : Rich examples for execution step planning
       :class:`PlannedStep` : Execution step structure and requirements
       :mod:`framework.infrastructure.orchestration` : Orchestration system integration
    """
    instructions: str
    examples: List[OrchestratorExample] = Field(default_factory=list)
    # Priority for orchestrator guide ordering
    priority: int = 0 