from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.webmcp import WebMCPService
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webmcp", tags=["WebMCP"])

class WebMCPDiscoverRequest(BaseModel):
    url: HttpUrl

class WebMCPExecuteRequest(BaseModel):
    url: HttpUrl
    tool_name: str
    parameters: Dict[str, Any]

@router.post("/discover")
async def discover_tools(
    request: WebMCPDiscoverRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Discover WebMCP tools available on a given URL.
    """
    try:
        async with WebMCPService(headless=True) as webmcp:
            tools = await webmcp.discover_tools(str(request.url))
            return {"status": "success", "tools": tools}
    except Exception as e:
        logger.error(f"WebMCP discovery failed: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/execute")
async def execute_tool(
    request: WebMCPExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a specific WebMCP tool on a URL.
    """
    try:
        async with WebMCPService(headless=True) as webmcp:
            result = await webmcp.execute_tool(
                str(request.url),
                request.tool_name,
                request.parameters
            )
            return result
    except Exception as e:
        logger.error(f"WebMCP execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
