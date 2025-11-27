-- ============================================
-- 股票概念分析系统 - 数据库初始化脚本
-- 版本: v2.0
-- 日期: 2025-11-23
-- ============================================

-- 执行顺序：从上到下依次执行

BEGIN;

-- ============================================
-- 1. 清理（可选，仅开发环境使用）
-- ============================================
-- DROP TABLE IF EXISTS concept_daily_summary CASCADE;
-- DROP TABLE IF EXISTS concept_stock_daily_rank CASCADE;
-- DROP TABLE IF EXISTS stock_concept_mapping_raw CASCADE;
-- DROP TABLE IF EXISTS stock_metric_data_raw CASCADE;
-- DROP TABLE IF EXISTS import_batches CASCADE;
-- DROP TABLE IF EXISTS stock_industries CASCADE;
-- DROP TABLE IF EXISTS stock_concepts CASCADE;
-- DROP TABLE IF EXISTS industries CASCADE;
-- DROP TABLE IF EXISTS concepts CASCADE;
-- DROP TABLE IF EXISTS stocks CASCADE;
-- DROP TABLE IF EXISTS metric_types CASCADE;

-- ============================================
-- 2. 用户认证表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户-角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

-- 角色-权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- ============================================
-- 3. 基础配置表
-- ============================================

-- 指标类型配置表
CREATE TABLE IF NOT EXISTS metric_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    file_pattern VARCHAR(100),
    field_mapping JSONB NOT NULL DEFAULT '{
        "stock_code": {"column": 0, "has_prefix": true},
        "trade_date": {"column": 1, "format": "YYYY-MM-DD"},
        "value": {"column": 2, "type": "bigint"}
    }',
    rank_order VARCHAR(10) DEFAULT 'DESC',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始化指标类型
INSERT INTO metric_types (code, name, description, file_pattern, rank_order) VALUES
('TTV', '交易总值', 'TTV交易指标数据', '*TTV*.txt', 'DESC'),
('EEE', '交易活跃度', 'EEE活跃度指标数据', '*EEE*.txt', 'DESC'),
('EFV', 'EFV指标', 'EFV指标数据', '*EFV*.txt', 'DESC'),
('AAA', 'AAA指标', 'AAA指标数据', '*AAA*.txt', 'DESC')
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- 3. 主数据表
-- ============================================

-- 股票信息表
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) UNIQUE NOT NULL,
    stock_name VARCHAR(100),
    exchange_prefix VARCHAR(10),
    exchange_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stocks_code ON stocks(stock_code);
CREATE INDEX IF NOT EXISTS idx_stocks_exchange ON stocks(exchange_prefix);

COMMENT ON COLUMN stocks.exchange_prefix IS 'SH=上海, SZ=深圳, BJ=北京';

-- 概念表
CREATE TABLE IF NOT EXISTS concepts (
    id SERIAL PRIMARY KEY,
    concept_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(concept_name);

-- 行业表
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    industry_name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES industries(id),
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_industries_parent ON industries(parent_id);

-- 股票-概念关系表
CREATE TABLE IF NOT EXISTS stock_concepts (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, concept_id)
);

