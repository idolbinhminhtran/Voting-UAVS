-- Migration 002: Create results view
-- This view makes it easier to query voting results

CREATE VIEW IF NOT EXISTS voting_results AS
SELECT 
    c.id as contestant_id,
    c.name as contestant_name,
    c.description,
    c.image_url,
    COUNT(v.id) as vote_count,
    c.is_active,
    c.created_at as contestant_created
FROM contestants c
LEFT JOIN votes v ON c.id = v.contestant_id
WHERE c.is_active = 1
GROUP BY c.id, c.name, c.description, c.image_url, c.is_active, c.created_at
ORDER BY vote_count DESC;

-- Create a view for ticket statistics
CREATE VIEW IF NOT EXISTS ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    SUM(CASE WHEN is_used = 1 THEN 1 ELSE 0 END) as used_tickets,
    SUM(CASE WHEN is_used = 0 THEN 1 ELSE 0 END) as unused_tickets,
    MIN(created_at) as first_ticket_created,
    MAX(created_at) as last_ticket_created
FROM tickets;

-- Create a view for daily voting activity
CREATE VIEW IF NOT EXISTS daily_voting_activity AS
SELECT 
    DATE(created_at) as vote_date,
    COUNT(*) as votes_cast,
    COUNT(DISTINCT contestant_id) as contestants_voted_for
FROM votes
GROUP BY DATE(created_at)
ORDER BY vote_date DESC;
