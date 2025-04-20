# OpenAI API service integration
import os
import openai
from typing import Dict, List, Optional, Any

class ChatGPTService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ChatGPT service with API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Either pass it explicitly or set OPENAI_API_KEY environment variable.")
        
        # Initialize the OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
    def get_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "gpt-3.5-turbo",
                       temperature: float = 0.7,
                       max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Get a completion from the ChatGPT model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: The OpenAI model to use
            temperature: Controls randomness (0-1)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The response from the API
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "message": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            # Log the error and return a failure response
            print(f"Error calling OpenAI API: {e}")
            return {
                "error": str(e),
                "message": None,
                "finish_reason": "error",
                "usage": None
            }
    
    def get_simple_completion(self, prompt: str, **kwargs) -> str:
        """
        Simplified method to get just the completion text from a single prompt.
        
        Args:
            prompt: The user's prompt text
            **kwargs: Additional parameters to pass to get_completion
            
        Returns:
            Just the completion text string
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.get_completion(messages, **kwargs)
        
        if "error" in response and response["error"]:
            raise Exception(f"Failed to get completion: {response['error']}")
            
        return response["message"]