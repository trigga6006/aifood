from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# Many-to-many relationship between Users and Restaurants (for staff/managers)
user_restaurant_association = Table(
    'user_restaurant_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('restaurant_id', Integer, ForeignKey('restaurants.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default='restaurant_manager')  # admin, restaurant_manager, staff
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    restaurants = relationship("Restaurant", secondary=user_restaurant_association, back_populates="users")

class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_url = Column(String(512))
    website = Column(String(255))
    primary_color = Column(String(50))  # For UI customization
    secondary_color = Column(String(50))  # For UI customization
    chatbot_greeting = Column(Text)  # Custom greeting for the chatbot
    cuisine_type = Column(String(100))
    price_range = Column(String(20))  # $, $$, $$$, $$$$
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    blob_storage_path = Column(String(512))  # Path to restaurant assets in Azure blob storage
    
    # Relationships
    users = relationship("User", secondary=user_restaurant_association, back_populates="restaurants")
    locations = relationship("Location", back_populates="restaurant", cascade="all, delete-orphan")
    hours = relationship("OperatingHours", back_populates="restaurant", cascade="all, delete-orphan")
    menus = relationship("Menu", back_populates="restaurant", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="restaurant", cascade="all, delete-orphan")
    chatbot_logs = relationship("ChatbotLog", back_populates="restaurant", cascade="all, delete-orphan")
    reservation_settings = relationship("ReservationSettings", back_populates="restaurant", uselist=False)

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="locations")

class OperatingHours(Base):
    __tablename__ = 'operating_hours'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday through 6=Sunday
    open_time = Column(String(8), nullable=False)  # Format: "HH:MM:SS"
    close_time = Column(String(8), nullable=False)  # Format: "HH:MM:SS"
    is_closed = Column(Boolean, default=False)  # For handling days when restaurant is closed
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="hours")

class Menu(Base):
    __tablename__ = 'menus'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    name = Column(String(100), nullable=False)  # Breakfast, Lunch, Dinner, etc.
    description = Column(Text)
    start_time = Column(String(8))  # When this menu becomes available, format: "HH:MM:SS"
    end_time = Column(String(8))    # When this menu ends, format: "HH:MM:SS"
    is_active = Column(Boolean, default=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menus")
    categories = relationship("MenuCategory", back_populates="menu", cascade="all, delete-orphan")

class MenuCategory(Base):
    __tablename__ = 'menu_categories'
    
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=False)
    name = Column(String(100), nullable=False)  # Appetizers, Entrees, Desserts, etc.
    description = Column(Text)
    display_order = Column(Integer, default=0)
    
    # Relationships
    menu = relationship("Menu", back_populates="categories")
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")

class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('menu_categories.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(512))
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    spice_level = Column(Integer)  # 0=Not Spicy to 5=Very Spicy
    contains_nuts = Column(Boolean, default=False)
    contains_dairy = Column(Boolean, default=False)
    contains_alcohol = Column(Boolean, default=False)
    popular = Column(Boolean, default=False)
    chef_special = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    category = relationship("MenuCategory", back_populates="items")
    ingredients = relationship("MenuItemIngredient", back_populates="menu_item", cascade="all, delete-orphan")

class MenuItemIngredient(Base):
    __tablename__ = 'menu_item_ingredients'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    name = Column(String(255), nullable=False)
    is_allergen = Column(Boolean, default=False)
    
    # Relationships
    menu_item = relationship("MenuItem", back_populates="ingredients")

class FAQ(Base):
    __tablename__ = 'faqs'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))  # Categorize FAQs: Reservations, Menu, Hours, etc.
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="faqs")

class ChatbotLog(Base):
    __tablename__ = 'chatbot_logs'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    session_id = Column(String(255), nullable=False)
    user_input = Column(Text, nullable=False)
    chatbot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    feedback_rating = Column(Integer)  # Optional user feedback (1-5)
    feedback_text = Column(Text)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="chatbot_logs")

class ReservationSettings(Base):
    __tablename__ = 'reservation_settings'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False, unique=True)
    accepts_reservations = Column(Boolean, default=True)
    min_party_size = Column(Integer, default=1)
    max_party_size = Column(Integer, default=10)
    reservation_interval = Column(Integer, default=30)  # In minutes
    advance_reservation_days = Column(Integer, default=30)  # How many days in advance reservations can be made
    special_instructions = Column(Text)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="reservation_settings")