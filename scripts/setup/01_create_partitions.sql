-- 批量创建缺失的分区表
-- 覆盖2023年6月到2024年12月的所有月份

-- 创建分区的函数
DO $$
DECLARE
    start_date DATE := '2023-06-01';
    end_date DATE := '2024-12-01';
    curr_date DATE;
    partition_name TEXT;
    year_month TEXT;
BEGIN
    curr_date := start_date;

    WHILE curr_date <= end_date LOOP
        year_month := to_char(curr_date, 'YYYY_MM');

        -- 为stock_metric_data_raw创建分区
        partition_name := 'stock_metric_data_raw_' || year_month;
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I PARTITION OF stock_metric_data_raw
            FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            curr_date,
            curr_date + interval '1 month'
        );

        -- 创建索引
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_stock_code ON %I(stock_code)',
            partition_name, partition_name
        );
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_trade_date ON %I(trade_date)',
            partition_name, partition_name
        );
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_metric_type ON %I(metric_type_id)',
            partition_name, partition_name
        );

        -- 为concept_stock_daily_rank创建分区
        partition_name := 'concept_stock_daily_rank_' || year_month;
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I PARTITION OF concept_stock_daily_rank
            FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            curr_date,
            curr_date + interval '1 month'
        );

        -- 创建索引
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_metric_concept_stock
            ON %I(metric_type_id, concept_id, stock_code)',
            partition_name, partition_name
        );
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_trade_date ON %I(trade_date)',
            partition_name, partition_name
        );
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_rank ON %I(rank)',
            partition_name, partition_name
        );

        RAISE NOTICE '创建分区: %', year_month;

        -- 下一个月
        curr_date := curr_date + interval '1 month';
    END LOOP;
END $$;

-- 验证创建的分区
SELECT
    tablename,
    SUBSTRING(tablename FROM '\d{4}_\d{2}$') as year_month
FROM pg_tables
WHERE tablename LIKE 'stock_metric_data_raw_%'
   OR tablename LIKE 'concept_stock_daily_rank_%'
ORDER BY tablename;