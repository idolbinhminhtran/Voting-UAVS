# 🏆 TOP 10 FINALISTS - Voting System

A modern, secure voting system built with Flask for the TOP 10 FINALISTS competition. Users can vote for their favorite contestants using unique ticket codes. Features include time-based voting restrictions, rate limiting, and a beautiful responsive frontend.

## ✨ Features

- **Secure Voting**: Unique ticket codes prevent duplicate votes
- **Time Restrictions**: Configurable voting hours (default: 9 AM - 5 PM)
- **Rate Limiting**: Prevents abuse with configurable limits per IP
- **Real-time Results**: Live voting results with percentages
- **Admin Panel**: Manage contestants, view statistics, and monitor system
- **Responsive Design**: Modern UI that works on all devices
- **Database Views**: Optimized queries for results and statistics
- **Ticket Generation**: Script to generate 400+ unique ticket codes

## 🏗️ Architecture

```
voting-flask/
├── app/                    # Flask application package
│   ├── __init__.py        # App factory and configuration
│   ├── config.py          # Environment-based configuration
│   ├── database.py        # Database adapter (Supabase/PostgreSQL)
│   ├── models.py          # Data models
│   ├── routes.py          # API endpoints
│   ├── services.py        # Business logic layer
│   └── utils.py           # Utility functions
├── migrations/             # Supabase database migrations
│   ├── supabase_001_create_tables.sql
│   ├── supabase_002_views_functions.sql
│   └── supabase_003_security_triggers.sql
├── frontend/              # Static frontend files
├── scripts/               # Utility scripts
│   ├── deploy_supabase.py      # Database deployment
│   ├── generate_tickets_supabase.py  # Ticket generation
│   ├── test_database.py        # Connection testing
│   ├── show_status.py         # System status
│   └── add_contestants.py     # Contestant management
└── run.py                 # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (Python 3.11 or 3.12 recommended)
- pip (Python package manager)
- Supabase account and project

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voting-flask
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Supabase**
   ```bash
   # Create .env file with your Supabase credentials
   cp env.example .env
   # Edit .env with your Supabase configuration
   ```

5. **Deploy database schema**
   ```bash
   python scripts/deploy_supabase.py
   ```

6. **Generate ticket codes**
   ```bash
   python scripts/generate_tickets_supabase.py --count 100
   ```

7. **Start the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5004`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///voting.db

# Timezone and Voting Hours
TIMEZONE=Asia/Ho_Chi_Minh
VOTING_START_TIME=09:00
VOTING_END_TIME=17:00

# Security
SECRET_KEY=your-secret-key-here
RATE_LIMIT_PER_HOUR=10

# Server
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=True
```

### Database Options

- **SQLite** (default): `sqlite:///voting.db`
- **PostgreSQL**: `postgresql://user:pass@localhost/dbname`
- **MySQL**: `mysql://user:pass@localhost/dbname`

## 📱 Frontend

### Main Voting Page (`/`)
- Ticket validation
- Contestant selection
- Real-time results display
- Voting status indicator

### Admin Panel (`/admin`)
- Dashboard with statistics
- Contestant management
- Results monitoring
- Ticket management
- System administration

## 🔌 API Endpoints

### Authentication
No authentication required for public endpoints.

### Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/api/vote` | Submit a vote | `{"ticket_code": "ABC123", "contestant_id": 1}` |
| `GET` | `/api/results` | Get voting results | - |
| `GET` | `/api/contestants` | Get contestants list | - |
| `POST` | `/api/ticket/validate` | Validate ticket code | `{"ticket_code": "ABC123"}` |

### Response Examples

**Vote Submission**
```json
{
  "message": "Vote submitted successfully",
  "contestant_name": "John Doe"
}
```

**Results**
```json
{
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "vote_count": 25,
      "percentage": 50.0
    }
  ],
  "total_votes": 50,
  "voting_open": true,
  "current_time": "2024-01-15T14:30:00+07:00"
}
```

## 🗄️ Database Schema

### Tables

- **`contestants`**: Contestant information
- **`tickets`**: Unique voting tickets
- **`votes`**: Individual votes cast
- **`sqlite_log`**: System audit log

### Views

- **`voting_results`**: Optimized results query
- **`ticket_stats`**: Ticket statistics
- **`daily_voting_activity`**: Daily voting patterns

## 🛠️ Development

### Project Structure

```
app/
├── __init__.py      # Flask app factory
├── config.py        # Configuration management
├── models.py        # Database models
├── routes.py        # API routes
├── services.py      # Business logic
└── utils.py         # Utility functions
```

### Adding New Features

1. **Models**: Add to `app/models.py`
2. **Routes**: Add to `app/routes.py`
3. **Services**: Add business logic to `app/services.py`
4. **Frontend**: Update HTML/CSS/JS in `frontend/`

### Testing

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

## 📊 Scripts

### Generate Tickets

Generate 400 unique ticket codes:

```bash
python scripts/generate_tickets.py [output_file.csv]
```

### Database Migrations

Run migrations manually if needed:

```bash
sqlite3 voting.db < migrations/001_create_tables.sql
sqlite3 voting.db < migrations/002_results_view.sql
sqlite3 voting.db < migrations/003_constraints.sql
```

## 🚀 Deployment

### Production Setup

1. **Set production environment**
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=<strong-random-key>
   ```

2. **Use Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. **Set up reverse proxy** (Nginx/Apache)

4. **Database**: Use PostgreSQL/MySQL for production

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## 🔒 Security Features

- **Rate Limiting**: Configurable per-IP limits
- **Input Validation**: Sanitized user inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: Input sanitization
- **Time-based Restrictions**: Voting hours enforcement
- **Unique Tickets**: One-time use voting codes

## 📈 Monitoring

### Logs
- Application logs in console
- Database audit logs
- Error tracking and reporting

### Metrics
- Total votes cast
- Ticket usage statistics
- Contestant performance
- System health status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the documentation
- Review existing issues
- Create a new issue with details

## 🔧 Troubleshooting

### Python 3.13 Compatibility Issues

If you encounter errors like:
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly but has additional attributes
```

**Solutions:**

1. **Use the fix script:**
   ```bash
   python fix_python313.py
   ```

2. **Use Python 3.11 or 3.12:**
   ```bash
   conda create -n voting python=3.11
   conda activate voting
   pip install -r requirements.txt
   ```

3. **Use the latest compatible requirements:**
   ```bash
   pip install -r requirements-latest.txt
   ```

### Common Issues

- **Import errors**: Make sure you're in the correct directory and virtual environment is activated
- **Database errors**: Check that the database file is writable and migrations are run
- **Port conflicts**: Change the PORT in .env file if 5000 is already in use

## 🔮 Roadmap

- [ ] Real-time WebSocket updates
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced security features

---

**Happy Voting! 🎉**
