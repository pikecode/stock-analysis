-- Insert default subscription plans
-- Run this with: psql -U peak -d stock_analysis -f scripts/insert_plans.sql

-- Delete existing plans (optional, uncomment if you want to reset)
-- DELETE FROM plans;

-- Insert plans
INSERT INTO plans (name, display_name, description, price, original_price, duration_days, is_active, sort_order, created_at, updated_at)
VALUES
    (
        'monthly',
        '月度套餐',
        '月度订阅，享受所有报表和分析功能',
        99.00,
        129.00,
        30,
        true,
        1,
        NOW(),
        NOW()
    ),
    (
        'quarterly',
        '季度套餐',
        '季度订阅，相比月度优惠15%',
        249.00,
        349.00,
        90,
        true,
        2,
        NOW(),
        NOW()
    ),
    (
        'half_yearly',
        '半年套餐',
        '半年订阅，相比月度优惠22%',
        475.00,
        749.00,
        180,
        true,
        3,
        NOW(),
        NOW()
    ),
    (
        'yearly',
        '年度套餐',
        '年度订阅，折扣力度最大，最划算的选择',
        699.00,
        1188.00,
        365,
        true,
        4,
        NOW(),
        NOW()
    )
ON CONFLICT (name) DO NOTHING;

-- Verify insertion
SELECT id, name, display_name, price, original_price, duration_days, is_active
FROM plans
ORDER BY sort_order;
