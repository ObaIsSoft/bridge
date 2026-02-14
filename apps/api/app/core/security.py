from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import ApiKey
from datetime import datetime
import hashlib
from starlette import status

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validate_api_key(
    api_key_header: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate the X-API-Key header.
    Checks for:
    - Existence in database
    - Expiration
    - Revocation
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )

    # Hash the provided key to compare with the stored hash
    key_hash = hashlib.sha256(api_key_header.encode()).hexdigest()
    
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    # Check for Revocation
    if api_key.revoked_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key has been revoked",
        )

    # Check for Expiration
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key has expired",
        )

    # Update last_used_at
    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return api_key

async def get_current_user(
    db: AsyncSession = Depends(get_db)
):
    from app.models import User
    # Mock authentication for MVP.
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(clerk_id="demo_user", email="demo@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user
