-- Migrate subscriptions table to match the Subscription model
-- This adds missing columns needed for the application

-- Step 1: Add new columns
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS start_date TIMESTAMP;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS end_date TIMESTAMP;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS amount_paid NUMERIC(10, 2) DEFAULT 0;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(100);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS notes TEXT;

-- Step 2: Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- Step 3: Migrate existing data from old schema to new schema
-- Set start_date to created_at for existing records
UPDATE subscriptions
SET start_date = created_at
WHERE start_date IS NULL;

-- Set end_date to valid_until for existing records
UPDATE subscriptions
SET end_date = valid_until
WHERE end_date IS NULL AND valid_until IS NOT NULL;

-- Set status based on is_valid
UPDATE subscriptions
SET status = CASE
    WHEN is_valid = true THEN 'active'
    ELSE 'expired'
END
WHERE status = 'active';

-- Step 4: Drop old columns (after data migration)
-- Keep them for now for backward compatibility
-- ALTER TABLE subscriptions DROP COLUMN IF EXISTS is_valid;
-- ALTER TABLE subscriptions DROP COLUMN IF EXISTS valid_until;

-- Display results
SELECT 'Migration completed successfully' AS status;
SELECT COUNT(*) as total_subscriptions FROM subscriptions;
