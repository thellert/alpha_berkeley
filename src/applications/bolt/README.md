# BOLT - Alpha Berkeley Framework Application

> **Intelligent Agent Application for Scientific Instrument Control**  
> Natural language interface for beamline operations built on the Alpha Berkeley Framework, demonstrating advanced AI agent patterns for scientific computing.

## 🚀 Executive Summary

BOLT is the base testbed that showcases the Alpha Berkeley Framework's capabilities for building intelligent scientific automation systems. It provides researchers with natural language control over complex experimental workflows through a modern AI agent architecture.

**Key Framework Features Demonstrated:**
- **Capability System**: Modular, composable operations with type-safe interfaces
- **Context Management**: Structured data flow with persistent state tracking
- **Natural Language Processing**: LLM-powered command interpretation and execution
- **Streaming Integration**: Real-time operation feedback and status updates

---

## 📋 Table of Contents

1. [Framework Architecture](#framework-architecture)
2. [Application Components](#application-components)
3. [Capability System](#capability-system)
4. [Context Management](#context-management)
5. [Operation Modes](#operation-modes)
6. [Setup and Configuration](#setup-and-configuration)
7. [Development Guide](#development-guide)
8. [Extension Patterns](#extension-patterns)

---

<<<<<<< HEAD
### On your webUI, modify openAI API to use http://pieplines:9099 instead of 
### http://host.docker.internal:9099, which lets you talk to bolt regularly

---

=======
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
## 🏗️ Framework Architecture

### Alpha Berkeley Integration

BOLT demonstrates the Alpha Berkeley Framework's architectural patterns for building intelligent agent applications:

1. **Agent Layer**: Natural language interface and conversation management
2. **Framework Layer**: LangGraph-based execution engine with streaming
3. **Capability Layer**: Modular, composable operations
4. **API Layer**: External system integration interface

### Component Flow

```
User Natural Language Input 
    ↓
Alpha Berkeley Agent (LLM Classification & Planning)
    ↓
LangGraph Execution Engine
    ↓
BOLT Capability Registry
    ↓
Context-Aware Operations
    ↓
External API Integration
```

### Framework Principles

- **Modular Design**: Capabilities are independently developed and composed
- **Type Safety**: Structured context classes with validation
- **Streaming Integration**: Real-time feedback through framework streaming
- **Registry Pattern**: Automatic capability discovery and registration
- **Context Management**: Persistent state across multi-step operations

---

## 💻 Application Components

### Core Framework Components

#### 1. Capability Registry (`registry.py`)
**Primary Function**: Automatic capability discovery and registration within the Alpha Berkeley Framework

- **Pattern**: Registry Provider implementation
- **Discovery**: Automatic capability and context type registration
- **Integration**: Seamless framework compatibility
- **Extensibility**: Plugin architecture for new capabilities

#### 2. Context Classes (`context_classes.py`)
**Primary Function**: Type-safe data structures for agent state management

- **Type Safety**: Pydantic-based validation and serialization
- **Framework Integration**: Compatible with Alpha Berkeley context patterns
- **Streaming Support**: Real-time state updates
- **Persistence**: Cross-operation state management

#### 3. API Integration (`bolt_api.py`)
**Primary Function**: External system communication interface

- **Abstraction**: Clean interface between framework and external systems
- **Error Handling**: Intelligent retry and error classification
- **Timeout Management**: Robust network communication
- **Type Safety**: Structured request/response handling

---

## 🎯 Capability System

### Alpha Berkeley Capability Pattern

BOLT demonstrates the Alpha Berkeley Framework's capability architecture through four core operations:

#### Context Classes (`context_classes.py`)
```python
# Motor Position Context
class CurrentAngleContext(CapabilityContext):
    motor: str          # Motor identifier
    angle: float        # Current position value
    condition: str      # Operation status
    timestamp: datetime # Reading timestamp

# Motor Movement Context  
class CurrentMoveMotorContext(CapabilityContext):
    motor: str          # Motor identifier
    angle: float        # Target position
    condition: str      # Movement status
    timestamp: datetime # Operation timestamp

# Image Capture Context
class CurrentTakeCaptureContext(CapabilityContext):
    condition: str      # Capture status
    timestamp: datetime # Operation timestamp

# Scan Execution Context
class CurrentRunScanContext(CapabilityContext):
    condition: str      # Scan status
    timestamp: datetime # Operation timestamp
```

### Capability Implementations

#### Motor Position Read (`motor_position_read.py`)
**Framework Pattern**: Data acquisition capability with context storage

**Key Features:**
- **@capability_node decorator**: Framework integration
- **Context management**: Structured data storage
- **Error classification**: Intelligent retry logic
- **Streaming integration**: Real-time feedback

**Example Usage Patterns:**
- "What's the current position?"
- "Check current state before next operation"
- "Show me the status"

#### Motor Position Set (`motor_position_set.py`)
**Framework Pattern**: Action capability with parameter extraction

**Key Features:**
- **Natural language parsing**: LLM-powered parameter extraction
- **Type validation**: Pydantic-based input validation
- **State transitions**: Context-aware operations
- **Streaming updates**: Progress tracking

**Example Usage Patterns:**
- "Move to 45 degrees"
- "Rotate by 30 degrees"  
- "Set position to 90"

#### Detector Image Capture (`detector_image_capture.py`)
**Framework Pattern**: Simple action capability

**Key Features:**
- **Single operation**: Atomic capability execution
- **Status reporting**: Operation result tracking
- **Error handling**: Framework error patterns
- **Context storage**: Result persistence

**Example Usage Patterns:**
- "Take an image"
- "Capture now"
- "Get a measurement"

#### Photogrammetry Scan Execute (`photogrammetry_scan_execute.py`)
**Framework Pattern**: Complex workflow capability

**Key Features:**
- **Multi-step coordination**: Sequential operation management
- **Parameter configuration**: Complex input handling
- **Progress tracking**: Long-running operation support
- **Result aggregation**: Comprehensive output context

**Example Usage Patterns:**
- "Run a scan from 0 to 180 degrees with 20 projections"
- "Execute a complete measurement cycle"
- "Start the automated sequence"

---

## 🔧 Context Management

### Framework Context Pattern

BOLT demonstrates the Alpha Berkeley Framework's context management system for maintaining state across multi-step operations.

#### Context Types and Usage

##### Data Reading Contexts
```python
class CurrentAngleReading(BaseModel):
    """Framework-compatible data reading structure"""
    motor: str
    angle: float
    condition: str
    timestamp: datetime
    
    # Framework integration
    @classmethod
    def from_api_response(cls, response_text: str) -> 'CurrentAngleReading':
        """Parse external API response into structured context"""
```

##### Operation Result Contexts
```python
class CurrentMoveMotorReading(BaseModel):
    """Action result with validation and persistence"""
    motor: str
    final_angle: float
    condition: str
    timestamp: datetime
    
    # Type safety and validation
    @validator('final_angle')
    def validate_angle_range(cls, v):
        return max(0, min(360, v))
```

#### Context Storage and Retrieval

**Framework Integration Pattern:**
```python
# Store context in framework state
context_updates = StateManager.store_context(
    state,
    registry.context_types.MOTOR_POSITION,
    "current_angle",
    angle_context
)

# Retrieve context for downstream operations
previous_angle = StateManager.get_context(
    state,
    registry.context_types.MOTOR_POSITION,
    "current_angle"
)
```

### Registry Implementation (`registry.py`)

#### BoltRegistryProvider
**Framework Pattern**: Registry provider for automatic discovery

**Alpha Berkeley Integration:**
```python
class BoltRegistryProvider(RegistryProvider):
    """Demonstrates framework registry patterns"""
    
    def get_capabilities(self) -> List[CapabilityRegistration]:
        return [
            CapabilityRegistration(
                name="motor_position_read",
                module_path="applications.bolt.capabilities.motor_position_read",
                class_name="MotorPositionReadCapability",
                description="Framework-integrated position reading",
                provides=["MOTOR_POSITION"],
                requires=[]
            ),
            # Additional capabilities...
        ]
    
    def get_context_types(self) -> List[ContextTypeRegistration]:
        return [
            ContextTypeRegistration(
                name="MOTOR_POSITION",
                module_path="applications.bolt.context_classes",
                class_name="CurrentAngleContext",
                description="Type-safe position data"
            ),
            # Additional context types...
        ]
```

**Framework Benefits:**
- **Automatic Discovery**: No manual capability registration required
- **Type Safety**: Context classes validated at registration
- **Dependency Resolution**: Framework handles capability ordering
- **Plugin Architecture**: Easy extension without core changes

---

## 🎯 External System Integration

### API Communication Pattern

BOLT demonstrates how Alpha Berkeley applications can integrate with external systems while maintaining framework patterns.

#### API Abstraction Layer (`bolt_api.py`)

**Framework Integration:**
```python
class BoltAPI:
    """External system interface following framework patterns"""
    
    def get_current_angle(self, motor: str) -> CurrentAngleReading:
        """
        Framework-compatible API call with error handling
        """
        try:
            response = requests.get(f"{self.api_url}/get_angle", timeout=5)
            return CurrentAngleReading.from_api_response(response.text)
        except Exception as e:
            # Framework error classification
            error_info = self.classify_error(e)
            raise CapabilityError(
                message=error_info.user_message,
                severity=error_info.severity,
                context={"operation": "get_angle", "motor": motor}
            )
```

#### Error Classification

**Framework Error Handling:**
```python
@staticmethod
def classify_error(exc: Exception) -> ErrorClassification:
    """Intelligent error classification for framework retry logic"""
    
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return ErrorClassification(
            severity=ErrorSeverity.RETRIABLE,
<<<<<<< HEAD
            metadata={
                "user_message": "Communication timeout, retrying...",
                "technical_details": str(exc)
            }
=======
            user_message="Communication timeout, retrying...",
            technical_details=str(exc)
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
        )
    
    return ErrorClassification(
        severity=ErrorSeverity.CRITICAL,
<<<<<<< HEAD
        metadata={
            "user_message": f"Operation failed: {str(exc)}",
            "technical_details": f"Error: {type(exc).__name__}"
        }
=======
        user_message=f"Operation failed: {str(exc)}",
        technical_details=f"Error: {type(exc).__name__}"
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
    )
```

---

## 🎯 Operation Modes

### 1. Alpha Berkeley CLI Interface

#### Framework Integration
```bash
cd interfaces/CLI
python direct_conversation.py
```

The BOLT application integrates seamlessly with the Alpha Berkeley Framework's CLI interface, demonstrating:

- **Natural Language Processing**: LLM-powered intent recognition
- **Capability Routing**: Automatic selection of appropriate operations
- **Context Persistence**: State management across conversation turns
- **Streaming Feedback**: Real-time operation updates

#### Framework Conversation Flow
```
User: "What's the current position?"
BOLT: [Invokes motor_position_read capability]
      → Context stored: CurrentAngleContext
      → Response: "Current position is 45.2°"

User: "Move to 90 degrees"
BOLT: [Invokes motor_position_set capability]
      → Parameter extraction: {"angle": 90, "mode": "absolute"}
      → Context update: CurrentMoveMotorContext
      → Response: "Moved to 90.0° successfully"

User: "Take a measurement"
BOLT: [Invokes detector_image_capture capability]
      → Context stored: CurrentTakeCaptureContext
      → Response: "Image captured successfully"
```

### 2. Web Interface Mode

#### Framework Web Integration
```bash
# Start framework services
python3 ./deployment/container_manager.py config.yml up

# Access Alpha Berkeley web interface
# URL: http://localhost:8080
```

**Framework Features Demonstrated:**
- **LangGraph Visualization**: Real-time execution plan display
- **Context Inspector**: Live state monitoring
- **Capability Registry**: Available operations browser
- **Streaming Updates**: WebSocket-based progress tracking

### 3. API Integration Mode

#### Framework API Patterns
BOLT demonstrates how Alpha Berkeley applications can integrate with external systems while maintaining framework benefits:

```python
# Framework-wrapped external operations
@capability_node
class MotorPositionReadCapability(BaseCapability):
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        # External API call with framework error handling
        api = BoltAPI()
        result = api.get_current_angle("DMC01:A") #Pass in motor param
        
        # Framework context storage
        context_updates = StateManager.store_context(
            state, self.registry.context_types.MOTOR_POSITION,
            "current_angle", result
        )
        
        return context_updates
```

---

## ⚙️ Setup and Configuration

### 1. Alpha Berkeley Framework Setup

#### Network Configuration
- **Connection**: EDUROAM network access
- **Firewall**: Port 8000 accessible to BOLT machine
- **DNS**: Ability to resolve 198.128.193.130

#### Software Dependencies
```bash
# Alpha Berkeley Framework core
pip install -r requirements.txt
```

#### Framework Structure
```
src/applications/bolt/
├── capabilities/           # Framework capability implementations
├── context_classes.py     # Type-safe context definitions
├── registry.py           # Framework registry provider
├── bolt_api.py           # External system integration
└── config.yml           # Application configuration
```

### 2. Alpha Berkeley Configuration

#### LLM Model Configuration
**File**: `src/framework/config.yml`

**Option 1: OpenAI GPT (Recommended for Production)**
```yaml
model:
  provider: "openai"
  model_name: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.1
  max_tokens: 1000
```

**Option 2: Local Ollama (Development)**
```yaml
model:
  provider: "ollama"  
  model_name: "mistral:7b"
  base_url: "http://localhost:11434"
  temperature: 0.1
```

**Option 3: Claude (Alternative)**
```yaml
model:
  provider: "cborg"
  model_name: "claude-3-sonnet"
  api_key: "${ANTHROPIC_API_KEY}"
```

#### Application Registration
**File**: `config.yml` (root level)
```yaml
applications:
  - name: "bolt"
    path: "src/applications/bolt"
    enabled: true
    registry_provider: "applications.bolt.registry:BoltRegistryProvider"
```

#### BOLT-Specific Configuration
**File**: `src/applications/bolt/config.yml`
```yaml
# External system configuration
api:
  base_url: "http://external-system:8000"
  timeout: 5
  retry_attempts: 3

# Framework integration settings
framework:
  streaming_enabled: true
  context_persistence: true
  error_classification: true
```

### 3. Framework Deployment

#### Container-Based Deployment
```bash
# 1. Start Alpha Berkeley framework services
python3 ./deployment/container_manager.py config.yml up

# 2. Test CLI interface with BOLT
cd interfaces/CLI
python direct_conversation.py
```

---

## 👩‍💻 Development Guide

### 1. Alpha Berkeley Framework Patterns

#### Adding New Capabilities

**Step 1: Create Framework-Compatible Capability**
```python
from framework.base import BaseCapability, capability_node
from framework.infrastructure import get_streamer

@capability_node
class NewBoltCapability(BaseCapability):
    name = "new_capability"
    description = "Framework-integrated operation"
    provides = ["NEW_CONTEXT_TYPE"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        # Framework streaming integration
        streamer = get_streamer("bolt", "new_capability", state)
        streamer.status("Starting new operation...")
        
        try:
            # Business logic implementation
            result = await perform_operation()
            
            # Framework context storage
            context_updates = StateManager.store_context(
                state,
                registry.context_types.NEW_CONTEXT_TYPE,
                "operation_result",
                result
            )
            
            streamer.status("Operation completed successfully!")
            return context_updates
            
        except Exception as e:
            # Framework error handling
            error_info = classify_error(e, {"capability": "new_capability"})
            streamer.error(error_info.user_message)
            raise CapabilityError(
                message=error_info.user_message,
                severity=error_info.severity
            )
```

**Step 2: Define Type-Safe Context Class**
```python
from framework.context import CapabilityContext
from pydantic import Field, validator
from typing import ClassVar

class NewOperationContext(CapabilityContext):
    CONTEXT_TYPE: ClassVar[str] = "NEW_CONTEXT_TYPE"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Type-safe fields with validation
    operation_id: str = Field(description="Unique operation identifier")
    result_data: float = Field(description="Operation result value")
    status: str = Field(description="Operation completion status")
    
    @validator('result_data')
    def validate_result_range(cls, v):
        """Framework-compatible validation"""
        if v < 0:
            raise ValueError("Result must be non-negative")
        return v
```

**Step 3: Register with Framework Registry**
```python
# In registry.py - BoltRegistryProvider.get_capabilities()
CapabilityRegistration(
    name="new_capability",
    module_path="applications.bolt.capabilities.new_capability",
    class_name="NewBoltCapability",
    description="Framework-integrated new operation",
    provides=["NEW_CONTEXT_TYPE"],
    requires=[],
    category="ACTION"  # Framework capability categorization
)

# In registry.py - BoltRegistryProvider.get_context_types()
ContextTypeRegistration(
    name="NEW_CONTEXT_TYPE",
    module_path="applications.bolt.context_classes",
    class_name="NewOperationContext",
    description="Type-safe operation result data"
)
```

### 2. Framework Best Practices

#### Error Handling with Framework Integration
```python
from framework.infrastructure.error_node import ErrorClassification, ErrorSeverity

@staticmethod
def classify_error(exc: Exception, context: dict) -> ErrorClassification:
    """Framework-compatible error classification"""
    
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return ErrorClassification(
            severity=ErrorSeverity.RETRIABLE,
<<<<<<< HEAD
            metadata={
                "user_message": "Communication timeout, retrying...",
                "technical_details": str(exc),
                "context": context
            }
=======
            user_message="Communication timeout, retrying...",
            technical_details=str(exc),
            context=context
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
        )
    
    if isinstance(exc, ValidationError):
        return ErrorClassification(
            severity=ErrorSeverity.USER_ERROR,
<<<<<<< HEAD
            metadata={
                "user_message": "Invalid parameters provided",
                "technical_details": str(exc),
                "context": context
            }
=======
            user_message="Invalid parameters provided",
            technical_details=str(exc),
            context=context
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
        )
    
    return ErrorClassification(
        severity=ErrorSeverity.CRITICAL,
<<<<<<< HEAD
        metadata={
            "user_message": f"Operation failed: {str(exc)}",
            "technical_details": f"Error: {type(exc).__name__}",
            "context": context
        }
=======
        user_message=f"Operation failed: {str(exc)}",
        technical_details=f"Error: {type(exc).__name__}",
        context=context
>>>>>>> c83bf20d4036189859a3421f360826da42cedb0a
    )
```

#### Streaming Integration Pattern
```python
from framework.infrastructure import get_streamer

async def execute_with_streaming(state: AgentState) -> Dict[str, Any]:
    """Framework streaming pattern for long-running operations"""
    
    streamer = get_streamer("bolt", "operation_name", state)
    
    # Initial status
    streamer.status("Initializing operation...")
    
    # Progress updates
    for i, step in enumerate(operation_steps):
        streamer.status(f"Executing step {i+1}/{len(operation_steps)}: {step}")
        await execute_step(step)
    
    # Success notification
    streamer.status("Operation completed successfully!")
    
    return context_updates
```

#### Context Management Pattern
```python
from framework.state import StateManager

def manage_context_lifecycle(state: AgentState) -> Dict[str, Any]:
    """Framework context management best practices"""
    
    # Retrieve existing context
    previous_context = StateManager.get_context(
        state,
        registry.context_types.MOTOR_POSITION,
        "previous_position"
    )
    
    # Perform operation using previous context
    if previous_context:
        new_result = build_on_previous_result(previous_context)
    else:
        new_result = perform_initial_operation()
    
    # Store new context
    context_updates = StateManager.store_context(
        state,
        registry.context_types.MOTOR_POSITION,
        "current_position",
        new_result
    )
    
    return context_updates
```

### 3. Framework Testing Strategies

#### Unit Testing with Framework Mocks
```python
import pytest
from framework.testing import create_mock_state, MockStreamer

@pytest.mark.asyncio
async def test_capability_execution():
    """Test capability using framework testing utilities"""
    
    # Create framework-compatible mock state
    mock_state = create_mock_state()
    
    # Execute capability
    result = await MotorPositionReadCapability.execute(mock_state)
    
    # Verify framework integration
    assert "context" in result
    assert result["context"]["motor_position"]["angle"] > 0
    
    # Verify streaming was used
    assert MockStreamer.was_called("motor_position_read")
```

#### Integration Testing with Framework
```python
from framework.testing import FrameworkTestCase

class TestBoltIntegration(FrameworkTestCase):
    """Framework-aware integration testing"""
    
    def setUp(self):
        super().setUp()
        self.app_config = self.load_test_config("bolt")
        self.mock_external_api()
    
    async def test_complete_workflow(self):
        """Test multi-capability workflow through framework"""
        
        # Execute workflow through framework
        conversation = [
            "What's the current position?",
            "Move to 90 degrees", 
            "Take a measurement"
        ]
        
        results = await self.execute_conversation(conversation)
        
        # Verify framework behavior
        self.assert_capabilities_called([
            "motor_position_read",
            "motor_position_set", 
            "detector_image_capture"
        ])
        
        self.assert_context_stored("MOTOR_POSITION")
        self.assert_streaming_messages_sent()
```

#### External System Mocking
```python
from unittest.mock import patch, MagicMock

class MockBoltAPI:
    """Framework-compatible external system mock"""
    
    def __init__(self):
        self.call_history = []
    
    def get_current_angle(self, motor: str) -> CurrentAngleReading:
        self.call_history.append(("get_current_angle", motor))
        return CurrentAngleReading(
            motor=motor,
            angle=45.0,
            condition="Mock reading - framework test",
            timestamp=datetime.now()
        )
    
    @property
    def was_called(self) -> bool:
        return len(self.call_history) > 0

# Use in tests
@patch('applications.bolt.bolt_api.BoltAPI', MockBoltAPI)
async def test_with_mocked_api():
    # Test capability with mocked external system
    pass
```

---

## 🛠️ Framework Troubleshooting

### Common Framework Integration Issues

#### 1. Capability Registration Problems

**Symptoms:**
- Capabilities not discovered by framework
- `CapabilityNotFound` errors in logs

**Diagnostics:**
```python
# Check registry registration
from applications.bolt.registry import BoltRegistryProvider

registry = BoltRegistryProvider()
capabilities = registry.get_capabilities()
print(f"Registered capabilities: {[c.name for c in capabilities]}")

# Verify module paths
import importlib
module = importlib.import_module("applications.bolt.capabilities.motor_position_read")
assert hasattr(module, "MotorPositionReadCapability")
```

**Solutions:**
1. **Verify Registry Provider**: Ensure `BoltRegistryProvider` is correctly configured
2. **Check Module Paths**: Validate capability module imports
3. **Framework Logs**: Enable debug logging for registration process

#### 2. Context Management Issues

**Symptoms:**
- Context data not persisting between capabilities
- Type validation errors in context classes

**Framework Debugging:**
```python
# Inspect context storage
from framework.state import StateManager

def debug_context_state(state: AgentState):
    """Debug framework context management"""
    context_keys = StateManager.get_all_context_keys(state)
    print(f"Available context keys: {context_keys}")
    
    for key in context_keys:
        context_data = StateManager.get_context(state, "MOTOR_POSITION", key)
        print(f"Context {key}: {context_data}")
```

**Solutions:**
1. **Context Type Registration**: Verify context classes are properly registered
2. **Pydantic Validation**: Check context class field definitions
3. **State Management**: Ensure proper context storage/retrieval patterns

#### 3. LLM Integration Problems

**Symptoms:**
- Capability routing failures
- Parameter extraction not working

**Framework Configuration Check:**
```python
# Verify LLM configuration
from framework.models import get_completion_model

def test_llm_connection():
    """Test framework LLM integration"""
    model = get_completion_model()
    response = model.complete("Test message")
    assert response is not None
```

**Solutions:**
```yaml
# Alternative LLM configurations for troubleshooting

# Option 1: Reduce model complexity
model:
  provider: "openai"
  model_name: "gpt-3.5-turbo"
  temperature: 0.0

# Option 2: Local testing
model:
  provider: "ollama"
  model_name: "mistral:7b"
  base_url: "http://localhost:11434"

# Option 3: Debug mode
debug:
  llm_requests: true
  capability_routing: true
```

#### 4. Streaming Integration Issues

**Symptoms:**
- No real-time feedback in UI
- Streaming messages not appearing

**Framework Streaming Debug:**
```python
from framework.infrastructure import get_streamer

def test_streaming_integration(state: AgentState):
    """Test framework streaming functionality"""
    streamer = get_streamer("bolt", "test_capability", state)
    
    # Test different message types
    streamer.status("Testing status message")
    streamer.info("Testing info message")
    streamer.error("Testing error message")
    
    # Verify streamer is properly configured
    assert streamer.application_name == "bolt"
    assert streamer.capability_name == "test_capability"
```
---

## 🚀 Extension Patterns


### 1. Framework Extensions

#### Enhanced Natural Language Processing
```python
@capability_node
class IntelligentScanPlanningCapability(BaseCapability):
    """AI-powered scan parameter optimization."""
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        # Analyze sample characteristics
        # Recommend optimal scan parameters
        # Predict data quality and acquisition time
        pass
```
---

## 📚 References and Documentation

### Framework Documentation
- **Alpha Berkeley Framework**: [Documentation](https://thellert.github.io/alpha_berkeley)
- **LangGraph Integration**: Native AI agent execution patterns
- **Context Management**: Type-safe data structures and access patterns

### Hardware Documentation
- **EPICS Control System**: [EPICS Documentation](https://epics.anl.gov/)
- **Galil Motion Control**: Motor controller programming guides
- **Allied Vision Cameras**: areaDetector integration documentation

### API References
- **FastAPI Framework**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **RESTful Design**: API endpoint specifications and usage
- **Error Handling**: Comprehensive error code documentation

### Scientific Applications
- **Photogrammetry**: Reconstruction algorithms and best practices
- **Beamline Operations**: Scientific experimental procedures
- **Data Management**: Research data lifecycle management

---
## 📋 Summary

The BOLT Beamline Agent represents a significant advancement in scientific instrument control, combining the power of modern AI with precision hardware control. This comprehensive system provides:

### **Key Achievements**
- **Natural Language Control**: Intuitive operation through conversational interfaces
- **Modular Architecture**: Extensible design for future enhancements
- **Robust Error Handling**: Intelligent retry and recovery mechanisms
- **Real-time Feedback**: Streaming status updates throughout operations
- **Framework Integration**: Full compatibility with Alpha Berkeley patterns

### **Multiple Approaches for Future Development**

#### **Approach 1: Incremental Enhancement**
**Best for**: Adding specific new capabilities without major architectural changes
- Add new hardware interfaces through the existing API layer
- Extend capabilities using the established framework patterns
- Minimal disruption to existing workflows
- Low risk, gradual improvement path

#### **Approach 2: Advanced AI Integration**
**Best for**: Leveraging machine learning for intelligent automation
- Implement predictive maintenance and failure detection
- Add intelligent scan parameter optimization
- Integrate computer vision for automated alignment
- Higher complexity but significant capability enhancement

#### **Approach 3: Ecosystem Integration**
**Best for**: Connecting BOLT with broader laboratory infrastructure
- LIMS integration for data management
- Analysis pipeline automation
- Remote collaboration capabilities
- Comprehensive laboratory digitization

### **Recommended Development Path**

For developers looking to extend BOLT, I recommend starting with **Approach 1** to understand the system thoroughly, then gradually incorporating elements from Approaches 2 and 3 based on specific research needs.

**Priority Order:**
1. **Immediate**: New hardware capabilities (sensors, actuators)
2. **Short-term**: Enhanced error recovery and diagnostic tools
3. **Medium-term**: AI-powered optimization and automation
4. **Long-term**: Full ecosystem integration and advanced analytics

This comprehensive documentation provides the foundation for understanding, operating, and extending the BOLT Beamline Agent system. The modular architecture and extensive examples make it straightforward for future developers to contribute meaningful enhancements while maintaining system reliability and user experience.

*For the most current information and updates, consult the Alpha Berkeley Framework documentation and community resources.*
