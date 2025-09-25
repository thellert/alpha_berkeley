import os
import asyncio # Added for asyncio.gather
import opentelemetry.trace # Added for setting attributes on the current span

# langfuse ##########################
from applications.als_assistant.utils import configure_langfuse
tracer = configure_langfuse()
# langfuse ##########################


from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass, field
from pydantic_graph import BaseNode, End, Graph, GraphRunContext
from pydantic_ai import Agent, RunContext, Tool, ModelRetry
from pydantic import BaseModel, Field
from configs.config import get_model_config
from framework.models import get_chat_completion, get_model
from configs.config import get_model_config

# Import necessary functions from util.py
from applications.als_assistant.services.pv_finder.util import format_pv_results_for_span

# Import local modules
from .tools import list_systems, list_families, list_common_names, inspect_fields, get_field_data, list_channel_names, get_AT_index
from .core import (
    QuerySplitterOutput,
    KeywordExtractorOutput,
    PVQueryOutput, 
    PVSearchResult,
    QueryAgentDeps,
    PVFinderGraphState
)
from .prompts import (
    get_query_splitter_prompt,
    get_keyword_extractor_prompt,
    get_pv_query_prompt
)

# Load unified configuration
langfuse_enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

# Use global logger
from configs.logger import get_logger
from applications.als_assistant.services.pv_finder.util import initialize_nltk_resources
logger = get_logger("als_assistant", "pv_finder")


# --- Direct Chat Completion Functions ---

async def _get_query_splitter_response(query: str) -> QuerySplitterOutput:
    """Split query using structured LLM generation."""
    query_splitter_config = get_model_config("als_assistant", "pv_finder", "query_splitter")
    
    response = await asyncio.to_thread(
        get_chat_completion,
        message=f"{get_query_splitter_prompt()}\n\nQuery to process: {query}",
        model_config=query_splitter_config,
        output_model=QuerySplitterOutput
    )
    return response

async def _get_keyword_extractor_response(query: str) -> KeywordExtractorOutput:
    """Extract keywords using structured LLM generation."""
    keyword_extractor_config = get_model_config("als_assistant", "pv_finder", "keyword")
    
    response = await asyncio.to_thread(
        get_chat_completion,
        message=f"{get_keyword_extractor_prompt()}\n\nQuery to process: {query}",
        model_config=keyword_extractor_config,
        output_model=KeywordExtractorOutput
    )
    return response

pv_query_config = get_model_config("als_assistant", "pv_finder", "pv_query")
retries = pv_query_config.get("retries", 3)  # Default to 3 retries if not configured
pv_query_agent = Agent(
    name="[Agent]: PV Query",
    model=get_model(model_config=pv_query_config),
    tools=[
        Tool(list_systems, takes_ctx=False, max_retries=retries),
        Tool(list_families, takes_ctx=False, max_retries=retries),
        Tool(inspect_fields, takes_ctx=False, max_retries=retries),
        Tool(get_field_data, takes_ctx=False, max_retries=retries),
        Tool(list_channel_names, takes_ctx=False, max_retries=retries),
        Tool(list_common_names, takes_ctx=False, max_retries=retries),
        Tool(get_AT_index, takes_ctx=False, max_retries=retries),
    ],
    deps_type=QueryAgentDeps,
    output_type=PVQueryOutput,
    retries=retries,
    instrument=langfuse_enabled,
)

# --- Dynamic System Prompts ---
@pv_query_agent.system_prompt
async def get_dynamic_system_prompt(ctx: RunContext[QueryAgentDeps]) -> str:
    # Ensure keywords and systems are lists, even if None
    keywords = ctx.deps.keywords if ctx.deps.keywords is not None else []
    systems = ctx.deps.systems if ctx.deps.systems is not None else []

    logger.debug(f"Systems: {', '.join(systems) if systems else 'none'}")
    logger.debug(f"Keywords: {', '.join(keywords) if keywords else 'none'}")
    
    # Use the new prompt builder with dynamic examples
    system_prompt = get_pv_query_prompt(
        keywords=keywords,
        systems=systems,
        max_examples=20
    )
    
    return system_prompt



@pv_query_agent.output_validator
async def validate_pv_query(ctx: RunContext[QueryAgentDeps], result: PVQueryOutput) -> PVQueryOutput:
    """Validate PV query output"""
    if result.pvs is None:
        raise ModelRetry("The 'pvs' field is required and must be a list (can be empty if no PVs found).")
    if not isinstance(result.pvs, list):
        raise ModelRetry(f"The 'pvs' field must be a list, got {type(result.pvs).__name__}: {result.pvs}")
    if not result.description:
        raise ModelRetry("The 'description' field is required. Please provide a description of the results.")
    if not isinstance(result.description, str):
        raise ModelRetry(f"The 'description' field must be a string, got {type(result.description).__name__}: {result.description}")
    return result

