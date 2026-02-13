from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.models import Webhook, User, WebhookLog
from app.schemas.webhook import WebhookCreate, WebhookResponse, WebhookLogResponse
import uuid
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Webhook))
    return result.scalars().all()

@router.post("/", response_model=WebhookResponse)
async def create_webhook(webhook_in: WebhookCreate, db: AsyncSession = Depends(get_db)):
    # Get default user for MVP
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    webhook = Webhook(
        **webhook_in.model_dump(),
        user_id=user.id
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook

@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    webhook = await db.get(Webhook, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    await db.delete(webhook)
    await db.commit()
    return {"status": "success"}

@router.get("/{webhook_id}/logs", response_model=List[WebhookLogResponse])
async def get_webhook_logs(webhook_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WebhookLog)
        .where(WebhookLog.webhook_id == webhook_id)
        .order_by(WebhookLog.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()
