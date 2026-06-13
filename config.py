import os
from datetime import timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///food_order.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gmail configuration for password reset
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your Gmail address
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Gmail App Password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Password reset token expiry (30 minutes)
    RESET_TOKEN_EXPIRY = 1800
