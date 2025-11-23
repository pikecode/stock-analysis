# 多指标数据系统设计

**版本**: v1.0
**日期**: 2025-11-22
**状态**: 核心设计

---

## 📋 需求背景

### 现状分析

**数据文件类型**:
- `TTV.txt` - 某种交易指标
- `EEE.txt` - 另一种交易指标
- `EFV.txt` - 未来新增
- `AAA.txt` - 未来新增
- 还会有更多...

**关键特征**:
1. ✅ 每种类型都是独立的指标
2. ✅ 同一类型可以有多个文件（不同日期）
3. ✅ 每种指标有自己独立的汇总逻辑
4. ✅ 需要支持动态扩展新指标

### 设计目标

1. **灵活性**: 支持任意多种指标类型
2. **扩展性**: 新增指标类型不需要修改数据库结构
3. **独立性**: 每种指标的汇总逻辑互不干扰
4. **统一性**: 所有指标使用统一的导入和查询接口

---

## 🎯 核心设计理念

### 1. 指标类型抽象

```
指标类型（Metric Type）
    ↓
包含：名称、代码、字段定义、汇总规则
    ↓
具体实例：TTV, EEE, EFV, AAA...
```

### 2. 数据分层

```
┌────────────────────────────────────────────┐
│ 指标配置层 (Metric Configuration)          │
│ - 指标类型定义                              │
│ - 字段映射规则                              │
│ - 汇总计算规则                              │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│ 源数据层 (Raw Data)                        │
│ - 所有指标的原始数据                        │
│ - 按指标类型标记                            │
└────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────┐
│ 计算结果层 (Computed Data)                 │
│ - 每种指标独立的汇总结果                    │
│ - 支持多指标对比                            │
└────────────────────────────────────────────┘
```

---

## 🗄️ 数据库设计

### 1. 指标类型配置表

#### metric_types - 指标类型定义

```sql
CREATE TABLE metric_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,        -- 指标代码：TTV, EEE, EFV
    name VARCHAR(100) NOT NULL,              -- 显示名称
    description TEXT,                        -- 描述

    -- 文件识别
    file_pattern VARCHAR(100),               -- 文件名模式：*TTV*.txt
    file_extension VARCHAR(20) DEFAULT 'txt',

    -- 字段配置
    field_mapping JSONB,                     -- 字段映射配置

    -- 汇总配置
    aggregation_config JSONB,                -- 汇总规则配置

    -- 状态
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,            -- 显示排序

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- 示例数据
INSERT INTO metric_types (code, name, description, file_pattern, field_mapping, aggregation_config)
VALUES
(
    'TTV',
    '交易总值',
    'TTV交易指标数据',
    '*TTV*.txt',
    '{
        "stock_code": {"column": 0, "type": "string", "required": true},
        "trade_date": {"column": 1, "type": "date", "required": true},
        "value": {"column": 2, "type": "bigint", "required": true}
    }',
    '{
        "concept_rank": {
            "enabled": true,
            "algorithm": "desc",
            "fields": ["value"]
        },
        "concept_summary": {
            "enabled": true,
            "aggregations": ["sum", "avg", "max", "min", "count"]
        }
    }'
),
(
    'EEE',
    '交易活跃度',
    'EEE活跃度指标数据',
    '*EEE*.txt',
    '{
        "stock_code": {"column": 0, "type": "string", "required": true},
        "trade_date": {"column": 1, "type": "date", "required": true},
        "value": {"column": 2, "type": "bigint", "required": true}
    }',
    '{
        "concept_rank": {
            "enabled": true,
            "algorithm": "desc",
            "fields": ["value"]
        },
        "concept_summary": {
            "enabled": true,
            "aggregations": ["sum", "avg", "max"]
        }
    }'
);
```

**字段说明**:
- `code`: 指标唯一标识（TTV, EEE等）
- `file_pattern`: 用于自动识别文件类型
- `field_mapping`: 字段映射规则（JSON格式）
- `aggregation_config`: 汇总计算规则（JSON格式）

---

### 2. 源数据表（多指标支持）

