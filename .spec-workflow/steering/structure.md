# Project Structure

## Directory Organization

```
stock-analysis/                               # 项目根目录
├── frontend/                                  # 前端 Vue 3 应用
│   ├── src/
│   │   ├── api/                              # API 服务模块
│   │   │   ├── index.ts                      # API 客户端入口
│   │   │   ├── stock.ts                      # 股票 API（获取列表、详情）
│   │   │   ├── concept.ts                    # 概念 API
│   │   │   ├── ranking.ts                    # 排名 API
│   │   │   └── user.ts                       # 用户相关 API（登录、认证）
│   │   ├── components/                       # 可复用组件
│   │   │   ├── Navbar.vue
│   │   │   ├── Footer.vue
│   │   │   └── [其他通用组件]
│   │   ├── layouts/                          # 布局组件
│   │   │   ├── ClientLayout.vue              # 客户端（已登录）主布局
│   │   │   ├── AdminLayout.vue               # 管理员主布局
│   │   │   └── PublicLayout.vue              # 公开页面布局
│   │   ├── views/                            # 页面组件（路由视图）
│   │   │   ├── public/                       # 公开页面（无需登录）
│   │   │   │   ├── HomePage.vue              # 首页（已适配移动端）
│   │   │   │   ├── PublicStockList.vue       # 股票列表（已适配移动端）
│   │   │   │   ├── PublicStockDetail.vue     # 股票详情
│   │   │   │   ├── PublicConceptList.vue     # 概念列表
│   │   │   │   ├── PublicConceptDetail.vue   # 概念详情
│   │   │   │   ├── PublicRankingView.vue     # 排名榜单
│   │   │   │   └── AboutPage.vue             # 关于我们
│   │   │   ├── reports/                      # 客户端报表页面（需登录）
│   │   │   │   ├── Dashboard.vue             # 报表总览
│   │   │   │   ├── ConceptStockRanking.vue   # 概念排名分析
│   │   │   │   ├── StockConceptTrend.vue     # 股票趋势
│   │   │   │   └── StockTopNAnalysis.vue     # Top N 分析
│   │   │   ├── analysis/                     # 数据分析页面（需登录）
│   │   │   │   ├── PortfolioAnalysis.vue     # 投资组合分析
│   │   │   │   └── PerformanceAnalysis.vue   # 业绩分析
│   │   │   ├── profile/                      # 用户个人中心（需登录）
│   │   │   │   ├── UserProfile.vue           # 用户信息
│   │   │   │   └── UserSettings.vue          # 账户设置
│   │   │   ├── admin/                        # 管理员页面（需管理员权限）
│   │   │   │   ├── Dashboard.vue             # 管理后台首页
│   │   │   │   ├── UserManagement.vue        # 用户管理
│   │   │   │   └── Settings.vue              # 系统设置
│   │   │   ├── stocks/                       # 股票管理（管理员）
│   │   │   │   ├── StockList.vue             # 股票列表管理
│   │   │   │   └── StockDetail.vue           # 股票详情编辑
│   │   │   ├── concepts/                     # 概念管理（管理员）
│   │   │   │   ├── ConceptList.vue           # 概念列表管理
│   │   │   │   └── ConceptDetail.vue         # 概念详情编辑
│   │   │   ├── rankings/                     # 排名管理（管理员）
│   │   │   │   └── RankingView.vue
│   │   │   ├── import/                       # 数据导入（管理员）
│   │   │   │   ├── ImportView.vue            # 导入界面
│   │   │   │   └── BatchList.vue             # 导入历史
│   │   │   ├── settings/                     # 系统设置（管理员）
│   │   │   │   └── AdminSettings.vue
│   │   │   ├── Login.vue                     # 用户登录
│   │   │   ├── AdminLogin.vue                # 管理员登录
│   │   │   ├── NotFound.vue                  # 404 页面
│   │   │   └── ErrorPage.vue                 # 错误页面
│   │   ├── router/
│   │   │   └── index.ts                      # 路由配置（三层路由：public/client/admin）
│   │   ├── stores/                           # Pinia 状态管理
│   │   │   ├── index.ts                      # 导出所有 store
│   │   │   └── auth.ts                       # 认证状态（用户信息、权限）
│   │   ├── styles/                           # 全局样式
│   │   │   ├── variables.css                 # CSS 变量（颜色、间距）
│   │   │   ├── reset.css                     # 重置样式
│   │   │   └── responsive.css                # 响应式工具类
│   │   ├── types/                            # TypeScript 类型定义
│   │   │   ├── index.ts                      # 通用类型导出
│   │   │   ├── api.ts                        # API 响应类型
│   │   │   ├── models.ts                     # 数据模型类型
│   │   │   └── enums.ts                      # 枚举类型
│   │   ├── utils/                            # 工具函数
│   │   │   ├── request.ts                    # API 请求封装（Axios 拦截器）
│   │   │   ├── format.ts                     # 数据格式化（日期、数字）
│   │   │   ├── storage.ts                    # 本地存储封装
│   │   │   └── common.ts                     # 通用工具函数
│   │   ├── App.vue                           # 根组件
│   │   └── main.ts                           # 应用入口
│   ├── public/                                # 静态资源（不被构建处理）
│   │   └── favicon.ico
│   ├── index.html                            # HTML 模板
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json                         # TypeScript 配置
│   ├── vite.config.ts                        # Vite 构建配置
│   ├── .env.example                          # 环境变量示例
│   └── README.md                             # 前端开发文档
│
├── backend/                                   # 后端 FastAPI 应用
│   ├── app/
│   │   ├── main.py                           # FastAPI 应用入口
│   │   ├── core/
│   │   │   ├── config.py                     # 配置管理（数据库、API 密钥等）
│   │   │   ├── database.py                   # 数据库连接和会话配置
│   │   │   ├── security.py                   # 认证和授权（JWT、密码哈希）
│   │   │   └── exceptions.py                 # 自定义异常
│   │   ├── models/
│   │   │   ├── user.py                       # 用户、角色、权限模型
│   │   │   ├── stock.py                      # 股票数据模型
│   │   │   ├── concept.py                    # 概念分类模型
│   │   │   ├── ranking.py                    # 排名数据模型
│   │   │   └── import_batch.py               # 数据导入批次模型
│   │   ├── schemas/                          # Pydantic 数据验证模型
│   │   │   ├── user.py                       # 用户请求/响应schema
│   │   │   ├── stock.py                      # 股票schema
│   │   │   ├── concept.py                    # 概念schema
│   │   │   └── common.py                     # 通用schema（分页、响应包装）
│   │   ├── routers/                          # API 路由处理器
│   │   │   ├── auth.py                       # 认证相关接口（登录、注册、刷新令牌）
│   │   │   ├── stocks.py                     # 股票管理接口
│   │   │   ├── concepts.py                   # 概念管理接口
│   │   │   ├── rankings.py                   # 排名查询接口
│   │   │   ├── reports.py                    # 报表生成接口
│   │   │   ├── analysis.py                   # 数据分析接口
│   │   │   ├── import.py                     # 数据导入接口
│   │   │   └── users.py                      # 用户管理接口（仅管理员）
│   │   ├── services/                         # 业务逻辑层
│   │   │   ├── stock_service.py              # 股票相关逻辑
│   │   │   ├── concept_service.py            # 概念相关逻辑
│   │   │   ├── user_service.py               # 用户相关逻辑
│   │   │   ├── auth_service.py               # 认证业务逻辑
│   │   │   ├── import_service.py             # 数据导入业务逻辑
│   │   │   └── report_service.py             # 报表生成业务逻辑
│   │   ├── middleware/
│   │   │   ├── auth.py                       # 认证中间件（验证 JWT）
│   │   │   ├── error_handler.py              # 异常处理中间件
│   │   │   └── logging.py                    # 日志中间件
│   │   ├── dependencies/
│   │   │   ├── auth.py                       # 依赖注入：获取当前用户
│   │   │   └── permissions.py                # 依赖注入：权限检查
│   │   └── utils/
│   │       ├── validators.py                 # 数据验证工具
│   │       ├── formatters.py                 # 数据格式化工具
│   │       └── common.py                     # 通用工具函数
│   │
│   ├── tasks/                                 # Celery 异步任务
│   │   ├── __init__.py
│   │   ├── celery_app.py                     # Celery 应用配置
│   │   ├── stock_tasks.py                    # 股票数据任务（定时获取、处理）
│   │   ├── import_tasks.py                   # 数据导入后台任务
│   │   └── report_tasks.py                   # 报表生成任务
│   │
│   ├── migrations/                            # 数据库迁移（如使用 Alembic）
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── scripts/                               # 管理脚本
│   │   ├── init_db.py                        # 初始化数据库
│   │   ├── seed_data.py                      # 填充测试数据
│   │   └── admin_setup.py                    # 创建管理员用户
│   │
│   ├── logs/                                  # 日志目录（.gitignore）
│   │
│   ├── requirements.txt                      # Python 依赖列表
│   ├── requirements-dev.txt                  # 开发依赖（pytest、flake8 等）
│   ├── .env.example                          # 环境变量示例
│   ├── .env                                  # 本地环境变量（.gitignore）
│   ├── main.py                               # 应用启动脚本（可选）
│   └── README.md                             # 后端开发文档
│
├── .spec-workflow/                           # 项目工作流文档
│   ├── steering/                             # 项目架构和状态文档
│   │   ├── product.md                        # 产品愿景和目标
│   │   ├── tech.md                           # 技术栈和架构决策
│   │   └── structure.md                      # 项目结构和编码规范
│   └── specs/                                # 功能规范文档
│
├── .gitignore
├── README.md                                 # 项目总览文档
└── docker-compose.yml                        # Docker 编排（可选）
```

