from mem0 import Memory
import os

# Custom instructions for memory processing
CUSTOM_INSTRUCTIONS = """
You are helping a control room assistant at the Advanced Light Source (ALS) extract relevant long-term memory.

Please extract:
- Personal preferences regarding the ALS machine, user interfaces, displays, panels, workflows, or tools.
- Factual information about the ALS accelerator, beamlines, components, or operational procedures.

Ignore general conversation, jokes, greetings, or unrelated information.

Here are some few-shot examples:

Input: Hi.
Output: {{"facts" : []}}

Input: I prefer using the 'Orbit Display' panel instead of the 'Fast Orbit Feedback' summary.
Output: {{"facts" : ["Prefers 'Orbit Display' panel over 'Fast Orbit Feedback' summary"]}}

Input: The ALS storage ring beam size is measured at beamline 3.1.
Output: {{"facts" : ["Storage Ring beam size measurement located at beamline 3.1"]}}

Input: I usually check the 'Temperature Monitor' first thing in the morning.
Output: {{"facts" : ["Prefers checking 'Temperature Monitor' panel in the morning"]}}

Input: Beam losses often happen near sector 12 during ramp-up.
Output: {{"facts" : ["Beam losses commonly occur near sector 12 during ramp-up"]}}

Input: The beam lifetime has been really stable lately.
Output: {{"facts" : ["Beam lifetime recently stable"]}}

Input: Thank you!
Output: {{"facts" : []}}

Return the extracted facts in a JSON format as shown above.
Be concise but specific when summarizing facts.
"""

def get_mem0_client():
    # Get service hosts from environment variables
    qdrant_host = os.getenv("QDRANT_HOST")
    ollama_host = os.getenv("OLLAMA_HOST")
    
    # Get ports from environment variables or use defaults
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
    
    # Get vector store config from environment variables
    collection_name = os.getenv("VECTOR_STORE_COLLECTION", "test")
    embedding_model_dims = int(os.getenv("EMBEDDING_MODEL_DIMS", "768"))
    
    # Get LLM config from environment variables
    llm_model = os.getenv("LLM_MODEL", "llama3.1:latest")
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0"))
    llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # Get embedder config from environment variables
    embedder_model = os.getenv("EMBEDDER_MODEL", "nomic-embed-text:latest")
    
    # Format the Ollama base URL
    ollama_base_url = f"http://{ollama_host}:{ollama_port}"
    
    print(f"DEBUG: QDRANT_HOST: {qdrant_host}")
    print(f"DEBUG: OLLAMA_HOST: {ollama_host}")
    print(f"DEBUG: QDRANT_PORT: {qdrant_port}")
    print(f"DEBUG: OLLAMA_PORT: {ollama_port}")
    
    
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": collection_name,
                "host": qdrant_host,
                "port": qdrant_port,
                "embedding_model_dims": embedding_model_dims,
            },
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "temperature": llm_temperature,
                "max_tokens": llm_max_tokens,
                "ollama_base_url": ollama_base_url,
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": embedder_model,
                "ollama_base_url": ollama_base_url,
            },
        },
        "custom_fact_extraction_prompt": CUSTOM_INSTRUCTIONS,
    }
    
    # Create and return the Memory client
    return Memory.from_config(config)