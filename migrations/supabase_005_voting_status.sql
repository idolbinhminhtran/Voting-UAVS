-- Migration 005: Add voting status table and helper functions

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Initialize voting_open flag if not exists
INSERT INTO app_settings (key, value)
VALUES ('voting_open', 'true')
ON CONFLICT (key) DO NOTHING;

-- Helper functions
CREATE OR REPLACE FUNCTION get_voting_open()
RETURNS BOOLEAN AS $$
DECLARE v TEXT; BEGIN
  SELECT value INTO v FROM app_settings WHERE key = 'voting_open';
  RETURN COALESCE(v, 'false')::BOOLEAN;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_voting_open(is_open BOOLEAN)
RETURNS VOID AS $$
BEGIN
  INSERT INTO app_settings (key, value, updated_at)
  VALUES ('voting_open', is_open::TEXT, NOW())
  ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
END $$ LANGUAGE plpgsql;


