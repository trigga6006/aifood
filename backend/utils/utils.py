# backend/utils/utils.py

import json
import re
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def sanitize_input(text):
    """
    Sanitize user input to prevent injection attacks
    """
    if not text:
        return ""
    
    # Remove any potentially harmful HTML or script tags
    sanitized = re.sub(r'<[^>]*>', '', text)
    
    # Limit the length of input
    max_length = 5000
    if len(sanitized) > max_length:
        return sanitized[:max_length]
    
    return sanitized

def validate_api_key(api_key):
    """
    Validate that an API key has the correct format
    """
    if not api_key:
        return False
    
    # Check if it's an OpenAI API key format (sk-...)
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
        
    return False

def rate_limiter(max_calls, time_frame):
    """
    Decorator to implement rate limiting
    
    Args:
        max_calls (int): Maximum number of calls allowed in the time frame
        time_frame (int): Time frame in seconds
    """
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove calls older than the time frame
            while calls and calls[0] < now - time_frame:
                calls.pop(0)
                
            # Check if we've reached the maximum number of calls
            if len(calls) >= max_calls:
                logger.warning(f"Rate limit exceeded: {max_calls} calls in {time_frame} seconds")
                return {
                    "error": "Rate limit exceeded",
                    "message": f"You can only make {max_calls} calls every {time_frame} seconds",
                    "status_code": 429
                }, 429
                
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def format_response(data=None, message="Success", status_code=200, error=None):
    """
    Format API responses consistently
    """
    response = {
        "status": "success" if not error else "error",
        "message": message,
        "data": data
    }
    
    if error:
        response["error"] = error
        
    return response, status_code

def log_api_call(endpoint, request_data, response_data, duration_ms):
    """
    Log API calls with timing information
    """
    logger.info(
        f"API Call: {endpoint} | Duration: {duration_ms:.2f}ms | "
        f"Request: {json.dumps(request_data)[:200]} | "
        f"Response: {json.dumps(response_data)[:200]}"
    )