#### stock_metric_data_raw - 统一的源数据表

```sql
CREATE TABLE stock_metric_data_raw (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL REFERENCES import_records(id),

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,        -- 冗余字段，便于查询

    -- 股票和日期
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,

    -- 通用数值字段
    value BIGINT,                            -- 主要数值
    value_decimal DECIMAL(15, 2),           -- 小数值（可选）
    value_text VARCHAR(100),                 -- 文本值（可选）

    -- 扩展字段（JSON存储）
    extra_fields JSONB,                      -- 额外的字段数据

    -- 元数据
    source_file VARCHAR(255),
    source_row_number INTEGER,
    raw_data JSONB,                          -- 完整原始数据

    -- 状态
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 分区示例
CREATE TABLE stock_metric_data_raw_2025_08 PARTITION OF stock_metric_data_raw
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

-- 索引
CREATE INDEX idx_metric_raw_type_code_date
    ON stock_metric_data_raw(metric_type_id, stock_code, trade_date);

CREATE INDEX idx_metric_raw_code
    ON stock_metric_data_raw(metric_code);

CREATE INDEX idx_metric_raw_batch
    ON stock_metric_data_raw(import_batch_id);

CREATE INDEX idx_metric_raw_date_type
    ON stock_metric_data_raw(trade_date, metric_type_id);
```

**设计说明**:
- 使用 `metric_type_id` 区分不同指标
- `value` 存储主要数值，满足大部分场景
- `extra_fields` 存储指标特有的额外字段
- `raw_data` 存储完整原始数据，支持未来扩展

---

### 3. 计算结果表（多指标支持）

#### stock_metric_data - 标准化后的数据

```sql
CREATE TABLE stock_metric_data (
    id BIGSERIAL,
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,

    -- 数值
    value BIGINT,
    value_decimal DECIMAL(15, 2),

    -- 计算元数据
    computed_from_batch_id INTEGER REFERENCES import_records(id),
    computed_at TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT 'v1.0',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 唯一约束
CREATE UNIQUE INDEX idx_metric_data_unique
    ON stock_metric_data(metric_type_id, stock_code, trade_date);

CREATE INDEX idx_metric_data_type_date
    ON stock_metric_data(metric_type_id, trade_date);
```

#### concept_metric_rank - 多指标排名

```sql
CREATE TABLE concept_metric_rank (
    id BIGSERIAL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 排名数据
    value BIGINT,
    rank INTEGER,
    percentile DECIMAL(5, 2),

    -- 计算元数据
    computed_at TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT 'v1.0',
    rank_algorithm VARCHAR(50) DEFAULT 'standard',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 复合索引
CREATE INDEX idx_concept_metric_rank_composite
    ON concept_metric_rank(concept_id, metric_type_id, trade_date, rank);

CREATE INDEX idx_concept_metric_rank_stock
    ON concept_metric_rank(stock_code, concept_id, metric_type_id, trade_date);
```

#### concept_metric_summary - 多指标汇总

```sql
CREATE TABLE concept_metric_summary (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    trade_date DATE NOT NULL,

    -- 指标标识
    metric_type_id INTEGER NOT NULL REFERENCES metric_types(id),
    metric_code VARCHAR(50) NOT NULL,

    -- 汇总数据
    total_value BIGINT,
    avg_value BIGINT,
    max_value BIGINT,
    min_value BIGINT,
    stock_count INTEGER,

    -- 扩展汇总字段（JSON）
    custom_aggregations JSONB,               -- 自定义汇总结果

    -- 计算元数据
    computed_at TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT 'v1.0',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(concept_id, metric_type_id, trade_date)
);

CREATE INDEX idx_concept_metric_summary_concept
    ON concept_metric_summary(concept_id, metric_type_id, trade_date);

CREATE INDEX idx_concept_metric_summary_date
    ON concept_metric_summary(trade_date, metric_type_id);
```

---

### 4. 导入记录增强

#### import_records - 增加指标类型字段

