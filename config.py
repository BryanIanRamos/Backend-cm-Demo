import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    # PostgreSQL Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Provide a default key for development

    # Debugging mode
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't', 'y', 'yes']

    # Log level
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    # JWT Secret Key
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')  # Default key for development

    # CSRF Protection
    CSRF_ENABLED = os.getenv('CSRF_ENABLED', 'False').lower() in ['true', '1', 't', 'y', 'yes']
