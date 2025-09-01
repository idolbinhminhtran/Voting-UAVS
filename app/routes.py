from flask import Blueprint, request, jsonify, session
from .models import Contestant, get_voting_results, get_ticket_stats
from .services import VotingService
from .utils import rate_limit_key, get_client_ip
from .config import Config
import hashlib
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Admin authentication
def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return jsonify({'error': 'Admin authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@api_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Admin credentials (you can change these)
        ADMIN_USERNAME = Config.ADMIN_USERNAME
        ADMIN_PASSWORD_HASH = Config.ADMIN_PASSWORD_HASH
        
        # Verify credentials
        if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
            session['admin_authenticated'] = True
            session['admin_username'] = username
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@api_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@api_bp.route('/admin/status', methods=['GET'])
def admin_status():
    """Check admin authentication status"""
    return jsonify({
        'authenticated': session.get('admin_authenticated', False),
        'username': session.get('admin_username', None)
    }), 200

@api_bp.route('/admin/reset-voting', methods=['POST'])
@require_admin
def reset_voting():
    """Reset all voting data"""
    try:
        from .services import VotingService
        VotingService.reset_voting()
        return jsonify({'success': True, 'message': 'Voting has been reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to reset voting'}), 500

@api_bp.route('/admin/generate-tickets', methods=['POST'])
@require_admin
def generate_tickets():
    """Generate new tickets"""
    try:
        data = request.get_json() or {}
        count = data.get('count', 100)
        
        from .utils import generate_ticket_code
        from .database import db_adapter
        
        # Generate unique ticket codes
        generated_tickets = []
        for i in range(count):
            ticket_code = generate_ticket_code()
            generated_tickets.append(ticket_code)
        
        # Insert tickets into database
        for ticket_code in generated_tickets:
            db_adapter.execute_query(
                "INSERT INTO tickets (ticket_code, is_used) VALUES (%s, FALSE) ON CONFLICT (ticket_code) DO NOTHING",
                (ticket_code,)
            )
        
        return jsonify({
            'success': True, 
            'message': f'Generated {len(generated_tickets)} new tickets',
            'count': len(generated_tickets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate tickets'}), 500

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
@require_admin
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

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test basic app functionality
        from .config import Config
        
        health_status = {
            'status': 'healthy',
            'timestamp': Config.get_current_time().isoformat(),
            'database_type': Config.DATABASE_TYPE,
            'environment': 'production'
        }
        
        # Test database connection
        try:
            from .database import db_adapter
            result = db_adapter.execute_query('SELECT 1', fetch_one=True)
            health_status['database'] = 'connected'
        except Exception as db_error:
            health_status['database'] = f'error: {str(db_error)}'
            health_status['status'] = 'unhealthy'
        
        # Test contestants loading
        try:
            from .models import Contestant
            contestants = Contestant.get_all()
            health_status['contestants'] = f'{len(contestants)} loaded'
        except Exception as contestant_error:
            health_status['contestants'] = f'error: {str(contestant_error)}'
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 500
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': 'unknown'
        }), 500
