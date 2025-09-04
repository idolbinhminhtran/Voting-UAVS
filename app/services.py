from .models import Contestant, Ticket, Vote, get_voting_results, get_ticket_stats
from .config import Config
from .database import db_adapter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VotingService:
    @staticmethod
    def submit_vote(ticket_code, contestant_id, ip_address, user_agent):
        """
        Submit a vote with transaction safety
        Returns: dict with 'success' boolean and additional info
        """
        try:
            # Use the submit_vote function for Supabase
            result = db_adapter.execute_function('submit_vote', 
                [ticket_code.strip(), contestant_id, ip_address, user_agent])
            
            if result and len(result) > 0:
                row = result[0]
                if row['success']:
                    logger.info(f"Vote submitted successfully: Contestant {row['contestant_name']}, Ticket {ticket_code.strip()}")
                    return {
                        'success': True,
                        'contestant_name': row['contestant_name'],
                        'ticket_code': ticket_code.strip(),
                        'vote_id': row['vote_id']
                    }
                else:
                    return {'success': False, 'error': row['message']}
            else:
                return {'success': False, 'error': 'Failed to submit vote'}
                
        except Exception as e:
            logger.error(f"Error submitting vote: {str(e)}")
            return {'success': False, 'error': 'Failed to submit vote'}
    
    @staticmethod
    def get_voting_stats():
        """Get comprehensive voting statistics"""
        try:
            ticket_stats = get_ticket_stats()
            results, total_votes = get_voting_results()
            
            return {
                'total_tickets': ticket_stats['total_tickets'],
                'used_tickets': ticket_stats['used_tickets'],
                'unused_tickets': ticket_stats['unused_tickets'],
                'contestant_stats': results,
                'voting_open': Config.is_voting_time(),
                'current_time': Config.get_current_time().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting voting stats: {str(e)}")
            return None
    
    @staticmethod
    def reset_voting():
        """Reset all votes and tickets (admin function)"""
        try:
            # Delete all votes
            db_adapter.execute_query('DELETE FROM votes')
            
            # Reset all tickets
            db_adapter.execute_query('UPDATE tickets SET is_used = FALSE, used_at = NULL')
            
            logger.info("Voting reset successfully")
            return True
                
        except Exception as e:
            logger.error(f"Error resetting voting: {str(e)}")
            return False

    @staticmethod
    def generate_tickets(count=100):
        """Generate new tickets directly in database."""
        try:
            import string
            import random
            
            # Start by clearing dependent table
            db_adapter.execute_query('DELETE FROM votes')
            # Clear tickets table entirely
            db_adapter.execute_query('DELETE FROM tickets')

            inserted = 0
            for i in range(count):
                # Generate a random ticket code (8 characters)
                ticket_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                try:
                    db_adapter.execute_query(
                        "INSERT INTO tickets (ticket_code, is_used, created_at) VALUES (%s, FALSE, NOW())",
                        (ticket_code,)
                    )
                    inserted += 1
                except Exception:
                    # If duplicate, try again with different code
                    continue
                    
            logger.info(f"Generated {inserted} new tickets")
            return {"success": True, "inserted": inserted}
        except Exception as e:
            logger.error(f"Error generating tickets: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def clear_all_tickets():
        """Delete all records in tickets (and dependent votes)."""
        try:
            db_adapter.execute_query('DELETE FROM votes')
            db_adapter.execute_query('DELETE FROM tickets')
            logger.info("All tickets cleared")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error clearing tickets: {str(e)}")
            return {"success": False, "error": str(e)}
