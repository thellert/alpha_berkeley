Build Your First Production-Ready Agent  
========================================

Learn to build sophisticated, enterprise-grade agentic systems with the Alpha Berkeley Framework through a comprehensive wind turbine monitoring example that demonstrates professional patterns from basic data retrieval to advanced LLM planning.

Why This Guide?
---------------

Building an agentic system from scratch can seem overwhelming. This guide takes you step-by-step through creating a **real, working agent** that monitors wind turbines - from the basic data structures to intelligent multi-step execution planning.

You'll learn by doing, not just reading about concepts.

What You'll Build
-----------------

A production-ready wind turbine monitoring agent that demonstrates enterprise patterns:

* ** Smart Data Retrieval** - Professional API integration with error handling and retry logic
* ** Intelligent Analysis** - LLM-powered analysis planning with Python execution services
* ** Adaptive Insights** - Domain-specific knowledge extraction from technical documentation
* ** Advanced Planning** - Multi-phase analysis coordination with fallback strategies
* ** Knowledge Integration** - RAG-style knowledge providers with structured LLM extraction
* ** Human Oversight** - Approval workflows for sensitive operations and code execution
* ** Operational Excellence** - Comprehensive logging, monitoring, and error classification
* ** Performance Optimization** - Model-specific configurations and resource management

.. note::
   This example uses mock APIs for development. The patterns shown work with real services too.

**Example Query:**
.. code-block:: text

   "Our wind farm has been underperforming lately. Can you analyze the turbine 
   performance over the past 2 weeks, identify which turbines are operating 
   below industry standards, and rank them by efficiency? I need to know which 
   ones require immediate maintenance attention."

**What the agent does automatically:**
1. Parse "past 2 weeks" into exact datetime range
2. Retrieve historical turbine performance data (5 turbines: T-001 through T-005)
3. Fetch corresponding weather data (wind speed conditions)
4. Extract industry performance benchmarks from knowledge base
5. **Create LLM-powered analysis plan** with structured phases:
   - Data correlation (merge turbine + weather data by timestamp)
   - Performance metrics calculation (efficiency vs theoretical maximum)
   - Industry benchmark comparison (classify against standards)
6. **Generate and execute Python code** for statistical analysis
7. **Identify underperformers** and rank turbines by performance
8. **Apply knowledge base thresholds** to classify performance levels

The 5-Component Architecture
----------------------------

The wind turbine tutorial agent built with the Alpha Berkeley Framework has these components:

.. code-block:: text

   📁 src/applications/wind_turbine/
   ├── registry.py              # Component registration
   ├── context_classes.py       # Type-safe data structures
   ├── mock_apis.py             # Realistic API simulation
   ├── config.yml               # Production configuration
   ├── capabilities/            # Sophisticated agent skills
   │   ├── turbine_data_archiver.py    # Basic patterns
   │   ├── weather_data_retrieval.py   # API integration
   │   ├── knowledge_retrieval.py      # RAG patterns
   │   └── turbine_analysis.py         # Advanced planning
   └── data_sources/            # LLM-enhanced knowledge providers
       └── knowledge_provider.py       # Production RAG system

Let's build each component step by step.

Step 1: Define Your Data Types
-------------------------------

First, create the data structures your agent will work with. These are type-safe containers that the framework uses to pass data between capabilities.

**File:** ``src/applications/wind_turbine/context_classes.py``