```sql
ALTER TABLE import_records
ADD COLUMN metric_type_id INTEGER REFERENCES metric_types(id),
ADD COLUMN metric_code VARCHAR(50),
ADD COLUMN auto_detected_type BOOLEAN DEFAULT false;  -- 是否自动检测的类型

-- 索引
CREATE INDEX idx_import_metric_type ON import_records(metric_type_id);
```

---

## 🔄 数据导入流程

### 1. 文件类型自动识别

```python
class MetricTypeDetector:
    """指标类型自动检测器"""

    async def detect_metric_type(self, file_name: str) -> Optional[MetricType]:
        """
        根据文件名自动识别指标类型

        Args:
            file_name: 文件名，如 "2025-08-21-TTV.txt"

        Returns:
            MetricType: 识别到的指标类型
        """
        # 获取所有激活的指标类型
        metric_types = await MetricType.filter(is_active=True).all()

        # 按文件模式匹配
        for metric_type in metric_types:
            pattern = metric_type.file_pattern
            if self._match_pattern(file_name, pattern):
                return metric_type

        # 未识别到，返回None
        return None

    def _match_pattern(self, file_name: str, pattern: str) -> bool:
        """
        匹配文件名模式

        pattern示例:
        - "*TTV*.txt" 匹配 "2025-08-21-TTV.txt"
        - "*EEE*.txt" 匹配 "data-EEE-20250821.txt"
        """
        import fnmatch
        return fnmatch.fnmatch(file_name.upper(), pattern.upper())
```

### 2. 增强的导入流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 文件上传                                                  │
│    - 上传文件                                                │
│    - 自动识别指标类型（根据文件名）                           │
│    - 如果无法识别，提示用户手动选择                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 指标类型确认                                              │
│    - 显示自动识别的类型                                       │
│    - 允许用户修改                                            │
│    - 加载该指标的字段映射配置                                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 数据预览                                                  │
│    - 根据字段映射配置解析数据                                 │
│    - 显示映射结果预览                                         │
│    - 数据校验                                                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 数据导入（写入源数据表）                                   │
│    - 创建导入批次记录（记录指标类型）                         │
│    - 写入 stock_metric_data_raw                              │
│    - 标记 metric_type_id 和 metric_code                      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 数据计算                                                  │
│    - 根据指标类型的汇总配置                                   │
│    - 标准化数据 → stock_metric_data                          │
│    - 计算排名 → concept_metric_rank                          │
│    - 计算汇总 → concept_metric_summary                       │
└─────────────────────────────────────────────────────────────┘
```

### 3. 导入服务实现

```python
class MetricImportService:
    """多指标导入服务"""

    async def import_metric_file(
        self,
        file_path: str,
        metric_type: MetricType,
        user_id: int
    ) -> ImportRecord:
        """
        导入指标文件

        Args:
            file_path: 文件路径
            metric_type: 指标类型
            user_id: 操作用户
        """
        # 1. 创建导入记录
        import_record = await ImportRecord.create(
            user_id=user_id,
            file_path=file_path,
            metric_type_id=metric_type.id,
            metric_code=metric_type.code,
            status='processing'
        )

        # 2. 读取文件并解析
        rows = await self._parse_file(file_path, metric_type)

        # 3. 批量写入源数据表
        await self._bulk_insert_raw_data(
            rows=rows,
            metric_type=metric_type,
            import_batch_id=import_record.id
        )

        # 4. 触发计算任务（可选）
        if should_compute_immediately:
            await self._trigger_computation(
                import_batch_id=import_record.id,
                metric_type=metric_type
            )

        return import_record

    async def _parse_file(
        self,
        file_path: str,
        metric_type: MetricType
    ) -> List[Dict]:
        """
        根据指标类型的字段映射配置解析文件
        """
        field_mapping = metric_type.field_mapping
        rows = []

        with open(file_path, 'r') as f:
            for line_no, line in enumerate(f, 1):
                parts = line.strip().split('\t')

                # 根据字段映射提取数据
                row = {
                    'stock_code': self._extract_field(
                        parts, field_mapping['stock_code']
                    ),
                    'trade_date': self._extract_field(
                        parts, field_mapping['trade_date']
                    ),
                    'value': self._extract_field(
                        parts, field_mapping['value']
                    ),
                    'source_row_number': line_no,
                    'raw_data': parts  # 保留原始数据
                }

                rows.append(row)

        return rows

    async def _bulk_insert_raw_data(
        self,
        rows: List[Dict],
        metric_type: MetricType,
        import_batch_id: int
    ):
        """批量插入源数据"""
        bulk_data = []
        for row in rows:
            bulk_data.append({
                'import_batch_id': import_batch_id,
                'metric_type_id': metric_type.id,
                'metric_code': metric_type.code,
                'stock_code': row['stock_code'],
                'trade_date': row['trade_date'],
                'value': row['value'],
                'source_row_number': row['source_row_number'],
                'raw_data': row['raw_data']
            })

        # 批量插入
        await StockMetricDataRaw.bulk_create(bulk_data, batch_size=1000)
