"""
OpenRouter provider (unified API for 100+ models).
Allows access to multiple providers through a single API.
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenRouterProvider(LLMProvider):
    """OpenRouter unified API provider"""
    
    AVAILABLE_MODELS = [
        "anthropic/claude-opus-4",
        "openai/gpt-4.5-turbo",
        "google/gemini-2.5-pro",
        "meta-llama/llama-3.3-70b-instruct",
        "mistralai/mistral-large-2"
    ]
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4.5-turbo"):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package required for OpenRouter")
        super().__init__(api_key, model)
        # OpenRouter uses OpenAI-compatible API
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using OpenRouter API"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            # Note: Not all OpenRouter models support JSON mode
            if response_format == "json":
                # Add to system message instead
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] += "\n\nRespond with valid JSON only."
                else:
                    messages.insert(0, {"role": "system", "content": "Respond with valid JSON only."})
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "openrouter"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        return 128000  # Varies by model
