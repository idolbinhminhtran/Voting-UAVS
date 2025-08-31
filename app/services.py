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
            # For PostgreSQL/Supabase, use the submit_vote function
            if Config.DATABASE_TYPE == 'postgresql':
                result = db_adapter.execute_function('submit_vote', 
                    [ticket_code, contestant_id, ip_address, user_agent])
                
                if result and len(result) > 0:
                    row = result[0]
                    if row['success']:
                        logger.info(f"Vote submitted successfully: Contestant {row['contestant_name']}, Ticket {ticket_code}")
                        return {
                            'success': True,
                            'contestant_name': row['contestant_name'],
                            'ticket_code': ticket_code,
                            'vote_id': row['vote_id']
                        }
                    else:
                        return {'success': False, 'error': row['message']}
                else:
                    return {'success': False, 'error': 'Failed to submit vote'}
            
            else:
                # SQLite version - original logic
                # Validate ticket
                ticket = Ticket.get_by_code(ticket_code)
                if not ticket:
                    return {'success': False, 'error': 'Invalid ticket code'}
                
                if ticket.is_used:
                    return {'success': False, 'error': 'Ticket already used'}
                
                # Validate contestant
                contestant = Contestant.get_by_id(contestant_id)
                if not contestant:
                    return {'success': False, 'error': 'Invalid contestant'}
                
                # Check voting time
                if not Config.is_voting_time():
                    return {'success': False, 'error': 'Voting is not allowed at this time'}
                
                # Create vote
                vote = Vote.create(contestant_id, ticket.id, ip_address, user_agent)
                
                # Mark ticket as used
                ticket.mark_as_used()
                
                logger.info(f"Vote submitted successfully: Contestant {contestant.name}, Ticket {ticket_code}")
                
                return {
                    'success': True,
                    'contestant_name': contestant.name,
                    'ticket_code': ticket_code,
                    'vote_id': vote.id
                }
                
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
            from . import get_db_connection
            conn = get_db_connection()
            
            # Delete all votes
            conn.execute('DELETE FROM votes')
            
            # Reset all tickets
            conn.execute('UPDATE tickets SET is_used = 0, used_at = NULL')
            
            conn.commit()
            conn.close()
            
            logger.info("Voting reset successfully")
            return True
                
        except Exception as e:
            logger.error(f"Error resetting voting: {str(e)}")
            return False
