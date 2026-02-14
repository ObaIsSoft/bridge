"""
LLM Failover Manager.
Handles provider selection, automatic failover, and failure tracking.
"""
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LLMProviderConfig
from app.services.llm.base import LLMProvider
from app.services.llm.providers.openai import OpenAIProvider
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.google import GoogleProvider
from app.services.llm.providers.mistral import MistralProvider
from app.services.llm.providers.cohere import CohereProvider
from app.services.llm.providers.groq import GroqProvider
from app.services.llm.providers.openrouter import OpenRouterProvider
from app.services.llm.providers.ollama import OllamaProvider
from app.core.encryption import decrypt_api_key

logger = logging.getLogger(__name__)


class LLMFailoverManager:
    """Manages LLM provider selection and automatic failover"""
    
    PROVIDER_CLASSES = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "mistral": MistralProvider,
        "cohere": CohereProvider,
        "groq": GroqProvider,
        "openrouter": OpenRouterProvider,
        "ollama": OllamaProvider,
    }
    
    MAX_CONSECUTIVE_FAILURES = 5
    FAILURE_COOLDOWN_MINUTES = 5
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_provider(self, user_id: UUID) -> tuple[LLMProvider, UUID]:
        """
        Get the next available LLM provider for user.
        Returns (provider_instance, provider_config_id)
        
        Skips providers that:
        - Are not active
        - Have >MAX_CONSECUTIVE_FAILURES
        - Failed in last FAILURE_COOLDOWN_MINUTES
        """
        stmt = select(LLMProviderConfig).where(
            LLMProviderConfig.user_id == user_id,
            LLMProviderConfig.is_active == True,
            LLMProviderConfig.consecutive_failures < self.MAX_CONSECUTIVE_FAILURES
        ).order_by(
            LLMProviderConfig.priority.asc(),
            LLMProviderConfig.last_used_at.asc().nullsfirst()
        )
        
        result = await self.db.execute(stmt)
        configs = result.scalars().all()
        
        if not configs:
            raise Exception("No active LLM providers configured for user")
        
        # Filter out recently failed providers
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.FAILURE_COOLDOWN_MINUTES)
        
        for config in configs:
            # Skip if recently failed
            if config.last_error and config.updated_at and config.updated_at > cutoff_time:
                continue
            
            # Try to create provider instance
            try:
                provider_class = self.PROVIDER_CLASSES.get(config.provider)
                if not provider_class:
                    logger.warning(f"Unknown provider: {config.provider}")
                    continue
                
                # Decrypt API key
                api_key = decrypt_api_key(config.api_key_encrypted)
                
                provider = provider_class(api_key=api_key, model=config.model)
                return provider, config.id
                
            except Exception as e:
                logger.error(f"Failed to initialize provider {config.provider}: {e}")
                await self.mark_failure(config.id, str(e))
                continue
        
        raise Exception("No available LLM providers (all failed or on cooldown)")
    
    async def mark_success(self, provider_id: UUID):
        """Reset failure count on successful call"""
        config = await self.db.get(LLMProviderConfig, provider_id)
        if config:
            config.consecutive_failures = 0
            config.last_error = None
            config.last_used_at = datetime.utcnow()
            config.updated_at = datetime.utcnow()
            await self.db.commit()
    
    async def mark_failure(self, provider_id: UUID, error: str):
        """Increment failure count, disable if >MAX_CONSECUTIVE_FAILURES"""
        config = await self.db.get(LLMProviderConfig, provider_id)
        if config:
            config.consecutive_failures += 1
            config.last_error = error[:500]  # Truncate
            config.updated_at = datetime.utcnow()
            
            if config.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                config.is_active = False
                logger.warning(
                    f"Disabled provider {config.provider} after {config.consecutive_failures} failures"
                )
            
            await self.db.commit()


async def get_llm_for_user(user_id: UUID, db: AsyncSession) -> LLMProvider:
    """
    Convenience function to get an LLM provider for a user.
    Handles failover automatically.
    """
    manager = LLMFailoverManager(db)
    provider, _ = await manager.get_provider(user_id)
    return provider
