from flask import Blueprint, request, jsonify
from .models import Contestant, get_voting_results, get_ticket_stats
from .services import VotingService
from .utils import rate_limit_key, get_client_ip
from .config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/vote', methods=['POST'])
def submit_vote():
    """Submit a vote for a contestant"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        ticket_code = data.get('ticket_code')
        contestant_id = data.get('contestant_id')
        
        if not ticket_code or not contestant_id:
            return jsonify({'error': 'Missing ticket_code or contestant_id'}), 400
        
        # Check if voting is currently allowed
        if not Config.is_voting_time():
            return jsonify({'error': 'Voting is not allowed at this time'}), 403
        
        # Submit vote using service
        result = VotingService.submit_vote(
            ticket_code=ticket_code,
            contestant_id=contestant_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get('User-Agent')
        )
        
        if result['success']:
            return jsonify({
                'message': 'Vote submitted successfully',
                'contestant_name': result['contestant_name']
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/results', methods=['GET'])
def get_results():
    """Get current voting results"""
    try:
        results, total_votes = get_voting_results()
        
        return jsonify({
            'results': results,
            'total_votes': total_votes,
            'voting_open': Config.is_voting_time(),
            'current_time': Config.get_current_time().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/contestants', methods=['GET'])
def get_contestants():
    """Get list of active contestants"""
    try:
        contestants = Contestant.get_all()
        return jsonify([contestant.to_dict() for contestant in contestants]), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/ticket/validate', methods=['POST'])
def validate_ticket():
    """Validate if a ticket code is valid and unused"""
    try:
        data = request.get_json()
        ticket_code = data.get('ticket_code')
        
        if not ticket_code:
            return jsonify({'error': 'Missing ticket_code'}), 400
        
        from .models import Ticket
        ticket = Ticket.get_by_code(ticket_code)
        
        if not ticket:
            return jsonify({'valid': False, 'error': 'Invalid ticket code'})
        
        if ticket.is_used:
            return jsonify({'valid': False, 'error': 'Ticket already used'})
        
        return jsonify({'valid': True, 'message': 'Ticket is valid'})
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/ticket/stats', methods=['GET'])
def get_ticket_statistics():
    """Get ticket statistics for admin panel"""
    try:
        from .models import get_ticket_stats
        stats = get_ticket_stats()
        
        return jsonify({
            'total_tickets': stats['total_tickets'],
            'used_tickets': stats['used_tickets'],
            'unused_tickets': stats['unused_tickets'],
            'usage_percentage': round((stats['used_tickets'] / stats['total_tickets'] * 100), 2) if stats['total_tickets'] > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
