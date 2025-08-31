import hashlib
import time
from flask import request
from .config import Config

def rate_limit_key(identifier, window_minutes=60):
    """
    Generate a rate limit key for the given identifier
    Args:
        identifier: User identifier (IP, user_id, etc.)
        window_minutes: Time window in minutes
    Returns:
        Rate limit key string
    """
    # Round down to the nearest time window
    window_start = int(time.time() // (window_minutes * 60))
    key_data = f"{identifier}:{window_start}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_client_ip(request):
    """
    Get the real client IP address, handling proxies
    """
    # Check for forwarded headers
    if request.headers.get('X-Forwarded-For'):
        # Get the first IP in the chain
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def format_datetime(dt, timezone=None):
    """
    Format datetime to string with optional timezone conversion
    """
    if timezone is None:
        timezone = Config.TIMEZONE
    
    if dt.tzinfo is None:
        # If naive datetime, assume UTC
        import pytz
        dt = pytz.utc.localize(dt)
    
    # Convert to target timezone
    target_tz = pytz.timezone(timezone)
    dt = dt.astimezone(target_tz)
    
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

def is_valid_ticket_format(ticket_code):
    """
    Validate ticket code format
    """
    if not ticket_code:
        return False
    
    # Check length and alphanumeric
    if len(ticket_code) < 6 or len(ticket_code) > 20:
        return False
    
    # Allow alphanumeric and hyphens
    import re
    if not re.match(r'^[A-Za-z0-9\-]+$', ticket_code):
        return False
    
    return True

def sanitize_input(text, max_length=255):
    """
    Sanitize user input
    """
    if not text:
        return ""
    
    # Remove HTML tags
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def generate_ticket_code(length=8):
    """
    Generate a random ticket code
    """
    import random
    import string
    
    # Use uppercase letters and numbers, avoid confusing characters
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    
    code = ''.join(random.choice(chars) for _ in range(length))
    return code
