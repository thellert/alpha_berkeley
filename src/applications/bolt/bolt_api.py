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
import time
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

@dataclass
class CurrentPlyQualityReading:
    """Structured data model for PLY quality assessment execution results."""
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
    #FASTAPI_URL = "host.docker.internal"

    FASTAPI_URL = "localhost"
    #Working with real data captured from tiled, with a delay to wait if the run is not complete
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

            # Use requests.post() correctly
            result = subprocess.run(cmd, capture_output=True, text=True)
            product = json.loads(result.stdout)
            
            item_uid = (product["item"]["item_uid"])

            try:
                current_pos = 0
                while(current_pos != "run_list"):
                    # Test GET method for history
                    queue_url = f"http://{self.FASTAPI_URL}:8003/api/re/runs/active"
                    
                    # Use GET method (not POST)
                    cmd = [
                        "curl",
                        "-X", "GET",  # Changed from POST to GET
                        queue_url,
                        "-H", "accept: application/json",
                        "-H", "Authorization: Apikey test"
                    ]   

                    result = subprocess.run(cmd, capture_output=True, text=True)
                    history_data = json.loads(result.stdout)
                    for item in history_data:
                        current_pos = item
                    time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")

            try:
                # Test GET method for history
                queue_url = f"http://{self.FASTAPI_URL}:8003/api/history/get"
                
                # Use GET method (not POST)
                cmd = [
                    "curl",
                    "-X", "GET",  # Changed from POST to GET
                    queue_url,
                    "-H", "accept: application/json",
                    "-H", "Authorization: Apikey test"
                ]   

                result = subprocess.run(cmd, capture_output=True, text=True)
                history_data = json.loads(result.stdout)

                for item in history_data["items"]:
                    if item["item_uid"] == item_uid:
                        run_id = (item["result"]["run_uids"][0])
                        break

            except Exception as e:
                print(f"Error: {e}")
            

            from tiled.client import from_uri
            tiled_server_url = "http://localhost:8000"
            tiled_api_key = "ca6ae384c9f944e1465176b7e7274046b710dc7e2703dc33369f7c900d69bd64"
            # Connect to the Tiled server
            tiled_client = from_uri(
                tiled_server_url,
                api_key=tiled_api_key
            )

            run_data = tiled_client["cd3f4195-1132-4e0d-8cf4-cfb402fee720"]
            angle = run_data.metadata['start']['angle_degrees']
                        
            return CurrentAngleReading(
                motor=motor,
                angle=float(angle),
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
                        "name": "camera_acquire",
                        "args": [],
                        "kwargs": {
                            "camera": "camera",
                            "motor": "rotation_motor",
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

            return CurrentTakeCaptureReading(
                condition="Remote Movement Succeeded",
                timestamp=datetime.now()
            )
        except Exception as e:
            print(str(e))
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

    def analyze_ply_quality(self, input_folder: str) -> CurrentPlyQualityReading: 
        """PLY quality assessment."""
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
                            "name": "analyze_ply_quality",
                            "args": [],
                            "kwargs": {
                                "image_dir": "Banana"
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

            return CurrentPlyQualityReading(
                condition="Remote PLY Quality Assessment Completed",
                timestamp=datetime.now()
            )
        except Exception as e:
            return CurrentPlyQualityReading(
                condition=f"Error: {str(e)}",
                timestamp=datetime.now()
            )

bolt_api = BoltAPI()
