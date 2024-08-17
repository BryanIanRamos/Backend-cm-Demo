import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    # PostgreSQL Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management
    # SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Debugging mode
    # DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't', 'y', 'yes']
    
    # Log level
    # LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
