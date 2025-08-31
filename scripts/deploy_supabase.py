#!/usr/bin/env python3
"""
Deploy script for setting up the voting system on Supabase
"""

import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config

def read_sql_file(file_path):
    """Read SQL file content"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def execute_sql_file(conn, file_path, description):
    """Execute SQL file"""
    print(f"📄 Executing {description}...")
    
    try:
        sql_content = read_sql_file(file_path)
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        cursor = conn.cursor()
        for statement in statements:
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        print(f"✅ {description} completed successfully")
        
    except Exception as e:
        print(f"❌ Error executing {description}: {e}")
        conn.rollback()
        raise

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def verify_deployment(conn):
    """Verify that tables and functions were created"""
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('contestants', 'tickets', 'votes', 'audit_log')
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    # Check views
    cursor.execute("""
        SELECT table_name FROM information_schema.views 
        WHERE table_schema = 'public' 
        AND table_name IN ('voting_results', 'ticket_stats')
    """)
    views = [row[0] for row in cursor.fetchall()]
    
    # Check functions
    cursor.execute("""
        SELECT routine_name FROM information_schema.routines 
        WHERE routine_schema = 'public' 
        AND routine_name IN ('validate_ticket_code', 'submit_vote', 'get_voting_stats')
    """)
    functions = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    
    print("\n📊 Deployment Verification:")
    print(f"   Tables: {', '.join(tables) if tables else 'None found'}")
    print(f"   Views: {', '.join(views) if views else 'None found'}")
    print(f"   Functions: {', '.join(functions) if functions else 'None found'}")
    
    expected_tables = {'contestants', 'tickets', 'votes', 'audit_log'}
    expected_views = {'voting_results', 'ticket_stats'}
    expected_functions = {'validate_ticket_code', 'submit_vote', 'get_voting_stats'}
    
    missing_tables = expected_tables - set(tables)
    missing_views = expected_views - set(views)
    missing_functions = expected_functions - set(functions)
    
    if missing_tables or missing_views or missing_functions:
        print("\n⚠️  Warning: Some objects are missing:")
        if missing_tables:
            print(f"   Missing tables: {', '.join(missing_tables)}")
        if missing_views:
            print(f"   Missing views: {', '.join(missing_views)}")
        if missing_functions:
            print(f"   Missing functions: {', '.join(missing_functions)}")
        return False
    else:
        print("\n✅ All expected database objects are present!")
        return True

def main():
    """Main deployment function"""
    print("🚀 Supabase Deployment Script")
    print("=" * 50)
    
    # Check if we're using PostgreSQL
    if not Config.DATABASE_URL.startswith('postgresql://'):
        print("❌ This script is for PostgreSQL/Supabase only")
        print(f"   Current DATABASE_URL: {Config.DATABASE_URL}")
        return 1
    
    print(f"🔗 Connecting to: {Config.DATABASE_URL[:50]}...")
    
    # Connect to database
    conn = check_database_connection()
    if not conn:
        return 1
    
    try:
        # Get the directory containing migration files
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
        
        # Execute migrations in order
        migrations = [
            ('supabase_001_create_tables.sql', 'Table creation'),
            ('supabase_002_views_functions.sql', 'Views and functions'),
            ('supabase_003_security_triggers.sql', 'Security and triggers')
        ]
        
        for filename, description in migrations:
            file_path = os.path.join(migrations_dir, filename)
            if os.path.exists(file_path):
                execute_sql_file(conn, file_path, description)
            else:
                print(f"⚠️  Warning: Migration file not found: {filename}")
        
        # Verify deployment
        if verify_deployment(conn):
            print("\n🎉 Supabase deployment completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Update your .env file with Supabase credentials")
            print("   2. Generate tickets using: python scripts/generate_tickets_supabase.py")
            print("   3. Test the application with the new database")
            print(f"   4. Set DATABASE_URL to your Supabase connection string")
        else:
            print("\n⚠️  Deployment completed with warnings")
            return 1
            
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return 1
    
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
