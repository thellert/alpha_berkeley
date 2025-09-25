import os
from typing import Optional, Union
import logging
import httpx
import openai
import ast

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai import Agent
from pydantic import BaseModel


# Helper function to create an OpenAI-compatible model instance
def _create_openai_compatible_model(
    model_id: str,
    api_key: str,
    base_url: Optional[str],
    timeout_arg_from_get_model: Optional[float],
    shared_http_client: Optional[httpx.AsyncClient] = None
) -> OpenAIModel:
    """Helper function to create an OpenAI-compatible model instance."""
    
    openai_client_instance: openai.AsyncOpenAI
    if shared_http_client:
        client_args = {
            "api_key": api_key,
            "http_client": shared_http_client
        }
        if base_url: # Pass base_url if provided
            client_args["base_url"] = base_url
        openai_client_instance = openai.AsyncOpenAI(**client_args)
    else:
        # No shared client.
        effective_timeout_for_openai = timeout_arg_from_get_model if timeout_arg_from_get_model is not None else 60.0
        client_args = {
            "api_key": api_key,
            "timeout": effective_timeout_for_openai
        }
        if base_url: # Pass base_url if provided
            client_args["base_url"] = base_url
        openai_client_instance = openai.AsyncOpenAI(**client_args)

    model = OpenAIModel(
        model_name=model_id,
        provider=OpenAIProvider(openai_client=openai_client_instance),
    )
    # Storing original model_id for clarity, similar to model_config.py
    model.model_id = model_id 
    return model

def get_model(
    provider: str,
    model_id: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    max_tokens: int = 100000,
) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """
    Get a model for structured LLM generation.
    """
    current_model_id = model_id
    current_api_key = api_key
    async_http_client: Optional[httpx.AsyncClient] = None
    proxy_url = os.getenv("HTTP_PROXY")

    # Create a custom client if a proxy is set or a specific timeout is requested
    if proxy_url or timeout is not None:
        client_params = {}
        if proxy_url:
            client_params["proxy"] = proxy_url
        if timeout is not None:
            client_params["timeout"] = timeout
        async_http_client = httpx.AsyncClient(**client_params)


    if provider.lower() == "google":
        if not current_model_id:
            raise ValueError("Model ID for Google not provided.")
        
        if not current_api_key:
            current_api_key = os.getenv("GEMINI_API_KEY")
        if not current_api_key:
            raise ValueError("No API key provided for Google and GEMINI_API_KEY not set.")
        
        google_provider = GoogleGLAProvider(
            api_key=current_api_key, 
            http_client=async_http_client
        )
        
        return GeminiModel(model_name=current_model_id, provider=google_provider)

    elif provider.lower() == "anthropic":
        if not current_model_id:
            raise ValueError("Model ID for Anthropic not provided.")

        if not current_api_key:
            current_api_key = os.getenv("ANTHROPIC_API_KEY_o")
        if not current_api_key:
            raise ValueError("No API key provided for Anthropic and ANTHROPIC_API_KEY_o not set.")

        anthropic_provider = AnthropicProvider(
            api_key=current_api_key,
            http_client=async_http_client
        )
        return AnthropicModel(
            model_name=current_model_id, 
            provider=anthropic_provider, 
        )
    
    elif provider.lower() == "openai":
        if not current_model_id:
            # Match behavior of model_config.py: model_id is required for openai.
            raise ValueError("Model ID for OpenAI not provided.")
        
        if not current_api_key:
            current_api_key = os.getenv("OPENAI_API_KEY")
        if not current_api_key:
            raise ValueError("No API key provided for OpenAI and OPENAI_API_KEY not set.")

        return _create_openai_compatible_model(
            model_id=current_model_id,
            api_key=current_api_key,
            base_url=None, # OpenAI doesn't take base_url this way, it's part of client config or defaults
            timeout_arg_from_get_model=timeout, # Pass the get_model's timeout arg
            shared_http_client=async_http_client
        )

    elif provider.lower() == "cborg":
        current_model_id = model_id if model_id is not None else os.getenv("MODEL_ID")
        if not current_model_id:
            raise ValueError("Model ID for cborg not provided directly or via MODEL_ID environment variable.")
        current_api_key = api_key if api_key is not None else os.getenv("CBORG_API_KEY")
        current_base_url = base_url if base_url is not None else os.getenv("CBORG_API_URL")

        if not current_api_key:
            raise ValueError("No API key provided for CBorg and CBORG_API_KEY not set.")
        if not current_base_url:
            raise ValueError("No base URL provided for CBorg and CBORG_API_URL not set.")

        # CBorg uses OpenAI-compatible API, so reuse the helper
        return _create_openai_compatible_model(
            model_id=current_model_id,
            api_key=current_api_key,
            base_url=current_base_url,
            timeout_arg_from_get_model=timeout,
            shared_http_client=async_http_client
        )

    else:
        raise ValueError(f"Invalid provider: {provider}. Must be 'anthropic', 'google', 'openai', or 'cborg'.")

