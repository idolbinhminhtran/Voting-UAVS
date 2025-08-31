#!/usr/bin/env python3
"""
Test script to verify Railway configuration
"""

import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file if it exists
env_path = Path('.env')
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from app.config import Config

def test_railway_config():
    """Test Railway-specific configuration"""
    print("🚂 RAILWAY CONFIGURATION TEST")
    print("=" * 40)
    
    # Test environment variables
    print(f"1. HOST: {Config.HOST}")
    print(f"2. PORT: {Config.PORT}")
    print(f"3. DATABASE_TYPE: {Config.DATABASE_TYPE}")
    print(f"4. DATABASE_URL: {Config.DATABASE_URL[:30]}...")
    print(f"5. SUPABASE_URL: {Config.SUPABASE_URL}")
    
    # Check Railway-specific requirements
    issues = []
    
    if Config.HOST != '0.0.0.0':
        issues.append("HOST should be '0.0.0.0' for Railway")
    
    if Config.PORT != 5000:
        issues.append("PORT should be 5000 for Railway")
    
    if not Config.DATABASE_URL or 'supabase' not in Config.DATABASE_URL:
        issues.append("DATABASE_URL should point to Supabase")
    
    if not Config.SUPABASE_URL:
        issues.append("SUPABASE_URL not set")
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("\n✅ All Railway configuration checks passed!")
        return True

if __name__ == "__main__":
    success = test_railway_config()
    sys.exit(0 if success else 1)
