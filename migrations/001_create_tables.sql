-- Migration 001: Create main tables
-- Run this to set up the initial database structure

-- Create contestants table
CREATE TABLE IF NOT EXISTS contestants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_code VARCHAR(20) UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL
);

-- Create votes table
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contestant_id INTEGER NOT NULL,
    ticket_id INTEGER NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contestant_id) REFERENCES contestants(id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tickets_code ON tickets(ticket_code);
CREATE INDEX IF NOT EXISTS idx_tickets_used ON tickets(is_used);
CREATE INDEX IF NOT EXISTS idx_votes_contestant ON votes(contestant_id);
CREATE INDEX IF NOT EXISTS idx_votes_ticket ON votes(ticket_id);
CREATE INDEX IF NOT EXISTS idx_votes_created ON votes(created_at);

-- Insert some sample contestants
INSERT OR IGNORE INTO contestants (name, description, image_url) VALUES
('Contestant 1', 'First contestant description', '/images/contestant1.jpg'),
('Contestant 2', 'Second contestant description', '/images/contestant2.jpg'),
('Contestant 3', 'Third contestant description', '/images/contestant3.jpg');
