"""
Base class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model_name: str = None, **kwargs):
        """
        Initialize the LLM provider
        
        Args:
            api_key: API key for the provider
            model_name: Name of the model to use
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key
        self.model_name = model_name
        self.parameters = kwargs
        self._validate_api_key()
    
    @abstractmethod
    def _validate_api_key(self):
        """Validate the API key format"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using the LLM
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generated text and metadata
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this provider
        
        Returns:
            List of model names
        """
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for given text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def get_provider_name(self) -> str:
        """Get the provider name"""
        return self.__class__.__name__.lower().replace('provider', '')
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dict containing model information
        """
        return {
            'provider': self.get_provider_name(),
            'model': self.model_name,
            'parameters': self.parameters
        }
    
    def format_messages(self, prompt: str, system_prompt: str = None) -> List[Dict[str, str]]:
        """
        Format prompt into messages format used by most APIs
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return messages


class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    pass


class APIKeyError(LLMProviderError):
    """Raised when API key is invalid"""
    pass


class ModelNotFoundError(LLMProviderError):
    """Raised when model is not found"""
    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded"""
    pass


class ProviderTimeoutError(LLMProviderError):
    """Raised when provider request times out"""
    pass