"""
Mistral AI provider implementation.
Supports: Mistral Large 2, Medium 3, Codestral
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False


class MistralProvider(LLMProvider):
    """Mistral AI API provider"""
    
    AVAILABLE_MODELS = [
        "mistral-large-2",
        "mistral-medium-3",
        "mistral-small",
        "codestral-latest"
    ]
    
    def __init__(self, api_key: str, model: str = "mistral-large-2"):
        if not MISTRAL_AVAILABLE:
            raise ImportError("mistralai package not installed. Run: poetry add mistralai")
        super().__init__(api_key, model)
        self.client = Mistral(api_key=api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using Mistral API"""
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
            
            response = self.client.chat.complete(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "mistral"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        return 128000
