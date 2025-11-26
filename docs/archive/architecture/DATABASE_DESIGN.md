# 数据库设计文档

**版本**: v2.0
**更新日期**: 2025-11-23

---

## 1. 设计概览

### 1.1 数据库选型

**PostgreSQL 15+**

选择原因：
- 强大的分区表支持
- JSONB性能优秀
- 窗口函数支持完善
- 开源免费

### 1.2 表分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                     配置层 (1张表)                           │
│                    metric_types                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     主数据层 (5张表)                         │
│   stocks / concepts / industries / stock_concepts / ...     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     源数据层 (3张表)                         │
│  import_batches / stock_metric_data_raw / mapping_raw       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    预计算层 (2张表)                          │
│      concept_stock_daily_rank / concept_daily_summary       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. ER图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  metric_types   │     │     stocks      │     │    concepts     │
│─────────────────│     │─────────────────│     │─────────────────│
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ code            │     │ stock_code (UK) │     │ concept_name(UK)│
│ name            │     │ stock_name      │     │ category        │
│ file_pattern    │     │ exchange_prefix │     │ description     │
│ rank_order      │     │ exchange_name   │     └─────────────────┘
└─────────────────┘     └─────────────────┘              │
        │                       │                        │
        │               ┌───────┴────────┐               │
        │               │                │               │
        │      ┌────────▼────────┐ ┌─────▼───────────────▼─────┐
        │      │ stock_industries │ │      stock_concepts       │
        │      │─────────────────│ │───────────────────────────│
        │      │ stock_code (FK) │ │ stock_code                │
        │      │ industry_id(FK) │ │ concept_id (FK)           │
        │      └─────────────────┘ └───────────────────────────┘
        │
        │      ┌─────────────────────────────────────────────────┐
        │      │              import_batches                      │
        │      │─────────────────────────────────────────────────│
        │      │ id (PK)                                          │
        └──────│ metric_type_id (FK)                              │
               │ file_name / status / data_date                   │
               └─────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────────────┐     ┌───────────────────────────────┐
│  stock_metric_data_raw    │     │  stock_concept_mapping_raw    │
│───────────────────────────│     │───────────────────────────────│
│ id (PK)                   │     │ id (PK)                       │
│ import_batch_id (FK)      │     │ import_batch_id (FK)          │
│ metric_type_id (FK)       │     │ stock_code / concept_name     │
│ stock_code / trade_date   │     │ industry_name                 │
│ trade_value               │     └───────────────────────────────┘
│ exchange_prefix           │
└───────────────────────────┘
               │
               │ 计算生成
               ▼
┌───────────────────────────┐     ┌───────────────────────────────┐
│ concept_stock_daily_rank  │     │    concept_daily_summary      │
│───────────────────────────│     │───────────────────────────────│
│ concept_id (FK)           │     │ concept_id (FK)               │
│ stock_code / trade_date   │     │ metric_type_id (FK)           │
│ metric_type_id (FK)       │     │ trade_date                    │
│ trade_value / rank        │     │ total/avg/max/min_value       │
│ percentile                │     │ stock_count                   │
└───────────────────────────┘     └───────────────────────────────┘
```

---

## 3. 表结构详细设计

### 3.1 配置层

#### metric_types - 指标类型配置

```sql
CREATE TABLE metric_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,      -- TTV, EEE, EFV
    name VARCHAR(100) NOT NULL,            -- 显示名称
    description TEXT,
    file_pattern VARCHAR(100),             -- 文件匹配模式 *TTV*.txt
    rank_order VARCHAR(10) DEFAULT 'DESC', -- 排名顺序
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**初始数据**:
```sql
INSERT INTO metric_types (code, name, file_pattern) VALUES
('TTV', '交易总值', '*TTV*.txt'),
('EEE', '交易活跃度', '*EEE*.txt'),
('EFV', 'EFV指标', '*EFV*.txt'),
('AAA', 'AAA指标', '*AAA*.txt');
```

---

### 3.2 主数据层

#### stocks - 股票信息

```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) UNIQUE NOT NULL,  -- 纯代码：600000
    stock_name VARCHAR(100),
    exchange_prefix VARCHAR(10),              -- SH, SZ, BJ
    exchange_name VARCHAR(50),                -- 上海/深圳/北京
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stocks_code ON stocks(stock_code);
CREATE INDEX idx_stocks_exchange ON stocks(exchange_prefix);
```

