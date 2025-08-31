from datetime import datetime
from . import get_db_connection
from .config import Config

class Contestant:
    def __init__(self, id, name, description, image_url, is_active, created_at):
        self.id = id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.is_active = is_active
        self.created_at = created_at
    
    @staticmethod
    def get_all():
        """Get all active contestants"""
        conn = get_db_connection()
        contestants = conn.execute(
            'SELECT * FROM contestants WHERE is_active = 1 ORDER BY name'
        ).fetchall()
        conn.close()
        
        return [Contestant(**dict(c)) for c in contestants]
    
    @staticmethod
    def get_by_id(contestant_id):
        """Get contestant by ID"""
        conn = get_db_connection()
        contestant = conn.execute(
            'SELECT * FROM contestants WHERE id = ? AND is_active = 1', 
            (contestant_id,)
        ).fetchone()
        conn.close()
        
        return Contestant(**dict(contestant)) if contestant else None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active
        }

class Ticket:
    def __init__(self, id, ticket_code, is_used, created_at, used_at):
        self.id = id
        self.ticket_code = ticket_code
        self.is_used = is_used
        self.created_at = created_at
        self.used_at = used_at
    
    @staticmethod
    def get_by_code(ticket_code):
        """Get ticket by code"""
        conn = get_db_connection()
        ticket = conn.execute(
            'SELECT * FROM tickets WHERE ticket_code = ?', 
            (ticket_code,)
        ).fetchone()
        conn.close()
        
        return Ticket(**dict(ticket)) if ticket else None
    
    def mark_as_used(self):
        """Mark ticket as used"""
        conn = get_db_connection()
        conn.execute(
            'UPDATE tickets SET is_used = 1, used_at = ? WHERE id = ?',
            (datetime.utcnow(), self.id)
        )
        conn.commit()
        conn.close()
        self.is_used = True
        self.used_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'ticket_code': self.ticket_code,
            'is_used': self.is_used,
            'created_at': self.created_at,
            'used_at': self.used_at
        }

class Vote:
    def __init__(self, id, contestant_id, ticket_id, ip_address, user_agent, created_at):
        self.id = id
        self.contestant_id = contestant_id
        self.ticket_id = ticket_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at
    
    @staticmethod
    def create(contestant_id, ticket_id, ip_address, user_agent):
        """Create a new vote"""
        conn = get_db_connection()
        cursor = conn.execute(
            '''INSERT INTO votes (contestant_id, ticket_id, ip_address, user_agent)
               VALUES (?, ?, ?, ?)''',
            (contestant_id, ticket_id, ip_address, user_agent)
        )
        vote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return Vote(vote_id, contestant_id, ticket_id, ip_address, user_agent, datetime.utcnow())
    
    @staticmethod
    def get_count_by_contestant(contestant_id):
        """Get vote count for a contestant"""
        conn = get_db_connection()
        count = conn.execute(
            'SELECT COUNT(*) FROM votes WHERE contestant_id = ?', 
            (contestant_id,)
        ).fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def get_total_count():
        """Get total vote count"""
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM votes').fetchone()[0]
        conn.close()
        return count
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'contestant_id': self.contestant_id,
            'ticket_id': self.ticket_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at
        }

# Database utility functions
def get_voting_results():
    """Get voting results with percentages"""
    conn = get_db_connection()
    
    # Get contestants with vote counts
    results = conn.execute('''
        SELECT c.id, c.name, c.description, c.image_url, 
               COUNT(v.id) as vote_count
        FROM contestants c
        LEFT JOIN votes v ON c.id = v.contestant_id
        WHERE c.is_active = 1
        GROUP BY c.id, c.name, c.description, c.image_url
        ORDER BY vote_count DESC
    ''').fetchall()
    
    conn.close()
    
    # Calculate percentages
    total_votes = sum(r['vote_count'] for r in results)
    
    formatted_results = []
    for result in results:
        percentage = round((result['vote_count'] / total_votes * 100), 2) if total_votes > 0 else 0
        formatted_results.append({
            'id': result['id'],
            'name': result['name'],
            'description': result['description'],
            'image_url': result['image_url'],
            'vote_count': result['vote_count'],
            'percentage': percentage
        })
    
    return formatted_results, total_votes

def get_ticket_stats():
    """Get ticket statistics"""
    conn = get_db_connection()
    
    total = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    used = conn.execute('SELECT COUNT(*) FROM tickets WHERE is_used = 1').fetchone()[0]
    unused = total - used
    
    conn.close()
    
    return {
        'total_tickets': total,
        'used_tickets': used,
        'unused_tickets': unused
    }
