-- 数据库优化脚本
-- 用于提升导入和查询性能

-- ============================================
-- 1. 分区表优化（按月分区）
-- ============================================

-- 创建分区表用于存储原始交易数据
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_partitioned (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL,
    metric_type_id INTEGER NOT NULL,
    metric_code VARCHAR(20) NOT NULL,
    stock_code_raw VARCHAR(30),
    stock_code VARCHAR(20) NOT NULL,
    exchange_prefix VARCHAR(5),
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,
    source_row_number INTEGER,
    raw_line TEXT,
    is_valid BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建分区表用于存储排名数据
CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_partitioned (
    id BIGSERIAL,
    metric_type_id INTEGER NOT NULL,
    metric_code VARCHAR(20) NOT NULL,
    concept_id INTEGER NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,
    rank INTEGER NOT NULL,
    import_batch_id INTEGER NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 函数：自动创建月度分区
CREATE OR REPLACE FUNCTION create_monthly_partitions(
    table_name TEXT,
    start_date DATE,
    end_date DATE
)
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_of_month DATE;
    end_of_month DATE;
BEGIN
    partition_date := start_date;

    WHILE partition_date < end_date LOOP
        start_of_month := partition_date;
        end_of_month := (partition_date + INTERVAL '1 month')::DATE;
        partition_name := table_name || '_' || to_char(partition_date, 'YYYY_MM');

        -- 创建分区
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
             FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            table_name,
            start_of_month,
            end_of_month
        );

        -- 为分区创建索引
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_%s_stock_date
             ON %I (stock_code, trade_date)',
            partition_name,
            partition_name
        );

        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_%s_metric_date
             ON %I (metric_type_id, trade_date)',
            partition_name,
            partition_name
        );

        partition_date := end_of_month;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建2024-2025年的分区
SELECT create_monthly_partitions('stock_metric_data_raw_partitioned', '2024-01-01'::DATE, '2026-01-01'::DATE);
SELECT create_monthly_partitions('concept_stock_daily_rank_partitioned', '2024-01-01'::DATE, '2026-01-01'::DATE);

-- ============================================
-- 2. 索引优化
-- ============================================

-- 股票表索引
CREATE INDEX IF NOT EXISTS idx_stocks_code_name ON stocks(stock_code, stock_name);

-- 概念表索引
CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(concept_name);

