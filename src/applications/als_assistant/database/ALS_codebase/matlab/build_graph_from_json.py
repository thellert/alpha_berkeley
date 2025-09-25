import json
import logging
from pathlib import Path
import networkx as nx
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class GraphBuilder:
    def __init__(self, function_definitions: dict, function_calls: dict, file_functions: dict):
        self.function_definitions = function_definitions
        self.function_calls = function_calls
        self.file_functions = file_functions # For statistics
        self.graph = nx.DiGraph()
        self._build_dependency_graph()

    def _build_dependency_graph(self):
        """Build the networkx dependency graph from collected data."""
        # Add all defined functions as nodes
        for func_name, func_data in self.function_definitions.items():
            self.graph.add_node(
                func_name, 
                group=func_data.get('group', 'Unknown'),
                keywords=func_data.get('keywords', ''),
                short_description=func_data.get('short_description', ''),
                long_description=func_data.get('long_description', ''),
                file_path=func_data.get('file_path', ''), 
                docstring=func_data.get('docstring', ''),
                type=func_data.get('file_type', 'Unknown'),
                cleaned_code=func_data.get('cleaned_code', ''),
                
            )
        
        # Add edges for function calls
        for caller, callees in self.function_calls.items():
            if caller not in self.function_definitions: # Ensure caller is a known function/script
                logging.debug(f"Skipping calls from '{caller}' as it's not in function_definitions (might be an MML-only reference or script not processed as primary)")
                continue
            for callee in callees:
                if callee in self.function_definitions: # Only add edge if callee is defined
                    self.graph.add_edge(caller, callee)
                else:
                    logging.debug(f"Callee '{callee}' called by '{caller}' not found in defined functions. Edge not added.")
                    
        logging.info(f"Built dependency graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def export_graph(self, output_dir_str: str):
        """
        Export the dependency graph as a GraphML file.
        """
        output_dir = Path(output_dir_str)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export as GraphML
        graphml_path = output_dir / 'matlab_dependencies.graphml'
        # Create a copy for export, ensuring all attributes are preserved
        graph_for_export = self.graph.copy()
        
        # Ensure all node attributes are strings for GraphML compatibility, converting if necessary
        for node, data in graph_for_export.nodes(data=True):
            for key, value in data.items():
                if not isinstance(value, str):
                    data[key] = str(value)
            # Ensure critical attributes expected by some GraphML readers are present, even if empty
            data.setdefault('label', node) # Use node name as label if not otherwise specified

        nx.write_graphml(graph_for_export, str(graphml_path))
        logging.info(f"Exported GraphML to {graphml_path}")


def main_graph_builder():
    """
    Main function for the graph builder module.
    Loads data with descriptions, builds the graph, and exports it.
    Also, optionally, regenerates GraphML from its own JSON output for verification.
    """
    logging.info("--- Starting Graph Builder Standalone Execution ---")

   
    project_root_dir = Path(os.getenv("PROJECT_ROOT"))
    target_processed_dir = project_root_dir / "database" / "ALS_codebase" / "matlab" / "processed"

    input_json_path = target_processed_dir / "parsed_matlab_data.json"
    # Output directory for graph files is also the target 'processed' directory
    output_dir_path = target_processed_dir 

    if not input_json_path.exists():
        logging.error(f"Input data file not found: {input_json_path}. Run the parser and description generator scripts first.")
        return

    try:
        with open(input_json_path, 'r') as f:
            enriched_data = json.load(f)
        logging.info(f"Successfully loaded data from {input_json_path}")
    except Exception as e:
        logging.error(f"Error loading data with descriptions from {input_json_path}: {e}")
        return

    function_definitions = enriched_data.get("function_definitions")
    function_calls_raw = enriched_data.get("function_calls")
    file_functions = enriched_data.get("file_functions")

    if function_definitions is None or function_calls_raw is None or file_functions is None:
        logging.error("Missing one or more required keys ('function_definitions', 'function_calls', 'file_functions') in input JSON. Cannot proceed.")
        return

    # Convert function_calls back to sets if they were stored as lists in JSON
    function_calls = {k: set(v) for k, v in function_calls_raw.items()}

    if not function_definitions:
        logging.warning("No function definitions available to build graph. Graph will be empty.")
        # Create empty structures to prevent downstream errors if proceeding with empty graph
        graph_builder = GraphBuilder({}, {}, {})
    else:
        graph_builder = GraphBuilder(function_definitions, function_calls, file_functions)
    
    graph_builder.export_graph(str(output_dir_path))
    

    logging.info(f"--- Graph Builder Standalone Execution Finished. Outputs in {output_dir_path} ---")

if __name__ == "__main__":
    main_graph_builder() 