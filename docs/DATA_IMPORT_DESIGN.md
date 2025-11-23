# 数据导入设计 - 源数据保留与重算机制

**版本**: v1.1
**日期**: 2025-11-22
**状态**: 补充设计

---

## 📋 核心设计理念

### 设计原则

**源数据与计算结果分离**:
```
源数据 (Raw Data) → 数据处理 → 计算结果 (Computed Data)
     ↓                             ↓
   永久保留                    可重新计算
```

**核心优势**:
1. ✅ 源数据永久保留，可追溯
2. ✅ 算法调整后可重新计算
3. ✅ 数据错误可修正后重算
4. ✅ 支持不同计算策略对比

---

## 🗄️ 数据存储设计

### 1. 源数据表（Raw Data Tables）

#### stock_daily_data_raw - 原始交易数据

**设计目标**: 保留CSV导入的原始数据，不做任何计算

```sql
CREATE TABLE stock_daily_data_raw (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL REFERENCES import_records(id),  -- 导入批次
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,

    -- 原始数据字段
    trade_value BIGINT,              -- 原始交易值
    price DECIMAL(10, 2),            -- 原始价格
    turnover_rate DECIMAL(6, 2),    -- 原始换手率
    net_inflow DECIMAL(15, 2),      -- 原始净流入

    -- 元数据
    source_file VARCHAR(255),        -- 源文件名
    source_row_number INTEGER,       -- 源文件行号
    raw_data JSONB,                  -- 完整原始数据（JSON）

    -- 状态标记
    is_valid BOOLEAN DEFAULT true,   -- 是否有效
    validation_errors JSONB,         -- 校验错误信息

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 分区（按月）
CREATE TABLE stock_daily_data_raw_2025_08 PARTITION OF stock_daily_data_raw
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

-- 索引
CREATE INDEX idx_stock_daily_raw_code_date
    ON stock_daily_data_raw(stock_code, trade_date);
CREATE INDEX idx_stock_daily_raw_batch
    ON stock_daily_data_raw(import_batch_id);
CREATE INDEX idx_stock_daily_raw_valid
    ON stock_daily_data_raw(is_valid) WHERE is_valid = true;
CREATE INDEX idx_stock_daily_raw_data
    ON stock_daily_data_raw USING GIN (raw_data);
```

**字段说明**:
- `import_batch_id`: 记录来自哪次导入，便于回溯
- `source_file`: 源文件名，便于追溯数据来源
- `source_row_number`: 源文件行号，定位原始数据
- `raw_data`: JSONB格式存储完整原始数据，支持未来扩展
- `is_valid`: 标记数据是否有效，无效数据不参与计算
- `validation_errors`: 记录数据校验错误

#### stock_concept_mapping_raw - 原始概念映射数据

```sql
CREATE TABLE stock_concept_mapping_raw (
    id SERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL REFERENCES import_records(id),

    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    concept_name VARCHAR(100) NOT NULL,     -- 原始概念名称
    industry_name VARCHAR(100),             -- 原始行业名称

    -- 其他原始字段
    page_count INTEGER,                     -- 全部页数
    hot_post_views BIGINT,                  -- 热帖阅读数

    -- 元数据
    source_file VARCHAR(255),
    source_row_number INTEGER,
    raw_data JSONB,

    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concept_mapping_raw_batch
    ON stock_concept_mapping_raw(import_batch_id);
CREATE INDEX idx_concept_mapping_raw_stock
    ON stock_concept_mapping_raw(stock_code);
```

---

### 2. 计算结果表（Computed Data Tables）

#### stock_daily_data - 标准化后的交易数据

**设计目标**: 从原始数据计算得出，可重新生成

```sql
CREATE TABLE stock_daily_data (
    id BIGSERIAL,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,

    -- 计算后的标准数据
    trade_value BIGINT,
    price DECIMAL(10, 2),
    turnover_rate DECIMAL(6, 2),
    net_inflow DECIMAL(15, 2),

    -- 计算元数据
    computed_from_batch_id INTEGER REFERENCES import_records(id),  -- 来源批次
    computed_at TIMESTAMP,                                         -- 计算时间
    computation_version VARCHAR(20) DEFAULT 'v1.0',                -- 计算版本

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 唯一约束：同一股票同一天只有一条记录
CREATE UNIQUE INDEX idx_stock_daily_unique
    ON stock_daily_data(stock_code, trade_date);
```