def clean_matlab_code(content: str) -> tuple[str, str]:
    """
    Cleans MATLAB code by removing trailing inline comments and extracts the file-level docstring.
    Full comment lines (e.g., function docstrings, other % blocks) are preserved in the cleaned code.

    Args:
        content: Raw MATLAB code string.

    Returns:
        A tuple: (cleaned_code_str, file_docstring_str)
        - cleaned_code_str: Code with trailing comments removed. Full comment lines (including
                            file-level and function-level docstrings) are preserved.
        - file_docstring_str: The initial block of comments from the file, if any,
                              with leading '%' and surrounding whitespace removed from each line.
    """
    lines = content.split('\n')
    
    file_docstring_extracted_lines = []
    first_actual_code_line_idx = 0 # Index in original `lines` where non-file-docstring content begins
    
    # 1. Extract file-level docstring
    # This docstring consists of initial contiguous comment lines
    in_file_docstring_block = False
    for i, line_text in enumerate(lines):
        stripped_content = line_text.strip()
        if stripped_content.startswith('%'):
            file_docstring_extracted_lines.append(stripped_content[1:].strip()) # Store without leading %
            in_file_docstring_block = True
            if i == len(lines) - 1: # If file ends with docstring
                first_actual_code_line_idx = len(lines)
        elif not stripped_content and in_file_docstring_block: # Allow empty lines within the docstring block
            file_docstring_extracted_lines.append("") 
        elif in_file_docstring_block: # First non-comment/non-empty line after a docstring block
            first_actual_code_line_idx = i
            break
        else: # Line is not a comment, and we haven't started a docstring block (e.g., code at the top)
            first_actual_code_line_idx = i
            break
    else: # Loop finished without break (e.g., file is all comments or all empty)
        if in_file_docstring_block or all(not line.strip() for line in lines):
             first_actual_code_line_idx = len(lines)
        # If not in_file_docstring_block and not all empty, means file had no leading comments.
        # first_actual_code_line_idx remains 0, which is correct.

    file_docstring_output = '\n'.join(file_docstring_extracted_lines).strip()

    # 2. Process all original lines to create cleaned_code_str
    # This version preserves all full comment lines and only removes trailing comments from code lines.
    output_code_lines = []
    for line_content_orig in lines:
        current_line_processed_chars = []
        in_string_parsing_mode = False
        string_literal_delimiter = None
        
        char_scan_idx = 0
        while char_scan_idx < len(line_content_orig):
            char_under_scan = line_content_orig[char_scan_idx]
            
            if char_under_scan in ("'", '"'): # String literal handling
                if not in_string_parsing_mode:
                    in_string_parsing_mode = True
                    string_literal_delimiter = char_under_scan
                elif char_under_scan == string_literal_delimiter:
                    in_string_parsing_mode = False
                    string_literal_delimiter = None
                current_line_processed_chars.append(char_under_scan)
            elif char_under_scan == '%': # Potential comment
                if not in_string_parsing_mode:
                    # If line (stripped) starts with '%', it's a full comment line; preserve it.
                    if line_content_orig.strip().startswith('%'):
                        current_line_processed_chars = list(line_content_orig) # Take whole original line
                        break # Done with this line, move to next line_content_orig
                    else: # It's a trailing comment on a code line.
                        break # Stop collecting chars for current_line_processed_chars
                else: # '%' is inside a string literal
                    current_line_processed_chars.append(char_under_scan)
            # Handle escaped '%%' within a string (e.g., for sprintf)
            elif char_under_scan == '%' and \
                 char_scan_idx + 1 < len(line_content_orig) and \
                 line_content_orig[char_scan_idx+1] == '%' and \
                 in_string_parsing_mode:
                current_line_processed_chars.append('%') # First %
                current_line_processed_chars.append('%') # Second %
                char_scan_idx += 1 # Advance past the second '%'
            else: # Regular character
                current_line_processed_chars.append(char_under_scan)
            char_scan_idx += 1
            
        # Append the processed line (or part of it if trailing comment was cut)
        # Original snippet rstrip()s and adds if non-empty.
        # This ensures that lines that become purely whitespace (e.g. "    % comment" -> "    ")
        # are kept as "    " if not empty after rstrip.
        # And full comment lines (e.g. "% my comment") are preserved as such.
        finalized_line = "".join(current_line_processed_chars).rstrip()
        output_code_lines.append(finalized_line)
    
    return output_code_lines, file_docstring_output

