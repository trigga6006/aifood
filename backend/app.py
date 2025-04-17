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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build')
CORS(app)  # Enable CORS for all routes

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

# API routes will be defined here

# Add this to app.py after the "# API routes will be defined here" comment

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
        return jsonify({'error': str(e)}), 500

# Add this after the chat function

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if blob_service_client is None or container_client is None:
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
        return jsonify({'error': str(e)}), 500

# Add this after the upload_file function

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        if blob_service_client is None or container_client is None:
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
        return jsonify({'error': str(e)}), 500

# Add this after the list_files function

@app.route('/api/health', methods=['GET'])
def health_check():
    status = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'openai': 'connected' if openai.api_key else 'not configured',
            'azure_storage': 'connected' if (blob_service_client and container_client) else 'not configured'
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