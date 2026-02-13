from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..core.database import get_db
from ..models import ApiKey, User
import uuid
import secrets
import hashlib
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/keys", tags=["API Keys"])

class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    last_four: str
    created_at: datetime
    last_used_at: datetime | None

    class Config:
        from_attributes = True

class ApiKeyCreate(BaseModel):
    name: str

@router.get("/", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ApiKey))
    return result.scalars().all()

@router.post("/", response_model=dict)
async def create_api_key(
    key_in: ApiKeyCreate,
    db: AsyncSession = Depends(get_db)
):
    # Demo user check
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(clerk_id="demo_user", email="demo@example.com")
        db.add(user)
        await db.commit()

    # Generate key
    raw_key = f"ab_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    api_key = ApiKey(
        user_id=user.id,
        name=key_in.name,
        key_hash=key_hash,
        prefix=raw_key[:8],
        last_four=raw_key[-4:]
    )
    
    db.add(api_key)
    await db.commit()
    
    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": raw_key, # Only shown once
        "warning": "Store this key safely! It will not be shown again."
    }
