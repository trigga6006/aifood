import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import openai
from services.database_services import ChatbotDataService, ChatbotLogService
from azure.storage.blob import BlobServiceClient
import uuid

class ChatbotService:
    """Service to integrate ChatGPT API with restaurant data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        
        # Azure Blob Storage setup
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "restaurant-data")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        
    def _upload_data_to_blob(self, restaurant_id: int, data: Dict[str, Any]) -> str:
        """Upload restaurant data to Azure Blob Storage"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Create container if it doesn't exist
            if not container_client.exists():
                container_client.create_container()
                
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2)
            
            # Create a unique blob name based on restaurant ID and timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            blob_name = f"restaurant_{restaurant_id}/{timestamp}.json"
            
            # Upload JSON data to blob
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(json_data, overwrite=True)
            
            return blob_name
            
        except Exception as e:
            print(f"Error uploading data to Azure Blob Storage: {str(e)}")
            return None

    def _download_data_from_blob(self, blob_path: str) -> Dict[str, Any]:
        """Download restaurant data from Azure Blob Storage"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_path)
            
            # Download blob content
            downloaded_blob = blob_client.download_blob()
            data = json.loads(downloaded_blob.readall())
            
            return data
            
        except Exception as e:
            print(f"Error downloading data from Azure Blob Storage: {str(e)}")
            return None

    def refresh_restaurant_data(self, restaurant_id: int) -> str:
        """Fetch restaurant data and upload to Azure Blob Storage"""
        # Get restaurant data from database
        restaurant_data = ChatbotDataService.get_restaurant_chatbot_data(self.db, restaurant_id)
        
        if not restaurant_data:
            return None
        
        # Upload data to Azure Blob Storage
        blob_path = self._upload_data_to_blob(restaurant_id, restaurant_data)
        
        # Update restaurant record with blob path
        from database.models import Restaurant
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if restaurant and blob_path:
            restaurant.blob_storage_path = blob_path
            restaurant.updated_at = datetime.utcnow()
            self.db.commit()
            
        return blob_path
    
    def generate_chatbot_response(self, restaurant_id: int, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Generate a response from the chatbot using ChatGPT API and restaurant data"""
        # Create session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Get restaurant data
        from database.models import Restaurant
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        
        if not restaurant:
            return {
                "session_id": session_id,
                "response": "Sorry, I couldn't find information about this restaurant.",
                "error": "Restaurant not found"
            }
            
        # Get restaurant data from Azure Blob Storage or database
        restaurant_data = None
        if restaurant.blob_storage_path:
            restaurant_data = self._download_data_from_blob(restaurant.blob_storage_path)
            
        # If no data in blob storage or failed to download, get fresh data from database
        if not restaurant_data:
            restaurant_data = ChatbotDataService.get_restaurant_chatbot_data(self.db, restaurant_id)
            # Upload fresh data to blob storage
            self._upload_data_to_blob(restaurant_id, restaurant_data)
            
        # Prepare context for ChatGPT
        restaurant_context = json.dumps(restaurant_data, indent=2)
        
        # Prepare system message with restaurant-specific information
        system_message = f"""
        You are a helpful waiter assistant for {restaurant.name}. 
        Your name is "{restaurant.name} Assistant".
        
        Use the following restaurant information to answer customer questions:
        {restaurant_context}
        
        - Be polite, friendly, and helpful like a waiter would be.
        - If asked about menu items, provide details about ingredients, pricing, and dietary information.
        - If asked about hours, provide the correct operating hours for the requested day.
        - If asked about location, provide the address and contact information.
        - If asked about reservations, provide the reservation policy and how to make a reservation.
        - If asked a question you don't have information for, apologize and offer to connect them with the restaurant directly.
        - Keep responses concise and conversational, like a helpful waiter would.
        - Do not mention that you're an AI or that you're using provided information.
        - If greeting the user, use the custom greeting if available: "{restaurant.chatbot_greeting or 'Welcome to ' + restaurant.name + '! How can I help you today?'}"
        """
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or the model of your choice
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Extract response text
            chatbot_response = response.choices[0].message.content.strip()
            
            # Log the conversation
            ChatbotLogService.log_conversation(
                self.db,
                {
                    "restaurant_id": restaurant_id,
                    "session_id": session_id,
                    "user_input": user_input,
                    "chatbot_response": chatbot_response,
                    "timestamp": datetime.utcnow()
                }
            )
            
            return {
                "session_id": session_id,
                "response": chatbot_response
            }
            
        except Exception as e:
            error_message = f"Error generating chatbot response: {str(e)}"
            print(error_message)
            
            return {
                "session_id": session_id,
                "response": "I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment.",
                "error": error_message
            }
