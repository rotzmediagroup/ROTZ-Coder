"""
LLM Provider Factory for DeepCode
"""

from typing import Dict, Any, Optional, Type
from .base_provider import LLMProvider, APIKeyError, ModelNotFoundError
from .deepseek_provider import DeepSeekProvider
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider
from .qwen_provider import QwenProvider
from .grok_provider import GrokProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances"""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        'deepseek': DeepSeekProvider,
        'gemini': GeminiProvider,
        'openrouter': OpenRouterProvider,
        'qwen': QwenProvider,
        'grok': GrokProvider
    }
    
    # Default models for each provider
    _default_models = {
        'deepseek': 'deepseek-coder',
        'gemini': 'gemini-pro',
        'openrouter': 'meta-llama/llama-2-70b-chat',
        'qwen': 'qwen-turbo',
        'grok': 'grok-1'
    }
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: str, 
                       model_name: str = None, **kwargs) -> LLMProvider:
        """
        Create a provider instance
        
        Args:
            provider_name: Name of the provider
            api_key: API key for the provider
            model_name: Optional model name
            **kwargs: Additional provider parameters
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider not found
            APIKeyError: If API key is invalid
        """
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(f"Provider '{provider_name}' not found. Available: {available}")
        
        provider_class = cls._providers[provider_name]
        
        # Use default model if not specified
        if not model_name:
            model_name = cls._default_models.get(provider_name)
        
        try:
            return provider_class(api_key=api_key, model_name=model_name, **kwargs)
        except Exception as e:
            if "api key" in str(e).lower():
                raise APIKeyError(f"Invalid API key for {provider_name}: {str(e)}")
            else:
                raise
    
    @classmethod
    def get_provider_info(cls, provider_name: str) -> Dict[str, Any]:
        """
        Get information about a provider
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Dict containing provider information
        """
        if provider_name not in cls._providers:
            return {}
        
        provider_class = cls._providers[provider_name]
        
        # Get available models (this requires an API key, so we'll use the class attribute if available)
        available_models = []
        if hasattr(provider_class, 'AVAILABLE_MODELS'):
            available_models = provider_class.AVAILABLE_MODELS
        
        return {
            'name': provider_name,
            'class': provider_class.__name__,
            'default_model': cls._default_models.get(provider_name),
            'available_models': available_models,
            'description': provider_class.__doc__ or f"{provider_name.title()} LLM provider"
        }
    
    @classmethod
    def get_all_provider_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about all available providers"""
        return {
            provider: cls.get_provider_info(provider) 
            for provider in cls._providers.keys()
        }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider], 
                         default_model: str = None):
        """
        Register a new provider
        
        Args:
            name: Provider name
            provider_class: Provider class
            default_model: Default model for this provider
        """
        cls._providers[name] = provider_class
        if default_model:
            cls._default_models[name] = default_model
    
    @classmethod
    def validate_provider_config(cls, provider_name: str, api_key: str, 
                                model_name: str = None) -> Dict[str, Any]:
        """
        Validate a provider configuration without creating an instance
        
        Args:
            provider_name: Name of the provider
            api_key: API key to validate
            model_name: Model name to validate
            
        Returns:
            Dict with validation results
        """
        result = {
            'valid': False,
            'error': None,
            'provider_exists': provider_name in cls._providers,
            'model_supported': False
        }
        
        if not result['provider_exists']:
            result['error'] = f"Provider '{provider_name}' not found"
            return result
        
        try:
            # Try to create provider instance
            provider = cls.create_provider(provider_name, api_key, model_name)
            
            # Check if model is supported
            available_models = provider.get_available_models()
            result['model_supported'] = not model_name or model_name in available_models
            
            if not result['model_supported']:
                result['error'] = f"Model '{model_name}' not supported by {provider_name}"
                return result
            
            result['valid'] = True
            
        except APIKeyError as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = f"Provider validation error: {str(e)}"
        
        return result


# Add support for existing OpenAI and Anthropic providers
try:
    from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
    from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
    
    # Wrapper classes to make existing providers compatible
    class OpenAIProviderWrapper(LLMProvider):
        """Wrapper for OpenAI provider"""
        
        AVAILABLE_MODELS = [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
        
        def __init__(self, api_key: str, model_name: str = "gpt-4-turbo-preview", **kwargs):
            super().__init__(api_key, model_name, **kwargs)
            self.client = OpenAIAugmentedLLM(api_key=api_key)
        
        def _validate_api_key(self):
            if not self.api_key or not self.api_key.startswith('sk-'):
                raise APIKeyError("Invalid OpenAI API key")
        
        def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
            # This would need to be adapted based on the actual OpenAIAugmentedLLM interface
            # For now, return a mock response
            return {
                'text': f"OpenAI response for: {prompt[:50]}...",
                'model': self.model_name,
                'provider': 'openai',
                'tokens_used': self.estimate_tokens(prompt) + 100,
                'input_tokens': self.estimate_tokens(prompt),
                'output_tokens': 100,
                'finish_reason': 'completed'
            }
        
        def get_available_models(self) -> list[str]:
            return self.AVAILABLE_MODELS.copy()
    
    
    class AnthropicProviderWrapper(LLMProvider):
        """Wrapper for Anthropic provider"""
        
        AVAILABLE_MODELS = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        
        def __init__(self, api_key: str, model_name: str = "claude-3-sonnet-20240229", **kwargs):
            super().__init__(api_key, model_name, **kwargs)
            self.client = AnthropicAugmentedLLM(api_key=api_key)
        
        def _validate_api_key(self):
            if not self.api_key or not self.api_key.startswith('sk-ant-'):
                raise APIKeyError("Invalid Anthropic API key")
        
        def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
            # This would need to be adapted based on the actual AnthropicAugmentedLLM interface
            # For now, return a mock response
            return {
                'text': f"Claude response for: {prompt[:50]}...",
                'model': self.model_name,
                'provider': 'anthropic',
                'tokens_used': self.estimate_tokens(prompt) + 150,
                'input_tokens': self.estimate_tokens(prompt),
                'output_tokens': 150,
                'finish_reason': 'completed'
            }
        
        def get_available_models(self) -> list[str]:
            return self.AVAILABLE_MODELS.copy()
    
    # Register the existing providers
    LLMProviderFactory.register_provider('openai', OpenAIProviderWrapper, 'gpt-4-turbo-preview')
    LLMProviderFactory.register_provider('anthropic', AnthropicProviderWrapper, 'claude-3-sonnet-20240229')
    
except ImportError:
    # If the existing providers aren't available, skip them
    pass