from flask import Flask, send_from_directory
from flask_cors import CORS
from .config import Config
from pathlib import Path

def init_db():
    """Initialize database - Supabase tables are created via migration scripts"""
    # Database initialization is handled by Supabase migration scripts
    # No local SQLite initialization needed
    pass

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Get the absolute path to the frontend directory
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    frontend_dir = frontend_dir.resolve()
    
    # Initialize extensions
    CORS(app)
    
    # Database is initialized via Supabase migration scripts
    # No local initialization needed
    
    # Frontend routes (define these first)
    @app.route('/')
    def index():
        print(f"Frontend route / accessed, serving from {frontend_dir}")  # Debug print
        return send_from_directory(str(frontend_dir), 'index.html')
    
    @app.route('/admin')
    def admin():
        print(f"Frontend route /admin accessed, serving from {frontend_dir}")  # Debug print
        return send_from_directory(str(frontend_dir), 'admin.html')
    
    @app.route('/admin-login')
    def admin_login_page():
        print(f"Frontend route /admin-login accessed, serving from {frontend_dir}")  # Debug print
        return send_from_directory(str(frontend_dir), 'admin-login.html')
    
    @app.route('/voting')
    def voting_page():
        print(f"Frontend route /voting accessed, serving from {frontend_dir}")  # Debug print
        return send_from_directory(str(frontend_dir), 'voting.html')
    
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