## Naming Conventions

### 文件命名

**前端：**
- **Vue 组件** - PascalCase（`HomePage.vue`, `UserProfile.vue`）
- **API 模块** - camelCase（`stockApi.ts`, `userAuth.ts`）
- **工具文件** - camelCase（`formatDate.ts`, `validateForm.ts`）
- **Store 模块** - camelCase（`authStore.ts`, `userStore.ts`）
- **样式文件** - kebab-case（`responsive.css`, `variables.css`）
- **测试文件** - `[filename].test.ts` 或 `[filename].spec.ts`

**后端：**
- **模块/包** - snake_case（`stock_service.py`, `user_models.py`）
- **类** - PascalCase（`StockService`, `UserModel`, `ImportTask`）
- **函数/方法** - snake_case（`get_user_by_id()`, `validate_stock_data()`）
- **常量** - UPPER_SNAKE_CASE（`DATABASE_URL`, `MAX_UPLOAD_SIZE`）
- **配置文件** - snake_case（`database.py`, `security.py`）

### 代码命名

**前端：**
- **组件** - PascalCase（`<UserProfile />`, `<StockCard />`)
- **方法/函数** - camelCase（`fetchUserData()`, `handleFormSubmit()`)
- **变量** - camelCase（`userName`, `isLoading`, `stockList`)
- **常量** - UPPER_SNAKE_CASE（`API_BASE_URL`, `MAX_RETRIES`)
- **枚举** - PascalCase（`UserRole.ADMIN`, `StockStatus.ACTIVE`)

