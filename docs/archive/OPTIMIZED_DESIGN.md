# 优化后的表设计与导入计算逻辑

**版本**: v2.0
**日期**: 2025-11-23
**状态**: Review优化版

---

## 1. 需求梳理

### 1.1 数据文件类型

| 文件类型 | 内容 | 结构 | 示例 |
|---------|------|------|------|
| **CSV** | 股票-概念-行业映射 | 股票代码,股票名称,概念,行业等 | `127111,金威转债,食品饮料` |
| **TXT** | 交易数据（多指标类型） | 股票代码(带前缀),日期,金额 | `SH600000\t2025-08-21\t459400` |

**TXT文件特点**:
- 文件类型：TTV.txt, EEE.txt, EFV.txt, AAA.txt...
- 股票代码有前缀：SH（上海）、SZ（深圳）、BJ（北京）
- **需要分离存储前缀**

### 1.2 导入时计算汇总需求

| 序号 | 需求 | 计算策略 | 说明 |
|-----|------|---------|------|
| 1 | 股票在交易日期所属概念的排名 | **预计算存储** | 查询频繁，计算复杂 |
| 2 | 概念在交易日期所有股票交易量汇总 | **预计算存储** | 查询频繁 |
| 3 | 概念中按排名排序的股票列表 | **使用排名表查询** | 不需额外存储 |
| 4 | 股票在日期范围内出现前N名的次数 | **实时聚合查询** | 基于排名表简单COUNT |
| 5 | 股票在概念中日期范围内的排名历史 | **使用排名表查询** | 不需额外存储 |
| 6 | 概念每日所有股票的求和 | **同需求2** | 预计算存储 |

---

## 2. 优化后的表结构设计

### 2.1 表设计总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        基础配置层                                │
├────────────────────┬────────────────────┬───────────────────────┤
│   metric_types     │                    │                       │
│   (指标类型配置)    │                    │                       │
└────────────────────┴────────────────────┴───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        主数据层                                  │
├────────────────────┬────────────────────┬───────────────────────┤
│      stocks        │     concepts       │     industries        │
│    (股票信息)       │    (概念信息)       │     (行业信息)         │
├────────────────────┴────────────────────┴───────────────────────┤
│                    stock_concepts (股票-概念关系)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        源数据层                                  │
├─────────────────────────────────────────────────────────────────┤
│            stock_metric_data_raw (原始交易数据-多指标)           │
│            stock_concept_mapping_raw (原始映射数据)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓ 导入时计算
┌─────────────────────────────────────────────────────────────────┐
│                       预计算结果层                               │
├─────────────────────────────────────────────────────────────────┤
│          concept_stock_daily_rank (股票-概念-日期排名)           │
│          concept_daily_summary (概念-日期汇总)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2.2 基础配置表

#### metric_types - 指标类型配置
```sql
CREATE TABLE metric_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,      -- TTV, EEE, EFV, AAA
    name VARCHAR(100) NOT NULL,            -- 显示名称：交易总值
    description TEXT,

    -- 文件识别
    file_pattern VARCHAR(100),             -- 文件名模式：*TTV*.txt

    -- 字段配置（JSON）
    field_mapping JSONB NOT NULL DEFAULT '{
        "stock_code": {"column": 0, "has_prefix": true},
        "trade_date": {"column": 1, "format": "YYYY-MM-DD"},
        "value": {"column": 2, "type": "bigint"}
    }',

    -- 排名配置
    rank_order VARCHAR(10) DEFAULT 'DESC', -- DESC=值大排前, ASC=值小排前

    -- 状态
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始化常用指标类型
INSERT INTO metric_types (code, name, file_pattern, rank_order) VALUES
('TTV', '交易总值', '*TTV*.txt', 'DESC'),
('EEE', '交易活跃度', '*EEE*.txt', 'DESC'),
('EFV', 'EFV指标', '*EFV*.txt', 'DESC'),
('AAA', 'AAA指标', '*AAA*.txt', 'DESC');
```

---

### 2.3 主数据表

#### stocks - 股票信息表（优化：增加前缀分离）
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) UNIQUE NOT NULL,  -- 纯代码：600000, 000001
    stock_name VARCHAR(100),
    exchange_prefix VARCHAR(10),              -- 交易所前缀：SH, SZ, BJ
    exchange_name VARCHAR(50),                -- 交易所名称：上海, 深圳, 北京

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stocks_code ON stocks(stock_code);
CREATE INDEX idx_stocks_exchange ON stocks(exchange_prefix);

