from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class WebhookBase(BaseModel):
    url: str
    name: str = "Default Webhook"
    is_active: bool = True
    events: List[str] = ["extraction.success", "extraction.failed"]

class WebhookCreate(WebhookBase):
    secret: Optional[str] = None

class WebhookResponse(WebhookBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookLogResponse(BaseModel):
    id: UUID
    webhook_id: UUID
    event_type: str
    status_code: Optional[int]
    latency_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
