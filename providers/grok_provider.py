"""
Grok (xAI) provider for DeepCode
"""

import requests
import json
from typing import Dict, Any, List
from .base_provider import LLMProvider, APIKeyError, ModelNotFoundError, RateLimitError, ProviderTimeoutError


class GrokProvider(LLMProvider):
    """Grok (xAI) LLM provider"""
    
    BASE_URL = "https://api.x.ai/v1"
    
    AVAILABLE_MODELS = [
        "grok-1",
        "grok-1.5",
        "grok-1.5-vision",
        "grok-beta"
    ]
    
    def __init__(self, api_key: str, model_name: str = "grok-1", **kwargs):
        """
        Initialize Grok provider
        
        Args:
            api_key: xAI API key
            model_name: Model name to use
            **kwargs: Additional parameters
        """
        if not model_name:
            model_name = "grok-1"
        
        super().__init__(api_key, model_name, **kwargs)
    
    def _validate_api_key(self):
        """Validate xAI API key"""
        if not self.api_key or len(self.api_key) < 20:
            raise APIKeyError("Invalid xAI API key")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using Grok API
        
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
                raise APIKeyError("Invalid xAI API key")
            elif response.status_code == 404:
                raise ModelNotFoundError(f"Model {self.model_name} not found")
            elif response.status_code == 429:
                raise RateLimitError("xAI rate limit exceeded")
            elif response.status_code != 200:
                raise ProviderTimeoutError(f"xAI API error: {response.status_code}")
            
            result = response.json()
            
            # Check for error in response
            if 'error' in result:
                error_msg = result['error'].get('message', 'Unknown error')
                raise ProviderTimeoutError(f"xAI API error: {error_msg}")
            
            # Extract response
            if 'choices' not in result or not result['choices']:
                raise ProviderTimeoutError("No response from xAI API")
            
            generated_text = result['choices'][0]['message']['content']
            
            # Get usage information if available
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', self.estimate_tokens(prompt))
            output_tokens = usage.get('completion_tokens', self.estimate_tokens(generated_text))
            total_tokens = usage.get('total_tokens', input_tokens + output_tokens)
            
            return {
                'text': generated_text,
                'model': self.model_name,
                'provider': 'grok',
                'tokens_used': total_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'finish_reason': result['choices'][0].get('finish_reason', 'completed')
            }
            
        except requests.exceptions.Timeout:
            raise ProviderTimeoutError("xAI API timeout")
        except requests.exceptions.RequestException as e:
            raise ProviderTimeoutError(f"xAI API request error: {str(e)}")
        except json.JSONDecodeError:
            raise ProviderTimeoutError("Invalid JSON response from xAI API")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Grok models"""
        return self.AVAILABLE_MODELS.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Grok model information"""
        model_info = super().get_model_info()
        
        context_lengths = {
            "grok-1": 131072,      # 128k context
            "grok-1.5": 131072,    # 128k context
            "grok-1.5-vision": 131072,  # 128k context
            "grok-beta": 131072    # 128k context
        }
        
        model_info.update({
            'context_length': context_lengths.get(self.model_name, 131072),
            'specialized_for': 'Real-time information, reasoning, humor, creative writing',
            'supports_function_calling': False,  # May change as Grok develops
            'supports_vision': 'vision' in self.model_name.lower(),
            'real_time_data': True,  # Grok has access to X (Twitter) data
            'training_cutoff': None  # Grok has real-time access
        })
        return model_info
    
    def generate_with_context(self, prompt: str, context_type: str = "web", **kwargs) -> Dict[str, Any]:
        """
        Generate with specific context types (leverage Grok's real-time capabilities)
        
        Args:
            prompt: Input prompt
            context_type: Type of context ('web', 'x_posts', 'news', 'academic')
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generated text and metadata
        """
        # Modify prompt based on context type
        context_prompts = {
            'web': "Use the latest web information and current events to answer: ",
            'x_posts': "Consider recent posts and discussions on X (Twitter) when answering: ",
            'news': "Based on the latest news and current events, answer: ",
            'academic': "Using the most recent academic research and papers, answer: "
        }
        
        context_prefix = context_prompts.get(context_type, "")
        enhanced_prompt = context_prefix + prompt
        
        return self.generate(enhanced_prompt, **kwargs)