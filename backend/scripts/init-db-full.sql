-- ========================================
-- Stock Analysis 数据库初始化脚本 (PostgreSQL)
-- 根据 .spec-workflow/database-schema.md
-- ========================================

-- 1. 创建 ENUM 类型
CREATE TYPE user_role_enum AS ENUM ('ADMIN', 'VIP', 'NORMAL');
CREATE TYPE import_status_enum AS ENUM ('pending', 'processing', 'success', 'failed', 'replaced');
CREATE TYPE compute_status_enum AS ENUM ('pending', 'computing', 'completed', 'failed');
CREATE TYPE rank_order_enum AS ENUM ('DESC', 'ASC');

-- ========================================
-- 第一层：用户认证系统
-- ========================================

-- users 表（用户账号信息）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    role user_role_enum NOT NULL DEFAULT 'NORMAL',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    display_name VARCHAR(100)
);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- subscriptions 表（订阅信息）
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id INTEGER,
    is_valid BOOLEAN DEFAULT true,
    valid_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);

-- subscription_logs 表（订阅日志）
CREATE TABLE IF NOT EXISTS subscription_logs (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id),
    action VARCHAR(50),
    valid_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 第二层：主数据管理
-- ========================================

-- stocks 表（股票基本信息）
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) UNIQUE NOT NULL,
    stock_name VARCHAR(100),
    exchange_prefix VARCHAR(10),
    exchange_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_stocks_stock_code ON stocks(stock_code);
CREATE INDEX idx_stocks_exchange_prefix ON stocks(exchange_prefix);

-- concepts 表（概念/板块）
CREATE TABLE IF NOT EXISTS concepts (
    id SERIAL PRIMARY KEY,
    concept_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_concepts_concept_name ON concepts(concept_name);

-- stock_concepts 表（股票-概念关联）
CREATE TABLE IF NOT EXISTS stock_concepts (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, concept_id)
);
CREATE INDEX idx_stock_concepts_stock_code ON stock_concepts(stock_code);
CREATE INDEX idx_stock_concepts_concept_id ON stock_concepts(concept_id);

-- industries 表（行业分类，支持树形结构）
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    industry_name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES industries(id),
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_industries_parent_id ON industries(parent_id);

-- stock_industries 表（股票-行业关联）
CREATE TABLE IF NOT EXISTS stock_industries (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    industry_id INTEGER NOT NULL REFERENCES industries(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, industry_id)
);

-- metric_types 表（指标类型定义）
CREATE TABLE IF NOT EXISTS metric_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    file_pattern VARCHAR(100),
    field_mapping JSON,
    rank_order rank_order_enum DEFAULT 'DESC',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_metric_types_code ON metric_types(code);

-- ========================================
-- 第三层：数据导入和处理
-- ========================================

-- import_batches 表（导入批次记录）
CREATE TABLE IF NOT EXISTS import_batches (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    metric_type_id INTEGER REFERENCES metric_types(id),
    file_size BIGINT,
    file_hash VARCHAR(64),
    data_date DATE,
    status import_status_enum NOT NULL DEFAULT 'pending',
    total_rows INTEGER DEFAULT 0,
    success_rows INTEGER DEFAULT 0,
    error_rows INTEGER DEFAULT 0,
    compute_status compute_status_enum DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);
CREATE INDEX idx_import_batches_status ON import_batches(status);
CREATE INDEX idx_import_batches_compute_status ON import_batches(compute_status);
CREATE INDEX idx_import_batches_data_date ON import_batches(data_date);
CREATE INDEX idx_import_batches_file_hash ON import_batches(file_hash);

