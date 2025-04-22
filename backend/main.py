# Main application 
# app.py

# Dependencies
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, Response
from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceNotFoundError
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import openai
from azure.storage.blob import BlobServiceClient
import logging
from datetime import datetime
from services.azure_storage import AzureStorageService

#For error handling
from werkzeug.exceptions import HTTPException
import traceback
import sys

#For logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Configure logging
# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
log_file_path = os.path.join(logs_dir, 'app.log')

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# File handler (rotating to keep log files manageable)
file_handler = RotatingFileHandler(
    log_file_path, 
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Root logger configuration
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Application logger
logger = logging.getLogger(__name__)
logger.info("Application starting up...")

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build')
CORS(app)  # Enable CORS for all routes

# Error handling 
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'status_code': 400
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': f"The requested URL {request.path} was not found on the server.",
        'status_code': 404
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method Not Allowed',
        'message': f"The method {request.method} is not allowed for the requested URL.",
        'status_code': 405
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    # Log the error and stacktrace
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, '__name__', 'Unknown Exception')
    
    logger.error(f"Internal Server Error: {exception_name} - {str(exception_value)}")
    logger.error(f"Traceback: {''.join(traceback.format_tb(exception_traceback))}")
    
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred on the server.',
        'status_code': 500
    }), 500

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, '__name__', 'Unknown Exception')
    
    logger.error(f"Unhandled Exception: {exception_name} - {str(exception_value)}")
    logger.error(f"Traceback: {''.join(traceback.format_tb(exception_traceback))}")
    
    return jsonify({
        'error': 'Unexpected Error',
        'message': f"An unexpected error occurred: {str(error)}",
        'status_code': 500
    }), 500

# Custom exception classes
class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        error_dict = dict(self.payload or ())
        error_dict['error'] = self.__class__.__name__
        error_dict['message'] = self.message
        error_dict['status_code'] = self.status_code
        return error_dict

