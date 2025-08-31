#!/usr/bin/env python3
"""
Main entry point for the Voting Flask application
Run this file to start the server
"""

import os
from dotenv import load_dotenv
from app import create_app, Config

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from Config class
    host = Config.HOST
    port = Config.PORT
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Voting System Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print(f"⏰ Timezone: {Config.TIMEZONE}")
    print(f"🗳️  Voting hours: {Config.VOTING_START_TIME} - {Config.VOTING_END_TIME}")
    print(f"📊 Rate limit: {Config.RATE_LIMIT_PER_HOUR} votes per hour per IP")
    print(f"💾 Database: {Config.SQLALCHEMY_DATABASE_URI}")
    print("\n" + "="*60)
    print("🎯 API Endpoints:")
    print("   POST /api/vote              - Submit a vote")
    print("   GET  /api/results           - Get voting results")
    print("   GET  /api/contestants       - Get contestants list")
    print("   POST /api/ticket/validate   - Validate ticket code")
    print("="*60)
    print("\n📱 Frontend:")
    print(f"   Main voting page: http://{host}:{port}/")
    print(f"   Admin panel: http://{host}:{port}/admin")
    print("\n" + "="*60)
    
    try:
        # Start the server
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Check your configuration and try again")
