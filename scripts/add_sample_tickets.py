#!/usr/bin/env python3
"""
Script to add sample tickets to the database for testing
"""

import sqlite3
import random
import string
from datetime import datetime

def generate_ticket_code(length=8):
    """Generate a random ticket code"""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    
    code = ''.join(random.choice(chars) for _ in range(length))
    return code

def add_sample_tickets(count=10):
    """Add sample tickets to the database"""
    conn = sqlite3.connect('voting.db')
    
    # Check if tickets already exist
    cursor = conn.execute('SELECT COUNT(*) FROM tickets')
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"Database already has {existing_count} tickets")
        conn.close()
        return
    
    print(f"Adding {count} sample tickets...")
    
    tickets = []
    for i in range(count):
        code = generate_ticket_code()
        tickets.append((code, datetime.now()))
    
    # Insert tickets
    conn.executemany(
        'INSERT INTO tickets (ticket_code, created_at) VALUES (?, ?)',
        tickets
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {count} sample tickets")
    print("\nSample ticket codes:")
    for i, (code, _) in enumerate(tickets[:5], 1):
        print(f"  {i}. {code}")
    
    if count > 5:
        print(f"  ... and {count - 5} more")

if __name__ == "__main__":
    add_sample_tickets(20)
