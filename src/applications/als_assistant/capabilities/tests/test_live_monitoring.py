"""
Test Live Monitoring Capability

Basic integration tests to validate the live monitoring capability works correctly
with the framework and can generate proper launcher configurations.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from applications.als_assistant.capabilities.live_monitoring import LiveMonitoringCapability
from applications.als_assistant.context_classes import PVAddresses, LauncherResultsContext
from framework.state import AgentState
from framework.state import StateManager


@pytest.fixture
def mock_state():
    """Create a mock AgentState for testing."""
    state = {
        'execution_plan': {
            'current_step_index': 0,
            'steps': [{
                'context_key': 'test_live_monitor',
                'capability': 'live_monitoring',
                'task_objective': 'Launch live monitoring for beam current',
                'inputs': [{'PV_ADDRESSES': 'beam_current_pvs'}]
            }]
        },
        'capability_context_data': {
            'PV_ADDRESSES': {
                'beam_current_pvs': PVAddresses(
                    pvs=['SR:DCCT', 'SR:BSC:HLC:current'],
                    description='Beam current related PVs'
                )
            }
        }
    }
    return state


@pytest.mark.asyncio
async def test_live_monitoring_capability_basic_execution(mock_state):
    """Test basic execution of live monitoring capability."""
    
    # Mock the launcher service to return a successful result
    mock_launcher_result = Mock()
    mock_launcher_result.success = True
    mock_launcher_result.launch_uri = 'myapp://launch_tool/phoebus%20-resource%20/path/to/config.plt'
    mock_launcher_result.command_name = 'Launch Data Browser: Beam Current Monitor'
    mock_launcher_result.command_description = 'Launches Data Browser for live beam current monitoring'
    mock_launcher_result.error_message = None
    
    # Mock the launcher service
    with patch('applications.als_assistant.capabilities.live_monitoring.LauncherService') as mock_launcher_class:
        mock_launcher_instance = mock_launcher_class.return_value
        mock_launcher_instance.execute = AsyncMock(return_value=mock_launcher_result)
        
        # Mock configuration
        with patch('applications.als_assistant.capabilities.live_monitoring.get_full_configuration') as mock_config:
            mock_config.return_value = {'test': 'config'}
            
            # Execute the capability
            capability = LiveMonitoringCapability()
            result = await capability.execute(mock_state)
            
            # Verify the result structure
            assert 'capability_context_data' in result
            assert 'LAUNCHER_RESULTS' in result['capability_context_data']
            assert 'test_live_monitor' in result['capability_context_data']['LAUNCHER_RESULTS']
            
            # Verify the launcher context was created correctly
            launcher_context = result['capability_context_data']['LAUNCHER_RESULTS']['test_live_monitor']
            assert isinstance(launcher_context, LauncherResultsContext)
            assert launcher_context.success == True
            assert launcher_context.pv_count == 2
            assert launcher_context.monitoring_type == 'live_data_browser'
            assert 'myapp://' in launcher_context.launch_uri


@pytest.mark.asyncio
async def test_live_monitoring_missing_pv_addresses(mock_state):
    """Test that missing PV addresses raises appropriate error."""
    
    # Remove PV addresses from state
    mock_state['capability_context_data']['PV_ADDRESSES'] = {}
    
    capability = LiveMonitoringCapability()
    
    # Should raise PVDependencyError
    with pytest.raises(Exception) as exc_info:
        await capability.execute(mock_state)
    
    # Verify it's the right type of error
    assert "PV addresses" in str(exc_info.value)


def test_live_monitoring_error_classification():
    """Test error classification for different error types."""
    from applications.als_assistant.capabilities.live_monitoring import (
        PVDependencyError, LauncherServiceError, LiveMonitoringError
    )
    
    capability = LiveMonitoringCapability()
    
    # Test PV dependency error
    pv_error = PVDependencyError("No PV addresses available")
    classification = capability.classify_error(pv_error, {})
    assert classification.severity.name == "REPLANNING"
    assert "PV addresses" in classification.user_message
    
    # Test launcher service error
    launcher_error = LauncherServiceError("Launcher service failed")
    classification = capability.classify_error(launcher_error, {})
    assert classification.severity.name == "RETRIABLE"
    assert "Launcher service" in classification.user_message
    
    # Test generic error
    generic_error = Exception("Unknown error")
    classification = capability.classify_error(generic_error, {})
    assert classification.severity.name == "RETRIABLE"


def test_orchestrator_guide_creation():
    """Test that orchestrator guide is properly created."""
    capability = LiveMonitoringCapability()
    guide = capability._create_orchestrator_guide()
    
    assert guide is not None
    assert "live_monitoring" in guide.instructions
    assert "real-time monitoring" in guide.instructions.lower()
    assert "live monitoring vs historical analysis" in guide.instructions.lower()
    assert len(guide.examples) >= 2
    assert guide.priority == 25


def test_classifier_guide_creation():
    """Test that classifier guide distinguishes live monitoring from other tasks."""
    capability = LiveMonitoringCapability()
    classifier = capability._create_classifier_guide()
    
    assert classifier is not None
    assert len(classifier.examples) >= 10
    
    # Check for positive examples
    positive_examples = [ex for ex in classifier.examples if ex.result == True]
    assert len(positive_examples) >= 4
    
    # Check for negative examples  
    negative_examples = [ex for ex in classifier.examples if ex.result == False]
    assert len(negative_examples) >= 6
    
    # Verify distinction between live monitoring and historical analysis
    historical_examples = [ex for ex in negative_examples if 'historical' in ex.reason.lower() or 'yesterday' in ex.query.lower()]
    assert len(historical_examples) >= 2


if __name__ == "__main__":
    pytest.main([__file__])
