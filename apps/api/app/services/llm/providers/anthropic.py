"""
Anthropic (Claude) provider implementation.
Supports: Claude Opus 4.6, Sonnet 4.5, Haiku 4.5
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    AVAILABLE_MODELS = [
        "claude-opus-4.6",
        "claude-sonnet-4.5",
        "claude-haiku-4.5",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
       "claude-3-haiku-20240307"
    ]
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4.5"):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: poetry add anthropic")
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using Anthropic API"""
        try:
            # Separate system message if present
            system_msg = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append(msg)
            
            kwargs = {
                "model": self.model,
                "messages": user_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
            }
            
            if system_msg:
                kwargs["system"] = system_msg
            
            response = self.client.messages.create(**kwargs)
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "anthropic"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        # Claude Opus 4.6 has 1M token context
        return 1000000 if "opus-4" in self.model else 200000
