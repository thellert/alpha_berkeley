#!/usr/bin/env python3
import asyncio
from fastmcp import Client
import uuid

async def test_pv_finder_server():
    """Test the PV Finder server running on port 8051."""
    server_url = "http://localhost:8051/sse" 
    print(f"Connecting to PV Finder server at {server_url}...") 
    
    # Create a client for the PV Finder server
    async with Client(server_url) as client:
        try:
            print("\nTesting run_pv_finder tool:")
            # Use a simple query relevant to the PV Finder's likely domain
            # query_text = "What is the beam current PV?"
            query_text = "Whats the lifetime of the storage ring?"
            
            # Generate test langfuse context with UUIDs
            langfuse_context = {
                "user_id": f"test_user_{uuid.uuid4()}",
                "session_id": f"benchmark_test",
                "trace_id": str(uuid.uuid4()),
                "parent_span_id": str(uuid.uuid4())
            }
            
            # Include langfuse context in parameters
            parameters = {
                "langfuse_context": langfuse_context
            }
            
            result = await client.call_tool("run_pv_finder", {
                "query": query_text,
                "parameters": parameters
            })
            
            print(f"Query: '{query_text}'")
            print(f"Using langfuse context: {langfuse_context}")
            
            # Check if the result is a list with a single text content item
            if isinstance(result, list) and len(result) == 1 and hasattr(result[0], 'type') and result[0].type == 'text' and hasattr(result[0], 'text'):
                print(f"Result:\n{result[0].text}")
            else:
                # Print the raw result if it's not the expected format
                print(f"Result: {result}")
            
            print("\nTest completed successfully!")
        except Exception as e:
            print(f"Error testing PV Finder server: {e}")

if __name__ == "__main__":
    asyncio.run(test_pv_finder_server()) 