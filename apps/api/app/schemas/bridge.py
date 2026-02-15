from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

class BridgeBase(BaseModel):
    name: str
    slug: Optional[str] = None
    domain: str
    target_url: str
    extraction_schema: Dict[str, Any]
    selectors: Optional[Dict[str, str]] = None
    auth_config: Optional[Dict[str, Any]] = None
    interaction_script: Optional[List[Dict[str, Any]]] = None
    session_data: Optional[Dict[str, Any]] = None
    
    # WebMCP
    has_webmcp: Optional[bool] = False
    webmcp_tool_count: Optional[int] = 0

class WebMCPToolCreate(BaseModel):
    tool_name: str
    tool_type: str
    description: Optional[str] = None
    parameters_schema: Optional[Dict[str, Any]] = None

class BridgeCreate(BridgeBase):
    webmcp_tools: Optional[List[WebMCPToolCreate]] = None

class PermissionResponse(BaseModel):
    domain: str
    status: str
    contact_email: Optional[str] = None
    twitter_handle: Optional[str] = None
    github_handle: Optional[str] = None
    linkedin_handle: Optional[str] = None
    last_checked: datetime

    class Config:
        from_attributes = True

class WebMCPToolResponse(WebMCPToolCreate):
    id: UUID
    is_available: bool
    last_verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BridgeResponse(BridgeBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    last_successful_extraction: Optional[datetime]
    last_error: Optional[str]
    permission: Optional[PermissionResponse] = None
    webmcp_tools: Optional[List[WebMCPToolResponse]] = []

    class Config:
        from_attributes = True

class ExtractionResult(BaseModel):
    bridge_id: UUID
    data: Dict[str, Any]
    timestamp: datetime

class TaskResponse(BaseModel):
    task_id: str
    status: str

class ScanFinding(BaseModel):
    type: str
    match: str
    file: Optional[str] = None
    source: Optional[str] = "file_system" # "file_system" or "git_history"
    validation_status: Optional[str] = "unknown" # "active", "revoked", "unknown"
    start: int
    end: int

class ScanResponse(BaseModel):
    total_findings: int
    findings: List[ScanFinding]
    scanned_at: datetime
