import shutil, sys, subprocess, os, time 
from PIL import Image

def ensure_directories(*paths: str) -> None:
    """ Create directories if they don't exist."""
    for path in paths:
        os.makedirs(path, exist_ok=True)

def feature_extraction(imageDir: str, databasePath: str, colmapPath: str):
    """ Run feature extraction. """
    subprocess.run([
        colmapPath, "feature_extractor",
        "--database_path", databasePath,
        "--image_path", imageDir,
        "--SiftExtraction.use_gpu", "0",
        "--SiftExtraction.num_threads", "6"  # or 1 to be safe
    ], check=True)

def feature_matching(databasePath: str, colmapPath: str):
    """ 
    Run feature matching. 
    """
    subprocess.run([
        colmapPath, "exhaustive_matcher",
        "--database_path", databasePath,
        "--SiftMatching.use_gpu", "0",
    ], check=True)

def sparse_reconstruction(imageDir: str, databasePath: str, colmapPath: str, sparseDir: str):
    """ 
    Run sparse reconstruction. 
    """
    subprocess.run([
        colmapPath, "mapper",
        "--database_path", databasePath,
        "--image_path", imageDir,
        "--output_path", sparseDir
    ], check=True)

def image_undistorter(imageDir: str, denseDir: str, colmapPath: str, sparseDir: str):
    """ 
    Run image undistorter, which outputs acccording 
    to quality of point detection.
    """
    subprocess.run([
        colmapPath, "image_undistorter",
        "--image_path", imageDir,
        "--input_path", sparseDir, "0",
        "--output_path", denseDir,
        "--output_type", "COLMAP"
    ], check=True)

def interface_colmap(workspace_dir: str, imageDir: str, basePath: str, sceneMVS: str, denseDir: str, mvs_bin_dir: str):
    """ 
    Run interfaceCOLMAP, which converts gathered data from 
    colmap and output scene_mvs, containing necessary scene 
    for next reconstruction steps. 
    """
    subprocess.run([
        os.path.join(mvs_bin_dir, "InterfaceCOLMAP"),
        "-i", os.path.join(workspace_dir, "dense"),       #Needed for manual colmap
        #"-i", os.path.join(workspace_dir, "dense", "0"),  Needed for automaticReconstruction combo     
        "-o", sceneMVS,
        "--image-folder", imageDir
    ],cwd=denseDir)

def densify_point_cloud(sceneMVS: str, denseDir: str, mvs_bin_dir: str):
    """ 
    Densify point cloud connects points by creating more points
    in between already created points. """
    subprocess.run([
        os.path.join(mvs_bin_dir, "DensifyPointCloud"),
        sceneMVS
    ], cwd=denseDir)

def reconstruct_mesh(denseMVS: str, denseDir: str, mvs_bin_dir: str):
    """ 
    Creates mesh of object, lacking color but connecting points.
    """
    subprocess.run([
        os.path.join(mvs_bin_dir, "ReconstructMesh"),
        denseMVS
    ], cwd=denseDir)

def texture_mesh(denseDir: str, sceneMVS: str, mvs_bin_dir: str):
    """ 
    Texture mesh mixes data from both sceneMVS and the mesh 
    
    Note: This is time consuming and should be skipped if mesh quality is subpar
    """

    subprocess.run([
        os.path.join(mvs_bin_dir, "TextureMesh"), 
        sceneMVS,
        "-m", "scene_dense_mesh.ply"
    ],cwd=denseDir)

def run_colmap_pipeline(image_dir: str, workspace_dir: str, colmap_path: str = "colmap") -> None:
    """
    Full COLMAP pipeline: feature extraction → matching → sparse reconstruction → undistortion.
    """
    print(f"Running COLMAP pipeline on {image_dir} -> {workspace_dir}")
    database_path = os.path.join(workspace_dir, "database.db")
    sparse_dir = os.path.join(workspace_dir, "sparse")
    dense_dir = os.path.join(workspace_dir, "dense")

    ensure_directories(workspace_dir, sparse_dir, dense_dir)

    feature_extraction(image_dir, database_path, colmap_path)
    feature_matching(database_path, colmap_path)
    sparse_reconstruction(image_dir, database_path, colmap_path, sparse_dir)
    image_undistorter(image_dir, dense_dir, colmap_path, os.path.join(sparse_dir, "0"))

    print("COLMAP pipeline completed.")

def run_openmvs_pipeline(base_path: str, image_dir: str, workspace_dir: str, mvs_bin_dir: str, image_file_name: str) -> None:
    """
    Run OpenMVS conversion and mesh reconstruction from COLMAP output.
    """

    dense_dir = os.path.join(workspace_dir, "dense")
    scene_mvs = os.path.join(dense_dir, "scene.mvs")
    dense_mvs = os.path.join(dense_dir, "scene_dense.mvs")
    ensure_directories(dense_dir)

    interface_colmap(workspace_dir, image_dir, base_path, scene_mvs, dense_dir, mvs_bin_dir)
    densify_point_cloud(scene_mvs, dense_dir, mvs_bin_dir)
    reconstruct_mesh(dense_mvs, dense_dir, mvs_bin_dir)
    texture_mesh(dense_dir, scene_mvs, mvs_bin_dir)

    print("OpenMVS pipeline completed.")

def automatic_reconstruction(image_dir: str, workspace_dir: str, colmap_path: str = "colmap"):
    """
    Run COLMAP's automatic reconstruction pipeline.
    """
    database_path = os.path.join(workspace_dir, "database.db")
    sparse_dir = os.path.join(workspace_dir, "sparse")
    dense_dir = os.path.join(workspace_dir, "dense")

    ensure_directories(workspace_dir, sparse_dir, dense_dir)

    subprocess.run([
        colmap_path, "automatic_reconstructor",
        "--workspace_path", workspace_dir,
        "--image_path", image_dir,
        "--data_type", "individual",  # or 'video' depending on your input
        "--quality", "medium",        # can be 'low', 'medium', or 'high'
        "--sparse", "true",
        "--dense", "true",
    ], check=True)

    print("Automatic reconstruction completed.")









#Turned off cuda dependency just for this system






if __name__ == "__main__":
    #File path names
    image_file_name = sys.argv[1]

    #Where reconstructions and image data is stored
    base_path = "/home/user/tmpData/AI_scan/"

    #Depending on where openMVS is ran
    mvs_bin_path = "/usr/local/bin/OpenMVS/"

    image_dir = os.path.join(base_path, image_file_name, "images_png")
    print(image_dir)

    if (os.path.exists(image_dir)):
        #Default images folder

        #Default workspace folder
        workspace_dir = os.path.join(base_path, image_file_name, "workspace")
        print("Made it here")
        t0 = time.time()
        run_colmap_pipeline(image_dir, workspace_dir)
        #automatic_reconstruction(image_dir, workspace_dir)
        t1 = time.time()

        t2 = time.time()
        run_openmvs_pipeline(base_path, image_dir, workspace_dir, mvs_bin_path, image_file_name)
        t3= time.time()

        #Timing check
        print(f"COLMAP time: {t1 - t0:.2f}s")
        print(f"OpenMVS time: {t3 - t2:.2f}s")
        print(f"Total time: {t3 - t0:.2f}s")
    else:
        print("This did not work")