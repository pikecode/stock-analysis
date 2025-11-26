# 多指标汇总数据存储策略分析

**版本**: v1.0
**日期**: 2025-11-22
**问题**: 多个指标的汇总计算结果是放到一起还是单独存储？

---

## 🤔 问题分析

### 场景说明

我们有多种指标：TTV、EEE、EFV、AAA...

每种指标都需要计算：
- **排名数据**: 股票在概念中的排名
- **汇总数据**: 概念的总和、平均值、最大值等

**核心问题**: 这些汇总结果如何存储？

---

## 📊 三种存储方案对比

### 方案A: 统一表存储（推荐）⭐

**表结构**:
```sql
-- 所有指标的排名都存在这一个表
CREATE TABLE concept_metric_rank (
    id BIGSERIAL,
    concept_id INTEGER,
    stock_code VARCHAR(20),
    trade_date DATE,

    -- 指标标识
    metric_type_id INTEGER,
    metric_code VARCHAR(50),

    -- 通用排名字段
    value BIGINT,
    rank INTEGER,
    percentile DECIMAL(5, 2),

    -- 扩展字段（JSON）
    extra_metrics JSONB,  -- 存储指标特有的额外数据

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 所有指标的汇总都存在这一个表
CREATE TABLE concept_metric_summary (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER,
    trade_date DATE,

    -- 指标标识
    metric_type_id INTEGER,
    metric_code VARCHAR(50),

    -- 通用汇总字段
    total_value BIGINT,
    avg_value BIGINT,
    max_value BIGINT,
    min_value BIGINT,
    stock_count INTEGER,

    -- 扩展汇总字段（JSON）
    custom_aggregations JSONB,  -- 指标特有的汇总结果

    UNIQUE(concept_id, metric_type_id, trade_date)
);
```

**数据示例**:
```
concept_metric_summary 表:
┌────────────┬──────────┬────────────┬─────────────┬───────────┬──────────┬──────────────────────┐
│ concept_id │   date   │metric_code │ total_value │ avg_value │max_value │ custom_aggregations  │
├────────────┼──────────┼────────────┼─────────────┼───────────┼──────────┼──────────────────────┤
│     1      │2025-08-21│    TTV     │ 100,000,000 │  666,666  │10,000,000│ {"top10_sum": 50M}   │
│     1      │2025-08-21│    EEE     │  80,000,000 │  533,333  │ 8,000,000│ {"active_count": 80} │
│     1      │2025-08-21│    EFV     │  60,000,000 │  400,000  │ 6,000,000│ {"flow_rate": 0.75}  │
│     1      │2025-08-22│    TTV     │ 105,000,000 │  700,000  │11,000,000│ {"top10_sum": 52M}   │
└────────────┴──────────┴────────────┴─────────────┴───────────┴──────────┴──────────────────────┘
```

**优点**:
- ✅ **多指标对比超级简单**: 一个查询搞定
  ```sql
  SELECT metric_code, total_value, avg_value
  FROM concept_metric_summary
  WHERE concept_id = 1 AND trade_date = '2025-08-21'
  ORDER BY metric_code;
  ```
- ✅ **新增指标零成本**: 不需要创建新表，直接插入数据
- ✅ **统一管理**: 所有指标用同样的查询、备份、监控逻辑
- ✅ **表结构稳定**: 未来新增指标不影响表结构
- ✅ **跨指标分析方便**: JOIN一次就能拿到所有指标

**缺点**:
- ⚠️ 如果指标间差异很大，可能有些字段用不上
- ⚠️ 单表数据量较大（但可以通过分区解决）
- ⚠️ 查询单一指标时需要 WHERE metric_code = 'TTV'

**适用场景**:
- ✅ 指标间结构相似（都是股票交易类数据）
- ✅ 需要频繁的多指标对比
- ✅ 指标类型会持续增加

---

### 方案B: 分表存储

