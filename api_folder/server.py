from fastapi import FastAPI, HTTPException
import os
import subprocess
import config

app = FastAPI()

env = "python"

@app.get("/move_motor/{amount}/{relative}")
def move_motor(amount: float, relative: int = 0):
    """
    Move motor to a position or by a relative amount with retry verification
    
    Parameters:
    - amount: Motor position (if relative=0) or relative movement amount (if relative=1)
    - relative: Flag (0 or 1) to determine movement type
      - 0 (default): Move to absolute position
      - 1: Move by relative amount from current position
    """
    import time
    
    try:
        target_position = None
        
        if relative == 1:
            # Relative movement - get current position first
            caget_path = config.get_caget_path()
            cmd = [caget_path, config.MOTOR_PV]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                value_str = result.stdout.strip().split()[-1]
                current_position = float(value_str)
                target_position = current_position + amount
            else:
                raise HTTPException(status_code=500, detail=f"Failed to get current motor position: {result.stderr}")
        else:
            # Absolute movement
            target_position = amount
        
        # Retry logic for motor movement
        caput_path = config.get_caput_path()
        caget_path = config.get_caget_path()
        
        for attempt in range(1, config.MOTOR_MAX_RETRIES + 1):
            print(f"Motor movement attempt {attempt}/{config.MOTOR_MAX_RETRIES} - Target: {target_position}")
            
            # Send move command
            cmd = [caput_path, config.MOTOR_PV, str(target_position)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Attempt {attempt}: Failed to send motor command: {result.stderr}")
                if attempt == config.MOTOR_MAX_RETRIES:
                    raise HTTPException(status_code=500, detail=f"Failed to move motor after {config.MOTOR_MAX_RETRIES} attempts: {result.stderr}")
                time.sleep(config.MOTOR_RETRY_DELAY)
                continue
            
            # Wait for motor to settle
            time.sleep(config.MOTOR_SETTLE_TIME)
            
            # Verify position
            verify_cmd = [caget_path, config.MOTOR_PV]
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
            
            if verify_result.returncode == 0:
                value_str = verify_result.stdout.strip().split()[-1]
                actual_position = float(value_str)
                position_error = abs(actual_position - target_position)
                
                print(f"Attempt {attempt}: Target={target_position}, Actual={actual_position}, Error={position_error}")
                
                if position_error <= config.MOTOR_POSITION_TOLERANCE:
                    # Success! Position matches within tolerance
                    degree_angle = actual_position * config.MOTOR_RATIO
                    movement_type = "relative" if relative == 1 else "absolute"
                    
                    return {
                        "message": f"Motor moved successfully ({movement_type} movement)",
                        "target_position": target_position,
                        "actual_position": actual_position,
                        "position_error": position_error,
                        "target_angle_degrees": degree_angle,
                        "movement_amount": amount,
                        "movement_type": movement_type,
                        "attempts_required": attempt
                    }
                else:
                    print(f"Attempt {attempt}: Position error {position_error} exceeds tolerance {config.MOTOR_POSITION_TOLERANCE}")
                    if attempt < config.MOTOR_MAX_RETRIES:
                        time.sleep(config.MOTOR_RETRY_DELAY)
                        continue
                    else:
                        raise HTTPException(
                            status_code=500, 
                            detail=f"Motor position verification failed after {config.MOTOR_MAX_RETRIES} attempts. "
                                   f"Target: {target_position}, Actual: {actual_position}, Error: {position_error}"
                        )
            else:
                print(f"Attempt {attempt}: Failed to verify motor position: {verify_result.stderr}")
                if attempt < config.MOTOR_MAX_RETRIES:
                    time.sleep(config.MOTOR_RETRY_DELAY)
                    continue
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to verify motor position after {config.MOTOR_MAX_RETRIES} attempts")
    
    except Exception as e:
        print(f"Error moving motor: {e}")
        raise HTTPException(status_code=500, detail=f"Error moving motor: {str(e)}")

@app.get("/take_measurement")
def acquire_image():
    """Take a measurement at the current motor position using papermill"""
    try:
        # Get current motor position
        caget_path = config.get_caget_path()
        cmd = [caget_path, config.MOTOR_PV]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            value_str = result.stdout.strip().split()[-1]
            current_angle = float(value_str)
        else:
            raise HTTPException(status_code=500, detail=f"Failed to get current motor position: {result.stderr}")
        
        current_angle = current_angle * config.MOTOR_RATIO
        # Execute measurement using papermill with current angle
        cmd = [
            "papermill", 
            "take_measurement.ipynb", 
            "output_measurement.ipynb",
            "-p", "angle", str(current_angle)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"message": f"Measurement successfully taken at current angle {current_angle}", "output_notebook": "output_measurement.ipynb"}
        else:
            raise HTTPException(status_code=500, detail=f"Measurement failed: {result.stderr}")

    except Exception as e:
        print(f"Error taking measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Error taking measurement: {str(e)}")
    
@app.get("/get_angle")
def get_angle():
    """Get the current motor angle"""
    try:
        # Get the current angle
        caget_path = config.get_caget_path()
        cmd = [caget_path, config.MOTOR_PV]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            value_str = result.stdout.strip().split()[-1]
            motor_position = float(value_str)
            angle_degrees = motor_position * config.MOTOR_RATIO
            
            print("Running!")
            return f"Current motor angle: {angle_degrees}"
        else:
            raise HTTPException(status_code=500, detail=f"Failed to get angle value: {result.stderr}")

    except Exception as e:
        print(f"Error getting current angle: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting current angle: {str(e)}")

@app.get("/run_scan/{start_angle}/{end_angle}/{num_projections}/{save_dir}")
def run_scan_full(start_angle: float, end_angle: float, num_projections: int, save_dir: str):
    """Run a full tomography scan with all parameters specified"""
    try:
        # Convert from degrees to motor positions
        start_motor_pos = float(start_angle) / config.MOTOR_RATIO
        end_motor_pos = float(end_angle) / config.MOTOR_RATIO
        num_projections = int(num_projections)
        
        print(f"Running tomography scan from {start_angle} to {end_angle} degrees with {num_projections} projections, saving to {save_dir}")

        cmd = [env, 'run_tomography_scan.py', str(start_motor_pos), str(end_motor_pos), str(num_projections), str(save_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Scan failed: {result.stderr}")
        
        return {
            "message": f"Completed tomography scan with {num_projections} projections from {start_angle} to {end_angle} degrees",
            "start_angle_deg": start_angle,
            "end_angle_deg": end_angle,
            "num_projections": num_projections,
            "save_directory": save_dir,
            "uncropped_path": f'/home/user/tmpData/AI_scan/{save_dir}/uncropped_images/',
            "cropped_path": f'/home/user/tmpData/AI_scan/{save_dir}/images/'
        }

    except Exception as e:
        print(f"Error running scan: {e}")
        raise HTTPException(status_code=500, detail=f"Error running scan: {str(e)}")
    
@app.get("/run_scan/{start_angle}/{end_angle}/{num_projections}/")
def run_scan_3(start_angle: float, end_angle: float, num_projections: int):
    """Run tomography scan with start/end angles and number of projections (uses default save directory)"""
    return run_scan_full(start_angle, end_angle, num_projections, config.DEFAULT_SCAN_PARAMS['save_dir'])

@app.get("/run_scan/{start_angle}/{end_angle}/")
def run_scan_2(start_angle: float, end_angle: float):
    """Run tomography scan with start/end angles (uses default projections and save directory)"""
    return run_scan_full(
        start_angle, 
        end_angle, 
        config.DEFAULT_SCAN_PARAMS['num_projections'], 
        config.DEFAULT_SCAN_PARAMS['save_dir']
    )

@app.get("/run_scan/{num_projections}/")
def run_scan_1(num_projections: int):
    """Run tomography scan with specified number of projections (uses default angles and save directory)"""
    return run_scan_full(
        config.DEFAULT_SCAN_PARAMS['start_angle'], 
        config.DEFAULT_SCAN_PARAMS['end_angle'], 
        num_projections, 
        config.DEFAULT_SCAN_PARAMS['save_dir']
    )
    
@app.get("/reconstruction/{file_name}/")
def reconstruction(file_name: str):
    """Run reconstruction on specified dataset"""
    try:
        print(f"Running reconstruction on {file_name}")

        cmd = [env, 'reconstruction.py', file_name]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Reconstruction failed: {result.stderr}")
        else:
            return {"message": f"Reconstruction succeeded for {file_name}"}
            
    except Exception as e:
        print(f"Error running reconstruction: {e}")
        raise HTTPException(status_code=500, detail=f"Error running reconstruction: {str(e)}")


