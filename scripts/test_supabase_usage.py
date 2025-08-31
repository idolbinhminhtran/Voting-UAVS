#!/usr/bin/env python3
"""
Comprehensive test script to verify Supabase usage
Tests database connection, configuration, and functionality
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

from app.config import Config
from app.database import db_adapter
from app.models import Contestant, Ticket, Vote

def test_configuration():
    """Test if configuration is set for Supabase"""
    print("🔧 Testing Configuration...")
    print(f"   Database Type: {Config.DATABASE_TYPE}")
    print(f"   Database URL: {Config.DATABASE_URL[:50]}...")
    print(f"   Supabase URL: {Config.SUPABASE_URL}")
    print(f"   Supabase Anon Key: {Config.SUPABASE_ANON_KEY[:20]}...")
    
    # Check if it's PostgreSQL/Supabase
    if Config.DATABASE_TYPE == 'postgresql':
        print("   ✅ Configuration: PostgreSQL/Supabase")
        return True
    else:
        print("   ❌ Configuration: Not PostgreSQL/Supabase")
        return False

def test_database_connection():
    """Test database connection to Supabase"""
    print("\n🔌 Testing Database Connection...")
    try:
        # Test PostgreSQL version
        result = db_adapter.execute_query('SELECT version()', fetch_one=True)
        if isinstance(result, dict):
            version = result['version']
        elif isinstance(result, tuple):
            version = result[0]
        else:
            version = str(result)
        
        print(f"   ✅ Connected to: {version}")
        
        # Test if it's Supabase (should contain 'PostgreSQL' in version)
        if 'PostgreSQL' in version:
            print("   ✅ Database: PostgreSQL (Supabase)")
            return True
        else:
            print("   ❌ Database: Not PostgreSQL")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def test_supabase_tables():
    """Test if Supabase tables exist"""
    print("\n📋 Testing Supabase Tables...")
    try:
        # Check for Supabase-specific tables
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        tables = db_adapter.execute_query(tables_query, fetch_all=True)
        
        expected_tables = ['contestants', 'tickets', 'votes']
        found_tables = [table[0] if isinstance(table, tuple) else table['table_name'] for table in tables]
        
        print(f"   Found tables: {found_tables}")
        
        # Check if all expected tables exist
        missing_tables = [table for table in expected_tables if table not in found_tables]
        if missing_tables:
            print(f"   ❌ Missing tables: {missing_tables}")
            return False
        else:
            print("   ✅ All expected tables found")
            return True
            
    except Exception as e:
        print(f"   ❌ Table check failed: {e}")
        return False

def test_supabase_views():
    """Test if Supabase views exist"""
    print("\n👁️ Testing Supabase Views...")
    try:
        # Check for Supabase-specific views
        views_query = """
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'public'
            ORDER BY viewname
        """
        views = db_adapter.execute_query(views_query, fetch_all=True)
        
        expected_views = ['voting_results', 'ticket_stats']
        found_views = [view[0] if isinstance(view, tuple) else view['viewname'] for view in views]
        
        print(f"   Found views: {found_views}")
        
        # Check if expected views exist
        missing_views = [view for view in expected_views if view not in found_views]
        if missing_views:
            print(f"   ⚠️ Missing views: {missing_views}")
            return False
        else:
            print("   ✅ All expected views found")
            return True
            
    except Exception as e:
        print(f"   ❌ View check failed: {e}")
        return False

def test_supabase_functions():
    """Test if Supabase functions exist"""
    print("\n⚙️ Testing Supabase Functions...")
    try:
        # Check for Supabase-specific functions
        functions_query = """
            SELECT proname 
            FROM pg_proc 
            WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY proname
        """
        functions = db_adapter.execute_query(functions_query, fetch_all=True)
        
        expected_functions = ['submit_vote', 'validate_ticket_code']
        found_functions = [func[0] if isinstance(func, tuple) else func['proname'] for func in functions]
        
        print(f"   Found functions: {found_functions}")
        
        # Check if expected functions exist
        missing_functions = [func for func in expected_functions if func not in found_functions]
        if missing_functions:
            print(f"   ⚠️ Missing functions: {missing_functions}")
            return False
        else:
            print("   ✅ All expected functions found")
            return True
            
    except Exception as e:
        print(f"   ❌ Function check failed: {e}")
        return False

def test_model_functionality():
    """Test if models work with Supabase"""
    print("\n🏗️ Testing Model Functionality...")
    try:
        # Test Contestant model
        contestants = Contestant.get_all()
        print(f"   ✅ Contestants loaded: {len(contestants)} found")
        
        # Test Ticket model
        tickets = db_adapter.execute_query('SELECT COUNT(*) FROM tickets', fetch_one=True)
        ticket_count = tickets[0] if isinstance(tickets, tuple) else tickets['count']
        print(f"   ✅ Tickets count: {ticket_count}")
        
        # Test Vote model
        votes = db_adapter.execute_query('SELECT COUNT(*) FROM votes', fetch_one=True)
        vote_count = votes[0] if isinstance(votes, tuple) else votes['count']
        print(f"   ✅ Votes count: {vote_count}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
        return False

def test_sqlite_absence():
    """Test that no SQLite files are being created"""
    print("\n🚫 Testing SQLite Absence...")
    
    # Check if voting.db exists
    if os.path.exists('voting.db'):
        print("   ❌ SQLite file 'voting.db' exists")
        return False
    else:
        print("   ✅ No SQLite file found")
    
    # Check if any .db files exist
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    if db_files:
        print(f"   ❌ Found SQLite files: {db_files}")
        return False
    else:
        print("   ✅ No SQLite files found")
    
    return True

def main():
    """Run all tests"""
    print("🧪 SUPABASE USAGE TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Supabase Tables", test_supabase_tables),
        ("Supabase Views", test_supabase_views),
        ("Supabase Functions", test_supabase_functions),
        ("Model Functionality", test_model_functionality),
        ("SQLite Absence", test_sqlite_absence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your project is properly using Supabase.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
