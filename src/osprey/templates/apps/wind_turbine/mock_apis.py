"""
Mock APIs for Wind Turbine Monitoring

Simulate external services for development and testing.
"""

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
        # Each turbine has different efficiency characteristics designed around knowledge thresholds
        # Knowledge thresholds: Excellent >85%, Good 75-85%, Maintenance <75%, Critical <70%
        self.turbine_efficiency_factors = {
            "T-001": 0.90,   # Excellent: above 85% threshold
            "T-002": 0.72,   # Below maintenance: under 75% threshold  
            "T-003": 0.88,   # Excellent: above 85% threshold
            "T-004": 0.65,   # Critical: under 70% economic threshold
            "T-005": 0.82,   # Good: between 75-85% thresholds
        }

    async def get_historical_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get historical turbine data for time range."""
        readings = []

        # Calculate realistic data points based on time range
        # Generate data every hour for realistic turbine monitoring
        total_hours = int((end_time - start_time).total_seconds() / 3600)
        num_points = min(max(total_hours, 24), 500)  # At least 24 points, max 500 for performance
        time_delta = (end_time - start_time) / num_points

        for i in range(num_points):
            timestamp = start_time + (time_delta * i)
            base_wind = get_wind_speed(timestamp)

            for turbine_id in self.turbine_ids:
                # Calculate theoretical power output based on wind speed
                # Simplified linear power curve: wind_speed * 0.18, capped at 2.5MW
                theoretical_power = min(2.5, base_wind * 0.18)

                # Apply turbine-specific efficiency factor
                efficiency_factor = self.turbine_efficiency_factors[turbine_id]
                final_power = theoretical_power * efficiency_factor

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

        # Calculate realistic data points based on time range
        # Weather data should match turbine data collection intervals
        total_hours = int((end_time - start_time).total_seconds() / 3600)
        num_points = min(max(total_hours, 24), 500)  # Match turbine data points exactly
        time_delta = (end_time - start_time) / num_points

        for i in range(num_points):
            timestamp = start_time + (time_delta * i)
            readings.append({
                "timestamp": timestamp,
                "wind_speed": round(get_wind_speed(timestamp), 1)
            })

        return readings


# Global instances  
turbine_api = TurbineSensorAPI()
weather_api = WeatherAPI() 