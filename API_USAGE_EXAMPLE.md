# 📊 新增 API 接口使用指南

## 接口说明

### 获取股票及其概念（按价值排序）

**端点**：`GET /api/v1/stocks/{stock_code}/concepts-ranked`

**功能**：查询股票代码，返回股票代码、股票名称 + 所有概念（按交易值从高到低排序）

---

## 请求参数

### 路径参数
- `stock_code` (string, required): 股票代码，例如 `600000`

### 查询参数
- `trade_date` (date, required): 交易日期，格式 `YYYY-MM-DD`，例如 `2025-01-15`
- `metric_code` (string, optional): 指标代码，默认值 `TTV`，可选值如 `EEE` 等

---

## 响应示例

### 请求
```bash
curl -X GET "http://localhost:8000/api/v1/stocks/600000/concepts-ranked?trade_date=2025-01-15&metric_code=TTV"
```

### 响应 (200 OK)
```json
{
  "stock_code": "600000",
  "stock_name": "浦发银行",
  "exchange_prefix": "SH",
  "trade_date": "2025-01-15",
  "metric_code": "TTV",
  "total_concepts": 8,
  "concepts": [
    {
      "id": 1,
      "concept_name": "金融科技",
      "category": "金融",
      "trade_value": 99999,
      "rank": 1,
      "percentile": 95.5
    },
    {
      "id": 2,
      "concept_name": "区域金融",
      "category": "金融",
      "trade_value": 88888,
      "rank": 2,
      "percentile": 88.2
    },
    {
      "id": 3,
      "concept_name": "上证50",
      "category": "指数成分",
      "trade_value": 77777,
      "rank": 3,
      "percentile": 80.1
    }
  ]
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| stock_code | string | 股票代码 |
| stock_name | string | 股票名称 |
| exchange_prefix | string | 交易所代码 (SH/SZ/BJ) |
| trade_date | date | 查询的交易日期 |
| metric_code | string | 查询的指标代码 |
| total_concepts | integer | 概念总数 |
| concepts | array | 概念列表 |
| concepts[].id | integer | 概念 ID |
| concepts[].concept_name | string | 概念名称 |
| concepts[].category | string | 概念分类 |
| concepts[].trade_value | integer | 交易值（按此字段降序排列） |
| concepts[].rank | integer | 概念内的股票排名 |
| concepts[].percentile | float | 百分位数 |

---

## 错误响应

### 股票不存在 (404 Not Found)
```json
{
  "detail": "Stock 600001 not found"
}
```

### 无数据 (返回空列表)
如果指定的日期没有数据，返回空的概念列表：
```json
{
  "stock_code": "600000",
  "stock_name": "浦发银行",
  "exchange_prefix": "SH",
  "trade_date": "2025-01-15",
  "metric_code": "TTV",
  "total_concepts": 0,
  "concepts": []
}
```

---

## 使用场景

### 场景 1：查询最新的概念排名
```bash
# 查询 600000（浦发银行）在 2025-01-15 的所有概念排名（使用 TTV 指标）
curl -X GET "http://localhost:8000/api/v1/stocks/600000/concepts-ranked?trade_date=2025-01-15&metric_code=TTV"
```

### 场景 2：使用不同指标查询
```bash
# 使用 EEE 指标查询相同股票的概念排名
curl -X GET "http://localhost:8000/api/v1/stocks/600000/concepts-ranked?trade_date=2025-01-15&metric_code=EEE"
```

### 场景 3：查询不同日期
```bash
# 查询另一个日期的概念排名
curl -X GET "http://localhost:8000/api/v1/stocks/600000/concepts-ranked?trade_date=2025-01-14&metric_code=TTV"
```

---

## 性能特性

✅ **性能优化**：
- 使用指定的 `trade_date` 而不是子查询获取最新日期，避免全表扫描
- 指定 `metric_code` 明确查询范围，充分利用数据库索引
- 使用 LEFT JOIN（outerjoin），确保即使没有排名数据也返回概念信息

**数据库查询优化**：
```sql
-- 使用索引：idx_rank_stock_concept_date(stock_code, concept_id, trade_date)
-- 条件 WHERE 子句充分利用索引过滤
SELECT c.id, c.concept_name, c.category,
       csdr.trade_value, csdr.rank, csdr.percentile
FROM stocks s
JOIN stock_concepts sc ON s.stock_code = sc.stock_code
JOIN concepts c ON sc.concept_id = c.id
LEFT JOIN concept_stock_daily_rank csdr
  ON csdr.stock_code = s.stock_code
  AND csdr.concept_id = c.id
  AND csdr.trade_date = '2025-01-15'
  AND csdr.metric_code = 'TTV'
WHERE s.stock_code = '600000'
ORDER BY csdr.trade_value DESC NULLS LAST
```

---

## 与其他接口的关系

| 接口 | 用途 | 差异 |
|------|------|------|
| `GET /stocks/{stock_code}` | 获取股票基本信息 + 概念 | 返回的概念无排名数据，无排序 |
| `GET /stocks/{stock_code}/concepts` | 获取股票的所有概念 | 返回概念列表，无排名数据 |
| `GET /stocks/{stock_code}/concepts-ranked` | **新增** | 返回概念列表 + 排名数据，按交易值排序 |
| `GET /rankings/concept/{concept_id}` | 获取概念的股票排名 | 按概念维度查询排名 |

---

## 实现细节

**文件位置**：
- API 实现：`backend/app/api/stocks.py:134-208`
- Response Schema：`backend/app/schemas/stock.py:210-231`
- 数据模型：`backend/app/models/stock.py`（Stock, Concept, StockConcept, ConceptStockDailyRank）

**关键代码**：
```python
@router.get("/{stock_code}/concepts-ranked", response_model=StockConceptsRankedResponse)
async def get_stock_concepts_ranked(
    stock_code: str,
    trade_date: date = Query(..., description="Trade date (YYYY-MM-DD)"),
    metric_code: str = Query("TTV", description="Metric code (e.g., TTV, EEE)"),
    db: Session = Depends(get_db),
):
    """Get concepts for a stock sorted by trade value (high to low)."""
    # ...查询逻辑...
```

---

## 测试步骤

1. **启动后端服务**
   ```bash
   cd backend
   python main.py
   ```

2. **访问 API 文档**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

3. **在 Swagger 中测试接口**
   - 打开 Swagger UI
   - 找到 `GET /stocks/{stock_code}/concepts-ranked` 端点
   - 输入参数并执行

4. **使用 curl 测试**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/stocks/600000/concepts-ranked?trade_date=2025-01-15&metric_code=TTV"
   ```

---

**创建日期**：2025-01-26
**版本**：v1.0.0
