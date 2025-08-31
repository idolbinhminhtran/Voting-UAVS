#!/usr/bin/env python3
"""
Script to show the current status of all contestants
"""

import sqlite3
from datetime import datetime

def show_status():
    """Show current status of all contestants"""
    conn = sqlite3.connect('voting.db')
    
    print("🏆 TOP 10 FINALISTS - Current Status")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get contestants with vote counts
    contestants = conn.execute('''
        SELECT 
            c.id,
            c.name,
            c.description,
            COALESCE(COUNT(v.id), 0) as vote_count
        FROM contestants c
        LEFT JOIN votes v ON c.id = v.contestant_id
        WHERE c.is_active = 1
        GROUP BY c.id
        ORDER BY vote_count DESC, c.name
    ''').fetchall()
    
    total_votes = sum(c[3] for c in contestants)
    
    print(f"📊 Total Votes Cast: {total_votes}")
    print()
    
    for i, (id, name, description, votes) in enumerate(contestants, 1):
        percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        print(f"{i:2d}. {name}")
        print(f"    📝 {description}")
        print(f"    🗳️  Votes: {votes} ({percentage:.1f}%)")
        print()
    
    # Show ticket statistics
    ticket_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_tickets,
            SUM(CASE WHEN is_used = 1 THEN 1 ELSE 0 END) as used_tickets,
            SUM(CASE WHEN is_used = 0 THEN 1 ELSE 0 END) as available_tickets
        FROM tickets
    ''').fetchone()
    
    print("🎫 Ticket Statistics:")
    print(f"   Total Tickets: {ticket_stats[0]}")
    print(f"   Used Tickets: {ticket_stats[1]}")
    print(f"   Available Tickets: {ticket_stats[2]}")
    print()
    
    # Show voting hours
    print("⏰ Voting Hours: 24/7 (Always Open)")
    print("🌐 Website: http://localhost:5004/")
    print("🔧 Admin Panel: http://localhost:5004/admin")
    
    conn.close()

if __name__ == "__main__":
    show_status()
