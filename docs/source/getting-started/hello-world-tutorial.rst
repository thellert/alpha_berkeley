===============================
Hello World Tutorial
===============================

This tutorial uses a very basic weather agent to demonstrate the complete framework workflow with minimal complexity. 

What You'll Build
=================

A "Hello World Weather" agent is a simple agent that:

* Responds to natural language weather queries
* These queries uses a mock API for realistic weather data.
* By this we demonstrate the complete capability → context → response flow
* Shows framework integration patterns

.. admonition:: What You'll Learn
   
   By the end of this guide, you'll have a working agent that responds to queries like "What's the weather in Prague?" with temperature and conditions data.

Prerequisites
=============

* Alpha Berkeley framework installed and running, otherwise follow the :doc:`installation guide <installation>` in the documentation.


Step 1: Explore the Project Structure
-------------------------------------

You can find the complete implementation of the hello_world_weather application (`browse on GitHub <https://github.com/thellert/alpha_berkeley/tree/main/src/applications/hello_world_weather>`_) in the following directory structure:

.. code-block::

   src/applications/hello_world_weather/
   ├── __init__.py
   ├── config.yml
   ├── mock_weather_api.py
   ├── context_classes.py
   ├── registry.py
   └── capabilities/
       ├── __init__.py
       └── current_weather.py

This tutorial will walk you through understanding how each component works and how they integrate together to create a complete AI agent application.

Step 2: The Mock Data Source
----------------------------

The ``mock_weather_api.py`` file provides a deterministic weather data provider that eliminates external API dependencies while demonstrating the framework's capability integration patterns.

.. code-block:: python

   """
   Simple Mock Weather API
   """

   import random
   from datetime import datetime
   from dataclasses import dataclass

   @dataclass
   class CurrentWeatherReading:
       """Simple weather data model."""
       location: str
       temperature: float
       conditions: str
       timestamp: datetime

   class SimpleWeatherAPI:
       """
       Mock weather API, returns basic weather data for 3 cities (San Francisco, New York, Prague).
       """
       
       def get_current_weather(self, location: str) -> CurrentWeatherReading:
           """Get simple current weather for a location."""
           # Implementation details below...

.. dropdown:: Complete Mock API Implementation
   
   Full implementation of the mock weather service (`view mock API on GitHub <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/hello_world_weather/mock_weather_api.py>`_)

   .. code-block:: python

      """
      Very simple mock weather API for quick setup.
      Returns basic weather data for 3 cities (San Francisco, New York, Prague).

      The weather API returns only the type safe data model for the current weather reading.
      """
      import random
      from datetime import datetime
      from dataclasses import dataclass

      @dataclass
      class CurrentWeatherReading:
          """Simple weather data model."""
          location: str
          temperature: float  # Celsius
          conditions: str
          timestamp: datetime

      class SimpleWeatherAPI:
          """
          Very simple mock weather API for quick setup.
          Returns basic weather data for 3 cities (San Francisco, New York, Prague).

          The weather API returns only the type safe data model for the current weather reading.
          """
          
          # Simple city data with basic temperature ranges
          CITY_DATA = {
              "San Francisco": {"base_temp": 18, "conditions": ["Sunny", "Foggy", "Partly Cloudy"]},
              "New York": {"base_temp": 15, "conditions": ["Sunny", "Rainy", "Cloudy", "Snow"]},
              "Prague": {"base_temp": 12, "conditions": ["Rainy", "Cloudy", "Partly Cloudy"]}
          }
          
          def get_current_weather(self, location: str) -> CurrentWeatherReading:
              """Get simple current weather for a location."""
              
              # Normalize location name
              location = location.title()
              if location not in self.CITY_DATA:
                  # Default to San Francisco if city not found
                  location = "San Francisco"
              
              city_info = self.CITY_DATA[location]
              
              # Simple random weather generation
              temperature = city_info["base_temp"] + random.randint(-5, 8)
              conditions = random.choice(city_info["conditions"])
              
              return CurrentWeatherReading(
                  location=location,
                  temperature=float(temperature),
                  conditions=conditions,
                  timestamp=datetime.now()
              )

      # Global API instance
      weather_api = SimpleWeatherAPI()

Step 3: Define the Context Class
---------------------------------

