"""
Cohere provider implementation.
Supports: Command R+, Command R, Command R7B
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False


class CohereProvider(LLMProvider):
    """Cohere API provider"""
    
    AVAILABLE_MODELS = [
        "command-r-plus",
        "command-r",
        "command-r-7b"
    ]
    
    def __init__(self, api_key: str, model: str = "command-r"):
        if not COHERE_AVAILABLE:
            raise ImportError("cohere package not installed. Run: poetry add cohere")
        super().__init__(api_key, model)
        self.client = cohere.ClientV2(api_key=api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using Cohere API"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            # Cohere doesn't have native JSON mode, we add instructions instead
            if response_format == "json" and messages:
                messages[-1]["content"] += "\n\nRespond with valid JSON only."
            
            response = self.client.chat(**kwargs)
            return response.message.content[0].text
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "cohere"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        return 128000
