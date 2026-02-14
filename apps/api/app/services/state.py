
import hashlib
import json
import logging
import os
import redis.asyncio as redis
from typing import Any, Optional

logger = logging.getLogger(__name__)

class StateService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = redis.from_url(self.redis_url, decode_responses=True)

    def _generate_hash(self, data: Any) -> str:
        """Generate a consistent SHA256 hash from a dictionary or string."""
        if isinstance(data, dict) or isinstance(data, list):
            # Sort keys to ensure consistent JSON string
            encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        else:
            encoded = str(data).encode("utf-8")
        
        return hashlib.sha256(encoded).hexdigest()

    async def is_seen(self, context_id: str, data: Any) -> bool:
        """
        Check if this data has been seen before for the given context (bridge_id).
        Returns True if duplicate.
        """
        try:
            data_hash = self._generate_hash(data)
            key = f"bridge:state:{context_id}:{data_hash}"
            
            exists = await self.redis.exists(key)
            return bool(exists)
        except Exception as e:
            logger.warning(f"State Engine unavailable (Redis error): {e}")
            return False

    async def mark_seen(self, context_id: str, data: Any, ttl: int = 86400 * 7):
        """
        Mark data as seen with a TTL (default 7 days).
        """
        try:
            data_hash = self._generate_hash(data)
            key = f"bridge:state:{context_id}:{data_hash}"
            
            # Store a simple timestamp or metadata
            await self.redis.set(key, "seen", ex=ttl)
            logger.info(f"Marked state as seen: {key}")
        except Exception as e:
            logger.warning(f"State Engine failed to save state: {e}")

    async def close(self):
        try:
            await self.redis.close()
        except:
            pass
