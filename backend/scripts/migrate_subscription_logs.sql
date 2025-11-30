-- Migrate subscription_logs table to match the SubscriptionLog model
-- This adds missing columns needed for the application

-- Step 1: Add new columns
ALTER TABLE subscription_logs ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE subscription_logs ADD COLUMN IF NOT EXISTS old_end_date TIMESTAMP;
ALTER TABLE subscription_logs ADD COLUMN IF NOT EXISTS new_end_date TIMESTAMP;
ALTER TABLE subscription_logs ADD COLUMN IF NOT EXISTS details TEXT;
ALTER TABLE subscription_logs ADD COLUMN IF NOT EXISTS performed_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- Step 2: Migrate existing data from old schema to new schema
-- Set new_end_date to valid_until for existing records
UPDATE subscription_logs
SET new_end_date = valid_until
WHERE new_end_date IS NULL AND valid_until IS NOT NULL;

-- Step 3: Drop old columns (after data migration)
-- Keep them for now for backward compatibility
-- ALTER TABLE subscription_logs DROP COLUMN IF EXISTS valid_until;

-- Display results
SELECT 'Migration completed successfully' AS status;
SELECT COUNT(*) as total_logs FROM subscription_logs;