#### concept_stock_daily_rank - 排名计算结果

```sql
CREATE TABLE concept_stock_daily_rank (
    id BIGSERIAL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,

    -- 计算结果
    trade_value BIGINT,
    rank INTEGER,
    percentile DECIMAL(5, 2),

    -- 计算元数据
    computed_at TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT 'v1.0',
    rank_algorithm VARCHAR(50) DEFAULT 'standard',  -- 排名算法标识

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

CREATE INDEX idx_concept_rank_composite
    ON concept_stock_daily_rank(concept_id, trade_date, rank);
```

---

### 3. 导入批次管理表

#### import_records - 增强版

```sql
CREATE TABLE import_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),

    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_path VARCHAR(500),
    file_hash VARCHAR(64),           -- SHA256哈希，防止重复导入

    -- 导入配置
    import_type VARCHAR(50),         -- concept_mapping, daily_data
    import_mode VARCHAR(20),         -- full, increment, replace

    -- 数据范围
    date_range_start DATE,           -- 数据日期范围
    date_range_end DATE,

    -- 执行状态
    status VARCHAR(20),              -- pending, processing, success, failed
    total_rows INTEGER,
    success_rows INTEGER,
    failed_rows INTEGER,
    duplicate_rows INTEGER,          -- 重复行数

    -- 错误信息
    error_log TEXT,
    validation_report JSONB,         -- 详细校验报告

    -- 时间信息
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 数据保留标记
    is_archived BOOLEAN DEFAULT false,        -- 是否已归档
    can_recompute BOOLEAN DEFAULT true,       -- 是否可重算

    -- 计算状态
    last_computed_at TIMESTAMP,              -- 最后计算时间
    computation_status VARCHAR(20)           -- not_computed, computing, computed, failed
);

CREATE INDEX idx_import_file_hash ON import_records(file_hash);
CREATE INDEX idx_import_date_range ON import_records(date_range_start, date_range_end);
CREATE INDEX idx_import_computation ON import_records(computation_status);
```

---

## 🔄 数据导入流程

### 完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 文件上传                                                  │
│    - 计算文件哈希                                            │
│    - 检查是否重复导入                                         │
│    - 存储到MinIO                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 数据预览                                                  │
│    - 读取前100行                                             │
│    - 自动检测字段类型                                         │
│    - 数据质量初步评估                                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 配置映射                                                  │
│    - 字段映射配置                                            │
│    - 导入模式选择（full/increment/replace）                  │
│    - 是否立即计算（或稍后手动触发）                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 数据导入（写入源数据表）                                   │
│    - 创建导入批次记录                                         │
│    - 逐行读取CSV                                             │
│    - 数据校验（格式、范围、重复）                             │
│    - 写入 stock_daily_data_raw                               │
│    - 标记无效数据（is_valid=false）                          │
│    - 更新导入进度                                            │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 数据计算（可选，可延迟）                                   │
│    - 触发计算任务                                            │
│    - 数据标准化（概念名称映射）                               │
│    - 写入 stock_daily_data                                   │
│    - 计算排名 → concept_stock_daily_rank                     │
│    - 计算汇总 → concept_daily_summary                        │
│    - 更新缓存                                                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 完成通知                                                  │
│    - 更新导入状态                                            │
│    - WebSocket推送完成消息                                   │
│    - 生成导入报告                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 数据重算机制

### 1. 重算触发场景

| 场景 | 触发方式 | 说明 |
|------|---------|------|
| **算法升级** | 手动触发 | 排名算法调整后，重新计算所有排名 |
| **数据修正** | 自动触发 | 修正源数据后，自动重算相关数据 |
| **批量重算** | 定时任务 | 每周重算一次，确保数据一致性 |
| **按需重算** | API调用 | 用户请求重算特定日期范围 |
| **增量重算** | 事件触发 | 新增源数据后，只重算增量部分 |