.. code-block:: python

   """
   Context classes define the data structures your agent works with.
   They're automatically type-checked and provide rich descriptions for the LLM.
   """
   
   from typing import Dict, Any, Optional, List, ClassVar
   from datetime import datetime
   from framework.context.base import CapabilityContext
   from pydantic import Field

   class TurbineDataContext(CapabilityContext):
       """Historical turbine performance data."""
       CONTEXT_TYPE: ClassVar[str] = "TURBINE_DATA"
       CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
       
       timestamps: List[datetime] = Field(description="List of timestamps for data points")
       turbine_ids: List[str] = Field(description="List of turbine IDs")
       power_outputs: List[float] = Field(description="List of power outputs in MW")
       time_range: str = Field(description="Human-readable time range description")
       total_records: int = Field(description="Total number of data records")
       
       def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Rich description for LLM consumption."""
           key_ref = key_name if key_name else "key_name"
           
           return {
               "data_points": self.total_records,
               "time_coverage": self.time_range,
               "turbine_count": len(set(self.turbine_ids)) if self.turbine_ids else 0,
               "data_structure": "Three parallel lists: timestamps, turbine_ids, power_outputs",
               "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.timestamps, context.{self.CONTEXT_TYPE}.{key_ref}.turbine_ids, context.{self.CONTEXT_TYPE}.{key_ref}.power_outputs",
               "example_usage": f"pd.DataFrame({{'timestamp': context.{self.CONTEXT_TYPE}.{key_ref}.timestamps, 'turbine_id': context.{self.CONTEXT_TYPE}.{key_ref}.turbine_ids, 'power_output': context.{self.CONTEXT_TYPE}.{key_ref}.power_outputs}})",
               "available_fields": ["timestamps", "turbine_ids", "power_outputs", "time_range", "total_records"]
           }
       
       def get_human_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Human-readable summary for UI/debugging."""
           unique_turbines = list(set(self.turbine_ids)) if self.turbine_ids else []
           avg_power = sum(self.power_outputs) / len(self.power_outputs) if self.power_outputs else 0
           
           return {
               "type": "Turbine Performance Data",
               "total_records": self.total_records,
               "time_range": self.time_range,
               "turbine_count": len(unique_turbines),
               "turbine_ids": unique_turbines[:5],  # Show first 5
               "average_power_output": f"{avg_power:.2f} MW" if avg_power else "N/A",
               "data_span": f"{self.timestamps[0]} to {self.timestamps[-1]}" if self.timestamps else "No data"
           }

   class WeatherDataContext(CapabilityContext):
       """Weather conditions data for turbine analysis."""
       CONTEXT_TYPE: ClassVar[str] = "WEATHER_DATA"
       CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
       
       timestamps: List[datetime] = Field(description="List of timestamps for weather data")
       wind_speeds: List[float] = Field(description="List of wind speeds in m/s")
       time_range: str = Field(description="Human-readable time range description")
       
       def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Rich description for LLM consumption."""
           key_ref = key_name if key_name else "key_name"
           
           avg_wind_speed = sum(self.wind_speeds) / len(self.wind_speeds) if self.wind_speeds else 0
           max_wind_speed = max(self.wind_speeds) if self.wind_speeds else 0
           min_wind_speed = min(self.wind_speeds) if self.wind_speeds else 0
           
           return {
               "data_points": len(self.timestamps),
               "time_coverage": self.time_range,
               "wind_speed_stats": {
                   "average": f"{avg_wind_speed:.2f} m/s",
                   "max": f"{max_wind_speed:.2f} m/s",
                   "min": f"{min_wind_speed:.2f} m/s"
               },
               "data_structure": "Two parallel lists: timestamps and wind_speeds",
               "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.timestamps, context.{self.CONTEXT_TYPE}.{key_ref}.wind_speeds",
               "example_usage": f"pd.DataFrame({{'timestamp': context.{self.CONTEXT_TYPE}.{key_ref}.timestamps, 'wind_speed': context.{self.CONTEXT_TYPE}.{key_ref}.wind_speeds}})",
               "available_fields": ["timestamps", "wind_speeds", "time_range"]
           }
       
       def get_human_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Human-readable summary for UI/debugging."""
           avg_wind_speed = sum(self.wind_speeds) / len(self.wind_speeds) if self.wind_speeds else 0
           max_wind_speed = max(self.wind_speeds) if self.wind_speeds else 0
           
           return {
               "type": "Weather Data",
               "data_points": len(self.timestamps),
               "time_range": self.time_range,
               "average_wind_speed": f"{avg_wind_speed:.2f} m/s",
               "max_wind_speed": f"{max_wind_speed:.2f} m/s",
               "data_span": f"{self.timestamps[0]} to {self.timestamps[-1]}" if self.timestamps else "No data"
           }

   class AnalysisResultsContext(CapabilityContext):
       """Performance analysis and baseline calculations."""
       CONTEXT_TYPE: ClassVar[str] = "ANALYSIS_RESULTS"
       CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"

       results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results container")
       expected_schema: Optional[Dict[str, Any]] = Field(default=None, description="Expected results structure")
       
       def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Rich description for LLM consumption."""
           key_ref = key_name if key_name else "key_name"
           return {
               "available_fields": list(self.results.keys()),
               "schema": self.expected_schema,
               "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.results['field_name']",
               "format": "All analysis results are in the .results dictionary - access them directly",
               "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.results['baseline_power'] for baseline power values"
           }
       
       def get_human_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Human-readable summary for UI/debugging."""
           # Extract all dynamic fields for user display
           user_data = {}
           for field_name, value in self.results.items():
               # Convert large data structures to summaries
               if isinstance(value, list) and len(value) > 10:
                   user_data[field_name] = f"List with {len(value)} items: {value[:3]}..."
               elif isinstance(value, dict) and len(value) > 10:
                   keys = list(value.keys())[:3]
                   user_data[field_name] = f"Dict with {len(value)} keys: {keys}..."
               else:
                   user_data[field_name] = value
           
           return {
               "type": "Turbine Analysis Results",
               "results": user_data,
               "field_count": len(user_data),
               "available_fields": list(user_data.keys())
           }

   class TurbineKnowledgeContext(CapabilityContext):
       """Knowledge base retrieval results for wind farm domain expertise."""
       CONTEXT_TYPE: ClassVar[str] = "TURBINE_KNOWLEDGE"
       CONTEXT_CATEGORY: ClassVar[str] = "KNOWLEDGE_DATA"
       
       knowledge_data: Dict[str, Any] = Field(default_factory=dict, description="Retrieved knowledge as flat dictionary")
       knowledge_source: str = Field(default="Wind Farm Knowledge Base", description="Source of the retrieved knowledge")
       query_processed: str = Field(default="", description="The query that was processed to extract this knowledge")
       
       def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Rich description for LLM consumption - guides Python code generation for data access."""
           key_ref = key_name if key_name else "key_name"
           
           # Get the actual field names that can be accessed in Python code
           available_data_fields = list(self.knowledge_data.keys()) if self.knowledge_data else []
           
           return {
               "knowledge_source": self.knowledge_source,
               "query_context": self.query_processed,
               "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.knowledge_data['field_name']",
               "available_fields": available_data_fields,
               "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.knowledge_data['{available_data_fields[0]}']" if available_data_fields else f"context.{self.CONTEXT_TYPE}.{key_ref}.knowledge_data['field_name']",
           }
       
       def get_human_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
           """Human-readable summary for UI/debugging."""
           # Return the entire knowledge_data for response generation use
           return {
               "type": "Wind Farm Knowledge",
               "source": self.knowledge_source,
               "query_processed": self.query_processed,
               "knowledge_data": self.knowledge_data,
           }

.. tip::
   **Why context classes matter:** They provide type safety, automatic validation, and help the LLM understand your data structure. The `get_access_details` method teaches the LLM exactly how to use your data in Python code generation. Separate lists make DataFrame creation easier.

Step 2: Create Mock Services
-----------------------------

Mock APIs let you develop and test your agent without real external services. They simulate realistic behavior and data patterns.

**File:** ``src/applications/wind_turbine/mock_apis.py``

.. code-block:: python

   """
   Mock APIs simulate real external services for development.
   They generate realistic data patterns for testing.
   """
   
   import random
   import math
   from typing import List, Dict
   from datetime import datetime
   from pydantic import BaseModel

   def get_wind_speed(timestamp: datetime) -> float:
       """Generate predictable wind speed pattern for tutorial purposes."""
       # Create a completely predictable pattern for tutorial clarity
       # Use consistent good wind conditions (12-15 m/s) to focus on turbine differences
       base_wind = 13.5  # Optimal wind speed for clear performance analysis
       # Very gentle daily cycle (±1.5 m/s) to keep within optimal range
       daily_variation = 1.5 * math.sin(timestamp.timestamp() / 86400 * 2 * math.pi)
       return max(12.0, min(15.0, base_wind + daily_variation))  # Keep in 12-15 m/s range

   class TurbineReading(BaseModel):
       """Type-safe model for turbine sensor readings."""
       turbine_id: str
       timestamp: datetime
       power_output: float  # MW

   class WeatherReading(BaseModel):
       """Type-safe model for weather data."""
       timestamp: datetime
       wind_speed: float  # m/s

   class TurbineSensorAPI:
       """Mock API for turbine sensor data with realistic patterns."""
       
       def __init__(self):
           self.turbine_ids = ["T-001", "T-002", "T-003", "T-004", "T-005"]
           # Each turbine has different efficiency characteristics for performance benchmarking
           self.turbine_efficiency_factors = {
               "T-001": 0.95,   # Excellent performer (95% of theoretical) 
               "T-002": 0.80,   # Good performer (80% of theoretical)
               "T-003": 0.60,   # Poor performer (60% of theoretical) - needs maintenance
               "T-004": 0.88,   # Very good performer (88% of theoretical)
               "T-005": 0.65    # Below average performer (65% of theoretical) - maintenance candidate
           }
           # Minimal noise factors for predictable tutorial results
           self.turbine_noise_factors = {
               "T-001": 0.02,   # Very stable
               "T-002": 0.02,   # Stable
               "T-003": 0.03,   # Slightly variable (compounds poor performance)
               "T-004": 0.02,   # Very stable
               "T-005": 0.03    # Slightly variable
           }
       
       async def get_historical_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
           """Get historical turbine data for time range."""
           readings = []
           time_delta = (end_time - start_time) / 100
           
           for i in range(100):
               timestamp = start_time + (time_delta * i)
               base_wind = get_wind_speed(timestamp)
               
               for turbine_id in self.turbine_ids:
                   # Calculate theoretical power output based on wind speed
                   # Simplified power curve: starts at 3 m/s, max at 2.5MW
                   theoretical_power = min(2.5, max(0, (base_wind - 3) * 0.20))
                   
                   # Apply turbine-specific efficiency factor
                   efficiency_factor = self.turbine_efficiency_factors[turbine_id]
                   base_power = theoretical_power * efficiency_factor
                   
                   # Add realistic noise variation  
                   noise_factor = self.turbine_noise_factors[turbine_id]
                   power_noise = random.uniform(-noise_factor, noise_factor) * base_power
                   final_power = max(0, base_power + power_noise)
                   
                   readings.append({
                       "turbine_id": turbine_id,
                       "timestamp": timestamp,
                       "power_output": round(final_power, 2)
                   })
           
           return readings

   class WeatherAPI:
       """Mock weather service for wind conditions."""
       
       async def get_weather_history(self, start_time: datetime, end_time: datetime) -> List[Dict]:
           """Get historical weather data for time range."""
           readings = []
           time_delta = (end_time - start_time) / 100
           
           for i in range(100):
               timestamp = start_time + (time_delta * i)
               readings.append({
                   "timestamp": timestamp,
                   "wind_speed": round(get_wind_speed(timestamp), 1)
               })
           
           return readings

   # Global instances  
   turbine_api = TurbineSensorAPI()
   weather_api = WeatherAPI()

.. tip::
   **Mock APIs are powerful:** They let you test complex scenarios, simulate edge cases, and develop without external dependencies. The patterns shown here work with real APIs too.

Step 3: Add a Professional Knowledge Source
--------------------------------------------

Modern agentic systems need domain expertise. Let's build a production-ready knowledge provider that demonstrates LLM-enhanced RAG patterns used in enterprise systems.

**File:** ``src/applications/wind_turbine/data_sources/knowledge_provider.py``

.. code-block:: python

   """
   Wind Farm Knowledge Provider
   
   Production-ready RAG-style knowledge base that uses LLM to extract structured
   technical parameters from domain documentation. Demonstrates enterprise
   knowledge retrieval patterns with error handling and structured outputs.
   """
   
   import logging
   import textwrap
   from typing import Dict, Any, Optional
   from pydantic import BaseModel, Field
   
   from framework.data_management import DataSourceProvider, DataSourceContext
   from framework.data_management.request import DataSourceRequest
   from framework.models.completion import get_chat_completion
   from configs.unified_config import get_model_config
   from applications.wind_turbine.context_classes import TurbineKnowledgeContext

   logger = logging.getLogger(__name__)

   class KnowledgeRetrievalResult(BaseModel):
       """Structured output model for LLM knowledge extraction."""
       
       knowledge_data: Dict[str, Any] = Field(
           default_factory=dict,
           description="Extracted numerical parameters and thresholds"
       )
       knowledge_source: str = Field(
           default="Wind Farm Knowledge Base",
           description="Source of the retrieved knowledge"
       )
       query_processed: str = Field(
           default="",
           description="The query that was processed"
       )

   class WindFarmKnowledgeProvider(DataSourceProvider):
       """Production-ready knowledge provider with LLM-enhanced extraction."""
       
       # Enterprise knowledge base - realistic technical documentation
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
           capacity factor, while industry average ranges from 25-35%. The economic 
           viability threshold is generally considered to be 70% efficiency.
           """
       }
       
       @property
       def name(self) -> str:
           return "wind_farm_knowledge"
       
       @property 
       def context_type(self) -> str:
           return "TURBINE_KNOWLEDGE"
       
       def should_respond(self, request: DataSourceRequest) -> bool:
           """Only respond to capability execution requests, not task extraction."""
           return request.requester.component_type != "task_extraction"
       
       async def retrieve_data(self, request: DataSourceRequest) -> Optional[DataSourceContext]:
           """Retrieve domain knowledge using LLM-enhanced query processing."""
           
           try:
               query = request.query or f"Retrieve wind turbine knowledge for {request.requester.component_name}"
               logger.info(f"Knowledge retrieval requested for: '{query}'")
               
               # Create structured LLM prompt with knowledge base
               retrieval_prompt = self._create_knowledge_retrieval_prompt(query)
               
               # Use application-specific model configuration
               model_config = get_model_config("wind_turbine", "knowledge_retrieval")
               
               # LLM-enhanced knowledge extraction
               knowledge_result = get_chat_completion(
                   message=retrieval_prompt,
                   model_config=model_config,
                   output_model=KnowledgeRetrievalResult
               )
               
               # Create structured context
               knowledge_context = TurbineKnowledgeContext(
                   knowledge_data=knowledge_result.knowledge_data,
                   knowledge_source=knowledge_result.knowledge_source,
                   query_processed=knowledge_result.query_processed
               )
               
               logger.info(f"Successfully extracted {len(knowledge_result.knowledge_data)} parameters")
               
               return DataSourceContext(
                   source_name=self.name,
                   context_type=self.context_type,
                   data=knowledge_context,
                   metadata={
                       "query": query,
                       "llm_processed": True,
                       "extracted_fields": list(knowledge_result.knowledge_data.keys())
                   },
                   provider=self
               )
               
           except Exception as e:
               logger.error(f"Knowledge retrieval failed: {e}")
               return None
       
       def _create_knowledge_retrieval_prompt(self, query: str) -> str:
           """Create structured LLM prompt for numerical parameter extraction."""
           
           knowledge_sections = []
           for section_name, section_data in self.KNOWLEDGE_BASE.items():
               knowledge_sections.append(f"**{section_name.replace('_', ' ').title()}:**")
               knowledge_sections.append(section_data.strip())
               knowledge_sections.append("")
           
           knowledge_base_text = "\n".join(knowledge_sections)
           
           return textwrap.dedent(f"""
               **TECHNICAL PARAMETER EXTRACTION**
               
               Extract relevant numerical parameters and thresholds for: {query}
               
               **AVAILABLE TECHNICAL DOCUMENTATION:**
               {knowledge_base_text}
               
               **EXTRACTION REQUIREMENTS:**
               1. Focus on numerical values, thresholds, and measurable specifications
               2. Convert all values to clean numerical format for Python analysis
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
               
               **FOCUS:** Extract only actionable numerical parameters for quantitative analysis.
               """).strip()