-- 交易所前缀映射
COMMENT ON COLUMN stocks.exchange_prefix IS 'SH=上海, SZ=深圳, BJ=北京';
```

#### concepts - 概念表
```sql
CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    concept_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),           -- 分类：概念/主题/板块
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concepts_name ON concepts(concept_name);
```

#### industries - 行业表
```sql
CREATE TABLE industries (
    id SERIAL PRIMARY KEY,
    industry_name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES industries(id),
    level INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### stock_concepts - 股票-概念关系表
```sql
CREATE TABLE stock_concepts (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(stock_code, concept_id)
);

CREATE INDEX idx_stock_concepts_stock ON stock_concepts(stock_code);
CREATE INDEX idx_stock_concepts_concept ON stock_concepts(concept_id);
```

#### stock_industries - 股票-行业关系表
```sql
CREATE TABLE stock_industries (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    industry_id INTEGER NOT NULL REFERENCES industries(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(stock_code, industry_id)
);
```

---

### 2.4 源数据表（导入时保留原始数据）

#### import_batches - 导入批次表
```sql
CREATE TABLE import_batches (
    id SERIAL PRIMARY KEY,

    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,          -- CSV, TXT
    metric_type_id INTEGER REFERENCES metric_types(id),  -- TXT文件关联指标类型
    file_size BIGINT,
    file_hash VARCHAR(64),                   -- SHA256防重复

    -- 日期信息（TXT文件特有）
    data_date DATE,                          -- 数据对应的交易日期

    -- 导入状态
    status VARCHAR(20) DEFAULT 'pending',    -- pending, processing, completed, failed
    total_rows INTEGER DEFAULT 0,
    success_rows INTEGER DEFAULT 0,
    error_rows INTEGER DEFAULT 0,

    -- 计算状态
    compute_status VARCHAR(20) DEFAULT 'pending',  -- pending, computing, completed

    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

CREATE INDEX idx_import_batches_status ON import_batches(status);
CREATE INDEX idx_import_batches_date ON import_batches(data_date);
CREATE INDEX idx_import_batches_metric ON import_batches(metric_type_id);
```

#### stock_metric_data_raw - 原始交易数据（多指标统一存储）
```sql
CREATE TABLE stock_metric_data_raw (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,        -- TTV, EEE, EFV（冗余便于查询）

    -- 股票信息（分离存储前缀）
    stock_code_raw VARCHAR(30) NOT NULL,     -- 原始代码：SH600000
    stock_code VARCHAR(20) NOT NULL,         -- 纯代码：600000
    exchange_prefix VARCHAR(10),             -- 前缀：SH

    -- 交易数据
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,             -- 交易金额

    -- 元数据
    source_row_number INTEGER,               -- 源文件行号
    raw_line TEXT,                           -- 原始行数据

    -- 状态
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建分区（按月）
CREATE TABLE stock_metric_data_raw_2025_08 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE stock_metric_data_raw_2025_09 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

-- 索引
CREATE INDEX idx_metric_raw_stock_date ON stock_metric_data_raw(stock_code, trade_date);
CREATE INDEX idx_metric_raw_metric_date ON stock_metric_data_raw(metric_type_id, trade_date);
CREATE INDEX idx_metric_raw_batch ON stock_metric_data_raw(import_batch_id);
```

#### stock_concept_mapping_raw - 原始概念映射数据
```sql
CREATE TABLE stock_concept_mapping_raw (
    id SERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),

    -- 原始数据
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    concept_name VARCHAR(100),
    industry_name VARCHAR(100),

    -- CSV其他字段（JSONB存储）
    extra_fields JSONB,

    -- 元数据
    source_row_number INTEGER,

    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concept_mapping_raw_batch ON stock_concept_mapping_raw(import_batch_id);
CREATE INDEX idx_concept_mapping_raw_stock ON stock_concept_mapping_raw(stock_code);
```

---

### 2.5 预计算结果表（导入时计算并存储）

#### concept_stock_daily_rank - 股票在概念中的每日排名
```sql
-- 满足需求：1、3、5，以及需求4的聚合查询
CREATE TABLE concept_stock_daily_rank (
    id BIGSERIAL,

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 核心数据
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,

    -- 交易数据
    trade_value BIGINT NOT NULL,

    -- 排名数据（预计算）
    rank INTEGER NOT NULL,                   -- 排名（1,2,3...）
    total_stocks INTEGER,                    -- 该概念当日总股票数
    percentile DECIMAL(5, 2),               -- 百分位（0-100）

    -- 计算元数据
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id),

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建分区
CREATE TABLE concept_stock_daily_rank_2025_08 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE concept_stock_daily_rank_2025_09 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

-- 索引（针对各种查询场景优化）
-- 需求1、5：查询股票在概念中的排名
CREATE INDEX idx_rank_stock_concept_date
    ON concept_stock_daily_rank(stock_code, concept_id, trade_date);

-- 需求3：查询概念中按排名排序的股票
CREATE INDEX idx_rank_concept_date_rank
    ON concept_stock_daily_rank(concept_id, trade_date, rank);

-- 需求4：统计前N名次数
CREATE INDEX idx_rank_stock_concept_rank
    ON concept_stock_daily_rank(stock_code, concept_id, rank);

-- 指标类型过滤
CREATE INDEX idx_rank_metric_date
    ON concept_stock_daily_rank(metric_type_id, trade_date);

-- 唯一约束
CREATE UNIQUE INDEX idx_rank_unique
    ON concept_stock_daily_rank(metric_type_id, concept_id, stock_code, trade_date);
```

#### concept_daily_summary - 概念每日汇总
```sql
-- 满足需求：2、6
CREATE TABLE concept_daily_summary (
    id SERIAL PRIMARY KEY,

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 核心数据
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    trade_date DATE NOT NULL,

    -- 汇总数据（预计算）
    total_value BIGINT,                     -- 总和
    avg_value BIGINT,                       -- 平均值
    max_value BIGINT,                       -- 最大值
    min_value BIGINT,                       -- 最小值
    stock_count INTEGER,                    -- 股票数量

    -- 扩展汇总（可选）
    median_value BIGINT,                    -- 中位数
    top10_sum BIGINT,                       -- 前10名总和

    -- 计算元数据
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id),

    UNIQUE(metric_type_id, concept_id, trade_date)
);

-- 索引
CREATE INDEX idx_summary_concept_date ON concept_daily_summary(concept_id, trade_date);
CREATE INDEX idx_summary_metric_date ON concept_daily_summary(metric_type_id, trade_date);
```

---

## 3. 导入时计算流程

### 3.1 整体流程

```
文件上传
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 文件解析与存储                                           │
│ - 创建import_batch记录                                          │
│ - 解析文件内容                                                   │
│ - 分离股票代码前缀（TXT文件）                                     │
│ - 存入原始数据表(stock_metric_data_raw / stock_concept_mapping_raw)│
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 数据校验与主数据同步                                     │
│ - 校验股票代码是否存在                                           │
│ - 新股票自动创建(stocks表)                                       │
│ - 新概念/行业自动创建(CSV导入时)                                  │
│ - 更新stock_concepts关系(CSV导入时)                              │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 计算排名与汇总（TXT文件导入后触发）                       │
│ - 计算每个股票在每个概念中的排名                                  │
│ - 计算每个概念的日汇总                                           │
│ - 写入预计算表                                                   │
└─────────────────────────────────────────────────────────────────┘
    ↓
更新import_batch状态为completed
```

### 3.2 TXT文件导入详细逻辑

```python
def import_txt_file(file_path: str, metric_code: str, data_date: date):
    """
    TXT文件导入流程
    """
    # 1. 创建导入批次
    batch = create_import_batch(file_name, metric_code, data_date)

    # 2. 解析文件并存储原始数据
    for line_num, line in enumerate(file_lines, 1):
        # 解析行数据：SH600000\t2025-08-21\t459400
        stock_code_raw, trade_date, trade_value = parse_line(line)

        # 分离前缀
        exchange_prefix = stock_code_raw[:2]  # SH, SZ, BJ
        stock_code = stock_code_raw[2:]       # 600000

        # 存入原始数据表
        insert_raw_data(
            import_batch_id=batch.id,
            metric_code=metric_code,
            stock_code_raw=stock_code_raw,
            stock_code=stock_code,
            exchange_prefix=exchange_prefix,
            trade_date=trade_date,
            trade_value=trade_value,
            source_row_number=line_num
        )

        # 同步股票信息（新股票自动创建）
        ensure_stock_exists(stock_code, exchange_prefix)

    # 3. 触发计算任务
    trigger_compute_task(batch.id)
```

### 3.3 排名计算SQL

```sql
-- 计算股票在概念中的排名（导入后自动执行）
INSERT INTO concept_stock_daily_rank (
    metric_type_id, metric_code, concept_id, stock_code, trade_date,
    trade_value, rank, total_stocks, percentile, import_batch_id
)
SELECT
    r.metric_type_id,
    r.metric_code,
    sc.concept_id,
    r.stock_code,
    r.trade_date,
    r.trade_value,
    -- 计算排名（同值同排名）
    DENSE_RANK() OVER (
        PARTITION BY sc.concept_id, r.trade_date
        ORDER BY r.trade_value DESC
    ) as rank,
    -- 该概念当日股票总数
    COUNT(*) OVER (PARTITION BY sc.concept_id, r.trade_date) as total_stocks,
    -- 百分位计算
    ROUND(
        100.0 * (1 - (DENSE_RANK() OVER (
            PARTITION BY sc.concept_id, r.trade_date
            ORDER BY r.trade_value DESC
        ) - 1)::DECIMAL / NULLIF(COUNT(*) OVER (PARTITION BY sc.concept_id, r.trade_date), 0)
        ), 2
    ) as percentile,
    r.import_batch_id
FROM stock_metric_data_raw r
JOIN stock_concepts sc ON r.stock_code = sc.stock_code
WHERE r.import_batch_id = :batch_id
  AND r.is_valid = true
ON CONFLICT (metric_type_id, concept_id, stock_code, trade_date)
DO UPDATE SET
    trade_value = EXCLUDED.trade_value,
    rank = EXCLUDED.rank,
    total_stocks = EXCLUDED.total_stocks,
    percentile = EXCLUDED.percentile,
    computed_at = CURRENT_TIMESTAMP,
    import_batch_id = EXCLUDED.import_batch_id;
```

### 3.4 概念汇总计算SQL

```sql
-- 计算概念每日汇总
INSERT INTO concept_daily_summary (
    metric_type_id, metric_code, concept_id, trade_date,
    total_value, avg_value, max_value, min_value, stock_count,
    median_value, top10_sum, import_batch_id
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
    -- 前10名总和
    (
        SELECT COALESCE(SUM(sub.trade_value), 0)
        FROM (
            SELECT r2.trade_value
            FROM stock_metric_data_raw r2
            JOIN stock_concepts sc2 ON r2.stock_code = sc2.stock_code
            WHERE sc2.concept_id = sc.concept_id
              AND r2.trade_date = r.trade_date
              AND r2.metric_type_id = r.metric_type_id
              AND r2.is_valid = true
            ORDER BY r2.trade_value DESC
            LIMIT 10
        ) sub
    ) as top10_sum,
    :batch_id as import_batch_id
FROM stock_metric_data_raw r
JOIN stock_concepts sc ON r.stock_code = sc.stock_code
WHERE r.import_batch_id = :batch_id
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
    top10_sum = EXCLUDED.top10_sum,
    computed_at = CURRENT_TIMESTAMP,
    import_batch_id = EXCLUDED.import_batch_id;
```

---

## 4. 查询场景对应SQL

### 需求1：查询股票所属的概念
```sql
-- 不需要预计算，直接查询关系表
SELECT c.concept_name, c.category
FROM stock_concepts sc
JOIN concepts c ON sc.concept_id = c.id
WHERE sc.stock_code = '600000';
```

### 需求2/6：概念每日所有股票的汇总
```sql
-- 直接查询预计算表
SELECT
    trade_date,
    total_value,
    avg_value,
    max_value,
    min_value,
    stock_count
FROM concept_daily_summary
WHERE concept_id = 1
  AND metric_code = 'TTV'
  AND trade_date BETWEEN '2025-08-01' AND '2025-08-31'
ORDER BY trade_date;
```

### 需求3：概念中选定日期按排名排序的股票
```sql
-- 直接查询预计算表
SELECT
    r.rank,
    r.stock_code,
    s.stock_name,
    r.trade_value,
    r.percentile
FROM concept_stock_daily_rank r
JOIN stocks s ON r.stock_code = s.stock_code
WHERE r.concept_id = 1
  AND r.metric_code = 'TTV'
  AND r.trade_date = '2025-08-21'
ORDER BY r.rank
LIMIT 50;
```

### 需求4：股票在日期范围内出现前N名的次数
```sql
-- 实时聚合查询（基于预计算的排名表，查询效率高）
SELECT
    r.concept_id,
    c.concept_name,
    COUNT(*) as top_n_count,
    COUNT(DISTINCT r.trade_date) as trading_days
FROM concept_stock_daily_rank r
JOIN concepts c ON r.concept_id = c.id
WHERE r.stock_code = '600000'
  AND r.metric_code = 'TTV'
  AND r.trade_date BETWEEN '2025-08-01' AND '2025-08-31'
  AND r.rank <= 10  -- 前10名
GROUP BY r.concept_id, c.concept_name
ORDER BY top_n_count DESC;
```

### 需求5：股票在概念中日期范围内的排名历史
```sql
-- 直接查询预计算表
SELECT
    r.trade_date,
    r.rank,
    r.trade_value,
    r.total_stocks,
    r.percentile
FROM concept_stock_daily_rank r
WHERE r.stock_code = '600000'
  AND r.concept_id = 1
  AND r.metric_code = 'TTV'
  AND r.trade_date BETWEEN '2025-08-01' AND '2025-08-31'
ORDER BY r.trade_date;
```

---

## 5. 存储策略决策

### 5.1 预计算存储 vs 实时查询

| 数据类型 | 存储策略 | 原因 |
|---------|---------|------|
| 股票-概念排名 | **预计算存储** | 计算涉及窗口函数，实时计算慢；查询频繁 |
| 概念日汇总 | **预计算存储** | 需要聚合大量数据；查询频繁 |
| 前N名出现次数 | **实时聚合** | 基于排名表简单COUNT，索引优化后毫秒级 |
| 排名历史 | **实时查询** | 直接查询排名表，无需额外计算 |

### 5.2 为什么需求4不预存储？

```
需求4：统计股票在概念中出现前N名的次数

方案A（预存储）：
- 需要为每个 N 值（前3名、前5名、前10名...）都存一份
- 日期范围变化需要重新计算
- 存储空间大，灵活性差

方案B（实时聚合）：✅ 推荐
- 基于排名表，简单 COUNT + WHERE rank <= N
- 支持任意 N 值和日期范围
- 有索引支持，查询毫秒级
```

---

## 6. 表结构对比（优化前 vs 优化后）

### 优化点总结

| 项目 | 优化前 | 优化后 |
|-----|-------|-------|
| **股票前缀** | 未分离 | `stock_code_raw` + `stock_code` + `exchange_prefix` 分离存储 |
| **原始数据** | 多表分散 | 统一 `stock_metric_data_raw` 表，按指标类型标记 |
| **排名计算** | 查询时计算 | 导入时预计算，存入 `concept_stock_daily_rank` |
| **概念汇总** | 查询时计算 | 导入时预计算，存入 `concept_daily_summary` |
| **前N名统计** | 复杂查询 | 基于预计算排名表简单聚合 |
| **索引设计** | 通用索引 | 针对6个需求场景定制索引 |

### 表数量对比

```
优化前：15+张表，结构复杂
优化后：核心11张表

基础配置：1张 (metric_types)
主数据：5张 (stocks, concepts, industries, stock_concepts, stock_industries)
源数据：3张 (import_batches, stock_metric_data_raw, stock_concept_mapping_raw)
预计算：2张 (concept_stock_daily_rank, concept_daily_summary)
```

---

## 7. 数据量估算与分区策略

### 7.1 数据量估算

假设：
- 5000只股票
- 300个概念
- 每只股票平均属于5个概念
- 每年250个交易日
- 3种指标类型

| 表 | 计算公式 | 年数据量 |
|----|---------|---------|
| stock_metric_data_raw | 5000 × 250 × 3 | 375万行 |
| concept_stock_daily_rank | 5000 × 5 × 250 × 3 | 1875万行 |
| concept_daily_summary | 300 × 250 × 3 | 22.5万行 |

### 7.2 分区策略

```sql
-- 按月分区（推荐）
-- 优点：查询时自动剪枝，删除旧数据简单

-- 自动创建分区的函数
CREATE OR REPLACE FUNCTION create_monthly_partitions(
    table_name TEXT,
    start_date DATE,
    months INTEGER
)
RETURNS VOID AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    next_date DATE;
BEGIN
    FOR i IN 0..months-1 LOOP
        partition_date := start_date + (i || ' months')::INTERVAL;
        next_date := partition_date + '1 month'::INTERVAL;
        partition_name := table_name || '_' || TO_CHAR(partition_date, 'YYYY_MM');

        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            partition_name, table_name, partition_date, next_date
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建2025年全年分区
SELECT create_monthly_partitions('stock_metric_data_raw', '2025-01-01', 12);
SELECT create_monthly_partitions('concept_stock_daily_rank', '2025-01-01', 12);
```

---

## 8. 完整建表脚本

执行顺序：
1. 基础配置表
2. 主数据表
3. 源数据表
4. 预计算表
5. 索引

详见附录A的完整SQL脚本。
