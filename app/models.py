from datetime import datetime
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
        query = 'SELECT * FROM contestants WHERE is_active = true ORDER BY name'
        contestants = db_adapter.execute_query(query, fetch_all=True)
        return [Contestant(**dict(c)) for c in contestants]
    
    @staticmethod
    def get_by_id(contestant_id):
        """Get contestant by ID"""
        query = 'SELECT * FROM contestants WHERE id = %s AND is_active = true'
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
        query = 'SELECT * FROM tickets WHERE ticket_code = %s'
        ticket = db_adapter.execute_query(query, (ticket_code,), fetch_one=True)
        return Ticket(**dict(ticket)) if ticket else None
    
    def mark_as_used(self):
        """Mark ticket as used"""
        query = 'UPDATE tickets SET is_used = true, used_at = NOW() WHERE id = %s'
        params = (self.id,)
        
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
        # Use the submit_vote function for Supabase
        result = db_adapter.execute_function('submit_vote', 
            [None, contestant_id, ip_address, user_agent])  # ticket_code will be resolved by function
        if result and result[0]['success']:
            return Vote(result[0]['vote_id'], contestant_id, ticket_id, ip_address, user_agent, datetime.utcnow())
        else:
            raise Exception(result[0]['message'] if result else 'Failed to create vote')
    
    @staticmethod
    def get_count_by_contestant(contestant_id):
        """Get vote count for a contestant"""
        query = 'SELECT COUNT(*) FROM votes WHERE contestant_id = %s'
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

def get_ticket_stats():
    """Get ticket statistics"""
    # Use the ticket_stats view
    query = 'SELECT * FROM ticket_stats'
    result = db_adapter.execute_query(query, fetch_one=True)
    
    return {
        'total_tickets': result['total_tickets'],
        'used_tickets': result['used_tickets'],
        'unused_tickets': result['unused_tickets'],
        'usage_percentage': float(result['usage_percentage'])
    }