.. tip::
   **Production Knowledge Providers:** This demonstrates enterprise RAG patterns with LLM-enhanced extraction, structured outputs, proper error handling, and metadata tracking. The pattern works with any domain - replace the knowledge base with your technical documentation.

Step 4: Build Your First Capability
------------------------------------

Capabilities are your agent's skills. Each capability uses the LangGraph-native architecture with these key components:

1. **@capability_node decorator** - Integrates with LangGraph execution
2. **execute() method** - The main business logic (static method)
3. **Classifier guide** - Teaches the LLM when to use this capability  
4. **Orchestrator guide** - Teaches the LLM how to plan with this capability

Let's build a capability that retrieves historical turbine data:

**File:** ``src/applications/wind_turbine/capabilities/turbine_data_archiver.py``

.. code-block:: python

   """
   Turbine Data Archiver Capability
   
   This capability retrieves historical turbine performance data.
   It shows the complete pattern for building capabilities.
   """
   
   import logging
   import textwrap
   from typing import Dict, Any, Optional
   
   from framework.base.decorators import capability_node
   from framework.base.capability import BaseCapability
   from framework.base.errors import ErrorClassification, ErrorSeverity
   from framework.base.examples import OrchestratorGuide, OrchestratorExample, ClassifierActions, ClassifierExample, TaskClassifierGuide
   from framework.base.planning import PlannedStep
   from framework.state import AgentState, StateManager
   from framework.registry import get_registry
   from framework.context.context_manager import ContextManager
   
   from applications.wind_turbine.context_classes import TurbineDataContext
   from applications.wind_turbine.mock_apis import turbine_api
   from configs.streaming import get_streamer
   from configs.logger import get_logger

   logger = get_logger("wind_turbine", "turbine_data_archiver")
   registry = get_registry()

   # === PROFESSIONAL ERROR HANDLING ===
   class TurbineDataError(Exception):
       """Base class for turbine data related errors."""
       pass

   class TurbineDataRetrievalError(TurbineDataError):
       """Raised when turbine data retrieval fails."""
       pass

   class MissingTimeRangeError(TurbineDataError):
       """Raised when required time range context is missing."""
       pass

   # === THE CAPABILITY CLASS ===
   @capability_node
   class TurbineDataArchiverCapability(BaseCapability):
       """LangGraph-native turbine data archiver capability."""
       
       # Required class attributes for registry configuration
       name = "turbine_data_archiver"
       description = "Retrieve historical turbine performance data from sensor archives"
       provides = ["TURBINE_DATA"]
       requires = ["TIME_RANGE"]
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           """Retrieve historical turbine data for the specified time range."""
           
           # Extract current step from execution plan
           step = StateManager.get_current_step(state)
           
           # Define streaming helper here for step awareness
           streamer = get_streamer("wind_turbine", "turbine_data_archiver", state)
           streamer.status("Retrieving historical turbine data...")
           
           # Extract required TIME_RANGE context using ContextManager
           try:
               context_manager = ContextManager(state)
               contexts = context_manager.extract_from_step(
                   step, state,
                   constraints=["TIME_RANGE"],
                   constraint_mode="hard"
               )
               time_range_input = contexts[registry.context_types.TIME_RANGE]
           except ValueError as e:
               raise MissingTimeRangeError(str(e))
           
           # Validate time range context
           if not hasattr(time_range_input, 'start_date') or not hasattr(time_range_input, 'end_date'):
               raise MissingTimeRangeError(f"{registry.context_types.TIME_RANGE} context missing required start_date/end_date attributes")
           
           logger.debug(f"Retrieving turbine data from {time_range_input.start_date} to {time_range_input.end_date}")
           
           try:
               # Use the mock API to get historical data
               turbine_readings = await turbine_api.get_historical_data(
                   start_time=time_range_input.start_date,
                   end_time=time_range_input.end_date
               )
               
               # Convert to separate lists (makes subsequent pd-dataframe conversion easier)
               timestamps = [reading["timestamp"] for reading in turbine_readings]
               turbine_ids = [reading["turbine_id"] for reading in turbine_readings]
               power_outputs = [reading["power_output"] for reading in turbine_readings]
               
               # Create turbine data context
               turbine_data = TurbineDataContext(
                   timestamps=timestamps,
                   turbine_ids=turbine_ids,
                   power_outputs=power_outputs,
                   time_range=f"{time_range_input.start_date} to {time_range_input.end_date}",
                   total_records=len(turbine_readings)
               )
               
               logger.info(f"Retrieved {len(turbine_readings)} turbine readings for time range")
               
               # Streaming completion
               streamer.status("Turbine data retrieved")
               
               # Store context using StateManager
               return StateManager.store_context(
                   state, 
                   registry.context_types.TURBINE_DATA, 
                   step.get("context_key"), 
                   turbine_data
               )
               
           except Exception as e:
               logger.error(f"Failed to retrieve turbine data: {e}")
               raise TurbineDataRetrievalError(f"Failed to retrieve turbine data: {str(e)}")
       
       @staticmethod
       def classify_error(exc: Exception, context: dict) -> ErrorClassification:
           """Professional error classification with domain-specific handling."""
           
           # Handle custom domain exceptions
           if isinstance(exc, MissingTimeRangeError):
               return ErrorClassification(
                   severity=ErrorSeverity.CRITICAL,
                   user_message="Time range not properly configured for turbine data retrieval",
                   technical_details=str(exc)
               )
           
           if isinstance(exc, TurbineDataRetrievalError):
               return ErrorClassification(
                   severity=ErrorSeverity.RETRIABLE,
                   user_message="Turbine sensors temporarily unavailable, retrying...",
                   technical_details=str(exc)
               )
           
           # Handle network/infrastructure errors as retriable
           if isinstance(exc, (ConnectionError, TimeoutError)):
               return ErrorClassification(
                   severity=ErrorSeverity.RETRIABLE,
                   user_message="Turbine data service timeout, retrying...",
                   technical_details=str(exc)
               )
           
           # Default to CRITICAL for unknown errors
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message=f"Turbine data retrieval error: {str(exc)}",
               technical_details=f"Error type: {type(exc).__name__}, Details: {str(exc)}"
           )
       
       def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
           """Teaches the LLM when to use this capability."""
           return TaskClassifierGuide(
               instructions="Determine if the task requires historical turbine performance data retrieval.",
               examples=[
                   ClassifierExample(
                       query="Show turbine performance for the past 3 days", 
                       result=True, 
                       reason="Request requires historical turbine performance data."
                   ),
                   ClassifierExample(
                       query="What is the current wind speed?", 
                       result=False, 
                       reason="Request is for current weather data, not turbine performance history."
                   ),
                   ClassifierExample(
                       query="Analyze recent turbine trends", 
                       result=True, 
                       reason="Analysis requires historical turbine data for trends."
                   )
               ],
               actions_if_true=ClassifierActions()
           )
       
       def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
           """Teaches the LLM how to plan with this capability."""
           registry = get_registry()
           
           example = OrchestratorExample(
               step=PlannedStep(
                   context_key="historical_turbine_data",
                   capability="turbine_data_archiver",
                   task_objective="Retrieve historical turbine performance data for analysis",
                   expected_output=registry.context_types.TURBINE_DATA,
                   success_criteria="Historical turbine performance data retrieved",
                   inputs=[{registry.context_types.TIME_RANGE: "past_3_days_timerange"}]
               ),
               scenario_description="Retrieving historical turbine performance data for analysis"
           )
           
           return OrchestratorGuide(
               instructions=textwrap.dedent(f"""
                   **When to plan "turbine_data_archiver" steps:**
                   - Tasks requiring historical turbine performance data
                   - Baseline calculations and trend analysis
                   - Investigating performance issues over time

                   **Required Dependencies:**
                   - {registry.context_types.TIME_RANGE}: Time range for data retrieval

                   **Output: {registry.context_types.TURBINE_DATA}**
                   - Contains turbine_readings with power_output, rpm, timestamps
                   - Provides data for downstream analysis capabilities
                   """),
               examples=[example],
               order=10
           )

