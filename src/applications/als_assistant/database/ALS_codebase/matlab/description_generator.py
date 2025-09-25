import logging
from pathlib import Path
import sys
import json
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# This allows imports from the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from framework.models import get_model
from pydantic_ai import Agent
from pydantic import BaseModel, Field

common_dir = Path(__file__).resolve().parent.parent / 'common'
sys.path.append(str(common_dir))

# Constants for error messages returned by generate_single_description or indicating failure
ERROR_LLM_OUTPUT = "Error: LLM output was not as expected."
ERROR_LLM_GENERATION = "Error generating description via LLM."
# This one was used if future.result() itself raised an exception in the previous simpler threaded version
ERROR_EXCEPTION_DURING_GENERATION = "Error: Exception during generation." 
# Set of known error messages that indicate a function needs reprocessing
ERROR_MESSAGES = {ERROR_LLM_OUTPUT, ERROR_LLM_GENERATION, ERROR_EXCEPTION_DURING_GENERATION}


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Pydantic model for the expected LLM output
class FunctionDescription(BaseModel):
    short_description: str = Field(..., description="A concise, one-sentence description for a given MATLAB code element.")
    long_description: str = Field(..., description="A detailed description for a given MATLAB code.")
    keywords: list[str] = Field(..., description="A list of 3-5 keywords that describe the MATLAB code element.")

