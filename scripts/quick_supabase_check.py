#!/usr/bin/env python3
"""
Quick manual test to verify Supabase usage
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file
env_path = Path('.env')
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from app.config import Config
from app.database import db_adapter

def quick_check():
    """Quick verification of Supabase usage"""
    print("🔍 QUICK SUPABASE VERIFICATION")
    print("=" * 40)
    
    # 1. Check configuration
    print(f"1. Database Type: {Config.DATABASE_TYPE}")
    print(f"2. Database URL: {Config.DATABASE_URL[:30]}...")
    print(f"3. Supabase URL: {Config.SUPABASE_URL}")
    
    # 2. Test connection
    try:
        result = db_adapter.execute_query('SELECT version()', fetch_one=True)
        version = result['version'] if isinstance(result, dict) else result[0]
        print(f"4. Database Version: {version[:30]}...")
        
        # 3. Check for Supabase-specific features
        tables = db_adapter.execute_query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('contestants', 'tickets', 'votes')
        """, fetch_all=True)
        
        table_names = [t['table_name'] if isinstance(t, dict) else t[0] for t in tables]
        print(f"5. Core Tables: {table_names}")
        
        # 4. Check for Supabase functions
        functions = db_adapter.execute_query("""
            SELECT proname FROM pg_proc 
            WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            AND proname IN ('submit_vote', 'validate_ticket_code')
        """, fetch_all=True)
        
        func_names = [f['proname'] if isinstance(f, dict) else f[0] for f in functions]
        print(f"6. Supabase Functions: {func_names}")
        
        # 5. Check data
        contestant_count = db_adapter.execute_query('SELECT COUNT(*) FROM contestants', fetch_one=True)
        ticket_count = db_adapter.execute_query('SELECT COUNT(*) FROM tickets', fetch_one=True)
        vote_count = db_adapter.execute_query('SELECT COUNT(*) FROM votes', fetch_one=True)
        
        print(f"7. Data Counts:")
        print(f"   - Contestants: {contestant_count[0] if isinstance(contestant_count, tuple) else contestant_count['count']}")
        print(f"   - Tickets: {ticket_count[0] if isinstance(ticket_count, tuple) else ticket_count['count']}")
        print(f"   - Votes: {vote_count[0] if isinstance(vote_count, tuple) else vote_count['count']}")
        
        # 6. Check for SQLite files
        if os.path.exists('voting.db'):
            print("8. ❌ SQLite file found")
            return False
        else:
            print("8. ✅ No SQLite files")
        
        print("\n🎉 VERIFICATION COMPLETE!")
        print("✅ Your project is successfully using Supabase!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_check()
    sys.exit(0 if success else 1)
