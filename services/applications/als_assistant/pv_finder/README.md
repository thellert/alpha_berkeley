# PV Finder MCP Server

This MCP (Model Context Protocol) server provides access to the Advanced Light Source (ALS) control system PV (Process Variable) finder agent. The agent can find PVs based on natural language queries.

## Features

- Handles natural language queries for PVs
- Returns PVs relevant to the query

## Setup and Management (Docker Compose)

The recommended way to run this server is using the container management system at the repository root.

1.  **Navigate to the repository root:**
    ```bash
    cd ../../../../ # From services/applications/als_assistant/pv_finder
    ```

2.  **Configure the service in config.yml:**
    Ensure the PV Finder service is listed in your `deployed_services`:
    ```yaml
    deployed_services:
      - applications.als_assistant.pv_finder
    ```

3.  **Deploy the service:**
    ```bash
    # Deploy all configured services (including PV Finder)
    python deployment/container_manager.py config.yml up -d
    ```
    This automatically finds the `docker-compose.yml.j2` template in this directory, renders it with your configuration, builds the `pv-finder-server` image if needed, and starts the container. The service runs as part of the `als-agents` Docker Compose project and is exposed on **host port 8051** (as configured in your config.yml).

4.  **Other Management Commands (run from repository root):**
    Use the container manager to control deployments:
    *   `python deployment/container_manager.py config.yml down`: Stop all services.
    *   `python deployment/container_manager.py config.yml rebuild -d`: Clean rebuild and start in detached mode.
    *   `python deployment/container_manager.py config.yml clean`: Remove containers, images, and volumes.
    *   `python deployment/container_manager.py config.yml`: Generate compose files without deploying.

5.  **Service-specific operations:**
    You can also manage just the PV Finder service by updating `deployed_services` in config.yml to include only:
    ```yaml
    deployed_services:
      - applications.als_assistant.pv_finder
    ```

## Connecting with MCP Clients

Once the server is running (started via the container management system), configure your MCP client to connect using SSE:

```json
{
  "mcpServers": {
    "pv-finder-server": {
      "transport": "sse",
      "url": "http://localhost:8051/sse"
      // Use "serverUrl" for Windsurf
      // Use "http://host.docker.internal:8051/sse" if client is also in Docker
    }
  }
}
```

## Usage

The server provides the following tool:

### run_pv_finder

Send a query to the PV Finder Agent to find PVs in the Advanced Light Source (ALS) control system.

**Parameters:**
- `query` (string): The user's natural language query for a PV.

**Example:**
```
"What is the PV for the storage ring beam current?"
```

## Development (Local Python)

For local development *without* Docker:

1.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the server directly (ensure environment variables like PORT, HOST, TRANSPORT are set appropriately if needed):
    ```bash
    python src/main.py
    ```
    *Note: This bypasses the Docker/Compose setup and runs directly on your host.*

## Notes

This server assumes that the main repository code is accessible. When deploying in a Docker container, the container management system automatically handles mounting the necessary source code from the repository (via the `copy_src` configuration and volume mounts in the docker-compose template). The PV Finder agent and related models from `src/applications/als_assistant/` are automatically made available in the container. 