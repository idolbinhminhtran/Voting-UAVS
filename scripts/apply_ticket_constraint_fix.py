#!/usr/bin/env python3
"""
Apply the ticket constraint fix to allow shorter ticket codes like D13.6
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_adapter
from app.config import Config

def apply_constraint_fix():
    """Apply the ticket constraint fix"""
    print("🔧 Applying Ticket Constraint Fix")
    print("=" * 40)
    print(f"Database Type: {Config.DATABASE_TYPE}")
    print(f"Database URL: {Config.DATABASE_URL}")
    print()
    
    try:
        # Drop the old constraint
        print("1. Dropping old ticket_code constraint...")
        db_adapter.execute_query(
            "ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_ticket_code_check"
        )
        print("   ✅ Old constraint dropped")
        
        # Add the new constraint (4-20 characters instead of 6-20)
        print("2. Adding new ticket_code constraint (4-20 characters)...")
        db_adapter.execute_query(
            "ALTER TABLE tickets ADD CONSTRAINT tickets_ticket_code_check CHECK (LENGTH(ticket_code) >= 4 AND LENGTH(ticket_code) <= 20)"
        )
        print("   ✅ New constraint added")
        
        # Test the constraint with a sample ticket code
        print("3. Testing constraint with D13.6...")
        try:
            # Try to insert a test ticket
            db_adapter.execute_query(
                "INSERT INTO tickets (ticket_code, is_used) VALUES ('TEST.1', FALSE) ON CONFLICT (ticket_code) DO NOTHING"
            )
            print("   ✅ Constraint test passed")
            
            # Clean up test ticket
            db_adapter.execute_query("DELETE FROM tickets WHERE ticket_code = 'TEST.1'")
            
        except Exception as test_error:
            print(f"   ❌ Constraint test failed: {test_error}")
            return False
        
        print()
        print("🎉 Ticket constraint fix applied successfully!")
        print("Now ticket codes like D13.6, A2.R3.5 will work properly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying constraint fix: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Ticket Constraint Fix Script")
    print("This will fix the database constraint to allow shorter ticket codes")
    print()
    
    response = input("Do you want to apply the fix? (y/N): ")
    if response.lower() != 'y':
        print("❌ Aborted by user")
        return
    
    success = apply_constraint_fix()
    
    if success:
        print("\n✅ Fix applied successfully!")
        print("You can now use ticket codes like D13.6 in the voting system.")
    else:
        print("\n❌ Fix failed! Please check the error messages above.")

if __name__ == "__main__":
    main()
