# 编码规范

---

## 1. 通用规范

### 1.1 命名规范

| 类型 | 规范 | 示例 |
|-----|------|------|
| 文件名 | 小写+下划线 | `stock_service.py` |
| 类名 | PascalCase | `StockService` |
| 函数/方法 | snake_case | `get_stock_by_code()` |
| 变量 | snake_case | `stock_code` |
| 常量 | 全大写+下划线 | `MAX_PAGE_SIZE` |
| 前端组件 | PascalCase | `StockList.vue` |

### 1.2 注释规范

```python
# 单行注释：解释复杂逻辑
# 不需要注释显而易见的代码

def calculate_rank(values: list[int]) -> list[int]:
    """
    计算排名

    Args:
        values: 数值列表

    Returns:
        排名列表（1开始）
    """
    pass
```

### 1.3 代码格式

- 缩进：4空格（Python）/ 2空格（JS/TS/Vue）
- 行宽：最大120字符
- 空行：函数间2行，类方法间1行

---

## 2. Python规范

### 2.1 导入顺序

```python
# 1. 标准库
import os
import json
from datetime import datetime

# 2. 第三方库
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. 本地模块
from app.models import Stock
from app.schemas import StockResponse
```

### 2.2 类型注解

```python
# 函数参数和返回值必须有类型注解
def get_stock(stock_code: str, db: Session) -> Stock | None:
    return db.query(Stock).filter(Stock.stock_code == stock_code).first()

# 复杂类型
from typing import Optional, List

def get_stocks(codes: List[str]) -> List[Stock]:
    pass
```

### 2.3 异常处理

```python
# 使用具体的异常类型
from fastapi import HTTPException

def get_stock(stock_code: str) -> Stock:
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    return stock

# 自定义异常
class StockNotFoundError(Exception):
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        super().__init__(f"Stock {stock_code} not found")
```

### 2.4 数据库操作

```python
# 使用Repository模式
class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, stock_code: str) -> Stock | None:
        return self.db.query(Stock).filter(
            Stock.stock_code == stock_code
        ).first()

    def create(self, stock_data: StockCreate) -> Stock:
        stock = Stock(**stock_data.dict())
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock

# 使用事务
from contextlib import contextmanager

@contextmanager
def transaction(db: Session):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
```

### 2.5 API路由

```python
from fastapi import APIRouter, Depends, Query
from app.schemas import StockResponse, StockListResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("", response_model=StockListResponse)
async def list_stocks(
    keyword: str = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """获取股票列表"""
    service = StockService(db)
    return service.list_stocks(keyword, page, page_size)
```

---

## 3. TypeScript/Vue规范

### 3.1 组件结构

```vue
<template>
  <div class="stock-list">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import type { Stock } from '@/types'

// 2. Props定义
const props = defineProps<{
  conceptId: number
}>()

// 3. Emits定义
const emit = defineEmits<{
  select: [stock: Stock]
}>()

// 4. 响应式数据
const stocks = ref<Stock[]>([])
const loading = ref(false)

// 5. 计算属性
const stockCount = computed(() => stocks.value.length)

// 6. 方法
async function fetchStocks() {
  loading.value = true
  try {
    stocks.value = await api.getStocks(props.conceptId)
  } finally {
    loading.value = false
  }
}

// 7. 生命周期
onMounted(() => {
  fetchStocks()
})
</script>

<style scoped>
.stock-list {
  /* 样式 */
}
</style>
```

### 3.2 类型定义

```typescript
// types/stock.ts
export interface Stock {
  stock_code: string
  stock_name: string
  exchange_prefix: string
}

export interface StockRanking {
  rank: number
  stock_code: string
  stock_name: string
  trade_value: number
  percentile: number
}

export interface StockListResponse {
  total: number
  items: Stock[]
}
```

### 3.3 API调用

```typescript
// api/stock.ts
import { request } from '@/utils/request'
import type { Stock, StockListResponse } from '@/types'

export const stockApi = {
  getList(params: { keyword?: string; page?: number }) {
    return request.get<StockListResponse>('/stocks', { params })
  },

  getDetail(stockCode: string) {
    return request.get<Stock>(`/stocks/${stockCode}`)
  },

  getConcepts(stockCode: string) {
    return request.get(`/stocks/${stockCode}/concepts`)
  },
}
```

### 3.4 状态管理（Pinia）

```typescript
// stores/stock.ts
import { defineStore } from 'pinia'
import { stockApi } from '@/api/stock'
import type { Stock } from '@/types'

export const useStockStore = defineStore('stock', {
  state: () => ({
    stocks: [] as Stock[],
    currentStock: null as Stock | null,
    loading: false,
  }),

  actions: {
    async fetchStocks(keyword?: string) {
      this.loading = true
      try {
        const { items } = await stockApi.getList({ keyword })
        this.stocks = items
      } finally {
        this.loading = false
      }
    },

    async fetchStock(stockCode: string) {
      this.currentStock = await stockApi.getDetail(stockCode)
    },
  },
})
```

---

## 4. SQL规范

### 4.1 命名规范

```sql
-- 表名：小写+下划线，复数
CREATE TABLE stocks (...);
CREATE TABLE stock_concepts (...);

-- 字段名：小写+下划线
stock_code, trade_date, created_at

-- 索引名：idx_表名_字段名
CREATE INDEX idx_stocks_code ON stocks(stock_code);

-- 唯一索引：uk_表名_字段名
CREATE UNIQUE INDEX uk_stocks_code ON stocks(stock_code);
```

### 4.2 查询规范

```sql
-- 使用明确的字段列表
SELECT stock_code, stock_name, trade_value
FROM stocks
WHERE stock_code = '600000';

-- 避免 SELECT *
-- BAD
SELECT * FROM stocks;

-- 使用参数化查询（防SQL注入）
-- Python
cursor.execute("SELECT * FROM stocks WHERE stock_code = %s", (stock_code,))

-- 大表查询必须使用索引
EXPLAIN ANALYZE SELECT * FROM concept_stock_daily_rank
WHERE stock_code = '600000' AND trade_date = '2025-08-21';
```

---

## 5. Git提交规范

### 5.1 Commit Message格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**:
```
feat(import): 添加CSV文件导入功能

- 支持股票-概念映射CSV导入
- 添加数据校验
- 自动创建新概念

Closes #123
```

### 5.2 分支命名

```
feature/import-csv       # 新功能
fix/ranking-calculation  # Bug修复
docs/api-documentation   # 文档
refactor/service-layer   # 重构
```

---

## 6. 代码审查清单

### 功能检查
- [ ] 功能是否符合需求
- [ ] 边界情况是否处理
- [ ] 错误处理是否完善

### 代码质量
- [ ] 命名是否清晰
- [ ] 是否有重复代码
- [ ] 函数是否过长（>50行）
- [ ] 是否有硬编码

### 安全检查
- [ ] 是否有SQL注入风险
- [ ] 是否有XSS风险
- [ ] 敏感信息是否暴露
- [ ] 权限检查是否完整

### 性能检查
- [ ] 是否有N+1查询
- [ ] 是否使用了索引
- [ ] 是否有不必要的循环