```

---

## 📊 多指标汇总逻辑

### 1. 汇总规则配置

**JSON配置示例**:

```json
{
  "TTV": {
    "concept_rank": {
      "enabled": true,
      "algorithm": "desc",
      "fields": ["value"],
      "null_handling": "exclude"
    },
    "concept_summary": {
      "enabled": true,
      "aggregations": ["sum", "avg", "max", "min", "count"],
      "custom_aggregations": [
        {
          "name": "top10_sum",
          "sql": "SUM(CASE WHEN rank <= 10 THEN value ELSE 0 END)"
        }
      ]
    }
  },
  "EEE": {
    "concept_rank": {
      "enabled": true,
      "algorithm": "desc",
      "fields": ["value"]
    },
    "concept_summary": {
      "enabled": true,
      "aggregations": ["sum", "avg", "max"],
      "custom_aggregations": [
        {
          "name": "active_count",
          "sql": "COUNT(CASE WHEN value > 100000 THEN 1 END)"
        }
      ]
    }
  },
  "EFV": {
    "concept_rank": {
      "enabled": true,
      "algorithm": "desc",
      "weight": 0.7
    },
    "concept_summary": {
      "enabled": true,
      "aggregations": ["sum", "weighted_avg"]
    }
  }
}
```

### 2. 汇总计算服务

```python
class MetricAggregationService:
    """多指标汇总服务"""

    async def compute_concept_summary(
        self,
        concept_id: int,
        metric_type: MetricType,
        date: date
    ):
        """
        计算指定概念、指定指标的汇总数据

        根据指标类型的汇总配置动态计算
        """
        config = metric_type.aggregation_config
        summary_config = config.get('concept_summary', {})

        if not summary_config.get('enabled'):
            return

        # 基础汇总
        aggregations = summary_config.get('aggregations', [])
        base_agg = self._build_base_aggregation_sql(aggregations)

        sql = f"""
        INSERT INTO concept_metric_summary
            (concept_id, metric_type_id, metric_code, trade_date,
             total_value, avg_value, max_value, min_value, stock_count)
        SELECT
            :concept_id,
            :metric_type_id,
            :metric_code,
            :date,
            {base_agg['sum']},
            {base_agg['avg']},
            {base_agg['max']},
            {base_agg['min']},
            {base_agg['count']}
        FROM stock_metric_data smd
        JOIN stock_concepts sc ON smd.stock_code = sc.stock_code
        WHERE sc.concept_id = :concept_id
          AND smd.metric_type_id = :metric_type_id
          AND smd.trade_date = :date
        ON CONFLICT (concept_id, metric_type_id, trade_date)
        DO UPDATE SET
            total_value = EXCLUDED.total_value,
            avg_value = EXCLUDED.avg_value,
            max_value = EXCLUDED.max_value,
            min_value = EXCLUDED.min_value,
            stock_count = EXCLUDED.stock_count,
            computed_at = NOW();
        """

        await db.execute(sql, {
            'concept_id': concept_id,
            'metric_type_id': metric_type.id,
            'metric_code': metric_type.code,
            'date': date
        })

        # 自定义汇总
        custom_aggs = summary_config.get('custom_aggregations', [])
        if custom_aggs:
            await self._compute_custom_aggregations(
                concept_id, metric_type, date, custom_aggs
            )

    def _build_base_aggregation_sql(self, aggregations: List[str]) -> Dict[str, str]:
        """构建基础汇总SQL"""
        agg_map = {
            'sum': 'COALESCE(SUM(smd.value), 0)',
            'avg': 'COALESCE(AVG(smd.value), 0)',
            'max': 'COALESCE(MAX(smd.value), 0)',
            'min': 'COALESCE(MIN(smd.value), 0)',
            'count': 'COUNT(*)'
        }

        return {agg: agg_map.get(agg, '0') for agg in aggregations}
