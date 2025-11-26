# 🏗️ 系统架构概览

## 整体架构

你的系统**不仅仅是 API + 管理后台**，而是一个**完整的企业级股票分析平台**，包含多个独立的组件和模块。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        股票分析系统架构                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐          ┌──────────────────────┐
│     前端管理界面       │          │    数据导入系统       │
│   (Frontend)         │          │  (Import Scripts)    │
│  • React/Vue UI      │          │  • CSV 导入           │
│  • 用户交互          │          │  • TXT 导入           │
│  • 数据展示          │          │  • 批量处理           │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                  │
           │      HTTP/REST                   │      Python
           │                                  │      Direct DB
           ├──────────────────┬───────────────┤
           │                  │               │
      ┌────▼─────────────────────────────────▼──────┐
      │         API 后端服务（FastAPI）             │
      │                                              │
      │  ┌─────────────────────────────────────┐   │
      │  │        API 路由（Routes）            │   │
      │  │  • /auth - 认证                      │   │
      │  │  • /stocks - 股票管理                │   │
      │  │  • /concepts - 概念管理              │   │
      │  │  • /rankings - 排名查询              │   │
      │  │  • /summaries - 数据汇总             │   │
      │  │  • /import - 数据导入                │   │
      │  └─────────────────────────────────────┘   │
      │                                              │
      │  ┌─────────────────────────────────────┐   │
      │  │      业务逻辑层（Services）         │   │
      │  │  • ImportService                    │   │
      │  │  • ComputeService                   │   │
      │  │  • CacheService                     │   │
      │  └─────────────────────────────────────┘   │
      │                                              │
      └────┬──────────────────────────────────┬─────┘
           │                                  │
           │                                  │
   ┌───────▼────────────┐          ┌─────────▼─────────┐
   │   PostgreSQL DB    │          │   Redis Cache     │
   │   (数据存储)        │          │  (会话/缓存)      │
   │                    │          │                   │
   │ • users            │          │ • 会话数据        │
   │ • stocks           │          │ • 查询缓存        │
   │ • concepts         │          │ • 任务队列        │
   │ • rankings         │          │                   │
   │ • metrics          │          └───────────────────┘
   │ • import_batches   │
   └────────────────────┘


   ┌──────────────────────────────────────────────────┐
   │      后台任务系统（Celery Workers）             │
   │  • 批量导入任务                                   │
   │  • 数据计算任务                                   │
   │  • 异步处理                                       │
   └──────────────────────────────────────────────────┘
