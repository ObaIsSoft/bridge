"""
API endpoints for LLM provider management.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import validate_api_key
from app.models import LLMProviderConfig, ApiKey
from app.core.encryption import encrypt_api_key, mask_api_key

router = APIRouter(prefix="/api/v1/llm", tags=["LLM Providers"])


# Schemas
class LLMProviderCreate(BaseModel):
    provider: str = Field(..., description="Provider name: openai, anthropic, google, etc.")
    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(..., description="Model to use (e.g., gpt-4o-mini, claude-sonnet-4.5)")
    priority: int = Field(default=0, description="Priority (lower = higher priority)")


class LLMProviderResponse(BaseModel):
    id: UUID
    provider: str
    model: str
    priority: int
    is_active: bool
    consecutive_failures: int
    last_used_at: str | None
    last_error: str | None
    
    class Config:
        from_attributes = True


class LLMProviderTestRequest(BaseModel):
    provider: str
    api_key: str
    model: str


# Endpoints
@router.get("/providers", response_model=List[LLMProviderResponse])
async def list_providers(
    api_key: ApiKey = Depends(validate_api_key),
    db: AsyncSession = Depends(get_db)
):
    """List all LLM providers configured for the current user"""
    result = await db.execute(
        select(LLMProviderConfig)
        .where(LLMProviderConfig.user_id == api_key.user_id)
        .order_by(LLMProviderConfig.priority)
    )
    providers = result.scalars().all()
    
    return [
        LLMProviderResponse(
            id=p.id,
            provider=p.provider,
            model=p.model,
            priority=p.priority,
            is_active=p.is_active,
            consecutive_failures=p.consecutive_failures,
            last_used_at=p.last_used_at.isoformat() if p.last_used_at else None,
            last_error=p.last_error
        )
        for p in providers
    ]


@router.post("/providers", response_model=LLMProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: LLMProviderCreate,
    api_key: ApiKey = Depends(validate_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Add a new LLM provider configuration"""
    # Encrypt API key before storing
    encrypted_key = encrypt_api_key(provider_data.api_key)
    
    logger.info(f"Creating LLM provider {provider_data.provider} with key {mask_api_key(provider_data.api_key)}")
    
    new_provider = LLMProviderConfig(
        user_id=api_key.user_id,
        provider=provider_data.provider,
        api_key_encrypted=encrypted_key,
        model=provider_data.model,
        priority=provider_data.priority
    )
    
    db.add(new_provider)
    await db.commit()
    await db.refresh(new_provider)
    
    return LLMProviderResponse(
        id=new_provider.id,
        provider=new_provider.provider,
        model=new_provider.model,
        priority=new_provider.priority,
        is_active=new_provider.is_active,
        consecutive_failures=new_provider.consecutive_failures,
        last_used_at=None,
        last_error=None
    )


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: UUID,
    api_key: ApiKey = Depends(validate_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Delete an LLM provider configuration"""
    provider = await db.get(LLMProviderConfig, provider_id)
    
    if not provider or provider.user_id != api_key.user_id:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    await db.delete(provider)
    await db.commit()
    
    return None


@router.post("/providers/test")
async def test_provider(
    test_data: LLMProviderTestRequest,
     api_key: ApiKey = Depends(validate_api_key)
):
    """Test if a provider configuration works"""
    try:
        # Import providers dynamically
        from app.services.llm.providers.openai import OpenAIProvider
        from app.services.llm.providers.anthropic import AnthropicProvider
        from app.services.llm.providers.google import GoogleProvider
        from app.services.llm.providers.mistral import MistralProvider
        from app.services.llm.providers.cohere import CohereProvider
        from app.services.llm.providers.groq import GroqProvider
        from app.services.llm.providers.openrouter import OpenRouterProvider
        from app.services.llm.providers.ollama import OllamaProvider
        
        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
            "mistral": MistralProvider,
            "cohere": CohereProvider,
            "groq": GroqProvider,
            "openrouter": OpenRouterProvider,
            "ollama": OllamaProvider,
        }
        
        ProviderClass = provider_map.get(test_data.provider)
        if not ProviderClass:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {test_data.provider}")
        
        # Test the provider
        provider = ProviderClass(api_key=test_data.api_key, model=test_data.model)
        
        # Simple test prompt
        import time
        start = time.time()
        result = await provider.complete(
            messages=[{"role": "user", "content": "Say 'test successful' in JSON format"}],
            temperature=0,
            response_format="json"
        )
        latency_ms = int((time.time() - start) * 1000)
        
        return {
            "status": "success",
            "latency_ms": latency_ms,
            "response": result[:100]  # Truncated
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
