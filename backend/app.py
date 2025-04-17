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