-- Migration 003: Add constraints and triggers
-- This adds data integrity constraints and triggers

-- Note: SQLite doesn't support ADD CONSTRAINT for existing tables
-- These constraints should be added when creating the tables
-- For now, we'll focus on triggers for data integrity

-- Add trigger to prevent voting outside of voting hours
-- Note: This is a simplified version. The main time checking is done in the application layer
CREATE TRIGGER IF NOT EXISTS check_voting_time
BEFORE INSERT ON votes
BEGIN
    SELECT CASE 
        WHEN strftime('%H:%M', 'now') < '09:00' OR strftime('%H:%M', 'now') > '17:00'
        THEN RAISE(ABORT, 'Voting is only allowed between 9:00 AM and 5:00 PM')
    END;
END;

-- Add trigger to update contestant vote count cache (if needed)
CREATE TRIGGER IF NOT EXISTS update_vote_count_after_insert
AFTER INSERT ON votes
BEGIN
    -- This could be used to maintain a vote count cache if needed
    -- For now, we'll just log the action
    SELECT 'Vote inserted: ' || NEW.id;
END;

-- Add unique constraint to prevent duplicate votes from same ticket
-- This is already handled by the UNIQUE constraint on ticket_id in votes table
-- But we can add an additional check

-- Add trigger to ensure ticket is marked as used when vote is created
CREATE TRIGGER IF NOT EXISTS mark_ticket_used_on_vote
AFTER INSERT ON votes
BEGIN
    UPDATE tickets SET is_used = 1, used_at = datetime('now') 
    WHERE id = NEW.ticket_id;
END;

-- Add trigger to prevent voting with already used tickets
CREATE TRIGGER IF NOT EXISTS prevent_used_ticket_vote
BEFORE INSERT ON votes
BEGIN
    SELECT CASE 
        WHEN (SELECT is_used FROM tickets WHERE id = NEW.ticket_id) = 1
        THEN RAISE(ABORT, 'Ticket already used')
    END;
END;

-- Add trigger to prevent multiple votes from same IP in short time (rate limiting)
CREATE TRIGGER IF NOT EXISTS check_rate_limit
BEFORE INSERT ON votes
BEGIN
    SELECT CASE 
        WHEN (SELECT COUNT(*) FROM votes 
              WHERE ip_address = NEW.ip_address 
              AND created_at > datetime('now', '-1 hour')) >= 10
        THEN RAISE(ABORT, 'Rate limit exceeded: too many votes from this IP')
    END;
END;
