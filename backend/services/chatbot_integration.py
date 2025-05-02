import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import openai
from services.database_services import ChatbotDataService, ChatbotLogService
import uuid
from dotenv import load_dotenv

class ChatbotService:
    """Service to integrate ChatGPT API with restaurant data"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # OpenAI API setup with error handling
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            print("OpenAI API key configured")
        else:
            print("Warning: OpenAI API key not found. Chatbot responses will be limited.")
    
    def generate_chatbot_response(self, restaurant_id: int, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Generate a response from the chatbot using ChatGPT API and restaurant data"""
        # Create session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Check if OpenAI API key is configured
        if not self.openai_api_key:
            return {
                "session_id": session_id,
                "response": "I'm not fully configured yet. Please set up the OpenAI API integration.",
                "error": "Missing OpenAI API key"
            }
            
        # Get restaurant data directly from database
        from database.models import Restaurant
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        
        if not restaurant:
            return {
                "session_id": session_id,
                "response": "Sorry, I couldn't find information about this restaurant.",
                "error": "Restaurant not found"
            }
            
        # Get restaurant data from database
        restaurant_data = ChatbotDataService.get_restaurant_chatbot_data(self.db, restaurant_id)
        
        if not restaurant_data:
            return {
                "session_id": session_id,
                "response": "Sorry, I couldn't load information about this restaurant.",
                "error": "Failed to load restaurant data"
            }
            
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
            log_entry = None
            try:
                log_entry = ChatbotLogService.log_conversation(
                    self.db,
                    {
                        "restaurant_id": restaurant_id,
                        "session_id": session_id,
                        "user_input": user_input,
                        "chatbot_response": chatbot_response,
                        "timestamp": datetime.utcnow()
                    }
                )
            except Exception as log_error:
                print(f"Error logging conversation: {str(log_error)}")
            
            return {
                "session_id": session_id,
                "response": chatbot_response,
                "log_id": log_entry.id if log_entry else None
            }
            
        except Exception as e:
            error_message = f"Error generating chatbot response: {str(e)}"
            print(error_message)
            
            # Try to log the error
            try:
                ChatbotLogService.log_conversation(
                    self.db,
                    {
                        "restaurant_id": restaurant_id,
                        "session_id": session_id,
                        "user_input": user_input,
                        "chatbot_response": "Error occurred",
                        "timestamp": datetime.utcnow(),
                        "feedback_text": error_message
                    }
                )
            except Exception:
                pass  # Silent fail if logging also fails
            
            return {
                "session_id": session_id,
                "response": "I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment.",
                "error": error_message
            }