```

---

## 🔌 API设计

### 1. 指标类型管理API

```http
# 获取所有指标类型
GET /api/v1/metric-types

# 创建新指标类型
POST /api/v1/metric-types
{
  "code": "AAA",
  "name": "新指标AAA",
  "file_pattern": "*AAA*.txt",
  "field_mapping": {...},
  "aggregation_config": {...}
}

# 更新指标类型
PUT /api/v1/metric-types/{id}

# 删除指标类型（软删除）
DELETE /api/v1/metric-types/{id}
```

### 2. 多指标查询API

```http
# 查询股票在多个指标中的排名
GET /api/v1/stocks/{code}/metric-ranks?date=2025-08-21&metrics=TTV,EEE

# 响应
{
  "stock_code": "600000",
  "date": "2025-08-21",
  "metrics": {
    "TTV": {
      "value": 1000000,
      "concept_ranks": [
        {"concept": "人工智能", "rank": 5, "percentile": 90.5}
      ]
    },
    "EEE": {
      "value": 800000,
      "concept_ranks": [
        {"concept": "人工智能", "rank": 8, "percentile": 85.2}
      ]
    }
  }
}

# 查询概念在多个指标的汇总
GET /api/v1/concepts/{id}/metric-summary?date=2025-08-21&metrics=TTV,EEE

# 响应
{
  "concept_id": 1,
  "concept_name": "人工智能",
  "date": "2025-08-21",
  "metrics": {
    "TTV": {
      "total_value": 100000000,
      "avg_value": 666666,
      "max_value": 10000000,
      "stock_count": 150
    },
    "EEE": {
      "total_value": 80000000,
      "avg_value": 533333,
      "max_value": 8000000,
      "stock_count": 150
    }
  }
}

# 多指标对比
POST /api/v1/analysis/metric-comparison
{
  "concept_id": 1,
  "metrics": ["TTV", "EEE", "EFV"],
  "date_range": {
    "start": "2025-08-01",
    "end": "2025-08-31"
  }
}
```

### 3. 导入API增强

```http
# 上传文件（自动识别指标类型）
POST /api/v1/import/upload
FormData: {file}

# 响应
{
  "file_path": "/uploads/2025-08-21-TTV.txt",
  "detected_metric": {
    "id": 1,
    "code": "TTV",
    "name": "交易总值"
  },
  "auto_detected": true
}

# 执行导入（指定指标类型）
POST /api/v1/import/execute
{
  "file_path": "/uploads/2025-08-21-TTV.txt",
  "metric_type_id": 1,
  "import_mode": "increment"
}
```

---

## 🎨 用户界面设计

### 1. 指标类型管理页面

```
┌─────────────────────────────────────────────────────────┐
│ 指标类型管理                            [新建指标类型] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 代码 | 名称    | 文件模式   | 状态 | 操作    │   │
│ │ TTV  │交易总值 │*TTV*.txt  │启用  │[编辑]   │   │
│ │ EEE  │活跃度   │*EEE*.txt  │启用  │[编辑]   │   │
│ │ EFV  │流动性   │*EFV*.txt  │启用  │[编辑]   │   │
│ │ AAA  │指标AAA  │*AAA*.txt  │禁用  │[编辑]   │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2. 新建/编辑指标类型对话框