.. tip::
   **LangGraph-Native Pattern:** Every capability uses the @capability_node decorator with BaseCapability. The execute() method contains your business logic, while classifier and orchestrator guides teach the LLM when and how to use your capabilities. Use ContextManager for input validation and get_streamer for status updates.

Step 4B: Advanced Analysis Capability (Production Patterns)
------------------------------------------------------------

The basic turbine data archiver shows fundamental patterns. Now let's examine a sophisticated capability that demonstrates enterprise-level features: **LLM-powered planning**, **Python execution services**, and **human approval workflows**.

**File:** ``src/applications/wind_turbine/capabilities/turbine_analysis.py`` (Key Patterns)

.. code-block:: python

   """
   Advanced Turbine Analysis Capability
   
   Demonstrates production-ready patterns: LLM planning, Python execution integration,
   approval workflows, and multi-phase analysis coordination.
   """
   
   import textwrap
   from typing import Dict, Any, List
   from pydantic import BaseModel, Field
   
   from framework.base.decorators import capability_node
   from framework.base.capability import BaseCapability
   from framework.services.python_executor.models import PythonExecutionRequest
   from framework.approval import (
       create_approval_type,
       get_approval_resume_data,
       handle_service_with_interrupts
   )
   from framework.models import get_chat_completion
   from framework.state import AgentState, StateManager
   from framework.context.context_manager import ContextManager
   from framework.registry import get_registry
   from applications.wind_turbine.context_classes import AnalysisResultsContext
   from configs.unified_config import get_model_config
   from configs.streaming import get_streamer
   from configs.logger import get_logger
   from langgraph.types import Command

   logger = get_logger("wind_turbine", "turbine_analysis")
   registry = get_registry()

   # === ANALYSIS PLANNING MODELS ===
   
   class AnalysisPhase(BaseModel):
       """Individual phase in the multi-step analysis plan."""
       phase: str = Field(description="Name of the analytical phase")
       subtasks: List[str] = Field(description="Specific computational tasks")
       output_state: str = Field(description="What this phase produces")

   class AnalysisPlan(BaseModel):
       """Complete analysis plan with structured phases."""
       phases: List[AnalysisPhase] = Field(description="Ordered list of analysis phases")

   # === LLM-POWERED PLANNING ===
   
   async def create_turbine_analysis_plan(task_objective: str, state: AgentState) -> List[AnalysisPhase]:
       """Use LLM to create hierarchical analysis plan for complex turbine analysis."""
       
       system_prompt = textwrap.dedent(f"""
           You are an expert in wind turbine performance analysis.
           Create a structured analysis plan for: "{task_objective}"
           
           DOMAIN KNOWLEDGE - CRITICAL CONCEPTS:
           - Wind turbine efficiency should be calculated relative to available wind conditions
           - True efficiency compares actual performance to theoretical maximum given wind resource
           - Industry benchmarks classify turbines by actual vs expected performance
           
           ANALYSIS CONSTRAINTS:
           - Focus on computational/analytical aspects only
           - Must correlate turbine data with weather data by timestamp
           - Must use knowledge base thresholds for performance classification
           - Create exactly 3-4 phases maximum for manageable Python code generation
           
           Structure each phase with:
           - phase: Name of the major analytical phase
           - subtasks: List of 2-3 specific computational tasks
           - output_state: What this phase accomplishes
           
           REQUIRED PHASES (adapt to specific task):
           1. Data Preparation and Correlation
           2. Performance Metrics Calculation  
           3. Industry Benchmark Comparison
           """)

       try:
           model_config = get_model_config("wind_turbine", "turbine_analysis")
           
           response_data = await get_chat_completion(
               model_config=model_config,
               message=f"{system_prompt}\n\nCreate the analysis plan.",
               output_model=AnalysisPlan,
           )
           
           return response_data.phases
           
       except Exception as e:
           logger.error(f"Failed to generate analysis plan: {e}")
           # Fallback to default structured plan
           return [
               AnalysisPhase(
                   phase="Data Preparation and Correlation",
                   subtasks=[
                       "Merge turbine power data with weather data by timestamp",
                       "Calculate theoretical power for each wind speed condition"
                   ],
                   output_state="Correlated turbine and weather dataset"
               ),
               AnalysisPhase(
                   phase="Performance Metrics Calculation",
                   subtasks=[
                       "Calculate actual vs theoretical efficiency for each turbine",
                       "Compute capacity factors relative to rated capacity"
                   ],
                   output_state="Efficiency metrics and capacity factors"
               ),
               AnalysisPhase(
                   phase="Industry Benchmark Comparison",
                   subtasks=[
                       "Apply knowledge base thresholds for performance classification",
                       "Rank turbines by performance metrics"
                   ],
                   output_state="Performance classifications and rankings"
               )
           ]

   @capability_node  
   class TurbineAnalysisCapability(BaseCapability):
       """Production-ready analysis capability with advanced patterns."""
       
       name = "turbine_analysis"
       description = "Analyze wind turbine performance against industry benchmarks"
       provides = [registry.context_types.ANALYSIS_RESULTS]
       requires = [registry.context_types.TURBINE_DATA, registry.context_types.WEATHER_DATA, registry.context_types.TURBINE_KNOWLEDGE]
       
       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           """Execute sophisticated turbine analysis with planning and Python execution."""
           
           step = StateManager.get_current_step(state)
           streamer = get_streamer("wind_turbine", "turbine_analysis", state)
           
           # Get Python executor service from registry
           python_service = registry.get_service("python_executor")
           if not python_service:
               raise RuntimeError("Python executor service not available")
           
           # =====================================================
           # PHASE 1: CHECK FOR APPROVED CODE EXECUTION
           # =====================================================
           
           # Check if resuming from human approval
           has_approval_resume, approved_payload = get_approval_resume_data(
               state, 
               create_approval_type("turbine_analysis")
           )
           
           if has_approval_resume:
               if approved_payload:
                   logger.success("Executing approved analysis code")
                   streamer.status("Executing approved code...")
                   resume_response = {"approved": True, **approved_payload}
               else:
                   logger.info("Analysis was rejected by user")
                   resume_response = {"approved": False}
               
               # Create service configuration
               service_config = {
                   "configurable": {
                       "thread_id": f"python_service_{step.get('context_key', 'default')}",
                       "checkpoint_ns": "python_executor"
                   }
               }
               
               # Resume with approval decision
               service_result = await python_service.ainvoke(
                   Command(resume=resume_response),
                   config=service_config
               )
           else:
               # =====================================================
               # PHASE 2: STRUCTURED ANALYSIS FLOW
               # =====================================================
               
               # Extract and validate required contexts
               context_manager = ContextManager(state)
               contexts = context_manager.extract_from_step(
                   step, state,
                   constraints=["TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE"],
                   constraint_mode="hard"
               )
               
               turbine_data = contexts[registry.context_types.TURBINE_DATA]
               weather_data = contexts[registry.context_types.WEATHER_DATA]
               knowledge_data = contexts[registry.context_types.TURBINE_KNOWLEDGE]
               
               # STEP 1: Create LLM-powered analysis plan
               streamer.status("Creating analysis plan...")
               task_objective = step.get("task_objective", "")
               
               analysis_plan = await create_turbine_analysis_plan(task_objective, state)
               logger.info(f"Generated plan with {len(analysis_plan)} phases")
               
               # STEP 2: Create structured prompts from plan
               context_description = context_manager.get_context_access_description(step.get('inputs', []))
               capability_prompts = [
                   f"ANALYSIS PLAN: {len(analysis_plan)} phases planned",
                   f"AVAILABLE DATA: {context_description}",
                   "Generate Python code following the structured analysis plan phases"
               ]
               
               # STEP 3: Execute with Python service and approval handling
               expected_results = {"turbine_metrics": {}, "performance_analysis": {}, "summary": {}}
               
               execution_request = PythonExecutionRequest(
                   user_query=state.get("input_output", {}).get("user_query", ""),
                   task_objective=task_objective,
                   expected_results=expected_results,
                   capability_prompts=capability_prompts,
                   execution_folder_name="turbine_analysis",
                   capability_context_data=state.get('capability_context_data', {}),
                   retries=3
               )
               
               streamer.status("Generating and executing Python code...")
               
               # Use centralized approval handling
               service_result = await handle_service_with_interrupts(
                   service=python_service,
                   request=execution_request,
                   config=service_config,
                   logger=logger,
                   capability_name="TurbineAnalysis"
               )
           
           # =====================================================
           # CONVERGENCE: Process results from either path
           # =====================================================
           
           # Create structured analysis context
           analysis_context = AnalysisResultsContext(
               results=service_result.results,
               expected_schema=execution_request.expected_results if not has_approval_resume else None
           )
           
           logger.success("Turbine analysis completed successfully")
           streamer.status("Analysis complete")
           
           # Store results
           return StateManager.store_context(
               state, 
               registry.context_types.ANALYSIS_RESULTS, 
               step.get("context_key"), 
               analysis_context
           )

