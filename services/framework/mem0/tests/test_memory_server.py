#!/usr/bin/env python3
import asyncio
from fastmcp import Client

async def test_memory_server():
    """Test the memory server running on port 8050."""
    print("Connecting to memory server at http://localhost:8050/sse...")
    
    # Create a client for the memory server
    async with Client("http://localhost:8050/sse") as client:
        try:
            print("\n1. Testing save_memory tool:")
            memory_text = "The ALS operates at 1.9 GeV with a beam current of 500 mA."
            save_result = await client.call_tool("save_memory", {"text": memory_text})
            print(f"Save result: {save_result}")
            
            print("\n2. Testing get_all_memories tool:")
            all_memories = await client.call_tool("get_all_memories", {})
            print(f"All memories: {all_memories}")
            
            print("\n3. Testing search_memories tool:")
            search_result = await client.call_tool("search_memories", {"query": "beam current", "limit": 1})
            print(f"Search result: {search_result}")
            
            print("\nAll tests completed successfully!")
        except Exception as e:
            print(f"Error testing memory server: {e}")

if __name__ == "__main__":
    asyncio.run(test_memory_server()) 