```
┌─────────────────────────────────────────────────────┐
│ 新建指标类型                               [x]     │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 基本信息:                                           │
│   代码*: [TTV________]                              │
│   名称*: [交易总值____]                             │
│   描述:  [_______________________________]         │
│                                                      │
│ 文件识别:                                           │
│   文件模式*: [*TTV*.txt]                           │
│   文件扩展名: [txt ▼]                              │
│                                                      │
│ 字段映射:                                           │
│   ┌─────────────────────────────────────┐          │
│   │ 字段名    │ 列位置 │ 数据类型 │必填│          │
│   │ stock_code│   0    │ string  │ ☑ │          │
│   │ trade_date│   1    │ date    │ ☑ │          │
│   │ value     │   2    │ bigint  │ ☑ │          │
│   └─────────────────────────────────────┘          │
│   [添加字段]                                        │
│                                                      │
│ 汇总配置:                                           │
│   ☑ 启用概念排名计算                                │
│       排名算法: [降序 ▼]                           │
│                                                      │
│   ☑ 启用概念汇总计算                                │
│       汇总函数: ☑ SUM  ☑ AVG  ☑ MAX                │
│                 ☑ MIN  ☑ COUNT                     │
│                                                      │
│ [取消]                              [保存]         │
└─────────────────────────────────────────────────────┘
```

### 3. 导入页面增强

```
┌─────────────────────────────────────────────────────┐
│ 数据导入                                             │
├─────────────────────────────────────────────────────┤
│ 文件: 2025-08-21-TTV.txt                            │
│                                                      │
│ 指标类型:                                           │
│   ● 自动识别: TTV - 交易总值                        │
│   ○ 手动选择: [请选择 ▼]                           │
│                                                      │
│ 数据预览: (根据TTV的字段映射)                       │
│ ┌──────────────────────────────────────┐           │
│ │ 股票代码 | 交易日期   | 交易总值    │           │
│ │ SH600000 | 2025-08-21 | 459400     │           │
│ │ SH600004 | 2025-08-21 | 375249     │           │
│ └──────────────────────────────────────┘           │
│                                                      │
│ 导入选项:                                           │
│   ☑ 保留源数据                                      │
│   ● 立即计算    ○ 稍后手动触发                     │
│                                                      │
│ [开始导入]                                          │
└─────────────────────────────────────────────────────┘
```

### 4. 多指标对比页面

```
┌─────────────────────────────────────────────────────────┐
│ 多指标对比分析                                          │
├─────────────────────────────────────────────────────────┤
│ 概念: [人工智能 ▼]                                     │
│ 日期: [2025-08-01] 到 [2025-08-31]                    │
│ 指标: ☑ TTV  ☑ EEE  ☑ EFV  □ AAA                      │
│                                                          │
│ 趋势对比图:                                             │
│ ┌────────────────────────────────────────────────┐     │
│ │                    ╱TTV                        │     │
│ │              ╱╲  ╱                             │     │
│ │         ╱╲╱  ╲╱                                │     │
│ │    EEE╱                    EFV                 │     │
│ │  ╱╲╱                    ╱╲                     │     │
│ │╱                    ╱╲╱  ╲                     │     │
│ │─────────────────────────────────────> 日期     │     │
│ └────────────────────────────────────────────────┘     │
│                                                          │
│ 指标汇总对比:                                           │
│ ┌────────────────────────────────────────────────┐     │
│ │ 指标 │ 总和      │ 平均值  │ 最大值   │ 相关性│     │
│ │ TTV  │100,000,000│ 666,666 │10,000,000│  1.0 │     │
│ │ EEE  │ 80,000,000│ 533,333 │ 8,000,000│  0.85│     │
│ │ EFV  │ 60,000,000│ 400,000 │ 6,000,000│  0.72│     │
│ └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 扩展新指标流程

### 添加新指标类型（如AAA.txt）的步骤

**1. 通过界面创建指标类型配置**:
```
代码: AAA
名称: 新指标AAA
文件模式: *AAA*.txt
字段映射: {
  "stock_code": {"column": 0, "type": "string"},
  "trade_date": {"column": 1, "type": "date"},
  "value": {"column": 2, "type": "bigint"}
}
汇总配置: {
  "concept_rank": {"enabled": true, "algorithm": "desc"},
  "concept_summary": {"enabled": true, "aggregations": ["sum", "avg"]}
}
```

**2. 系统自动支持**:
- ✅ 文件上传时自动识别AAA类型
- ✅ 使用配置的字段映射解析数据
- ✅ 写入统一的源数据表（标记metric_code='AAA'）
- ✅ 根据汇总配置计算排名和汇总

**3. 无需修改代码**:
- ✅ 无需修改数据库表结构
- ✅ 无需修改导入代码
- ✅ 无需修改查询API
- ✅ 只需配置新的指标类型

---

## 📊 数据查询示例

### 1. 查询TTV指标的数据

```sql
-- 查询某股票TTV指标的历史数据
SELECT
    trade_date,
    value as ttv_value
