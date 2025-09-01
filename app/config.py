import os
from datetime import datetime
import pytz
from pathlib import Path

# Load .env file if it exists
env_path = Path('.env')
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

class Config:
    # Database - Supabase PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:[password]@db.[project_id].supabase.co:5432/postgres')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Database type detection
    DATABASE_TYPE = 'postgresql'
    
    # Timezone
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
    
    # Voting settings
    VOTING_START_TIME = os.getenv('VOTING_START_TIME', '00:00')
    VOTING_END_TIME = os.getenv('VOTING_END_TIME', '23:59')
    
    # Rate limiting
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '10'))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Admin credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', 'fcf730b6d95236ecd3c9fc2d92d7b6b2bb061514961aec041d6c7a7192f592e4')  # Default: secret123
    
    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')  # Use 0.0.0.0 for Railway deployment
    PORT = int(os.getenv('PORT', '5000'))  # Use 5000 for Railway
    
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