.. tip::
   **Advanced Patterns Demonstrated:**
   
   - **LLM Planning**: Dynamic analysis plan generation based on task requirements
   - **Python Execution**: Integration with secure Python execution services  
   - **Approval Workflows**: Human oversight for sensitive operations
   - **Structured Prompts**: Converting analysis plans into executable Python code
   - **Error Recovery**: Fallback plans when LLM planning fails
   - **State Management**: Handling complex approval/resume flows

Step 5: Register Your Components
--------------------------------

The registry tells the framework about all your components. This is where everything comes together.

**File:** ``src/applications/wind_turbine/registry.py``

.. code-block:: python

   """
   Wind Turbine Application Registry Configuration.
   
   This module defines the component registry for the Wind Turbine Monitoring application.
   All wind turbine-specific capabilities, context classes, and data sources are declared here.
   """
   
   from framework.registry import (
       CapabilityRegistration, 
       ContextClassRegistration,
       DataSourceRegistration,
       RegistryConfig,
       RegistryConfigProvider
   )

   class WindTurbineRegistryProvider(RegistryConfigProvider):
       """Registry provider for Wind Turbine application."""
       
       def get_registry_config(self) -> RegistryConfig:
           """Get wind turbine application registry configuration."""
           return RegistryConfig(
               core_nodes=[],  # Applications don't define core nodes
               
               # Exclude framework components that conflict with specialized implementations
               framework_exclusions={
                   "capabilities": ["python"]  # Use specialized turbine_analysis instead
               },
               
               capabilities=[
                   CapabilityRegistration(
                       name="weather_data_retrieval",
                       module_path="applications.wind_turbine.capabilities.weather_data_retrieval",
                       class_name="WeatherDataRetrievalCapability", 
                       description="Retrieve weather data for wind analysis",
                       provides=["WEATHER_DATA"],
                       requires=["TIME_RANGE"]
                   ),
                   CapabilityRegistration(
                       name="knowledge_retrieval",
                       module_path="applications.wind_turbine.capabilities.knowledge_retrieval",
                       class_name="KnowledgeRetrievalCapability",
                       description="Retrieve technical standards and performance benchmarks from knowledge base",
                       provides=["TURBINE_KNOWLEDGE"],
                       requires=[]
                   ),
                   CapabilityRegistration(
                       name="turbine_data_archiver",
                       module_path="applications.wind_turbine.capabilities.turbine_data_archiver",
                       class_name="TurbineDataArchiverCapability",
                       description="Retrieve historical turbine performance data",
                       provides=["TURBINE_DATA"],
                       requires=["TIME_RANGE"]
                   ),
                   CapabilityRegistration(
                       name="turbine_analysis",
                       module_path="applications.wind_turbine.capabilities.turbine_analysis",
                       class_name="TurbineAnalysisCapability",
                       description="Analyze turbine performance against industry benchmarks",
                       provides=["ANALYSIS_RESULTS"],
                       requires=["TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE"]
                   )
               ],
               
               context_classes=[
                   ContextClassRegistration(
                       context_type="TURBINE_DATA",
                       module_path="applications.wind_turbine.context_classes", 
                       class_name="TurbineDataContext"
                   ),
                   ContextClassRegistration(
                       context_type="WEATHER_DATA",
                       module_path="applications.wind_turbine.context_classes",
                       class_name="WeatherDataContext"
                   ),
                   ContextClassRegistration(
                       context_type="ANALYSIS_RESULTS",
                       module_path="applications.wind_turbine.context_classes",
                       class_name="AnalysisResultsContext"
                   ),
                   ContextClassRegistration(
                       context_type="TURBINE_KNOWLEDGE",
                       module_path="applications.wind_turbine.context_classes",
                       class_name="TurbineKnowledgeContext"
                   ),
               ],
               
               data_sources=[
                   DataSourceRegistration(
                       name="wind_farm_knowledge",
                       module_path="applications.wind_turbine.data_sources.knowledge_provider",
                       class_name="WindFarmKnowledgeProvider",
                       description="Mock RAG-style knowledge base for wind farm domain expertise"
                   )
               ],
               
               framework_prompt_providers=[],
               
               initialization_order=[
                   "context_classes",
                   "data_sources", 
                   "capabilities",
                   "framework_prompt_providers"
               ]
           )

