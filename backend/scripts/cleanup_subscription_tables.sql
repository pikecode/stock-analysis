-- 完整清理subscriptions和subscription_logs表的旧字段
-- 确保与Model定义完全一致

-- ============================================
-- 清理 subscriptions 表
-- ============================================

-- 删除旧字段（如果存在）
ALTER TABLE subscriptions DROP COLUMN IF EXISTS is_valid;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS valid_until;

-- 确保所有新字段都存在且设置正确
-- start_date和end_date应该是NOT NULL
ALTER TABLE subscriptions ALTER COLUMN start_date SET NOT NULL;
ALTER TABLE subscriptions ALTER COLUMN end_date SET NOT NULL;

-- 设置默认值
ALTER TABLE subscriptions ALTER COLUMN amount_paid SET DEFAULT 0;
ALTER TABLE subscriptions ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE subscriptions ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE subscriptions ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- ============================================
-- 清理 subscription_logs 表
-- ============================================

-- 删除旧字段（如果存在）
ALTER TABLE subscription_logs DROP COLUMN IF EXISTS valid_until;

-- 确保action是NOT NULL
ALTER TABLE subscription_logs ALTER COLUMN action SET NOT NULL;

-- 设置默认值
ALTER TABLE subscription_logs ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

-- ============================================
-- 验证表结构
-- ============================================

-- 显示最终的表结构
\echo '========================================'
\echo 'subscriptions 表结构:'
\echo '========================================'
\d subscriptions

\echo ''
\echo '========================================'
\echo 'subscription_logs 表结构:'
\echo '========================================'
\d subscription_logs

\echo ''
\echo '========================================'
\echo '清理完成！'
\echo '========================================'

SELECT 'subscriptions表记录数:' as info, COUNT(*) as count FROM subscriptions
UNION ALL
SELECT 'subscription_logs表记录数:', COUNT(*) FROM subscription_logs;
