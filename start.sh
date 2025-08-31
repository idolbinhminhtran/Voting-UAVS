#!/bin/bash
echo "🚀 Starting Voting System on Railway..."
echo "📍 Port: $PORT"
echo "🔧 Environment: $RAILWAY_ENVIRONMENT"

# Start the Flask application with Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:app