**后端：**
- **类** - PascalCase（`class User:`, `class StockService:`)
- **方法/函数** - snake_case（`def get_user()`, `async def create_stock()`)
- **变量** - snake_case（`user_id`, `stock_data`, `is_active`)
- **常量** - UPPER_SNAKE_CASE（`API_TIMEOUT`, `DB_POOL_SIZE`)

### API 路由命名

**RESTful 规范：**
```
GET    /api/v1/stocks              # 获取股票列表
POST   /api/v1/stocks              # 创建股票
GET    /api/v1/stocks/{id}         # 获取单个股票
PUT    /api/v1/stocks/{id}         # 更新股票
DELETE /api/v1/stocks/{id}         # 删除股票

GET    /api/v1/users/me            # 获取当前用户信息
POST   /api/v1/auth/login          # 用户登录
POST   /api/v1/auth/logout         # 用户登出
POST   /api/v1/auth/refresh        # 刷新令牌
```

## Import Patterns

### 前端导入顺序

```typescript
// 1. 外部依赖
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// 2. 第三方库
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 3. 内部模块 - API
import { stockApi, userApi } from '@/api'

// 4. 内部模块 - Components
import UserCard from '@/components/UserCard.vue'
import Header from '@/components/Header.vue'

// 5. 内部模块 - Stores
import { useAuthStore } from '@/stores'

// 6. 内部模块 - Types
import type { User, Stock } from '@/types'

// 7. 样式导入
import '@/styles/responsive.css'
```

### 后端导入顺序

```python
# 1. 标准库
from datetime import datetime
import os
from typing import List, Optional

# 2. 第三方库
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. 本地应用
from app.models import User, Stock
from app.schemas import UserSchema
from app.core.database import get_db
from app.core.security import verify_password
from app.services import user_service
```

## Code Structure Patterns

### Vue 组件组织结构

```typescript
<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { Stock } from '@/types'

// 2. 类型定义
interface FormData {
  name: string
  price: number
}

// 3. 响应式状态
const router = useRouter()
const stocks = ref<Stock[]>([])
const loading = ref(false)
const searchQuery = ref('')

// 4. 计算属性
const filteredStocks = computed(() => {
  return stocks.value.filter(s => s.name.includes(searchQuery.value))
})

// 5. 生命周期和事件处理
onMounted(async () => {
  await fetchStocks()
})

// 6. 业务逻辑函数
const fetchStocks = async () => {
  loading.value = true
  // ...
  loading.value = false
}

const handleSearch = () => {
  // ...
}
</script>

<template>
  <!-- 模板结构 -->
</template>

<style scoped>
/* 样式 */
</style>
```

### FastAPI 路由组织结构

