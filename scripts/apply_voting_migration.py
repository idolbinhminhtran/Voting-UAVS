#!/usr/bin/env python3
"""
Apply voting status migration to Supabase database
"""
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_adapter

def apply_voting_migration():
    """Apply the voting status migration"""
    
    migration_sql = """
-- Migration 005: Add voting status table and helper functions

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Initialize voting_open flag if not exists
INSERT INTO app_settings (key, value)
VALUES ('voting_open', 'true')
ON CONFLICT (key) DO NOTHING;

-- Helper functions
CREATE OR REPLACE FUNCTION get_voting_open()
RETURNS BOOLEAN AS $$
DECLARE v TEXT; BEGIN
  SELECT value INTO v FROM app_settings WHERE key = 'voting_open';
  RETURN COALESCE(v, 'false')::BOOLEAN;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_voting_open(is_open BOOLEAN)
RETURNS VOID AS $$
BEGIN
  INSERT INTO app_settings (key, value, updated_at)
  VALUES ('voting_open', is_open::TEXT, NOW())
  ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
END $$ LANGUAGE plpgsql;
"""
    
    try:
        print("Applying voting status migration...")
        
        # Execute the migration SQL
        db_adapter.execute_query(migration_sql)
        
        print("✅ Migration applied successfully!")
        
        # Test the functions
        print("\nTesting functions...")
        result = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
        print(f"Current voting status: {'OPEN' if result['open'] else 'CLOSED'}")
        
        # Test setting voting status
        db_adapter.execute_query("SELECT set_voting_open(TRUE)")
        result = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
        print(f"After setting to OPEN: {'OPEN' if result['open'] else 'CLOSED'}")
        
        print("\n✅ All functions working correctly!")
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = apply_voting_migration()
    sys.exit(0 if success else 1)