### 2. 重算API设计

```python
# API端点
POST /api/v1/recompute/trigger
POST /api/v1/recompute/batch/{batch_id}
POST /api/v1/recompute/date-range
GET  /api/v1/recompute/status/{task_id}
DELETE /api/v1/recompute/cancel/{task_id}
```

**触发全量重算**:
```http
POST /api/v1/recompute/trigger
Content-Type: application/json

{
  "recompute_type": "all",              // all, daily_data, ranks, summary
  "date_range": {
    "start": "2025-08-01",
    "end": "2025-08-31"
  },
  "options": {
    "clear_existing": true,             // 清除现有计算结果
    "computation_version": "v1.1",      // 计算版本
    "rank_algorithm": "improved"        // 排名算法
  }
}

// 响应
{
  "code": 200,
  "data": {
    "task_id": "recompute_20251122_001",
    "status": "pending",
    "estimated_duration": 600,           // 预计耗时（秒）
    "total_batches": 30,                 // 总批次数
    "affected_dates": ["2025-08-01", "2025-08-02", ...]
  }
}
```

**基于导入批次重算**:
```http
POST /api/v1/recompute/batch/123
Content-Type: application/json

{
  "recompute_scope": "full",            // full, ranks_only, summary_only
  "force": false                         // 是否强制重算（即使已计算过）
}
```

**按日期范围重算**:
```http
POST /api/v1/recompute/date-range
Content-Type: application/json

{
  "start_date": "2025-08-21",
  "end_date": "2025-08-21",
  "concepts": [1, 2, 3],                 // 可选：只重算指定概念
  "stocks": ["600000", "000001"]         // 可选：只重算指定股票
}
```

### 3. 重算任务表

```sql
CREATE TABLE recompute_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,

    -- 重算配置
    recompute_type VARCHAR(50),          -- all, daily_data, ranks, summary
    date_range_start DATE,
    date_range_end DATE,
    import_batch_ids INTEGER[],          -- 涉及的导入批次
    concept_ids INTEGER[],               -- 涉及的概念（可选）
    stock_codes TEXT[],                  -- 涉及的股票（可选）

    -- 计算配置
    computation_version VARCHAR(20),
    rank_algorithm VARCHAR(50),
    clear_existing BOOLEAN DEFAULT false,

    -- 执行状态
    status VARCHAR(20),                  -- pending, running, completed, failed, cancelled
    progress INTEGER DEFAULT 0,          -- 进度（百分比）
    total_items INTEGER,                 -- 总任务数
    processed_items INTEGER DEFAULT 0,   -- 已处理数

    -- 结果统计
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,

    -- 错误信息
    error_log TEXT,

    -- 时间信息
    created_by INTEGER REFERENCES users(id),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recompute_status ON recompute_tasks(status);
CREATE INDEX idx_recompute_date_range ON recompute_tasks(date_range_start, date_range_end);
```

### 4. 重算服务实现

