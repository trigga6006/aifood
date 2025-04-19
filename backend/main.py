# Main application 
# app.py

# Dependencies
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import openai
from azure.storage.blob import BlobServiceClient
import logging
from datetime import datetime

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
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure Azure Blob Storage
azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
azure_container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

# Initialize Azure Blob Storage client
try:
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    container_client = blob_service_client.get_container_client(azure_container_name)
    logger.info("Successfully connected to Azure Blob Storage")
except Exception as e:
    logger.error(f"Failed to connect to Azure Blob Storage: {str(e)}")
    blob_service_client = None
    container_client = None

# Helper functions
def is_blob_storage_configured():
    """Check if Azure Blob Storage is properly configured."""
    return blob_service_client is not None and container_client is not None

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API routes
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        conversation_history = data.get('history', [])
        
        # Prepare messages for OpenAI API
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the new user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=messages,
            max_tokens=int(os.getenv('MAX_TOKENS', 500)),
            temperature=float(os.getenv('TEMPERATURE', 0.7))
        )
        
        assistant_response = response.choices[0].message.content
        
        # Log the interaction
        logger.info(f"User message: {user_message}")
        logger.info(f"Assistant response: {assistant_response[:100]}...")  # Log first 100 chars
        
        return jsonify({
            'response': assistant_response,
            'usage': response.usage,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

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
            return jsonify({'error': 'Azure Blob Storage not configured properly'}), 500
            
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        
        # Upload file to Azure Blob Storage
        blob_client = container_client.get_blob_client(unique_filename)
        file_contents = file.read()
        blob_client.upload_blob(file_contents, overwrite=True)
        
        # Get the URL of the uploaded file
        file_url = f"{blob_client.url}"
        
        logger.info(f"File uploaded successfully: {unique_filename}")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'url': file_url
        })
        
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while uploading the file.'}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        if not is_blob_storage_configured():
            return jsonify({'error': 'Azure Blob Storage not configured properly'}), 500
            
        # List all blobs in the container
        blobs = container_client.list_blobs()
        files = []
        
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob.name)
            files.append({
                'name': blob.name,
                'url': blob_client.url,
                'size': blob.size,
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

@app.route('/api/health', methods=['GET'])
def health_check():
    status = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'openai': 'connected' if openai.api_key else 'not configured',
            'azure_storage': 'connected' if is_blob_storage_configured() else 'not configured'
        }
    }
    return jsonify(status)

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Run the application
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
