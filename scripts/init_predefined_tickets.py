#!/usr/bin/env python3
"""
Initialize pre-defined tickets in the database
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_adapter
from app.predefined_tickets import get_predefined_tickets
from app.config import Config

def sync_predefined_tickets():
    """Sync all pre-defined tickets to the database"""
    print("🎫 Syncing Pre-defined Tickets to Database")
    print("=" * 50)
    print(f"Database Type: {Config.DATABASE_TYPE}")
    print(f"Database URL: {Config.DATABASE_URL}")
    print()
    
    predefined_tickets = get_predefined_tickets()
    print(f"📊 Total pre-defined tickets: {len(predefined_tickets)}")
    
    # Check current ticket count in database
    try:
        current_count = db_adapter.execute_query('SELECT COUNT(*) FROM tickets', fetch_one=True)[0]
        print(f"📊 Current tickets in database: {current_count}")
        print()
    except Exception as e:
        print(f"❌ Error checking current tickets: {e}")
        return False
    
    # Sync tickets
    synced_count = 0
    error_count = 0
    
    print("🔄 Syncing tickets...")
    for i, ticket_code in enumerate(predefined_tickets):
        try:
            result = db_adapter.execute_query(
                "INSERT INTO tickets (ticket_code, is_used, created_at) VALUES (%s, FALSE, NOW()) ON CONFLICT (ticket_code) DO NOTHING RETURNING ticket_code",
                (ticket_code,),
                fetch_one=True
            )
            
            if result:
                synced_count += 1
                
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(predefined_tickets)} tickets...")
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error syncing {ticket_code}: {e}")
    
    print()
    print("📊 Sync Results:")
    print(f"   ✅ Successfully synced: {synced_count} new tickets")
    print(f"   📝 Already existed: {len(predefined_tickets) - synced_count - error_count}")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count}")
    
    # Verify final count
    try:
        final_count = db_adapter.execute_query('SELECT COUNT(*) FROM tickets', fetch_one=True)[0]
        print(f"   📊 Total tickets in database: {final_count}")
    except Exception as e:
        print(f"   ❌ Error checking final count: {e}")
    
    print()
    print("🎉 Pre-defined tickets sync completed!")
    
    # Show some sample tickets
    print("\n📝 Sample pre-defined tickets:")
    for i, ticket in enumerate(predefined_tickets[:10]):
        print(f"   {i+1:2d}. {ticket}")
    if len(predefined_tickets) > 10:
        print(f"   ... and {len(predefined_tickets) - 10} more")
    
    return True

def show_predefined_tickets():
    """Show all pre-defined tickets"""
    tickets = get_predefined_tickets()
    print("🎫 Pre-defined Ticket Codes")
    print("=" * 30)
    
    for i, ticket in enumerate(tickets, 1):
        print(f"{i:3d}. {ticket}")
    
    print(f"\nTotal: {len(tickets)} tickets")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage pre-defined tickets')
    parser.add_argument('--sync', action='store_true',
                       help='Sync pre-defined tickets to database')
    parser.add_argument('--list', action='store_true',
                       help='List all pre-defined tickets')
    
    args = parser.parse_args()
    
    if args.list:
        show_predefined_tickets()
    elif args.sync:
        sync_predefined_tickets()
    else:
        # Default action: show help
        parser.print_help()
        print("\nExamples:")
        print("  python scripts/init_predefined_tickets.py --sync   # Sync tickets to database")
        print("  python scripts/init_predefined_tickets.py --list   # List all pre-defined tickets")

if __name__ == "__main__":
    main()
