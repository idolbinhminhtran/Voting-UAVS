#!/usr/bin/env python3
"""Delete all records in votes and tickets tables on Supabase."""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config

def main():
    import psycopg2
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute('DELETE FROM votes')
        cur.execute('DELETE FROM tickets')
        conn.commit()
        print('✅ Deleted all votes and tickets')
        cur.close()
        conn.close()
    except Exception as e:
        print('❌ Error clearing tickets:', e)
        sys.exit(1)

if __name__ == '__main__':
    main()