**表结构**:
```sql
-- TTV的排名表
CREATE TABLE concept_ttv_rank (
    id BIGSERIAL,
    concept_id INTEGER,
    stock_code VARCHAR(20),
    trade_date DATE,
    ttv_value BIGINT,
    rank INTEGER,
    percentile DECIMAL(5, 2),
    -- TTV特有字段
    ttv_top10_sum BIGINT,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- EEE的排名表
CREATE TABLE concept_eee_rank (
    id BIGSERIAL,
    concept_id INTEGER,
    stock_code VARCHAR(20),
    trade_date DATE,
    eee_value BIGINT,
    rank INTEGER,
    percentile DECIMAL(5, 2),
    -- EEE特有字段
    eee_active_count INTEGER,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- TTV的汇总表
CREATE TABLE concept_ttv_summary (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER,
    trade_date DATE,
    total_ttv BIGINT,
    avg_ttv BIGINT,
    max_ttv BIGINT,
    -- TTV特有汇总
    top10_ttv_sum BIGINT,
    UNIQUE(concept_id, trade_date)
);

-- EEE的汇总表
CREATE TABLE concept_eee_summary (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER,
    trade_date DATE,
    total_eee BIGINT,
    avg_eee BIGINT,
    max_eee BIGINT,
    -- EEE特有汇总
    active_stock_count INTEGER,
    UNIQUE(concept_id, trade_date)
);

-- 每增加一种指标（如EFV），就需要创建两个新表...
```

**优点**:
- ✅ **每种指标完全独立**: 字段可以完全不同
- ✅ **查询单一指标最快**: 不需要过滤 metric_code
- ✅ **数据隔离性好**: 一种指标的问题不影响其他指标
- ✅ **表结构清晰**: 每个表的含义明确

**缺点**:
- ❌ **多指标对比复杂**: 需要UNION或多次查询
  ```sql
  -- 查询多个指标需要UNION
  SELECT 'TTV' as metric, total_ttv as total FROM concept_ttv_summary WHERE ...
  UNION ALL
  SELECT 'EEE' as metric, total_eee as total FROM concept_eee_summary WHERE ...
  UNION ALL
  SELECT 'EFV' as metric, total_efv as total FROM concept_efv_summary WHERE ...
  ```
- ❌ **新增指标成本高**: 需要创建新表、新索引、新分区
- ❌ **管理复杂**: 每种指标的备份、监控、维护都要单独处理
- ❌ **代码重复**: 每种指标需要单独的查询代码

**适用场景**:
- ✅ 指标间差异巨大（完全不同的数据结构）
- ✅ 很少需要多指标对比
- ✅ 指标类型固定，不会频繁增加

---

### 方案C: 混合存储（平衡方案）

**核心思想**: 通用字段统一表 + 特有字段分表

**表结构**:
```sql
-- 基础汇总表（所有指标共用）
CREATE TABLE concept_metric_summary_base (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER,
    trade_date DATE,
    metric_type_id INTEGER,
    metric_code VARCHAR(50),

    -- 通用汇总字段（所有指标都有的）
    total_value BIGINT,
    avg_value BIGINT,
    max_value BIGINT,
    min_value BIGINT,
    stock_count INTEGER,

    UNIQUE(concept_id, metric_type_id, trade_date)
);

-- TTV特有汇总表（可选）
CREATE TABLE concept_ttv_summary_ext (
    id SERIAL PRIMARY KEY,
    base_summary_id INTEGER REFERENCES concept_metric_summary_base(id),

    -- TTV特有的汇总字段
    top10_sum BIGINT,
    top20_sum BIGINT,
    weighted_avg DECIMAL(15, 2),

    UNIQUE(base_summary_id)
);

-- EEE特有汇总表（可选）
CREATE TABLE concept_eee_summary_ext (
    id SERIAL PRIMARY KEY,
    base_summary_id INTEGER REFERENCES concept_metric_summary_base(id),

    -- EEE特有的汇总字段
    active_count INTEGER,
    activity_score DECIMAL(10, 2),

    UNIQUE(base_summary_id)
);
```

**查询示例**:
```sql
-- 多指标对比（只查基础字段）
SELECT metric_code, total_value, avg_value
FROM concept_metric_summary_base
WHERE concept_id = 1 AND trade_date = '2025-08-21';

-- 查询TTV的详细数据（包含特有字段）
SELECT
    b.*,
    t.top10_sum,
    t.top20_sum,
    t.weighted_avg
FROM concept_metric_summary_base b
LEFT JOIN concept_ttv_summary_ext t ON b.id = t.base_summary_id
WHERE b.metric_code = 'TTV'
  AND b.concept_id = 1
  AND b.trade_date = '2025-08-21';
```