```

---

## 📊 详细组件说明

### 1️⃣ **前端管理界面** (Frontend)
**技术栈**：Vue 3 + TypeScript + Vite

**功能模块**：
| 模块 | 功能 |
|------|------|
| **Login** | 用户认证 |
| **Stocks** | 股票查询、搜索、详情展示 |
| **Concepts** | 概念管理、概念成分股查看 |
| **Rankings** | 排名数据展示、趋势分析 |
| **Import** | 数据导入界面、进度跟踪 |

**特点**：
- ✅ 提供友好的用户界面
- ✅ 实时数据展示
- ✅ 图表和数据可视化
- ✅ 数据导入向导

**启动方式**：
```bash
npm run dev  # 开发模式
npm run build  # 生产构建
```

---

### 2️⃣ **API 后端** (Backend API)
**技术栈**：Python 3.11 + FastAPI + SQLAlchemy

**API 模块**（`backend/app/api/`）：

#### 🔐 认证 (`auth.py`)
```
POST   /auth/login              - 用户登录
POST   /auth/refresh            - 刷新 Token
POST   /auth/logout             - 用户登出
GET    /auth/me                 - 获取当前用户
POST   /auth/register           - 用户注册
```

#### 📈 股票 (`stocks.py`)
```
GET    /stocks                  - 列表（分页、搜索）
GET    /stocks/{stock_code}     - 股票详情
GET    /stocks/{stock_code}/concepts                  - 获取股票的所有概念
GET    /stocks/{stock_code}/concepts-ranked           - ⭐ 获取概念（按价值排序）
```

#### 💡 概念 (`concepts.py`)
```
GET    /concepts                - 概念列表
GET    /concepts/{concept_id}   - 概念详情
GET    /concepts/{concept_id}/stocks  - 获取概念的股票
```

#### 📊 排名 (`rankings.py`)
```
GET    /rankings/concept/{concept_id}                 - 特定日期排名
GET    /rankings/stock/{stock_code}                   - 股票排名历史
GET    /rankings/stock/{stock_code}/top-n-count      - Top N 统计
GET    /rankings/concept/{concept_id}/stocks-in-range - ⭐ 日期范围内的股票排名
```

#### 📈 汇总 (`summaries.py`)
```
GET    /summaries/concept/{concept_id}        - 概念日期汇总
GET    /summaries/concept/{concept_id}/compare - 指标对比
```

#### 📥 导入 (`imports.py`)
```
POST   /import/upload           - 上传文件
GET    /import/batches          - 导入批次列表
GET    /import/batches/{batch_id} - 批次详情
POST   /import/batches/{batch_id}/recompute - 重新计算
GET    /import/metrics          - 支持的指标列表
```

**特点**：
- ✅ RESTful 设计
- ✅ JWT 认证
- ✅ 请求验证
- ✅ 错误处理
- ✅ 自动 API 文档（Swagger）

**访问 API 文档**：
```
http://localhost:8000/api/docs          (Swagger UI)
http://localhost:8000/api/redoc         (ReDoc)
```

---

### 3️⃣ **数据导入系统** (Import Scripts)
**位置**：`imports/` 目录
**语言**：Python

**导入工具**：

#### 直接导入 (`direct_import.py`)
```bash
# CSV 导入（股票-概念映射）
python direct_import.py <file.csv> --type CSV

# TXT 导入（交易数据）
python direct_import.py <file.txt> --type TXT --metric-code EEE
```

**用途**：单文件、小文件导入

#### 批量导入 (`batch_import.py`)
```bash
# 批量导入（多日期大文件）
python batch_import.py <file.txt> --metric-code EEE --parallel 8

# 继续中断的导入
python batch_import.py <file.txt> --metric-code EEE --resume
```

**用途**：大文件、多日期数据的并行导入

**特点**：
- ✅ 支持多种格式（CSV、TXT）
- ✅ 并行处理（加快导入速度）
- ✅ 断点续传
- ✅ 进度跟踪
- ✅ 错误恢复

---

### 4️⃣ **数据库** (PostgreSQL)
**主要表**：

```sql
-- 基础数据
stocks              - 股票信息
concepts            - 概念定义
industries          - 行业分类

-- 关系表
stock_concepts      - 股票-概念映射
stock_industries    - 股票-行业映射

-- 用户和权限
users               - 用户账户
roles               - 用户角色
permissions         - 权限定义

-- 交易数据
stock_metric_data_raw        - 原始指标数据（分区表）
concept_stock_daily_rank     - 每日排名（分区表）
concept_daily_summary        - 每日汇总

-- 系统表
import_batches      - 导入批次跟踪
metric_types        - 指标类型定义
```

**分区策略**：
- `stock_metric_data_raw` - 按 `trade_date` 月度分区
- `concept_stock_daily_rank` - 按 `trade_date` 月度分区

---

### 5️⃣ **缓存系统** (Redis)
**用途**：

```
redis://localhost:6379/0     - 会话和通用缓存
redis://localhost:6379/1     - Celery 消息队列
redis://localhost:6379/2     - Celery 结果存储
```

**缓存项**：
- 用户会话
- API 查询结果
- 计算结果

---

### 6️⃣ **任务队列** (Celery)
**消息队列**：Redis
**用途**：

```
• 后台导入任务
• 数据计算任务
• 异步报告生成
```

**启动方式**：
```bash
bash scripts/setup/start.sh celery
```

---

### 7️⃣ **脚本和工具**

#### 初始化脚本 (`scripts/setup/`)
```bash
init.sh           - 完整项目初始化
init-db.sh        - 数据库初始化
start.sh          - 服务启动管理
```

#### 快速命令 (`quick_commands.sh`)
```bash
import_csv <file>                  - 导入 CSV
import_txt <file> <code>          - 导入 TXT
batch_import <file> <code> [n]    - 批量导入
create_partitions                 - 创建分区
optimize_indexes                  - 优化索引
check_progress <code>             - 查看进度
```

---

## 🔄 数据流

### 导入流程
```
用户上传文件（Frontend）
        ↓
