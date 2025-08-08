"""
Wind Turbine Context Classes

This module contains all context class definitions for the wind turbine monitoring agent.
Context classes use Pydantic for automatic serialization and type safety.
"""

from typing import Dict, Any, Optional, List, ClassVar
from datetime import datetime
from pydantic import Field
from framework.context.base import CapabilityContext


class TurbineDataContext(CapabilityContext):
    """Historical turbine performance data."""
    CONTEXT_TYPE: ClassVar[str] = "TURBINE_DATA"
    CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
    
    timestamps: List[datetime] = Field(description="List of timestamps for data points")
    turbine_ids: List[str] = Field(description="List of turbine IDs")
    power_outputs: List[float] = Field(description="List of power outputs in MW (megawatts)")
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
    
    knowledge_data: Dict[str, Any] = Field(default_factory=dict, description="Retrieved knowledge as flat dictionary (no nested structures)")
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
 