**优点**:
- ✅ 兼具两种方案的优点
- ✅ 基础对比简单（用基础表）
- ✅ 详细查询灵活（JOIN扩展表）
- ✅ 如果指标没有特殊字段，不需要创建扩展表

**缺点**:
- ⚠️ 复杂度增加（两层表）
- ⚠️ 查询需要JOIN（性能略低）
- ⚠️ 有特殊字段的指标仍需创建扩展表

**适用场景**:
- ✅ 指标间有共同字段，也有特殊字段
- ✅ 需要在对比和详查之间平衡
- ✅ 部分指标有复杂的特殊需求

---

## 🎯 推荐方案

### 基于你的场景分析

**你的数据特点**:
1. TTV.txt、EEE.txt、EFV.txt 都是股票交易相关数据
2. 文件格式相似（都是：股票代码 + 日期 + 数值）
3. 汇总逻辑相似（都需要求和、平均、最大值等）
4. 未来会持续新增指标类型
5. 需要多指标对比分析

### 推荐：**方案A（统一表）+ JSONB扩展字段** ⭐⭐⭐⭐⭐

**理由**:
1. ✅ 你的指标结构高度相似，适合统一存储
2. ✅ 需要频繁的多指标对比（概念热度分析）
3. ✅ 指标类型会持续增加（EFV、AAA...）
4. ✅ JSONB字段可以满足特殊汇总需求
5. ✅ PostgreSQL的JSONB性能很好，可以建索引

### 具体实现方案

#### 表结构设计

```sql
-- 排名数据表
CREATE TABLE concept_metric_rank (
    id BIGSERIAL,
    concept_id INTEGER NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,

    -- 指标标识
    metric_type_id INTEGER NOT NULL,
    metric_code VARCHAR(50) NOT NULL,

    -- 核心排名字段（所有指标都有）
    value BIGINT,                     -- 主要数值
    rank INTEGER,                     -- 排名
    percentile DECIMAL(5, 2),        -- 百分位

    -- 扩展字段（JSON，存储指标特有的计算结果）
    extra_metrics JSONB DEFAULT '{}',

    -- 元数据
    computed_at TIMESTAMP,
    computation_version VARCHAR(20),

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 索引
CREATE INDEX idx_concept_metric_rank_main
    ON concept_metric_rank(concept_id, metric_type_id, trade_date, rank);

CREATE INDEX idx_concept_metric_rank_stock
    ON concept_metric_rank(stock_code, metric_type_id, trade_date);

-- JSONB索引（如果需要查询扩展字段）
CREATE INDEX idx_concept_metric_rank_extra
    ON concept_metric_rank USING GIN (extra_metrics);

-- 汇总数据表
CREATE TABLE concept_metric_summary (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER NOT NULL,
    trade_date DATE NOT NULL,

    -- 指标标识
    metric_type_id INTEGER NOT NULL,
    metric_code VARCHAR(50) NOT NULL,

    -- 核心汇总字段（所有指标都有）
    total_value BIGINT,              -- 总和
    avg_value BIGINT,                -- 平均值
    max_value BIGINT,                -- 最大值
    min_value BIGINT,                -- 最小值
    stock_count INTEGER,             -- 股票数量

    -- 扩展汇总字段（JSON，存储指标特有的汇总）
    custom_aggregations JSONB DEFAULT '{}',

    -- 元数据
    computed_at TIMESTAMP,
    computation_version VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(concept_id, metric_type_id, trade_date)
);

-- 索引
CREATE INDEX idx_concept_metric_summary_main
    ON concept_metric_summary(concept_id, metric_type_id, trade_date);

CREATE INDEX idx_concept_metric_summary_date
    ON concept_metric_summary(trade_date, metric_type_id);

-- JSONB索引
CREATE INDEX idx_concept_metric_summary_custom
    ON concept_metric_summary USING GIN (custom_aggregations);
```

#### 数据存储示例

