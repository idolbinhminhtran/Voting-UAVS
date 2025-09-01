#!/bin/bash
echo "🚀 Starting Voting System on Railway..."
echo "📍 Port: $PORT"
echo "🔧 Environment: $RAILWAY_ENVIRONMENT"
echo "💾 Database URL: ${DATABASE_URL:0:30}..."
echo "🌐 Supabase URL: $SUPABASE_URL"

# Test if environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set!"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL not set!"
    exit 1
fi

echo "✅ Environment variables are set"

# Start the Flask application with Gunicorn
echo "🔄 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level debug run:app
