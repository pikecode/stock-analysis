# 数据导入工作流程设计文档

**文档版本**: 2.0
**更新日期**: 2025-11-28
**作者**: Product Team + Claude Code

---

## 1. 数据导入概述

系统采用**两阶段分离的数据导入模式**：
- **第一阶段（CSV）**：股票基本信息和概念关系数据导入
- **第二阶段（TXT）**：日期特定的指标数据导入和计算

### 1.1 关键特性

✅ **CSV数据更新特性**
- 数据：股票-概念关系映射（静态关联数据）
- 更新频率：**不定时更新**（一次性或定期）
- 导入策略：**增量更新** - 只关心新增和变化的映射关系
- 覆盖方式：全量替换某股票的旧概念映射，保留未修改的部分

✅ **TXT数据周期特性**
- 数据：特定日期的股票指标数据
- 时间维度：**日期特定** - 每个文件代表特定日期的快照
- 更新频率：**几乎每个交易日都有新数据**（如每天导入一次）
- 多种指标：支持多种指标文件（如 EEE.txt, TTV.txt 等）

✅ **指标类型独立性**
- 每种指标类型维护独立的：
  - 排名数据（`concept_stock_daily_rank`）
  - 汇总数据（`concept_daily_summary`）
  - 计算逻辑
- 不同指标的数据相互独立，可并行处理

---

## 2. 数据源文件格式

### 2.1 CSV 文件（股票-概念关系）

**文件名示例**: `2025-08-22-01-31.csv`

**文件格式**:
```csv
股票代码,股票名称,全部页数,热帖首页页阅读总数,价格,行业,概念,换手,净流入
127111,金威转债,2,18340,0,None,食品饮料,0,0
127111,金威转债,2,18340,0,None,福建板块,0,0
127111,金威转债,2,18340,0,None,2025中报预增,0,0
113698,凯众转债,3,13810,0,None,汽车零部件,0,0
113698,凯众转债,3,13810,0,None,上海板块,0,0
...
```

**数据特征**:
- 编码：UTF-8
- 分隔符：逗号 (,)
- 必需列：股票代码、股票名称、概念
- 可选列：行业（如值为"None"则忽略）
- 多行关系：同一股票可有多行记录（每行一个概念）

**数据语义**:
- 每一行表示 **一个股票-概念的关联关系**
- 股票代码 (如 127111) 为标准代码，**不包含交易所前缀**
- 概念名称为灵活分类标签（如"福建板块"、"2025中报预增"等）
- 行业数据为可选的标准行业分类

### 2.2 TXT 文件（日期特定指标数据）

**文件名示例**:
- `EEE.txt` - 行业活跃度指标
- `TTV.txt` - 交易交易量指标
- 其他指标文件...

**文件格式**:
```
SH600000	2025-08-21	459400
SH600004	2025-08-21	375249
SH600006	2025-08-21	414249
SZ000001	2025-08-21	987654
BJ430047	2025-08-21	12345
...
```

**数据特征**:
- 编码：UTF-8
- 分隔符：Tab (制表符) 或空格
- 列数：至少3列（股票代码、日期、指标值）
- 股票代码格式：包含交易所前缀（SH/SZ/BJ + 6位代码）

**数据语义**:
- **列1 (股票代码)**：带交易所前缀的股票代码
  - `SH` = 上海交易所（Shanghai）
  - `SZ` = 深圳交易所（Shenzhen）
  - `BJ` = 北京交易所（Beijing）
  - 后6位数字为标准股票代码
  - 导入时**移除前缀**后存储，与CSV中的代码对应

- **列2 (日期)**：YYYY-MM-DD 格式的交易日期
  - 表示该指标数据所属的特定日期
  - 用于时间序列分析和排名计算

- **列3 (指标值)**：该股票在该日期的指标数值
  - 数字类型，表示交易量、活跃度等指标的大小
  - 每只股票的值通常不同
  - 用于排名计算（通常按值降序排列）

---

## 3. 导入处理流程

### 3.1 CSV 导入流程

