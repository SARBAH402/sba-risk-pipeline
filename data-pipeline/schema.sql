-- Drop existing tables to ensure a clean initialization
DROP TABLE IF EXISTS remittances;
DROP TABLE IF EXISTS corporates;

-- 1. Corporate Metadata Table
CREATE TABLE corporates (
    corporate_id VARCHAR(50) PRIMARY KEY,
    industry VARCHAR(100) NOT NULL
);

-- 2. Transactional Risk/Remittance Table
CREATE TABLE remittances (
    record_id SERIAL PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    corporate_id VARCHAR(50) NOT NULL,
    record_date DATE NOT NULL,
    inflation_rate DECIMAL,
    high_inflation_flag BOOLEAN,
    base_withdrawal_prob DECIMAL,
    adjusted_withdrawal_prob DECIMAL,
    -- Strict Foreign Key linking back to the corporate entity
    CONSTRAINT fk_corporate
        FOREIGN KEY (corporate_id) 
        REFERENCES corporates(corporate_id)
        ON DELETE CASCADE
);

-- 1. Enable security gates on the tables
ALTER TABLE corporates ENABLE ROW LEVEL SECURITY;
ALTER TABLE remittances ENABLE ROW LEVEL SECURITY;

-- 2. Policy: Corporate Isolation
-- Blocks a client from viewing any corporation other than their own
CREATE POLICY "Corporate Profile Isolation" 
ON corporates 
FOR SELECT 
USING (
    corporate_id = (current_setting('request.jwt.claims', true)::json->>'corporate_id')::text
);

-- 3. Policy: Transactional Data Isolation
-- Blocks a client from viewing risk data belonging to another corporation
CREATE POLICY "Transactional Data Isolation" 
ON remittances 
FOR SELECT 
USING (
    corporate_id = (current_setting('request.jwt.claims', true)::json->>'corporate_id')::text
);