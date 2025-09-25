"""
Shared Context Classes for ALS Assistant Agent Capabilities

This module contains all context class definitions that can be shared between capabilities.
Context classes use Pydantic for automatic serialization and type safety.
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional, TYPE_CHECKING, ClassVar
from datetime import datetime

# Import the updated framework architecture
from framework.context.base import CapabilityContext
from framework.context.context_manager import recursively_summarize_data

# ===================================================================
# ==================== PYDANTIC CONTEXT CLASSES ==================
# ===================================================================

class PVAddresses(CapabilityContext):
    """
    Framework context for PV address finding capability results.
    
    This is the rich context object used throughout the framework for PV address data.
    It extends CapabilityContext to provide framework integration, UI methods, and
    state management capabilities.
    
    This class is architecturally separate from the service layer PVSearchResult DTO
    to maintain clean boundaries between service and framework layers.
    """
    CONTEXT_TYPE: ClassVar[str] = "PV_ADDRESSES"
    CONTEXT_CATEGORY: ClassVar[str] = "METADATA"
    
    pvs: List[str]  # List of found PV addresses
    description: str  # Description or additional information about the PVs
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description for LLM consumption."""
        key_ref = key_name if key_name else "key_name"
        return {
            "pvs": self.pvs,
            "total_available": len(self.pvs),
            "comments": self.description,
            "data_structure": "List of PV address strings",
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.pvs",
            "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.pvs[0] gives '{self.pvs[0] if self.pvs else 'PV_NAME'}'",
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """
        FOR HUMAN DISPLAY: Create readable summary for UI/debugging.
        Always customize for better user experience.
        """
        return {
            "type": "PV Addresses",
            "total_pvs": len(self.pvs),
            "pv_list": self.pvs,
            "description": self.description,
        }


class PVValue(BaseModel):
    """Individual PV value data - simple nested structure for Pydantic."""
    value: str
    timestamp: datetime  # Pydantic handles datetime serialization automatically
    units: str


class PVValues(CapabilityContext):
    """Result from PV value retrieval operation and context for downstream capabilities."""
    CONTEXT_TYPE: ClassVar[str] = "PV_VALUES"
    CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
    
    pv_values: Dict[str, PVValue]  # Clean structure - no DotDict needed
    
    @property
    def pv_count(self) -> int:
        """Number of PVs retrieved."""
        return len(self.pv_values)
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description for LLM consumption."""
        pvs_preview = list(self.pv_values.keys())[:3]
        example_pv = pvs_preview[0] if pvs_preview else "SR:DCCT"
        
        # Get example value from the PVValue object
        try:
            example_value = self.pv_values[example_pv].value if example_pv in self.pv_values else '400.5'
        except:
            example_value = '400.5'
        
        key_ref = key_name if key_name else "key_name"
        return {
            "pv_count": self.pv_count,
            "pvs": pvs_preview,
            "data_structure": "Dict[pv_name -> PVValue] where PVValue has .value, .timestamp, .units fields - IMPORTANT: use bracket notation for PV names (due to special characters like colons), but dot notation for fields",
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.pv_values['PV_NAME'].value (NOT ['value'])",
            "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.pv_values['{example_pv}'].value gives '{example_value}' (use .value not ['value'])",
            "available_fields": ["value", "timestamp", "units"],
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """
        FOR HUMAN DISPLAY: Create readable summary for UI/debugging.
        Always customize for better user experience.
        """
        pv_data = {}
        for pv_name, pv_info in self.pv_values.items():
            pv_data[pv_name] = {
                "value": pv_info.value,
                "timestamp": pv_info.timestamp,
                "units": pv_info.units
            }
        
        return {
            "type": "PV Values",
            "pv_data": pv_data,
        }


class ArchiverDataContext(CapabilityContext):
    """
    Structured context for archiver data capability results.
    
    This stores archiver data with datetime objects for full datetime functionality and consistency.
    """
    CONTEXT_TYPE: ClassVar[str] = "ARCHIVER_DATA"
    CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
    
    timestamps: List[datetime]  # List of datetime objects for full datetime functionality
    precision_ms: int  # Data precision in milliseconds
    time_series_data: Dict[str, List[float]]  # PV name -> time series values (aligned with timestamps)
    available_pvs: List[str]  # List of available PV names for intuitive filtering
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description of the archiver data structure."""
        total_points = len(self.timestamps)
        
        # Get example PV for demo purposes
        example_pv = self.available_pvs[0] if self.available_pvs else "SR:DCCT"
        example_value = self.time_series_data[example_pv][0] if self.available_pvs and self.time_series_data.get(example_pv) else 100.5
        
        key_ref = key_name if key_name else "key_name"
        start_time = self.timestamps[0]
        end_time = self.timestamps[-1]
        duration = end_time - start_time
        
        return {
            "total_points": total_points,
            "precision_ms": self.precision_ms,
            "pv_count": len(self.available_pvs),
            "available_pvs": self.available_pvs,
            "time_info": f"Data spans from {start_time} to {end_time} (duration: {duration})",
            "data_structure": "4 attributes: timestamps (list of datetime objects), precision_ms (int), time_series_data (dict of pv_name -> list of float values), available_pvs (list of PV names)",
            "CRITICAL_ACCESS_PATTERNS": {
                "get_pv_names": f"pv_names = context.{self.CONTEXT_TYPE}.{key_ref}.available_pvs",
                "get_pv_data": f"data = context.{self.CONTEXT_TYPE}.{key_ref}.time_series_data['PV_NAME']",
                "get_timestamps": f"timestamps = context.{self.CONTEXT_TYPE}.{key_ref}.timestamps",
                "get_single_value": f"value = context.{self.CONTEXT_TYPE}.{key_ref}.time_series_data['PV_NAME'][index]",
                "get_time_at_index": f"time = context.{self.CONTEXT_TYPE}.{key_ref}.timestamps[index]"
            },
            "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.time_series_data['{example_pv}'][0] gives {example_value}, context.{self.CONTEXT_TYPE}.{key_ref}.timestamps[0] gives datetime object",
            "datetime_features": "Full datetime functionality: arithmetic, comparison, formatting with .strftime(), timezone operations"
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """
        FOR HUMAN DISPLAY: Format data for response generation.
        Downsamples large datasets to prevent context window overflow.
        """
        max_samples = 10
        
        try:
            total_points = len(self.timestamps)
            
            # Create sample indices (start, middle, end)
            if total_points <= max_samples:
                sample_indices = list(range(total_points))
            else:
                # Include start, end, and evenly distributed middle points
                step = max(1, total_points // (max_samples - 2))
                sample_indices = [0] + list(range(step, total_points - 1, step))[:max_samples-2] + [total_points - 1]
                sample_indices = sorted(list(set(sample_indices)))  # Remove duplicates and sort
            
            # Sample timestamps
            sample_timestamps = [self.timestamps[i] for i in sample_indices]
            
            # Sample PV data
            pv_summary = {}
            for pv_name, values in self.time_series_data.items():
                sample_values = [values[i] for i in sample_indices]
                
                pv_summary[pv_name] = {
                    "sample_values": sample_values,
                    "sample_timestamps": sample_timestamps,
                    "statistics": {
                        "total_points": len(values),
                        "min_value": min(values),
                        "max_value": max(values),
                        "first_value": values[0],
                        "last_value": values[-1],
                        "mean_value": sum(values) / len(values)
                    }
                }
            
            return {
                "WARNING": "🚨 THIS IS DOWNSAMPLED ARCHIVER DATA - DO NOT USE FOR FINAL NUMERICAL ANSWERS! 🚨",
                "guidance": "For accurate analysis results, use ANALYSIS_RESULTS context instead of raw archiver data",
                "data_info": {
                    "total_points": total_points,
                    "precision_ms": self.precision_ms,
                    "time_range": {
                        "start": self.timestamps[0] if self.timestamps else None,
                        "end": self.timestamps[-1] if self.timestamps else None
                    },
                    "downsampling_info": f"Showing {len(sample_indices)} sample points out of {total_points} total points"
                },
                "pv_data": pv_summary,
                "IMPORTANT_NOTE": "Use this only for understanding data structure. For analysis results, request ANALYSIS_RESULTS context."
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error downsampling archiver data: {e}")
            return {
                "ERROR": f"Failed to downsample archiver data: {str(e)}",
                "WARNING": "Could not process archiver data - use ANALYSIS_RESULTS instead"
            }

class AnalysisResultsContext(CapabilityContext):
    """
    Dynamic context for data analysis capability results.
    
    This provides a flexible container for analysis results with a standardized structure
    instead of dynamic field assignment that breaks type safety.
    """
    CONTEXT_TYPE: ClassVar[str] = "ANALYSIS_RESULTS"
    CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
    
    results: Dict[str, Any]  # All analysis results go in this standardized container
    expected_schema: Optional[Dict[str, Any]] = None  # Schema documentation for the results
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description for LLM consumption."""
        key_ref = key_name if key_name else "key_name"
        return {
            "available_fields": list(self.results.keys()),
            "schema": self.expected_schema,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.results['field_name']",
            "format": "All analysis results are in the .results dictionary - access them directly via dot notation",
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """
        FOR HUMAN DISPLAY: Create readable summary for UI/debugging.
        Always customize for better user experience.
        """
        # Extract all dynamic fields for user display
        user_data = {}
        for field_name, value in self.results.items():
            # Use the shared recursive summarization function
            user_data[field_name] = recursively_summarize_data(value)
        
        return {
            "type": "Analysis Results",
            "results": user_data,
            "field_count": len(user_data),
            "available_fields": list(user_data.keys())
        }


class VisualizationResultsContext(CapabilityContext):
    """
    Dynamic context for data visualization capability results.
    
    This provides a flexible container for visualization results with a standardized structure.
    """
    CONTEXT_TYPE: ClassVar[str] = "VISUALIZATION_RESULTS"
    CONTEXT_CATEGORY: ClassVar[str] = "OUTPUTS"
    
    results: Dict[str, Any]  # All visualization results go here
    expected_schema: Optional[Dict[str, Any]] = None  # Schema documentation
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description for LLM consumption."""
        key_ref = key_name if key_name else "key_name"
        return {
            "available_fields": list(self.results.keys()),
            "schema": self.expected_schema,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.results['field_name']",
            "format": "All visualization results are in the .results dictionary",
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """
        FOR HUMAN DISPLAY: Create readable summary for UI/debugging.
        Always customize for better user experience.
        """
        # Extract all dynamic fields for user display
        user_data = {}
        for field_name, value in self.results.items():
            # Use the shared recursive summarization function
            user_data[field_name] = recursively_summarize_data(value)
        
        return {
            "type": "Visualization Results",
            "results": user_data,
            "field_count": len(user_data),
            "available_fields": list(user_data.keys())
        }


class OperationResultsContext(CapabilityContext):
    """
    Dynamic context for machine operations capability results.
    
    This provides a flexible container for operation results with a standardized structure.
    """
    CONTEXT_TYPE: ClassVar[str] = "OPERATION_RESULTS"
    CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
    
    results: Dict[str, Any]  # All operation results go here
    expected_schema: Optional[Dict[str, Any]] = None  # Schema documentation
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description for LLM consumption."""
        key_ref = key_name if key_name else "key_name"
        operation_type = self.results.get('operation_type', 'unknown')
        success = self.results.get('success', False)
        
        return {
            "operation_type": operation_type,
            "success": success,
            "available_fields": list(self.results.keys()),
            "schema": self.expected_schema,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.results['field_name']",
            "format": "All operation results are in the .results dictionary",
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """
        FOR HUMAN DISPLAY: Create readable summary for UI/debugging.
        Always customize for better user experience.
        """
        # Extract all dynamic fields for user display
        user_data = {}
        operation_type = "unknown"
        success = False
        
        for field_name, value in self.results.items():
            if field_name == 'operation_type':
                operation_type = value
            elif field_name == 'success':
                success = value
            else:
                # Use the shared recursive summarization function
                user_data[field_name] = recursively_summarize_data(value)
        
        return {
            "type": "Operation Results",
            "operation_type": operation_type,
            "success": success,
            "results": user_data,
            "field_count": len(user_data),
            "available_fields": list(user_data.keys())
        }


class LauncherResultsContext(CapabilityContext):
    """
    Framework context for live monitoring launcher capability results.
    
    This context stores the results of launching monitoring applications like Phoebus Data Browser.
    It provides launch URIs and configuration details for external application integration.
    """
    CONTEXT_TYPE: ClassVar[str] = "LAUNCHER_RESULTS"
    CONTEXT_CATEGORY: ClassVar[str] = "RESULTS"
    
    launch_uri: str  # URI to launch the application
    command_name: str  # Human-readable command name
    command_description: str  # Description of what will be launched
    success: bool  # Whether the launcher configuration was successful
    pv_count: int  # Number of PVs configured for monitoring
    monitoring_type: str  # Type of monitoring (e.g., "live_data_browser")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Rich description for LLM consumption."""
        key_ref = key_name if key_name else "key_name"
        return {
            "launch_uri": self.launch_uri,
            "command_name": self.command_name,
            "command_description": self.command_description,
            "success": self.success,
            "pv_count": self.pv_count,
            "monitoring_type": self.monitoring_type,
            "data_structure": "Launcher configuration with URI and metadata",
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.launch_uri",
            "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.launch_uri provides the application launch URI",
        }
    
    def get_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Human-readable summary of launcher results."""
        return {
            "type": "Launcher Results",
            "command": self.command_name,
            "status": "Ready to launch" if self.success else "Configuration failed",
            "pv_count": self.pv_count,
            "monitoring_type": self.monitoring_type,
        }