```python
class RecomputeService:
    """数据重算服务"""

    async def trigger_recompute(
        self,
        recompute_type: str,
        date_range: DateRange,
        options: RecomputeOptions
    ) -> RecomputeTask:
        """
        触发重算任务

        Args:
            recompute_type: 重算类型（all/daily_data/ranks/summary）
            date_range: 日期范围
            options: 重算配置

        Returns:
            RecomputeTask: 重算任务对象
        """
        # 1. 创建重算任务记录
        task = RecomputeTask.create(
            task_id=generate_task_id(),
            recompute_type=recompute_type,
            date_range=date_range,
            options=options
        )

        # 2. 提交到Celery队列
        celery_task = recompute_data_task.delay(
            task_id=task.task_id,
            config=task.to_dict()
        )

        # 3. 返回任务信息
        return task

    async def recompute_from_raw_data(
        self,
        date_range: DateRange,
        clear_existing: bool = False
    ):
        """
        从原始数据重新计算

        流程:
        1. 读取源数据表（stock_daily_data_raw）
        2. 数据标准化和清洗
        3. 写入计算结果表（stock_daily_data）
        4. 计算排名
        5. 计算汇总
        """
        # 如果需要清除现有数据
        if clear_existing:
            await self._clear_computed_data(date_range)

        # 分批处理
        for date in date_range:
            # 1. 读取当日原始数据
            raw_data = await self._fetch_raw_data(date)

            # 2. 数据标准化
            standardized_data = await self._standardize_data(raw_data)

            # 3. 写入标准化数据
            await self._write_daily_data(standardized_data)

            # 4. 计算排名
            await self._compute_ranks(date)

            # 5. 计算汇总
            await self._compute_summary(date)

            # 6. 更新进度
            await self._update_progress(task_id, progress)

    async def _standardize_data(self, raw_data: List[RawData]) -> List[StandardData]:
        """
        数据标准化

        - 概念名称映射（使用 concept_mappings 表）
        - 数据类型转换
        - 异常值处理
        """
        result = []
        for row in raw_data:
            # 概念名称标准化
            concept_id = await self._map_concept_name(row.concept_name)

            # 数据验证和转换
            standard_row = StandardData(
                stock_code=row.stock_code,
                trade_date=row.trade_date,
                trade_value=self._validate_value(row.trade_value),
                concept_id=concept_id,
                computed_from_batch_id=row.import_batch_id,
                computation_version='v1.0'
            )
            result.append(standard_row)

        return result

    async def _compute_ranks(self, date: date):
        """
        计算排名

        使用窗口函数批量计算所有概念的股票排名
        """
        sql = """
        WITH ranked AS (
            SELECT
                sc.concept_id,
                sdd.stock_code,
                sdd.trade_value,
                RANK() OVER (
                    PARTITION BY sc.concept_id
                    ORDER BY sdd.trade_value DESC NULLS LAST
                ) as rank,
                PERCENT_RANK() OVER (
                    PARTITION BY sc.concept_id
                    ORDER BY sdd.trade_value DESC
                ) as percentile
            FROM stock_daily_data sdd
            JOIN stock_concepts sc ON sdd.stock_code = sc.stock_code
            WHERE sdd.trade_date = :date
              AND sdd.trade_value IS NOT NULL
        )
        INSERT INTO concept_stock_daily_rank
            (concept_id, stock_code, trade_date, trade_value, rank, percentile,
             computed_at, computation_version)
        SELECT
            concept_id, stock_code, :date, trade_value, rank,
            percentile * 100,
            NOW(), 'v1.0'
        FROM ranked
        ON CONFLICT (concept_id, stock_code, trade_date)
        DO UPDATE SET
            trade_value = EXCLUDED.trade_value,
            rank = EXCLUDED.rank,
            percentile = EXCLUDED.percentile,
            computed_at = NOW();
        """
        await db.execute(sql, {"date": date})
```

---

## 📊 数据流向图

```
CSV文件导入
    ↓
┌────────────────────────────────────┐
│  stock_daily_data_raw              │  ← 源数据（永久保留）
│  - 完整原始数据                     │
│  - 包含元数据                       │
│  - 支持重新处理                     │
└────────────────────────────────────┘
    ↓ 数据标准化（可重复执行）
┌────────────────────────────────────┐
│  stock_daily_data                  │  ← 标准化数据（可重算）
│  - 概念名称已映射                   │
│  - 数据已清洗                       │
└────────────────────────────────────┘
    ↓ 排名计算（可重复执行）
┌────────────────────────────────────┐
│  concept_stock_daily_rank          │  ← 计算结果（可重算）
│  - 排名数据                         │
│  - 可使用不同算法                   │
└────────────────────────────────────┘
    ↓ 汇总计算（可重复执行）
┌────────────────────────────────────┐
│  concept_daily_summary             │  ← 汇总结果（可重算）
│  - 总和、平均、最大值               │
└────────────────────────────────────┘
```

---

## 🎯 重算策略

### 1. 增量重算

**场景**: 新增了一批数据，只需重算这批数据