CREATE INDEX IF NOT EXISTS idx_stock_concepts_stock ON stock_concepts(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_concepts_concept ON stock_concepts(concept_id);

-- 股票-行业关系表
CREATE TABLE IF NOT EXISTS stock_industries (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    industry_id INTEGER NOT NULL REFERENCES industries(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, industry_id)
);

CREATE INDEX IF NOT EXISTS idx_stock_industries_stock ON stock_industries(stock_code);

-- ============================================
-- 4. 导入管理表
-- ============================================

-- 导入批次表
CREATE TABLE IF NOT EXISTS import_batches (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    metric_type_id INTEGER REFERENCES metric_types(id),
    file_size BIGINT,
    file_hash VARCHAR(64),
    data_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    total_rows INTEGER DEFAULT 0,
    success_rows INTEGER DEFAULT 0,
    error_rows INTEGER DEFAULT 0,
    compute_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_import_batches_status ON import_batches(status);
CREATE INDEX IF NOT EXISTS idx_import_batches_date ON import_batches(data_date);
CREATE INDEX IF NOT EXISTS idx_import_batches_metric ON import_batches(metric_type_id);
CREATE INDEX IF NOT EXISTS idx_import_batches_hash ON import_batches(file_hash);

COMMENT ON COLUMN import_batches.status IS 'pending, processing, completed, failed';
COMMENT ON COLUMN import_batches.compute_status IS 'pending, computing, completed, failed';

-- ============================================
-- 5. 源数据表（分区表）
-- ============================================

-- 原始交易数据表（主表）
CREATE TABLE IF NOT EXISTS stock_metric_data_raw (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,
    stock_code_raw VARCHAR(30) NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    exchange_prefix VARCHAR(10),
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,
    source_row_number INTEGER,
    raw_line TEXT,
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建2025年分区
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_01 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_02 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_03 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_04 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_05 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_06 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_07 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_08 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_09 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_10 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_11 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2025_12 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- 索引
CREATE INDEX IF NOT EXISTS idx_metric_raw_stock_date ON stock_metric_data_raw(stock_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_metric_raw_metric_date ON stock_metric_data_raw(metric_type_id, trade_date);
CREATE INDEX IF NOT EXISTS idx_metric_raw_batch ON stock_metric_data_raw(import_batch_id);

-- 原始概念映射数据表
CREATE TABLE IF NOT EXISTS stock_concept_mapping_raw (
    id SERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    concept_name VARCHAR(100),
    industry_name VARCHAR(100),
    extra_fields JSONB,
    source_row_number INTEGER,
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_concept_mapping_raw_batch ON stock_concept_mapping_raw(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_concept_mapping_raw_stock ON stock_concept_mapping_raw(stock_code);

-- ============================================
-- 6. 预计算结果表（分区表）
-- ============================================

-- 股票在概念中的每日排名表（主表）
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank (
    id BIGSERIAL,
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,
    rank INTEGER NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id),
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建2025年分区
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_01 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_02 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_03 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_04 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_05 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_06 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_07 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_08 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_09 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_10 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_11 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2025_12 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- 排名表索引（针对各查询场景优化）
CREATE INDEX IF NOT EXISTS idx_rank_stock_concept_date
    ON concept_stock_daily_rank(stock_code, concept_id, trade_date);
CREATE INDEX IF NOT EXISTS idx_rank_concept_date_rank
    ON concept_stock_daily_rank(concept_id, trade_date, rank);
CREATE INDEX IF NOT EXISTS idx_rank_stock_concept_rank
    ON concept_stock_daily_rank(stock_code, concept_id, rank);
CREATE INDEX IF NOT EXISTS idx_rank_metric_date
    ON concept_stock_daily_rank(metric_type_id, trade_date);

-- 唯一约束（防止重复计算）
CREATE UNIQUE INDEX IF NOT EXISTS idx_rank_unique
    ON concept_stock_daily_rank(metric_type_id, concept_id, stock_code, trade_date);

-- 概念每日汇总表
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
    stock_count INTEGER,
    median_value BIGINT,
    top10_sum BIGINT,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id),
    UNIQUE(metric_type_id, concept_id, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_summary_concept_date ON concept_daily_summary(concept_id, trade_date);
CREATE INDEX IF NOT EXISTS idx_summary_metric_date ON concept_daily_summary(metric_type_id, trade_date);

-- ============================================
-- 7. 辅助函数
-- ============================================

-- 自动创建分区的函数
CREATE OR REPLACE FUNCTION create_monthly_partition(
    p_table_name TEXT,
    p_year INTEGER,
    p_month INTEGER
)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := make_date(p_year, p_month, 1);
    end_date := start_date + INTERVAL '1 month';
    partition_name := p_table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        partition_name, p_table_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- 解析股票代码前缀的函数
CREATE OR REPLACE FUNCTION parse_stock_code(raw_code TEXT)
RETURNS TABLE(
    stock_code VARCHAR(20),
    exchange_prefix VARCHAR(10),
    exchange_name VARCHAR(50)
) AS $$
DECLARE
    prefix TEXT;
    code TEXT;
BEGIN
    -- 提取前缀和代码
    prefix := UPPER(LEFT(raw_code, 2));
    code := SUBSTRING(raw_code FROM 3);

    -- 验证前缀
    IF prefix IN ('SH', 'SZ', 'BJ') THEN
        stock_code := code;
        exchange_prefix := prefix;
        exchange_name := CASE prefix
            WHEN 'SH' THEN '上海证券交易所'
            WHEN 'SZ' THEN '深圳证券交易所'
            WHEN 'BJ' THEN '北京证券交易所'
        END;
    ELSE
        -- 无前缀情况
        stock_code := raw_code;
        exchange_prefix := NULL;
        exchange_name := NULL;
    END IF;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 8. 计算存储过程
-- ============================================

-- 计算排名的存储过程
CREATE OR REPLACE PROCEDURE compute_daily_rank(p_batch_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 插入或更新排名数据
    INSERT INTO concept_stock_daily_rank (
        metric_type_id, metric_code, concept_id, stock_code, trade_date,
        trade_value, rank, import_batch_id
    )
    SELECT
        r.metric_type_id,
        r.metric_code,
        sc.concept_id,
        r.stock_code,
        r.trade_date,
        r.trade_value,
        DENSE_RANK() OVER (
            PARTITION BY sc.concept_id, r.trade_date
            ORDER BY r.trade_value DESC
        ) as rank,
        r.import_batch_id
    FROM stock_metric_data_raw r
    JOIN stock_concepts sc ON r.stock_code = sc.stock_code
    WHERE r.import_batch_id = p_batch_id
      AND r.is_valid = true
    ON CONFLICT (metric_type_id, concept_id, stock_code, trade_date)
    DO UPDATE SET
        trade_value = EXCLUDED.trade_value,
        rank = EXCLUDED.rank,
        computed_at = CURRENT_TIMESTAMP,
        import_batch_id = EXCLUDED.import_batch_id;

    RAISE NOTICE 'Rank computation completed for batch %', p_batch_id;
END;
$$;

-- 计算概念汇总的存储过程
CREATE OR REPLACE PROCEDURE compute_daily_summary(p_batch_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 插入或更新汇总数据
    INSERT INTO concept_daily_summary (
        metric_type_id, metric_code, concept_id, trade_date,
        total_value, avg_value, max_value, min_value, stock_count,
        median_value, import_batch_id
    )
    SELECT
        r.metric_type_id,
        r.metric_code,
        sc.concept_id,
        r.trade_date,
        SUM(r.trade_value) as total_value,
        AVG(r.trade_value)::BIGINT as avg_value,
        MAX(r.trade_value) as max_value,
        MIN(r.trade_value) as min_value,
        COUNT(*) as stock_count,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.trade_value)::BIGINT as median_value,
        p_batch_id as import_batch_id
    FROM stock_metric_data_raw r
    JOIN stock_concepts sc ON r.stock_code = sc.stock_code
    WHERE r.import_batch_id = p_batch_id
      AND r.is_valid = true
    GROUP BY r.metric_type_id, r.metric_code, sc.concept_id, r.trade_date
    ON CONFLICT (metric_type_id, concept_id, trade_date)
    DO UPDATE SET
        total_value = EXCLUDED.total_value,
        avg_value = EXCLUDED.avg_value,
        max_value = EXCLUDED.max_value,
        min_value = EXCLUDED.min_value,
        stock_count = EXCLUDED.stock_count,
        median_value = EXCLUDED.median_value,
        computed_at = CURRENT_TIMESTAMP,
        import_batch_id = EXCLUDED.import_batch_id;

    -- 更新top10_sum（需要单独计算）
    UPDATE concept_daily_summary s
    SET top10_sum = (
        SELECT COALESCE(SUM(sub.trade_value), 0)
        FROM (
            SELECT r.trade_value
            FROM stock_metric_data_raw r
            JOIN stock_concepts sc ON r.stock_code = sc.stock_code
            WHERE sc.concept_id = s.concept_id
              AND r.trade_date = s.trade_date
              AND r.metric_type_id = s.metric_type_id
              AND r.is_valid = true
            ORDER BY r.trade_value DESC
            LIMIT 10
        ) sub
    )
    WHERE s.import_batch_id = p_batch_id;

    RAISE NOTICE 'Summary computation completed for batch %', p_batch_id;
END;
$$;

-- 完整计算流程（导入后调用）
CREATE OR REPLACE PROCEDURE compute_all_for_batch(p_batch_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 更新计算状态
    UPDATE import_batches SET compute_status = 'computing' WHERE id = p_batch_id;

    -- 计算排名
    CALL compute_daily_rank(p_batch_id);

    -- 计算汇总
    CALL compute_daily_summary(p_batch_id);

    -- 更新计算状态为完成
    UPDATE import_batches SET compute_status = 'completed' WHERE id = p_batch_id;

    RAISE NOTICE 'All computations completed for batch %', p_batch_id;
EXCEPTION
    WHEN OTHERS THEN
        UPDATE import_batches
        SET compute_status = 'failed',
            error_message = SQLERRM
        WHERE id = p_batch_id;
        RAISE;
END;
$$;

COMMIT;

-- ============================================
-- 验证脚本
-- ============================================
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
-- SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public';