Step 6: Professional Configuration Management
---------------------------------------------

Configuration files enable fine-tuned control over model behavior, performance optimization, and operational parameters for production deployments.

**File:** ``src/applications/wind_turbine/config.yml``

.. code-block:: yaml

   # Wind Turbine Monitoring Application Configuration
   # Professional configuration with detailed explanations

   # === APPLICATION-SPECIFIC MODEL CONFIGURATIONS ===
   # Different capabilities need different model parameters for optimal performance
   models:
     # Complex analysis requiring detailed reasoning and Python code generation
     turbine_analysis:
       provider: cborg                    # Cloud provider for enterprise models
       model_id: anthropic/claude-sonnet  # High-reasoning model for complex analysis
       max_tokens: 8192                   # Large context for multi-phase analysis plans
       temperature: 0.1                   # Low temperature for consistent technical output
       
     # Knowledge extraction requiring structured output
     knowledge_retrieval:
       provider: cborg
       model_id: anthropic/claude-sonnet
       max_tokens: 2048                   # Smaller context for focused knowledge extraction
       temperature: 0.0                   # Deterministic for consistent parameter extraction

   # === PIPELINE CONFIGURATION ===
   # Application identity and operational parameters
   pipeline:
     name: "Wind Turbine Monitor"
     description: "Advanced wind turbine performance monitoring and analysis system"
     version: "1.0.0"
     
   # === OPERATIONAL LOGGING ===
   # Color-coded logging for operational visibility and debugging
   logging:
     level: "INFO"                        # Production logging level
     logging_colors:
       # Wind turbine capability color coding for operational monitoring
       time_range_parsing: "light_blue"   # Time/date processing operations
       weather_data_retrieval: "cyan"     # External weather service calls
       turbine_data_archiver: "green"     # Historical data retrieval operations
       turbine_analysis: "yellow"         # Complex analysis and Python execution
       knowledge_retrieval: "magenta"     # Knowledge base operations
       
   # === PERFORMANCE TUNING ===
   # Production performance and reliability settings
   performance:
     max_concurrent_requests: 5           # Limit concurrent LLM calls for cost control
     request_timeout_seconds: 120         # Timeout for complex analysis operations
     retry_attempts: 3                    # Automatic retry for transient failures
     
   # === SECURITY AND COMPLIANCE ===
   # Production security settings
   security:
     enable_code_review: true             # Require human approval for Python execution
     allowed_packages: ["pandas", "numpy", "matplotlib", "seaborn"]  # Restrict Python packages
     max_execution_time: 300              # Limit Python execution time (seconds)

