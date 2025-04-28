import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Import your database configuration
try:
    from config.database import engine, Base, get_db
    from database.models import User, Restaurant  # Import some models to test
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have both database.py and models.py files created and properly formatted.")
    sys.exit(1)

def test_database_connection():
    """Test connection to the database"""
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            print("✅ Successfully connected to the database!")
            return True
    except Exception as e:
        print(f"❌ Failed to connect to the database: {str(e)}")
        return False

def test_create_tables():
    """Test creating tables from models"""
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print("✅ Successfully created database tables!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing database configuration...")
    print(f"Database URL: postgresql://{os.getenv('DB_USER')}:***@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    connection_success = test_database_connection()
    
    if connection_success:
        table_success = test_create_tables()
        
    print("Database testing completed.")