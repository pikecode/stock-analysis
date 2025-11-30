-- Initialize test users and subscription plans
-- Production database initialization script

-- Insert VIP test user
INSERT INTO users (username, email, password_hash, phone, role, status, created_at, updated_at)
VALUES (
    'vip_user',
    'vip@qwquant.com',
    -- password: vip123456
    '9faf7b9495467e75c27f9f1a8e6775ae33c7e7fc24e9e5d6e2ac8ec1f08b8eb4',
    '13800138001',
    'VIP'::user_role_enum,
    'active',
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- Insert normal test user
INSERT INTO users (username, email, password_hash, phone, role, status, created_at, updated_at)
VALUES (
    'normal_user',
    'user@qwquant.com',
    -- password: user123456
    '90aae915da86d3b3a4da7a996bc264bfbaf50a953cbbe8cd3478a2a6ccc7b900',
    '13800138002',
    'NORMAL'::user_role_enum,
    'active',
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- Insert subscription plans
INSERT INTO plans (name, display_name, description, price, original_price, duration_days, features, is_active, sort_order, created_at, updated_at)
VALUES
    (
        'trial',
        '免费试用',
        '7天免费试用，体验基础功能',
        0.00,
        99.00,
        7,
        '基础数据查看,每日涨跌榜,概念板块分析',
        true,
        1,
        NOW(),
        NOW()
    ),
    (
        'monthly_vip',
        '月度VIP',
        '1个月VIP会员，解锁所有功能',
        99.00,
        129.00,
        30,
        '所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析',
        true,
        2,
        NOW(),
        NOW()
    ),
    (
        'quarterly_vip',
        '季度VIP',
        '3个月VIP会员，性价比之选',
        249.00,
        387.00,
        90,
        '所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析,行业对比分析',
        true,
        3,
        NOW(),
        NOW()
    ),
    (
        'yearly_vip',
        '年度VIP',
        '12个月VIP会员，最优惠价格',
        899.00,
        1548.00,
        365,
        '所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析,行业对比分析,专属客服支持,API接口访问',
        true,
        4,
        NOW(),
        NOW()
    ),
    (
        'premium_yearly',
        '至尊年费',
        '12个月至尊会员,尊享全部权益',
        1999.00,
        2999.00,
        365,
        '所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析,行业对比分析,专属客服支持,API接口访问,量化策略回测,智能选股推荐,专业研报',
        true,
        5,
        NOW(),
        NOW()
    )
ON CONFLICT (name) DO NOTHING;

-- Show results
SELECT '✅ Test users:' AS status;
SELECT username, email, role, status FROM users WHERE username IN ('vip_user', 'normal_user');

SELECT '✅ Subscription plans:' AS status;
SELECT name, display_name, price, duration_days FROM plans ORDER BY sort_order;