```sql
-- TTV指标的汇总数据
INSERT INTO concept_metric_summary VALUES (
    1,                    -- id
    1,                    -- concept_id (人工智能)
    '2025-08-21',        -- trade_date
    1,                    -- metric_type_id (TTV)
    'TTV',               -- metric_code
    100000000,           -- total_value
    666666,              -- avg_value
    10000000,            -- max_value
    50000,               -- min_value
    150,                 -- stock_count
    '{
        "top10_sum": 50000000,
        "top20_sum": 75000000,
        "median": 600000,
        "std_dev": 1500000
    }'::jsonb,          -- custom_aggregations
    NOW(),              -- computed_at
    'v1.0'              -- computation_version
);

-- EEE指标的汇总数据
INSERT INTO concept_metric_summary VALUES (
    2,
    1,                   -- 同一个概念
    '2025-08-21',       -- 同一天
    2,                   -- metric_type_id (EEE)
    'EEE',
    80000000,
    533333,
    8000000,
    40000,
    150,
    '{
        "active_count": 80,
        "inactive_count": 70,
        "activity_rate": 0.53,
        "peak_hour": 14
    }'::jsonb,          -- EEE特有的汇总
    NOW(),
    'v1.0'
);
```

#### 查询示例

**1. 多指标对比（超简单）**:
```sql
-- 查询人工智能概念在2025-08-21的所有指标汇总
SELECT
    metric_code,
    total_value,
    avg_value,
    max_value,
    stock_count
FROM concept_metric_summary
WHERE concept_id = 1
  AND trade_date = '2025-08-21'
ORDER BY metric_code;

-- 结果:
-- TTV | 100000000 | 666666 | 10000000 | 150
-- EEE |  80000000 | 533333 |  8000000 | 150
-- EFV |  60000000 | 400000 |  6000000 | 150
```

**2. 查询TTV特有的汇总字段**:
```sql
-- 查询TTV的top10_sum
SELECT
    metric_code,
    total_value,
    custom_aggregations->>'top10_sum' as top10_sum,
    custom_aggregations->>'median' as median
FROM concept_metric_summary
WHERE concept_id = 1
  AND metric_code = 'TTV'
  AND trade_date = '2025-08-21';

-- 结果:
-- TTV | 100000000 | 50000000 | 600000
```

**3. 多指标趋势对比**:
```sql
-- 查询过去30天的TTV和EEE趋势
SELECT
    trade_date,
    MAX(CASE WHEN metric_code = 'TTV' THEN total_value END) as ttv_total,
    MAX(CASE WHEN metric_code = 'EEE' THEN total_value END) as eee_total
FROM concept_metric_summary
WHERE concept_id = 1
  AND trade_date >= CURRENT_DATE - INTERVAL '30 days'
  AND metric_code IN ('TTV', 'EEE')
GROUP BY trade_date
ORDER BY trade_date;
```

**4. JSONB字段查询和索引**:
```sql
-- 查询所有top10_sum > 40000000的概念
SELECT
    concept_id,
    metric_code,
    total_value,
    custom_aggregations->>'top10_sum' as top10_sum
FROM concept_metric_summary
WHERE metric_code = 'TTV'
  AND (custom_aggregations->>'top10_sum')::BIGINT > 40000000
  AND trade_date = '2025-08-21';

-- 这个查询会使用GIN索引
```

---

## 📊 性能对比

### 存储空间对比

**方案A（统一表）**:
```
假设有3种指标（TTV, EEE, EFV），1000个概念，365天数据

concept_metric_summary:
  3 × 1000 × 365 = 1,095,000 行

每行约 300 bytes (包含JSONB)
总计: ~329 MB
```

**方案B（分表）**:
```
concept_ttv_summary: 1000 × 365 = 365,000 行
concept_eee_summary: 1000 × 365 = 365,000 行
concept_efv_summary: 1000 × 365 = 365,000 行

每行约 250 bytes
总计: ~273 MB

但需要管理3个表
```

**结论**: 存储空间差异不大（~20%），但方案A管理更简单

### 查询性能对比

| 查询类型 | 方案A（统一表） | 方案B（分表） | 胜出 |
|---------|----------------|--------------|------|
| 单指标查询 | WHERE metric_code='TTV' | SELECT FROM ttv_table | 方案B略优 |
| 多指标对比 | 一次查询 | UNION或多次查询 | **方案A大幅领先** |
| 跨指标分析 | 一次JOIN | 多表JOIN/UNION | **方案A领先** |
| 插入性能 | 同一个表 | 分散到多个表 | 相近 |

**结论**: 方案A在多指标对比场景下性能明显更好

---

## 💡 最佳实践

### 使用统一表时的注意事项

