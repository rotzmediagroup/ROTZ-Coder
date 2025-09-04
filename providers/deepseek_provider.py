"""
DeepSeek provider for DeepCode
"""

import requests
import json
from typing import Dict, Any, List
from .base_provider import LLMProvider, APIKeyError, ModelNotFoundError, RateLimitError, ProviderTimeoutError


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider"""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    AVAILABLE_MODELS = [
        "deepseek-coder",
        "deepseek-coder-33b-instruct",
        "deepseek-coder-7b-instruct",
        "deepseek-chat"
    ]
    
    def __init__(self, api_key: str, model_name: str = "deepseek-coder", **kwargs):
        """
        Initialize DeepSeek provider
        
        Args:
            api_key: DeepSeek API key
            model_name: Model name to use
            **kwargs: Additional parameters
        """
        if not model_name:
            model_name = "deepseek-coder"
        
        super().__init__(api_key, model_name, **kwargs)
    
    def _validate_api_key(self):
        """Validate DeepSeek API key"""
        if not self.api_key or len(self.api_key) < 20:
            raise APIKeyError("Invalid DeepSeek API key")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using DeepSeek API
        
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
            'Content-Type': 'application/json'
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
                raise APIKeyError("Invalid DeepSeek API key")
            elif response.status_code == 404:
                raise ModelNotFoundError(f"Model {self.model_name} not found")
            elif response.status_code == 429:
                raise RateLimitError("DeepSeek rate limit exceeded")
            elif response.status_code != 200:
                raise ProviderTimeoutError(f"DeepSeek API error: {response.status_code}")
            
            result = response.json()
            
            # Extract response
            if 'choices' not in result or not result['choices']:
                raise ProviderTimeoutError("No response from DeepSeek API")
            
            generated_text = result['choices'][0]['message']['content']
            
            # Calculate tokens (approximate)
            input_tokens = self.estimate_tokens(prompt)
            output_tokens = self.estimate_tokens(generated_text)
            
            return {
                'text': generated_text,
                'model': self.model_name,
                'provider': 'deepseek',
                'tokens_used': input_tokens + output_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'finish_reason': result['choices'][0].get('finish_reason', 'unknown')
            }
            
        except requests.exceptions.Timeout:
            raise ProviderTimeoutError("DeepSeek API timeout")
        except requests.exceptions.RequestException as e:
            raise ProviderTimeoutError(f"DeepSeek API request error: {str(e)}")
        except json.JSONDecodeError:
            raise ProviderTimeoutError("Invalid JSON response from DeepSeek API")
    
    def get_available_models(self) -> List[str]:
        """Get list of available DeepSeek models"""
        return self.AVAILABLE_MODELS.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get DeepSeek model information"""
        model_info = super().get_model_info()
        model_info.update({
            'context_length': 16384,  # DeepSeek context length
            'specialized_for': 'Code generation and understanding',
            'supports_function_calling': False,
            'supports_vision': False
        })
        return model_info