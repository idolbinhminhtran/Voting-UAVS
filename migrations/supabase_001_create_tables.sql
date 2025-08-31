-- Supabase Migration 001: Create main tables for PostgreSQL
-- Run this to set up the initial database structure in Supabase

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create contestants table
CREATE TABLE IF NOT EXISTS contestants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL CHECK (LENGTH(name) >= 2 AND LENGTH(name) <= 100),
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_code VARCHAR(20) UNIQUE NOT NULL CHECK (LENGTH(ticket_code) >= 6 AND LENGTH(ticket_code) <= 20),
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE NULL
);

-- Create votes table
CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    contestant_id INTEGER NOT NULL,
    ticket_id INTEGER NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (contestant_id) REFERENCES contestants(id) ON DELETE CASCADE,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tickets_code ON tickets(ticket_code);
CREATE INDEX IF NOT EXISTS idx_tickets_used ON tickets(is_used);
CREATE INDEX IF NOT EXISTS idx_votes_contestant ON votes(contestant_id);
CREATE INDEX IF NOT EXISTS idx_votes_ticket ON votes(ticket_id);
CREATE INDEX IF NOT EXISTS idx_votes_created ON votes(created_at);
CREATE INDEX IF NOT EXISTS idx_votes_ip_created ON votes(ip_address, created_at);

-- Insert sample contestants
INSERT INTO contestants (name, description, image_url) VALUES
('Anne and Quang', 'Dynamic duo with exceptional talent', '/images/default-avatar.svg'),
('HORIZON', 'Innovative musical group pushing boundaries', '/images/default-avatar.svg'),
('Truong Ho Quan Minh', 'Solo artist with unique style', '/images/default-avatar.svg'),
('BlackB', 'Contemporary music collective', '/images/default-avatar.svg'),
('Ban Nhac Anh Em', 'Brotherhood band with harmonious sound', '/images/default-avatar.svg'),
('Nguyen Tan Phuc', 'Versatile performer with wide range', '/images/default-avatar.svg'),
('Anne Vu', 'Solo artist with powerful vocals', '/images/default-avatar.svg'),
('Nguyen Ngoc Minh Anh', 'Emerging talent with fresh perspective', '/images/default-avatar.svg'),
('Son Truong Nguyen', 'Experienced performer with stage presence', '/images/default-avatar.svg'),
('Tran Nguyen Tony', 'Dynamic performer with international appeal', '/images/default-avatar.svg')
ON CONFLICT (name) DO NOTHING;
