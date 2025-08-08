"""
Mock APIs for Wind Turbine Monitoring

Simulate external services for development and testing.
"""

import random
import asyncio
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