FROM stock_metric_data
WHERE stock_code = '600000'
  AND metric_code = 'TTV'
  AND trade_date BETWEEN '2025-08-01' AND '2025-08-31'
ORDER BY trade_date;
```

### 2. 查询多指标对比

```sql
-- 查询某股票在人工智能概念中的多指标排名
SELECT
    cmr.metric_code,
    mt.name as metric_name,
    cmr.value,
    cmr.rank,
    cmr.percentile
FROM concept_metric_rank cmr
JOIN metric_types mt ON cmr.metric_type_id = mt.id
WHERE cmr.stock_code = '600000'
  AND cmr.concept_id = 1
  AND cmr.trade_date = '2025-08-21'
ORDER BY cmr.metric_code;
```

### 3. 概念多指标汇总

```sql
-- 查询人工智能概念的多指标汇总
SELECT
    cms.metric_code,
    mt.name as metric_name,
    cms.total_value,
    cms.avg_value,
    cms.max_value,
    cms.stock_count
FROM concept_metric_summary cms
JOIN metric_types mt ON cms.metric_type_id = mt.id
WHERE cms.concept_id = 1
  AND cms.trade_date = '2025-08-21'
ORDER BY cms.metric_code;
```

---

## 🎯 实现优先级

### Phase 1: 基础多指标支持（必须）

- [ ] 创建 `metric_types` 表
- [ ] 创建 `stock_metric_data_raw` 表
- [ ] 创建 `stock_metric_data` 表
- [ ] 创建 `concept_metric_rank` 表
- [ ] 创建 `concept_metric_summary` 表
- [ ] 指标类型自动检测
- [ ] 基础导入流程支持多指标

### Phase 2: 配置化（重要）

- [ ] 指标类型管理界面
- [ ] 字段映射配置
- [ ] 汇总规则配置
- [ ] 指标类型CRUD API

### Phase 3: 高级功能（增强）

- [ ] 多指标对比分析
- [ ] 自定义汇总函数
- [ ] 指标相关性分析
- [ ] 指标权重配置

---

## 💡 最佳实践

### 1. 指标代码命名规范

```
- 使用大写字母
- 3-5个字符
- 语义明确
- 避免重复

