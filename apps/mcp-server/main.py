import asyncio
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import os
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bridge-mcp-server")

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("BRIDGE_API_KEY", "")

# Initialize FastMCP server
mcp = FastMCP("Bridge")

async def fetch_bridges() -> List[Dict[str, Any]]:
    """Fetch active bridges from the API Bridge backend."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            # We'll use the existing /bridges endpoint
            response = await client.get(f"{API_URL}/api/v1/bridges/", headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch bridges: {e}")
            return []

@mcp.tool()
async def list_available_bridges() -> str:
    """List all configured API bridges available for extraction."""
    bridges = await fetch_bridges()
    if not bridges:
        return "No bridges configured or backend is unreachable."
    
    output = "Available Bridges:\n"
    for b in bridges:
        slug = b.get('slug', 'N/A')
        output += f"- {b['name']} (Slug: {slug}) [{b['domain']}]\n"
    return output

@mcp.tool()
async def get_bridge_schema(bridge_identifier: str) -> Dict[str, Any]:
    """
    Get the extraction schema for a specific bridge.
    Arguments:
        bridge_identifier: The UUID or Slug (e.g., 'amazon-products') of the bridge.
    """
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            url = f"{API_URL}/api/v1/bridges/{bridge_identifier}"
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("extraction_schema", {})
        except Exception as e:
            logger.error(f"Failed to fetch schema: {e}")
            return {"error": str(e)}

@mcp.tool()
async def extract_data_from_bridge(bridge_identifier: str) -> Dict[str, Any]:
    """
    Extract structured data from a specific bridge.
    Arguments:
        bridge_identifier: The UUID or Slug (e.g., 'amazon-products') of the bridge.
    """
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            # Trigger the extraction (now async, returns a task_id)
            extract_url = f"{API_URL}/api/v1/bridges/{bridge_identifier}/extract"
            response = await client.post(extract_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")

            if not task_id:
                return {"error": "Failed to trigger extraction task"}

            # Poll for results
            for _ in range(20): # 20 attempts, 1s interval
                await asyncio.sleep(1)
                status_url = f"{API_URL}/api/v1/bridges/tasks/{task_id}"
                status_res = await client.get(status_url, headers=headers)
                status_res.raise_for_status()
                status_data = status_res.json()

                if status_data["status"] == "SUCCESS":
                    return status_data.get("result", {})
                elif status_data["status"] == "FAILURE":
                    return {"error": status_data.get("error", "Task failed")}
            
            return {"error": "Extraction timed out after 20 seconds"}

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Standard MCP server startup
    mcp.run()