```python
async def incremental_recompute(batch_id: int):
    """
    增量重算

    只重算指定批次的数据，不影响其他数据
    """
    # 1. 获取批次的日期范围
    batch = await ImportRecord.get(batch_id)
    date_range = (batch.date_range_start, batch.date_range_end)

    # 2. 只处理这个批次的数据
    for date in date_range:
        # 标准化该批次的数据
        await standardize_batch_data(batch_id, date)

        # 重新计算该日期的排名（会影响所有股票）
        await recompute_ranks(date)

        # 重新计算该日期的汇总
        await recompute_summary(date)
```

### 2. 全量重算

**场景**: 算法升级，需要重算所有历史数据

```python
async def full_recompute(
    start_date: date,
    end_date: date,
    new_version: str = "v1.1"
):
    """
    全量重算

    重新处理所有源数据
    """
    # 1. 清空计算结果表（可选）
    if clear_existing:
        await clear_computed_data(start_date, end_date)

    # 2. 从源数据表重新计算
    for date in date_range(start_date, end_date):
        await recompute_from_raw_data(date, version=new_version)
```

### 3. 选择性重算

**场景**: 只重算特定概念或特定股票

```python
async def selective_recompute(
    date_range: DateRange,
    concepts: List[int] = None,
    stocks: List[str] = None
):
    """
    选择性重算

    只重算指定的概念或股票
    """
    for date in date_range:
        if concepts:
            # 只重算指定概念的排名
            for concept_id in concepts:
                await recompute_concept_rank(concept_id, date)

        if stocks:
            # 只重算指定股票相关的数据
            for stock_code in stocks:
                await recompute_stock_data(stock_code, date)
```

---

## 🔧 配置管理

### 1. 计算版本管理

```python
class ComputationVersion:
    """计算版本配置"""

    VERSIONS = {
        'v1.0': {
            'rank_algorithm': 'standard',
            'standardization_rules': 'basic',
            'created_at': '2025-11-01'
        },
        'v1.1': {
            'rank_algorithm': 'improved',
            'standardization_rules': 'enhanced',
            'created_at': '2025-12-01',
            'changes': '改进排名算法，优化概念映射'
        }
    }

    @classmethod
    def get_current_version(cls):
        """获取当前使用的版本"""
        return 'v1.1'
```

### 2. 重算策略配置

```yaml
# config/recompute.yaml

recompute_strategy:
  # 自动重算配置
  auto_recompute:
    enabled: true
    trigger_on: ['data_import', 'data_correction']
    delay_seconds: 60  # 延迟60秒后触发

  # 定时重算配置
  scheduled_recompute:
    enabled: true
    cron: "0 3 * * 0"  # 每周日凌晨3点
    scope: "last_7_days"

  # 批量重算配置
  batch_recompute:
    chunk_size: 1000   # 每批处理1000条
    parallel: 4        # 并行4个任务
    retry_times: 3     # 失败重试3次
```

---

## 📋 用户界面设计

### 1. 导入页面增强

**步骤4: 导入选项**

```
┌─────────────────────────────────────────────┐
│ 导入配置                                     │
├─────────────────────────────────────────────┤
│                                              │
│ 导入模式:                                    │
│   ○ 完整导入 (Full)                         │
│   ● 增量导入 (Increment)                    │
│   ○ 替换导入 (Replace)                      │
│                                              │
│ ☑ 保留源数据 (Raw Data)                     │
│   源数据将永久保存，支持后续重新计算          │
│                                              │
│ 计算选项:                                    │
│   ● 立即计算                                 │
│   ○ 稍后手动触发                             │
│                                              │
│ 计算范围:                                    │
│   ☑ 标准化数据                               │
│   ☑ 排名计算                                 │
│   ☑ 汇总统计                                 │
│                                              │
│ [上一步]              [开始导入] →           │
└─────────────────────────────────────────────┘
```

### 2. 重算管理页面

