import os
from datetime import datetime
import pytz

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///voting.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Timezone
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
    
    # Voting settings
    VOTING_START_TIME = os.getenv('VOTING_START_TIME', '00:00')
    VOTING_END_TIME = os.getenv('VOTING_END_TIME', '23:59')
    
    # Rate limiting
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '10'))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Server configuration
    HOST = os.getenv('HOST', '127.0.0.1')  # Changed from 0.0.0.0 to 127.0.0.1
    PORT = int(os.getenv('PORT', '5004'))  # Changed to 5004
    
    @staticmethod
    def get_current_time():
        """Get current time in configured timezone"""
        tz = pytz.timezone(Config.TIMEZONE)
        return datetime.now(tz)
    
    @staticmethod
    def is_voting_time():
        """Check if current time is within voting hours"""
        # Always return True for 24-hour voting
        return True
