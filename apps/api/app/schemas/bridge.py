from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

class BridgeBase(BaseModel):
    name: str
    domain: str
    target_url: str
    extraction_schema: Dict[str, Any]
    selectors: Optional[Dict[str, str]] = None

class BridgeCreate(BridgeBase):
    pass

class BridgeResponse(BridgeBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    last_successful_extraction: Optional[datetime]
    last_error: Optional[str]

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
