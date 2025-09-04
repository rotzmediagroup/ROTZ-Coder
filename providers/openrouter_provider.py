"""
OpenRouter provider for DeepCode
"""

import requests
import json
from typing import Dict, Any, List
from .base_provider import LLMProvider, APIKeyError, ModelNotFoundError, RateLimitError, ProviderTimeoutError


class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider for accessing various models"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    # Popular models available through OpenRouter
    AVAILABLE_MODELS = [
        "meta-llama/llama-2-70b-chat",
        "meta-llama/llama-2-13b-chat",
        "meta-llama/codellama-34b-instruct",
        "mistralai/mistral-7b-instruct",
        "mistralai/mixtral-8x7b-instruct",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-sonnet",
        "openai/gpt-3.5-turbo",
        "openai/gpt-4",
        "google/gemma-7b-it",
        "microsoft/wizardlm-2-8x22b",
        "qwen/qwen-72b-chat",
        "deepseek/deepseek-coder-33b-instruct"
    ]
    
    def __init__(self, api_key: str, model_name: str = "meta-llama/llama-2-70b-chat", **kwargs):
        """
        Initialize OpenRouter provider
        
        Args:
            api_key: OpenRouter API key
            model_name: Model name to use
            **kwargs: Additional parameters
        """
        if not model_name:
            model_name = "meta-llama/llama-2-70b-chat"
        
        super().__init__(api_key, model_name, **kwargs)
    
    def _validate_api_key(self):
        """Validate OpenRouter API key"""
        if not self.api_key or len(self.api_key) < 20:
            raise APIKeyError("Invalid OpenRouter API key")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using OpenRouter API
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generated text and metadata
        """
        # Merge parameters
        params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.95,
            **self.parameters,
            **kwargs
        }
        
        # Format messages
        messages = self.format_messages(prompt, kwargs.get('system_prompt'))
        
        # Prepare request
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://deepcode.ai',  # Required by OpenRouter
            'X-Title': 'DeepCode AI Research Engine'  # Optional but helpful
        }
        
        payload = {
            'model': self.model_name,
            'messages': messages,
            'temperature': params['temperature'],
            'max_tokens': params['max_tokens'],
            'top_p': params['top_p'],
            'stream': False
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 401:
                raise APIKeyError("Invalid OpenRouter API key")
            elif response.status_code == 404:
                raise ModelNotFoundError(f"Model {self.model_name} not found on OpenRouter")
            elif response.status_code == 429:
                raise RateLimitError("OpenRouter rate limit exceeded")
            elif response.status_code == 402:
                raise RateLimitError("OpenRouter credit limit exceeded")
            elif response.status_code != 200:
                raise ProviderTimeoutError(f"OpenRouter API error: {response.status_code}")
            
            result = response.json()
            
            # Check for error in response
            if 'error' in result:
                error_msg = result['error'].get('message', 'Unknown error')
                raise ProviderTimeoutError(f"OpenRouter API error: {error_msg}")
            
            # Extract response
            if 'choices' not in result or not result['choices']:
                raise ProviderTimeoutError("No response from OpenRouter API")
            
            generated_text = result['choices'][0]['message']['content']
            
            # Get usage information if available
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', self.estimate_tokens(prompt))
            output_tokens = usage.get('completion_tokens', self.estimate_tokens(generated_text))
            total_tokens = usage.get('total_tokens', input_tokens + output_tokens)
            
            return {
                'text': generated_text,
                'model': self.model_name,
                'provider': 'openrouter',
                'tokens_used': total_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'finish_reason': result['choices'][0].get('finish_reason', 'unknown')
            }
            
        except requests.exceptions.Timeout:
            raise ProviderTimeoutError("OpenRouter API timeout")
        except requests.exceptions.RequestException as e:
            raise ProviderTimeoutError(f"OpenRouter API request error: {str(e)}")
        except json.JSONDecodeError:
            raise ProviderTimeoutError("Invalid JSON response from OpenRouter API")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from OpenRouter"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/models",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                models_data = response.json()
                return [model['id'] for model in models_data.get('data', [])]
            else:
                # Fall back to static list if API call fails
                return self.AVAILABLE_MODELS.copy()
                
        except Exception:
            # Fall back to static list if API call fails
            return self.AVAILABLE_MODELS.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        model_info = super().get_model_info()
        
        # Context lengths vary by model
        context_lengths = {
            "meta-llama/llama-2-70b-chat": 4096,
            "meta-llama/llama-2-13b-chat": 4096,
            "meta-llama/codellama-34b-instruct": 16384,
            "mistralai/mistral-7b-instruct": 8192,
            "mistralai/mixtral-8x7b-instruct": 32768,
            "anthropic/claude-3-haiku": 200000,
            "anthropic/claude-3-sonnet": 200000,
            "openai/gpt-3.5-turbo": 16385,
            "openai/gpt-4": 8192,
            "google/gemma-7b-it": 8192,
            "microsoft/wizardlm-2-8x22b": 65536,
            "qwen/qwen-72b-chat": 32768,
            "deepseek/deepseek-coder-33b-instruct": 16384
        }
        
        model_info.update({
            'context_length': context_lengths.get(self.model_name, 4096),
            'specialized_for': 'Varies by model - access to various open-source and proprietary models',
            'supports_function_calling': 'gpt-4' in self.model_name or 'claude' in self.model_name,
            'supports_vision': False  # Most models don't support vision
        })
        return model_info
    
    def get_model_pricing(self) -> Dict[str, float]:
        """Get pricing information for the current model"""
        # This would fetch real pricing from OpenRouter API
        # For now, return placeholder values
        return {
            'input_cost_per_1k_tokens': 0.001,
            'output_cost_per_1k_tokens': 0.002,
            'currency': 'USD'
        }