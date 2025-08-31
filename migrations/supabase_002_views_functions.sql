-- Supabase Migration 002: Create views and functions
-- This creates useful views and functions for the voting system

-- Create voting results view
CREATE OR REPLACE VIEW voting_results AS
SELECT 
    c.id,
    c.name,
    c.description,
    c.image_url,
    COUNT(v.id) as vote_count,
    ROUND(
        CASE 
            WHEN (SELECT COUNT(*) FROM votes) > 0 
            THEN (COUNT(v.id)::DECIMAL / (SELECT COUNT(*) FROM votes) * 100)
            ELSE 0 
        END, 2
    ) as percentage
FROM contestants c
LEFT JOIN votes v ON c.id = v.contestant_id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.description, c.image_url
ORDER BY vote_count DESC;

-- Create ticket statistics view
CREATE OR REPLACE VIEW ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    COUNT(CASE WHEN is_used = TRUE THEN 1 END) as used_tickets,
    COUNT(CASE WHEN is_used = FALSE THEN 1 END) as unused_tickets,
    ROUND(
        CASE 
            WHEN COUNT(*) > 0 
            THEN (COUNT(CASE WHEN is_used = TRUE THEN 1 END)::DECIMAL / COUNT(*) * 100)
            ELSE 0 
        END, 2
    ) as usage_percentage
FROM tickets;

-- Function to validate ticket
CREATE OR REPLACE FUNCTION validate_ticket_code(ticket_code_param VARCHAR)
RETURNS TABLE(
    is_valid BOOLEAN,
    message TEXT,
    ticket_id INTEGER
) 
LANGUAGE plpgsql
AS $$
DECLARE
    ticket_record RECORD;
BEGIN
    SELECT * INTO ticket_record FROM tickets WHERE ticket_code = ticket_code_param;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Invalid ticket code'::TEXT, NULL::INTEGER;
    ELSIF ticket_record.is_used THEN
        RETURN QUERY SELECT FALSE, 'Ticket already used'::TEXT, ticket_record.id;
    ELSE
        RETURN QUERY SELECT TRUE, 'Ticket is valid'::TEXT, ticket_record.id;
    END IF;
END;
$$;

-- Function to submit vote with transaction safety
CREATE OR REPLACE FUNCTION submit_vote(
    ticket_code_param VARCHAR,
    contestant_id_param INTEGER,
    ip_address_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    contestant_name VARCHAR,
    vote_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    ticket_record RECORD;
    contestant_record RECORD;
    new_vote_id INTEGER;
BEGIN
    -- Validate ticket
    SELECT * INTO ticket_record FROM tickets WHERE ticket_code = ticket_code_param;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Invalid ticket code'::TEXT, NULL::VARCHAR, NULL::INTEGER;
        RETURN;
    END IF;
    
    IF ticket_record.is_used THEN
        RETURN QUERY SELECT FALSE, 'Ticket already used'::TEXT, NULL::VARCHAR, NULL::INTEGER;
        RETURN;
    END IF;
    
    -- Validate contestant
    SELECT * INTO contestant_record FROM contestants WHERE id = contestant_id_param AND is_active = TRUE;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Invalid contestant'::TEXT, NULL::VARCHAR, NULL::INTEGER;
        RETURN;
    END IF;
    
    -- Create vote and mark ticket as used in a transaction
    BEGIN
        -- Insert vote
        INSERT INTO votes (contestant_id, ticket_id, ip_address, user_agent)
        VALUES (contestant_id_param, ticket_record.id, ip_address_param, user_agent_param)
        RETURNING id INTO new_vote_id;
        
        -- Mark ticket as used
        UPDATE tickets 
        SET is_used = TRUE, used_at = NOW() 
        WHERE id = ticket_record.id;
        
        RETURN QUERY SELECT TRUE, 'Vote submitted successfully'::TEXT, contestant_record.name, new_vote_id;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT FALSE, 'Failed to submit vote'::TEXT, NULL::VARCHAR, NULL::INTEGER;
    END;
END;
$$;

-- Function to get voting statistics
CREATE OR REPLACE FUNCTION get_voting_stats()
RETURNS TABLE(
    total_votes BIGINT,
    total_tickets BIGINT,
    used_tickets BIGINT,
    unused_tickets BIGINT,
    usage_percentage NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM votes) as total_votes,
        ts.total_tickets,
        ts.used_tickets,
        ts.unused_tickets,
        ts.usage_percentage
    FROM ticket_stats ts;
END;
$$;
