import asyncio
from celery import shared_task
from app.core.celery import celery_app
from app.services.crawler import CrawlerService
from app.services.extractor import ExtractionService
from app.core.database import AsyncSessionLocal
from app.models import Bridge, UsageLog
from sqlalchemy import select
from datetime import datetime
import time
import logging
import httpx
from app.models import Bridge, UsageLog, Webhook, WebhookLog
import nest_asyncio
nest_asyncio.apply()

logger = logging.getLogger(__name__)

@celery_app.task(name="app.services.tasks.run_extraction_task")
def run_extraction_task(bridge_id: str, user_id: str):
    """
    Background task to run website extraction using Playwright and OpenAI.
    Since Celery is synchronous by default, we use asyncio.run to execute our async services.
    """
    return asyncio.run(_perform_extraction(bridge_id, user_id))

async def _fire_webhooks(db, user_id, event_type, payload):
    """Fire registered webhooks for a specific event."""
    result = await db.execute(select(Webhook).where(Webhook.user_id == user_id, Webhook.is_active == True))
    webhooks = result.scalars().all()
    
    async with httpx.AsyncClient() as client:
        for webhook in webhooks:
            if event_type in webhook.events:
                start_time = time.time()
                try:
                    resp = await client.post(webhook.url, json={
                        "event": event_type,
                        "timestamp": datetime.utcnow().isoformat(),
                        "payload": payload
                    }, timeout=10)
                    
                    status_code = resp.status_code
                    resp_body = resp.text[:1000]
                except Exception as e:
                    status_code = 500
                    resp_body = str(e)
                
                latency = int((time.time() - start_time) * 1000)
                
                # Log webhook attempt
                log = WebhookLog(
                    webhook_id=webhook.id,
                    event_type=event_type,
                    payload=payload,
                    status_code=status_code,
                    response_body=resp_body,
                    latency_ms=latency
                )
                db.add(log)
    await db.commit()

async def _perform_extraction(bridge_id: str, user_id: str):
    start_time = time.time()
    async with AsyncSessionLocal() as db:
        try:
            bridge = await db.get(Bridge, bridge_id)
            if not bridge:
                logger.error(f"Bridge {bridge_id} not found for extraction task")
                return {"status": "error", "message": "Bridge not found"}

            crawler = CrawlerService()
            extractor = ExtractionService()

            html, new_session_data = await crawler.get_page_content(
                url=bridge.target_url,
                auth_config=bridge.auth_config,
                interaction_script=bridge.interaction_script,
                session_data=bridge.session_data
            )
            if not html:
                raise Exception("Failed to crawl target URL")
            
            # Save new session data (Persist cookies for next run)
            if new_session_data:
                bridge.session_data = new_session_data
                db.add(bridge) # Ensure update is tracked
                logger.info(f"Updated session data for bridge {bridge.id}")

            data = await extractor.extract_structured_data(html, bridge.extraction_schema)
            
            # 4. Deduplication (State Engine)
            from app.services.state import StateService
            state_service = StateService()
            try:
                is_seen = await state_service.is_seen(bridge_id, data)
                if is_seen:
                    logger.info(f"Duplicate data detected for bridge {bridge_id}. Skipping.")
                    await state_service.close()
                    return {
                        "status": "skipped",
                        "reason": "duplicate_data",
                        "bridge_id": str(bridge.id),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Mark as seen for next time
                await state_service.mark_seen(bridge_id, data)
            finally:
                await state_service.close()
            latency_ms = int((time.time() - start_time) * 1000)

            # Update bridge status
            bridge.last_successful_extraction = datetime.utcnow()
            bridge.last_error = None

            # Record usage log
            usage_log = UsageLog(
                user_id=user_id,
                bridge_id=bridge.id,
                method="TASK",
                path=f"/bridges/{bridge.id}/extract",
                status_code=200,
                latency_ms=latency_ms
            )
            db.add(usage_log)
            await db.commit()

            # Trigger Webhooks
            await _fire_webhooks(db, user_id, "extraction.success", {
                "bridge_id": str(bridge.id),
                "data": data
            })

            return {
                "status": "success",
                "bridge_id": str(bridge.id),
                "data": data,
                "timestamp": bridge.last_successful_extraction.isoformat()
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Extraction task failed for bridge {bridge_id}: {e}")
            
            # Re-fetch bridge to ensure we're on a clean session state
            bridge = await db.get(Bridge, bridge_id)
            if bridge:
                bridge.last_error = str(e)
                
                usage_log = UsageLog(
                    user_id=user_id,
                    bridge_id=bridge.id,
                    method="TASK",
                    path=f"/bridges/{bridge.id}/extract",
                    status_code=500,
                    latency_ms=latency_ms
                )
                db.add(usage_log)
                await db.commit()
                
                # Trigger Webhooks
                await _fire_webhooks(db, user_id, "extraction.failed", {
                    "bridge_id": str(bridge.id),
                    "error": str(e)
                })

            return {"status": "error", "message": str(e)}
