-- Migration 004: Relax ticket_code length constraint to support seat codes like D13.1
-- Previous constraint required LENGTH(ticket_code) BETWEEN 6 AND 20
-- New constraint allows LENGTH(ticket_code) BETWEEN 4 AND 20

ALTER TABLE tickets
DROP CONSTRAINT IF EXISTS tickets_ticket_code_check;

ALTER TABLE tickets
ADD CONSTRAINT tickets_ticket_code_check
CHECK (LENGTH(ticket_code) >= 4 AND LENGTH(ticket_code) <= 20);


