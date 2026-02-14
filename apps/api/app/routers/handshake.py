from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models import User, HandshakeRequest
from app.services.outreach import OutreachService
from app.core.security import get_current_user
import uuid

router = APIRouter(prefix="/handshake", tags=["handshake"])

class HandshakeInitRequest(BaseModel):
    domain: str
    method: str # EMAIL, TWITTER, GITHUB
    recipient: str
    context: Optional[str] = None # Extra info for the AI

class HandshakeResponse(BaseModel):
    id: uuid.UUID
    status: str
    message_body: str
    recipient: str

@router.post("/initiate", response_model=HandshakeResponse)
async def initiate_handshake(
    request: HandshakeInitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Generate Message (Template for now, LLM later)
    subject = f"Collaboration Request: {request.domain}"
    body = f"""Hello {request.recipient},

I'm building a bridge to {request.domain} using Bridge.dev. 
I'd love to request permission to access your public data in an ethical, structured way.

Best,
{current_user.email}
"""
    
    # 2. Create Request Record
    handshake = HandshakeRequest(
        user_id=current_user.id,
        domain=request.domain,
        method=request.method.upper(),
        recipient=request.recipient,
        status="PENDING_APPROVAL",
        message_subject=subject,
        message_body=body
    )
    
    db.add(handshake)
    await db.commit()
    await db.refresh(handshake)
    
    return handshake

@router.post("/approve/{request_id}", response_model=HandshakeResponse)
async def approve_handshake(
    request_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch Request
    result = await db.execute(select(HandshakeRequest).where(HandshakeRequest.id == request_id, HandshakeRequest.user_id == current_user.id))
    handshake = result.scalars().first()
    
    if not handshake:
        raise HTTPException(status_code=404, detail="Handshake request not found")
        
    if handshake.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Cannot approve request in status {handshake.status}")

    # 2. Update Status
    handshake.status = "Sending..." # Temporary status (or keep pending until done)
    await db.commit()
    
    # 3. Schedule Sending Task
    background_tasks.add_task(send_outreach_task, handshake.id)
    
    return handshake

async def send_outreach_task(handshake_id: uuid.UUID):
    # Re-open DB session for background task
    from app.core.database import AsyncSessionLocal
    service = OutreachService()
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(HandshakeRequest).where(HandshakeRequest.id == handshake_id))
        handshake = result.scalars().first()
        
        if not handshake:
            return

        try:
            remote_id = None
            if handshake.method == "EMAIL":
                # Assuming recipient is email
                remote_id = await service.send_email(handshake.recipient, handshake.message_subject, handshake.message_body)
            elif handshake.method == "TWITTER":
                remote_id = await service.send_tweet(handshake.recipient, handshake.message_body)
            elif handshake.method == "GITHUB":
                # Assuming recipient is repo url for issue, or we need a way to distinguish
                # For now, let's assume recipient is the repo url
                remote_id = await service.create_github_issue(handshake.recipient, handshake.message_subject, handshake.message_body)
            
            handshake.status = "SENT"
            handshake.remote_id = remote_id
            
        except Exception as e:
            handshake.status = "FAILED"
            handshake.error_log = str(e)
        
        await db.commit()
