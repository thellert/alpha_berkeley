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
from configs.config import get_model_config
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
    
    # Simplified knowledge base focused on essential parameters for tutorial
    # Contains clean technical documents that LLM will extract numerical parameters from
    KNOWLEDGE_BASE = {
        "turbine_specifications": """
        WindMax 2500 Turbine Specifications
        
        Rated capacity: 2.5 MW per turbine
        Cut-in wind speed: 3 m/s  
        Cut-out wind speed: 25 m/s
        Optimal wind range: 12-18 m/s
        Rotor diameter: 112 meters
        Hub height: 95 meters
        """,
        
        "performance_benchmarks": """
        Industry Performance Standards
        
        Excellent performance: Above 85% capacity factor
        Good performance: 75-85% capacity factor  
        Maintenance required: Below 75% capacity factor
        Economic viability threshold: 70% capacity factor
        
        Typical fleet capacity factors: 25-35% annually
        Target operational uptime: 97%
        Performance consistency target: Low variability preferred
        """,
        
        "maintenance_thresholds": """
        Maintenance Decision Criteria
        
        Immediate intervention: Below 70% performance
        Scheduled maintenance: Below 75% performance
        Monitoring required: 75-85% performance  
        Excellent operation: Above 85% performance
        
        Annual maintenance costs: 2-3% of initial investment
        Fleet performance tracking: Monthly capacity factor analysis
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
            
            model_config = get_model_config("wind_turbine", "knowledge_retrieval")
            
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
            **EXTRACT ESSENTIAL PARAMETERS FOR TURBINE ANALYSIS**
            
            Extract these specific numerical parameters from the documentation for: {query}
            
            **AVAILABLE TECHNICAL DOCUMENTATION:**
            {knowledge_base_text}
            
            **REQUIRED PARAMETERS TO EXTRACT:**
            
            From specifications:
            - rated_capacity_mw (from "2.5 MW")
            - cut_in_wind_speed_ms (from "3 m/s")
            - cut_out_wind_speed_ms (from "25 m/s")
            - optimal_wind_min_ms (from "12-18 m/s" range)
            - optimal_wind_max_ms (from "12-18 m/s" range)
            
            From performance benchmarks:  
            - excellent_performance_threshold_percent (from "above 85%")
            - good_performance_min_percent (from "75-85%")
            - good_performance_max_percent (from "75-85%")
            - maintenance_threshold_percent (from "below 75%")
            - economic_threshold_percent (from "70%")
            
            From maintenance criteria:
            - immediate_intervention_threshold_percent (from "below 70%")
            - target_uptime_percent (from "97%")
            
            **EXTRACTION RULES:**
            - Extract only numerical values (no text descriptions)
            - Include units in parameter names for clarity
            - Use consistent naming convention with underscores
            - Convert percentages to decimal numbers (e.g., "85%" → 85.0)
            
            **OUTPUT FORMAT:**
            - knowledge_data: Flat dictionary with the extracted parameters
            - knowledge_source: "Wind Farm Knowledge Base" 
            - query_processed: "{query}"
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