```
┌─────────────────────────────────────────┐
│ 1. 上传CSV文件                           │
│    (文件格式检验：列名、编码)            │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 2. 逐行解析                              │
│    - 提取：股票代码、股票名称、概念、行业 │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 3. 数据清理和验证                        │
│    - 过滤无效行（缺少必需列）            │
│    - 忽略无效行业（值为"None"/"nan"）    │
│    - 去重处理                            │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 4. 批量收集（内存中）                    │
│    - new_stocks: {code, name}           │
│    - new_concepts: [name1, name2, ...]  │
│    - mappings: {股票, 概念}多对多         │
│    - raw_mappings: 原始审计数据           │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 5. 批量数据库操作                        │
│    - INSERT INTO stocks (新股票)         │
│    - INSERT INTO concepts (新概念)       │
│    - DELETE FROM stock_concepts (旧映射) │
│      WHERE stock_code IN (...)           │
│    - INSERT INTO stock_concepts (新映射) │
│    - INSERT INTO import_raw_data (审计)  │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 6. 导入完成                              │
│    status: success                       │
│    compute_status: pending (仅CSV不计算) │
└─────────────────────────────────────────┘
```

**关键设计点**：
1. **全量更新策略**：删除旧映射后重新插入，确保数据一致性
2. **增量新增**：新股票和新概念只在首次出现时创建
3. **原始数据保存**：保留审计记录供问题追踪

### 3.2 TXT 导入流程

```
┌──────────────────────────────────────────┐
│ 1. 上传TXT文件                            │
│    (选择指标类型：EEE, TTV, 其他...)       │
│    (文件格式检验：编码、分隔符)           │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 2. 逐行解析                               │
│    - 分隔符检测（Tab或空格）              │
│    - 提取3个字段：代码, 日期, 值           │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 3. 字段转换                               │
│    - 剥离交易所前缀：SH600000 → 600000   │
│    - 解析日期：2025-08-21 → date对象     │
│    - 转换为整数：float → int              │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 4. 预加载映射关系 ⚠️ 重要                 │
│    ├─ 加载所有stock_concepts映射          │
│    ├─ 构建valid_stocks集合                │
│    └─ (必须：CSV数据应已导入)             │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 5. 验证和过滤                             │
│    - 仅保留在stock_concepts中的股票        │
│    - 记录invalid_count（未关联的股票）    │
│    ⚠️ 如果stock_code未在CSV中出现过，    │
│       则被过滤（重要：CSV和TXT代码须一致) │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 6. 批量导入原始数据                       │
│    - INSERT INTO stock_metric_data_raw    │
│      (batch_id, metric_type, stock_code,  │
│       trade_date, trade_value, ...)       │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 7. 计算排名和汇总                         │
│    ⚠️ 这是TXT导入特有的步骤                │
│                                          │
│    按概念分组 → 按trade_value排序          │
│    ├─ concept_stock_daily_rank:           │
│    │  存储每只股票的日排名                  │
│    └─ concept_daily_summary:              │
│       计算概念的日汇总数据                  │
│       (总值、均值、极值、股票数等)        │
└────────────┬─────────────────────────────┘
             ↓
┌──────────────────────────────────────────┐
│ 8. 导入完成                               │
│    status: success                        │
│    compute_status: completed              │
│    数据可用于查询                          │
└──────────────────────────────────────────┘
```

**关键设计点**：
1. **代码转换**：前缀剥离是必须的，确保与CSV代码一致
2. **有效性过滤**：只有在CSV中定义过概念关联的股票才会被处理
3. **日期快照**：每个文件代表特定日期的完整快照，不同日期独立处理
4. **计算并行性**：不同指标类型的排名计算相互独立，可并行执行

---

## 4. 指标类型管理

### 4.1 指标类型定义

系统支持多种指标类型，每种指标在独立维度进行排名和汇总。

**metric_types 表字段说明**:

| 字段 | 说明 | 示例 |
|------|------|------|
| code | 指标唯一代码 | EEE, TTV, TOP |
| name | 指标显示名称 | 行业活跃度, 交易交易量 |
| file_pattern | 文件匹配模式 | `EEE*.txt`, `TTV*.txt` |
| rank_order | 排序方向 | DESC (值越大排名越高) |
| is_active | 是否启用 | true/false |

### 4.2 内置指标类型

