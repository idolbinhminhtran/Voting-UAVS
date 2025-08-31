from flask import Flask, send_from_directory
from flask_cors import CORS
from .config import Config
import sqlite3
import os
from pathlib import Path

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('voting.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    
    # Create tables
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS contestants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_code TEXT UNIQUE NOT NULL,
            is_used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contestant_id INTEGER NOT NULL,
            ticket_id INTEGER NOT NULL UNIQUE,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contestant_id) REFERENCES contestants (id),
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_tickets_code ON tickets(ticket_code);
        CREATE INDEX IF NOT EXISTS idx_tickets_used ON tickets(is_used);
        CREATE INDEX IF NOT EXISTS idx_votes_contestant ON votes(contestant_id);
        CREATE INDEX IF NOT EXISTS idx_votes_ticket ON votes(ticket_id);
        CREATE INDEX IF NOT EXISTS idx_votes_created ON votes(created_at);
    ''')
    
    # Insert sample contestants if none exist
    cursor = conn.execute('SELECT COUNT(*) FROM contestants')
    if cursor.fetchone()[0] == 0:
        # Use a simple SVG data URI for the default avatar
        default_avatar = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iMzUiIHI9IjE1IiBmaWxsPSIjOUI5QkEwIi8+CjxyZWN0IHg9IjMwIiB5PSI1NSIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjOUI5QkEwIi8+Cjwvc3ZnPgo='
        conn.executescript(f'''
            INSERT INTO contestants (name, description, image_url) VALUES
            ('Contestant 1', 'First contestant description', '{default_avatar}'),
            ('Contestant 2', 'Second contestant description', '{default_avatar}'),
            ('Contestant 3', 'Third contestant description', '{default_avatar}');
        ''')
    
    conn.commit()
    conn.close()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Get the absolute path to the frontend directory
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    frontend_dir = frontend_dir.resolve()
    
    # Initialize extensions
    CORS(app)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Frontend routes (define these first)
    @app.route('/')
    def index():
        print(f"Frontend route / accessed, serving from {frontend_dir}")  # Debug print
        return send_from_directory(str(frontend_dir), 'index.html')
    
    @app.route('/admin')
    def admin():
        print(f"Frontend route /admin accessed, serving from {frontend_dir}")  # Debug print
        return send_from_directory(str(frontend_dir), 'admin.html')
    
    @app.route('/styles.css')
    def styles():
        return send_from_directory(str(frontend_dir), 'styles.css')
    
    @app.route('/script.js')
    def script():
        return send_from_directory(str(frontend_dir), 'script.js')
    
    @app.route('/<path:filename>')
    def frontend_files(filename):
        print(f"Frontend file requested: {filename} from {frontend_dir}")  # Debug print
        # Handle the default-avatar.png request by serving the SVG file
        if filename == 'images/default-avatar.png':
            return send_from_directory(str(frontend_dir), 'images/default-avatar.svg', mimetype='image/svg+xml')
        return send_from_directory(str(frontend_dir), filename)
    
    # Import and register API blueprints (after frontend routes)
    from .routes import api_bp
    app.register_blueprint(api_bp)
    
    print("✅ Flask app created with routes:")
    print("   - / (frontend)")
    print("   - /admin (frontend)")
    print("   - /api/* (API endpoints)")
    print(f"   - Frontend directory: {frontend_dir}")
    
    return app
