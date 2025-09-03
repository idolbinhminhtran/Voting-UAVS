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
@api_bp.route('/admin/voting-status', methods=['GET'])
@require_admin
def get_voting_status():
    """Get current voting open/closed status"""
    try:
        from .database import db_adapter
        row = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
        return jsonify({'voting_open': bool(row['open']) if row and 'open' in row else True}), 200
    except Exception:
        return jsonify({'voting_open': True}), 200

@api_bp.route('/admin/voting-open', methods=['POST'])
@require_admin
def open_voting():
    """Open voting (set flag true)"""
    try:
        from .database import db_adapter
        db_adapter.execute_query("SELECT set_voting_open(TRUE)")
        return jsonify({'success': True, 'message': 'Voting opened'}), 200
    except Exception:
        return jsonify({'error': 'Failed to open voting'}), 500

@api_bp.route('/admin/voting-close', methods=['POST'])
@require_admin
def close_voting():
    """Close voting (set flag false)"""
    try:
        from .database import db_adapter
        db_adapter.execute_query("SELECT set_voting_open(FALSE)")
        return jsonify({'success': True, 'message': 'Voting closed'}), 200
    except Exception:
        return jsonify({'error': 'Failed to close voting'}), 500

@api_bp.route('/admin/status', methods=['GET'])
def admin_status():
    """Check admin authentication status"""
    try:
        from .database import db_adapter
        row = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
        voting_open = bool(row['open']) if row and 'open' in row else True
    except Exception:
        voting_open = True
    return jsonify({
        'authenticated': session.get('admin_authenticated', False),
        'username': session.get('admin_username', None),
        'voting_open': voting_open
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

@api_bp.route('/admin/sync-predefined-tickets', methods=['POST'])
@require_admin
def sync_predefined_tickets():
    """Sync pre-defined tickets to database"""
    try:
        from .predefined_tickets import get_predefined_tickets
        from .database import db_adapter
        
        predefined_tickets = get_predefined_tickets()
        synced_count = 0
        
        # Insert pre-defined tickets into database if they don't exist
        for ticket_code in predefined_tickets:
            result = db_adapter.execute_query(
                "INSERT INTO tickets (ticket_code, is_used, created_at) VALUES (%s, FALSE, NOW()) ON CONFLICT (ticket_code) DO NOTHING RETURNING ticket_code",
                (ticket_code,),
                fetch_one=True
            )
            if result:
                synced_count += 1
        
        return jsonify({
            'success': True, 
            'message': f'Synced {synced_count} pre-defined tickets to database',
            'total_predefined': len(predefined_tickets),
            'newly_synced': synced_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to sync pre-defined tickets'}), 500

# Removed seating system endpoints - tickets are now based on pre-defined seat codes

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
        # Check global voting flag
        try:
            from .database import db_adapter
            row = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
            voting_open = bool(row['open']) if row and 'open' in row else True
        except Exception:
            voting_open = True
        if not voting_open:
            return jsonify({'error': 'Voting is currently closed'}), 403
        
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
        
        # Read voting_open from DB settings
        from .database import db_adapter
        voting_open = True
        try:
            row = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
            if row and 'open' in row:
                voting_open = bool(row['open'])
        except Exception:
            voting_open = True
        
        return jsonify({
            'results': results,
            'total_votes': total_votes,
            'voting_open': voting_open,
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
        
        # Also include open flag for settings
        from .database import db_adapter
        try:
            row = db_adapter.execute_query("SELECT get_voting_open() AS open", fetch_one=True)
            voting_open = bool(row['open']) if row and 'open' in row else True
        except Exception:
            voting_open = True
        return jsonify({
            'total_tickets': stats['total_tickets'],
            'used_tickets': stats['used_tickets'],
            'unused_tickets': stats['unused_tickets'],
            'usage_percentage': round((stats['used_tickets'] / stats['total_tickets'] * 100), 2) if stats['total_tickets'] > 0 else 0,
            'voting_open': voting_open
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