.. tip::
   **Production Configuration Patterns:**
   
   - **Model Specialization**: Different capabilities use different model configurations optimized for their specific tasks
   - **Operational Visibility**: Color-coded logging enables rapid debugging in production
   - **Performance Controls**: Concurrency limits and timeouts prevent resource exhaustion
   - **Security Boundaries**: Code review requirements and package restrictions ensure safe operation
   - **Cost Management**: Token limits and retry controls manage LLM usage costs

See It In Action
----------------

Once you've built these components, your agent can handle complex requests automatically:

**User Request:**
.. code-block:: text

   "Analyze turbine performance over the past week and identify which turbines 
   need maintenance based on efficiency drops."

**Automatic Execution Plan:**
1. **Parse time range** → "past week" becomes specific dates
2. **Retrieve knowledge** → Industry benchmarks and technical standards (85% excellent, 75% good, <75% maintenance)
3. **Fetch turbine data** → Historical performance records (T-001 through T-005)
4. **Fetch weather data** → Wind conditions for correlation (12-15 m/s optimal range)
5. **Create analysis plan** → LLM generates structured 3-phase analysis approach
6. **Execute Python analysis** → Statistical calculations with approval workflow
7. **Generate insights** → Performance classifications and maintenance rankings

**Example Results:**
.. code-block:: text

   📊 **Wind Farm Performance Analysis Results**
   
   **Turbine Rankings (by efficiency):**
   1. T-001: 94.2% efficiency → Excellent performer ✅
   2. T-004: 87.1% efficiency → Very good performer ✅  
   3. T-002: 79.3% efficiency → Good performer ⚠️
   4. T-005: 64.8% efficiency → Below average → **Maintenance recommended** 🔧
   5. T-003: 59.1% efficiency → Poor performer → **Immediate maintenance required** 🚨
   
   **Farm Average:** 76.9% efficiency
   **Industry Benchmark:** 75% maintenance threshold
   **Maintenance Priority:** T-003, T-005

