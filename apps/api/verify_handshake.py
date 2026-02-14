import asyncio
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_handshake")

# FORCE OVERRIDE DB SETTINGS BEFORE IMPORTING DB
from app.core.config import settings
settings.database_url = "sqlite+aiosqlite:///./test.db"

from app.core.database import AsyncSessionLocal, engine, Base
from app.models import User, Bridge, HandshakeRequest, DomainPermission
from app.routers.handshake import HandshakeInitRequest, initiate_handshake, approve_handshake, send_outreach_task
from fastapi import BackgroundTasks

async def verify():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        logger.info("🧪 Starting Handshake Protocol Verification...")

        # 1. Setup Data
        # Ensure user exists
        from sqlalchemy import select
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            user = User(clerk_id="test_user", email="test@bridge.dev")
            db.add(user)
            await db.commit()
            print(f"Created Test User: {user.id}")

        # Ensure Bridge exists
        bridge_id = uuid.uuid4()
        bridge = Bridge(
            id=bridge_id,
            user_id=user.id,
            name="Test Bridge",
            domain="example.com",
            target_url="https://example.com",
            extraction_schema={}
        )
        db.add(bridge)
        try:
            await db.commit()
        except:
            await db.rollback()
            # Bridge might exist, ignore
            pass
        
        print(f"Bridge ID: {bridge.id}")

        # 2. Initiate Handshake
        req = HandshakeInitRequest(
            domain="example.com",
            method="EMAIL",
            recipient="contact@example.com",
            context="Testing Handshake"
        )
        
        logger.info("🤝 Initiating Handshake...")
        try:
            handshake = await initiate_handshake(req, user, db)
            print(f"✅ Handshake Created: {handshake.id} (Status: {handshake.status})")
            print(f"   Subject: {handshake.message_subject}")
            print(f"   Body: {handshake.message_body[:50]}...")
        except Exception as e:
            print(f"❌ Initiation Failed: {e}")
            return

        # 3. Approve Handshake
        logger.info("👍 Approving Handshake...")
        bg_tasks = BackgroundTasks()
        try:
            handshake = await approve_handshake(handshake.id, bg_tasks, user, db)
            print(f"✅ Handshake Approved: {handshake.id} (Status: {handshake.status})")
        except Exception as e:
            print(f"❌ Approval Failed: {e}")
            return

        # 4. Simulate Background Task
        logger.info("📨 Sending Message (Simulated)...")
        # We don't have SMTP creds, so it should log error or simulated failure
        await send_outreach_task(handshake.id)
        
        # 5. Verify Final Status
        await db.refresh(handshake)
        print(f"🏁 Final Status: {handshake.status}")
        print(f"   Error Log: {handshake.error_log}")

        # Clean up
        await db.delete(handshake)
        # await db.delete(bridge)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(verify())
