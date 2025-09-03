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
    def __init__(self, id, ticket_code, is_used, created_at, used_at, seat_id=None, seat_code=None, section_code=None, **kwargs):
        self.id = id
        self.ticket_code = ticket_code
        self.is_used = is_used
        self.created_at = created_at
        self.used_at = used_at
        self.seat_id = seat_id
        self.seat_code = seat_code
        self.section_code = section_code
    
    @staticmethod
    def get_by_code(ticket_code):
        """Get ticket by code - uses pre-defined tickets system"""
        from .predefined_tickets import is_valid_ticket_code
        
        # First check if it's a valid pre-defined ticket
        if not is_valid_ticket_code(ticket_code):
            return None
        
        # Check if ticket exists in database and get its usage status
        query = 'SELECT * FROM tickets WHERE ticket_code = %s'
        ticket = db_adapter.execute_query(query, (ticket_code,), fetch_one=True)
        
        if ticket:
            return Ticket(**dict(ticket))
        else:
            # If ticket doesn't exist in database but is pre-defined, create it as unused
            from datetime import datetime
            insert_query = 'INSERT INTO tickets (ticket_code, is_used, created_at) VALUES (%s, FALSE, NOW()) RETURNING *'
            new_ticket = db_adapter.execute_query(insert_query, (ticket_code,), fetch_one=True)
            return Ticket(**dict(new_ticket)) if new_ticket else None
    
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
            'used_at': self.used_at,
            'seat_id': self.seat_id,
            'seat_code': self.seat_code,
            'section_code': self.section_code
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
    """Get ticket statistics based on pre-defined tickets"""
    from .predefined_tickets import get_predefined_tickets, get_ticket_count
    
    # Get stats from database for tickets that have been used
    try:
        # Try to use the ticket_stats view first
        query = 'SELECT * FROM ticket_stats'
        result = db_adapter.execute_query(query, fetch_one=True)
        if result:
            db_used = result['used_tickets']
            db_total = result['total_tickets']
        else:
            # Fallback to direct query
            db_stats = db_adapter.execute_query("""
                SELECT 
                    COUNT(*) as total_in_db,
                    SUM(CASE WHEN is_used THEN 1 ELSE 0 END) as used_tickets
                FROM tickets
            """, fetch_one=True)
            db_used = db_stats['used_tickets'] or 0
            db_total = db_stats['total_in_db'] or 0
    except:
        # Fallback to direct query if view doesn't exist
        db_stats = db_adapter.execute_query("""
            SELECT 
                COUNT(*) as total_in_db,
                SUM(CASE WHEN is_used THEN 1 ELSE 0 END) as used_tickets
            FROM tickets
        """, fetch_one=True)
        db_used = db_stats['used_tickets'] or 0
        db_total = db_stats['total_in_db'] or 0
    
    total_predefined = get_ticket_count()
    used_tickets = db_used
    unused_tickets = total_predefined - used_tickets
    usage_percentage = (used_tickets / total_predefined * 100) if total_predefined > 0 else 0
    
    return {
        'total_tickets': total_predefined,
        'used_tickets': used_tickets,
        'unused_tickets': unused_tickets,
        'usage_percentage': round(usage_percentage, 2),
        'predefined_count': total_predefined,
        'synced_to_db': db_total
    }
