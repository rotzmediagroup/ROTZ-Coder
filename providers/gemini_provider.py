"""
Google Gemini provider for DeepCode
"""

import google.generativeai as genai
from typing import Dict, Any, List
from .base_provider import LLMProvider, APIKeyError, ModelNotFoundError, RateLimitError, ProviderTimeoutError


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    AVAILABLE_MODELS = [
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", **kwargs):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Google AI API key
            model_name: Model name to use
            **kwargs: Additional parameters
        """
        if not model_name:
            model_name = "gemini-pro"
        
        super().__init__(api_key, model_name, **kwargs)
        
        # Configure the Gemini client
        genai.configure(api_key=self.api_key)
        
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise ModelNotFoundError(f"Failed to initialize Gemini model {self.model_name}: {str(e)}")
    
    def _validate_api_key(self):
        """Validate Google AI API key"""
        if not self.api_key or len(self.api_key) < 20:
            raise APIKeyError("Invalid Google AI API key")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using Gemini API
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generated text and metadata
        """
        # Merge parameters
        params = {
            'temperature': 0.7,
            'max_output_tokens': 2048,
            'top_p': 0.95,
            'top_k': 40,
            **self.parameters,
            **kwargs
        }
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=params['temperature'],
            max_output_tokens=params['max_output_tokens'],
            top_p=params['top_p'],
            top_k=params['top_k']
        )
        
        # Add system instruction if provided
        system_prompt = kwargs.get('system_prompt')
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        else:
            full_prompt = prompt
        
        try:
            # Generate content
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                stream=False
            )
            
            # Check if generation was blocked
            if response.candidates and response.candidates[0].finish_reason.name in ['SAFETY', 'RECITATION']:
                raise ProviderTimeoutError(f"Content generation blocked: {response.candidates[0].finish_reason.name}")
            
            if not response.text:
                raise ProviderTimeoutError("No response generated from Gemini")
            
            generated_text = response.text
            
            # Calculate tokens (approximate)
            input_tokens = self.estimate_tokens(full_prompt)
            output_tokens = self.estimate_tokens(generated_text)
            
            # Get finish reason
            finish_reason = "completed"
            if response.candidates:
                finish_reason = response.candidates[0].finish_reason.name.lower()
            
            return {
                'text': generated_text,
                'model': self.model_name,
                'provider': 'gemini',
                'tokens_used': input_tokens + output_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'finish_reason': finish_reason
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'api key' in error_msg or 'unauthorized' in error_msg:
                raise APIKeyError("Invalid Google AI API key")
            elif 'quota' in error_msg or 'rate limit' in error_msg:
                raise RateLimitError("Google AI rate limit exceeded")
            elif 'not found' in error_msg:
                raise ModelNotFoundError(f"Gemini model {self.model_name} not found")
            else:
                raise ProviderTimeoutError(f"Gemini API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        return self.AVAILABLE_MODELS.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information"""
        model_info = super().get_model_info()
        
        context_lengths = {
            "gemini-pro": 32768,
            "gemini-pro-vision": 16384,
            "gemini-1.5-pro": 1048576,  # 1M tokens
            "gemini-1.5-flash": 1048576   # 1M tokens
        }
        
        model_info.update({
            'context_length': context_lengths.get(self.model_name, 32768),
            'specialized_for': 'General purpose, multimodal capabilities',
            'supports_function_calling': True,
            'supports_vision': 'vision' in self.model_name.lower()
        })
        return model_info
    
    def generate_with_image(self, prompt: str, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Generate text with image input (for vision models)
        
        Args:
            prompt: Text prompt
            image_data: Image data as bytes
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generated text and metadata
        """
        if 'vision' not in self.model_name.lower():
            raise ModelNotFoundError(f"Model {self.model_name} does not support vision")
        
        # This would be implemented for vision models
        # For now, just return the text generation
        return self.generate(prompt, **kwargs)