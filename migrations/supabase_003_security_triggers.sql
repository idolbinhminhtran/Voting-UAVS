-- Supabase Migration 003: Security policies and triggers
-- This adds Row Level Security and audit triggers

-- Enable Row Level Security on all tables
ALTER TABLE contestants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;

-- Create policies for contestants (read-only for public)
CREATE POLICY "Contestants are viewable by everyone"
ON contestants FOR SELECT
USING (is_active = TRUE);

-- Create policies for tickets (only for validation, no direct access)
CREATE POLICY "Tickets can only be validated via function"
ON tickets FOR SELECT
USING (FALSE); -- Block direct access, use functions instead

-- Create policies for votes (read-only for results)
CREATE POLICY "Votes are viewable for results"
ON votes FOR SELECT
USING (TRUE);

-- Prevent direct INSERT/UPDATE/DELETE on votes table
CREATE POLICY "Votes can only be inserted via function"
ON votes FOR INSERT
WITH CHECK (FALSE); -- Block direct insert, use submit_vote function

-- Create audit log table for tracking important events
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on audit log
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Create policy for audit log (admin only)
CREATE POLICY "Audit log is admin only"
ON audit_log FOR ALL
USING (FALSE); -- Only accessible via functions/admin role

-- Create trigger function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (event_type, table_name, record_id, new_values)
        VALUES (TG_OP, TG_TABLE_NAME, NEW.id, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (event_type, table_name, record_id, old_values, new_values)
        VALUES (TG_OP, TG_TABLE_NAME, NEW.id, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (event_type, table_name, record_id, old_values)
        VALUES (TG_OP, TG_TABLE_NAME, OLD.id, row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

-- Create audit triggers
CREATE TRIGGER audit_contestants_trigger
    AFTER INSERT OR UPDATE OR DELETE ON contestants
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_tickets_trigger
    AFTER INSERT OR UPDATE OR DELETE ON tickets
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_votes_trigger
    AFTER INSERT OR UPDATE OR DELETE ON votes
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Function to prevent voting outside business hours (if needed)
CREATE OR REPLACE FUNCTION check_voting_hours()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- This is a placeholder - adjust based on your business rules
    -- Currently allows 24/7 voting as per your config
    RETURN NEW;
END;
$$;

-- Function to enforce rate limiting at database level
CREATE OR REPLACE FUNCTION check_rate_limit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    vote_count INTEGER;
BEGIN
    -- Check votes from same IP in last hour
    SELECT COUNT(*) INTO vote_count
    FROM votes 
    WHERE ip_address = NEW.ip_address 
    AND created_at > NOW() - INTERVAL '1 hour';
    
    IF vote_count >= 10 THEN
        RAISE EXCEPTION 'Rate limit exceeded: too many votes from this IP address';
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create rate limiting trigger
CREATE TRIGGER rate_limit_trigger
    BEFORE INSERT ON votes
    FOR EACH ROW EXECUTE FUNCTION check_rate_limit();

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type);
