import re
import logging
from pathlib import Path
from collections import defaultdict
import sys
import os
import json

# Add the common directory to the path for imports
common_dir = Path(__file__).resolve().parent.parent / 'common'
sys.path.append(str(common_dir))

# Import cleaning function from utils
from utils import clean_matlab_code, check_physbase_mounted, read_paths_from_file

# Set up logging (can be configured by the main script if preferred)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


class MatlabFileParser:
    """Extracts MATLAB function definitions, calls, and metadata from files."""
    
    def __init__(self):
        self.function_definitions = {}  # {func_name: {'file_path': str, 'docstring': str, 'group': str, 'cleaned_code': str, 'file_type': str, 'short_description': '', 'long_description': ''}}
        self.file_functions = defaultdict(list)  # {file_path: [function_names]}
        self.function_calls = defaultdict(set)  # {function_name: {called_functions}}
        self.file_groups = {} # {file_path: group_name}
        
        script_dir = Path(__file__).resolve().parent
        mml_definitions_path = script_dir / "source" / "als_matlab_function_definitions.txt"
        self.mml_functions = self._load_mml_functions(mml_definitions_path)
        
    def _load_mml_functions(self, filepath: Path) -> set:
        """Loads MML function names from a given file."""
        mml_functions = set()
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            mml_functions.add(line)
                logging.info(f"Loaded {len(mml_functions)} MML function definitions from {filepath}")
            else:
                logging.error(f"MML function definition file not found: {filepath}. No MML functions will be specifically tracked.")
        except Exception as e:
            logging.error(f"Error loading MML function definitions from {filepath}: {e}")
        return mml_functions
            
    def extract_main_function_definition(self, content_lines):
        """
        Reads MATLAB file content and extracts the main function name.
        """
        function_pattern = re.compile(r"^\s*function\s+(?:[\w\s,\[\]]+\s*=\s*)?([a-zA-Z]\w*)\s*\(.*")
        for line in content_lines:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            match_obj = function_pattern.match(line)
            if match_obj:
                return match_obj.group(1)
            else:
                return None 
    
    def extract_function_calls(self, content, primary_function_name):
        """
        Extracts function calls from MATLAB code based on the list of MML functions.
        """
        called_functions = set()
        content_str = '\\n'.join(content) if isinstance(content, list) else content
        for mml_func_name in self.mml_functions:
            # Ensure the MML function is present and is not the primary function itself
            if mml_func_name in content_str and mml_func_name != primary_function_name:
                called_functions.add(mml_func_name)
        return called_functions
    
    def associate_file_with_group(self, file_path: str, group_name: str):
        """Associates a file path with a group name."""
        self.file_groups[file_path] = group_name

    def analyze_file(self, file_path: str):
        """
        Analyzes a single MATLAB file for its primary function, called functions,
        docstring, and cleaned code. Updates internal data structures.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                raw_content = file.read()
            
            cleaned_content_lines, file_docstring = clean_matlab_code(raw_content)
            
            primary_function_name = self.extract_main_function_definition(cleaned_content_lines)
            
            # Determine file type and ensure a name for scripts
            if primary_function_name is None:
                file_type = 'script'
                # Use the file stem as the name for scripts
                primary_function_name = Path(file_path).stem 
            else:
                file_type = 'function'
                
            called_functions = self.extract_function_calls(cleaned_content_lines, primary_function_name)
            
            self.file_functions[file_path].append(primary_function_name)
            self.function_calls[primary_function_name].update(called_functions) # Use update for sets

            # Store detailed information for each primary function or script
            # Initialize 'description' field, to be populated later by LLM
            self.function_definitions[primary_function_name] = {
                'file_path': file_path,
                'docstring': file_docstring,
                'group': self.file_groups.get(file_path, 'Unknown'), # Get group, default if not set
                'file_type': file_type,
                'cleaned_code': "\\n".join(cleaned_content_lines),
                'called_functions': list(called_functions), # Store for direct access if needed
                'keywords': [],
                'short_description': '',
                'long_description': ''
            }
            
            logging.debug(f"Analyzed {file_type}: {primary_function_name} in {file_path}. Calls: {called_functions}")

        except Exception as e:
            logging.error(f"Error analyzing file {file_path}: {str(e)}")

    def get_extracted_data(self):
        """Returns the extracted function definitions and calls."""
        return self.function_definitions, self.function_calls, self.file_functions, self.file_groups

def main_parser():
    """
    Main function for the parser module.
    Loads MATLAB file paths, parses them, and saves the raw extracted data.
    """
    logging.info("--- Starting MATLAB Parser Standalone Execution ---")
    
    physbase_root = "/home/als/physbase"
    if not check_physbase_mounted():
        logging.error(f"ERROR: PHYSBASE directory not properly mounted at {physbase_root}")
        logging.error("Please mount PHYSBASE before running this script's parser stage.")
        return

    parser = MatlabFileParser()
    
    workspace_root = Path("/home/als/")
    script_dir = Path(__file__).resolve().parent
    source_dir = script_dir / 'source'
    output_dir = script_dir / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_json_path = output_dir / "parsed_matlab_data.json"

    group_configs = {
        "StorageRing": source_dir / "als_matlab_paths_StorageRing.txt",
        "Booster":     source_dir / "als_matlab_paths_Booster.txt",
        "BTS":         source_dir / "als_matlab_paths_BTS.txt",
        "GTB":         source_dir / "als_matlab_paths_GTB.txt",
        "Common":      source_dir / "als_matlab_paths_Common.txt",
        "MML":         source_dir / "als_matlab_paths_MML.txt",
    }

    all_matlab_files_to_process = set()
    
    logging.info("Loading MATLAB file paths for defined groups...")
    for group_name, path_file in group_configs.items():
        logging.info(f"Processing group: {group_name} from file {path_file}")
        matlab_files_for_group = read_paths_from_file(str(path_file), relative_path_prefix=str(workspace_root))
        if not matlab_files_for_group:
            logging.warning(f"No MATLAB files found for group {group_name} in {path_file}")
            continue
        
        for file_path in matlab_files_for_group:
            parser.associate_file_with_group(file_path, group_name)
            all_matlab_files_to_process.add(file_path)
        logging.info(f"Loaded {len(matlab_files_for_group)} files for group {group_name}")

    if not all_matlab_files_to_process:
        logging.error("No MATLAB files found to analyze from any group definitions.")
        return

    matlab_paths_list = sorted(list(all_matlab_files_to_process))
    logging.info(f"Found a total of {len(matlab_paths_list)} unique MATLAB files to analyze.")
    
    logging.info("Starting MATLAB file analysis...")
    for idx, file_path in enumerate(matlab_paths_list):
        if (idx + 1) % 100 == 0: # Log progress
            logging.info(f"Parsing file {idx + 1}/{len(matlab_paths_list)}: {file_path}")
            
        if os.path.exists(file_path):
            parser.analyze_file(file_path)
        else:
            logging.warning(f"File not found during analysis: {file_path}. Skipping.")
    
    function_definitions, function_calls, file_functions, file_groups = parser.get_extracted_data()
    logging.info(f"Initial parsing complete. Found {len(function_definitions)} functions/scripts.")

    # Save the extracted data
    data_to_save = {
        "function_definitions": function_definitions,
        "function_calls": {k: list(v) for k, v in function_calls.items()}, # Convert sets to lists for JSON
        "file_functions": file_functions,
        "file_groups": file_groups
    }

    try:
        with open(output_json_path, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        logging.info(f"Parser output saved to {output_json_path}")
    except Exception as e:
        logging.error(f"Error saving parsed data to JSON: {e}")

    logging.info("--- MATLAB Parser Standalone Execution Finished ---")

if __name__ == "__main__":
    main_parser() 