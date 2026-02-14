"""
Ollama provider for local models.
Supports self-hosted LLMs like Llama3, Mistral, Qwen, etc.
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class OllamaProvider(LLMProvider):
    """Ollama local model provider"""
    
    AVAILABLE_MODELS = [
        "llama3.3",
        "llama3.1",
        "mistral",
        "qwen2.5",
        "deepseek-r1",
        "codellama"
    ]
    
    def __init__(self, api_key: str = "ollama", model: str = "llama3.3", base_url: str = "http://localhost:11434"):
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx package required for Ollama")
        # Ollama doesn't use API keys, but we keep the interface consistent
        super().__init__(api_key, model)
        self.base_url = base_url
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using local Ollama instance"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            # Ollama doesn't have native JSON mode; add to prompt
            if response_format == "json" and messages:
                messages[-1]["content"] += "\n\nRespond with valid JSON only."
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                return result["message"]["content"]
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "ollama"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        return 128000  # Depends on model, but most support this