推荐: TTV, EEE, EFV, AAA
不推荐: t1, metric1, data
```

### 2. 字段映射配置

```json
{
  "stock_code": {
    "column": 0,              // 列位置（从0开始）
    "type": "string",         // 数据类型
    "required": true,         // 是否必填
    "pattern": "^[0-9]{6}$"  // 可选：正则验证
  },
  "trade_date": {
    "column": 1,
    "type": "date",
    "required": true,
    "format": "YYYY-MM-DD"    // 日期格式
  },
  "value": {
    "column": 2,
    "type": "bigint",
    "required": true,
    "min": 0,                 // 可选：最小值
    "max": 999999999999       // 可选：最大值
  }
}
```

### 3. 汇总配置最佳实践

```json
{
  "concept_rank": {
    "enabled": true,
    "algorithm": "desc",      // desc: 降序, asc: 升序
    "null_handling": "exclude" // exclude: 排除空值, zero: 当作0
  },
  "concept_summary": {
    "enabled": true,
    "aggregations": ["sum", "avg", "max", "min", "count"],
    "custom_aggregations": [
      {
        "name": "top10_sum",
        "description": "前10名总和",
        "sql": "SUM(CASE WHEN rank <= 10 THEN value ELSE 0 END)"
      }
    ]
  }
}
```

---

## ✅ 总结

这个设计提供了：

1. ✅ **完全灵活的多指标支持** - 支持TTV、EEE、EFV、AAA等任意多种指标
2. ✅ **动态扩展** - 新增指标类型无需修改代码和数据库结构
3. ✅ **配置化** - 通过界面配置指标类型、字段映射、汇总规则
4. ✅ **独立汇总逻辑** - 每种指标有自己独立的计算规则
5. ✅ **统一管理** - 所有指标使用统一的导入、查询、重算接口
6. ✅ **多指标对比** - 支持多个指标的对比分析

**核心优势**:
- 新增指标类型只需配置，无需开发
- 所有指标数据统一存储，便于管理
- 支持任意复杂的汇总逻辑
- 完全向后兼容，不影响现有功能

---

## 📊 附录：汇总数据存储策略决策

> **重要**: 完整分析请参考 [METRIC_STORAGE_STRATEGY.md](./METRIC_STORAGE_STRATEGY.md)

### 问题：多指标汇总结果是统一存储还是分表存储？

**推荐方案：统一表 + JSONB扩展字段** ⭐⭐⭐⭐⭐

### 核心表结构

```sql
-- 所有指标的汇总都存在这一个表
CREATE TABLE concept_metric_summary (
    concept_id INTEGER,
    metric_type_id INTEGER,      -- 区分不同指标
    metric_code VARCHAR(50),      -- TTV, EEE, EFV

    -- 通用字段（所有指标都有）
    total_value BIGINT,
    avg_value BIGINT,
    max_value BIGINT,
    min_value BIGINT,
    stock_count INTEGER,

    -- 扩展字段（指标特有的汇总）
    custom_aggregations JSONB,    -- {"top10_sum": 50M, "active_count": 80}

    UNIQUE(concept_id, metric_type_id, trade_date)
);
```

### 数据示例

```
┌────────────┬────────────┬─────────────┬───────────┬──────────────────────┐
│ concept_id │metric_code │ total_value │ avg_value │ custom_aggregations  │
├────────────┼────────────┼─────────────┼───────────┼──────────────────────┤
│     1      │    TTV     │ 100,000,000 │  666,666  │ {"top10_sum": 50M}   │
│     1      │    EEE     │  80,000,000 │  533,333  │ {"active_cnt": 80}   │
│     1      │    EFV     │  60,000,000 │  400,000  │ {"flow_rate": 0.75}  │
└────────────┴────────────┴─────────────┴───────────┴──────────────────────┘
```

### 为什么选择统一表？

| 优势 | 说明 |
|------|------|
| **多指标对比超简单** | 一个SQL查询所有指标 |
| **新增指标零成本** | 不需要创建新表 |
| **代码统一** | 一套代码处理所有指标 |
| **JSONB灵活性** | 每种指标可以有自己的特殊字段 |
| **性能优秀** | PostgreSQL的JSONB支持索引 |

### 查询示例

```sql
-- 多指标对比（一个查询搞定）
SELECT metric_code, total_value, avg_value
FROM concept_metric_summary
WHERE concept_id = 1 AND trade_date = '2025-08-21';

-- 查询TTV特有字段
SELECT
    total_value,
    custom_aggregations->>'top10_sum' as top10_sum
FROM concept_metric_summary
WHERE metric_code = 'TTV' AND concept_id = 1;
```

### 对比方案：分表存储

**不推荐**，因为：
- ❌ 每种指标需要单独的表（concept_ttv_summary, concept_eee_summary...）
- ❌ 多指标对比需要UNION多个表
- ❌ 新增指标需要创建新表
- ❌ 代码重复，维护成本高

**详细分析**: 参见 [METRIC_STORAGE_STRATEGY.md](./METRIC_STORAGE_STRATEGY.md)
