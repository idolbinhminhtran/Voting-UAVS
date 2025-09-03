#!/usr/bin/env python3
"""
Simple script to sync predefined tickets to database
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.predefined_tickets import get_predefined_tickets
import psycopg2
from app.config import Config

def sync_tickets():
    """Sync predefined tickets directly to database"""
    print("🎫 Syncing Pre-defined Tickets to Supabase")
    print("=" * 50)
    
    tickets = get_predefined_tickets()
    print(f"📊 Total pre-defined tickets: {len(tickets)}")
    print(f"Tickets: {', '.join(tickets)}")
    print()
    
    try:
        # Connect directly to Supabase
        conn = psycopg2.connect(Config.DATABASE_URL)
        cursor = conn.cursor()
        
        # Check current tickets
        cursor.execute("SELECT COUNT(*) FROM tickets")
        current_count = cursor.fetchone()[0]
        print(f"📊 Current tickets in database: {current_count}")
        
        # Insert each predefined ticket
        synced_count = 0
        for ticket_code in tickets:
            try:
                cursor.execute(
                    "INSERT INTO tickets (ticket_code, is_used, created_at) VALUES (%s, FALSE, NOW()) ON CONFLICT (ticket_code) DO NOTHING RETURNING ticket_code",
                    (ticket_code,)
                )
                result = cursor.fetchone()
                if result:
                    synced_count += 1
                    print(f"   ✅ Added: {ticket_code}")
                else:
                    print(f"   ⏭️  Already exists: {ticket_code}")
            except Exception as e:
                print(f"   ❌ Error adding {ticket_code}: {e}")
        
        # Commit changes
        conn.commit()
        
        # Check final count
        cursor.execute("SELECT COUNT(*) FROM tickets")
        final_count = cursor.fetchone()[0]
        
        print()
        print("📊 Sync Results:")
        print(f"   ✅ Successfully synced: {synced_count} new tickets")
        print(f"   📝 Already existed: {len(tickets) - synced_count}")
        print(f"   📊 Total tickets in database: {final_count}")
        
        cursor.close()
        conn.close()
        
        print()
        print("🎉 Sync completed! You can now use these ticket codes:")
        for ticket in tickets:
            print(f"   - {ticket}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    sync_tickets()
