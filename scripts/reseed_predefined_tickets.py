#!/usr/bin/env python3
"""
Wipe votes and tickets, then seed only predefined tickets directly in Supabase.
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.predefined_tickets import get_predefined_tickets
from app.config import Config

def main():
    import psycopg2
    print("⚠️  WARNING: This will DELETE all votes and tickets, then insert predefined tickets only.")
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor()

        # Clear tables
        cur.execute('DELETE FROM votes')
        cur.execute('DELETE FROM tickets')

        tickets = get_predefined_tickets()
        for code in tickets:
            cur.execute(
                "INSERT INTO tickets (ticket_code, is_used, created_at) VALUES (%s, FALSE, NOW())",
                (code,)
            )

        conn.commit()
        print(f"✅ Reseeded {len(tickets)} predefined tickets")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error reseeding tickets: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