# --- Agent Graph Nodes ---
@dataclass
class QuerySplittingNode(BaseNode[PVFinderGraphState]):
    @classmethod
    def get_node_id(cls):
        return f"[NODE]: Query Splitting"
    async def run(self, ctx: GraphRunContext[PVFinderGraphState]) -> "ParallelQueryProcessingNode":
        span = opentelemetry.trace.get_current_span()
        span.set_attribute("input", ctx.state.initial_query)

        # --- MAIN LOGIC ---
        result = await _get_query_splitter_response(ctx.state.initial_query)
        ctx.state.split_queries = result.queries
        
        logger.key_info(f"Split queries: {ctx.state.split_queries}")
        span.set_attribute("output", ctx.state.split_queries)
        return ParallelQueryProcessingNode()

@dataclass
class ParallelQueryProcessingNode(BaseNode[PVFinderGraphState]):
    @classmethod
    def get_node_id(cls):
        return f"[NODE]: Query Processing"
    
    async def _process_query_unit_async(self, query_string: str) -> PVQueryOutput:
        
        keyword_result = await _get_keyword_extractor_response(
            f"Extract keywords and relevant system components from the following query: {query_string}"
        )
        
        extracted_keywords = keyword_result.keywords if keyword_result.keywords is not None else []
        extracted_systems = keyword_result.systems if keyword_result.systems is not None else []

        logger.debug(f"For query '{query_string}', extracted keywords: {extracted_keywords}, systems: {extracted_systems}")

        current_query_agent_deps = QueryAgentDeps(
            initial_query=query_string,
            keywords=extracted_keywords,
            systems=extracted_systems,
        )
        
        pv_result = await pv_query_agent.run(
            query_string,
            deps=current_query_agent_deps
        )
        
        pvs = pv_result.output.pvs 
        description = pv_result.output.description
                
        return PVQueryOutput(
            pvs=pvs, 
            description=description
        )

    async def run(self, ctx: GraphRunContext[PVFinderGraphState]) -> "AggregationAndFinalResponseNode":
        # Get the current OpenTelemetry span
        span = opentelemetry.trace.get_current_span()
        span.set_attribute("input", ctx.state.split_queries)

        # --- MAIN LOGIC ---
        tasks = [
            self._process_query_unit_async(q_str)
            for q_str in ctx.state.split_queries
        ]
        results = await asyncio.gather(*tasks)
        ctx.state.pv_results = results
        
        # Logging
        logger.key_info(f"Parallel processing completed for {len(ctx.state.pv_results)} queries")
        span.set_attribute("output", format_pv_results_for_span(ctx.state.pv_results))

        return AggregationAndFinalResponseNode()

@dataclass
class AggregationAndFinalResponseNode(BaseNode[PVFinderGraphState]):
    async def run(self, ctx: GraphRunContext[PVFinderGraphState]) -> End[PVSearchResult]:
        span = opentelemetry.trace.get_current_span()
        span.set_attribute("input", format_pv_results_for_span(ctx.state.pv_results))

        unique_final_pvs: List[str] = []
        final_description_parts: List[str] = []
        seen_pvs = set()

        if ctx.state.pv_results:
            for result_item in ctx.state.pv_results:
                if result_item.pvs:
                    for pv in result_item.pvs:
                        # Strip trailing whitespace from PV names
                        cleaned_pv = pv.strip() if isinstance(pv, str) else pv
                        if cleaned_pv not in seen_pvs:
                            unique_final_pvs.append(cleaned_pv)
                            seen_pvs.add(cleaned_pv)
                if result_item.description: 
                    final_description_parts.append(result_item.description)
        
        final_description = "\n\n".join(final_description_parts)
        
        response = PVSearchResult(pvs=unique_final_pvs, description=final_description)
        
        logger.success(f"Final aggregated response: Found {response.pvs} PVs")
        span.set_attribute("output", response.pvs if response.pvs else response.description)
        return End(response)


# --- Workflow Definition and Execution ---
pv_finder_graph = Graph(
    name="[Graph]: PV Finder",
    nodes=(
        QuerySplittingNode, 
        ParallelQueryProcessingNode, 
        AggregationAndFinalResponseNode
        ),
    state_type=PVFinderGraphState
)

async def run_pv_finder_graph(user_query: str) -> PVSearchResult:
    """
    Use this tool when you need a PV address.

    Args:
        query: The user's query about the ALS control system
        
    Returns:
        The response from the PV finder that includes the PV address
    """
    
    with tracer.start_as_current_span("PV Finder", attributes={"input": user_query}) as span:
        
        initial_state = PVFinderGraphState(initial_query=user_query)
        graph_run_result = await pv_finder_graph.run(
            QuerySplittingNode(),
            state=initial_state
        ) 
        final_response_obj = graph_run_result.output
        
        span.set_attribute("output", final_response_obj.pvs if final_response_obj.pvs else final_response_obj.description)
        
        return final_response_obj


# Example Usage (can be used for testing during development)
async def _example_usage():
    """Example function for testing during development."""
    initialize_nltk_resources()
    test_query = "What is the beam current PV?"
    
    try:
        final_result = await run_pv_finder_graph(test_query)
        logger.success(f"Example result: Found {len(final_result.pvs)} PVs")
        logger.info(f"Description: {final_result.description}")
        return final_result
    except Exception as e:
        logger.error(f"Error running PV finder graph: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # The global logger already configures Rich logging
    asyncio.run(_example_usage())