-- stock_metric_data_raw 表（原始指标数据）
CREATE TABLE IF NOT EXISTS stock_metric_data_raw (
    id BIGSERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,
    stock_code_raw VARCHAR(30),
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    exchange_prefix VARCHAR(10),
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,
    source_row_number INTEGER,
    raw_line TEXT,
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_stock_metric_data_raw_stock_code ON stock_metric_data_raw(stock_code);
CREATE INDEX idx_stock_metric_data_raw_trade_date ON stock_metric_data_raw(trade_date);
CREATE INDEX idx_stock_metric_data_raw_metric_code ON stock_metric_data_raw(metric_code);
CREATE INDEX idx_stock_metric_data_raw_import_batch_id ON stock_metric_data_raw(import_batch_id);

-- stock_concept_mapping_raw 表（CSV 原始数据存档）
CREATE TABLE IF NOT EXISTS stock_concept_mapping_raw (
    id BIGSERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),
    stock_code VARCHAR(20),
    stock_name VARCHAR(100),
    concept_name VARCHAR(100),
    source_row_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_stock_concept_mapping_raw_import_batch_id ON stock_concept_mapping_raw(import_batch_id);

-- ========================================
-- 第四层：预计算数据（用于查询优化）
-- ========================================

-- concept_stock_daily_rank 表（概念-股票-日排名）
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank (
    id BIGSERIAL PRIMARY KEY,
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,
    rank INTEGER,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id)
);
CREATE INDEX idx_concept_stock_daily_rank_concept_id ON concept_stock_daily_rank(concept_id);
CREATE INDEX idx_concept_stock_daily_rank_stock_code ON concept_stock_daily_rank(stock_code);
CREATE INDEX idx_concept_stock_daily_rank_trade_date ON concept_stock_daily_rank(trade_date);
CREATE INDEX idx_concept_stock_daily_rank_metric_code ON concept_stock_daily_rank(metric_code);

-- concept_daily_summary 表（概念-日汇总）
CREATE TABLE IF NOT EXISTS concept_daily_summary (
    id SERIAL PRIMARY KEY,
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    trade_date DATE NOT NULL,
    total_value BIGINT,
    avg_value BIGINT,
    max_value BIGINT,
    min_value BIGINT,
    median_value BIGINT,
    top10_sum BIGINT,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id)
);
CREATE INDEX idx_concept_daily_summary_concept_id ON concept_daily_summary(concept_id);
CREATE INDEX idx_concept_daily_summary_trade_date ON concept_daily_summary(trade_date);
CREATE INDEX idx_concept_daily_summary_metric_code ON concept_daily_summary(metric_code);

-- ========================================
-- 初始化默认数据
-- ========================================

-- 插入默认指标类型
INSERT INTO metric_types (code, name, description, file_pattern, rank_order, is_active, sort_order)
VALUES
    ('EEE', '行业活跃度', '衡量行业/概念的活跃程度', 'EEE_*.txt', 'DESC', true, 1),
    ('TTV', '交易交易量', '衡量成交量相关指标', 'TTV_*.txt', 'DESC', true, 2),
    ('TOP', 'Top指标', '其他统计指标', 'TOP_*.txt', 'DESC', true, 3)
ON CONFLICT (code) DO NOTHING;

-- 插入管理员账户
INSERT INTO users (username, email, password_hash, role, status, display_name)
VALUES ('admin', 'admin@example.com', '$2b$12$WLAaJJvzNcFwKKr2XVOdMuxyu/tr6h.nG1QqnqqDyl/JQo15Wb/xm', 'ADMIN', 'active', '系统管理员')
ON CONFLICT (username) DO NOTHING;

-- ========================================
-- 分析
-- ========================================
COMMENT ON TABLE users IS '用户表 - 存储用户账号信息';
COMMENT ON TABLE stocks IS '股票表 - 存储所有上市公司股票的基本信息';
COMMENT ON TABLE concepts IS '概念表 - 存储股票概念分类（板块）';
COMMENT ON TABLE stock_concepts IS '股票-概念关联表 - 多对多关系';
COMMENT ON TABLE metric_types IS '指标类型表 - 定义系统支持的指标类型';
COMMENT ON TABLE import_batches IS '导入批次表 - 追踪每次数据文件导入的状态和结果';
COMMENT ON TABLE stock_metric_data_raw IS '原始指标数据表 - 存储从文件导入的原始指标数据';
COMMENT ON TABLE concept_stock_daily_rank IS '概念-股票-日排名表 - 存储每只股票在每个概念内的日排名';
COMMENT ON TABLE concept_daily_summary IS '概念-日汇总表 - 存储每个概念在每天的聚合统计数据';