```sql
-- 示例初始化数据
INSERT INTO metric_types (code, name, description, file_pattern, rank_order, is_active) VALUES
('EEE', '行业活跃度', '来自EEE指标文件', 'EEE*.txt', 'DESC', true),
('TTV', '交易交易量', '来自TTV指标文件', 'TTV*.txt', 'DESC', true),
('TOP', 'TOP指标', '其他统计指标', 'TOP*.txt', 'DESC', true);
```

### 4.3 指标数据独立性

✅ **每种指标完全独立**：
- 数据源隔离：EEE.txt 和 TTV.txt 分别存储在不同的表分区
- 排名独立：同一股票在不同指标中的排名互不影响
- 汇总独立：每种指标有独立的日汇总统计
- 查询路由：API查询时指定 `metric_type` 参数获取对应数据

**数据流向示例**:
```
EEE.txt  ───→  stock_metric_data_raw (metric_type=EEE)
              ───→  concept_stock_daily_rank (metric_type=EEE)
              ───→  concept_daily_summary (metric_type=EEE)

TTV.txt  ───→  stock_metric_data_raw (metric_type=TTV)
              ───→  concept_stock_daily_rank (metric_type=TTV)
              ───→  concept_daily_summary (metric_type=TTV)

(并行处理，不相互干扰)
```

---

## 5. 数据库表关系

### 5.1 导入流程中涉及的表

```
┌──────────────────────────────┐
│  CSV导入                      │
└────────┬─────────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
 stocks   concepts
    │         │
    └────┬────┘
         ↓
  stock_concepts  ←─── 核心关联表
         │
         │
┌────────┴─────────────────────┐
│  import_batches              │ (追踪每次导入)
│  - status: pending/processing/success
│  - compute_status: pending (CSV不计算)
└──────────────────────────────┘


┌──────────────────────────────┐
│  TXT导入                      │
└────────┬─────────────────────┘
         │
         ├─→  stock_metric_data_raw  ← 源数据（不直接查询）
         │            ↓
         │      (预加载映射关系)
         │      ↓
         ├─→  concept_stock_daily_rank  ← 排名数据（API查询用）
         │
         └─→  concept_daily_summary  ← 汇总数据（API查询用）

┌─────────────────────────────────┐
│  import_batches                 │
│  - status: pending/processing/success
│  - compute_status: computing/completed
│  - metric_type_id: 关联指标类型
└─────────────────────────────────┘
```

### 5.2 关键表字段说明

#### import_batches（导入批次追踪）

| 字段 | CSV导入 | TXT导入 | 说明 |
|------|--------|--------|------|
| file_type | CSV | TXT | 文件类型 |
| metric_type_id | NULL | 设置 | 仅TXT需要指标类型 |
| data_date | NULL | 设置 | TXT的数据日期 |
| status | success | success | 导入最终状态 |
| compute_status | pending | computing→completed | CSV不需计算，TXT需计算 |
| total_rows | 映射数 | 数据行数 | - |
| success_rows | 成功数 | 有效数 | - |
| error_rows | 失败数 | 无关联数 | - |

#### stock_metric_data_raw（原始指标数据源）

| 字段 | 说明 | 示例 |
|------|------|------|
| metric_type_id | 指标类型 | 1 (EEE) / 2 (TTV) |
| stock_code | 标准代码（已去前缀） | 600000 |
| trade_date | 数据日期 | 2025-08-21 |
| trade_value | 指标值 | 459400 |
| import_batch_id | 关联导入批次 | - |

---

## 6. 导入规则和约束

### 6.1 CSV 导入规则

| 规则 | 说明 |
|------|------|
| 必需列 | 股票代码、股票名称、概念 |
| 编码 | UTF-8 |
| 分隔符 | 逗号 (,) |
| 重复处理 | 同一股票可多行（每行一个概念）✓ |
| 行业处理 | "None" / "nan" 值被忽略 |
| 更新策略 | 全量替换（删除旧映射后重新插入） |
| 数据唯一性 | stock_code + concept_name 为关键组合 |

### 6.2 TXT 导入规则