**设计说明**:
- `stock_code`: 存储纯代码（去掉前缀）
- `exchange_prefix`: 单独存储前缀，便于统计分析

#### concepts - 概念

```sql
CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    concept_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),           -- 分类
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concepts_name ON concepts(concept_name);
```

#### industries - 行业

```sql
CREATE TABLE industries (
    id SERIAL PRIMARY KEY,
    industry_name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES industries(id),
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### stock_concepts - 股票-概念关系

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

#### stock_industries - 股票-行业关系

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

### 3.3 源数据层

#### import_batches - 导入批次

```sql
CREATE TABLE import_batches (
    id SERIAL PRIMARY KEY,

    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,           -- CSV, TXT
    metric_type_id INTEGER REFERENCES metric_types(id),
    file_size BIGINT,
    file_hash VARCHAR(64),                    -- SHA256防重复

    -- 数据日期
    data_date DATE,                           -- TXT文件的交易日期

    -- 导入状态
    status VARCHAR(20) DEFAULT 'pending',     -- pending/processing/completed/failed
    total_rows INTEGER DEFAULT 0,
    success_rows INTEGER DEFAULT 0,
    error_rows INTEGER DEFAULT 0,

    -- 计算状态
    compute_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,

    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

CREATE INDEX idx_import_batches_status ON import_batches(status);
CREATE INDEX idx_import_batches_date ON import_batches(data_date);
CREATE INDEX idx_import_batches_hash ON import_batches(file_hash);
```

#### stock_metric_data_raw - 原始交易数据（分区表）

```sql
CREATE TABLE stock_metric_data_raw (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 股票信息（分离前缀）
    stock_code_raw VARCHAR(30) NOT NULL,      -- 原始：SH600000
    stock_code VARCHAR(20) NOT NULL,          -- 纯码：600000
    exchange_prefix VARCHAR(10),              -- 前缀：SH

    -- 交易数据
    trade_date DATE NOT NULL,
    trade_value BIGINT NOT NULL,

    -- 元数据
    source_row_number INTEGER,
    raw_line TEXT,

    -- 状态
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 索引
CREATE INDEX idx_metric_raw_stock_date ON stock_metric_data_raw(stock_code, trade_date);
CREATE INDEX idx_metric_raw_metric_date ON stock_metric_data_raw(metric_type_id, trade_date);
CREATE INDEX idx_metric_raw_batch ON stock_metric_data_raw(import_batch_id);
```

#### stock_concept_mapping_raw - 原始映射数据

```sql
CREATE TABLE stock_concept_mapping_raw (
    id SERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL REFERENCES import_batches(id),

    -- 原始数据
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    concept_name VARCHAR(100),
    industry_name VARCHAR(100),

    -- 扩展字段
    extra_fields JSONB,
    source_row_number INTEGER,

    -- 状态
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mapping_raw_batch ON stock_concept_mapping_raw(import_batch_id);
CREATE INDEX idx_mapping_raw_stock ON stock_concept_mapping_raw(stock_code);
```

---

### 3.4 预计算层

#### concept_stock_daily_rank - 排名表（分区表）

```sql
CREATE TABLE concept_stock_daily_rank (
    id BIGSERIAL,

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 核心数据
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,

    -- 交易和排名
    trade_value BIGINT NOT NULL,
    rank INTEGER NOT NULL,
    total_stocks INTEGER,
    percentile DECIMAL(5, 2),

    -- 计算元数据
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id),

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 场景化索引
CREATE INDEX idx_rank_stock_concept_date
    ON concept_stock_daily_rank(stock_code, concept_id, trade_date);
CREATE INDEX idx_rank_concept_date_rank
    ON concept_stock_daily_rank(concept_id, trade_date, rank);
CREATE INDEX idx_rank_stock_concept_rank
    ON concept_stock_daily_rank(stock_code, concept_id, rank);

-- 唯一约束
CREATE UNIQUE INDEX idx_rank_unique
    ON concept_stock_daily_rank(metric_type_id, concept_id, stock_code, trade_date);
```

#### concept_daily_summary - 汇总表

```sql
CREATE TABLE concept_daily_summary (
    id SERIAL PRIMARY KEY,

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 核心数据
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    trade_date DATE NOT NULL,

    -- 汇总数据
    total_value BIGINT,
    avg_value BIGINT,
    max_value BIGINT,
    min_value BIGINT,
    stock_count INTEGER,
    median_value BIGINT,
    top10_sum BIGINT,

    -- 计算元数据
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_batch_id INTEGER REFERENCES import_batches(id),

    UNIQUE(metric_type_id, concept_id, trade_date)
);

CREATE INDEX idx_summary_concept_date ON concept_daily_summary(concept_id, trade_date);
CREATE INDEX idx_summary_metric_date ON concept_daily_summary(metric_type_id, trade_date);
```

---

## 4. 分区策略

### 4.1 分区设计

**按月分区**（适用于 stock_metric_data_raw 和 concept_stock_daily_rank）

```sql
-- 2025年分区示例
CREATE TABLE stock_metric_data_raw_2025_01
    PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE stock_metric_data_raw_2025_02
    PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
-- ... 依此类推
```

### 4.2 分区优势

- **查询优化**: 按日期查询时自动剪枝
- **维护简便**: 删除旧数据只需DROP分区
- **并行扫描**: 多分区可并行查询

### 4.3 自动分区函数

```sql
CREATE OR REPLACE FUNCTION create_monthly_partition(
    p_table_name TEXT,
    p_year INTEGER,
    p_month INTEGER
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := make_date(p_year, p_month, 1);
    end_date := start_date + INTERVAL '1 month';
    partition_name := p_table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, p_table_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 5. 索引设计

### 5.1 索引策略

| 表 | 索引 | 用途 |
|----|------|------|
| concept_stock_daily_rank | (stock_code, concept_id, trade_date) | 需求1/5：股票排名查询 |
| concept_stock_daily_rank | (concept_id, trade_date, rank) | 需求3：概念排名列表 |
| concept_stock_daily_rank | (stock_code, concept_id, rank) | 需求4：前N名统计 |
| concept_daily_summary | (concept_id, trade_date) | 需求2/6：概念汇总 |

### 5.2 索引与查询对应

```sql
-- 需求1/5：查询股票在概念中的排名
-- 使用索引：idx_rank_stock_concept_date
SELECT * FROM concept_stock_daily_rank
WHERE stock_code = '600000'
  AND concept_id = 1
  AND trade_date BETWEEN '2025-08-01' AND '2025-08-31';

-- 需求3：查询概念排名列表
-- 使用索引：idx_rank_concept_date_rank
SELECT * FROM concept_stock_daily_rank
WHERE concept_id = 1
  AND trade_date = '2025-08-21'
ORDER BY rank;

-- 需求4：统计前N名次数
-- 使用索引：idx_rank_stock_concept_rank
SELECT concept_id, COUNT(*)
FROM concept_stock_daily_rank
WHERE stock_code = '600000'
  AND rank <= 10
  AND trade_date BETWEEN '2025-08-01' AND '2025-08-31'
GROUP BY concept_id;
```

---

## 6. 数据量估算

### 6.1 假设条件

- 股票数：5000只
- 概念数：300个
- 平均每只股票属于5个概念
- 每年交易日：250天
- 指标类型：3种

### 6.2 年数据量

| 表 | 计算 | 年数据量 |
|----|------|---------|
| stock_metric_data_raw | 5000 × 250 × 3 | 375万行 |
| concept_stock_daily_rank | 5000 × 5 × 250 × 3 | 1875万行 |
| concept_daily_summary | 300 × 250 × 3 | 22.5万行 |

### 6.3 存储估算

| 表 | 单行大小 | 年存储 |
|----|---------|--------|
| stock_metric_data_raw | ~200B | ~750MB |
| concept_stock_daily_rank | ~100B | ~1.8GB |
| concept_daily_summary | ~100B | ~22MB |

---

## 7. 初始化脚本

完整建表脚本位置：`docs/sql/init_tables.sql`

使用方式：
```bash
psql -U postgres -d stock_analysis -f docs/sql/init_tables.sql
```

---

## 附录

### A. 字段类型说明

| 类型 | 用途 | 示例 |
|-----|------|------|
| VARCHAR(20) | 股票代码 | 600000 |
| VARCHAR(50) | 指标代码 | TTV |
| VARCHAR(100) | 名称 | 人工智能 |
| BIGINT | 交易金额 | 459400 |
| DATE | 交易日期 | 2025-08-21 |
| DECIMAL(5,2) | 百分比 | 95.50 |
| JSONB | 扩展字段 | {"extra": "data"} |

### B. 状态枚举

**import_batches.status**:
- pending: 等待处理
- processing: 处理中
- completed: 完成
- failed: 失败

**import_batches.compute_status**:
- pending: 等待计算
- computing: 计算中
- completed: 计算完成
- failed: 计算失败