class DescriptionGenerator:
    def __init__(self, model_id: str = "anthropic/claude-sonnet", provider: str = "cborg", max_workers: int = None, max_retries: int = 3):
        self.model_id = model_id
        self.provider = provider
        self.max_workers = max_workers if max_workers is not None else os.cpu_count()
        self.max_retries = max_retries
        logging.info(f"DescriptionGenerator initialized with model_id: {self.model_id}, provider: {self.provider}, max_workers: {self.max_workers}, max_retries: {self.max_retries}.")

    def generate_single_description(self, function_name: str, function_data: dict) -> tuple[str, str, list[str]]:
        """
        Generates a short and long description for a single function using an LLM.
        Returns error strings if generation fails at the LLM step.
        """
        cleaned_code = function_data.get('cleaned_code', '')
        docstring = function_data.get('docstring', '')
        file_type = function_data.get('file_type', 'function')
        file_path = function_data.get('file_path', 'N/A')
        group = function_data.get('group', 'N/A')

        # Augment group name
        if group == 'MML':
            group = 'MML (Matlab Middle Layer, general)'
        elif group == 'BTS':
            group = 'BTS (Booster To Storage Ring Transfer Line)'
        elif group == 'Booster':
            group = 'Booster Ring'
        elif group == 'StorageRing':
            group = 'Storage Ring'
        elif group == 'GTB':
            group = 'GTB (Gun To Booster Transfer Line)'
        elif group == 'Common':
            group = 'Common (Common ALS Specific Matlab Middle Layer code)'
        else:
            group = 'Unknown'
            
        # Prepare the cleaned code string for the prompt to avoid f-string syntax issues
        cleaned_code_str_for_prompt = '\n'.join(cleaned_code.splitlines()) if cleaned_code else 'No code provided.'

        system_prompt_content = f"""
        You are an expert MATLAB programmer at the Advanced Light Source Matlab Middle Layer team.
        
        Your taks is to analyze the provided Matlab code, understand its purpose and dependencies, and generate a report. 
        
        Details of the MATLAB code element:
        Name: {function_name}
        Type: {file_type}
        Source File: {file_path}
        Group: {group}
        
        Docstring:
        {docstring if docstring else 'No docstring provided.'}
        
        Cleaned Code Snippet:
        {cleaned_code_str_for_prompt}
        
        Based on all the information above, you have three tasks:
        
        Task 1: Provide a concise, one-sentence description for this MATLAB code element.
        The sentence should be suitable for use as a short description in a database or a quick help tooltip.
        Focus on what it *does*. Output only the description sentence.
        
        Task 2: Provide a detailed description for this MATLAB code.
        The description should be suitable for a software engineer to understand in detail what this function does and what its dependencies are. 

        Task 3: Provide a list of 3-5 keywords that describe this MATLAB code element. These should be relevant terms that could be used for searching or categorizing the code.

        Treat all acronyms (e.g., ICT, BSC, QF3S, IRM23) as literal, case-sensitive strings. Do not attempt to expand or interpret them unless their meaning is explicitly provided in the context. Do not hallucinate or invent acronyms.
        
        You output should be a json object in the following format:
        {{
            "short_description": "A concise, one-sentence description for this MATLAB code element.",
            "long_description": "A detailed description for this MATLAB code.",
            "keywords": ["keyword1", "keyword2", "keyword3"]
        }}
        """
        
        logging.debug(f"System prompt for {function_name}:{system_prompt_content}")

        try:
            agent = Agent(
                model=get_model(provider=self.provider, model_id=self.model_id),
                output_type=FunctionDescription,
                system_prompt=system_prompt_content
            )
            
            # Provide a user message, as some backends require it even if the system prompt is comprehensive
            lm_response = agent.run_sync("Generate the descriptions based on the provided information and instructions.") 
            
            if lm_response and lm_response.output:
                short_desc = lm_response.output.short_description
                long_desc = lm_response.output.long_description
                keywords = lm_response.output.keywords
                logging.debug(f"Generated descriptions for {function_name}: \n\nShort='{short_desc}', \n\nLong='{long_desc}', \n\nKeywords='{keywords}'\n\n------------------------------\n\n")
                return short_desc, long_desc, keywords
            else:
                logging.error(f"Failed to get a valid output from LLM for {function_name}. LM Response: {lm_response}")
                return ERROR_LLM_OUTPUT, ERROR_LLM_OUTPUT, []
        except Exception as e:
            logging.error(f"Error generating description for {function_name} with LLM: {e}")
            return ERROR_LLM_GENERATION, ERROR_LLM_GENERATION, []

    def _needs_description(self, func_data: dict) -> bool:
        """Checks if a function's data indicates its descriptions are missing, empty, None, or are known error messages."""
        short_desc = func_data.get('short_description')
        long_desc = func_data.get('long_description')
        keywords = func_data.get('keywords')

        # Condition 1: Main description fields are missing (None) or empty strings.
        if not short_desc or not long_desc:
            return True
        
        # Condition 2: Keywords are missing (None) or an empty list.
        if keywords is None or not keywords: # 'not keywords' handles empty list; 'keywords is None' explicitly handles None.
            return True
        
        # Condition 3: Existing descriptions are known error messages (needs to check type first).
        # These checks are important for reprocessing items that failed in a previous run with an older version of this script.
        if isinstance(short_desc, str) and (short_desc.startswith("Error:") or short_desc in ERROR_MESSAGES):
            return True
        if isinstance(long_desc, str) and (long_desc.startswith("Error:") or long_desc in ERROR_MESSAGES):
            return True
            
        return False

    def populate_descriptions(self, function_definitions: dict):
        """
        Iterates through function definitions and populates description fields using an LLM,
        with parallel execution and a retry mechanism.
        Modifies the function_definitions dictionary in place.
        """
        if not function_definitions:
            logging.warning("No function definitions provided to populate descriptions.")
            return

        # Identify functions that initially need descriptions
        functions_to_process_dict = {
            name: data for name, data in function_definitions.items() if self._needs_description(data)
        }
        
        if not functions_to_process_dict:
            logging.info("All functions already have complete descriptions.")
            return

        retry_counts = {name: 0 for name in functions_to_process_dict}
        initial_total_to_process = len(functions_to_process_dict)
        logging.info(f"Starting description generation. Total functions needing descriptions: {initial_total_to_process}")

        with tqdm(total=initial_total_to_process, desc="Overall Progress", unit="func") as pbar_outer:
            while functions_to_process_dict:
                current_batch_func_names = list(functions_to_process_dict.keys())
                if not current_batch_func_names:
                    logging.info("All tasks processed or max retries reached for all pending tasks.")
                    break
                
                logging.info(f"Starting new processing iteration. Functions in this batch: {len(current_batch_func_names)}")
                
                successful_in_batch = 0
                
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_func_name = {
                        executor.submit(self.generate_single_description, func_name, functions_to_process_dict[func_name]): func_name
                        for func_name in current_batch_func_names
                    }

                    with tqdm(as_completed(future_to_func_name), total=len(future_to_func_name), desc="Current Batch", unit="func", leave=False) as pbar_inner:
                        for future in pbar_inner:
                            func_name = future_to_func_name[future]
                            original_func_data_ref = function_definitions[func_name] # To update in place

                            try:
                                short_description, long_description, keywords = future.result()
                                
                                if short_description in ERROR_MESSAGES or long_description in ERROR_MESSAGES or \
                                    short_description.startswith("Error:") or long_description.startswith("Error:") or \
                                    not short_description or not long_description or not keywords: # Treat empty as error for retry
                                        raise ValueError(f"LLM returned an error or empty description/keywords: Short='{short_description}', Long='{long_description}', Keywords='{keywords}'")

                                original_func_data_ref['short_description'] = short_description
                                original_func_data_ref['long_description'] = long_description
                                original_func_data_ref['keywords'] = keywords
                                
                                if func_name in functions_to_process_dict: # Successfully processed
                                    del functions_to_process_dict[func_name]
                                    pbar_outer.update(1)
                                    successful_in_batch +=1
                                retry_counts[func_name] = 0 # Reset retry count on success

                            except Exception as exc:
                                logging.warning(f"Error processing {func_name} (attempt {retry_counts.get(func_name, 0) + 1}/{self.max_retries}): {exc}")
                                retry_counts[func_name] = retry_counts.get(func_name, 0) + 1
                                if retry_counts[func_name] >= self.max_retries:
                                    logging.error(f"Max retries ({self.max_retries}) reached for {func_name}. Giving up. Last error: {exc}")
                                    # Instead of populating with error messages, we will leave the fields as they are.
                                    # This ensures _needs_description will pick it up next time if it's still not populated.
                                    # original_func_data_ref['short_description'] = err_msg
                                    # original_func_data_ref['long_description'] = err_msg
                                    # original_func_data_ref['keywords'] = []
                                    if func_name in functions_to_process_dict:
                                        del functions_to_process_dict[func_name] 
                                        pbar_outer.update(1) # Count as "processed" for outer bar
                                # Else: function remains in functions_to_process_dict for the next main loop iteration

                if not functions_to_process_dict:
                    logging.info("All functions processed or max retries reached for all.")
                    break 
                
                if successful_in_batch == 0 and current_batch_func_names:
                    logging.warning(
                        f"An iteration with {len(current_batch_func_names)} functions completed with 0 successes. "
                        f"This might indicate a persistent issue (e.g., API key, network, model availability). "
                        f"Retrying for functions not yet at max attempts."
                    )
        
        final_pending_count = len(functions_to_process_dict)
        if final_pending_count > 0: # Should be 0 if loop exited cleanly
            logging.warning(f"{final_pending_count} functions remained in processing queue unexpectedly after loop completion.")
            # Update pbar for any remaining items if they weren't caught by max_retries logic somehow
            pbar_outer.update(final_pending_count)


        processed_count = initial_total_to_process - len(functions_to_process_dict)
        failed_after_retries = sum(1 for name in retry_counts if retry_counts[name] >= self.max_retries and name not in functions_to_process_dict) # Re-evaluate based on retry_counts for final tally
        
        logging.info(f"Finished populating descriptions. Initial functions to process: {initial_total_to_process}.")
        # The pbar_outer.n should reflect the total items "handled" (succeeded or max_retried)
        logging.info(f"Total functions handled (succeeded or max retries): {pbar_outer.n}")
        
        # A more accurate count of final states:
        successful_final = 0
        error_final = 0
        for name, data in function_definitions.items():
            if name not in retry_counts : # Was not in the initial "to_process" list
                 if not self._needs_description(data): # if it was pre-filled and correct
                    successful_final +=1
                 # else: it was pre-filled but with an error, and somehow missed by initial scan - unlikely
            elif self._needs_description(data): # Still needs description (i.e. ended with error)
                error_final += 1
            else: # Does not need description (i.e. success)
                successful_final += 1
        
        logging.info(f"Final tally: {successful_final} functions with descriptions, {error_final} functions with errors after processing.")


