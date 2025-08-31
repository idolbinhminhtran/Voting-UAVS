# 🚀 Migration to Supabase Guide

Hướng dẫn chuyển project "The Gala Final Voting" từ SQLite sang Supabase (PostgreSQL).

## 📋 Yêu cầu

- Python 3.7+
- Tài khoản Supabase
- PostgreSQL client (psycopg2)

## 🔧 Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

## 🗃️ Thiết lập Supabase

### 1. Tạo Project trên Supabase

1. Truy cập [supabase.com](https://supabase.com)
2. Tạo tài khoản và project mới
3. Ghi lại thông tin:
   - Project URL
   - API Keys (anon key, service role key)
   - Database password

### 2. Cấu hình Environment Variables

Tạo file `.env` từ `env.example`:

```bash
cp env.example .env
```

Cập nhật các thông tin Supabase trong `.env`:

```env
# Database URL cho Supabase
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://[PROJECT-ID].supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

## 🚀 Migration Process

### 1. Chạy Deployment Script

```bash
python scripts/deploy_supabase.py
```

Script này sẽ:
- ✅ Tạo tất cả tables (contestants, tickets, votes, audit_log)
- ✅ Tạo views (voting_results, ticket_stats)
- ✅ Tạo functions (submit_vote, validate_ticket_code, get_voting_stats)
- ✅ Thiết lập Row Level Security (RLS)
- ✅ Tạo audit triggers

### 2. Tạo Tickets

```bash
python scripts/generate_tickets_supabase.py --count 100
```

Tùy chọn:
- `--count N`: Tạo N tickets (mặc định: 100)
- `--force`: Bắt buộc tạo kể cả khi đã có tickets

### 3. Kiểm tra Migration

```bash
python scripts/show_status.py
```

## 🏗️ Database Schema (PostgreSQL)

### Tables

```sql
-- Contestants table
CREATE TABLE contestants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tickets table
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    ticket_code VARCHAR(20) UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE NULL
);

-- Votes table
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    contestant_id INTEGER NOT NULL,
    ticket_id INTEGER NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (contestant_id) REFERENCES contestants(id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);
```

### Views

```sql
-- Voting results with percentages
CREATE VIEW voting_results AS
SELECT 
    c.id, c.name, c.description, c.image_url,
    COUNT(v.id) as vote_count,
    ROUND(COUNT(v.id)::DECIMAL / (SELECT COUNT(*) FROM votes) * 100, 2) as percentage
FROM contestants c
LEFT JOIN votes v ON c.id = v.contestant_id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.description, c.image_url
ORDER BY vote_count DESC;

-- Ticket statistics
CREATE VIEW ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    COUNT(CASE WHEN is_used = TRUE THEN 1 END) as used_tickets,
    COUNT(CASE WHEN is_used = FALSE THEN 1 END) as unused_tickets,
    ROUND(COUNT(CASE WHEN is_used = TRUE THEN 1 END)::DECIMAL / COUNT(*) * 100, 2) as usage_percentage
FROM tickets;
```

### Functions

#### Submit Vote Function
```sql
SELECT * FROM submit_vote(
    'TICKET123',  -- ticket_code
    1,            -- contestant_id
    '127.0.0.1',  -- ip_address
    'Mozilla/5.0' -- user_agent
);
```

#### Validate Ticket Function
```sql
SELECT * FROM validate_ticket_code('TICKET123');
```

## 🔒 Security Features

### Row Level Security (RLS)

- **Contestants**: Public read access for active contestants
- **Tickets**: No direct access, only via functions
- **Votes**: Read-only access for results
- **Audit Log**: Admin only access

### Rate Limiting

Database-level rate limiting: Maximum 10 votes per IP per hour

### Audit Logging

Tất cả thay đổi được ghi lại trong `audit_log` table.

## 🔄 API Compatibility

Application code được thiết kế để tương thích với cả SQLite và PostgreSQL:

```python
# Tự động detect database type
if Config.DATABASE_TYPE == 'postgresql':
    # Use PostgreSQL-specific features
    result = db_adapter.execute_function('submit_vote', params)
else:
    # Use SQLite fallback
    # ... original SQLite logic
```

## 🧪 Testing

### 1. Test Database Connection

```bash
python -c "from app.database import db_adapter; print('✅ Database connected!')"
```

### 2. Test Ticket Validation

```bash
curl -X POST http://localhost:5004/api/ticket/validate \
  -H "Content-Type: application/json" \
  -d '{"ticket_code":"YOUR_TICKET_CODE"}'
```

### 3. Test Vote Submission

```bash
curl -X POST http://localhost:5004/api/vote \
  -H "Content-Type: application/json" \
  -d '{"ticket_code":"YOUR_TICKET_CODE","contestant_id":1}'
```

## 📊 Monitoring

### Supabase Dashboard

- Database usage
- Real-time subscriptions
- API logs
- Performance metrics

### Application Logs

```bash
# View application logs
tail -f app.log
```

## 🔧 Troubleshooting

### Common Issues

1. **Connection Error**
   ```
   FATAL: password authentication failed
   ```
   ➡️ Kiểm tra lại database password trong DATABASE_URL

2. **Permission Denied**
   ```
   permission denied for table
   ```
   ➡️ Kiểm tra RLS policies trong Supabase dashboard

3. **Function Not Found**
   ```
   function submit_vote() does not exist
   ```
   ➡️ Chạy lại deployment script

### Backup & Recovery

```bash
# Backup database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql
```

## 🎯 Performance Tips

1. **Indexes**: Đã tự động tạo indexes cho performance tối ưu
2. **Connection Pooling**: Supabase tự động quản lý connection pool
3. **Edge Functions**: Có thể sử dụng Supabase Edge Functions cho logic phức tạp

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## 🆘 Support

Nếu gặp vấn đề, hãy:
1. Kiểm tra logs trong Supabase dashboard
2. Xem lại cấu hình environment variables
3. Đảm bảo đã chạy đúng migration scripts
