# 数据库设计文档

## 目录
1. [数据库架构概述](#数据库架构概述)
2. [核心表设计](#核心表设计)
3. [数据流向](#数据流向)
4. [计算逻辑](#计算逻辑)
5. [关键概念解释](#关键概念解释)
6. [查询示例](#查询示例)

---

## 数据库架构概述

### 表分类

本系统采用分层设计，分为三层：

```
┌─────────────────────────────────────────────────┐
│ 用户认证系统                                     │
│ (users, roles, permissions, user_roles,         │
│  role_permissions)                              │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 主数据管理                                       │
│ (stocks, concepts, industries, stock_concepts,  │
│  stock_industries, metric_types)                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 数据导入和处理                                   │
│ (import_batches, stock_metric_data_raw)         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 预计算数据（用于查询优化）                       │
│ (concept_stock_daily_rank,                      │
│  concept_daily_summary)                         │
└─────────────────────────────────────────────────┘
```

### 数据库连接信息

- **开发环境**：PostgreSQL
- **位置**：`.env` 文件中配置 `DATABASE_URL`
- **当前配置**：`postgresql://postgres@localhost:5432/stock_analysis`

---

## 核心表设计

### 1. 用户认证系统

#### users（用户表）
存储用户账号信息，支持多角色。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| username | VARCHAR(50) | 用户名 | UNIQUE, NOT NULL |
| email | VARCHAR(100) | 邮箱 | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | 密码哈希 | NOT NULL |
| phone | VARCHAR(20) | 电话 | - |
| avatar_url | VARCHAR(255) | 头像URL | - |
| status | VARCHAR(20) | 状态 | 默认 'active' |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |
| last_login_at | TIMESTAMP | 最后登录时间 | - |

**关系**：多对多 → roles（通过 user_roles 表）

#### roles（角色表）
定义系统中的角色。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| name | VARCHAR(50) | 角色代码 | UNIQUE, NOT NULL |
| display_name | VARCHAR(100) | 角色显示名 | NOT NULL |
| description | VARCHAR(255) | 角色描述 | - |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

**系统内置角色**：
- `admin` - 管理员，全系统访问权限
- `customer` - 客户，访问分析报表和个人功能
- `public` - 公开用户，只读访问公开数据

#### permissions（权限表）
细粒度权限定义。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| code | VARCHAR(100) | 权限代码 | UNIQUE, NOT NULL |
| name | VARCHAR(100) | 权限名称 | UNIQUE, NOT NULL |
| resource | VARCHAR(50) | 资源名 | NOT NULL |
| action | VARCHAR(20) | 操作（read/write/delete） | NOT NULL |
| description | VARCHAR(255) | 权限描述 | - |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

**例子**：
- code: `stocks.read`, resource: `stocks`, action: `read` → 查看股票
- code: `imports.write`, resource: `imports`, action: `write` → 上传数据

#### user_roles（用户-角色关联）
多对多关系表。

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INTEGER | 用户ID (FK) |
| role_id | INTEGER | 角色ID (FK) |

#### role_permissions（角色-权限关联）
多对多关系表。

| 字段 | 类型 | 说明 |
|------|------|------|
| role_id | INTEGER | 角色ID (FK) |
| permission_id | INTEGER | 权限ID (FK) |

---

### 2. 主数据管理

#### stocks（股票表）
存储所有上市公司股票的基本信息。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| stock_code | VARCHAR(20) | 股票代码 | UNIQUE, NOT NULL |
| stock_name | VARCHAR(100) | 股票名称 | - |
| exchange_prefix | VARCHAR(10) | 交易所前缀 | SH/SZ/BJ |
| exchange_name | VARCHAR(50) | 交易所名称 | - |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

**索引**：stock_code, exchange_prefix

**例子**：
```
stock_code=600000, stock_name=浦发银行, exchange_prefix=SH
stock_code=000001, stock_name=平安银行, exchange_prefix=SZ
```

#### concepts（概念/板块表）
存储股票概念分类（也称"板块"、"题材"）。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| concept_name | VARCHAR(100) | 概念名称 | UNIQUE, NOT NULL |
| category | VARCHAR(50) | 分类 | - |
| description | TEXT | 概念描述 | - |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

**索引**：concept_name

**例子**：
```
concept_name=银行, category=金融
concept_name=AI概念, category=科技
concept_name=沪股通, category=交易制度
```

#### stock_concepts（股票-概念关联）
多对多关系：一只股票可属于多个概念，一个概念可包含多只股票。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| stock_code | VARCHAR(20) | 股票代码 | FK → stocks |
| concept_id | INTEGER | 概念ID | FK → concepts |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

**索引**：stock_code, concept_id

**例子**：
```
600000 (浦发银行) → 银行、上海板块、融资融券
000001 (平安银行) → 银行、深圳板块、券商概念
```

#### industries（行业表）
存储行业分类，支持树形结构。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| industry_name | VARCHAR(100) | 行业名称 | UNIQUE, NOT NULL |
| parent_id | INTEGER | 父行业ID | FK → industries |
| level | INTEGER | 层级 | 默认 1 |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

**例子**：
```
金融(parent_id=NULL, level=1)
  └─ 银行(parent_id=金融, level=2)
  └─ 保险(parent_id=金融, level=2)
```

#### stock_industries（股票-行业关联）

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| stock_code | VARCHAR(20) | 股票代码 | FK → stocks |
| industry_id | INTEGER | 行业ID | FK → industries |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

#### metric_types（指标类型表）
定义系统支持的指标类型和其处理规则。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| code | VARCHAR(50) | 指标代码 | UNIQUE, NOT NULL |
| name | VARCHAR(100) | 指标名称 | NOT NULL |
| description | TEXT | 指标说明 | - |
| file_pattern | VARCHAR(100) | 数据文件匹配模式 | 如：`EEE_*.txt` |
| field_mapping | JSON | 字段映射配置 | - |
| rank_order | VARCHAR(10) | 排序顺序 | DESC/ASC，默认 DESC |
| is_active | BOOLEAN | 是否启用 | 默认 true |
| sort_order | INTEGER | 显示顺序 | 默认 0 |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

**内置指标**：
- EEE - 行业活跃度（数据来自EEE指标文件）
- TTV - 交易交易量（数据来自TTV指标文件）
- TOP - Top指标（其他统计指标）

---

### 3. 数据导入和处理

#### import_batches（导入批次表）
追踪每次数据文件导入的状态和结果。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| file_name | VARCHAR(255) | 原始文件名 | NOT NULL |
| file_type | VARCHAR(20) | 文件类型 | CSV/TXT |
| metric_type_id | INTEGER | 指标类型ID | FK → metric_types |
| file_size | BIGINT | 文件大小（字节） | - |
| file_hash | VARCHAR(64) | 文件哈希值 | 用于去重 |
| data_date | DATE | 数据所属日期 | 如：2025-11-04 |
| status | VARCHAR(20) | 导入状态 | pending/processing/success/failed |
| total_rows | INTEGER | 总行数 | 默认 0 |
| success_rows | INTEGER | 成功行数 | 默认 0 |
| error_rows | INTEGER | 失败行数 | 默认 0 |
| compute_status | VARCHAR(20) | 计算状态 | pending/computing/completed/failed |
| error_message | TEXT | 错误信息 | - |
| started_at | TIMESTAMP | 开始时间 | - |
| completed_at | TIMESTAMP | 完成时间 | - |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |
| created_by | INTEGER | 创建用户ID | FK → users |

**索引**：status, compute_status, data_date, file_hash

**导入流程**：
```
1. pending → 等待处理
2. processing → 正在导入
3. success + compute_status: pending → 导入完成，等待计算排名和汇总
4. compute_status: computing → 正在计算
5. compute_status: completed → 计算完成，数据可用
```

#### stock_metric_data_raw（原始指标数据表）
存储从文件导入的原始指标数据，是所有计算的数据源。

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | BIGINT | 主键 | PK |
| import_batch_id | INTEGER | 所属导入批次 | FK → import_batches |
| metric_type_id | INTEGER | 指标类型 | FK → metric_types |
| metric_code | VARCHAR(50) | 指标代码 | 如：EEE, TTV |
| stock_code_raw | VARCHAR(30) | 原始股票代码 | 导入时的原始值 |
| stock_code | VARCHAR(20) | 标准化股票代码 | NOT NULL |
| exchange_prefix | VARCHAR(10) | 交易所前缀 | - |
| trade_date | DATE | 交易日期 | NOT NULL |
| trade_value | BIGINT | 指标值 | NOT NULL |
| source_row_number | INTEGER | 源文件行号 | 用于问题追踪 |
| raw_line | TEXT | 原始行数据 | 保存完整原始数据 |
| is_valid | BOOLEAN | 是否有效 | 默认 true |
| validation_errors | JSON | 验证错误信息 | - |
| created_at | TIMESTAMP | 创建时间 | 默认当前时间 |

**索引**：stock_code, trade_date, metric_code, import_batch_id

**重要说明**：这是所有计算的**源数据**
- `trade_value` 是股票在该日期的原始指标值
- 不同股票的值通常**不同**
- 这个表的数据不会被直接查询（通过预计算表查询）

---

### 4. 预计算数据表（用于API查询）

这两个表是通过 `compute_service.py` 从 `stock_metric_data_raw` 计算生成，用于快速查询。

#### concept_stock_daily_rank（概念-股票-日排名表）
**用途**：存储每只股票在每个概念内的日排名

**核心设计理念**：
- **一行 = 一只股票在一个概念内一天的排名信息**
- 同一股票在同一天的不同概念中排名可能不同

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | BIGINT | 主键 | PK |
| metric_type_id | INTEGER | 指标类型 | FK → metric_types |
| metric_code | VARCHAR(50) | 指标代码 | 如：EEE, TTV |
| concept_id | INTEGER | 概念ID | FK → concepts |
| stock_code | VARCHAR(20) | 股票代码 | NOT NULL |
| trade_date | DATE | 交易日期 | NOT NULL |
| trade_value | BIGINT | 股票的指标值 | ⚠️ 来自stock_metric_data_raw |
| rank | INTEGER | 排名 | 在该概念内的排名位置 |
| computed_at | TIMESTAMP | 计算时间 | 默认当前时间 |
| import_batch_id | INTEGER | 所属导入批次 | FK → import_batches |

**索引**：concept_id, stock_code, trade_date, metric_code

**关键理解**：
- `trade_value` = 股票本身的指标值（不是"在概念下的交易量"）
- `rank` = 该股票在该概念内的排名（相同的trade_value会同时排名）
- 例如：600000在"银行"概念下的EEE排名是13，但600000的trade_value值1137952是它本身的EEE指标值，与其他股票无关

**计算SQL**（来自 `compute_service.py`）：
```sql
INSERT INTO concept_stock_daily_rank (...)
SELECT
    r.metric_type_id,
    r.metric_code,
    sc.concept_id,
    r.stock_code,
    r.trade_date,
    r.trade_value,  -- ⚠️ 直接取自stock_metric_data_raw
    DENSE_RANK() OVER (
        PARTITION BY r.metric_type_id, sc.concept_id, r.trade_date
        ORDER BY r.trade_value DESC
    ) as rank
FROM stock_metric_data_raw r
JOIN stock_concepts sc ON r.stock_code = sc.stock_code
WHERE r.import_batch_id = :batch_id AND r.is_valid = true
```

#### concept_daily_summary（概念-日汇总表）
**用途**：存储每个概念在每天的聚合统计数据

**核心设计理念**：
- **一行 = 一个概念在一天的汇总数据**
- 包含该概念在导入数据中有记录的股票的聚合统计：总值、均值、最大值、最小值等
- ⚠️ **注意**：概念包含的股票数由 `stock_concepts` 表管理（主数据），不在此表存储

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PK |
| metric_type_id | INTEGER | 指标类型 | FK → metric_types |
| metric_code | VARCHAR(50) | 指标代码 | 如：EEE, TTV |
| concept_id | INTEGER | 概念ID | FK → concepts |
| trade_date | DATE | 交易日期 | NOT NULL |
| **total_value** | BIGINT | **该日期有数据的所有股票的trade_value总和** | SUM(trade_value) |
| **avg_value** | BIGINT | **平均值** | AVG(trade_value) |
| **max_value** | BIGINT | **最大值** | MAX(trade_value) |
| **min_value** | BIGINT | **最小值** | MIN(trade_value) |
| **median_value** | BIGINT | **中位数** | PERCENTILE_CONT(0.5) |
| **top10_sum** | BIGINT | **前10只股票的trade_value总和** | 单独计算 |
| computed_at | TIMESTAMP | 计算时间 | 默认当前时间 |
| import_batch_id | INTEGER | 所属导入批次 | FK → import_batches |

**索引**：concept_id, trade_date, metric_code

**实际例子**（2025-11-04 EEE指标 银行概念）：
```
total_value: 42,408,691  -- 该日期有数据的股票的EEE值总和
avg_value: 986,248       -- 平均值
max_value: 5,140,764     -- 最高的股票值
min_value: 44,659        -- 最低的股票值
median_value: 441,832    -- 中间值
top10_sum: 26,908,249    -- 排名前10的股票值总和
```

**设计决策**：

早期版本在此表中存储了 `stock_count`（该日期有数据的股票数），但这造成了设计问题：
- ❌ 违反数据库范式（概念的股票数是静态的主数据，不应该在日汇总表中）
- ❌ 造成语义混淆（两个不同的"股票数"：概念包含数 vs. 该日期有数据的股票数）
- ✅ **改进方案**：概念包含的股票数总是从 `stock_concepts` 表查询

**计算SQL**（来自 `compute_service.py` 第90-126行）：
```sql
INSERT INTO concept_daily_summary (
    metric_type_id, metric_code, concept_id, trade_date,
    total_value, avg_value, max_value, min_value,
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
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.trade_value)::BIGINT as median_value,
    :batch_id as import_batch_id
FROM stock_metric_data_raw r
JOIN stock_concepts sc ON r.stock_code = sc.stock_code
WHERE r.import_batch_id = :batch_id AND r.is_valid = true
GROUP BY r.metric_type_id, r.metric_code, sc.concept_id, r.trade_date
```

top10_sum 单独计算。

---

## 数据流向

### 完整的数据处理流程

```
┌──────────────────────────┐
│  用户上传数据文件         │
│  (EEE_20251104.txt)      │
└──────────────┬───────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  导入处理 (optimized_txt_import.py)  │
│  1. 解析文件内容                      │
│  2. 验证数据格式                      │
│  3. 标准化股票代码                    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  保存到 import_batches               │
│  status: pending → processing        │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  插入 stock_metric_data_raw          │
│  • 原始股票代码: 600000              │
│  • 标准化股票代码: 600000            │
│  • trade_value: 1137952              │
│  • 其他字段: 指标代码、日期等        │
│  status: success                     │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  计算排名和汇总 (compute_service.py) │
│  compute_status: pending → computing │
└──────────────┬───────────────────────┘
               │
         ┌─────┴─────┐
         │           │
         ▼           ▼
    ┌────────────┐ ┌────────────┐
    │ 计算排名   │ │ 计算汇总   │
    └────────────┘ └────────────┘
         │           │
    1. JOIN stock_│   1. SUM(trade_value)
       concepts  │   2. AVG(trade_value)
    2. DENSE_RANK│   3. MAX/MIN/MEDIAN
       按trade_v│   4. COUNT(stocks)
       alue排序 │
         │           │
         ▼           ▼
    ┌────────────────────────┐
    │ concept_stock_         │
    │ daily_rank             │
    │ (600000在"银行"概念   │
    │  的排名=13)            │
    └────────────────────────┘

    ┌────────────────────────┐
    │ concept_daily_         │
    │ summary                │
    │ (银行概念总统计：      │
    │  43只股票，总值等)     │
    └────────────────────────┘
         │           │
         └─────┬─────┘
               │
               ▼
    ┌──────────────────────┐
    │ 前端API查询使用      │
    │ 这两个预计算表       │
    └──────────────────────┘
```

### 关键数据点连接

```
stocks (股票信息)
  ↓
stock_concepts (关联概念)
  ↓
stock_metric_data_raw (原始指标数据)
  │
  ├─→ concept_stock_daily_rank (排名)
  │   用途: 查询特定股票在概念内的排名
  │   API: GET /api/v1/stocks/{code}/concepts-ranked
  │
  └─→ concept_daily_summary (汇总)
      用途: 查询概念的整体统计
      API: GET /api/v1/concepts/{id}/summaries
```

---

## 计算逻辑

### 排名计算（DENSE_RANK）

**目的**：计算每只股票在其所属每个概念内的排名

**关键特性**：
- 使用 DENSE_RANK()，不留空隙排名（即使有并列也连续）
- 按 `trade_value` 降序排列（大值排名靠前）
- 分组维度：(metric_code, concept_id, trade_date)

**例子**（银行概念 2025-11-04 EEE指标）：

```
trade_value排序：
5140764 → rank 1   (平安、其他高值)
...
1137952 → rank 13  (浦发银行)
...
44659   → rank 43  (最低)

### 汇总计算（Aggregation）

**目的**：统计每个概念的整体情况

**计算字段**：

1. **total_value**
   ```
   = SUM(所有股票的trade_value)
   例：43只银行股票的EEE值之和 = 42,408,691
   ```

2. **avg_value**
   ```
   = AVG(所有股票的trade_value)
   例：42,408,691 / 43 ≈ 986,248
   ```

3. **stock_count**
   ```
   = COUNT(股票数)
   例：银行概念有43只股票
   ```

4. **max_value / min_value**
   ```
   = MAX/MIN(所有股票的trade_value)
   ```

5. **median_value**
   ```
   = PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY trade_value)
   = 中间位置的值（无论几只股票）
   ```

6. **top10_sum**
   ```
   = SUM(排名前10的股票的trade_value)
   例：26,908,249（前10只银行股票的值之和）
   ```

---

## 关键概念解释

### 1. trade_value 的含义

**常见误解**：
- ❌ trade_value = "股票在概念下的交易量"
- ❌ trade_value = "概念的交易量"

**正确理解**：
- ✅ trade_value = **股票本身在该指标下的原始值**
- 来源：stock_metric_data_raw 表中的原始数据
- 与概念无关，是股票的全局属性

**为什么同一股票在不同概念下的 trade_value 相同？**

因为 `trade_value` 来自原始数据，是股票的属性，不是概念的属性：

```
600000 (浦发银行) EEE值 = 1137952 (这是全局值)

在"银行"概念内：rank=13, trade_value=1137952
在"上海板块"概念内：rank=12, trade_value=1137952 (相同)
在"融资融券"概念内：rank=81, trade_value=1137952 (相同)

相同的原因：同一天同一指标，这个股票只有一个 trade_value 值
```

### 2. 概念（Concept）vs 行业（Industry）

| 特性 | 概念 | 行业 |
|------|------|------|
| 定义 | 灵活的题材分类 | 标准的行业分类 |
| 结构 | 平坦或简单分层 | 树形多层级 |
| 变化 | 常变（追踪热点） | 相对稳定 |
| 用途 | 投资分析、选股 | 宏观分析、行业对比 |
| 例子 | AI概念、沪股通、转债标的 | 金融→银行、制造→汽车 |
| 关联表 | stock_concepts | stock_industries |

### 3. 指标类型（Metric Type）

不同的指标文件提供不同的数据维度：

| 指标代码 | 指标名称 | 文件模式 | 说明 |
|---------|---------|---------|------|
| EEE | 行业活跃度 | `EEE_*.txt` | 衡量行业/概念的活跃程度 |
| TTV | 交易交易量 | `TTV_*.txt` | 衡量成交量相关指标 |
| TOP | Top指标 | `TOP_*.txt` | 其他统计指标 |

同一支股票在同一天可能有多个指标值：
```
600000 2025-11-04:
  EEE = 1137952
  TTV = 999999
  TOP = 888888
```

### 4. 导入流程的两个关键阶段

**阶段1：数据导入（status）**
```
pending → processing → success (数据保存到stock_metric_data_raw)
```

**阶段2：计算处理（compute_status）**
```
pending → computing → completed (计算排名和汇总)
```

只有 compute_status = completed 的数据才能被 API 查询。

---

## 查询示例

### 查询1：获取某股票在某概念的排名

**需求**：查询600000在"银行"概念2025-11-04 EEE指标的排名

```sql
SELECT
    c.concept_name,
    r.stock_code,
    r.rank,
    r.trade_value
FROM concept_stock_daily_rank r
JOIN concepts c ON r.concept_id = c.id
WHERE r.stock_code = '600000'
  AND c.concept_name = '银行'
  AND r.trade_date = '2025-11-04'
  AND r.metric_code = 'EEE';
```

**结果**：
```
concept_name | stock_code | rank | trade_value
银行         | 600000     | 13   | 1137952
```

### 查询2：获取概念的汇总统计

**需求**：获取"银行"概念2025-11-04 EEE指标的统计数据

```sql
SELECT
    c.concept_name,
    s.stock_count,
    s.total_value,
    s.avg_value,
    s.max_value,
    s.min_value,
    s.median_value,
    s.top10_sum
FROM concept_daily_summary s
JOIN concepts c ON s.concept_id = c.id
WHERE c.concept_name = '银行'
  AND s.trade_date = '2025-11-04'
  AND s.metric_code = 'EEE';
```

**结果**：
```
concept_name | stock_count | total_value | avg_value | max_value | min_value | median_value | top10_sum
银行         | 43          | 42408691    | 986248    | 5140764   | 44659     | 441832       | 26908249
```

### 查询3：比较同一股票在多个概念的排名

**需求**：查询600000在所有概念的2025-11-04 EEE排名

```sql
SELECT
    c.concept_name,
    r.rank,
    r.trade_value
FROM concept_stock_daily_rank r
JOIN concepts c ON r.concept_id = c.id
WHERE r.stock_code = '600000'
  AND r.trade_date = '2025-11-04'
  AND r.metric_code = 'EEE'
ORDER BY r.rank ASC;
```

**结果**：
```
concept_name  | rank | trade_value
转债标的      | 6    | 1137952
上海板块      | 12   | 1137952
银行          | 13   | 1137952
...
```

### 查询4：找出某概念的排名前N的股票

**需求**：找出"银行"概念EEE排名前5的股票

```sql
SELECT
    s.stock_code,
    s.stock_name,
    r.rank,
    r.trade_value
FROM concept_stock_daily_rank r
JOIN stocks s ON r.stock_code = s.stock_code
WHERE r.concept_id = (SELECT id FROM concepts WHERE concept_name = '银行')
  AND r.trade_date = '2025-11-04'
  AND r.metric_code = 'EEE'
ORDER BY r.rank ASC
LIMIT 5;
```

### 查询5：获取概念的实际股票数（正确方法）

**需求**：获取"银行"概念包含的股票数

```sql
-- ✅ 正确做法：从 stock_concepts 主数据表查询
SELECT COUNT(*) as concept_total_stock_count
FROM stock_concepts
WHERE concept_id = (SELECT id FROM concepts WHERE concept_name = '银行');
-- 结果: 86（概念实际包含的所有股票数，不受日期影响，永不改变）
```

**设计说明**：

- **之前的问题**：`concept_daily_summary` 中存储了 `stock_count`，表示该日期有数据的股票数
  - 这造成语义混淆，容易误认为是"概念包含的股票数"
  - 实际上这只是"导入数据中有记录的股票数"

- **改进方案**：
  - ✅ 概念包含的股票数 → 总是从 `stock_concepts` 表查询（权威来源）
  - ✅ 该日期有数据的股票数 → 可从 `stock_metric_data_raw` 动态计算，不需要持久化
  - ✅ 日汇总表只关注聚合统计（总值、均值、极值等），不存储计数

---

## 数据一致性保证

### 关键约束

1. **外键约束**：
   - stock_metric_data_raw.stock_code → stocks.stock_code
   - stock_concepts.stock_code → stocks.stock_code
   - 保证任何导入的股票代码必须先存在于 stocks 表

2. **唯一约束**：
   - stocks: stock_code (一个代码一只股票)
   - concepts: concept_name (一个名字一个概念)
   - metric_types: code (一个代码一个指标)

3. **业务规则**：
   - 只有 is_valid=true 的数据才参与计算
   - 只有 import_batch.compute_status=completed 的数据才能被查询

### 数据清洁性

- 验证错误存储在 stock_metric_data_raw.validation_errors (JSON)
- 原始行数据保存在 raw_line，方便问题追踪
- 可通过 is_valid 标记屏蔽错误数据

---

## 性能优化

### 索引策略

```sql
-- 查询优化关键索引
stocks: stock_code (PRIMARY + UNIQUE)
concepts: concept_name (UNIQUE)
stock_metric_data_raw: (stock_code, trade_date, metric_code)
concept_stock_daily_rank: (concept_id, trade_date)
concept_daily_summary: (concept_id, trade_date)
```

### 预计算表的作用

concept_stock_daily_rank 和 concept_daily_summary 是**物化视图**：
- 避免每次查询都重新计算排名和汇总
- 一次导入计算，多次快速查询
- 空间换时间的策略

---

## 常见操作和维护

### 添加新指标

1. 在 metric_types 插入新指标定义
2. 准备遵循 file_pattern 的数据文件
3. 通过导入API上传文件
4. 系统自动计算和展示

### 添加新概念

```sql
INSERT INTO concepts (concept_name, category, description)
VALUES ('新概念名', '分类', '描述');

-- 然后关联股票
INSERT INTO stock_concepts (stock_code, concept_id)
VALUES ('600000', (SELECT id FROM concepts WHERE concept_name = '新概念名'));
```

### 数据更正

如需修正历史数据：
1. 修改 stock_metric_data_raw 的数据
2. 重新运行 compute_service.compute_all_for_batch()
3. concept_stock_daily_rank 和 concept_daily_summary 会自动更新

---

## 扩展和未来改进

### 当前限制

1. **SQLite支持有限**（开发环境）
   - 生产应使用 PostgreSQL
   - 某些高级SQL特性（PERCENTILE_CONT）仅在 PostgreSQL 中可用

2. **时间序列数据**
   - 目前只支持日粒度
   - 可扩展为周/月粒度的汇总

3. **缺少维度表**
   - 可添加时间维度表以支持更复杂的时间分析
   - 可添加地域维度表支持地区分析

### 可能的优化方向

1. 添加物化视图支持月度、季度、年度汇总
2. 分区策略：按 trade_date 分区处理更大数据量
3. 缓存层：在 Redis 中缓存热点查询
4. 数据仓库：迁移到专门的OLAP系统（如ClickHouse）

