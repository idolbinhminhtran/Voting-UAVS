#!/usr/bin/env python3
"""
Database connection test script
Tests connection for both SQLite and PostgreSQL databases
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file if it exists
env_path = Path('.env')
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from app.database import db_adapter
from app.config import Config

def test_database_connection():
    """Test database connection and show database info"""
    print(f"Database Type: {Config.DATABASE_TYPE}")
    print(f"Database URL: {Config.DATABASE_URL[:50]}...")
    
    try:
        # Test basic connection
        if Config.DATABASE_TYPE == 'postgresql':
            # PostgreSQL version query
            result = db_adapter.execute_query('SELECT version()', fetch_one=True)
            print('✅ Database connected successfully!')
            print(f'PostgreSQL version: {result[0]}')
        else:
            # SQLite version query
            result = db_adapter.execute_query('SELECT sqlite_version()', fetch_one=True)
            print('✅ Database connected successfully!')
            print(f'SQLite version: {result[0]}')
        
        # Test if tables exist
        print("\nChecking database tables...")
        if Config.DATABASE_TYPE == 'postgresql':
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
        else:
            tables_query = """
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """
        
        tables = db_adapter.execute_query(tables_query, fetch_all=True)
        if tables:
            print("✅ Found tables:")
            for table in tables:
                table_name = table[0] if isinstance(table, tuple) else table['table_name'] if Config.DATABASE_TYPE == 'postgresql' else table['name']
                print(f"  - {table_name}")
        else:
            print("⚠️  No tables found in database")
            
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False
    
    return True

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
