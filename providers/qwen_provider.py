"""
Qwen (Alibaba) provider for DeepCode
"""

import requests
import json
from typing import Dict, Any, List
from .base_provider import LLMProvider, APIKeyError, ModelNotFoundError, RateLimitError, ProviderTimeoutError


class QwenProvider(LLMProvider):
    """Qwen (Alibaba DashScope) LLM provider"""
    
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    AVAILABLE_MODELS = [
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen-max-1201",
        "qwen-72b-chat",
        "qwen-14b-chat",
        "qwen-7b-chat",
        "qwen-coder-plus"
    ]
    
    def __init__(self, api_key: str, model_name: str = "qwen-turbo", **kwargs):
        """
        Initialize Qwen provider
        
        Args:
            api_key: Alibaba DashScope API key
            model_name: Model name to use
            **kwargs: Additional parameters
        """
        if not model_name:
            model_name = "qwen-turbo"
        
        super().__init__(api_key, model_name, **kwargs)
    
    def _validate_api_key(self):
        """Validate Qwen API key"""
        if not self.api_key or len(self.api_key) < 20:
            raise APIKeyError("Invalid Qwen API key")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using Qwen API
        
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
            'Accept': 'application/json'
        }
        
        payload = {
            'model': self.model_name,
            'input': {
                'messages': messages
            },
            'parameters': {
                'temperature': params['temperature'],
                'max_tokens': params['max_tokens'],
                'top_p': params['top_p'],
                'result_format': 'message'
            }
        }
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 401:
                raise APIKeyError("Invalid Qwen API key")
            elif response.status_code == 404:
                raise ModelNotFoundError(f"Model {self.model_name} not found")
            elif response.status_code == 429:
                raise RateLimitError("Qwen rate limit exceeded")
            elif response.status_code != 200:
                raise ProviderTimeoutError(f"Qwen API error: {response.status_code}")
            
            result = response.json()
            
            # Check for error in response
            if 'code' in result and result['code'] != '200':
                error_msg = result.get('message', 'Unknown error')
                raise ProviderTimeoutError(f"Qwen API error: {error_msg}")
            
            # Extract response
            output = result.get('output', {})
            if not output or 'text' not in output:
                raise ProviderTimeoutError("No response from Qwen API")
            
            generated_text = output['text']
            
            # Get usage information if available
            usage = result.get('usage', {})
            input_tokens = usage.get('input_tokens', self.estimate_tokens(prompt))
            output_tokens = usage.get('output_tokens', self.estimate_tokens(generated_text))
            total_tokens = usage.get('total_tokens', input_tokens + output_tokens)
            
            return {
                'text': generated_text,
                'model': self.model_name,
                'provider': 'qwen',
                'tokens_used': total_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'finish_reason': output.get('finish_reason', 'completed')
            }
            
        except requests.exceptions.Timeout:
            raise ProviderTimeoutError("Qwen API timeout")
        except requests.exceptions.RequestException as e:
            raise ProviderTimeoutError(f"Qwen API request error: {str(e)}")
        except json.JSONDecodeError:
            raise ProviderTimeoutError("Invalid JSON response from Qwen API")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Qwen models"""
        return self.AVAILABLE_MODELS.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Qwen model information"""
        model_info = super().get_model_info()
        
        context_lengths = {
            "qwen-turbo": 8192,
            "qwen-plus": 32768,
            "qwen-max": 8192,
            "qwen-max-1201": 8192,
            "qwen-72b-chat": 32768,
            "qwen-14b-chat": 8192,
            "qwen-7b-chat": 8192,
            "qwen-coder-plus": 16384
        }
        
        model_info.update({
            'context_length': context_lengths.get(self.model_name, 8192),
            'specialized_for': 'Multilingual processing, Chinese language, general purpose',
            'supports_function_calling': self.model_name in ['qwen-plus', 'qwen-max'],
            'supports_vision': False,
            'languages': ['Chinese', 'English', 'Japanese', 'Korean', 'Spanish', 'French', 'German']
        })
        return model_info