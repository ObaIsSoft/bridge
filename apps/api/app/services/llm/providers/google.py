"""
Google Gemini provider implementation.
Supports: Gemini 3 Deep Think, Gemini 2.5 Pro, Gemini 2.5 Flash
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleProvider(LLMProvider):
    """Google Gemini API provider"""
    
    AVAILABLE_MODELS = [
        "gemini-3-deep-think",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not GOOGLE_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Run: poetry add google-generativeai")
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.model_instance = genai.GenerativeModel(model)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion using Google Gemini API"""
        try:
            # Convert messages to Gemini format
            prompt_parts = []
            for msg in messages:
                role_prefix = f"{msg['role']}: " if msg['role'] != 'user' else ""
                prompt_parts.append(f"{role_prefix}{msg['content']}")
            
            prompt = "\n\n".join(prompt_parts)
            
            generation_config = {
                "temperature": temperature,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "google"
    
    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS
    
    def get_max_context_length(self) -> int:
        # Gemini 2.5 has up to 1M tokens
        if "2.5" in self.model or "3" in self.model:
            return 1000000
        return 128000
