#!/usr/bin/env python3
"""
Run seating system migration
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

def run_seating_migration():
    print('🚀 Running seating system migration...')

    # Read and execute migration
    migration_file = Path('migrations/seating_system_migration.sql')
    
    if not migration_file.exists():
        print('❌ Migration file not found!')
        return
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    try:
        # Execute the entire migration as one block to handle functions properly
        print('Executing migration...')
        db_adapter.execute_query(migration_sql)
        
        print('✅ Seating system migration completed successfully!')
        
        # Test the new tables
        sections = db_adapter.execute_query('SELECT * FROM seating_sections ORDER BY section_code', fetch_all=True)
        print(f'📊 Created {len(sections)} seating sections:')
        for section in sections:
            print(f'   - {section["section_code"]}: {section["section_name"]} ({section["max_capacity"]} seats)')
        
        # Count total seats
        total_seats = db_adapter.execute_query('SELECT COUNT(*) as count FROM seats', fetch_one=True)
        print(f'🪑 Total seats created: {total_seats["count"]}')
        
        # Test the view
        stats = db_adapter.execute_query('SELECT * FROM get_section_stats()', fetch_all=True)
        print(f'\n📈 Section Statistics:')
        for stat in stats:
            print(f'   {stat["section_code"]}: {stat["available_seats"]}/{stat["total_seats"]} available')
        
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_seating_migration()
