from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, time

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add this at the top of your db_migration.py file
import logging

print("testdb file ran")

# db_migration.py


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Loaded environment variables from .env file")

# Get database connection parameters from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default PostgreSQL port
DB_NAME = os.getenv("DB_NAME")

# Import database models
from database.models import Base  # Make sure this imports all your model classes

def create_database():
    """Create database tables if they don't exist"""
    logger.info(f"Starting database migration for database '{DB_NAME}'")
    
    # Verify all required environment variables are present
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        logger.error("Missing required database environment variables")
        logger.error(f"DB_USER: {'Set' if DB_USER else 'Missing'}")
        logger.error(f"DB_PASSWORD: {'Set' if DB_PASSWORD else 'Missing'}")
        logger.error(f"DB_HOST: {'Set' if DB_HOST else 'Missing'}")
        logger.error(f"DB_NAME: {'Set' if DB_NAME else 'Missing'}")
        raise ValueError("Missing required database environment variables")
    
    # Create database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    logger.info(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}")
    
    try:
        # Create engine and connect to the database
        engine = create_engine(DATABASE_URL)
        logger.info("Successfully connected to database")
        
        # Create all tables based on the models
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("All database tables created successfully")
        
        # Create a session for testing
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test the database connection
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            logger.info("Database connection test successful")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        create_database()
        logger.info("Database migration completed successfully")
    except Exception as e:
        logger.error(f"Database migration script failed: {str(e)}")
        exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Then in your create_database function:
def create_database():
    """Create the database if it doesn't exist"""
    logger.info(f"Attempting to create database '{DB_NAME}' if it doesn't exist...")
    
    # Rest of your function, but add more logging
    # For example:
    logger.info(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}")
    
    # And after you check if the database exists:
    if not database_exists:
        logger.info(f"Database '{DB_NAME}' does not exist. Creating now...")
    else:
        logger.info(f"Database '{DB_NAME}' already exists.")

# Add similar logging to the other functions

# Import your models
from database.models import (
    Restaurant, Location, OperatingHours, Menu, MenuCategory, 
    MenuItem, MenuItemIngredient, FAQ, User, ChatbotLog,
    ReservationSettings
)