Context classes provide structured data storage and enable seamless integration between your agent's capabilities. Define a context class file (we'll call it ``context_classes.py``) to specify how weather information is stored and accessed throughout the framework.

.. admonition:: Requirements

   All context classes must inherit from ``CapabilityContext`` and implement the following required methods:

**Class Structure:**

.. code-block:: python

    class CurrentWeatherContext(CapabilityContext):
        """Context for current weather conditions."""
        
        # Context type and category identifiers
        CONTEXT_TYPE: ClassVar[str] = "CURRENT_WEATHER"
        CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
        
        # Your data fields (must be json serializable)
        location: str = Field(description="Location name")
        temperature: float = Field(description="Temperature in Celsius")
        conditions: str = Field(description="Weather conditions")
        timestamp: datetime = Field(description="When data was retrieved")

**Required Method 1: get_access_details()**

Provides structured access information for LLM consumption. This method is used when LLMs need to write Python code to access this context type:

.. code-block:: python

        def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
            """Provide access details for LLM consumption."""
            key_ref = key_name if key_name else "key_name"
            
            return {
                "location": self.location,
                "temperature": self.temperature,
                "conditions": self.conditions,
                "temperature_formatted": f"{self.temperature}°C",
                "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.temperature, context.{self.CONTEXT_TYPE}.{key_ref}.conditions",
                "example_usage": f"The temperature in {self.location} is {{context.{self.CONTEXT_TYPE}.{key_ref}.temperature}}°C with {{context.{self.CONTEXT_TYPE}.{key_ref}.conditions}} conditions",
                "available_fields": ["location", "temperature", "conditions", "timestamp"]
            }

**Required Method 2: get_human_summary()**

Provides human-readable summaries for user interfaces and debugging:

.. code-block:: python

        def get_human_summary(self, key: str) -> dict:
            """Get human-readable summary for this weather context."""
            return {
                "summary": f"Weather in {self.location} on {self.timestamp.strftime('%Y-%m-%d')}: {self.temperature}°C, {self.conditions}",
            }

.. dropdown:: Complete Weather Context Implementation
   
   Full context class showing all required methods (`view context class on GitHub <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/hello_world_weather/context_classes.py>`_)

   .. code-block:: python

      """
      Hello World Weather Context Classes - Quick Start Version

      These classes serve as a simple data structure for exchange of the weather information between the capabilities and the orchestrator.

      It is important to note that the context classes are not used to determine the location, but rather to determine if the task requires current weather information for a specific location.
      The location is determined by the orchestrator based on the user query and the context of the task.

      The context classes are used to store the weather information in a structured format that can be easily used by the capabilities and the orchestrator.
      """

      from datetime import datetime
      from typing import Dict, Any, Optional, ClassVar
      from pydantic import Field
      from framework.context.base import CapabilityContext

      class CurrentWeatherContext(CapabilityContext):
          """Simple context for current weather conditions."""
          
          CONTEXT_TYPE: ClassVar[str] = "CURRENT_WEATHER"
          CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
          
          # Basic weather data
          location: str = Field(description="Location name")
          temperature: float = Field(description="Temperature in Celsius")
          conditions: str = Field(description="Weather conditions description")
          timestamp: datetime = Field(description="Timestamp of weather data")
          
          @property
          def context_type(self) -> str:
              """Return the context type identifier."""
              return self.CONTEXT_TYPE
          
          def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
              """Provide access details for LLM consumption."""
              key_ref = key_name if key_name else "key_name"
              
              return {
                  "location": self.location,
                  "current_temp": f"{self.temperature}°C",
                  "conditions": self.conditions,
                  "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.temperature, context.{self.CONTEXT_TYPE}.{key_ref}.conditions",
                  "example_usage": f"The temperature in {self.location} is {{context.{self.CONTEXT_TYPE}.{key_ref}.temperature}}°C with {{context.{self.CONTEXT_TYPE}.{key_ref}.conditions}} conditions",
                  "available_fields": ["location", "temperature", "conditions", "timestamp"]
              }
          
          def get_human_summary(self, key: str) -> dict:
              """Get human-readable summary for this weather context."""
              return {
                  "summary": f"Weather in {self.location} on {self.timestamp.strftime('%Y-%m-%d')}: {self.temperature}°C, {self.conditions}",
              }

