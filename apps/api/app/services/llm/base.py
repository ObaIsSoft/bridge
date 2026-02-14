"""
Abstract base class for LLM providers.
All provider adapters must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LLMProvider(ABC):
    """Base class for all LLM provider implementations"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        response_format: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion from messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            response_format: "json" for JSON mode, None for text
            max_tokens: Maximum tokens in response
            
        Returns:
            String response from the model
            
        Raises:
            Exception: On API errors, rate limits, invalid requests
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier (e.g., 'openai', 'anthropic')"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """List models available for this provider"""
        pass
    
    def get_max_context_length(self) -> int:
        """Return maximum context window for current model"""
        return 128000  # Default, override in subclasses
