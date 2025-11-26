# 📊 概念股票排名范围查询 API

## 接口说明

### 获取概念中日期范围内的股票排名

**端点**：`GET /api/v1/rankings/concept/{concept_id}/stocks-in-range`

**功能**：查询指定概念在日期范围内的股票排名，支持两种模式：
1. **最新日期模式**（推荐）：返回范围内最新日期的股票排名
2. **聚合模式**：返回范围内所有数据的聚合统计（平均排名、最佳排名等）

---

## 请求参数

### 路径参数
- `concept_id` (integer, required): 概念ID，例如 `1`

### 查询参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `start_date` | date | ✅ | - | 日期范围开始（YYYY-MM-DD） |
| `end_date` | date | ✅ | - | 日期范围结束（YYYY-MM-DD） |
| `metric_code` | string | ❌ | `TTV` | 指标代码（如 TTV、EEE） |
| `limit` | integer | ❌ | `100` | 返回的最大股票数（1-500） |
| `use_latest_date` | boolean | ❌ | `true` | 是否使用范围内最新日期；false 返回聚合数据 |

---

## 响应示例

### 模式 1：最新日期模式（use_latest_date=true）

**请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range?start_date=2025-11-01&end_date=2025-11-10&metric_code=TTV&limit=5&use_latest_date=true"
```

**响应** (200 OK)：
```json
{
  "concept_id": 1,
  "concept_name": "消费电子",
  "metric_code": "TTV",
  "start_date": "2025-11-01",
  "end_date": "2025-11-10",
  "query_date": "2025-11-10",
  "total_stocks": 5,
  "stocks": [
    {
      "stock_code": "600130",
      "stock_name": "*ST波导",
      "rank": 1,
      "trade_value": 0,
      "percentile": 100.0,
      "trade_date": "2025-11-10"
    },
    {
      "stock_code": "600203",
      "stock_name": "福日电子",
      "rank": 2,
      "trade_value": 0,
      "percentile": 98.98,
      "trade_date": "2025-11-10"
    },
    {
      "stock_code": "600745",
      "stock_name": "闻泰科技",
      "rank": 3,
      "trade_value": 0,
      "percentile": 97.96,
      "trade_date": "2025-11-10"
    }
  ]
}
```

### 模式 2：聚合模式（use_latest_date=false）

**请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range?start_date=2025-11-01&end_date=2025-11-10&metric_code=TTV&limit=5&use_latest_date=false"
```

**响应** (200 OK)：
```json
{
  "concept_id": 1,
  "concept_name": "消费电子",
  "metric_code": "TTV",
  "start_date": "2025-11-01",
  "end_date": "2025-11-10",
  "query_date": null,
  "total_stocks": 5,
  "stocks": [
    {
      "stock_code": "002475",
      "stock_name": "立讯精密",
      "rank": 1,
      "trade_value": 22,
      "percentile": null,
      "trade_date": null
    },
    {
      "stock_code": "300857",
      "stock_name": "协创数据",
      "rank": 1,
      "trade_value": 8,
      "percentile": null,
      "trade_date": null
    }
  ]
}
```

---

## 响应字段说明

### 顶级字段

| 字段 | 类型 | 说明 |
|------|------|------|
| concept_id | integer | 概念ID |
| concept_name | string | 概念名称 |
| metric_code | string | 查询的指标代码 |
| start_date | date | 查询范围开始日期 |
| end_date | date | 查询范围结束日期 |
| query_date | date \| null | 实际查询的日期（最新日期模式）；null 表示聚合模式 |
| total_stocks | integer | 返回的股票数量 |
| stocks | array | 股票排名列表 |

### stocks[] 数组字段

| 字段 | 类型 | 说明（最新日期模式） | 说明（聚合模式） |
|------|------|--------|---------|
| stock_code | string | 股票代码 | 股票代码 |
| stock_name | string | 股票名称 | 股票名称 |
| rank | integer | 股票排名 | **最佳排名**（日期范围内最好的排名） |
| trade_value | integer | 交易值 | **平均交易值**（日期范围内的平均值） |
| percentile | float | 百分位数 | null（聚合模式无此数据） |
| trade_date | date | 查询日期 | null（聚合模式无此数据） |

---

## 使用场景

### 场景 1：查询最新排名
获取某个概念在最近一个交易日的股票排名：

```bash
curl -X GET "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range?start_date=2025-11-01&end_date=2025-11-10&metric_code=TTV&use_latest_date=true"
```

**用途**：
- 获取概念中表现最好的股票
- 了解概念的最新成分股排名
- 动态更新概念排名信息

### 场景 2：分析时间段内的表现
获取某个概念在整个时间段内的聚合排名数据：