```python
# routers/stocks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import StockSchema, StockCreateSchema
from app.services import stock_service
from app.core.database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/stocks",
    tags=["stocks"],
    dependencies=[Depends(get_current_user)]
)

# 1. 获取列表
@router.get("/", response_model=List[StockSchema])
async def list_stocks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取股票列表"""
    return stock_service.get_stocks(db, skip=skip, limit=limit)

# 2. 获取详情
@router.get("/{stock_id}", response_model=StockSchema)
async def get_stock(stock_id: int, db: Session = Depends(get_db)):
    """获取单个股票详情"""
    stock = stock_service.get_stock(db, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

# 3. 创建
@router.post("/", response_model=StockSchema)
async def create_stock(
    stock: StockCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建新股票"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return stock_service.create_stock(db, stock)
```

## Module Boundaries

### 模块依赖方向

```
Models（数据模型）
    ↑
Schemas（数据验证）
    ↑
Services（业务逻辑）
    ↑
Routers（API 接口）
    ↑
Frontend（前端应用）
```

**规则：**
1. 依赖方向单向向上（低层不依赖高层）
2. Services 层只依赖 Models 和外部库
3. Routers 层只依赖 Services、Schemas 和依赖注入
4. 业务逻辑在 Services 层，路由只处理 HTTP 问题

### 前端模块边界

```
Views（页面）
    ↑
Components（组件）
    ↑
Utils（工具函数）
    ↑
API（API 调用）
    ↑
Types（类型定义）
```

**规则：**
1. Views 只组装 Components，不包含业务逻辑
2. Components 接收 props，通过 emit 向上通信
3. API 模块统一管理所有后端通信
4. Utils 包含通用工具，无业务逻辑

## Code Size Guidelines

**前端：**
- **文件大小** - 单个组件 < 500 行（内容过多应拆分）
- **方法大小** - 单个方法 < 50 行（过长应提取函数）
- **嵌套深度** - 最多 4 层（过深应使用计算属性）

**后端：**
- **模块大小** - 单个文件 < 500 行（过大应拆分为子模块）
- **函数大小** - 单个函数 < 80 行（复杂逻辑应分解）
- **类大小** - 单个类 < 300 行（职责过多应继续拆分）
- **循环深度** - 最多 2 层嵌套（过深应提取函数）

## Documentation Standards

### 必需的文档

1. **README.md** - 项目总体介绍和快速开始
2. **API 文档** - FastAPI 自动生成 (Swagger UI)
3. **组件注释** - 复杂组件的 PropTypes 和用法注释
4. **函数文档** - 后端核心函数必须有 docstring

### 注释指南

**有用的注释：**
```typescript
// 这里需要特殊处理因为浏览器缓存问题
const cacheBustUrl = `${url}?t=${Date.now()}`
```

**无用的注释：**
```typescript
// 增加 1
count++
```

**Python docstring 示例：**
```python
def get_stocks_by_concept(db: Session, concept_id: int) -> List[Stock]:
    """
    获取某个概念下的所有股票。

    Args:
        db: 数据库会话
        concept_id: 概念 ID

    Returns:
        股票列表，按涨幅倒序排列

    Raises:
        ValueError: 如果 concept_id 不存在
    """
    # 实现...
```

## 响应式设计断点

媒体查询统一使用以下三个断点：

```css
/* 移动端：默认（< 768px） */
.element {
  font-size: 14px;
  padding: 16px;
}

/* 平板：768px+ */
@media (min-width: 768px) {
  .element {
    font-size: 15px;
    padding: 20px;
  }
}

/* PC：1024px+ */
@media (min-width: 1024px) {
  .element {
    font-size: 16px;
    padding: 24px;
  }
}
```

## 开发工作流程

### 本地开发启动

**前端：**
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

**后端：**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# API 文档：http://localhost:8000/docs
```

### 换机器开发步骤

1. Clone 项目仓库
2. 按上述启动步骤初始化前后端环境
3. 参考 `.env.example` 配置本地环境变量
4. 运行 backend 初始化脚本：`python scripts/init_db.py`
5. 创建测试管理员用户：`python scripts/admin_setup.py`
6. 前后端同时启动，开始开发

### Git 工作流

**分支策略：**
- `main` - 主分支，仅接收来自 PR 的更新，受保护
- `feature/*` - 功能分支，从 main 创建，完成后 PR 合并回 main
- `bugfix/*` - 修复分支，紧急修复直接合并

**提交规范：**
```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码风格调整
refactor: 代码重构
test: 添加测试
chore: 构建工具和依赖更新
```

## 关键文件快速导航

| 文件/目录 | 用途 | 维护者 |
|---------|------|-------|
| `frontend/src/router/index.ts` | 路由配置和权限控制 | 前端开发 |
| `frontend/src/api/` | API 调用封装 | 前端开发 |
| `backend/app/main.py` | FastAPI 应用配置 | 后端开发 |
| `backend/app/models/` | 数据库模型定义 | 后端开发 |
| `backend/app/routers/` | API 路由实现 | 后端开发 |
| `.spec-workflow/steering/` | 项目文档和架构 | 所有开发者 |
