-- Seating System Migration for UGT 25
-- Tạo hệ thống vé theo ghế ngồi

-- Create seating sections table
CREATE TABLE IF NOT EXISTS seating_sections (
    id SERIAL PRIMARY KEY,
    section_code VARCHAR(10) NOT NULL UNIQUE, -- A1, A2, C1, C2, C3, BGK
    section_name VARCHAR(50) NOT NULL,
    section_type VARCHAR(20) NOT NULL, -- 'VIP', 'REGULAR', 'SPECIAL'
    max_capacity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10,2) DEFAULT 0.00,
    color_code VARCHAR(7) DEFAULT '#667eea', -- Màu hiển thị trên seating chart
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create individual seats table
CREATE TABLE IF NOT EXISTS seats (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL,
    seat_row VARCHAR(5) NOT NULL, -- R2, R3, R4, R5, R6
    seat_number INTEGER NOT NULL, -- 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    seat_code VARCHAR(10) NOT NULL UNIQUE, -- A1-R2-1, A2-R3-5, etc.
    is_available BOOLEAN DEFAULT TRUE,
    is_reserved BOOLEAN DEFAULT FALSE,
    reserved_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (section_id) REFERENCES seating_sections(id) ON DELETE CASCADE
);

-- Update tickets table to include seat information
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS seat_id INTEGER REFERENCES seats(id) ON DELETE SET NULL;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS seat_code VARCHAR(10);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS section_code VARCHAR(10);

-- Create seating chart layout table for positioning
CREATE TABLE IF NOT EXISTS seating_layout (
    id SERIAL PRIMARY KEY,
    section_code VARCHAR(10) NOT NULL,
    seat_row VARCHAR(5) NOT NULL,
    seat_number INTEGER NOT NULL,
    position_x INTEGER NOT NULL, -- X coordinate for visual positioning
    position_y INTEGER NOT NULL, -- Y coordinate for visual positioning
    FOREIGN KEY (section_code) REFERENCES seating_sections(section_code) ON DELETE CASCADE,
    UNIQUE(section_code, seat_row, seat_number)
);

-- Insert seating sections based on the UGT 25 layout
INSERT INTO seating_sections (section_code, section_name, section_type, max_capacity, price, color_code) VALUES
('A1', 'Khu vực A1 - Khách mời ngoại giao', 'VIP', 45, 0.00, '#FFD700'),
('A2', 'Khu vực A2 - Hội sinh viên', 'REGULAR', 70, 0.00, '#87CEEB'),
('BGK', 'Ban Giám Khảo', 'SPECIAL', 10, 0.00, '#FF6B6B'),
('C1', 'Khu vực C1', 'REGULAR', 60, 0.00, '#98FB98'),
('C2', 'Khu vực C2', 'REGULAR', 64, 0.00, '#DDA0DD'),
('C3', 'Khu vực C3', 'REGULAR', 40, 0.00, '#F0E68C')
ON CONFLICT (section_code) DO UPDATE SET
    section_name = EXCLUDED.section_name,
    max_capacity = EXCLUDED.max_capacity,
    color_code = EXCLUDED.color_code;

-- Insert seats for section A1 (5 rows x 9 seats)
INSERT INTO seats (section_id, seat_row, seat_number, seat_code, is_available)
SELECT 
    s.id,
    'R' || row_num,
    seat_num,
    s.section_code || '-R' || row_num || '-' || seat_num,
    TRUE
FROM seating_sections s
CROSS JOIN generate_series(2, 6) AS row_num
CROSS JOIN generate_series(1, 9) AS seat_num
WHERE s.section_code = 'A1'
ON CONFLICT (seat_code) DO NOTHING;

-- Insert seats for section A2 BGK (2 rows x 10 seats)
INSERT INTO seats (section_id, seat_row, seat_number, seat_code, is_available)
SELECT 
    s.id,
    'R' || row_num,
    seat_num,
    s.section_code || '-R' || row_num || '-' || seat_num,
    TRUE
FROM seating_sections s
CROSS JOIN generate_series(2, 3) AS row_num
CROSS JOIN generate_series(1, 10) AS seat_num
WHERE s.section_code = 'BGK'
ON CONFLICT (seat_code) DO NOTHING;

-- Insert seats for section A2 main (4 rows x 7 seats)
INSERT INTO seats (section_id, seat_row, seat_number, seat_code, is_available)
SELECT 
    s.id,
    'R' || row_num,
    seat_num,
    s.section_code || '-R' || row_num || '-' || seat_num,
    TRUE
