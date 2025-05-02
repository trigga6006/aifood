"""
Seed script for adding test data to the restaurant chatbot database
Run this script to populate your database with sample restaurant data for testing.

Usage:
    python seed_test_data.py
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database connection parameters
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default PostgreSQL port
DB_NAME = os.getenv("DB_NAME")

# Import database models
from database.models import (
    User, Restaurant, Location, OperatingHours, Menu, MenuCategory, 
    MenuItem, MenuItemIngredient, FAQ, ReservationSettings
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_session():
    """Create and return a database session"""
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
    
    # Create engine and connect to the database
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def create_test_users(db):
    """Create test users"""
    logger.info("Creating test users...")
    
    # Check if users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        logger.info(f"Found {existing_users} existing users, skipping user creation")
        return
    
    # Create an admin user
    admin_user = User(
        email="admin@example.com",
        password_hash=pwd_context.hash("admin123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(admin_user)
    
    # Create a restaurant manager
    manager_user = User(
        email="manager@example.com",
        password_hash=pwd_context.hash("manager123"),
        first_name="Restaurant",
        last_name="Manager",
        role="restaurant_manager",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(manager_user)
    
    # Create a staff member
    staff_user = User(
        email="staff@example.com",
        password_hash=pwd_context.hash("staff123"),
        first_name="Staff",
        last_name="Member",
        role="staff",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(staff_user)
    
    db.commit()
    logger.info("Test users created successfully")
    return [admin_user, manager_user, staff_user]

def create_test_restaurant(db, manager_user):
    """Create a test restaurant with all related data"""
    logger.info("Creating test restaurant...")
    
    # Check if restaurants already exist
    existing_restaurants = db.query(Restaurant).count()
    if existing_restaurants > 0:
        logger.info(f"Found {existing_restaurants} existing restaurants, skipping restaurant creation")
        return db.query(Restaurant).first()
    
    # Create a restaurant
    restaurant = Restaurant(
        name="Bella Italia",
        description="A cozy Italian restaurant offering authentic dishes from various regions of Italy.",
        logo_url="https://example.com/logos/bella_italia.png",
        website="https://bellaitalia.example.com",
        primary_color="#e53935",
        secondary_color="#4caf50",
        chatbot_greeting="Buongiorno! Welcome to Bella Italia. How can I assist you today?",
        cuisine_type="Italian",
        price_range="$$",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )
    db.add(restaurant)
    db.flush()  # Get restaurant ID
    
    # Associate the restaurant with the manager
    manager_user.restaurants.append(restaurant)
    
    logger.info(f"Created restaurant: {restaurant.name} (ID: {restaurant.id})")
    
    # Create location for the restaurant
    location = Location(
        restaurant_id=restaurant.id,
        address_line1="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        phone="(555) 123-4567",
        email="info@bellaitalia.example.com",
        is_primary=True
    )
    db.add(location)
    logger.info(f"Added location for {restaurant.name}")
    
    # Create operating hours
    days_of_week = range(7)  # 0=Monday through 6=Sunday
    for day in days_of_week:
        # Different hours for weekdays and weekends
        if day < 5:  # Monday-Friday
            hours = OperatingHours(
                restaurant_id=restaurant.id,
                day_of_week=day,
                open_time="11:00:00",
                close_time="22:00:00",
                is_closed=False
            )
        elif day == 5:  # Saturday
            hours = OperatingHours(
                restaurant_id=restaurant.id,
                day_of_week=day,
                open_time="12:00:00",
                close_time="23:00:00",
                is_closed=False
            )
        else:  # Sunday
            hours = OperatingHours(
                restaurant_id=restaurant.id,
                day_of_week=day,
                open_time="12:00:00",
                close_time="21:00:00",
                is_closed=False
            )
        db.add(hours)
    logger.info(f"Added operating hours for {restaurant.name}")
    
    # Create reservation settings
    reservation_settings = ReservationSettings(
        restaurant_id=restaurant.id,
        accepts_reservations=True,
        min_party_size=1,
        max_party_size=10,
        reservation_interval=30,  # In minutes
        advance_reservation_days=30,  # How many days in advance
        special_instructions="For parties larger than 10, please call us directly."
    )
    db.add(reservation_settings)
    logger.info(f"Added reservation settings for {restaurant.name}")
    
    # Create menus
    create_restaurant_menus(db, restaurant.id)
    
    # Create FAQs
    create_restaurant_faqs(db, restaurant.id)
    
    db.commit()
    logger.info(f"Test restaurant '{restaurant.name}' created successfully with all related data")
    return restaurant

def create_restaurant_menus(db, restaurant_id):
    """Create menus, categories and items for a restaurant"""
    logger.info(f"Creating menus for restaurant ID {restaurant_id}...")
    
    # Create lunch menu
    lunch_menu = Menu(
        restaurant_id=restaurant_id,
        name="Lunch Menu",
        description="Available daily from 11 AM to 3 PM",
        start_time="11:00:00",
        end_time="15:00:00",
        is_active=True
    )
    db.add(lunch_menu)
    db.flush()
    logger.info(f"Created Lunch Menu (ID: {lunch_menu.id})")
    
    # Create dinner menu
    dinner_menu = Menu(
        restaurant_id=restaurant_id,
        name="Dinner Menu",
        description="Our evening offerings, available from 5 PM to close",
        start_time="17:00:00",
        end_time="22:00:00",
        is_active=True
    )
    db.add(dinner_menu)
    db.flush()
    logger.info(f"Created Dinner Menu (ID: {dinner_menu.id})")
    
    # Create menu categories and items for dinner menu
    
    # Appetizers category
    appetizers = MenuCategory(
        menu_id=dinner_menu.id,
        name="Appetizers",
        description="Starters to share",
        display_order=1
    )
    db.add(appetizers)
    db.flush()
    
    # Pasta category
    pasta = MenuCategory(
        menu_id=dinner_menu.id,
        name="Pasta",
        description="Handmade pasta dishes",
        display_order=2
    )
    db.add(pasta)
    db.flush()
    
    # Main courses category
    main_courses = MenuCategory(
        menu_id=dinner_menu.id,
        name="Main Courses",
        description="Hearty entrees",
        display_order=3
    )
    db.add(main_courses)
    db.flush()
    
    # Desserts category
    desserts = MenuCategory(
        menu_id=dinner_menu.id,
        name="Desserts",
        description="Sweet treats to end your meal",
        display_order=4
    )
    db.add(desserts)
    db.flush()
    
    logger.info("Created menu categories")
    
    # Add menu items
    
    # Appetizers
    bruschetta = MenuItem(
        category_id=appetizers.id,
        name="Bruschetta",
        description="Grilled bread rubbed with garlic and topped with diced tomatoes, fresh basil, and olive oil",
        price=8.95,
        is_vegetarian=True,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=False,
        contains_alcohol=False,
        popular=True,
        display_order=1,
        is_active=True
    )
    db.add(bruschetta)
    db.flush()
    
    # Add ingredients to bruschetta
    for ingredient in ["Baguette", "Garlic", "Tomatoes", "Basil", "Olive Oil"]:
        ing = MenuItemIngredient(
            menu_item_id=bruschetta.id,
            name=ingredient,
            is_allergen=ingredient == "Garlic"
        )
        db.add(ing)
    
    # Calamari
    calamari = MenuItem(
        category_id=appetizers.id,
        name="Calamari Fritti",
        description="Crispy fried calamari served with marinara sauce and lemon wedges",
        price=12.95,
        is_vegetarian=False,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=False,
        contains_alcohol=False,
        popular=True,
        display_order=2,
        is_active=True
    )
    db.add(calamari)
    db.flush()
    
    # Add ingredients to calamari
    for ingredient in ["Calamari", "Flour", "Salt", "Pepper", "Marinara Sauce", "Lemon"]:
        ing = MenuItemIngredient(
            menu_item_id=calamari.id,
            name=ingredient,
            is_allergen=ingredient == "Calamari"
        )
        db.add(ing)
    
    # Pasta - Spaghetti Carbonara
    carbonara = MenuItem(
        category_id=pasta.id,
        name="Spaghetti Carbonara",
        description="Spaghetti with a creamy sauce of eggs, Pecorino Romano, pancetta, and black pepper",
        price=16.95,
        is_vegetarian=False,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=1,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=False,
        popular=True,
        chef_special=True,
        display_order=1,
        is_active=True
    )
    db.add(carbonara)
    db.flush()
    
    # Add ingredients to carbonara
    for ingredient in ["Spaghetti", "Eggs", "Pecorino Romano", "Pancetta", "Black Pepper"]:
        ing = MenuItemIngredient(
            menu_item_id=carbonara.id,
            name=ingredient,
            is_allergen=ingredient in ["Eggs", "Pecorino Romano"]
        )
        db.add(ing)
    
    # Pasta - Fettuccine Alfredo
    alfredo = MenuItem(
        category_id=pasta.id,
        name="Fettuccine Alfredo",
        description="Fettuccine pasta in a rich, creamy Parmesan cheese sauce",
        price=15.95,
        is_vegetarian=True,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=False,
        popular=True,
        display_order=2,
        is_active=True
    )
    db.add(alfredo)
    db.flush()
    
    # Add ingredients to alfredo
    for ingredient in ["Fettuccine", "Butter", "Heavy Cream", "Parmesan Cheese", "Garlic", "Black Pepper"]:
        ing = MenuItemIngredient(
            menu_item_id=alfredo.id,
            name=ingredient,
            is_allergen=ingredient in ["Parmesan Cheese", "Butter", "Heavy Cream"]
        )
        db.add(ing)
    
    # Main Course - Chicken Parmesan
    chicken_parm = MenuItem(
        category_id=main_courses.id,
        name="Chicken Parmesan",
        description="Breaded chicken breast topped with marinara sauce and melted mozzarella, served with spaghetti",
        price=21.95,
        is_vegetarian=False,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=False,
        popular=True,
        display_order=1,
        is_active=True
    )
    db.add(chicken_parm)
    db.flush()
    
    # Add ingredients to chicken parmesan
    for ingredient in ["Chicken Breast", "Breadcrumbs", "Eggs", "Marinara Sauce", "Mozzarella", "Spaghetti"]:
        ing = MenuItemIngredient(
            menu_item_id=chicken_parm.id,
            name=ingredient,
            is_allergen=ingredient in ["Eggs", "Mozzarella"]
        )
        db.add(ing)
    
    # Main Course - Osso Buco
    osso_buco = MenuItem(
        category_id=main_courses.id,
        name="Osso Buco",
        description="Braised veal shanks with vegetables, white wine and broth, served with risotto alla Milanese",
        price=28.95,
        is_vegetarian=False,
        is_vegan=False,
        is_gluten_free=True,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=True,
        chef_special=True,
        display_order=2,
        is_active=True
    )
    db.add(osso_buco)
    db.flush()
    
    # Dessert - Tiramisu
    tiramisu = MenuItem(
        category_id=desserts.id,
        name="Tiramisu",
        description="Coffee-soaked ladyfingers layered with mascarpone cream and dusted with cocoa powder",
        price=8.95,
        is_vegetarian=True,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=True,
        popular=True,
        display_order=1,
        is_active=True
    )
    db.add(tiramisu)
    db.flush()
    
    # Dessert - Panna Cotta
    panna_cotta = MenuItem(
        category_id=desserts.id,
        name="Panna Cotta",
        description="Silky vanilla custard topped with mixed berry compote",
        price=7.95,
        is_vegetarian=True,
        is_vegan=False,
        is_gluten_free=True,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=False,
        display_order=2,
        is_active=True
    )
    db.add(panna_cotta)
    db.flush()
    
    # Create similar categories for lunch menu (simplified version)
    lunch_apps = MenuCategory(
        menu_id=lunch_menu.id,
        name="Appetizers",
        description="Light starters",
        display_order=1
    )
    db.add(lunch_apps)
    
    lunch_mains = MenuCategory(
        menu_id=lunch_menu.id,
        name="Main Dishes",
        description="Lunch entrees",
        display_order=2
    )
    db.add(lunch_mains)
    
    db.flush()
    
    # Add a few items to lunch menu
    lunch_salad = MenuItem(
        category_id=lunch_apps.id,
        name="Caprese Salad",
        description="Fresh mozzarella, tomatoes, and basil drizzled with balsamic glaze",
        price=10.95,
        is_vegetarian=True,
        is_vegan=False,
        is_gluten_free=True,
        spice_level=0,
        contains_nuts=False,
        contains_dairy=True,
        contains_alcohol=False,
        popular=True,
        display_order=1,
        is_active=True
    )
    db.add(lunch_salad)
    
    lunch_panini = MenuItem(
        category_id=lunch_mains.id,
        name="Italian Panini",
        description="Ciabatta bread with prosciutto, mozzarella, tomato, and pesto",
        price=12.95,
        is_vegetarian=False,
        is_vegan=False,
        is_gluten_free=False,
        spice_level=0,
        contains_nuts=True,  # Pesto often contains pine nuts
        contains_dairy=True,
        contains_alcohol=False,
        popular=True,
        display_order=1,
        is_active=True
    )
    db.add(lunch_panini)
    
    logger.info("Added menu items to categories")
    
    # Commit all menu changes
    db.commit()
    logger.info("Restaurant menus created successfully")

def create_restaurant_faqs(db, restaurant_id):
    """Create FAQs for a restaurant"""
    logger.info(f"Creating FAQs for restaurant ID {restaurant_id}...")
    
    faqs = [
        # Reservations
        {
            "restaurant_id": restaurant_id,
            "question": "Do you accept reservations?",
            "answer": "Yes, we accept reservations for lunch and dinner. You can make a reservation through our website or by calling us.",
            "category": "Reservations",
            "display_order": 1
        },
        {
            "restaurant_id": restaurant_id,
            "question": "What is your cancellation policy?",
            "answer": "We ask that you cancel at least 2 hours before your reservation time. For parties of 6 or more, please cancel 24 hours in advance.",
            "category": "Reservations",
            "display_order": 2
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Can I make a reservation for a large group?",
            "answer": "Yes, we can accommodate groups up to 10 people through our online reservation system. For larger parties, please call us directly.",
            "category": "Reservations",
            "display_order": 3
        },
        
        # Menu
        {
            "restaurant_id": restaurant_id,
            "question": "Do you have vegetarian options?",
            "answer": "Yes, we have several vegetarian options on our menu. These are marked with a (V) symbol.",
            "category": "Menu",
            "display_order": 1
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Do you have gluten-free options?",
            "answer": "Yes, we offer gluten-free pasta as a substitute for most of our pasta dishes. Please inform your server of any allergies.",
            "category": "Menu",
            "display_order": 2
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Do you have a children's menu?",
            "answer": "Yes, we have a children's menu with smaller portions of pasta, pizza, and chicken dishes.",
            "category": "Menu",
            "display_order": 3
        },
        
        # Hours & Location
        {
            "restaurant_id": restaurant_id,
            "question": "What are your hours?",
            "answer": "We are open Monday to Friday from 11 AM to 10 PM, Saturday from 12 PM to 11 PM, and Sunday from 12 PM to 9 PM.",
            "category": "Hours",
            "display_order": 1
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Is there parking available?",
            "answer": "We offer validated parking in the garage next door for up to 2 hours.",
            "category": "Location",
            "display_order": 1
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Are you accessible by public transportation?",
            "answer": "Yes, we're located two blocks from the Main Street subway station on the Red Line.",
            "category": "Location",
            "display_order": 2
        },
        
        # Services
        {
            "restaurant_id": restaurant_id,
            "question": "Do you offer takeout?",
            "answer": "Yes, we offer takeout for all menu items. You can order online or by phone.",
            "category": "Services",
            "display_order": 1
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Do you deliver?",
            "answer": "We offer delivery through several delivery apps including UberEats, DoorDash, and GrubHub.",
            "category": "Services",
            "display_order": 2
        },
        {
            "restaurant_id": restaurant_id,
            "question": "Do you cater events?",
            "answer": "Yes, we offer catering for events of all sizes. Please contact us at least 48 hours in advance to discuss menu options and pricing.",
            "category": "Services",
            "display_order": 3
        }
    ]
    
    # Add all FAQs to the database
    for faq_data in faqs:
        faq = FAQ(**faq_data, is_active=True)
        db.add(faq)
    
    db.commit()
    logger.info(f"Created {len(faqs)} FAQs for the restaurant")

def seed_data():
    """Main function to seed the database with test data"""
    try:
        logger.info("Starting database seed process...")
        
        # Get database session
        db = get_db_session()
        
        # Create test users
        users = create_test_users(db)
        
        # Create test restaurant with all related data
        if users:
            restaurant = create_test_restaurant(db, users[1])  # Use the manager user
        
        logger.info("Database seeding completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_data()
    if success:
        print("✅ Database seeded successfully with test data!")
    else:
        print("❌ Failed to seed database.")
        sys.exit(1)