| 规则 | 说明 |
|------|------|
| 必需列 | 股票代码(含前缀)、日期、指标值 |
| 编码 | UTF-8 |
| 分隔符 | Tab 或空格 |
| 代码格式 | SH/SZ/BJ + 6位数字 |
| 日期格式 | YYYY-MM-DD |
| 有效性过滤 | ⚠️ 只保留在 stock_concepts 中存在的股票 |
| 关键约束 | **CSV 必须先导入，否则 TXT 数据无法关联** |
| 并行处理 | 不同指标类型可独立并行处理 |

### 6.3 导入顺序约束

```
⚠️ 关键约束：CSV → TXT

第1步: 导入 CSV 文件
       ↓
       创建股票、概念、stock_concepts映射

第2步: 导入 TXT 文件
       ↓
       前置检查：验证stock_code在stock_concepts中存在
       ↓
       如果CSV中无该股票的概念映射 → 过滤（invalid_count++）
       ↓
       计算排名和汇总
```

**原因**：TXT 导入的数据需要与股票的概念映射关联，如果股票未在 CSV 中定义过概念，则无法进行排名计算。

---

## 7. 导入状态机

### 7.1 CSV 导入状态流

```
    ┌─────────────────────────────────────┐
    │  开始：用户上传CSV文件               │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ status: pending                      │
    │ (等待处理)                            │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ status: processing                   │
    │ (正在导入数据)                        │
    └────────────┬────────────────────────┘
                 ↓
           ┌─────┴─────┐
           ↓           ↓
       ┌────────┐  ┌────────┐
       │导入成功│  │导入失败│
       └────┬───┘  └────┬───┘
            ↓           ↓
    ┌──────────────┐ ┌─────────────────┐
    │status:       │ │status: failed    │
    │success       │ │error_message: {} │
    │compute_status│ └─────────────────┘
    │pending       │        ↓
    │(不需计算)    │ ┌──────────────────┐
    └──────────────┘ │前端展示错误信息   │
         ↓           │用户可重新上传     │
    ┌─────────────┐  └──────────────────┘
    │数据可用      │
    │可查询关系    │
    └─────────────┘
```

### 7.2 TXT 导入状态流

```
    ┌──────────────────────────────────────┐
    │ 开始：用户上传TXT文件                 │
    │      选择指标类型                     │
    └─────────────┬────────────────────────┘
                  ↓
    ┌──────────────────────────────────────┐
    │ status: pending                       │
    │ compute_status: pending               │
    │ (等待处理)                             │
    └─────────────┬────────────────────────┘
                  ↓
    ┌──────────────────────────────────────┐
    │ status: processing                    │
    │ compute_status: pending               │
    │ (正在导入数据)                         │
    └─────────────┬────────────────────────┘
                  ↓
    ┌──────────────────────────────────────┐
    │ status: processing                    │
    │ compute_status: computing             │
    │ (正在计算排名和汇总)                   │
    └─────────────┬────────────────────────┘
                  ↓
             ┌────┴────┐
             ↓         ↓
       ┌─────────┐ ┌──────────┐
       │计算成功 │ │计算失败  │
       └────┬────┘ └────┬─────┘
            ↓           ↓
    ┌──────────────────┐ ┌──────────────┐
    │status: success   │ │status: failed │
    │compute_status:   │ │compute_status:│
    │completed         │ │failed         │
    │                  │ │error_message: │
    │✅ 数据可用        │ │需排查日志      │
    │✅ 排名生成        │ └──────────────┘
    │✅ 汇总完成        │
    └──────────────────┘
```

---

## 8. 计算逻辑（TXT导入特有）

### 8.1 排名计算

**输入**：stock_metric_data_raw 中该日期、该指标的所有有效数据

**处理**：
```
FOR EACH concept:
    ├─ 筛选：该概念下的所有股票
    ├─ 过滤：仅保留有trade_value的记录
    ├─ 排序：按trade_value降序排列
    └─ 排名：使用DENSE_RANK()分配排名
            (相同值的股票排名相同，不留空位)

INSERT INTO concept_stock_daily_rank:
    ├─ metric_type_id
    ├─ concept_id
    ├─ stock_code
    ├─ rank (1, 2, 3, ...)
    ├─ trade_value
    ├─ trade_date
    └─ import_batch_id
```

### 8.2 汇总计算