class ResourceNotFoundError(APIError):
    """Exception raised when a requested resource is not found"""
    def __init__(self, message="The requested resource was not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)

class ValidationError(APIError):
    """Exception raised when input validation fails"""
    def __init__(self, message="Invalid input data", payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(APIError):
    """Exception raised when authentication fails"""
    def __init__(self, message="Authentication failed", payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Exception raised when user lacks permission"""
    def __init__(self, message="You don't have permission to perform this action", payload=None):
        super().__init__(message, status_code=403, payload=payload)

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Configure OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key

# Flag for using mock responses (set to True to avoid OpenAI API costs)
USE_MOCK_RESPONSES = True

# ChatGPT Service Class - Embedded in main.py to avoid import issues
class ChatGPTService:
    def __init__(self, api_key: str = None):
        """Initialize the ChatGPT service with API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Either pass it explicitly or set OPENAI_API_KEY environment variable.")
        
        # Set the API key for the older openai library
        openai.api_key = self.api_key
        
    def get_completion(self, 
                       messages, 
                       model="gpt-3.5-turbo",
                       temperature=0.7,
                       max_tokens=1000):
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
        # Use mock response if flag is set
        if USE_MOCK_RESPONSES:
            return self.get_mock_completion(messages)
            
        try:
            # Using the older style API
            response = openai.ChatCompletion.create(
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
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                "error": str(e),
                "message": None,
                "finish_reason": "error",
                "usage": None
            }
    
    def get_simple_completion(self, prompt, **kwargs):
        """
        Simplified method to get just the completion text from a single prompt.
        
        Args:
            prompt: The user's prompt text
            **kwargs: Additional parameters to pass to get_completion
            
        Returns:
            Just the completion text string
        """
        # Use mock response if flag is set
        if USE_MOCK_RESPONSES:
            return "This is a mock response for testing. The integration is working correctly!"
            
        messages = [{"role": "user", "content": prompt}]
        response = self.get_completion(messages, **kwargs)
        
        if "error" in response and response["error"]:
            raise Exception(f"Failed to get completion: {response['error']}")
            
        return response["message"]
        
    def get_mock_completion(self, messages):
        """Return a mock response for testing without hitting the API"""
        # Generate a contextual response based on the user's input
        user_message = ""
        for msg in messages:
            if msg["role"] == "user":
                user_message = msg["content"]
                break
                
        # Simple keyword-based response generation
        response_text = "I'm a mock AI assistant. "
        
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            response_text += "Hello! How can I help you today?"
        elif "how are you" in user_message.lower():
            response_text += "I'm just a mock response, but thanks for asking!"
        elif "food" in user_message.lower() or "recipe" in user_message.lower() or "cook" in user_message.lower():
            response_text += "I'd be happy to discuss food and recipes with you. What kind of cuisine are you interested in?"
        elif "weather" in user_message.lower():
            response_text += "I don't have access to real-time weather data in mock mode, but I can pretend it's a lovely day!"
        elif "thank" in user_message.lower():
            response_text += "You're welcome! Is there anything else I can help with?"
        else:
            response_text += "I understand you're asking about: '" + user_message[:30] + "...' This is a mock response for testing purposes."
            
        return {
            "message": response_text,
            "finish_reason": "stop",
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_message.split()) + len(response_text.split())
            }
        }

# Initialize the ChatGPT service
try:
    chatgpt_service = ChatGPTService(api_key=openai_api_key)
    logger.info("ChatGPT service initialized successfully")
    if USE_MOCK_RESPONSES:
        logger.info("Using MOCK responses for ChatGPT API (to avoid API costs)")
except Exception as e:
    chatgpt_service = None
    logger.error(f"Failed to initialize ChatGPT service: {str(e)}")

# Configure Azure Blob Storage
azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
azure_container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

# Initialize Azure Blob Storage service
blob_service_client = None
container_client = None

def initialize_azure_storage():
    """Initialize Azure Blob Storage client with proper error handling."""
    global blob_service_client, container_client
    
    if not azure_connection_string or not azure_container_name:
        logger.warning("Azure Blob Storage configuration missing. File storage features disabled.")
        return False
    
    try:
        # Create the blob service client
        blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        
        # Check if container exists, create if it doesn't
        container_client = blob_service_client.get_container_client(azure_container_name)
        
        # Verify connection by listing blobs (will raise error if container doesn't exist)
        next(container_client.list_blobs(), None)
        
        logger.info(f"Successfully connected to Azure Blob Storage container: {azure_container_name}")
        return True
    except ResourceNotFoundError:
        # Container doesn't exist, create it
        try:
            logger.info(f"Container {azure_container_name} not found. Creating now...")
            container_client = blob_service_client.create_container_client(azure_container_name)
            container_client.create_container()
            logger.info(f"Container {azure_container_name} created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create container: {str(e)}")
            blob_service_client = None
            container_client = None
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Azure Blob Storage: {str(e)}")
        blob_service_client = None
        container_client = None
        return False

# Initialize Azure storage on app startup
azure_storage_available = initialize_azure_storage()

def is_blob_storage_configured():
    """Check if Azure Blob Storage is properly configured and connected."""
    return azure_storage_available and blob_service_client is not None and container_client is not None

def get_secure_file_url(blob_name, expiry_hours=1):
    """Generate a secure, time-limited SAS URL for accessing a blob."""
    if not is_blob_storage_configured():
        return None
    
    try:
        # Generate a SAS token with expiration
        from datetime import datetime, timedelta
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        # Get account information from connection string
        account_name = blob_service_client.account_name
        account_key = blob_service_client.credential.account_key
        
        # Generate SAS token with read permission
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=azure_container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        # Construct the full URL with SAS token
        blob_client = container_client.get_blob_client(blob_name)
        sas_url = f"{blob_client.url}?{sas_token}"
        
        return sas_url
    except Exception as e:
        logger.error(f"Error generating secure URL for blob {blob_name}: {str(e)}")
        return None

def allowed_file(filename):
    """Check if the file has an allowed extension for security."""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx'}
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal attacks."""
    # Remove any directory path components
    filename = os.path.basename(filename)
    # Replace potentially dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename

# Add a root endpoint for API info
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Welcome to the ChatGPT API server',
        'endpoints': {
            'chat': '/api/chat',
            'test': '/api/chat/test'
        },
        'mock_mode': USE_MOCK_RESPONSES
    })

# New API endpoint for ChatGPT interaction
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        # Check if ChatGPT service is available
        if chatgpt_service is None:
            return jsonify({'error': 'ChatGPT service not available'}), 503
        
        # Extract parameters
        message = data.get('message')
        chat_history = data.get('chat_history', [])
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        
        # Format messages for ChatGPT API
        messages = []
        
        # Add chat history
        for msg in chat_history:
            role = "assistant" if msg.get('is_bot', False) else "user"
            messages.append({
                "role": role,
                "content": msg.get('text', '')
            })
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Get response from ChatGPT
        logger.info(f"Sending chat request with {len(messages)} messages")
        
        # Using mock or real API based on the flag
        response = chatgpt_service.get_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Check for errors
        if "error" in response and response["error"]:
            logger.error(f"ChatGPT API error: {response['error']}")
            return jsonify({
                'error': 'Error from ChatGPT API',
                'details': response['error']
            }), 500
        
        # Return response
        return jsonify({
            'response': response["message"],
            'usage': response["usage"],
            'finish_reason': response["finish_reason"]
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while processing chat request.'}), 500

# Add a simple test endpoint for checking if ChatGPT is working
@app.route('/api/chat/test', methods=['GET'])
def test_chat():
    try:
        # Check if ChatGPT service is available
        if chatgpt_service is None:
            return jsonify({'error': 'ChatGPT service not available'}), 503
        
        # Use mock response for test endpoint
        test_response = "This is a test response. The integration is working correctly!"
        if not USE_MOCK_RESPONSES:
            test_response = chatgpt_service.get_simple_completion("Say 'Hello, I am working correctly!'")
        
        return jsonify({
            'status': 'success',
            'message': 'ChatGPT API test successful',
            'response': test_response,
            'mock_mode': USE_MOCK_RESPONSES
        })
        
    except Exception as e:
        logger.error(f"Error in chat test endpoint: {str(e)}")
        logger.error(f"Exception traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'ChatGPT API test failed: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
            
        if not is_blob_storage_configured():
            return jsonify({'error': 'Azure Blob Storage not available'}), 503
        
        # Sanitize and create unique filename
        safe_filename = sanitize_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{safe_filename}"
        
        # Get content type or default to octet-stream
        content_type = file.content_type or 'application/octet-stream'
        
        # Create blob client and set content settings
        blob_client = container_client.get_blob_client(unique_filename)
        
        # Read file data
        file_contents = file.read()
        
        # Set content settings including content type
        from azure.storage.blob import ContentSettings
        content_settings = ContentSettings(
            content_type=content_type,
            cache_control="max-age=86400"  # Cache for 24 hours
        )
        
        # Upload to Azure with proper content settings
        blob_client.upload_blob(
            file_contents, 
            overwrite=True,
            content_settings=content_settings
        )
        
        # Generate secure URL with expiration
        secure_url = get_secure_file_url(unique_filename)
        
        logger.info(f"File uploaded successfully: {unique_filename} ({len(file_contents)} bytes)")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'size': len(file_contents),
            'content_type': content_type,
            'url': blob_client.url,  # Base URL (requires storage permissions)
            'secure_url': secure_url,  # SAS URL with temporary access
            'uploaded_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while uploading the file.'}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        if not is_blob_storage_configured():
            return jsonify({'error': 'Azure Blob Storage not available'}), 503
        
        # Get optional prefix filter
        prefix = request.args.get('prefix', None)
            
        # List blobs with optional prefix filter
        blobs = container_client.list_blobs(name_starts_with=prefix)
        files = []
        
        for blob in blobs:
            # Generate secure URL with expiration
            secure_url = get_secure_file_url(blob.name)
            
            # Add file info to response
            files.append({
                'name': blob.name,
                'url': secure_url,  # Only return secure URLs
                'size': blob.size,
                'content_type': blob.content_settings.content_type if blob.content_settings else None,
                'created': blob.creation_time.isoformat() if blob.creation_time else None,
                'last_modified': blob.last_modified.isoformat() if blob.last_modified else None
            })
        
        return jsonify({
            'files': files,
            'count': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error in list_files endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while listing files.'}), 500

@app.route('/api/files/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        if not is_blob_storage_configured():
            return jsonify({'error': 'Azure Blob Storage not available'}), 503
        
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        try:
            # Get blob client
            blob_client = container_client.get_blob_client(safe_filename)
            
            # Download the blob
            download_stream = blob_client.download_blob()
            
            # Get content and content type
            content = download_stream.readall()
            content_type = download_stream.properties.content_settings.content_type
            
            # Return file as response
            return Response(
                content,
                mimetype=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={os.path.basename(safe_filename)}"
                }
            )
            
        except ResourceNotFoundError:
            return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in download_file endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while downloading the file.'}), 500

@app.route('/api/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        if not is_blob_storage_configured():
            return jsonify({'error': 'Azure Blob Storage not available'}), 503
        
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        try:
            # Get blob client and delete the blob
            blob_client = container_client.get_blob_client(safe_filename)
            blob_client.delete_blob()
            
            logger.info(f"File deleted successfully: {safe_filename}")
            
            return jsonify({
                'message': 'File deleted successfully',
                'filename': safe_filename
            })
            
        except ResourceNotFoundError:
            return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in delete_file endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting the file.'}), 500

# Run the application on port 5000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)