FROM seating_sections s
CROSS JOIN generate_series(3, 6) AS row_num
CROSS JOIN generate_series(1, 7) AS seat_num
WHERE s.section_code = 'A2'
ON CONFLICT (seat_code) DO NOTHING;

-- Insert seats for sections C1, C2, C3 (estimated based on image)
-- C1: 6 rows x 10 seats
INSERT INTO seats (section_id, seat_row, seat_number, seat_code, is_available)
SELECT 
    s.id,
    'R' || row_num,
    seat_num,
    s.section_code || '-R' || row_num || '-' || seat_num,
    TRUE
FROM seating_sections s
CROSS JOIN generate_series(1, 6) AS row_num
CROSS JOIN generate_series(1, 10) AS seat_num
WHERE s.section_code = 'C1'
ON CONFLICT (seat_code) DO NOTHING;

-- C2: 8 rows x 8 seats
INSERT INTO seats (section_id, seat_row, seat_number, seat_code, is_available)
SELECT 
    s.id,
    'R' || row_num,
    seat_num,
    s.section_code || '-R' || row_num || '-' || seat_num,
    TRUE
FROM seating_sections s
CROSS JOIN generate_series(1, 8) AS row_num
CROSS JOIN generate_series(1, 8) AS seat_num
WHERE s.section_code = 'C2'
ON CONFLICT (seat_code) DO NOTHING;

-- C3: 5 rows x 8 seats
INSERT INTO seats (section_id, seat_row, seat_number, seat_code, is_available)
SELECT 
    s.id,
    'R' || row_num,
    seat_num,
    s.section_code || '-R' || row_num || '-' || seat_num,
    TRUE
FROM seating_sections s
CROSS JOIN generate_series(1, 5) AS row_num
CROSS JOIN generate_series(1, 8) AS seat_num
WHERE s.section_code = 'C3'
ON CONFLICT (seat_code) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_seats_section ON seats(section_id);
CREATE INDEX IF NOT EXISTS idx_seats_available ON seats(is_available);
CREATE INDEX IF NOT EXISTS idx_seats_code ON seats(seat_code);
CREATE INDEX IF NOT EXISTS idx_tickets_seat ON tickets(seat_id);
CREATE INDEX IF NOT EXISTS idx_seating_sections_code ON seating_sections(section_code);

-- Create a view for seat availability
CREATE OR REPLACE VIEW seat_availability AS
SELECT 
    s.id as seat_id,
    s.seat_code,
    s.seat_row,
    s.seat_number,
    s.is_available,
    s.is_reserved,
    sec.section_code,
    sec.section_name,
    sec.section_type,
    sec.color_code,
    t.id as ticket_id,
    t.ticket_code,
    t.is_used as ticket_used,
    v.id as vote_id,
    v.contestant_id
FROM seats s
JOIN seating_sections sec ON s.section_id = sec.id
LEFT JOIN tickets t ON s.id = t.seat_id
LEFT JOIN votes v ON t.id = v.ticket_id
ORDER BY sec.section_code, s.seat_row, s.seat_number;

-- Create function to reserve a seat
CREATE OR REPLACE FUNCTION reserve_seat(seat_code_param VARCHAR(10))
RETURNS BOOLEAN AS $$
DECLARE
    seat_record RECORD;
BEGIN
    -- Check if seat exists and is available
    SELECT * INTO seat_record 
    FROM seats 
    WHERE seat_code = seat_code_param 
    AND is_available = TRUE 
    AND is_reserved = FALSE;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Reserve the seat
    UPDATE seats 
    SET is_reserved = TRUE, reserved_at = NOW()
    WHERE seat_code = seat_code_param;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Create function to get section statistics
CREATE OR REPLACE FUNCTION get_section_stats()
RETURNS TABLE(
    section_code VARCHAR(10),
    section_name VARCHAR(50),
    total_seats INTEGER,
    available_seats INTEGER,
    reserved_seats INTEGER,
    occupied_seats INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sec.section_code,
        sec.section_name,
        COUNT(s.id)::INTEGER as total_seats,
        COUNT(CASE WHEN s.is_available = TRUE AND s.is_reserved = FALSE THEN 1 END)::INTEGER as available_seats,
        COUNT(CASE WHEN s.is_reserved = TRUE THEN 1 END)::INTEGER as reserved_seats,
        COUNT(CASE WHEN t.is_used = TRUE THEN 1 END)::INTEGER as occupied_seats
    FROM seating_sections sec
    LEFT JOIN seats s ON sec.id = s.section_id
    LEFT JOIN tickets t ON s.id = t.seat_id
    GROUP BY sec.section_code, sec.section_name
    ORDER BY sec.section_code;
END;
$$ LANGUAGE plpgsql;