**输入**：同一日期、同一概念、同一指标的所有股票数据

**处理**：
```
FOR EACH concept, EACH trade_date:
    ├─ 总值 = SUM(trade_value)
    ├─ 平均值 = AVG(trade_value)
    ├─ 最大值 = MAX(trade_value)
    ├─ 最小值 = MIN(trade_value)
    ├─ 中位数 = MEDIAN(trade_value)
    ├─ 股票总数 = COUNT(DISTINCT stock_code)
    └─ 该日期有数据的股票数 = COUNT(stock_code)

INSERT INTO concept_daily_summary:
    ├─ metric_type_id
    ├─ concept_id
    ├─ trade_date
    ├─ total_value
    ├─ avg_value
    ├─ max_value
    ├─ min_value
    ├─ median_value
    ├─ stocks_total (来自stock_concepts的静态数据)
    ├─ stocks_with_data (该日期有数据的股票数)
    └─ import_batch_id
```

---

## 9. 数据一致性保证

### 9.1 CSV 导入的一致性

- **主键约束**：stock_code 和 concept_name 都有唯一性约束
- **外键约束**：stock_concepts 中的 stock_code 和 concept_id 必须存在
- **事务保证**：所有操作在单个事务中，要么全部成功要么全部回滚
- **冲突处理**：使用 ON CONFLICT DO UPDATE/NOTHING 处理重复

### 9.2 TXT 导入的一致性

- **前置验证**：数据必须经过 stock_concepts 有效性检查
- **原始数据保存**：所有源数据保存在 stock_metric_data_raw（便于问题追踪）
- **计算原子性**：排名和汇总计算在单个事务中完成
- **索引支持**：关键查询字段都建有索引确保性能

### 9.3 跨表一致性

```
stock_concepts 表是核心枢纽
    ↓
CSV更新 → 影响 stock_concepts
    ↓
TXT导入 → 依赖 stock_concepts 进行过滤
    ↓
结果：CSV和TXT之间的数据通过stock_concepts紧密关联
```

---

## 10. 性能考虑

### 10.1 CSV导入性能

| 操作 | 数据量 | 预期时间 | 优化策略 |
|------|--------|---------|---------|
| 文件解析（pandas） | 10K行 | <100ms | 流式处理，分批插入 |
| 批量插入 | 1K新股票 | 100-200ms | 批大小=1000 |
| 概念插入 | 1K新概念 | 50-100ms | 批大小=5000 |
| 映射插入 | 10K映射 | 200-500ms | 批大小=5000 |
| **总耗时** | | **<1秒** | ✅ 优秀 |

### 10.2 TXT导入性能

| 操作 | 数据量 | 预期时间 | 优化策略 |
|------|--------|---------|---------|
| 文件解析 | 5K行 | <50ms | 逐行流处理 |
| 预加载映射 | 1K股票 | <100ms | 内存缓存 |
| 有效性过滤 | 5K行 | <50ms | 集合查询 |
| 原始数据插入 | 4K行 | 100-200ms | 批大小=1000 |
| 排名计算 | 100概念 | 50-100ms | 内存计算 |
| 汇总计算 | 100概念 | 30-50ms | 单遍扫描 |
| **总耗时** | | **<500ms** | ✅ 优秀 |

### 10.3 索引策略

```sql
-- stock_concepts 的索引（最关键）
CREATE INDEX idx_stock_code ON stock_concepts(stock_code);
CREATE INDEX idx_concept_id ON stock_concepts(concept_id);
CREATE UNIQUE INDEX uq_stock_concept ON stock_concepts(stock_code, concept_id);

-- stock_metric_data_raw 的索引
CREATE INDEX idx_stock_code_date ON stock_metric_data_raw(stock_code, trade_date);
CREATE INDEX idx_metric_date ON stock_metric_data_raw(metric_type_id, trade_date);
CREATE INDEX idx_batch_id ON stock_metric_data_raw(import_batch_id);

-- 查询优化索引
CREATE INDEX idx_concept_rank_date ON concept_stock_daily_rank(concept_id, trade_date);
CREATE INDEX idx_summary_date ON concept_daily_summary(metric_type_id, trade_date);
```

---

## 11. 监控和调试

