import os
import re

def extract_function_definition(matlab_file_path):
    """
    Reads a MATLAB file and attempts to extract the function name 
    from the first non-comment, non-empty line.
    """
    # Regex to capture the function name. It handles:
    #   function funcName(...)
    #   function out = funcName(...)
    #   function [out1, out2] = funcName(...)
    function_pattern = re.compile(r"^\s*function\s+(?:[\w\s,\[\]]+\s*=\s*)?([a-zA-Z]\w*)\s*\(.*")

    try:
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
        content_lines = None
        for encoding in encodings_to_try:
            try:
                with open(matlab_file_path, 'r', encoding=encoding) as f:
                    content_lines = f.readlines()
                break 
            except UnicodeDecodeError:
                continue
        
        if content_lines is None:
            print(f"Warning: Could not decode file {matlab_file_path} with attempted encodings.")
            return None

        for line in content_lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            if line.startswith("%"):  # Skip comment lines
                continue
            
            match_obj = function_pattern.match(line)
            if match_obj:
                return match_obj.group(1)  # Return the captured function name
            else:
                # First real line is not a function definition or doesn't match pattern
                return None 
                
    except IOError as e:
        # print(f"Warning: Could not read file {matlab_file_path}. Reason: {e}")
        return None
    except Exception as e:
        # print(f"Warning: Unexpected error processing file {matlab_file_path}. Reason: {e}")
        return None
    
    return None # If file is empty or only contains comments/blank lines

def create_matlab_file_list():
    base_path = "/home/als/physbase/mmlt/machine/ALS"

    subsystem_map = {
        "Booster": ["Booster", "BoosterOpsData"],
        "BTS": ["BTS", "BTSOpsData"],
        "GTB": ["GTB", "GTBOpsData"],
        "StorageRing": ["StorageRing", "StorageRingOpsData"],
        "Common": ["Common"],
        "MML": ["../../mml"]
    }
    
    all_matlab_files_for_output = {}
    all_function_definitions = set()
    processed_files_for_functions = set()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    excluded_dir_name = "@AccObj" # Directory name to exclude
    # Construct the full path for the MML directory to correctly build the exclusion path
    mml_base_path = os.path.abspath(os.path.join(base_path, "../../mml"))
    path_to_exclude = os.path.join(mml_base_path, excluded_dir_name)

    # Process each system defined in the subsystem_map
    for system_name, folders_for_system in subsystem_map.items():
        print(f"Processing system: {system_name}")
        system_specific_files = set()
        for folder_name_part in folders_for_system:
            current_folder_path = os.path.abspath(os.path.join(base_path, folder_name_part))
            
            if os.path.isdir(current_folder_path):
                print(f"  Scanning: {current_folder_path}")
                for root, _, files in os.walk(current_folder_path):
                    # Check if the current root is the excluded directory or a subdirectory of it
                    if os.path.abspath(root).startswith(os.path.abspath(path_to_exclude)):
                        print(f"    Skipping excluded directory: {root}")
                        continue # Skip this directory

                    for file in files:
                        if file.endswith(".m"):
                            full_file_path = os.path.join(root, file)
                            system_specific_files.add(full_file_path)

                            if full_file_path not in processed_files_for_functions:
                                definition = extract_function_definition(full_file_path)
                                if definition:
                                    all_function_definitions.add(definition)
                                processed_files_for_functions.add(full_file_path)
            else:
                print(f"  Warning: Directory not found for system '{system_name}': {current_folder_path}")
        
        all_matlab_files_for_output[system_name] = sorted(list(system_specific_files))

    # Write the collected file paths to separate output files for each system
    prefix_to_remove = "/home/als/"
    for system_name_loop, file_list_loop in all_matlab_files_for_output.items():
        output_filename_subsystem = os.path.join(script_dir, f"als_matlab_paths_{system_name_loop}.txt")
        try:
            with open(output_filename_subsystem, "w") as f:
                f.write(f"# List of MATLAB (.m) files for ALS system: {system_name_loop}\n")
                f.write(f"# Paths listed below are relative to {prefix_to_remove.rstrip('/')}\n")
                
                source_folder_descriptions = subsystem_map.get(system_name_loop, [])
                folders_str = ", ".join([f"'{s}'" for s in source_folder_descriptions])
                f.write(f"# Files were sourced from definitions: {folders_str}\n")
                f.write(f"# (applied relative to base: {base_path}, or used as specified in map)\n\n")

                if file_list_loop:
                    for file_path in file_list_loop:
                        output_path = file_path
                        if file_path.startswith(prefix_to_remove):
                            output_path = file_path[len(prefix_to_remove):]
                        f.write(f"{output_path}\n")
                else:
                    f.write("# No .m files found for this system/combination of directories.\n")
            print(f"Successfully wrote MATLAB file paths for {system_name_loop} to '{os.path.abspath(output_filename_subsystem)}'")
        except IOError as e:
            print(f"Error: Could not write to file '{output_filename_subsystem}' for system {system_name_loop}. Reason: {e}")

    # Write all found function definitions to a new file
    output_filename_functions = os.path.join(script_dir, "als_matlab_function_definitions.txt")
    try:
        with open(output_filename_functions, "w") as f:
            f.write("# List of unique MATLAB function names found in the ALS codebase\n")
            f.write(f"# Searched in paths defined in subsystem_map, relative to base: {base_path}\n\n")
            if all_function_definitions:
                for definition in sorted(list(all_function_definitions)): # Sort for consistent output
                    f.write(f"{definition}\n")
            else:
                f.write("# No function definitions found.\n")
        print(f"Successfully wrote MATLAB function definitions to '{os.path.abspath(output_filename_functions)}'")
    except IOError as e:
        print(f"Error: Could not write to file '{output_filename_functions}'. Reason: {e}")

if __name__ == "__main__":
    create_matlab_file_list()
