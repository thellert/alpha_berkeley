<h1 align="center">MCP-Mem0: Long-Term Memory for the ALS Control System</h1>

<p align="center">
  <img src="public/Mem0AndMCP.png" alt="Mem0 and MCP Integration" width="600">
</p>

An implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server integrated with [Mem0](https://mem0.ai) for providing AI agents with persistent memory capabilities. This implementation is specifically designed for the Advanced Light Source (ALS) accelerator facility.

## Overview

This project implements an MCP server that enables AI agents to store, retrieve, and search memories using semantic search. It is tailored for use at the Advanced Light Source (ALS) particle accelerator facility, storing information about machine preferences, operational procedures, and historical observations.

The implementation follows the best practices laid out by Anthropic for building MCP servers, allowing seamless integration with any MCP-compatible client.

## Management (Docker Compose)

This server is designed to be run as part of a larger collection of ALS agents managed by Docker Compose.

The lifecycle (start, stop, restart, build, logs, status) of this server is controlled by the central management script located at the root of the repository:

```bash
# Navigate to the repository root
cd ../../

# Start/Update all agents (including this one)
# Requires Python 3.10+
python manage_agents.py --up # Default action, can also omit --up

# Stop all agents
python manage_agents.py --stop

# View logs for all agents
python manage_agents.py --logs

# Check status of all agents
python manage_agents.py --status

# See the script's help for other options (--rebuild, --force-recreate, --no-tests, etc.)
python manage_agents.py --help
```

This server (`mem0-server`) runs within the `als-agents` Docker Compose project, managed by the Python script.

## Features

The server provides three essential memory management tools:

1. **`save_memory`**: Store ALS-related information in long-term memory with semantic indexing
2. **`get_all_memories`**: Retrieve all stored ALS memories for comprehensive context
3. **`search_memories`**: Find relevant ALS memories using semantic search

## Prerequisites

- Python 3.12+
- Qdrant vector database (for vector storage of memories)
- Ollama for local LLM and embedding models
- Docker if running the MCP server as a container (recommended)

## Installation

### Using uv

1. Install uv if you don't have it:
   ```bash
   pip install uv
   ```

2. Clone this repository and navigate to the project directory.

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure your environment variables in the `.env` file (see Configuration section)

### Using Docker (Recommended)

The Docker image for this server is built and run automatically when using the main `manage_agents.py` script in the repository root.

Manual building (for debugging or inspection) can be done using:
```bash
# In the MCP_servers/memory_server directory
docker build -t mcp/mem0 --build-arg PORT=8050 .
```

## Configuration

The following environment variables can be configured in your `.env` file:

| Variable | Description | Example |
|----------|-------------|----------|
| `TRANSPORT` | Transport protocol (sse or stdio) | `sse` |
| `HOST` | Host to bind to when using SSE transport | `0.0.0.0` |
| `PORT` | Port to listen on when using SSE transport | `8050` |

The configuration for Mem0 client is set in the `utils.py` file and uses:
- Qdrant vector store for memory storage
- Ollama for LLM (llama3.1:latest) and embedding models (nomic-embed-text:latest)
- Custom fact extraction prompt tailored for ALS-specific information

## Running the Server

### Using Docker

With the `docker-compose.yml` file in place, the server's lifecycle is managed by the root `manage_agents.py` script.

Manual interaction with the service *within the context of the whole project* can be done using `docker-compose` commands from the **repository root**, specifying all relevant compose files. See the `manage_agents.py` script for how this is constructed (it builds the necessary `-f` arguments for `docker-compose`). Direct `docker-compose` commands within *this* directory are generally **not recommended** as they won't manage the full `als-agents` project correctly.

#### SSE Transport

When the service is running (started via the root `manage_agents.py` script), the MCP server will be available as an API endpoint within the container network and exposed on the host machine (default port 8050).

#### Stdio Transport

Using stdio directly with a service managed by Docker Compose is less common. The recommended approach is to use SSE transport when running via Docker Compose. If stdio is strictly required, the configuration below attempts to run a *new, separate* container from the image, which might not be what you intend if you want to interact with the service managed by the compose stack.

### Docker with Stdio Configuration

```json
{
  "mcpServers": {
    "mem0": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT=stdio", 
               "-e", "HOST=localhost", 
               "-e", "PORT=8050", 
               "--network=host", # May be needed depending on Ollama/Qdrant setup
               "mcp/mem0" # Assumes image 'mcp/mem0' was built
              ],
      "env": { 
        # Env vars passed via '-e' in args above for Docker
      }
    }
  }
}
```
> **Note:** This runs a new container via `docker run`, separate from any service potentially running via the `manage_agents.py` script (which uses `docker-compose up`). It also assumes the `mcp/mem0` image has been built previously (e.g., by running `python manage_agents.py --rebuild` or `docker-compose build` via that script). Connecting via SSE to the service started by `manage_agents.py` is generally recommended.

## Integration with MCP Clients

### SSE Configuration

Once you have the server running with SSE transport, you can connect to it using this configuration:

```json
{
  "mcpServers": {
    "mem0": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

> **Note for Windsurf users**: Use `serverUrl` instead of `url` in your configuration:
> ```json
> {
>   "mcpServers": {
>     "mem0": {
>       "transport": "sse",
>       "serverUrl": "http://localhost:8050/sse"
>     }
>   }
> }
> ```

> **Note for n8n users**: Use host.docker.internal instead of localhost since n8n has to reach outside of its own container to the host machine:
> 
> So the full URL in the MCP node would be: http://host.docker.internal:8050/sse

Make sure to update the port if you are using a value other than the default 8050.

### Python with Stdio Configuration

Add this server to your MCP configuration for Claude Desktop, Windsurf, or any other MCP client:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "your/path/to/mcp-mem0/.venv/Scripts/python.exe",
      "args": ["your/path/to/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "HOST": "localhost",
        "PORT": "8050"
      }
    }
  }
}
```

## Custom ALS Memory Processing

This implementation includes a custom instruction set specifically designed for processing Advanced Light Source (ALS) related information:

- Personal preferences regarding ALS machine interfaces and displays
- Factual information about the ALS accelerator, beamlines, and components
- Operational procedures and workflows
- Machine performance observations and patterns

The memory extraction process is optimized to identify and store relevant ALS information while filtering out conversational elements not relevant to operations.

## Building Your Own Server

This template provides a foundation for building more complex MCP servers. To build your own:

1. Add your own tools by creating methods with the `@mcp.tool()` decorator
2. Create your own lifespan function to add your own dependencies (clients, database connections, etc.)
3. Modify the `utils.py` file for any helper functions and custom configurations you need
4. Customize the fact extraction prompt for your specific domain
5. Feel free to add prompts and resources as well with `@mcp.resource()` and `@mcp.prompt()`
