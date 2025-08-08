# Hello World Weather Agent - Quick Start

A super simple weather agent for learning Alpha Berkeley Framework basics. Get it running in 15 minutes!

## What It Does

Ask about current weather in San Francisco, New York, or Prague and get instant results! The current weather conditions are provided by a simple mock API.



## Quick Setup (15 minutes)

1. **Try these queries:**
   ```
   "What's the weather in San Francisco?"
   "How's the weather in New York?"
   "Tell me about Prague weather"
   ```

That's it! No external APIs, no complex setup.

## What You'll Learn

### Framework Basics
- **Context Classes**: Type-safe data structures (`CurrentWeatherContext`)
- **Capabilities**: Business logic components (`current_weather`)
- **Mock Services**: No external dependencies needed
- **LLM Integration**: Automatic query understanding
- **LangGraph Native**: Uses modern `@capability_node` decorator patterns

✅ **Migrated**: This example uses the modern LangGraph-native framework patterns with `@capability_node` decorator, streaming integration, and helper functions for context storage.

### Simple Architecture
```
User Query → LLM Classifier → Weather Capability → Mock API → Results
```

## Files Overview

```
src/applications/hello_world_weather/
├── config.yml                    # Simple configuration
├── context_classes.py             # Weather data structure
├── mock_weather_api.py            # Fake weather service
├── registry.py                    # Component registration  
├── capabilities/
│   └── current_weather.py        # Main weather logic
└── README.md                      # This file
```

## How It Works

1. **User asks**: "What's the weather in London?"
2. **LLM understands**: Classifies as weather request
3. **Capability runs**: Extracts "London" from query
4. **Mock API**: Generates realistic London weather
5. **Result returned**: Structured weather data

## Supported Cities

- San Francisco (default)
- New York
- Prague

## Next Steps

Once this is working:
1. **Explore the code**: See how capabilities work
2. **Add a city**: Modify `mock_weather_api.py`
3. **Try the Wind Turbine agent**: More complex example
4. **Build your own**: Use this as a template

## Key Code Patterns

### Context Class (Data Structure)
```python
class CurrentWeatherContext(CapabilityContext):
    CONTEXT_TYPE: ClassVar[str] = "CURRENT_WEATHER"
    
    location: str = Field(description="Location name")
    temperature: float = Field(description="Temperature in Celsius")
    conditions: str = Field(description="Weather conditions description")
    timestamp: datetime = Field(description="Timestamp of weather data")
```

### Capability (Business Logic)  
```python
@capability_node
class CurrentWeatherCapability(BaseCapability):
    name = "current_weather"
    description = "Get current weather conditions for a location"
    
    @staticmethod
    async def execute(state: AgentState, **kwargs):
        # LangGraph streaming
        writer = get_stream_writer()
        if writer:
            writer({"event_type": "status", "message": "Getting weather..."})
        
        # Business logic
        weather = weather_api.get_current_weather(location)
        
        # Context storage using helper functions
        return StateManager.store_context(state, "CURRENT_WEATHER", context_key, weather)
```

## Troubleshooting

**Not working?** Check:
- Is Ollama running? (`ollama serve`)
- Is mistral:7b installed? (`ollama pull mistral:7b`)
- Any errors in the terminal output?
- Is the application properly configured in the main `config.yml`?

**Need help?** This is the simplest possible example - if it's not working, there might be a framework setup issue.

---

**Goal**: Get this running in 15 minutes, then explore the more complex Wind Turbine agent! 