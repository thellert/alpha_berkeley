from ophyd import EpicsMotor, EpicsSignal
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector import AreaDetector, ADComponent, ImagePlugin, TIFFPlugin
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.areadetector.cam import CamBase
from bluesky import RunEngine
from databroker import Broker, temp
from bluesky.plans import scan, count
import bluesky.plan_stubs as bps
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image
import time, sys, os, subprocess
from collections import defaultdict
class PvaPlugin(PluginBase):
    _suffix = 'Pva1:'
    _plugin_type = 'NDPluginPva'
    _default_read_attrs = ['enable']
    _default_configuration_attrs = ['enable']

    array_callbacks = ADComponent(EpicsSignal, 'ArrayCallbacks')

# Create RunEngine
RE = RunEngine({})

# Define the motor
motor = EpicsMotor('DMC01:A', name='motor')

# Define the camera deviceca
class MyCamera(AreaDetector):
    cam = ADComponent(AreaDetectorCam, 'cam1:') #Fixed the single camera issue?
    image = ADComponent(ImagePlugin, 'image1:')
    tiff = ADComponent(TIFFPlugin, 'TIFF1:')
    pva = ADComponent(PvaPlugin, 'Pva1:')

# Instantiate the camera
camera = MyCamera('13ARV1:', name='camera')
camera.wait_for_connection()

#CAM OPTIONS
camera.stage_sigs[camera.cam.acquire] = 0 
camera.stage_sigs[camera.cam.image_mode] = 0 # single multiple continuous
camera.stage_sigs[camera.cam.trigger_mode] = 0 # internal external

#IMAGE OPTIONS
camera.stage_sigs[camera.image.enable] = 1 # pva plugin
camera.stage_sigs[camera.image.queue_size] = 2000

#TIFF OPTIONS
camera.stage_sigs[camera.tiff.enable] = 1
camera.stage_sigs[camera.tiff.auto_save] = 1
camera.stage_sigs[camera.tiff.file_write_mode] = 0  # Or 'Single' works too
camera.stage_sigs[camera.tiff.nd_array_port] = 'SP1'  
camera.stage_sigs[camera.tiff.auto_increment] = 1       #Doesn't work, must be ignored

#PVA OPTIONS
camera.stage_sigs[camera.pva.enable] = 1
camera.stage_sigs[camera.pva.blocking_callbacks] = 'No'
camera.stage_sigs[camera.pva.queue_size] = 2000  # or higher
camera.stage_sigs[camera.pva.nd_array_port] = 'SP1' 
camera.stage_sigs[camera.pva.array_callbacks] = 0  # disable during scan

def wait_for_file(filepath, timeout=5.0, poll_interval=0.1):
    """Wait until a file appears on disk, or timeout."""
    start = time.time()
    while not os.path.exists(filepath):
        if time.time() - start > timeout:
            raise TimeoutError(f"Timed out waiting for file: {filepath}")
        time.sleep(poll_interval)

def scan_with_saves(start_pos, end_pos, num_points):
    #Requirements for image capturing
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    callbacks_signal = EpicsSignal('13ARV1:image1:EnableCallbacks', name='callbacks_signal')
    acquire_signal = EpicsSignal('13ARV1:cam1:Acquire', name='acquire_signal')

    yield from bps.mv(callbacks_signal, 0)
    max_retries = 50
    positions = np.linspace(start_pos, end_pos, num_points)
    yield from bps.open_run()
    camera.cam.array_callbacks.put(0, wait=True)

    print("\n--- Staging camera ---")
    yield from bps.stage(camera)

    current_number = camera.tiff.file_number.get()

    NUM_IMAGES_PER_POS = 20

    for i, pos in enumerate(positions):
        print(f"\nMoving to pos={pos}")
        yield from bps.mv(motor, pos)
        yield from bps.sleep(2.0) 
        yield from bps.mv(acquire_signal, 0)  # Triggers a single image

        #for img_idx in range(NUM_IMAGES_PER_POS):
        filename = f'scan_{timestamp}_pos_{i}_shot_angle_{pos * 2.8125}'           
        current_number += 1
        filepath = os.path.join(save_dir, f"{filename}_{current_number}.tiff")

        yield from bps.mv(camera.tiff.file_name, filename)
        yield from bps.mv(camera.tiff.file_number, current_number)

        for attempt in range(1, max_retries + 1):

            try:
                print(f"[Attempt {attempt}] Capturing → {filepath}")
                yield from bps.mv(acquire_signal, 1)  # Triggers a single image
                yield from bps.sleep(1)

                # Wait for file to appear
                wait_for_file(filepath, timeout=5.0)

                print(f"✓ Image saved at {filepath}")
                break  # Exit retry loop if successful

            except TimeoutError:
                print(f"--Timeout waiting for image at {filepath}")
                if attempt == max_retries:
                    print(f"--Failed after {max_retries} attempts, skipping position {pos}")
                else:
                    print("↻ Retrying acquisition...")
                    yield from bps.mv(acquire_signal, 0)  # Triggers a single image
                    yield from bps.sleep(0.5)
    
    print("\n--- Unstaging camera ---")
    yield from bps.unstage(camera)

    yield from bps.mv(motor, 0.0)
    yield from bps.close_run()

def cropImages(inputDir):
    crop_box = (800, 800, 1600, 1500)
    output_dir = inputDir.replace('raw_images/', 'images/')

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(inputDir):
        if filename.endswith('.tiff'):
            image_path = os.path.join(inputDir, filename)
            img = Image.open(image_path)
            cropped = img.crop(crop_box)
            cropped.save(os.path.join(output_dir, filename))

def convert_image_format(image_dir: str, output_image_dir: str):
    os.makedirs(output_image_dir, exist_ok=True)

    for filename in os.listdir(image_dir):
        if filename.lower().endswith(".tiff") or filename.lower().endswith(".tif"):
            tiff_path = os.path.join(image_dir, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(output_image_dir, png_filename)

            with Image.open(tiff_path) as im:
                im.save(png_path, format="PNG")

if __name__ == "__main__":
    # Run scan
    try:
        print("Starting script")
        # File configuration
        base_path =  '/home/user/tmpData/AI_scan/' + sys.argv[4]
        save_dir = base_path + '/raw_images/'

        # Ensure the directory exists
        os.makedirs(save_dir, exist_ok=True)
        # Then set the path in EPICS

        start_pos = float(sys.argv[1])
        end_pos = float(sys.argv[2])
        num_points = int(sys.argv[3])

        camera.tiff.file_path.put(save_dir)
        camera.tiff.file_template.put('%s%s_%d.tiff')

        RE(scan_with_saves(start_pos, end_pos, num_points))

        cropImages(save_dir)

        image_dir_preprocess = os.path.join(base_path, "images")
        image_dir = os.path.join(base_path, "images_png")

        if ((os.path.exists(image_dir)) == 0):
            convert_image_format(image_dir_preprocess, image_dir)

        #cropped_dir = save_dir.replace('images_uncropped/', 'images/')
        #average_output_dir = os.path.join(cropped_dir, 'averaged')
        #average_images_per_position(cropped_dir, average_output_dir)

    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        RE.stop()
    except Exception as e:
        print(f"\nError during scan: {e}")
        #RE.stop()