Step 4: Building the Weather Capability
----------------------------------------

Capabilities are the **business logic units** that perform specific tasks. Our weather capability demonstrates the essential patterns for data retrieval, context storage, and framework integration.

**4.1: The @capability_node Decorator**

The ``@capability_node`` decorator validates required class components and creates a LangGraph-compatible wrapper function with full infrastructure support:

.. code-block:: python

   @capability_node
   class CurrentWeatherCapability(BaseCapability):
       """Get current weather conditions for a location."""
       
       # Required class attributes for registry configuration
       name = "current_weather"
       description = "Get current weather conditions for a location"
       provides = ["CURRENT_WEATHER"]
       requires = []

.. admonition:: Key Insight
   
   The ``provides`` field tells the framework what context types this capability generates. The ``requires`` field tells the framework what context types this capability needs to run.

**4.2: Core Business Logic**

The ``execute()`` method contains your main business logic, which you could call the 'tool' in agentic terms. Here's the weather retrieval:

.. code-block:: python

       @staticmethod
       async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
           """Execute weather retrieval."""
           step = StateManager.get_current_step(state)
           streamer = get_streamer("hello_world_weather", "current_weather", state)
           
           try:
               streamer.status("Extracting location from query...")
               query = StateManager.get_current_task(state).lower()
               
               # Simple location detection
               location = "San Francisco"  # default
               if "new york" in query or "nyc" in query:
                   location = "New York"
               elif "prague" in query or "praha" in query:
                   location = "Prague"
               
               streamer.status(f"Getting weather for {location}...")
               weather = weather_api.get_current_weather(location)
               
               # Create context object
               context = CurrentWeatherContext(
                   location=weather.location,
                   temperature=weather.temperature,
                   conditions=weather.conditions,
                   timestamp=weather.timestamp
               )
               
               # Store context in framework state
               context_updates = StateManager.store_context(
                   state, 
                   registry.context_types.CURRENT_WEATHER, 
                   step.get("context_key"), 
                   context
               )
               
               streamer.status(f"Weather retrieved: {location} - {weather.temperature}°C")
               return context_updates
               
           except Exception as e:
               logger.error(f"Weather retrieval error: {e}")
               raise

.. admonition:: Key Steps

   1. **Framework Setup** - Get streaming utilities and current execution step
   2. **Location Extraction** - Parse user query to find location (simplified for demo)
   3. **Data Retrieval** - Call your API/service to get actual data  
   4. **Context Creation** - Convert raw data to structured context object
   5. **State Storage** - Store context so other capabilities and LLM can access it

**4.3: Essential Supporting Methods**

Every capability needs basic error handling and retry policies:

.. code-block:: python

       @staticmethod
       def classify_error(exc: Exception, context: dict) -> ErrorClassification:
           """Classify errors for retry decisions."""
           if isinstance(exc, (ConnectionError, TimeoutError)):
               return ErrorClassification(
                   severity=ErrorSeverity.RETRIABLE,
                   user_message="Weather service timeout, retrying...",
                   metadata={"technical_details": str(exc)}
               )
           
           return ErrorClassification(
               severity=ErrorSeverity.CRITICAL,
               user_message=f"Weather service error: {str(exc)}",
               metadata={
                   "technical_details": f"Error: {type(exc).__name__}"
               }
           )
       
       @staticmethod 
       def get_retry_policy() -> Dict[str, Any]:
           """Retry policy for weather data retrieval."""
           return {
               "max_attempts": 3,
               "delay_seconds": 0.5,
               "backoff_factor": 1.5
           }

.. admonition:: Framework Benefits

   The Framework Handles Everything Else: Error routing, retry logic, user messaging, and execution flow are automatically managed by the framework infrastructure.

**4.4: Orchestrator Guide**
   
The orchestrator guide teaches the LLM how to plan execution steps and use your capability effectively:

