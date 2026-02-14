"""
OpenAI provider implementation.
Supports: GPT-5.2 Instant, GPT-4.5 Turbo, o1, o1-mini
"""
import openai
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    AVAILABLE_MODELS = [
        "gpt-5.2-instant",
        "gpt-4.5-turbo",
        "gpt-4o-mini",
        "gpt-4o",
        "o1",
        "o1-mini"
    ]
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.client = openai.OpenAI(api_key=api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using OpenAI API"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "openai"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        context_limits = {
            "gpt-5.2-instant": 128000,
            "gpt-4.5-turbo": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4o": 128000,
            "o1": 200000,
            "o1-mini": 128000,
        }
        return context_limits.get(self.model, 128000)