### 11.1 导入监控

```python
# 前端显示进度
import_batches.status          # pending/processing/success/failed
import_batches.compute_status  # pending/computing/completed/failed
import_batches.total_rows      # 总行数
import_batches.success_rows    # 成功行数
import_batches.error_rows      # 失败行数
import_batches.error_message   # 错误详情
```

### 11.2 问题排查

**问题1**：TXT导入显示"invalid rows"过多
```sql
-- 检查CSV中的股票概念映射
SELECT COUNT(*) FROM stock_concepts WHERE stock_code LIKE '600000';
-- 预期：>0（说明该股票在CSV中已定义）
```

**问题2**：排名计算失败
```sql
-- 检查原始数据是否成功导入
SELECT COUNT(*) FROM stock_metric_data_raw
WHERE metric_type_id = 1 AND trade_date = '2025-08-21';
-- 预期：>0（说明数据已导入）
```

**问题3**：概念的汇总数据不完整
```sql
-- 检查该日期的排名记录
SELECT COUNT(DISTINCT stock_code) FROM concept_stock_daily_rank
WHERE concept_id = 10 AND trade_date = '2025-08-21';
-- 对应的汇总中 stocks_with_data 应该等于这个数值
```

---

## 12. 最佳实践

### 12.1 CSV导入最佳实践

✅ 建议做法：
- 定期导入最新的股票-概念关系
- 定义清晰的更新周期（如每周一次）
- 在导入前备份旧数据
- 检查导入后的 error_rows 是否为 0

❌ 避免做法：
- 频繁导入相同内容（数据重复）
- 导入包含无效概念名称的数据
- 忽视 import_batches 中的错误信息

### 12.2 TXT导入最佳实践

✅ 建议做法：
- 确保 CSV 已先导入
- 按日期逐次导入（便于排查和回滚）
- 验证文件格式（Tab分隔、日期格式）
- 监控 compute_status 直到 completed

❌ 避免做法：
- 跳过 CSV 直接导入 TXT
- 使用格式不一致的文件（如空格vs Tab）
- 导入多个相同日期的同类型文件（导致重复计算）

### 12.3 指标类型管理最佳实践

✅ 建议做法：
- 在 metric_types 表中清晰定义每种指标
- 使用一致的命名规范（EEE, TTV, TOP等）
- 为每种新指标创建专用的文件模式
- 定期审查未使用的指标类型

---

## 附录：SQL 查询示例

### A1. 查询导入历史

```sql
-- 查看最近的导入记录
SELECT id, file_name, file_type, status, compute_status,
       success_rows, error_rows, created_at
FROM import_batches
ORDER BY created_at DESC
LIMIT 20;

-- 查看特定日期的TXT导入
SELECT * FROM import_batches
WHERE file_type = 'TXT' AND data_date = '2025-08-21'
ORDER BY created_at DESC;
```

### A2. 验证数据导入结果

```sql
-- CSV导入验证：查看股票-概念的映射关系
SELECT s.stock_code, s.stock_name, c.concept_name
FROM stock_concepts sc
JOIN stocks s ON sc.stock_code = s.stock_code
JOIN concepts c ON sc.concept_id = c.id
WHERE s.stock_code = '600000'
LIMIT 10;

-- TXT导入验证：查看某日期的指标数据
SELECT stock_code, trade_value, trade_date
FROM stock_metric_data_raw
WHERE metric_type_id = 1 AND trade_date = '2025-08-21'
ORDER BY trade_value DESC
LIMIT 10;
```

### A3. 排名和汇总查询

```sql
-- 查看某概念在某日期的股票排名
SELECT rank, stock_code, trade_value, trade_date
FROM concept_stock_daily_rank
WHERE concept_id = 10 AND trade_date = '2025-08-21'
ORDER BY rank ASC;

-- 查看某概念的日汇总数据
SELECT trade_date, total_value, avg_value, max_value, stocks_with_data
FROM concept_daily_summary
WHERE concept_id = 10 AND trade_date = '2025-08-21';
```

---

**文档版本历史**：
- v2.0 (2025-11-28)：完整重构，基于实际数据文件和导入逻辑
- v1.0 (2025-08-22)：初始版本