class RestaurantService:
    """Service for restaurant-related database operations"""
    
    @staticmethod
    def create_restaurant(db: Session, restaurant_data: Dict[str, Any]) -> Restaurant:
        """Create a new restaurant entry"""
        restaurant = Restaurant(**restaurant_data)
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        return restaurant
    
    @staticmethod
    def get_restaurant_by_id(db: Session, restaurant_id: int) -> Optional[Restaurant]:
        """Get restaurant by ID"""
        return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    @staticmethod
    def update_restaurant(db: Session, restaurant_id: int, restaurant_data: Dict[str, Any]) -> Optional[Restaurant]:
        """Update restaurant information"""
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if restaurant:
            for key, value in restaurant_data.items():
                setattr(restaurant, key, value)
            restaurant.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(restaurant)
        return restaurant
    
    @staticmethod
    def get_all_restaurants(db: Session, skip: int = 0, limit: int = 100) -> List[Restaurant]:
        """Get all restaurants with pagination"""
        return db.query(Restaurant).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_restaurants_by_user(db: Session, user_id: int) -> List[Restaurant]:
        """Get all restaurants associated with a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user.restaurants
        return []

class LocationService:
    """Service for restaurant location operations"""
    
    @staticmethod
    def create_location(db: Session, location_data: Dict[str, Any]) -> Location:
        """Create a new location for a restaurant"""
        location = Location(**location_data)
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def get_locations_by_restaurant(db: Session, restaurant_id: int) -> List[Location]:
        """Get all locations for a restaurant"""
        return db.query(Location).filter(Location.restaurant_id == restaurant_id).all()
    
    @staticmethod
    def update_location(db: Session, location_id: int, location_data: Dict[str, Any]) -> Optional[Location]:
        """Update a location"""
        location = db.query(Location).filter(Location.id == location_id).first()
        if location:
            for key, value in location_data.items():
                setattr(location, key, value)
            db.commit()
            db.refresh(location)
        return location

class OperatingHoursService:
    """Service for restaurant operating hours"""
    
    @staticmethod
    def create_hours(db: Session, hours_data: Dict[str, Any]) -> OperatingHours:
        """Create operating hours for a restaurant"""
        hours = OperatingHours(**hours_data)
        db.add(hours)
        db.commit()
        db.refresh(hours)
        return hours
    
    @staticmethod
    def get_hours_by_restaurant(db: Session, restaurant_id: int) -> List[OperatingHours]:
        """Get all operating hours for a restaurant"""
        return db.query(OperatingHours).filter(
            OperatingHours.restaurant_id == restaurant_id
        ).order_by(OperatingHours.day_of_week).all()
    
    @staticmethod
    def is_restaurant_open_now(db: Session, restaurant_id: int) -> bool:
        """Check if a restaurant is currently open"""
        now = datetime.now()
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        current_time = now.strftime("%H:%M:%S")
        
        hours = db.query(OperatingHours).filter(
            OperatingHours.restaurant_id == restaurant_id,
            OperatingHours.day_of_week == current_day,
            OperatingHours.is_closed == False
        ).first()
        
        if hours and hours.open_time <= current_time <= hours.close_time:
            return True
        return False

class MenuService:
    """Service for restaurant menu operations"""
    
    @staticmethod
    def create_menu(db: Session, menu_data: Dict[str, Any]) -> Menu:
        """Create a new menu for a restaurant"""
        menu = Menu(**menu_data)
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu
    
    @staticmethod
    def get_menus_by_restaurant(db: Session, restaurant_id: int) -> List[Menu]:
        """Get all menus for a restaurant"""
        return db.query(Menu).filter(
            Menu.restaurant_id == restaurant_id,
            Menu.is_active == True
        ).all()
    
    @staticmethod
    def create_category(db: Session, category_data: Dict[str, Any]) -> MenuCategory:
        """Create a new menu category"""
        category = MenuCategory(**category_data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def create_menu_item(db: Session, item_data: Dict[str, Any], ingredients: List[Dict[str, Any]] = None) -> MenuItem:
        """Create a new menu item with optional ingredients"""
        menu_item = MenuItem(**item_data)
        db.add(menu_item)
        db.commit()
        db.refresh(menu_item)
        
        # Add ingredients if provided
        if ingredients:
            for ing_data in ingredients:
                ingredient = MenuItemIngredient(menu_item_id=menu_item.id, **ing_data)
                db.add(ingredient)
            db.commit()
        
        return menu_item
    
    @staticmethod
    def get_full_menu_by_restaurant(db: Session, restaurant_id: int) -> Dict[str, Any]:
        """Get the full menu structure for a restaurant"""
        menus = db.query(Menu).filter(
            Menu.restaurant_id == restaurant_id,
            Menu.is_active == True
        ).all()
        
        result = []
        for menu in menus:
            menu_dict = {
                "id": menu.id,
                "name": menu.name,
                "description": menu.description,
                "start_time": menu.start_time,
                "end_time": menu.end_time,
                "categories": []
            }
            
            for category in menu.categories:
                category_dict = {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "items": []
                }
                
                for item in category.items:
                    if item.is_active:
                        item_dict = {
                            "id": item.id,
                            "name": item.name,
                            "description": item.description,
                            "price": item.price,
                            "image_url": item.image_url,
                            "dietary_info": {
                                "vegetarian": item.is_vegetarian,
                                "vegan": item.is_vegan,
                                "gluten_free": item.is_gluten_free,
                                "contains_nuts": item.contains_nuts,
                                "contains_dairy": item.contains_dairy,
                                "contains_alcohol": item.contains_alcohol,
                                "spice_level": item.spice_level
                            },
                            "popular": item.popular,
                            "chef_special": item.chef_special,
                            "ingredients": [ing.name for ing in item.ingredients]
                        }
                        category_dict["items"].append(item_dict)
                
                if category_dict["items"]:  # Only add categories with active items
                    menu_dict["categories"].append(category_dict)
            
            result.append(menu_dict)
        
        return result

class FAQService:
    """Service for restaurant FAQ operations"""
    
    @staticmethod
    def create_faq(db: Session, faq_data: Dict[str, Any]) -> FAQ:
        """Create a new FAQ for a restaurant"""
        faq = FAQ(**faq_data)
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq
    
    @staticmethod
    def get_faqs_by_restaurant(db: Session, restaurant_id: int) -> List[FAQ]:
        """Get all FAQs for a restaurant"""
        return db.query(FAQ).filter(
            FAQ.restaurant_id == restaurant_id,
            FAQ.is_active == True
        ).order_by(FAQ.category, FAQ.display_order).all()
    
    @staticmethod
    def update_faq(db: Session, faq_id: int, faq_data: Dict[str, Any]) -> Optional[FAQ]:
        """Update an FAQ"""
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if faq:
            for key, value in faq_data.items():
                setattr(faq, key, value)
            db.commit()
            db.refresh(faq)
        return faq

class ChatbotLogService:
    """Service for chatbot conversation logs"""
    
    @staticmethod
    def log_conversation(db: Session, log_data: Dict[str, Any]) -> ChatbotLog:
        """Log a chatbot conversation"""
        log = ChatbotLog(**log_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_logs_by_restaurant(db: Session, restaurant_id: int, limit: int = 100) -> List[ChatbotLog]:
        """Get recent conversation logs for a restaurant"""
        return db.query(ChatbotLog).filter(
            ChatbotLog.restaurant_id == restaurant_id
        ).order_by(ChatbotLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_logs_by_session(db: Session, session_id: str) -> List[ChatbotLog]:
        """Get all conversation logs for a specific session"""
        return db.query(ChatbotLog).filter(
            ChatbotLog.session_id == session_id
        ).order_by(ChatbotLog.timestamp).all()
    
    @staticmethod
    def add_feedback(db: Session, log_id: int, rating: int, feedback_text: str = None) -> Optional[ChatbotLog]:
        """Add user feedback to a conversation log"""
        log = db.query(ChatbotLog).filter(ChatbotLog.id == log_id).first()
        if log:
            log.feedback_rating = rating
            log.feedback_text = feedback_text
            db.commit()
            db.refresh(log)
        return log

class ChatbotDataService:
    """Service to format restaurant data for the chatbot"""
    
    @staticmethod
    def get_restaurant_chatbot_data(db: Session, restaurant_id: int) -> Dict[str, Any]:
        """Get all restaurant data in a format suitable for the chatbot"""
        restaurant = RestaurantService.get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            return None
        
        locations = LocationService.get_locations_by_restaurant(db, restaurant_id)
        hours = OperatingHoursService.get_hours_by_restaurant(db, restaurant_id)
        menus = MenuService.get_full_menu_by_restaurant(db, restaurant_id)
        faqs = FAQService.get_faqs_by_restaurant(db, restaurant_id)
        
        # Format hours for better readability
        formatted_hours = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for hour in hours:
            day_entry = {
                "day": days[hour.day_of_week],
                "is_closed": hour.is_closed,
                "hours": None if hour.is_closed else f"{hour.open_time} - {hour.close_time}"
            }
            formatted_hours.append(day_entry)
        
        # Format FAQs by category
        formatted_faqs = {}
        for faq in faqs:
            if faq.category not in formatted_faqs:
                formatted_faqs[faq.category] = []
            formatted_faqs[faq.category].append({
                "question": faq.question,
                "answer": faq.answer
            })
        
        # Build the final data structure
        chatbot_data = {
            "restaurant_info": {
                "name": restaurant.name,
                "description": restaurant.description,
                "cuisine_type": restaurant.cuisine_type,
                "price_range": restaurant.price_range,
                "website": restaurant.website
            },
            "locations": [
                {
                    "address": f"{loc.address_line1}, {loc.address_line2 or ''}, {loc.city}, {loc.state}, {loc.postal_code}",
                    "phone": loc.phone,
                    "email": loc.email,
                    "is_primary": loc.is_primary
                } for loc in locations
            ],
            "hours": formatted_hours,
            "menus": menus,
            "faqs": formatted_faqs
        }
        
        # Check if restaurant accepts reservations
        reservation_settings = db.query(ReservationSettings).filter(
            ReservationSettings.restaurant_id == restaurant_id
        ).first()
        
        if reservation_settings:
            chatbot_data["reservations"] = {
                "accepts_reservations": reservation_settings.accepts_reservations,
                "min_party_size": reservation_settings.min_party_size,
                "max_party_size": reservation_settings.max_party_size,
                "advance_reservation_days": reservation_settings.advance_reservation_days,
                "special_instructions": reservation_settings.special_instructions
            }
        
            return chatbot_data

