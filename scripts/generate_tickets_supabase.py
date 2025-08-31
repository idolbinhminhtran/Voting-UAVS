#!/usr/bin/env python3
"""
Generate voting tickets for Supabase (PostgreSQL)
"""

import sys
import os
import random
import string

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_adapter
from app.config import Config

def generate_ticket_code(length=8):
    """Generate a random ticket code"""
    # Use uppercase letters and numbers, excluding similar looking characters
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(length))

def ticket_exists(ticket_code):
    """Check if ticket code already exists"""
    if Config.DATABASE_TYPE == 'postgresql':
        query = 'SELECT COUNT(*) FROM tickets WHERE ticket_code = %s'
    else:
        query = 'SELECT COUNT(*) FROM tickets WHERE ticket_code = ?'
    
    result = db_adapter.execute_query(query, (ticket_code,), fetch_one=True)
    return result[0] > 0

def generate_tickets(count=100):
    """Generate unique ticket codes"""
    print(f"🎫 Generating {count} unique ticket codes...")
    
    tickets = []
    generated = 0
    
    while generated < count:
        ticket_code = generate_ticket_code()
        
        # Ensure uniqueness
        if not ticket_exists(ticket_code) and ticket_code not in [t[0] for t in tickets]:
            tickets.append((ticket_code,))
            generated += 1
            
            if generated % 10 == 0:
                print(f"   Generated {generated}/{count} tickets...")
    
    return tickets

def insert_tickets(tickets):
    """Insert tickets into database"""
    print(f"💾 Inserting {len(tickets)} tickets into database...")
    
    if Config.DATABASE_TYPE == 'postgresql':
        # Use batch insert for PostgreSQL
        query = 'INSERT INTO tickets (ticket_code) VALUES %s'
        # For PostgreSQL, we need to format the values properly
        values = ','.join([f"('{ticket[0]}')" for ticket in tickets])
        full_query = f"INSERT INTO tickets (ticket_code) VALUES {values}"
        db_adapter.execute_query(full_query)
    else:
        # Use executemany for SQLite
        query = 'INSERT INTO tickets (ticket_code) VALUES (?)'
        with db_adapter.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, tickets)
            conn.commit()
    
    print(f"✅ Successfully inserted {len(tickets)} tickets!")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate voting tickets for Supabase')
    parser.add_argument('--count', type=int, default=100, 
                       help='Number of tickets to generate (default: 100)')
    parser.add_argument('--force', action='store_true',
                       help='Force generation even if tickets already exist')
    
    args = parser.parse_args()
    
    print("🚀 Ticket Generator for Supabase")
    print("=" * 40)
    print(f"Database Type: {Config.DATABASE_TYPE}")
    print(f"Database URL: {Config.DATABASE_URL}")
    print()
    
    # Check current ticket count
    try:
        if Config.DATABASE_TYPE == 'postgresql':
            count_query = 'SELECT COUNT(*) FROM tickets'
        else:
            count_query = 'SELECT COUNT(*) FROM tickets'
        
        current_count = db_adapter.execute_query(count_query, fetch_one=True)[0]
        print(f"📊 Current tickets in database: {current_count}")
        
        if current_count > 0 and not args.force:
            response = input("Tickets already exist. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted by user")
                return
        
        # Generate and insert tickets
        tickets = generate_tickets(args.count)
        insert_tickets(tickets)
        
        # Verify insertion
        new_count = db_adapter.execute_query(count_query, fetch_one=True)[0]
        print(f"📊 Total tickets after generation: {new_count}")
        
        print("\n🎉 Ticket generation completed successfully!")
        
        # Show some sample tickets
        if Config.DATABASE_TYPE == 'postgresql':
            sample_query = 'SELECT ticket_code FROM tickets ORDER BY created_at DESC LIMIT 5'
        else:
            sample_query = 'SELECT ticket_code FROM tickets ORDER BY created_at DESC LIMIT 5'
        
        samples = db_adapter.execute_query(sample_query, fetch_all=True)
        print("\n📝 Sample ticket codes:")
        for sample in samples:
            print(f"   • {sample[0] if isinstance(sample, (tuple, list)) else sample['ticket_code']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