.. code-block:: python

    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
    """Guide the orchestrator on how to use this capability."""
    example = OrchestratorExample(
              step=PlannedStep(
                  context_key="current_weather",
                  capability="current_weather",
                  task_objective="Get current weather conditions for the specified location",
                  expected_output=registry.context_types.CURRENT_WEATHER,
                  success_criteria="Current weather data retrieved with temperature and conditions",
            inputs=[]
              ),
              scenario_description="Getting current weather for a location",
              notes=f"Output stored as {registry.context_types.CURRENT_WEATHER} with live weather data."
          )
          
          return OrchestratorGuide(
              instructions=f"""**When to plan "current_weather" steps:**
      - When users ask for current weather conditions
      - For real-time weather information requests
      - When location-specific current conditions are needed

      **Output: {registry.context_types.CURRENT_WEATHER}**
      - Contains: location, temperature, conditions, timestamp
      - Available for immediate display or further analysis

      **Location Support:**
      - Supports: San Francisco, New York, Prague
    - Defaults to San Francisco if location not specified""",
        examples=[example],
        order=5
    )

.. admonition:: For Complex Capabilities
   
   When building more sophisticated capabilities with multiple steps, dependencies, or complex planning logic, providing comprehensive orchestrator examples becomes crucial. The orchestrator uses these examples to understand when and how to integrate your capability into multi-step execution plans.

**4.5: Classifier Guide**

The classifier guide teaches the LLM when to activate your capability based on user queries:

.. code-block:: python

      def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Guide the classifier on when to activate this capability."""
          return TaskClassifierGuide(
              instructions="Determine if the task requires current weather information for a specific location.",
              examples=[
                  ClassifierExample(
                      query="What's the weather like in San Francisco right now?", 
                      result=True,  
                      reason="Request asks for current weather conditions in a specific location."
                  ),
                  ClassifierExample(
                      query="How's the weather today?", 
                      result=True, 
                      reason="Current weather request, though location may need to be inferred."
                  ),
                  ClassifierExample(
                      query="What was the weather like last week?", 
                      result=False, 
                      reason="Request is for historical weather data, not current conditions."
                  ),
                  ClassifierExample(
                    query="What tools do you have?", 
                    result=False, 
                    reason="Request is for tool information, not weather."
                  ),
              ],
              actions_if_true=ClassifierActions()
          )

.. admonition:: Quality Examples Matter
   
   The classifier's accuracy depends heavily on the quality and diversity of your examples. Include edge cases, ambiguous queries, and clear negative examples to help the LLM make better classification decisions.

.. dropdown:: Complete Current Weather Capability Implementation
   
   Full capability showing all required methods and patterns (`view capability on GitHub <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/hello_world_weather/capabilities/current_weather.py>`_)

   .. code-block:: python

      """
      Current Weather Capability
      
      Simple capability to get current weather conditions for a location.
      """
      
      from typing import Dict, Any, Optional
      
      from framework.base import (
          BaseCapability, capability_node,
          OrchestratorGuide, OrchestratorExample, PlannedStep,
          ClassifierActions, ClassifierExample, TaskClassifierGuide
      )
      from framework.base.errors import ErrorClassification, ErrorSeverity
      from framework.registry import get_registry
      from framework.state import AgentState, StateManager
      from configs.logger import get_logger
      from configs.streaming import get_streamer
      
      from applications.hello_world_weather.context_classes import CurrentWeatherContext
      from applications.hello_world_weather.mock_weather_api import weather_api
      
      logger = get_logger("hello_world_weather", "current_weather")
      registry = get_registry()
      
      @capability_node
      class CurrentWeatherCapability(BaseCapability):
          """Get current weather conditions for a location."""
          
          # Required class attributes for registry configuration
          name = "current_weather"
          description = "Get current weather conditions for a location"
          provides = ["CURRENT_WEATHER"]
          requires = []
          
          @staticmethod
          async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
              """Execute weather retrieval."""
              step = StateManager.get_current_step(state)
              streamer = get_streamer("hello_world_weather", "current_weather", state)
              
              try:
                  streamer.status("Extracting location from query...")
                  query = StateManager.get_current_task(state).lower()
                  
                  # Simple location detection
                  location = "San Francisco"  # default
                  if "new york" in query or "nyc" in query:
                      location = "New York"
                  elif "prague" in query or "praha" in query:
                      location = "Prague"
                  
                  streamer.status(f"Getting weather for {location}...")
                  weather = weather_api.get_current_weather(location)
                  
                  # Create context object
                  context = CurrentWeatherContext(
                      location=weather.location,
                      temperature=weather.temperature,
                      conditions=weather.conditions,
                      timestamp=weather.timestamp
                  )
                  
                  # Store context in framework state
                  context_updates = StateManager.store_context(
                      state, 
                      registry.context_types.CURRENT_WEATHER, 
                      step.get("context_key"), 
                      context
                  )
                  
                  streamer.status(f"Weather retrieved: {location} - {weather.temperature}°C")
                  return context_updates
                  
              except Exception as e:
                  logger.error(f"Weather retrieval error: {e}")
                  raise
          
          @staticmethod
          def classify_error(exc: Exception, context: dict) -> ErrorClassification:
              """Classify errors for retry decisions."""
              if isinstance(exc, (ConnectionError, TimeoutError)):
                  return ErrorClassification(
                      severity=ErrorSeverity.RETRIABLE,
                      user_message="Weather service timeout, retrying...",
                      metadata={"technical_details": str(exc)}
                  )
              
              return ErrorClassification(
                  severity=ErrorSeverity.CRITICAL,
                  user_message=f"Weather service error: {str(exc)}",
                  metadata={"technical_details": f"Error: {type(exc).__name__}"}
              )
          
          @staticmethod 
          def get_retry_policy() -> Dict[str, Any]:
              """Retry policy for weather data retrieval."""
              return {
                  "max_attempts": 3,
                  "delay_seconds": 0.5,
                  "backoff_factor": 1.5
              }
          
          def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
              """Guide the orchestrator on how to use this capability."""
              example = OrchestratorExample(
                  step=PlannedStep(
                      context_key="current_weather",
                      capability="current_weather",
                      task_objective="Get current weather conditions for the specified location",
                      expected_output=registry.context_types.CURRENT_WEATHER,
                      success_criteria="Current weather data retrieved with temperature and conditions",
                      inputs=[]
                  ),
                  scenario_description="Getting current weather for a location",
                  notes=f"Output stored as {registry.context_types.CURRENT_WEATHER} with live weather data."
              )
              
              return OrchestratorGuide(
                  instructions=f"""**When to plan "current_weather" steps:**
          - When users ask for current weather conditions
          - For real-time weather information requests
          - When location-specific current conditions are needed

          **Output: {registry.context_types.CURRENT_WEATHER}**
          - Contains: location, temperature, conditions, timestamp
          - Available for immediate display or further analysis

          **Location Support:**
          - Supports: San Francisco, New York, Prague
          - Defaults to San Francisco if location not specified""",
                  examples=[example],
                  order=5
              )
          
          def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
              """Guide the classifier on when to activate this capability."""
              return TaskClassifierGuide(
                  instructions="Determine if the task requires current weather information for a specific location.",
                  examples=[
                      ClassifierExample(
                          query="What's the weather like in San Francisco right now?", 
                          result=True,  
                          reason="Request asks for current weather conditions in a specific location."
                      ),
                      ClassifierExample(
                          query="How's the weather today?", 
                          result=True, 
                          reason="Current weather request, though location may need to be inferred."
                      ),
                      ClassifierExample(
                          query="What was the weather like last week?", 
                          result=False, 
                          reason="Request is for historical weather data, not current conditions."
                      ),
                      ClassifierExample(
                          query="What tools do you have?", 
                          result=False, 
                          reason="Request is for tool information, not weather."
                      ),
                  ],
                  actions_if_true=ClassifierActions()
              )

Step 5: Understanding the Registry
-----------------------------------

The registry system is how the framework discovers and manages your application's components. It uses a simple pattern where your application provides a configuration that tells the framework what capabilities and context classes you've defined.

.. admonition:: Registry Purpose
   
   The registry enables loose coupling and lazy loading - the framework can discover your components without importing them until needed, improving startup performance and modularity.

**5.1: The Registry Provider Pattern**

Every application implements a ``RegistryConfigProvider`` that tells the framework what components exist:

.. code-block:: python

   from framework.registry import RegistryConfigProvider, RegistryConfig
   
   class HelloWorldWeatherRegistryProvider(RegistryConfigProvider):
       """Registry provider for Hello World Weather application."""
       
       def get_registry_config(self) -> RegistryConfig:
           """Tell the framework what components this application provides."""
           return RegistryConfig(
               capabilities=[...],      # Your capabilities
               context_classes=[...]    # Your context classes
           )

**5.2: Registering Capabilities**

Use a list of ``CapabilityRegistration`` objects to tell the framework about your capabilities:

.. code-block:: python

   from framework.registry import CapabilityRegistration
   
   capabilities=[
       CapabilityRegistration(
           name="current_weather",                    # Unique name
           module_path="applications.hello_world_weather.capabilities.current_weather",
           class_name="CurrentWeatherCapability",     # Class to load
           description="Get current weather conditions for a location",
           provides=["CURRENT_WEATHER"],              # Context types it creates
           requires=[]                                # Context types it needs
       )
   ]

**5.3: Registering Context Classes**

Use a list of ``ContextClassRegistration`` objects to register your data structures:

.. code-block:: python

   from framework.registry import ContextClassRegistration
   
   context_classes=[
       ContextClassRegistration(
           context_type="CURRENT_WEATHER",           # Must match capability's "provides"
           module_path="applications.hello_world_weather.context_classes",
           class_name="CurrentWeatherContext"        # Class to load
       )
   ]

.. dropdown:: Complete Registry Implementation
   
   Complete registry file (`view registry on GitHub <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/hello_world_weather/registry.py>`_)

   .. code-block:: python

      """
      Hello World Weather Registry
      
      Simple registration of weather capabilities and context classes.
      """
      
      from framework.registry import (
          CapabilityRegistration, 
          ContextClassRegistration, 
          RegistryConfig,
          RegistryConfigProvider
      )
      
      class HelloWorldWeatherRegistryProvider(RegistryConfigProvider):
          """Registry provider for Hello World Weather application."""
          
          def get_registry_config(self) -> RegistryConfig:
              """Get hello world weather application registry configuration.
              
              Returns:
                  RegistryConfig: Registry configuration for hello world weather application
              """
              return RegistryConfig(
                  capabilities=[
                      CapabilityRegistration(
                          name="current_weather",
                          module_path="applications.hello_world_weather.capabilities.current_weather",
                          class_name="CurrentWeatherCapability", 
                          description="Get current weather conditions for a location",
                          provides=["CURRENT_WEATHER"],
                          requires=[]
                      )
                  ],
                  
                  context_classes=[
                      ContextClassRegistration(
                          context_type="CURRENT_WEATHER",
                          module_path="applications.hello_world_weather.context_classes", 
                          class_name="CurrentWeatherContext"
                      )
                  ]
              )

Step 6: Application Configuration
----------------------------------

The ``config.yml`` file contains the application settings (`view config on GitHub <https://github.com/thellert/alpha_berkeley/blob/main/src/applications/hello_world_weather/config.yml>`_):

.. code-block:: yaml

   # Hello World Weather Application Configuration - Quick Start Version

   # OpenWebUI pipeline configuration
   pipeline:
     name: "Hello World Weather"

   # Logging
   logging:
     logging_colors:
       current_weather: "blue"

**Enable Your Application**

Finally, you need to enable your application in the main configuration file. Add ``hello_world_weather`` to the applications list in the root ``config.yml``:

**File:** ``config.yml`` (at project root)

.. code-block:: yaml

   applications: 
     - hello_world_weather

.. admonition::
   The framework automatically discovers application configurations using this applications list. Without adding your application here, the framework won't load it, even if the application config file exists.

Step 7: Test Your Agent
-----------------------

To test your new agent, you can use the Direct Conversation interface, which allows you to interact with it directly from the command line.

1. **Navigate to the CLI directory**:
   .. code-block:: bash

      cd interfaces/CLI

2. **Run the Direct Conversation script**:
   .. code-block:: bash

      python direct_conversation.py

*Start asking questions*: The framework will automatically load the hello_world_weather application and you can ask weather-related questions directly in the terminal. When you run your agent, you'll see the framework's decision-making process in action. Here are the key phases to watch for:


**Phase 1: Framework Initialization**

.. code-block::

   🔄 Initializing framework...
   INFO Registry: Registry initialization complete!
        Components loaded:
           • X capabilities: memory, time_range_parsing, respond, clarify, current_weather ...
           • X context types: MEMORY_CONTEXT, TIME_RANGE, CURRENT_WEATHER ...
   ✅ Framework initialized!

.. admonition:: What's Happening
   :class: important
   
   The framework loads all available capabilities, including your ``current_weather`` capability and ``CURRENT_WEATHER`` context type. This modular loading system allows you to see exactly which components are active in your agent.

**Phase 2: Task Processing Pipeline**

The user query "What's the weather in San Francisco right now?" is processed by the framework.

.. code-block::

   🔄 Processing: What's the weather in San Francisco right now?
   🔄 Extracting actionable task from conversation
   INFO Task_Extraction: * Extracted: 'Get the current weather conditions in San Francisco...'
   🔄 Analyzing task requirements...
   INFO Classifier: >>> Capability 'current_weather' >>> True
   🔄 Generating execution plan...

.. admonition:: What's Happening
   :class: important
   
   This is the **core decision-making process**: 
   
   1. **Task Extraction**: Complete chat history gets converted to an actionable task
   2. **Classification**: Each capability is checked if it is needed to complete the current task. Notice how your capability gets activated (``>>> True``).
   3. **Planning**: An execution strategy is formulated, taking the active capabilities into account   
   
**Phase 3: Execution Planning**

.. code-block::

   INFO Orchestrator: ==================================================
   INFO Orchestrator:  << Step 1
   INFO Orchestrator:  << ├───── id: 'sf_weather'
   INFO Orchestrator:  << ├─── node: 'current_weather'
   INFO Orchestrator:  << ├─── task: 'Retrieve current weather conditions for San Francisco
                          including temperature, conditions, and timestamp'
   INFO Orchestrator:  << └─ inputs: '[]'
   INFO Orchestrator:  << Step 2
   INFO Orchestrator:  << ├───── id: 'weather_response'
   INFO Orchestrator:  << ├─── node: 'respond'
   INFO Orchestrator:  << ├─── task: 'Present the current weather conditions for San Francisco to
                          the user in a clear and readable format'
   INFO Orchestrator:  << └─ inputs: '[{'CURRENT_WEATHER': 'sf_weather'}]'
   INFO Orchestrator: ==================================================
   ✅ Orchestrator: Final execution plan ready with 2 steps

.. admonition:: What's Happening
   :class: important
   
   The orchestrator breaks down the task into logical steps:
   
   - **Step 1**: Use your ``current_weather`` capability to get data and store it under the key ``sf_weather``
   - **Step 2**: Use the ``respond`` capability to format results and use the ``sf_weather`` context as input, knowing that its a ``CURRENT_WEATHER`` context type.
   
   This demonstrates how capabilities work together in a coordinated workflow.

**Phase 4: Real-Time Execution**

.. code-block::

   🔄 Executing current_weather... (10%)
   🔄 Extracting location from query...
   🔄 Getting weather for San Francisco...
   🔄 Weather retrieved: San Francisco - 21.0°C
   🔄 Generating response...

.. admonition:: What's Happening
   :class: important
   
   Your capability is now running! The status messages come from your ``streamer.status()`` (OpenWebUI) and ``logger.info()`` (CLI) calls, providing real-time feedback as your business logic executes.

**Final Result**

.. code-block::

   🤖 According to the [CURRENT_WEATHER.sf_weather] data, the weather conditions in San Francisco 
   for 2025-08-04 are 21.0°C and Partly Cloudy.

.. admonition:: Success Indicators
   :class: important
   
   - Your weather data was successfully retrieved and stored as ``[CURRENT_WEATHER.sf_weather]``
   - The context reference shows the framework is using your structured data
   - The response is formatted professionally using the framework's response capability

**What You've Built**

By completing this tutorial, you've created an agentic system that demonstrates:

- **Modular Architecture**: Your capability integrates seamlessly with framework components
- **Scalable Orchestration**: The framework can handle multiple capabilities and context types
- **Structured Data Flow**: Information flows through context classes to enable capability coordination
- **Informative UX**: Real-time status updates and structured responses

.. admonition:: Next Steps
   
   Try invoking other (framework-provided) capabilities :
   
   - "Save the current weather in Prague to my memories"
   - "Calculate the square root of 42"

   Try out 'human in the loop' mechanics, for example by activating ``planning`` mode:

   - "/planning What's the weather in Prague?"

   Try using the OpenWebUI interface by running your agent through the pipeline container service.

   **Ready for more?** :doc:`Build your first production agent <build-your-first-agent>` with advanced capabilities, multi-step workflows, and external data source provider integrations.