def main_description_generator():
    """
    Main function for the description generator module.
    Loads parsed data, generates descriptions in batches with periodic saving, and saves the enriched data.
    """
    logging.info("--- Starting Description Generator Standalone Execution ---")
    
    script_dir = Path(__file__).resolve().parent
    processed_dir = script_dir / "processed"
    io_json_path = processed_dir / "parsed_matlab_data.json"

    if not io_json_path.exists():
        logging.error(f"Input data file not found: {io_json_path}. Run the parser script first.")
        return

    try:
        with open(io_json_path, 'r') as f:
            data_to_update = json.load(f)
        logging.info(f"Successfully loaded data from {io_json_path}")
    except Exception as e:
        logging.error(f"Error loading data from {io_json_path}: {e}")
        return

    function_definitions = data_to_update.get("function_definitions")
    if function_definitions is None:
        logging.error("'function_definitions' not found in the input JSON. Cannot proceed.")
        return
    
    if not function_definitions:
        logging.warning("'function_definitions' is empty in the input JSON. No descriptions to generate.")
        # Save the (potentially empty but structured) file back if it was loaded.
        try:
            with open(io_json_path, 'w') as f:
                json.dump(data_to_update, f, indent=2)
            logging.info(f"Saved data (with no function definitions to process) to {io_json_path}")
        except Exception as e:
            logging.error(f"Error saving data to {io_json_path}: {e}")
        return

    provider = "cborg"
    model_id = "anthropic/claude-sonnet"
    num_threads = 5  # User-set: parallel threads for LLM calls within populate_descriptions
    max_retries_per_function = 3 # Max retries for a single function within populate_descriptions
    
    MAIN_SAVE_BATCH_SIZE = 100 # Number of functions to process before saving progress to JSON

    desc_generator = DescriptionGenerator(
        model_id=model_id, 
        provider=provider,
        max_workers=num_threads,
        max_retries=max_retries_per_function
    )

    main_loop_iteration = 0
    while True:
        main_loop_iteration += 1
        logging.info(f"\n\n\n--- Main Processing Loop Iteration: {main_loop_iteration} ---")

        # Identify all functions that currently need descriptions based on their current state
        functions_requiring_description_now_dict = {
            name: data
            for name, data in function_definitions.items()
            if desc_generator._needs_description(data) # Use instance method
        }

        if not functions_requiring_description_now_dict:
            logging.info("All functions appear to have valid descriptions or have been processed to their internal max retries. Main loop finished.")
            break
        
        # Convert to list of items and shuffle
        functions_requiring_description_now_items = list(functions_requiring_description_now_dict.items())
        random.shuffle(functions_requiring_description_now_items)

        num_needing_processing = len(functions_requiring_description_now_items)
        logging.info(f"Found {num_needing_processing} functions still needing descriptions in this pass (order randomized).")

        # Take a sub-batch of these functions for the current populate_descriptions call
        # items_for_current_populate_call is already a list of (name, data) tuples
        items_for_current_populate_call = functions_requiring_description_now_items[:MAIN_SAVE_BATCH_SIZE]
        current_batch_dict_to_populate = dict(items_for_current_populate_call)
        
        if not current_batch_dict_to_populate:
            # This should ideally be caught by the (not functions_requiring_description_now_dict) check.
            # Added as a safeguard.
            logging.info("No functions were selected for the current main processing batch, though some were eligible. Exiting main loop.")
            break

        logging.info(f"Processing a main batch of {len(current_batch_dict_to_populate)} functions (up to {MAIN_SAVE_BATCH_SIZE} targeted).")
        
        # populate_descriptions will modify function_definitions in-place
        # because current_batch_dict_to_populate contains references to its items.
        desc_generator.populate_descriptions(current_batch_dict_to_populate)

        logging.info(f"Main batch processing via populate_descriptions complete for {len(current_batch_dict_to_populate)} functions. Saving current state of all data...")
        try:
            with open(io_json_path, 'w') as f:
                json.dump(data_to_update, f, indent=2) # Save the entire updated data_to_update
            logging.info(f"Successfully saved updated data to {io_json_path}")
        except Exception as e:
            logging.error(f"CRITICAL: Error saving updated data to {io_json_path}: {e}")
            logging.warning("Continuing to next main batch despite save failure. Data integrity risk.")
        
        # The loop continues, and functions_requiring_description_now_dict will be re-evaluated
        # in the next iteration based on the changes made by populate_descriptions.

    # data_to_update["function_definitions"] = function_definitions # This assignment is redundant as modifications are in-place
    logging.info("--- Description Generator Standalone Execution Finished ---")

if __name__ == "__main__":
    main_description_generator() 