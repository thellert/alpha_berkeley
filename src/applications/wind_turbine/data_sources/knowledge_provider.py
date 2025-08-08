"""
Wind Farm Knowledge Provider

Mock RAG-style knowledge base that uses LLM to retrieve domain-specific information
for wind turbine analysis. Simulates enterprise knowledge retrieval systems.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import textwrap

from framework.data_management import DataSourceProvider, DataSourceContext
from framework.data_management.request import DataSourceRequest
from framework.models.completion import get_chat_completion
from configs.unified_config import get_model_config
from applications.wind_turbine.context_classes import TurbineKnowledgeContext

logger = logging.getLogger(__name__)


class KnowledgeRetrievalResult(BaseModel):
    """LLM output model for knowledge extraction - matches TurbineKnowledgeContext structure."""
    
    knowledge_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Whatever knowledge the LLM extracted and structured from the knowledge base"
    )
    knowledge_source: str = Field(
        default="Wind Farm Knowledge Base",
        description="Source of the retrieved knowledge"
    )
    query_processed: str = Field(
        default="",
        description="The query that was processed to extract this knowledge"
    )


class WindFarmKnowledgeProvider(DataSourceProvider):
    """
    Mock RAG-style knowledge provider for wind farm domain expertise.
    
    Simulates enterprise knowledge retrieval by combining a static knowledge base
    with LLM-enhanced query processing to extract relevant domain information.
    """
    
    # Raw knowledge base - simulates enterprise technical documentation
    # Contains realistic technical documents that LLM will extract parameters from
    KNOWLEDGE_BASE = {
        "turbine_technical_specifications": """
        WindMax 2500 Turbine Technical Specifications
        
        Our wind farm operates WindMax 2500 turbines with a rated capacity of 2.5 MW each.
        The turbines have an optimal operating range between 12-18 m/s wind speeds, with
        cut-in at 3 m/s and cut-out at 25 m/s for safety. The theoretical maximum power
        coefficient for this turbine design is 0.47, representing peak efficiency under
        ideal conditions.
        
        Rotor diameter: 112 meters
        Hub height: 95 meters
        Design life: 20 years
        """,
        
        "performance_standards_guide": """
        Wind Turbine Performance Standards and Benchmarks
        
        Industry performance standards for 2.5MW turbines indicate that excellent 
        performers achieve efficiency ratings above 85% of their theoretical maximum 
        output under given wind conditions. Good performers typically maintain 
        75-85% efficiency, while turbines operating below 75% efficiency require 
        maintenance intervention.
        
        For capacity factor analysis, top-tier turbines achieve over 35% annual 
        capacity factor, while industry average ranges from 25-35%. Turbines with 
        capacity factors below 25% indicate potential mechanical issues or 
        suboptimal placement.
        
        The economic viability threshold is generally considered to be 70% efficiency - 
        turbines performing below this level are typically not cost-effective to operate 
        without immediate maintenance.
        """,
        
        "maintenance_protocols": """
        Maintenance and Performance Monitoring Guidelines
        
        Scheduled maintenance should prioritize turbines showing sustained efficiency 
        below 75% or capacity factors under 25%. Historical data shows that turbines 
        operating consistently below 70% efficiency require immediate intervention 
        to remain economically viable.
        
        Performance monitoring should track:
        - Daily efficiency relative to wind conditions
        - Monthly capacity factor calculations  
        - Comparative performance against peer turbines
        - Degradation trends over time
        
        Maintenance costs typically represent 2-3% of initial investment annually for 
        turbines operating within normal parameters.
        """,
        
        "operational_guidelines": """
        Wind Farm Operational Best Practices
        
        Optimal turbine performance occurs when wind speeds are consistently within 
        the 12-18 m/s range. Performance degrades significantly outside this range, 
        with efficiency dropping below 60% when winds are consistently under 8 m/s 
        or over 22 m/s.
        
        Turbine availability should target 97% uptime for economic viability. 
        Seasonal performance variations of 15-25% are considered normal due to 
        changing wind patterns throughout the year.
        """
    }
    
    @property
    def name(self) -> str:
        """Unique identifier for this data source provider."""
        return "wind_farm_knowledge"
    
    @property 
    def context_type(self) -> str:
        """Context type this provider creates."""
        return "TURBINE_KNOWLEDGE"
    
    def should_respond(self, request: DataSourceRequest) -> bool:
        """
        Determine if this knowledge provider should respond to the request.
        
        Only responds to capability execution requests, not task extraction.
        This prevents unnecessary LLM calls during task understanding phase.
        """
        if request.requester.component_type == "task_extraction":
            return False
        return True
    
    async def retrieve_data(self, request: DataSourceRequest) -> Optional[DataSourceContext]:
        """
        Retrieve domain knowledge using LLM-enhanced query processing.
        
        Simulates RAG by combining static knowledge base with specific query
        and using LLM to extract and format relevant knowledge.
        
        Args:
            request: Data source request containing query and metadata
            
        Returns:
            DataSourceContext with structured knowledge data, or None if failed
        """
        try:
            query = request.query or f"Retrieve wind turbine knowledge for {request.requester.component_name} capability"
            
            logger.info(f"Knowledge retrieval requested for query: '{query}'")
            
            retrieval_prompt = self._create_knowledge_retrieval_prompt(query)
            
            model_config = get_model_config("wind_turbine", "weather_analysis")
            
            logger.debug("Invoking LLM for knowledge retrieval...")
            
            knowledge_result = get_chat_completion(
                message=retrieval_prompt,
                model_config=model_config,
                output_model=KnowledgeRetrievalResult
            )
            
            knowledge_context = TurbineKnowledgeContext(
                knowledge_data=knowledge_result.knowledge_data,
                knowledge_source=knowledge_result.knowledge_source,
                query_processed=knowledge_result.query_processed
            )
            
            logger.info(f"Successfully retrieved knowledge with {len(knowledge_result.knowledge_data)} fields from LLM")
            
            return DataSourceContext(
                source_name=self.name,
                context_type=self.context_type,
                data=knowledge_context,
                metadata={
                    "query": query,
                    "knowledge_areas": list(self.KNOWLEDGE_BASE.keys()),
                    "llm_processed": True,
                    "extracted_fields": list(knowledge_result.knowledge_data.keys())
                },
                provider=self
            )
            
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            return None
    

    
    def _create_knowledge_retrieval_prompt(self, query: str) -> str:
        """Create LLM prompt for knowledge retrieval."""

        knowledge_sections = []
        for section_name, section_data in self.KNOWLEDGE_BASE.items():
            knowledge_sections.append(f"**{section_name.replace('_', ' ').title()}:**")
            knowledge_sections.append(self._format_knowledge_section(section_data))
            knowledge_sections.append("")
        
        knowledge_base_text = "\n".join(knowledge_sections)
        
        return textwrap.dedent(f"""
            **TECHNICAL PARAMETER EXTRACTION**
            
            Extract relevant numerical parameters and thresholds from technical documentation for: {query}
            
            **AVAILABLE TECHNICAL DOCUMENTATION:**
            {knowledge_base_text}
            
            **EXTRACTION REQUIREMENTS:**
            1. Focus on numerical values, thresholds, and measurable specifications
            2. Convert all values to clean numerical format suitable for Python analysis
            3. Use descriptive keys that include units for clarity
            
            **OUTPUT FORMAT:**
            - knowledge_data: Flat dictionary with numerical parameters only
            - knowledge_source: "Wind Farm Knowledge Base" 
            - query_processed: "{query}"
            
            **NUMERICAL EXTRACTION GUIDELINES:**
            - Extract percentages as numbers (e.g., "above 85%" → "excellent_efficiency_percent": 85.0)
            - Extract thresholds (e.g., "below 75%" → "maintenance_threshold_percent": 75.0)  
            - Extract capacities with units (e.g., "2.5 MW" → "rated_capacity_mw": 2.5)
            - Extract ranges as min/max (e.g., "12-18 m/s" → "optimal_wind_min_ms": 12.0, "optimal_wind_max_ms": 18.0)
            - Use descriptive keys that indicate measurement type and units
            
            **FOCUS:** Extract only actionable numerical parameters that can be used in quantitative analysis.
            """).strip()
    
    def _format_knowledge_section(self, knowledge_section: str) -> str:
        """Format a knowledge base section for inclusion in the LLM prompt."""
        # Knowledge sections are now plain text documents
        return knowledge_section.strip()
    
    def format_for_prompt(self, context: DataSourceContext) -> str:
        """
        Format knowledge context for inclusion in LLM prompts.
        
        This method controls how the retrieved knowledge appears when used
        by other capabilities (like performance analysis).
        """
        if not context or not context.data:
            return "**Wind Farm Knowledge:** (No knowledge available)"
        
        knowledge_data = context.data
        if not isinstance(knowledge_data, TurbineKnowledgeContext):
            return f"**Wind Farm Knowledge:** {str(knowledge_data)}"
        
        # Format whatever knowledge the LLM extracted
        formatted_sections = ["**Wind Farm Knowledge Base (LLM Extracted):**"]
        
        # The knowledge_data.knowledge_data contains whatever the LLM decided to extract
        if hasattr(knowledge_data, 'knowledge_data') and knowledge_data.knowledge_data:
            for key, value in knowledge_data.knowledge_data.items():
                if isinstance(value, dict):
                    formatted_sections.append(f"**{key.replace('_', ' ').title()}:**")
                    for sub_key, sub_value in value.items():
                        formatted_sections.append(f"  - {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    formatted_sections.append(f"**{key.replace('_', ' ').title()}:** {', '.join(map(str, value))}")
                else:
                    formatted_sections.append(f"**{key.replace('_', ' ').title()}:** {value}")
        
        formatted_sections.append(f"**Source:** {knowledge_data.knowledge_source}")
        
        return "\n".join(formatted_sections)