The framework coordinates all these steps automatically, handling dependencies, error recovery, data flow between capabilities, and even human approval for Python code execution.

Production Deployment Patterns
------------------------------

The wind turbine agent demonstrates enterprise-ready patterns for production deployment. Here are the key architectural decisions that make it production-grade:

**🔐 Security and Compliance**

.. code-block:: python

   # Human approval for sensitive operations
   from framework.approval import handle_service_with_interrupts
   
   # Code execution requires explicit approval
   service_result = await handle_service_with_interrupts(
       service=python_service,
       request=execution_request,
       config=service_config,
       logger=logger,
       capability_name="TurbineAnalysis"
   )

**📊 Operational Monitoring**

.. code-block:: python

   # Structured logging with operational context
   logger = get_logger("wind_turbine", "turbine_analysis")
   streamer = get_streamer("wind_turbine", "turbine_analysis", state)
   
   # Real-time status updates
   streamer.status("Creating analysis plan...")
   streamer.status("Generating and executing Python code...")
   streamer.status("Analysis complete")

**⚡ Performance Optimization**

.. code-block:: python

   # Model-specific configurations for optimal performance
   model_config = get_model_config("wind_turbine", "turbine_analysis")
   
   # Structured error recovery with domain-specific handling
   if isinstance(exc, MissingTimeRangeError):
       return ErrorClassification(severity=ErrorSeverity.CRITICAL, ...)
   elif isinstance(exc, TurbineDataRetrievalError):
       return ErrorClassification(severity=ErrorSeverity.RETRIABLE, ...)

**🔄 State Management**

.. code-block:: python

   # Robust approval/resume flow handling
   has_approval_resume, approved_payload = get_approval_resume_data(state, approval_type)
   
   if has_approval_resume:
       # Resume from approval decision
       service_result = await python_service.ainvoke(Command(resume=response))
   else:
       # Normal execution flow
       service_result = await handle_service_with_interrupts(...)

What's Next?
------------

Now that you understand both basic and advanced patterns, you can build production-ready agentic systems:

**🔧 Extend Capabilities:**
- **Real-time Monitoring**: Add streaming data capabilities with WebSocket integration
- **Predictive Maintenance**: Implement ML models using the Python execution service
- **Automated Actions**: Build control capabilities with approval workflows
- **Multi-Source Integration**: Connect multiple data sources (SCADA, historians, APIs)

**🧠 Advanced Intelligence Patterns:**
- **Dynamic Planning**: Use LLM-powered workflow generation for complex scenarios
- **Learning Systems**: Implement feedback loops using the memory storage service
- **Domain Expertise**: Expand knowledge bases with vector storage and semantic search
- **Contextual Reasoning**: Build capabilities that adapt behavior based on operational context

**🔗 Enterprise Integration:**
- **Authentication**: Integrate with enterprise identity providers (LDAP, SAML)
- **Monitoring**: Connect to enterprise monitoring (Grafana, Datadog, Splunk)
- **Data Sources**: Replace mock APIs with real enterprise systems
- **Compliance**: Add audit trails and regulatory compliance features

**📊 Scaling Patterns:**
- **Multi-tenant**: Extend for multiple wind farms with tenant isolation
- **High Availability**: Implement redundancy and failover strategies
- **Performance**: Add caching layers and request optimization
- **Cost Control**: Implement LLM usage monitoring and budget controls

**🚀 Advanced Architectures:**
- **Microservices**: Split capabilities into independent deployable services
- **Event-Driven**: Build reactive systems using the framework's event capabilities
- **Multi-Agent**: Coordinate multiple specialized agents for complex operations
- **Edge Computing**: Deploy lightweight agents at turbine locations

.. tip::
   **Production Success Patterns:**
   
   - **Start with Domain Expertise**: Your knowledge providers are the foundation of intelligent behavior
   - **Design for Operations**: Include logging, monitoring, and debugging from day one
   - **Build in Security**: Use approval workflows for sensitive operations and validate all inputs
   - **Plan for Scale**: Design context classes and capabilities with performance in mind
   - **Implement Gradually**: Use the progressive complexity approach - basic → advanced → production

**Framework Advantages in Production:**

The Alpha Berkeley Framework provides enterprise-grade foundations:

- **LangGraph Integration**: Native support for complex, stateful workflows
- **Type Safety**: Pydantic-based context classes prevent runtime errors
- **Error Recovery**: Sophisticated error classification and retry mechanisms
- **Human Oversight**: Built-in approval systems for sensitive operations
- **Operational Visibility**: Comprehensive logging and real-time status updates
- **Service Integration**: Seamless integration with Python execution, memory, and data services

The patterns you've learned work across domains - financial analysis, IoT monitoring, scientific research, manufacturing optimization. The key is understanding your data structures, building domain expertise through knowledge providers, and creating capabilities that demonstrate intelligent coordination.

Ready to build your production agentic system? Start with your domain's context classes and knowledge sources, then progressively add capabilities that demonstrate the sophisticated patterns shown here. The framework provides the enterprise infrastructure - you provide the domain intelligence!