#### 1. JSONB字段设计规范

```json
// 推荐的JSONB结构
{
  // 使用清晰的键名
  "top10_sum": 50000000,
  "top20_sum": 75000000,

  // 复杂对象也可以
  "distribution": {
    "0-1M": 50,
    "1M-10M": 80,
    "10M+": 20
  },

  // 数组也支持
  "top_stocks": ["600000", "000001", "000002"]
}

// 避免的结构
{
  "field1": xxx,  // 键名不明确
  "data": {...}   // 太宽泛
}
```

#### 2. 索引策略

```sql
-- 主要查询索引
CREATE INDEX idx_main
ON concept_metric_summary(concept_id, metric_type_id, trade_date);

-- 如果经常按metric_code查询
CREATE INDEX idx_metric_code
ON concept_metric_summary(metric_code, trade_date);

-- 如果需要查询JSONB中的特定字段
CREATE INDEX idx_custom_top10
ON concept_metric_summary((custom_aggregations->>'top10_sum'));
```

#### 3. 分区策略

```sql
-- 按日期分区（推荐按月）
CREATE TABLE concept_metric_summary_2025_08
PARTITION OF concept_metric_summary
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

-- 优点：
-- 1. 查询历史数据时只扫描相关分区
-- 2. 可以方便地归档旧分区
-- 3. 删除历史数据很快（DROP PARTITION）
```

#### 4. 数据一致性保证

```python
async def save_metric_summary(
    concept_id: int,
    metric_type: MetricType,
    date: date,
    summary_data: dict
):
    """
    保存指标汇总数据

    使用UPSERT确保数据一致性
    """
    sql = """
    INSERT INTO concept_metric_summary (
        concept_id, metric_type_id, metric_code, trade_date,
        total_value, avg_value, max_value, min_value, stock_count,
        custom_aggregations, computed_at, computation_version
    )
    VALUES (:concept_id, :metric_type_id, :metric_code, :date,
            :total, :avg, :max, :min, :count,
            :custom, NOW(), :version)
    ON CONFLICT (concept_id, metric_type_id, trade_date)
    DO UPDATE SET
        total_value = EXCLUDED.total_value,
        avg_value = EXCLUDED.avg_value,
        max_value = EXCLUDED.max_value,
        min_value = EXCLUDED.min_value,
        stock_count = EXCLUDED.stock_count,
        custom_aggregations = EXCLUDED.custom_aggregations,
        computed_at = NOW(),
        computation_version = EXCLUDED.computation_version;
    """
```

---

## 🎯 实施建议

### Phase 1: 基础实现

```sql
1. 创建 concept_metric_summary 表
2. 实现基础汇总功能（sum, avg, max, min）
3. 测试TTV和EEE两种指标
```

### Phase 2: 扩展字段

```sql
1. 添加 custom_aggregations JSONB字段
2. 实现TTV的特殊汇总（top10_sum等）
3. 实现EEE的特殊汇总（active_count等）
```

### Phase 3: 性能优化

```sql
1. 创建JSONB索引
2. 分析慢查询
3. 调整索引策略
```

### Phase 4: 新增指标

```sql
1. 添加EFV指标配置
2. 导入EFV数据
3. 验证自动汇总
```

---

## ✅ 最终建议

**强烈推荐使用方案A（统一表 + JSONB扩展）**

**理由总结**:
1. ✅ 你的场景非常适合（指标相似、需要对比、持续扩展）
2. ✅ 开发效率高（一套代码处理所有指标）
3. ✅ 查询性能好（多指标对比只需一次查询）
4. ✅ 扩展性强（新增指标零成本）
5. ✅ PostgreSQL的JSONB性能优秀（支持索引、支持复杂查询）
6. ✅ 维护成本低（一个表vs多个表）

**何时考虑方案B（分表）**:
- ❌ 如果各指标结构完全不同（例如：一个是交易数据，一个是文本分析）
- ❌ 如果几乎不需要多指标对比
- ❌ 如果指标类型固定且数量很少

**何时考虑方案C（混合）**:
- ⚠️ 如果某些指标的扩展字段非常多（>10个）
- ⚠️ 如果需要在扩展字段上做复杂的聚合查询
- ⚠️ 如果对查询性能要求极高

**对于你的场景，方案A是最优选择！** ⭐