```
┌─────────────────────────────────────────────────────────┐
│ 数据重算管理                              [新建重算任务] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 重算任务列表                                             │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 任务ID | 类型 | 日期范围 | 进度 | 状态 | 操作   │   │
│ │ recom  │ 全量 │08-01 to  │ 75%  │运行中│[取消] │   │
│ │ _001   │      │08-31     │      │      │       │   │
│ ├────────────────────────────────────────────────┤   │
│ │ recom  │ 排名 │08-21     │100%  │完成  │[查看] │   │
│ │ _002   │      │          │      │      │       │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ 快速重算                                                 │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 日期范围: [2025-08-21] 到 [2025-08-21]        │   │
│ │                                                  │   │
│ │ 重算类型:                                        │   │
│ │   ☑ 标准化数据  ☑ 排名计算  ☑ 汇总统计         │   │
│ │                                                  │   │
│ │ [开始重算]                                       │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ 批次重算                                                 │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 导入批次: [选择批次 ▼]                          │   │
│ │                                                  │   │
│ │ 批次 #123                                        │   │
│ │ - 文件: 2025-08-22-01-31.csv                    │   │
│ │ - 日期范围: 2025-08-21                          │   │
│ │ - 记录数: 76,639                                │   │
│ │ - 计算状态: 未计算                              │   │
│ │                                                  │   │
│ │ [重新计算]                                       │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 实现优先级

### Phase 1: 基础实现（必须）

- [ ] 创建 `stock_daily_data_raw` 表
- [ ] 修改导入流程，写入源数据表
- [ ] 基础重算API
- [ ] 简单的重算UI

### Phase 2: 增强功能（重要）

- [ ] 创建 `recompute_tasks` 表
- [ ] 完整的重算服务
- [ ] 批次管理
- [ ] WebSocket进度推送

### Phase 3: 高级功能（可选）

- [ ] 定时自动重算
- [ ] 选择性重算
- [ ] 计算版本管理
- [ ] 重算任务队列优化

---

## 💡 最佳实践

### 1. 数据保留策略

```python
# 源数据永久保留
stock_daily_data_raw: 永久保留

# 计算结果可以删除重建
stock_daily_data: 可重算
concept_stock_daily_rank: 可重算
concept_daily_summary: 可重算

# 归档策略
超过1年的源数据 → 归档到冷存储（可选）
超过3个月的计算结果 → 可以清理（保留源数据即可）
```

### 2. 重算时机建议

| 场景 | 建议 |
|------|------|
| **数据导入后** | 立即计算（默认） |
| **数据修正后** | 自动触发重算 |
| **算法升级后** | 手动全量重算 |
| **定期维护** | 每周重算最近7天 |

### 3. 性能优化

```python
# 1. 批量处理
batch_size = 1000
for chunk in chunked(raw_data, batch_size):
    process_chunk(chunk)

# 2. 并行计算
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(recompute_date, date)
        for date in date_range
    ]

# 3. 增量更新
# 只更新变化的数据，而不是全部删除重建
ON CONFLICT (stock_code, trade_date) DO UPDATE ...
```

---

## 📊 监控指标

### 重算任务监控

```python
# Prometheus指标
recompute_task_total = Counter('recompute_task_total', 'Total recompute tasks')
recompute_task_duration = Histogram('recompute_task_duration_seconds', 'Recompute duration')
recompute_task_rows = Histogram('recompute_task_rows', 'Rows processed')

# 记录指标
recompute_task_total.inc()
with recompute_task_duration.time():
    process_recompute()
recompute_task_rows.observe(rows_processed)
```

---

## ✅ 总结

这个设计提供了：

1. ✅ **源数据永久保留** - 所有原始CSV数据完整保存
2. ✅ **计算结果可重建** - 基于源数据随时重新计算
3. ✅ **灵活的重算机制** - 支持全量、增量、选择性重算
4. ✅ **版本管理** - 支持不同计算版本并存
5. ✅ **完整的追溯** - 每条数据都能追溯到源文件
6. ✅ **用户友好** - 提供直观的重算管理界面

**核心优势**:
- 数据安全：源数据永久保留，不怕丢失
- 灵活性：算法调整后可以重算历史数据
- 可追溯：每条数据都有完整的元数据
- 高效：支持增量重算，避免全量计算