```bash
curl -X GET "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range?start_date=2025-11-01&end_date=2025-11-10&metric_code=TTV&use_latest_date=false"
```

**用途**：
- 找出在时间段内**表现最稳定**的股票（最佳排名好）
- 分析股票在概念中的**平均表现**
- 识别表现持续优异的成分股

### 场景 3：不同指标对比
对比不同指标下的排名：

```bash
# 使用 TTV 指标
curl -X GET "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range?start_date=2025-11-01&end_date=2025-11-10&metric_code=TTV"

# 使用 EEE 指标
curl -X GET "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range?start_date=2025-11-01&end_date=2025-11-10&metric_code=EEE"
```

---

## 错误响应

### 概念不存在 (404 Not Found)
```json
{
  "detail": "Concept 999 not found"
}
```

### 无数据 (200 OK，空列表)
如果指定的日期范围内没有数据：
```json
{
  "concept_id": 1,
  "concept_name": "消费电子",
  "metric_code": "TTV",
  "start_date": "2025-01-01",
  "end_date": "2025-01-10",
  "query_date": null,
  "total_stocks": 0,
  "stocks": []
}
```

---

## 实现细节

**文件位置**：
- API 实现：`backend/app/api/rankings.py:230-385`
- Response Schema：`backend/app/schemas/stock.py:234-256`

**关键特性**：
- ✅ 两种查询模式（最新日期 vs 聚合）
- ✅ 性能优化（使用 MAX() 查询获取最新日期，避免全表扫描）
- ✅ 数据聚合（支持平均值、最佳值等统计）
- ✅ 完整的错误处理
- ✅ 支持多个指标代码

**数据库查询**：

模式 1（最新日期）：
```sql
-- Step 1: 获取范围内最新日期
SELECT MAX(trade_date) FROM concept_stock_daily_rank
WHERE concept_id = ? AND metric_code = ?
  AND trade_date BETWEEN ? AND ?

-- Step 2: 获取该日期的排名
SELECT * FROM concept_stock_daily_rank
WHERE concept_id = ? AND trade_date = ? AND metric_code = ?
ORDER BY trade_value DESC
```

模式 2（聚合）：
```sql
SELECT stock_code,
       AVG(trade_value) as avg_trade_value,
       MIN(rank) as best_rank,
       COUNT(DISTINCT trade_date) as trading_days
FROM concept_stock_daily_rank
WHERE concept_id = ? AND metric_code = ?
  AND trade_date BETWEEN ? AND ?
GROUP BY stock_code
ORDER BY AVG(trade_value) DESC
```

---

## 与其他接口的关系

| 接口 | 用途 | 返回数据 |
|------|------|---------|
| `GET /rankings/concept/{id}` | 单个日期的概念排名 | 指定日期的所有股票排名 |
| **`GET /rankings/concept/{id}/stocks-in-range`** | **日期范围的概念排名** | **最新或聚合的股票排名** |
| `GET /rankings/stock/{code}` | 股票在概念中的历史 | 时间序列排名数据 |

---

## Python 调用示例

```python
import requests
from datetime import date

# 最新日期模式
response = requests.get(
    "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range",
    params={
        "start_date": "2025-11-01",
        "end_date": "2025-11-10",
        "metric_code": "TTV",
        "limit": 10,
        "use_latest_date": True
    }
)

data = response.json()
print(f"概念：{data['concept_name']}")
print(f"查询日期：{data['query_date']}")
for stock in data['stocks']:
    print(f"  {stock['stock_code']} {stock['stock_name']}: 排名 #{stock['rank']}")

# 聚合模式
response = requests.get(
    "http://localhost:8000/api/v1/rankings/concept/1/stocks-in-range",
    params={
        "start_date": "2025-11-01",
        "end_date": "2025-11-10",
        "metric_code": "TTV",
        "use_latest_date": False
    }
)

data = response.json()
print(f"\n{data['start_date']} 到 {data['end_date']} 平均表现：")
for stock in data['stocks']:
    print(f"  {stock['stock_code']}: 最佳排名 #{stock['rank']}, 平均交易值 {stock['trade_value']}")
```

---

## 测试步骤

1. **启动后端**：确保 API 服务运行在 http://localhost:8000

2. **访问 Swagger UI**：
   ```
   http://localhost:8000/api/docs
   ```

3. **找到新接口**：
   - 在 "Rankings" 部分找到 `GET /rankings/concept/{concept_id}/stocks-in-range`

4. **填写参数并测试**：
   ```
   concept_id: 1
   start_date: 2025-11-01
   end_date: 2025-11-10
   metric_code: TTV
   use_latest_date: true
   ```

---

**创建日期**：2025-01-26
**版本**：v1.0.0
**状态**：✅ 已实现并测试
