# 🚀 Railway Deployment Guide

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be on GitHub
3. **Supabase Project**: Your Supabase database should be set up

## Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `idolbinhminhtran/Voting-UAVS`

### 2. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```env
# Database Configuration - Supabase
DATABASE_URL=postgresql://postgres.remlmzjtgswmhaqllutv:tranbinhminh2003@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres

# Supabase Configuration
SUPABASE_URL=https://remlmzjtgswmhaqllutv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJlbWxtemp0Z3N3bWhhcWxsdXR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYxMTgxMzksImV4cCI6MjA3MTY5NDEzOX0.HdPPo9YD7CyuyvUY_au2DlK2lP7N03MAN_TV4uTM0_w
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJlbWxtemp0Z3N3bWhhcWxsdXR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjExODEzOSwiZXhwIjoyMDcxNjk0MTM5fQ.IJFxOepxCwpN0KT8ZqaTeh1r-XPnV6xc2jqHOvafbX0

# Application Configuration
DATABASE_TYPE=postgresql
HOST=0.0.0.0
PORT=5000
TIMEZONE=Asia/Ho_Chi_Minh
VOTING_START_TIME=00:00
VOTING_END_TIME=23:59
RATE_LIMIT_PER_HOUR=10
FLASK_DEBUG=False
```

### 3. Deploy

1. Railway will automatically detect the Python project
2. It will install dependencies from `requirements.txt`
3. It will use the start command from `railway.json`
4. Your app will be deployed to a Railway URL

### 4. Verify Deployment

After deployment, check:

1. **Health Check**: Visit your Railway URL
2. **API Test**: Visit `https://your-app.railway.app/api/contestants`
3. **Frontend**: Visit `https://your-app.railway.app/`

## Configuration Files

### `railway.json`
- Specifies the start command and restart policy

### `Procfile`
- Alternative way to specify the start command

### `start.sh`
- Startup script with logging and configuration

### `requirements.txt`
- Python dependencies including `gunicorn` for production

### `runtime.txt`
- Specifies Python version (3.11)

## Troubleshooting

### Common Issues

1. **"No start command found"**
   - Ensure `railway.json` or `Procfile` exists
   - Check that `start.sh` is executable

2. **Database connection failed**
   - Verify environment variables are set correctly
   - Check Supabase connection string

3. **Port binding issues**
   - Railway uses `$PORT` environment variable
   - Ensure app binds to `0.0.0.0:$PORT`

### Logs

Check Railway logs in the dashboard:
- Build logs: Installation and setup
- Runtime logs: Application execution

## Post-Deployment

1. **Test all endpoints**:
   - `GET /api/contestants`
   - `GET /api/results`
   - `POST /api/vote`
   - `POST /api/ticket/validate`

2. **Monitor performance**:
   - Check Railway metrics
   - Monitor Supabase usage

3. **Set up custom domain** (optional):
   - Go to Railway dashboard → Settings → Domains
   - Add your custom domain

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Supabase PostgreSQL connection | `postgresql://user:pass@host:port/db` |
| `SUPABASE_URL` | Supabase project URL | `https://project.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_SERVICE_KEY` | Supabase service key | `eyJhbGciOiJIUzI1NiIs...` |
| `DATABASE_TYPE` | Database type | `postgresql` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `TIMEZONE` | Application timezone | `Asia/Ho_Chi_Minh` |
| `FLASK_DEBUG` | Debug mode | `False` |

## Support

If you encounter issues:
1. Check Railway logs
2. Verify environment variables
3. Test locally with same configuration
4. Check Supabase dashboard for database issues
