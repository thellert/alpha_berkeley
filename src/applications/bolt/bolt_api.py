"""
Mock Bolt API based on Mock Weather API for Hello World Weather Tutorial.
"""
import random, requests #added requests
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CurrentAngleReading:
    """Structured data model for current weather conditions.
    """
    motor: str
    angle: float  # We'll be using this as motor angle
    condition: str
    timestamp: datetime

@dataclass
class CurrentMoveMotorReading:
    """Structured data model for move motor conditions."""

    motor: str
    angle: float  # We'll be using this as motor angle
    condition: str
    timestamp: datetime

@dataclass
class CurrentTakeMeasurementReading:
    """Structured data model for move motor conditions."""

    condition: str
    timestamp: datetime

class BoltAPI:
    """Mock weather service for Hello World Weather tutorial application.
    """
    
    # City-specific weather pattern configuration
    MOTOR_DATA = {
        "DMC01:A": {}
    }
    """Weather pattern configuration for supported cities.
    """

    FASTAPI_URL = "http://198.128.193.130:8000"

    def get_current_angle(self, motor: str) -> CurrentAngleReading:
        """Retrieve current weather conditions for the specified location.
        """
        
        get_angle_API = self.FASTAPI_URL + "/get_angle"

        # Normalize location name for consistent matching
        motor = motor.title()
        if motor not in self.MOTOR_DATA:
            # Default to San Francisco if city not found to ensure consistent tutorial behavior
            motor = "DMC01:A"
                
        try:
            #response = requests.get(str(self.FASTAPI_URL), timeout= 5)
            response = requests.get(get_angle_API, timeout=5, proxies={"http": None, "https": None})

            data = response.text
            angle_str = data.split()
            angle_str = angle_str[-1][:-1]  #Remove last character from said string
            
            angle_res = angle_str

            return CurrentAngleReading(
                motor=motor,
                angle=float(angle_res),
                condition="Remote Angle Reading",
                timestamp=datetime.now()
            )
        except Exception as e:
            return CurrentAngleReading(
                motor=motor,
                angle=-1.0,
                condition=f"Error: {str(e)}",
                timestamp=datetime.now()
            )

    def move_motor(self, motor: str, move_amount: str, flag: int) -> CurrentMoveMotorReading:
        """Retrieve current weather conditions for the specified location.
        """
        print(move_amount)
        move_motor_api = f"{self.FASTAPI_URL}/move_motor/{move_amount}/{flag}"

        # Normalize location name for consistent matching
        motor = motor.title()
        if motor not in self.MOTOR_DATA:
            # Default to San Francisco if city not found to ensure consistent tutorial behavior
            motor = "DMC01:A"
                
        try:
            #response = requests.get(str(self.FASTAPI_URL), timeout= 5)
            response = requests.get(move_motor_api, timeout=5, proxies={"http": None, "https": None})

            return CurrentMoveMotorReading(
                motor=motor,
                angle=float(move_amount),
                condition="Remote Movement Succeeded",
                timestamp=datetime.now()
            )
        except Exception as e:
            print(str(e))
            return CurrentMoveMotorReading(
                motor=motor,
                angle=-1.0,
                condition=f"Error: {str(e)}",
                timestamp=datetime.now()
            )


# Global API instance for application-wide weather data access
bolt_api = BoltAPI()
