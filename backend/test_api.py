"""
Combined file to run the Restaurant Chatbot API
"""
import os
import logging
import uvicorn
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Add this right after creating your FastAPI app
app = FastAPI(title="Restaurant Chatbot API - Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import database configuration
from config.database import engine, Base, get_db
from database.models import *  # Import all models

# Import services
from services.chatbot_integration import ChatbotService
from services.database_services import (
    RestaurantService, MenuService, FAQService, 
    LocationService, OperatingHoursService, ChatbotLogService
)

# Define pydantic models for request/response
from pydantic import BaseModel, Field

class ChatbotRequest(BaseModel):
    restaurant_id: int
    user_input: str
    session_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    session_id: str
    response: str
    error: Optional[str] = None

class FeedbackRequest(BaseModel):
    log_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None

# Create FastAPI app
app = FastAPI(title="Restaurant Chatbot API - Test")

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create router
router = APIRouter()

# Chatbot endpoint
@router.post("/api/chatbot", response_model=ChatbotResponse)
async def chatbot_interaction(
    request: ChatbotRequest,
    db: Session = Depends(get_db)
):
    chatbot_service = ChatbotService(db)
    
    # Generate response
    response = chatbot_service.generate_chatbot_response(
        restaurant_id=request.restaurant_id,
        user_input=request.user_input,
        session_id=request.session_id
    )
    
    return response

# Feedback endpoint
@router.post("/api/chatbot/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    updated_log = ChatbotLogService.add_feedback(
        db, 
        feedback.log_id, 
        feedback.rating, 
        feedback.feedback_text
    )
    
    if not updated_log:
        raise HTTPException(status_code=404, detail="Conversation log not found")
    
    return {"message": "Feedback submitted successfully"}

# Get restaurant data for frontend dashboard
@router.get("/api/restaurant/{restaurant_id}")
async def get_restaurant_data(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    restaurant = RestaurantService.get_restaurant_by_id(db, restaurant_id)
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    locations = LocationService.get_locations_by_restaurant(db, restaurant_id)
    hours = OperatingHoursService.get_hours_by_restaurant(db, restaurant_id)
    menus = MenuService.get_full_menu_by_restaurant(db, restaurant_id)
    faqs = FAQService.get_faqs_by_restaurant(db, restaurant_id)
    
    return {
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "description": restaurant.description,
            "logo_url": restaurant.logo_url,
            "website": restaurant.website,
            "primary_color": restaurant.primary_color,
            "secondary_color": restaurant.secondary_color,
            "chatbot_greeting": restaurant.chatbot_greeting,
            "cuisine_type": restaurant.cuisine_type,
            "price_range": restaurant.price_range,
            "is_active": restaurant.is_active
        },
        "locations": locations,
        "hours": hours,
        "menus": menus,
        "faqs": faqs
    }

# Get conversation logs for a restaurant
@router.get("/api/restaurant/{restaurant_id}/logs")
async def get_restaurant_logs(
    restaurant_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    logs = ChatbotLogService.get_logs_by_restaurant(db, restaurant_id, limit)
    return {"logs": logs}

# Refresh restaurant data in blob storage
@router.post("/api/restaurant/{restaurant_id}/refresh-data")
async def refresh_restaurant_data(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    chatbot_service = ChatbotService(db)
    blob_path = chatbot_service.refresh_restaurant_data(restaurant_id)
    
    if not blob_path:
        raise HTTPException(status_code=404, detail="Failed to refresh restaurant data")
    
    return {"message": "Restaurant data refreshed successfully", "blob_path": blob_path}

# Include router in app
app.include_router(router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Restaurant Chatbot API Test Server"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting API server...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")