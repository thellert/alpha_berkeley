"""
BOLT Beamline API Interface.

Provides interface to BOLT imaging beamline hardware systems
including motor control, detector imaging, and photogrammetry operations.
"""
import random
import requests #added requests
from datetime import datetime
from dataclasses import dataclass
import subprocess

@dataclass
class CurrentAngleReading:
    """Structured data model for motor angular position readings.
    """
    motor: str
    angle: float  # We'll be using this as motor angle
    condition: str
    timestamp: datetime

@dataclass
class CurrentMoveMotorReading:
    """Structured data model for motor movement operation results."""
    motor: str
    angle: float  # Final motor angle position
    condition: str
    timestamp: datetime

@dataclass
class CurrentTakeCaptureReading:
    """Structured data model for detector image capture results."""
    condition: str
    timestamp: datetime

@dataclass
class CurrentRunScanReading:
    """Structured data model for photogrammetry scan execution results."""
    condition: str
    timestamp: datetime

@dataclass
class CurrentReconstructObjectReading:
    """Structured data model for reconstruction from folder execution results."""
    condition: str
    timestamp: datetime

class BoltAPI:
    """BOLT beamline hardware interface.
    
    Provides interface to BOLT imaging beamline systems including
    motor control, detector operations, and photogrammetry scan coordination.
    """
    
    # Motor configuration
    MOTOR_DATA = {
        "DMC01:A": {}
    }
    """Motor configuration for BOLT beamline motors."""

    #For WebUI Use
    FASTAPI_URL = "host.docker.internal"

    #FASTAPI_URL = "localhost"

    def get_current_angle(self, motor: str) -> CurrentAngleReading:
        """Retrieve current angular position of the specified motor."""
        
        # Normalize motor name for consistent matching
        motor = motor.title()
        if motor not in self.MOTOR_DATA:
            # Default to DMC01:A if motor not found
            motor = "DMC01:A"
                
        try:
            """Get motor values"""
            import json
            
            # Use the configurable FASTAPI_URL
            queue_url = f"http://{self.FASTAPI_URL}:8003/api/queue/item/execute"
            
            cmd = [
                "curl",
                "-X", "POST",
                queue_url,
                "-H", "accept: application/json",
                "-H", "Authorization: Apikey test",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "item": {
                        "name": "get_angle",
                        "args": [],
                        "kwargs": {"motor": "rotation_motor"},
                        "item_type": "plan",
                        "user": "UNAUTHENTICATED_SINGLE_USER",
                        "user_group": "primary",
                    }
                }),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            print("Return code:", result.returncode)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
            angle_res = 0

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

    def move_motor(self, motor: str, move_amount: str) -> CurrentMoveMotorReading:
        """Move motor to specified position (absolute or relative based on flag).
        """
        move_motor_api = f"{self.FASTAPI_URL}/move_motor/{move_amount}/"
        # Normalize motor name for consistent matching
        motor = motor.title()
        if motor not in self.MOTOR_DATA:
            # Default to DMC01:A if motor not found
            motor = "DMC01:A"
                
        try:
            import json
            
            # Use the configurable FASTAPI_URL
            queue_url = f"http://{self.FASTAPI_URL}:8003/api/queue/item/execute"
        
            cmd = [
                "curl",
                "-X", "POST",
                queue_url,
                "-H", "accept: application/json",
                "-H", "Authorization: Apikey test",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "item": {
                        "name": "move_motor",
                        "args": [],
                        "kwargs": {
                            "motor": "rotation_motor",
                            "position": float(move_amount)
                        },
                        "item_type": "plan",
                        "user": "UNAUTHENTICATED_SINGLE_USER",
                        "user_group": "primary"
                    }
                }),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            print("Return code:", result.returncode)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

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

    def take_capture(self) -> CurrentTakeCaptureReading:
        """Capture single image from detector.
        """
        
        take_capture_API = self.FASTAPI_URL + "/take_measurement"
                
        try:
            #response = requests.get(str(self.FASTAPI_URL), timeout= 5)
            response = requests.get(take_capture_API, timeout=5, proxies={"http": None, "https": None})

            data = response.text
            print(data)

            return CurrentTakeCaptureReading(
                condition="Remote Capture taken",
                timestamp=datetime.now()
            )
        except Exception as e:
            return CurrentTakeCaptureReading(
                condition=f"Error: {str(e)}",
                timestamp=datetime.now()
            )

    def run_photogrammetry_scan(self, start_angle: float, end_angle: float, num_projections: int, save_folder: str) -> CurrentRunScanReading:
        """Execute photogrammetry scan with multiple projections."""
        
        try:
            import json
            
            # Use the configurable FASTAPI_URL
            queue_url = f"http://{self.FASTAPI_URL}:8003/api/queue/item/execute"
            cmd = [
                "curl",
                "-X", "POST",
                queue_url,
                "-H", "accept: application/json",
                "-H", "Authorization: Apikey test",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "item": {
                        "name": "rotation_scan",
                        "args": [],
                        "kwargs": {
                            "start_angle": str(start_angle),
                            "end_angle": str(end_angle),
                            "num_points": str(num_projections),
                            "save_dir": str(save_folder)
                        },
                        "item_type": "plan",
                        "user": "UNAUTHENTICATED_SINGLE_USER",
                        "user_group": "primary"
                    }
                }),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            #print("Return code:", result.returncode)
            #print("STDOUT:", result.stdout)
            #print("STDERR:", result.stderr)

            return CurrentRunScanReading(
                condition="Remote Scan Completed",
                timestamp=datetime.now()
            )
        except Exception as e:
            return CurrentRunScanReading(
                condition=f"Error: {str(e)}",
                timestamp=datetime.now()
            )
# Global API instance for BOLT beamline hardware access
    def reconstruct_object(self, input_folder: str) -> CurrentReconstructObjectReading: 
        """Reconstruct object from folder."""
        try:
            import json
            
            # Use the configurable FASTAPI_URL
            queue_url = f"http://{self.FASTAPI_URL}:8003/api/queue/item/execute"
            cmd = [
                "curl",
                "-X", "POST",
                queue_url,
                "-H", "accept: application/json",
                "-H", "Authorization: Apikey test",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "item": {
                            "name": "reconstruct_object",
                            "args": [],
                            "kwargs": {
                                "image_dir": str(input_folder)
                            },
                            "item_type": "plan",
                            "user": "UNAUTHENTICATED_SINGLE_USER",
                            "user_group": "primary"
                        }
                }),
            ]   

            result = subprocess.run(cmd, capture_output=True, text=True)
            print("Return code:", result.returncode)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

            return CurrentReconstructObjectReading(
                condition="Remote Reconstruction Completed",
                timestamp=datetime.now()
            )
        except Exception as e:
            return CurrentReconstructObjectReading(
                condition=f"Error: {str(e)}",
                timestamp=datetime.now()
            )

bolt_api = BoltAPI()
