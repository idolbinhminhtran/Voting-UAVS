from datetime import datetime
from . import get_db_connection
from .config import Config
from .database import db_adapter

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
        if Config.DATABASE_TYPE == 'postgresql':
            query = 'SELECT * FROM contestants WHERE is_active = true ORDER BY name'
        else:
            query = 'SELECT * FROM contestants WHERE is_active = 1 ORDER BY name'
        
        contestants = db_adapter.execute_query(query, fetch_all=True)
        return [Contestant(**dict(c)) for c in contestants]
    
    @staticmethod
    def get_by_id(contestant_id):
        """Get contestant by ID"""
        if Config.DATABASE_TYPE == 'postgresql':
            query = 'SELECT * FROM contestants WHERE id = %s AND is_active = true'
        else:
            query = 'SELECT * FROM contestants WHERE id = ? AND is_active = 1'
        
        contestant = db_adapter.execute_query(query, (contestant_id,), fetch_one=True)
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
        if Config.DATABASE_TYPE == 'postgresql':
            query = 'SELECT * FROM tickets WHERE ticket_code = %s'
        else:
            query = 'SELECT * FROM tickets WHERE ticket_code = ?'
        
        ticket = db_adapter.execute_query(query, (ticket_code,), fetch_one=True)
        return Ticket(**dict(ticket)) if ticket else None
    
    def mark_as_used(self):
        """Mark ticket as used"""
        if Config.DATABASE_TYPE == 'postgresql':
            query = 'UPDATE tickets SET is_used = true, used_at = NOW() WHERE id = %s'
            params = (self.id,)
        else:
            query = 'UPDATE tickets SET is_used = 1, used_at = ? WHERE id = ?'
            params = (datetime.utcnow(), self.id)
        
        db_adapter.execute_query(query, params)
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
        if Config.DATABASE_TYPE == 'postgresql':
            # Use the submit_vote function for PostgreSQL/Supabase
            result = db_adapter.execute_function('submit_vote', 
                [None, contestant_id, ip_address, user_agent])  # ticket_code will be resolved by function
            if result and result[0]['success']:
                return Vote(result[0]['vote_id'], contestant_id, ticket_id, ip_address, user_agent, datetime.utcnow())
            else:
                raise Exception(result[0]['message'] if result else 'Failed to create vote')
        else:
            query = '''INSERT INTO votes (contestant_id, ticket_id, ip_address, user_agent)
                       VALUES (?, ?, ?, ?)'''
            # For SQLite, we need to get the lastrowid differently
            with db_adapter.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (contestant_id, ticket_id, ip_address, user_agent))
                vote_id = cursor.lastrowid
                conn.commit()
                return Vote(vote_id, contestant_id, ticket_id, ip_address, user_agent, datetime.utcnow())
    
    @staticmethod
    def get_count_by_contestant(contestant_id):
        """Get vote count for a contestant"""
        if Config.DATABASE_TYPE == 'postgresql':
            query = 'SELECT COUNT(*) FROM votes WHERE contestant_id = %s'
        else:
            query = 'SELECT COUNT(*) FROM votes WHERE contestant_id = ?'
        
        result = db_adapter.execute_query(query, (contestant_id,), fetch_one=True)
        return result[0] if result else 0
    
    @staticmethod
    def get_total_count():
        """Get total vote count"""
        query = 'SELECT COUNT(*) FROM votes'
        result = db_adapter.execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
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
    if Config.DATABASE_TYPE == 'postgresql':
        # Use the voting_results view
        query = 'SELECT * FROM voting_results'
        results = db_adapter.execute_query(query, fetch_all=True)
        total_votes = sum(r['vote_count'] for r in results)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result['id'],
                'name': result['name'],
                'description': result['description'],
                'image_url': result['image_url'],
                'vote_count': result['vote_count'],
                'percentage': float(result['percentage'])
            })
        
        return formatted_results, total_votes
    else:
        # SQLite version
        query = '''
            SELECT c.id, c.name, c.description, c.image_url, 
                   COUNT(v.id) as vote_count
            FROM contestants c
            LEFT JOIN votes v ON c.id = v.contestant_id
            WHERE c.is_active = 1
            GROUP BY c.id, c.name, c.description, c.image_url
            ORDER BY vote_count DESC
        '''
        results = db_adapter.execute_query(query, fetch_all=True)
        
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
    if Config.DATABASE_TYPE == 'postgresql':
        # Use the ticket_stats view
        query = 'SELECT * FROM ticket_stats'
        result = db_adapter.execute_query(query, fetch_one=True)
        
        return {
            'total_tickets': result['total_tickets'],
            'used_tickets': result['used_tickets'],
            'unused_tickets': result['unused_tickets'],
            'usage_percentage': float(result['usage_percentage'])
        }
    else:
        # SQLite version
        total_query = 'SELECT COUNT(*) FROM tickets'
        used_query = 'SELECT COUNT(*) FROM tickets WHERE is_used = 1'
        
        total = db_adapter.execute_query(total_query, fetch_one=True)[0]
        used = db_adapter.execute_query(used_query, fetch_one=True)[0]
        unused = total - used
        usage_percentage = round((used / total * 100), 2) if total > 0 else 0
        
        return {
            'total_tickets': total,
            'used_tickets': used,
            'unused_tickets': unused,
            'usage_percentage': usage_percentage
        }