API 接收并验证（/import/upload）
        ↓
创建 ImportBatch 记录
        ↓
交由导入服务处理
        ↓
可选：提交到 Celery 任务队列（大文件）
        ↓
解析文件、验证数据
        ↓
插入 stock_metric_data_raw 表
        ↓
计算排名数据 → concept_stock_daily_rank
        ↓
计算汇总数据 → concept_daily_summary
        ↓
更新 ImportBatch 状态为完成
        ↓
缓存失效（Redis）
```

### 查询流程
```
Frontend 调用 API
        ↓
FastAPI 路由匹配
        ↓
检查认证、授权
        ↓
查询数据（可能命中缓存）
        ↓
数据验证、转换
        ↓
返回 JSON 响应
        ↓
Frontend 渲染展示
```

---

## 📱 使用者视图

### 不同角色的交互方式

```
┌─────────────┐
│   数据分析师   │
└──────┬──────┘
       │ 使用前端查询
       │ 导入新数据
       ↓
   ┌──────────────────┐
   │   前端管理界面     │
   └────────┬─────────┘
            │ 调用 REST API
            ↓
   ┌──────────────────┐
   │   API 后端       │
   └────────┬─────────┘
            │
            ↓
   ┌──────────────────┐
   │   数据库         │
   └──────────────────┘


┌──────────────┐
│  系统管理员    │
└──────┬───────┘
       │
       ├─ 数据库管理
       │  └─ 初始化、分区、索引优化
       │
       ├─ 服务管理
       │  └─ 启动/停止 API、Celery
       │
       └─ 配置管理
          └─ 环境变量、数据库连接


┌──────────────┐
│  开发人员      │
└──────┬───────┘
       │
       ├─ API 开发
       ├─ 前端开发
       ├─ 脚本优化
       └─ 数据库设计
```

---

## 🚀 启动和部署

### 本地开发启动
```bash
# 方式 1：启动所有服务
bash scripts/setup/start.sh all

# 方式 2：逐个启动
bash scripts/setup/start.sh backend    # 后端 API
bash scripts/setup/start.sh frontend   # 前端 UI
bash scripts/setup/start.sh celery     # 任务队列

# 检查状态
bash scripts/setup/start.sh status
```

### 访问地址
| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |

---

## 📦 核心技术栈

### 后端
- **框架**：FastAPI
- **ORM**：SQLAlchemy
- **数据库**：PostgreSQL
- **缓存**：Redis
- **任务队列**：Celery
- **认证**：JWT

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **路由**：Vue Router
- **状态管理**：Pinia/Vuex

### 数据处理
- **Python 3.11+**
- **Pandas**
- **SQLAlchemy**
- **并行处理**：multiprocessing

---

## 🎯 现状总结

**你的系统包括**：
- ✅ 1 个 **API 后端**（FastAPI）- 提供数据接口
- ✅ 1 个 **Web 管理界面**（Vue 3）- 用户交互
- ✅ 1 个 **数据导入系统**（Python scripts）- 数据摄入
- ✅ 1 个 **任务队列**（Celery）- 后台处理
- ✅ 1 个 **数据库**（PostgreSQL）- 数据存储
- ✅ 1 个 **缓存层**（Redis）- 性能优化

**这是一个完整的 3 层架构**：
1. **表现层**（Frontend）
2. **应用层**（API Backend）
3. **数据层**（Database + Cache）

---

**架构图生成日期**：2025-01-26
**版本**：v1.0
**状态**：正在积极开发
