# API设计文档

**版本**: v2.0
**更新日期**: 2025-11-23
**基础路径**: `/api/v1`

---

## 1. API概览

### 1.1 模块划分

| 模块 | 路径前缀 | 说明 |
|-----|---------|------|
| 认证 | `/auth` | 登录、登出、Token刷新 |
| 用户 | `/users` | 用户管理 |
| 股票 | `/stocks` | 股票查询 |
| 概念 | `/concepts` | 概念查询 |
| 排名 | `/rankings` | 排名分析 |
| 汇总 | `/summaries` | 汇总统计 |
| 导入 | `/import` | 数据导入 |
| 指标 | `/metrics` | 指标类型管理 |

### 1.2 通用响应格式

**成功响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

**错误响应**:
```json
{
  "code": 40001,
  "message": "参数错误",
  "detail": "stock_code不能为空"
}
```

### 1.3 认证方式

- Header: `Authorization: Bearer <access_token>`
- Token有效期：2小时

---

## 2. 认证模块 `/auth`

### 2.1 用户登录

```
POST /auth/login
```

**请求**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 7200,
    "user": {
      "id": 1,
      "username": "admin",
      "roles": ["admin"]
    }
  }
}
```

### 2.2 刷新Token

```
POST /auth/refresh
```

**请求**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 2.3 登出

```
POST /auth/logout
```

---

## 3. 股票模块 `/stocks`

### 3.1 股票列表

```
GET /stocks
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| keyword | string | 否 | 搜索关键词 |
| exchange | string | 否 | 交易所(SH/SZ/BJ) |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "total": 5000,
    "items": [
      {
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "exchange_prefix": "SH",
        "exchange_name": "上海证券交易所"
      }
    ]
  }
}
```

### 3.2 股票详情

```
GET /stocks/{stock_code}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "stock_code": "600000",
    "stock_name": "浦发银行",
    "exchange_prefix": "SH",
    "concepts": [
      {"id": 1, "name": "银行"},
      {"id": 2, "name": "上海板块"}
    ],
    "industries": [
      {"id": 1, "name": "金融"}
    ]
  }
}
```

### 3.3 股票所属概念（需求1）

```
GET /stocks/{stock_code}/concepts
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "stock_code": "600000",
    "stock_name": "浦发银行",
    "concepts": [
      {"id": 1, "name": "银行", "category": "行业"},
      {"id": 2, "name": "上海板块", "category": "地区"}
    ]
  }
}
```

---

## 4. 概念模块 `/concepts`

### 4.1 概念列表

```
GET /concepts
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| keyword | string | 否 | 搜索关键词 |
| category | string | 否 | 分类筛选 |

### 4.2 概念详情

```
GET /concepts/{concept_id}
```

### 4.3 概念下的股票列表

```
GET /concepts/{concept_id}/stocks
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "concept_id": 1,
    "concept_name": "人工智能",
    "stock_count": 150,
    "stocks": [
      {"stock_code": "600000", "stock_name": "浦发银行"}
    ]
  }
}
```

---

## 5. 排名模块 `/rankings`

### 5.1 概念排名列表（需求3）

```
GET /rankings/concept/{concept_id}
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| trade_date | date | 是 | 交易日期 |
| metric_code | string | 否 | 指标代码，默认TTV |
| limit | int | 否 | 返回数量，默认50 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "concept_id": 1,
    "concept_name": "人工智能",
    "trade_date": "2025-08-21",
    "metric_code": "TTV",
    "total_stocks": 150,
    "rankings": [
      {
        "rank": 1,
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "trade_value": 10000000,
        "percentile": 99.33
      },
      {
        "rank": 2,
        "stock_code": "000001",
        "stock_name": "平安银行",
        "trade_value": 9500000,
        "percentile": 98.67
      }
    ]
  }
}
```

### 5.2 股票排名历史（需求5/6）

```
GET /rankings/stock/{stock_code}
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| concept_id | int | 是 | 概念ID |
| start_date | date | 是 | 开始日期 |
| end_date | date | 是 | 结束日期 |
| metric_code | string | 否 | 指标代码 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "stock_code": "600000",
    "stock_name": "浦发银行",
    "concept_id": 1,
    "concept_name": "人工智能",
    "metric_code": "TTV",
    "history": [
      {
        "trade_date": "2025-08-21",
        "rank": 5,
        "trade_value": 459400,
        "total_stocks": 150,
        "percentile": 96.67
      },
      {
        "trade_date": "2025-08-22",
        "rank": 3,
        "trade_value": 520000,
        "total_stocks": 150,
        "percentile": 98.00
      }
    ]
  }
}
```

### 5.3 前N名出现次数统计（需求4）