-- 股票概念关系表索引
CREATE INDEX IF NOT EXISTS idx_stock_concepts_stock ON stock_concepts(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_concepts_concept ON stock_concepts(concept_id);
CREATE INDEX IF NOT EXISTS idx_stock_concepts_both ON stock_concepts(stock_code, concept_id);

-- 原始数据表复合索引
CREATE INDEX IF NOT EXISTS idx_raw_data_composite
ON stock_metric_data_raw(metric_type_id, trade_date, stock_code, trade_value DESC)
WHERE is_valid = true;

-- 使用BRIN索引优化时序数据查询
CREATE INDEX IF NOT EXISTS idx_raw_data_date_brin
ON stock_metric_data_raw USING BRIN(trade_date);

-- 排名表索引
CREATE INDEX IF NOT EXISTS idx_rank_concept_date
ON concept_stock_daily_rank(concept_id, trade_date, rank);

CREATE INDEX IF NOT EXISTS idx_rank_stock_date
ON concept_stock_daily_rank(stock_code, trade_date);

CREATE INDEX IF NOT EXISTS idx_rank_metric_concept_date
ON concept_stock_daily_rank(metric_type_id, concept_id, trade_date);

-- 汇总表索引
CREATE INDEX IF NOT EXISTS idx_summary_concept_date
ON concept_daily_summary(concept_id, trade_date);

CREATE INDEX IF NOT EXISTS idx_summary_metric_date
ON concept_daily_summary(metric_type_id, trade_date);

-- ============================================
-- 3. 物化视图优化
-- ============================================

-- 创建物化视图：股票最新排名
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_latest_stock_rankings AS
WITH latest_dates AS (
    SELECT
        metric_type_id,
        MAX(trade_date) as latest_date
    FROM concept_stock_daily_rank
    GROUP BY metric_type_id
)
SELECT
    r.metric_type_id,
    r.metric_code,
    r.concept_id,
    r.stock_code,
    r.trade_date,
    r.trade_value,
    r.rank,
    s.stock_name,
    c.concept_name
FROM concept_stock_daily_rank r
JOIN latest_dates ld ON r.metric_type_id = ld.metric_type_id
    AND r.trade_date = ld.latest_date
JOIN stocks s ON r.stock_code = s.stock_code
JOIN concepts c ON r.concept_id = c.id
WITH DATA;

-- 创建索引
CREATE UNIQUE INDEX idx_mv_latest_rankings
ON mv_latest_stock_rankings(metric_type_id, concept_id, stock_code);

-- 创建物化视图：概念Top10股票
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_concept_top10 AS
SELECT
    r.metric_type_id,
    r.concept_id,
    r.trade_date,
    r.stock_code,
    r.trade_value,
    r.rank,
    s.stock_name,
    c.concept_name
FROM concept_stock_daily_rank r
JOIN stocks s ON r.stock_code = s.stock_code
JOIN concepts c ON r.concept_id = c.id
WHERE r.rank <= 10
WITH DATA;

-- 创建索引
CREATE INDEX idx_mv_top10_concept_date
ON mv_concept_top10(concept_id, trade_date);

-- ============================================
-- 4. 性能调优参数
-- ============================================

-- 增加工作内存（需要超级用户权限）
-- ALTER SYSTEM SET work_mem = '256MB';
-- ALTER SYSTEM SET maintenance_work_mem = '1GB';
-- ALTER SYSTEM SET shared_buffers = '2GB';
-- ALTER SYSTEM SET effective_cache_size = '8GB';
-- ALTER SYSTEM SET random_page_cost = 1.1;  -- 对于SSD

-- ============================================
-- 5. 统计信息更新
-- ============================================

-- 更新表统计信息
ANALYZE stocks;
ANALYZE concepts;
ANALYZE stock_concepts;
ANALYZE stock_metric_data_raw;
ANALYZE concept_stock_daily_rank;
ANALYZE concept_daily_summary;

-- ============================================
-- 6. 清理和维护函数
-- ============================================

-- 函数：清理过期的导入批次
CREATE OR REPLACE FUNCTION cleanup_old_imports(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 删除旧的原始数据
    DELETE FROM stock_metric_data_raw
    WHERE import_batch_id IN (
        SELECT id FROM import_batches
        WHERE created_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL
        AND status IN ('replaced', 'failed')
    );

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- 删除旧的批次记录
    DELETE FROM import_batches
    WHERE created_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL
    AND status IN ('replaced', 'failed');

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 函数：刷新物化视图
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_stock_rankings;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_concept_top10;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. 触发器优化
-- ============================================

-- 触发器：自动更新修改时间
CREATE OR REPLACE FUNCTION update_modified_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 应用触发器到需要的表
DROP TRIGGER IF EXISTS update_stocks_modified ON stocks;
CREATE TRIGGER update_stocks_modified
    BEFORE UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_time();

-- ============================================
-- 8. 查询优化视图
-- ============================================

-- 创建视图：概念日度表现
CREATE OR REPLACE VIEW v_concept_daily_performance AS
SELECT
    cs.concept_id,
    c.concept_name,
    cs.trade_date,
    cs.metric_type_id,
    mt.code as metric_code,
    mt.name as metric_name,
    cs.total_value,
    cs.avg_value,
    cs.top10_sum,
    cs.stock_count,
    ROUND(cs.top10_sum::DECIMAL / NULLIF(cs.total_value, 0) * 100, 2) as top10_ratio
FROM concept_daily_summary cs
JOIN concepts c ON cs.concept_id = c.id
JOIN metric_types mt ON cs.metric_type_id = mt.id;

-- ============================================
-- 9. 分区表维护
-- ============================================

-- 函数：自动创建下个月的分区
CREATE OR REPLACE FUNCTION auto_create_next_month_partition()
RETURNS void AS $$
DECLARE
    next_month DATE;
    tables_to_partition TEXT[] := ARRAY[
        'stock_metric_data_raw_partitioned',
        'concept_stock_daily_rank_partitioned'
    ];
    table_name TEXT;
BEGIN
    next_month := date_trunc('month', CURRENT_DATE + INTERVAL '1 month');

    FOREACH table_name IN ARRAY tables_to_partition
    LOOP
        PERFORM create_monthly_partitions(
            table_name,
            next_month,
            next_month + INTERVAL '1 month'
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建定时任务（使用pg_cron扩展，如果可用）
-- SELECT cron.schedule('create-partitions', '0 0 25 * *', 'SELECT auto_create_next_month_partition();');