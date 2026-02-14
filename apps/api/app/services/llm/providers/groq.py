"""
Groq provider implementation (uses OpenAI-compatible API).
Fast LPU inference for Llama, Mixtral models.
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqProvider(LLMProvider):
    """Groq fast inference API provider"""
    
    AVAILABLE_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Run: poetry add groq")
        super().__init__(api_key, model)
        self.client = Groq(api_key=api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using Groq API"""
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
            logger.error(f"Groq API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "groq"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        # Most Groq models have 32k context, except the large ones
        if "32768" in self.model:
            return 32768
        return 8192