```
GET /rankings/stock/{stock_code}/top-n-count
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| concept_id | int | 否 | 概念ID（不传则统计所有概念） |
| start_date | date | 是 | 开始日期 |
| end_date | date | 是 | 结束日期 |
| top_n | int | 否 | 前N名，默认10 |
| metric_code | string | 否 | 指标代码 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "stock_code": "600000",
    "stock_name": "浦发银行",
    "date_range": {
      "start": "2025-08-01",
      "end": "2025-08-31"
    },
    "top_n": 10,
    "metric_code": "TTV",
    "trading_days": 22,
    "statistics": [
      {
        "concept_id": 1,
        "concept_name": "人工智能",
        "top_n_count": 15,
        "top_n_rate": 68.18
      },
      {
        "concept_id": 2,
        "concept_name": "银行",
        "top_n_count": 20,
        "top_n_rate": 90.91
      }
    ]
  }
}
```

---

## 6. 汇总模块 `/summaries`

### 6.1 概念日汇总（需求2/6）

```
GET /summaries/concept/{concept_id}
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| start_date | date | 是 | 开始日期 |
| end_date | date | 是 | 结束日期 |
| metric_code | string | 否 | 指标代码 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "concept_id": 1,
    "concept_name": "人工智能",
    "metric_code": "TTV",
    "summaries": [
      {
        "trade_date": "2025-08-21",
        "total_value": 100000000,
        "avg_value": 666666,
        "max_value": 10000000,
        "min_value": 10000,
        "stock_count": 150,
        "median_value": 500000,
        "top10_sum": 50000000
      }
    ]
  }
}
```

### 6.2 多指标对比

```
GET /summaries/concept/{concept_id}/compare
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| trade_date | date | 是 | 交易日期 |
| metric_codes | string | 否 | 指标代码列表，逗号分隔 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "concept_id": 1,
    "trade_date": "2025-08-21",
    "metrics": [
      {
        "metric_code": "TTV",
        "metric_name": "交易总值",
        "total_value": 100000000,
        "avg_value": 666666,
        "stock_count": 150
      },
      {
        "metric_code": "EEE",
        "metric_name": "交易活跃度",
        "total_value": 80000000,
        "avg_value": 533333,
        "stock_count": 150
      }
    ]
  }
}
```

---

## 7. 导入模块 `/import`

### 7.1 上传文件

```
POST /import/upload
Content-Type: multipart/form-data
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| file | file | 是 | CSV或TXT文件 |
| file_type | string | 是 | CSV / TXT |
| metric_code | string | 否 | TXT文件的指标代码 |
| data_date | date | 否 | TXT文件的数据日期 |

**响应**:
```json
{
  "code": 0,
  "data": {
    "batch_id": 123,
    "file_name": "TTV_2025-08-21.txt",
    "status": "pending",
    "message": "文件上传成功，等待处理"
  }
}
```

### 7.2 导入进度查询

```
GET /import/batches/{batch_id}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "batch_id": 123,
    "file_name": "TTV_2025-08-21.txt",
    "status": "completed",
    "compute_status": "completed",
    "total_rows": 5597,
    "success_rows": 5590,
    "error_rows": 7,
    "started_at": "2025-08-21T10:00:00",
    "completed_at": "2025-08-21T10:01:30"
  }
}
```

### 7.3 导入批次列表

```
GET /import/batches
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| status | string | 否 | 状态筛选 |
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |

### 7.4 重新计算

```
POST /import/batches/{batch_id}/recompute
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "batch_id": 123,
    "compute_status": "computing",
    "message": "重新计算任务已启动"
  }
}
```

---

## 8. 指标模块 `/metrics`

### 8.1 指标类型列表

```
GET /metrics
```

**响应**:
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "code": "TTV",
      "name": "交易总值",
      "file_pattern": "*TTV*.txt",
      "is_active": true
    },
    {
      "id": 2,
      "code": "EEE",
      "name": "交易活跃度",
      "file_pattern": "*EEE*.txt",
      "is_active": true
    }
  ]
}
```

### 8.2 新增指标类型

```
POST /metrics
```

**请求**:
```json
{
  "code": "EFV",
  "name": "EFV指标",
  "file_pattern": "*EFV*.txt",
  "rank_order": "DESC"
}
```

---

## 9. 错误码定义

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| 40001 | 参数错误 |
| 40002 | 数据不存在 |
| 40003 | 文件格式错误 |
| 40101 | 未登录 |
| 40102 | Token过期 |
| 40103 | 权限不足 |
| 50001 | 服务器内部错误 |
| 50002 | 数据库错误 |
| 50003 | 导入任务失败 |

---

## 10. WebSocket接口

### 10.1 导入进度推送

```
WS /ws/import/{batch_id}
```

**消息格式**:
```json
{
  "type": "progress",
  "data": {
    "batch_id": 123,
    "status": "processing",
    "progress": 45,
    "processed_rows": 2500,
    "total_rows": 5597
  }
}
```

```json
{
  "type": "completed",
  "data": {
    "batch_id": 123,
    "status": "completed",
    "success_rows": 5590,
    "error_rows": 7
  }
}
```