def read_paths_from_file(file_list_path: str, relative_path_prefix: str = "") -> list[str]:
    """
    Reads a list of file paths from a text file or a Python file.

    For .txt files:
    - Each line is treated as a potential path.
    - Lines starting with '#' are ignored as comments.

    For .py files:
    - Assumes paths are in a list assigned to a variable named 'file_list'.
    - Example: file_list = ['/path/to/file1.m', 'relative/path/file2.m']

    Args:
        file_list_path (str): Path to the text or Python file containing file paths.
        relative_path_prefix (str): A prefix to prepend to paths that are not absolute.
                                    If empty, relative paths are returned as is, unless they
                                    should be resolved relative to file_list_path (not current behavior).

    Returns:
        list: A list of processed file paths.
    """
    processed_paths = []
    
    if not os.path.exists(file_list_path):
        logging.error(f"Path list file not found: {file_list_path}")
        return []

    try:
        file_extension = os.path.splitext(file_list_path)[1].lower()
        raw_paths = []

        if file_extension == '.txt':
            with open(file_list_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        raw_paths.append(line)
        
        elif file_extension == '.py':
            with open(file_list_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content, filename=file_list_path) # Add filename for better error reporting
                found_list = False
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            # Check for target.id if it's an ast.Name node
                            if isinstance(target, ast.Name) and target.id == 'file_list':
                                if isinstance(node.value, ast.List):
                                    for elt in node.value.elts:
                                        # For Python 3.8+ ast.Constant, Python < 3.8 ast.Str
                                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                            raw_paths.append(elt.value)
                                        elif hasattr(elt, 's') and isinstance(elt.s, str): # Compatibility for ast.Str (Python < 3.8)
                                            raw_paths.append(elt.s)
                                        else:
                                            logging.warning(f"Skipping non-string or unexpected element in list 'file_list' in {file_list_path}: {ast.dump(elt)}")
                                    found_list = True
                                    break # Processed the 'file_list'
                                else:
                                    logging.warning(f"Variable 'file_list' in {file_list_path} is not a list: {ast.dump(node.value)}")
                                    found_list = True # Mark as found to stop searching for 'file_list'
                                    break
                        if found_list:
                            break 
                if not found_list:
                    logging.warning(f"Python file {file_list_path} does not contain a 'file_list' variable assign to a list of strings.")
            except SyntaxError as e:
                logging.error(f"Syntax error parsing Python file {file_list_path}: {e}")
                return [] # Stop processing this file on syntax error
            except Exception as e:
                logging.error(f"Error processing Python file {file_list_path} for paths: {e}")
                return [] # Stop processing on other AST/parsing errors

        else:
            logging.error(f"Unsupported file type for path list: {file_list_path}. Only .txt and .py are supported.")
            return []

        # Process raw_paths to prepend prefix if path is relative
        for path_str in raw_paths:
            path_str = path_str.strip() 
            if not path_str:
                continue

            if os.path.isabs(path_str):
                processed_paths.append(os.path.normpath(path_str))
            elif relative_path_prefix:
                processed_paths.append(os.path.normpath(os.path.join(relative_path_prefix, path_str)))
            else:
                # If no prefix and path is relative, append it as is (normalized).
                processed_paths.append(os.path.normpath(path_str))
                
    except FileNotFoundError: # Should be caught by the initial os.path.exists, but good for safety
        logging.error(f"Path list file not found (should not happen here): {file_list_path}")
    except Exception as e:
        # General error catching for file operations or other unexpected issues
        logging.error(f"Error reading or processing path list file {file_list_path}: {e}")
        
    return processed_paths

def read_matlab_file(file_path):
    """
    Read a MATLAB file and clean its content.
    
    Args:
        file_path (str): Path to the MATLAB file
        
    Returns:
        str or None: Cleaned MATLAB code, or None if there was an error
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
            # clean_matlab_code now returns a tuple (cleaned_code_str, file_docstring_str)
            # We only need the cleaned_code_str here as per original function's intent.
            cleaned_code_str, _ = clean_matlab_code(content)
            return cleaned_code_str
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return None
    

def check_physbase_mounted():
    """
    Check if the physbase directory is properly mounted.
    
    Returns:
        bool: True if physbase is mounted, False otherwise
    """
    physbase_path = '/home/als/physbase/'
    if not os.path.exists(physbase_path):
        logging.error(f"PHYSBASE directory not found at {physbase_path}")
        logging.error("Please mount PHYSBASE before running this script")
        return False
    
    # Check for the mmlt directory which should exist in physbase
    mmlt_path = os.path.join(physbase_path, 'mmlt')
    if not os.path.exists(mmlt_path):
        logging.error(f"MMLT directory not found at {mmlt_path}")
        logging.error("PHYSBASE appears to be mounted incorrectly")
        return False
    
    return True

def create_analysis_prompt(file_content):
    prompt = f"""
    Analyze the following Matlab code file and provide a short summary of the code.
    
    CODE:
    ```matlab
    {file_content}
    ```
    
    Provide your response in a clear, structured format that would help another developer understand what this code does without having to read all of it.
    """
    return prompt


def run_analysis_agent(file_content: str, model_id: str = "anthropic/claude-sonnet"):
    """
    Get an analysis agent for code analysis.
    
    Args:
        model_id (str): The ID of the model to use
        
    Returns:
        Agent: An agent for code analysis
    """
    
    class CodeDescription(BaseModel):
        description: str
               
    analysis_agent = Agent(
        model=get_model(
            provider="cborg",
            model_id=model_id
        ),
        output_type=CodeDescription,
        system_prompt=create_analysis_prompt(file_content)
    )
        
    lm_response = analysis_agent.run()
    analysis_output: CodeDescription = lm_response.output
    return analysis_output.description