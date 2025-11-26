# 股票概念分析系统 - 详细设计文档

**版本**: v1.0
**日期**: 2025-11-22
**作者**: Claude
**状态**: 设计评审中

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [需求分析](#2-需求分析)
3. [技术架构](#3-技术架构)
4. [数据库设计](#4-数据库设计)
5. [API接口设计](#5-api接口设计)
6. [前端设计](#6-前端设计)
7. [安全设计](#7-安全设计)
8. [性能优化](#8-性能优化)
9. [部署方案](#9-部署方案)
10. [开发计划](#10-开发计划)
11. [风险与挑战](#11-风险与挑战)
12. [待完善事项](#12-待完善事项)

---

## 1. 项目概述

### 1.1 项目背景

基于现有的股票概念数据和交易数据，开发一个综合分析系统，用于：
- 管理股票与概念的关联关系
- 分析股票在不同概念中的表现和排名
- 提供多维度的数据查询和可视化

### 1.2 核心目标

- **数据管理**: 便捷的CSV数据导入和管理
- **多维分析**: 支持6大核心分析需求
- **可视化**: 直观的图表和排名展示
- **权限控制**: 完整的用户和权限管理体系

### 1.3 用户角色

| 角色 | 权限范围 | 主要功能 |
|------|---------|---------|
| **超级管理员** | 全部权限 | 系统配置、用户管理、所有功能 |
| **管理员** | 数据管理 | 数据导入、查看、导出 |
| **分析师** | 高级查询 | 复杂分析、自定义报表 |
| **普通用户** | 基础查询 | 查看榜单、基础查询 |

---

## 2. 需求分析

### 2.1 功能需求清单

#### 核心功能模块

**模块A: 用户认证与管理**
- [ ] 用户登录/登出
- [ ] JWT Token认证
- [ ] 用户CRUD操作
- [ ] 角色分配
- [ ] 权限控制
- [ ] 操作日志记录

**模块B: 数据导入**
- [ ] CSV文件上传
- [ ] 数据格式验证
- [ ] 数据预览（前100行）
- [ ] 字段映射配置
- [ ] 异步导入任务
- [ ] 导入进度实时推送
- [ ] 导入历史记录
- [ ] 错误日志下载

**模块C: 数据查询**
- [ ] **需求1**: 查询股票所属的概念
- [ ] **需求2**: 股票在所属概念中每天的排名信息
- [ ] **需求3**: 概念中选定日期顺序排名的股票
- [ ] **需求4**: 股票在概念中日期范围内出现前几名的次数
- [ ] **需求5**: 股票在概念中日期范围内的排名信息
- [ ] **需求6**: 概念每日所有股票的求和

**模块D: 数据可视化**
- [ ] 股票排名趋势图
- [ ] 概念总量趋势图
- [ ] 排名榜单（日/周/月）
- [ ] 概念对比分析
- [ ] 热力图/相关性矩阵

**模块E: 报表导出**
- [ ] Excel导出
- [ ] CSV导出
- [ ] PDF报表生成

### 2.2 非功能需求

| 类别 | 要求 | 指标 |
|------|------|------|
| **性能** | 查询响应时间 | <500ms (P95) |
| **性能** | 导入处理能力 | 10万行/分钟 |
| **可用性** | 系统可用率 | ≥99% |
| **安全** | 密码强度 | 8位以上，包含字母数字 |
| **安全** | Token有效期 | 2小时(Access) / 7天(Refresh) |
| **扩展性** | 数据增长 | 支持到100万行 |

---

## 3. 技术架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                   客户端层                               │
├────────────────────┬────────────────────────────────────┤
│  后台管理端        │         用户展示端                  │
│  Vue 3 + Element   │      Vue 3 + Ant Design            │
│  Plus + ECharts    │      Vue + ECharts                 │
└────────────────────┴────────────────────────────────────┘
                       │ HTTPS/WSS
┌─────────────────────────────────────────────────────────┐
│                  Nginx (反向代理)                        │
│              静态资源 + API网关 + 负载均衡                │
└─────────────────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────────────┐
│               FastAPI 应用服务                           │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │认证服务  │查询服务  │导入服务  │统计服务  │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│                                                          │
│  ┌─────────────────────────────────────────┐            │
│  │      Celery Worker (异步任务)            │            │
│  │   - 数据导入  - 排名计算  - 报表生成     │            │
│  └─────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
                       │
┌──────────────┬──────────────┬──────────────┐
│  PostgreSQL  │    Redis     │    MinIO     │
│  (主数据库)  │   (缓存层)   │  (文件存储)  │
└──────────────┴──────────────┴──────────────┘
```

### 3.2 技术栈详细清单

#### 后端技术栈

| 组件 | 技术选型 | 版本 | 用途 |
|------|---------|------|------|
| **Web框架** | FastAPI | 0.115+ | 高性能异步API服务 |
| **Python** | Python | 3.11+ | 开发语言 |
| **ORM** | SQLAlchemy | 2.0+ | 数据库ORM |
| **数据验证** | Pydantic | 2.0+ | 数据模型验证 |
| **异步任务** | Celery | 5.3+ | 后台任务队列 |
| **认证** | python-jose | 3.3+ | JWT Token |
| **密码加密** | passlib + bcrypt | 1.7+ | 密码哈希 |
| **数据处理** | Pandas | 2.0+ | CSV数据处理 |
| **Excel处理** | openpyxl | 3.1+ | Excel读写 |
| **PDF生成** | ReportLab | 4.0+ | PDF报表 |
| **HTTP客户端** | httpx | 0.27+ | 异步HTTP |

#### 前端技术栈

| 组件 | 技术选型 | 版本 | 用途 |
|------|---------|------|------|
| **框架** | Vue 3 | 3.4+ | 前端框架 |
| **语言** | TypeScript | 5.0+ | 类型安全 |
| **构建工具** | Vite | 5.0+ | 快速构建 |
| **状态管理** | Pinia | 2.1+ | 状态管理 |
| **路由** | Vue Router | 4.0+ | 路由管理 |
| **UI库(后台)** | Element Plus | 2.8+ | 组件库 |
| **UI库(前台)** | Ant Design Vue | 4.0+ | 组件库 |
| **图表** | Apache ECharts | 5.5+ | 数据可视化 |
| **HTTP** | Axios | 1.6+ | HTTP请求 |
| **WebSocket** | socket.io-client | 4.7+ | 实时通信 |

#### 数据存储

| 组件 | 技术选型 | 版本 | 用途 |
|------|---------|------|------|
| **关系数据库** | PostgreSQL | 15+ | 主数据存储 |
| **缓存** | Redis | 7+ | 缓存、Session、队列 |
| **对象存储** | MinIO | latest | 文件存储 |

#### 部署运维

| 组件 | 技术选型 | 版本 | 用途 |
|------|---------|------|------|
| **容器化** | Docker | 24+ | 容器化 |
| **容器编排** | Docker Compose | 2.20+ | 本地编排 |
| **Web服务器** | Nginx | 1.25+ | 反向代理 |
| **ASGI服务器** | Uvicorn | 0.30+ | ASGI运行 |
| **进程管理** | Supervisor | 4.2+ | 进程守护 |

### 3.3 系统分层架构

```
┌─────────────────────────────────────────────┐
│           Presentation Layer                │  表示层
│  (Vue Components, Pages, Routes)            │
└─────────────────────────────────────────────┘
                    ↓ HTTP/REST
┌─────────────────────────────────────────────┐
│            API Gateway Layer                │  网关层
│         (Nginx, Rate Limiting)              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Application Layer                  │  应用层
│  ┌────────────────────────────────────┐     │
│  │  API Routers (FastAPI)             │     │
│  │  - /auth  - /stocks  - /concepts   │     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Service Layer                     │  业务层
│  ┌──────────┬──────────┬─────────────┐     │
│  │AuthSvc   │StockSvc  │ImportSvc    │     │
│  └──────────┴──────────┴─────────────┘     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Data Access Layer                   │  数据访问层
│  ┌────────────────────────────────────┐     │
│  │  Repository Pattern                │     │
│  │  SQLAlchemy ORM                    │     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Data Layer                        │  数据层
│  PostgreSQL + Redis + MinIO                 │
└─────────────────────────────────────────────┘
```

---

## 4. 数据库设计

### 4.1 ER图关系

```
Users ──< UserRoles >── Roles ──< RolePermissions >── Permissions

Stocks ──< StockConcepts >── Concepts
   │
   └──< StockIndustries >── Industries
   │
   └──< StockDailyData

Concepts ──< ConceptStockDailyRank
   │
   └──< ConceptDailySummary

Users ──< ImportRecords
  │
  └──< AuditLogs
```

### 4.2 详细表结构设计

#### 4.2.1 用户认证模块

**users - 用户表**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',  -- active, disabled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
```

**roles - 角色表**
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,  -- super_admin, admin, analyst, viewer
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始化默认角色
INSERT INTO roles (name, display_name, description) VALUES
('super_admin', '超级管理员', '拥有所有权限'),
('admin', '管理员', '数据管理权限'),
('analyst', '分析师', '高级查询权限'),
('viewer', '普通用户', '基础查询权限');
```

**user_roles - 用户角色关联表**
```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
```

**permissions - 权限表**
```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- stock:read, user:write
    resource VARCHAR(50) NOT NULL,      -- stock, user, concept
    action VARCHAR(20) NOT NULL,        -- read, write, delete, execute
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始化权限
INSERT INTO permissions (name, resource, action, description) VALUES
('stock:read', 'stock', 'read', '查看股票'),
('stock:write', 'stock', 'write', '编辑股票'),
('concept:read', 'concept', 'read', '查看概念'),
('user:read', 'user', 'read', '查看用户'),
('user:write', 'user', 'write', '管理用户'),
('import:execute', 'import', 'execute', '导入数据'),
('export:execute', 'export', 'execute', '导出数据');
```

**role_permissions - 角色权限关联表**
```sql
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
```

#### 4.2.2 业务数据模块

**stocks - 股票信息表**
```sql
CREATE TABLE stocks (
    stock_code VARCHAR(20) PRIMARY KEY,  -- 600000, 000001, 127111
    stock_name VARCHAR(100) NOT NULL,
    exchange VARCHAR(10),                 -- SH, SZ, BJ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stocks_name ON stocks(stock_name);
CREATE INDEX idx_stocks_exchange ON stocks(exchange);
```

**concepts - 概念表**
```sql
CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    concept_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),                -- 行业/板块/主题
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concepts_name ON concepts(concept_name);
CREATE INDEX idx_concepts_category ON concepts(category);
```

**industries - 行业表**
```sql
CREATE TABLE industries (
    id SERIAL PRIMARY KEY,
    industry_name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES industries(id),  -- 支持行业分级
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_industries_parent ON industries(parent_id);
```

**stock_concepts - 股票概念关联表**
```sql
CREATE TABLE stock_concepts (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code) ON DELETE CASCADE,
    concept_id INTEGER NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, concept_id)
);

CREATE INDEX idx_stock_concepts_stock ON stock_concepts(stock_code);
CREATE INDEX idx_stock_concepts_concept ON stock_concepts(concept_id);
```

**stock_industries - 股票行业关联表**
```sql
CREATE TABLE stock_industries (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code) ON DELETE CASCADE,
    industry_id INTEGER NOT NULL REFERENCES industries(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, industry_id)
);

CREATE INDEX idx_stock_industries_stock ON stock_industries(stock_code);
CREATE INDEX idx_stock_industries_industry ON stock_industries(industry_id);
```

**stock_daily_data - 每日交易数据表（分区表）**
```sql
CREATE TABLE stock_daily_data (
    id BIGSERIAL,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,
    trade_value BIGINT,              -- 交易数据/热度值
    price DECIMAL(10, 2),
    turnover_rate DECIMAL(6, 2),
    net_inflow DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建分区（按月）
CREATE TABLE stock_daily_data_2025_08 PARTITION OF stock_daily_data
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE stock_daily_data_2025_09 PARTITION OF stock_daily_data
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

-- 创建索引
CREATE UNIQUE INDEX idx_stock_daily_unique
    ON stock_daily_data(stock_code, trade_date);
CREATE INDEX idx_stock_daily_date ON stock_daily_data(trade_date);
CREATE INDEX idx_stock_daily_value ON stock_daily_data(trade_value DESC);
```

**concept_stock_daily_rank - 概念股票每日排名表（预计算）**
```sql
CREATE TABLE concept_stock_daily_rank (
    id BIGSERIAL,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(stock_code),
    trade_date DATE NOT NULL,
    trade_value BIGINT,
    rank INTEGER,                    -- 排名
    percentile DECIMAL(5, 2),       -- 百分位
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);

-- 创建分区
CREATE TABLE concept_stock_daily_rank_2025_08 PARTITION OF concept_stock_daily_rank
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

-- 创建索引
CREATE INDEX idx_concept_rank_composite
    ON concept_stock_daily_rank(concept_id, trade_date, rank);
CREATE INDEX idx_concept_rank_stock
    ON concept_stock_daily_rank(stock_code, concept_id, trade_date);
```

**concept_daily_summary - 概念每日汇总表**
```sql
CREATE TABLE concept_daily_summary (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    trade_date DATE NOT NULL,
    total_value BIGINT,              -- 总和
    stock_count INTEGER,             -- 股票数量
    avg_value BIGINT,                -- 平均值
    max_value BIGINT,                -- 最大值
    top_stock_code VARCHAR(20),      -- 最大值对应股票
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(concept_id, trade_date)
);

CREATE INDEX idx_concept_summary_concept ON concept_daily_summary(concept_id, trade_date);
CREATE INDEX idx_concept_summary_date ON concept_daily_summary(trade_date);
```

#### 4.2.3 系统管理模块

**import_records - 导入记录表**
```sql
CREATE TABLE import_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_path VARCHAR(500),
    import_type VARCHAR(50),         -- concept_mapping, daily_data
    import_mode VARCHAR(20),         -- full, increment
    status VARCHAR(20),              -- pending, processing, success, failed
    total_rows INTEGER,
    success_rows INTEGER,
    failed_rows INTEGER,
    error_log TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_import_user ON import_records(user_id);
CREATE INDEX idx_import_status ON import_records(status);
CREATE INDEX idx_import_created ON import_records(created_at DESC);
```

**audit_logs - 操作日志表**
```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,     -- login, import, export, query, update
    resource VARCHAR(100),           -- table name, API endpoint
    details JSONB,                   -- 详细信息
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_details ON audit_logs USING GIN (details);
```

### 4.3 数据库索引策略

| 表名 | 索引类型 | 字段 | 用途 |
|------|---------|------|------|
| users | B-tree | username, email | 登录查询 |
| stock_daily_data | B-tree | (stock_code, trade_date) | 唯一性 + 查询 |
| stock_daily_data | B-tree | trade_date | 日期范围查询 |
| concept_stock_daily_rank | B-tree | (concept_id, trade_date, rank) | 排名查询 |
| audit_logs | GIN | details | JSONB字段查询 |

### 4.4 数据完整性约束

**外键约束**:
- 所有关联表都使用外键约束
- 使用 `ON DELETE CASCADE` 保证数据一致性
- 避免孤儿数据

**唯一性约束**:
- username, email 唯一
- (stock_code, trade_date) 唯一
- (concept_id, trade_date) 唯一

**非空约束**:
- 关键业务字段必须非空
- 使用 DEFAULT 提供默认值

---

## 5. API接口设计

### 5.1 API设计原则

1. **RESTful规范**: 资源导向，使用HTTP动词
2. **版本控制**: `/api/v1/` 路径前缀
3. **统一响应格式**: JSON格式，包含code/message/data
4. **错误处理**: 标准HTTP状态码 + 业务错误码
5. **分页规范**: `page`, `page_size`, `total`
6. **认证**: Bearer Token (JWT)

### 5.2 响应格式规范

**成功响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        // 业务数据
    }
}
```

**失败响应**:
```json
{
    "code": 400,
    "message": "Invalid input",
    "error": {
        "field": "username",
        "detail": "Username already exists"
    }
}
```

**分页响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [...],
        "total": 1000,
        "page": 1,
        "page_size": 20,
        "total_pages": 50
    }
}
```

### 5.3 完整API清单

#### 5.3.1 认证模块 `/api/v1/auth`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/auth/login` | 用户登录 | `{username, password}` | `{access_token, refresh_token, user}` |
| POST | `/auth/logout` | 用户登出 | - | `{message}` |
| POST | `/auth/refresh` | 刷新Token | `{refresh_token}` | `{access_token}` |
| GET | `/auth/me` | 获取当前用户 | - | `{user, roles, permissions}` |
| PUT | `/auth/password` | 修改密码 | `{old_password, new_password}` | `{message}` |

#### 5.3.2 用户管理 `/api/v1/users`

| 方法 | 路径 | 说明 | 权限 | 参数 |
|------|------|------|------|------|
| GET | `/users` | 用户列表 | user:read | `?page=1&page_size=20&search=&status=` |
| POST | `/users` | 创建用户 | user:write | `{username, email, password, roles}` |
| GET | `/users/:id` | 用户详情 | user:read | - |
| PUT | `/users/:id` | 更新用户 | user:write | `{email, roles, ...}` |
| DELETE | `/users/:id` | 删除用户 | user:write | - |
| PUT | `/users/:id/status` | 启用/禁用 | user:write | `{status: "active"}` |
| GET | `/users/:id/logs` | 操作日志 | user:read | `?page=1&page_size=20` |

#### 5.3.3 数据导入 `/api/v1/import`

| 方法 | 路径 | 说明 | 权限 | 参数 |
|------|------|------|------|------|
| POST | `/import/upload` | 上传文件 | import:execute | `FormData: {file}` |
| POST | `/import/preview` | 数据预览 | import:execute | `{file_path, limit=100}` |
| POST | `/import/execute` | 执行导入 | import:execute | `{file_path, type, mode, mapping}` |
| GET | `/import/records` | 导入历史 | import:execute | `?page=1&status=` |
| GET | `/import/records/:id` | 导入详情 | import:execute | - |
| DELETE | `/import/records/:id` | 删除记录 | import:execute | - |

**WebSocket接口**:
- `ws://api/v1/import/progress/:task_id` - 实时推送导入进度

#### 5.3.4 股票查询 `/api/v1/stocks`

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/stocks` | 股票列表 | `?search=&concept=&industry=&page=1` |
| GET | `/stocks/:code` | 股票详情 | - |
| GET | `/stocks/:code/concepts` | **需求1**: 股票所属概念 | - |
| GET | `/stocks/:code/daily-data` | 每日数据 | `?start_date=&end_date=` |
| GET | `/stocks/:code/ranks` | 在各概念中的排名 | `?date=2025-08-21` |

**响应示例 - 需求1**:
```json
{
    "code": 200,
    "data": {
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "concepts": [
            {"id": 1, "name": "银行"},
            {"id": 2, "name": "上海板块"}
        ]
    }
}
```

#### 5.3.5 概念查询 `/api/v1/concepts`

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/concepts` | 概念列表 | `?category=&search=&page=1` |
| GET | `/concepts/:id` | 概念详情 | - |
| GET | `/concepts/:id/stocks` | 概念包含股票 | `?page=1` |
| GET | `/concepts/:id/daily-ranks` | **需求3**: 某日排名 | `?date=2025-08-21&limit=100` |
| GET | `/concepts/:id/daily-summary` | **需求6**: 每日汇总 | `?start_date=&end_date=` |

**响应示例 - 需求3**:
```json
{
    "code": 200,
    "data": {
        "concept_id": 1,
        "concept_name": "人工智能",
        "date": "2025-08-21",
        "rankings": [
            {
                "rank": 1,
                "stock_code": "600000",
                "stock_name": "浦发银行",
                "trade_value": 1000000
            }
        ]
    }
}
```

**响应示例 - 需求6**:
```json
{
    "code": 200,
    "data": {
        "concept_id": 1,
        "concept_name": "人工智能",
        "summary": [
            {
                "date": "2025-08-21",
                "total_value": 123456789,
                "stock_count": 150,
                "avg_value": 823045,
                "max_value": 10000000
            }
        ]
    }
}
```

#### 5.3.6 分析查询 `/api/v1/analysis`

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/analysis/stock-rank-trend` | **需求2**: 股票每日排名 | `{stock_code, concept_ids, start_date, end_date}` |
| POST | `/analysis/stock-top-count` | **需求4**: 上榜次数统计 | `{stock_code, concept_id, start_date, end_date, top_n}` |
| POST | `/analysis/stock-rank-history` | **需求5**: 排名历史 | `{stock_code, concept_id, start_date, end_date}` |
| POST | `/analysis/concept-comparison` | 概念对比 | `{concept_ids, start_date, end_date}` |

**响应示例 - 需求2**:
```json
{
    "code": 200,
    "data": {
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "rank_trends": {
            "人工智能": [
                {"date": "2025-08-21", "rank": 5, "value": 100000},
                {"date": "2025-08-22", "rank": 3, "value": 150000}
            ]
        }
    }
}
```

**响应示例 - 需求4**:
```json
{
    "code": 200,
    "data": {
        "stock_code": "600000",
        "concept_name": "人工智能",
        "date_range": ["2025-08-01", "2025-08-30"],
        "top_n": 10,
        "statistics": {
            "total_days": 30,
            "top_n_days": 15,
            "top_n_rate": 0.5
        },
        "details": [
            {"date": "2025-08-21", "rank": 5, "in_top": true}
        ]
    }
}
```

**响应示例 - 需求5**:
```json
{
    "code": 200,
    "data": {
        "stock_code": "600000",
        "concept_name": "人工智能",
        "rank_history": [
            {"date": "2025-08-21", "rank": 5, "value": 100000, "percentile": 90.5}
        ],
        "statistics": {
            "avg_rank": 4.5,
            "best_rank": 1,
            "worst_rank": 20,
            "avg_value": 120000
        }
    }
}
```

#### 5.3.7 报表导出 `/api/v1/export`

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/export/excel` | 导出Excel | `{type, params, columns}` |
| POST | `/export/csv` | 导出CSV | `{type, params}` |
| POST | `/export/pdf` | 导出PDF | `{type, params, template}` |
| GET | `/export/tasks/:id` | 导出任务状态 | - |

### 5.4 错误码设计

| HTTP状态码 | 业务码 | 说明 |
|-----------|--------|------|
| 200 | 200 | 成功 |
| 400 | 4001 | 参数错误 |
| 400 | 4002 | 数据验证失败 |
| 401 | 4011 | 未认证 |
| 401 | 4012 | Token过期 |
| 403 | 4031 | 无权限 |
| 404 | 4041 | 资源不存在 |
| 409 | 4091 | 数据冲突（如用户名已存在） |
| 429 | 4291 | 请求过于频繁 |
| 500 | 5001 | 服务器内部错误 |
| 500 | 5002 | 数据库错误 |

---

## 6. 前端设计

### 6.1 前端架构

```
src/
├── main.ts                 # 入口文件
├── App.vue                # 根组件
├── views/                 # 页面组件
│   ├── auth/
│   │   ├── Login.vue
│   │   └── Register.vue
│   ├── dashboard/
│   │   └── Dashboard.vue
│   ├── import/
│   │   ├── FileUpload.vue
│   │   ├── DataPreview.vue
│   │   └── ImportHistory.vue
│   ├── stock/
│   │   ├── StockList.vue
│   │   ├── StockDetail.vue
│   │   └── StockRankTrend.vue
│   ├── concept/
│   │   ├── ConceptList.vue
│   │   ├── ConceptAnalysis.vue
│   │   └── ConceptRanking.vue
│   ├── analysis/
│   │   ├── RankingBoard.vue
│   │   ├── TrendAnalysis.vue
│   │   └── ComparisonChart.vue
│   └── user/
│       ├── UserList.vue
│       └── UserEdit.vue
├── components/            # 公共组件
│   ├── common/
│   │   ├── Pagination.vue
│   │   ├── SearchBar.vue
│   │   └── DataTable.vue
│   ├── charts/
│   │   ├── LineChart.vue
│   │   ├── BarChart.vue
│   │   └── HeatMap.vue
│   └── upload/
│       └── FileUploader.vue
├── router/               # 路由配置
│   └── index.ts
├── store/                # Pinia Store
│   ├── auth.ts
│   ├── stock.ts
│   └── concept.ts
├── api/                  # API封装
│   ├── request.ts
│   ├── auth.ts
│   ├── stock.ts
│   └── concept.ts
├── utils/               # 工具函数
│   ├── format.ts
│   ├── validate.ts
│   └── chart.ts
└── types/               # TypeScript类型
    ├── user.ts
    ├── stock.ts
    └── api.ts
```

### 6.2 核心页面设计

#### 6.2.1 数据导入页面

**功能流程**:
```
1. 文件上传 → 2. 数据预览 → 3. 配置映射 → 4. 执行导入 → 5. 查看结果
```

**页面布局**:
```
┌─────────────────────────────────────────────────┐
│  导入数据                                        │
├─────────────────────────────────────────────────┤
│  [步骤条: 上传 → 预览 → 配置 → 执行]            │
├─────────────────────────────────────────────────┤
│  Step 1: 上传文件                                │
│  ┌─────────────────────────────────────┐        │
│  │  [拖拽区域] 或点击上传              │        │
│  │  支持格式: CSV, TXT (最大100MB)    │        │
│  └─────────────────────────────────────┘        │
│  [下一步]                                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Step 2: 数据预览                                │
│  文件: 2025-08-22-01-31.csv (4.3MB)             │
│  ┌─────────────────────────────────────┐        │
│  │ 股票代码 | 股票名称 | 概念 | ...    │        │
│  │ 127111  | 金威转债 | 食品饮料 |     │        │
│  │ ...                                 │        │
│  └─────────────────────────────────────┘        │
│  [上一步] [下一步]                              │
└─────────────────────────────────────────────────┘
```

#### 6.2.2 股票查询页面

**页面布局**:
```
┌─────────────────────────────────────────────────┐
│  股票查询                                        │
├─────────────────────────────────────────────────┤
│  [搜索框: 股票代码/名称]  [高级筛选▼]           │
├─────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ 股票: 600000    │  │  30日趋势图          │  │
│  │ 名称: 浦发银行  │  │  ┌───────────────┐  │  │
│  │ 概念: [人工智能]│  │  │ ╱╲  ╱╲       │  │  │
│  │      [上海板块] │  │  │╱  ╲╱  ╲      │  │  │
│  └─────────────────┘  │  └───────────────┘  │  │
│                       └─────────────────────┘  │
├─────────────────────────────────────────────────┤
│  在各概念中的排名                                │
│  ┌─────────────────────────────────────────┐   │
│  │ 概念       | 排名 | 交易值    | 百分位  │   │
│  │ 人工智能   |  5   | 1,000,000 | 90.5%  │   │
│  │ 上海板块   |  12  |   800,000 | 75.2%  │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

#### 6.2.3 概念分析页面

**页面布局**:
```
┌─────────────────────────────────────────────────┐
│  概念分析                                        │
├─────────────────────────────────────────────────┤
│  [概念选择: 人工智能 ▼] [日期: 2025-08-21]     │
├─────────────────────────────────────────────────┤
│  概念总量趋势                                    │
│  ┌─────────────────────────────────────┐        │
│  │                        ╱╲            │        │
│  │  总值            ╱╲  ╱  ╲           │        │
│  │  (百万)      ╱╲╱  ╲╱    ╲          │        │
│  │         ╱╲╱                         │        │
│  │  ──────────────────────────────>    │        │
│  │       日期                           │        │
│  └─────────────────────────────────────┘        │
├─────────────────────────────────────────────────┤
│  成分股排名 (2025-08-21)                        │
│  ┌─────────────────────────────────────┐        │
│  │ 排名 | 股票代码 | 名称 | 交易值     │        │
│  │  1   | 600000  | 浦发 | 10,000,000 │        │
│  │  2   | 000001  | 平安 |  8,000,000 │        │
│  │ ...                                 │        │
│  └─────────────────────────────────────┘        │
│  [导出Excel] [导出PDF]                         │
└─────────────────────────────────────────────────┘
```

#### 6.2.4 排名榜单页面

**页面布局**:
```
┌─────────────────────────────────────────────────┐
│  排名榜单                                        │
├─────────────────────────────────────────────────┤
│  [日榜] [周榜] [月榜]  日期: 2025-08-21         │
├──────────────┬──────────────┬──────────────────┤
│ 概念热度榜   │ 股票热度榜   │  活跃股票榜      │
│              │              │                  │
│ 1. 人工智能  │ 1. 浦发银行  │ 1. XXX (20次)   │
│    ↑2 100亿  │    ↑5 1000万 │    上榜率 66%   │
│              │              │                  │
│ 2. 新能源车  │ 2. 中国平安  │ 2. YYY (18次)   │
│    ↓1  90亿  │    ↑3  800万 │    上榜率 60%   │
│              │              │                  │
│ ...          │ ...          │ ...              │
└──────────────┴──────────────┴──────────────────┘
```

### 6.3 组件设计

#### 关键组件清单

| 组件名 | 用途 | Props | Events |
|--------|------|-------|--------|
| `StockSelector` | 股票选择器 | `multiple, value` | `change` |
| `ConceptSelector` | 概念选择器 | `multiple, value` | `change` |
| `DateRangePicker` | 日期范围 | `value, shortcuts` | `change` |
| `RankTrendChart` | 排名趋势图 | `data, options` | - |
| `DataTable` | 数据表格 | `columns, data, pagination` | `pageChange` |
| `FileUploader` | 文件上传 | `accept, maxSize` | `success, error` |
| `ProgressBar` | 导入进度 | `percent, status` | - |

### 6.4 状态管理设计

**Auth Store**:
```typescript
interface AuthState {
  user: User | null
  token: string | null
  roles: Role[]
  permissions: string[]
}

actions:
- login(credentials)
- logout()
- refreshToken()
- checkPermission(permission)
```

**Stock Store**:
```typescript
interface StockState {
  stockList: Stock[]
  currentStock: Stock | null
  concepts: Concept[]
  loading: boolean
}

actions:
- fetchStockList(params)
- fetchStockDetail(code)
- fetchStockConcepts(code)
- fetchStockRanks(code, date)
```

---

## 7. 安全设计

### 7.1 认证安全

**JWT Token设计**:
```json
{
  "user_id": 1,
  "username": "admin",
  "roles": ["admin"],
  "exp": 1732234567,
  "iat": 1732227367
}
```

**Token策略**:
- Access Token: 2小时有效期
- Refresh Token: 7天有效期
- Token存储: localStorage (前端), Redis (后端黑名单)

**密码安全**:
- 使用 bcrypt (cost=12)
- 密码复杂度: 8位以上，包含字母+数字
- 登录失败锁定: 5次错误后锁定15分钟

### 7.2 授权安全

**RBAC权限模型**:
```python
def check_permission(user, permission):
    user_permissions = get_user_permissions(user)
    return permission in user_permissions

# 装饰器示例
@require_permission("stock:read")
def get_stock_list():
    pass
```

**API鉴权中间件**:
```python
async def verify_token(request):
    token = request.headers.get("Authorization")
    if not token:
        raise Unauthorized()

    payload = decode_jwt(token)
    user = get_user(payload["user_id"])
    request.state.user = user
```

### 7.3 数据安全

**SQL注入防护**:
- 使用ORM参数化查询
- 禁止直接拼接SQL

**XSS防护**:
- 前端输出转义
- CSP (Content Security Policy)

**CSRF防护**:
- SameSite Cookie
- CSRF Token验证

**文件上传安全**:
- 文件类型白名单
- 文件大小限制 (100MB)
- 文件名随机化
- 病毒扫描 (可选)

### 7.4 传输安全

**HTTPS**:
- TLS 1.3
- 强制HTTPS重定向

**API限流**:
- 全局: 1000 req/min
- 用户: 100 req/min
- IP: 200 req/min

### 7.5 审计日志

**记录内容**:
- 用户登录/登出
- 数据导入/导出
- 用户管理操作
- 敏感查询操作

**日志格式**:
```json
{
  "timestamp": "2025-11-22T10:00:00Z",
  "user_id": 1,
  "action": "import",
  "resource": "stock_daily_data",
  "ip": "192.168.1.1",
  "details": {
    "file": "2025-08-22.csv",
    "rows": 10000
  }
}
```

---

## 8. 性能优化

### 8.1 数据库优化

**索引优化**:
- 覆盖索引减少回表
- 复合索引顺序优化
- 定期ANALYZE更新统计信息

**分区策略**:
```sql
-- 按月分区
CREATE TABLE stock_daily_data_2025_08 PARTITION OF stock_daily_data
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
```

**查询优化**:
- 使用窗口函数批量计算排名
- 避免N+1查询，使用JOIN
- EXPLAIN分析慢查询

**连接池**:
```python
# SQLAlchemy配置
pool_size = 20
max_overflow = 10
pool_timeout = 30
pool_recycle = 3600
```

### 8.2 缓存策略

**三层缓存**:

**L1 - 应用内存缓存**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_concept_by_id(concept_id):
    return db.query(Concept).get(concept_id)
```

**L2 - Redis缓存**:
```python
# 热门概念列表，缓存5分钟
cache_key = "concepts:hot"
ttl = 300

# 股票详情，缓存1小时
cache_key = f"stock:{stock_code}"
ttl = 3600
```

**L3 - 预计算表**:
- concept_stock_daily_rank (每日凌晨计算)
- concept_daily_summary (每日凌晨汇总)

**缓存失效策略**:
- TTL过期
- 主动刷新 (数据导入后)
- LRU淘汰

### 8.3 异步处理

**Celery任务**:
```python
# 数据导入任务
@celery.task
def import_daily_data(file_path, user_id):
    # 大文件分批处理
    for chunk in read_csv_chunks(file_path, chunksize=1000):
        process_chunk(chunk)
        update_progress(task_id, progress)

# 排名计算任务
@celery.task
def calculate_daily_ranks(date):
    concepts = get_all_concepts()
    for concept in concepts:
        calculate_concept_ranks(concept, date)
```

**WebSocket推送**:
```python
# 实时推送导入进度
async def push_progress(task_id, progress):
    await websocket_manager.send_message(
        user_id,
        {"task_id": task_id, "progress": progress}
    )
```

### 8.4 前端优化

**懒加载**:
- 路由懒加载
- 图片懒加载
- 虚拟滚动 (大列表)

**防抖节流**:
```typescript
// 搜索输入防抖
const debouncedSearch = debounce((keyword) => {
  searchStocks(keyword)
}, 300)
```

**资源优化**:
- Gzip压缩
- CDN加速
- 代码分割
- Tree Shaking

---

## 9. 部署方案

### 9.1 Docker Compose部署

**目录结构**:
```
deployment/
├── docker-compose.yml
├── .env
├── nginx/
│   └── nginx.conf
└── scripts/
    ├── init_db.sh
    └── backup.sh
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: stock-db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: stock-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # MinIO对象存储
  minio:
    image: minio/minio:latest
    container_name: stock-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  # 后端API服务
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: stock-api
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      MINIO_ENDPOINT: minio:9000
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ../backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  # Celery Worker
  worker:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: stock-worker
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    volumes:
      - ../backend:/app
    depends_on:
      - postgres
      - redis
    command: celery -A app.tasks worker --loglevel=info

  # 前端 - 后台管理
  admin-web:
    build:
      context: ../admin-frontend
      dockerfile: Dockerfile
    container_name: stock-admin-web
    ports:
      - "8080:80"

  # 前端 - 用户展示
  user-web:
    build:
      context: ../user-frontend
      dockerfile: Dockerfile
    container_name: stock-user-web
    ports:
      - "8081:80"

  # Nginx网关
  nginx:
    image: nginx:alpine
    container_name: stock-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - admin-web
      - user-web

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 9.2 单机部署架构

```
Server (Ubuntu 22.04)
│
├── Nginx (80/443)
│   ├── /admin → admin-web:80
│   ├── /app → user-web:80
│   └── /api → backend:8000
│
├── PostgreSQL (5432)
├── Redis (6379)
├── MinIO (9000)
│
├── Backend (Uvicorn:8000)
├── Worker (Celery)
│
└── Docker Volumes
    ├── postgres_data
    ├── redis_data
    └── minio_data
```

### 9.3 部署流程

**1. 环境准备**:
```bash
# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**2. 配置环境变量**:
```bash
# .env文件
DB_USER=stockuser
DB_PASSWORD=your_secure_password
DB_NAME=stock_analysis
REDIS_PASSWORD=your_redis_password
MINIO_USER=minioadmin
MINIO_PASSWORD=your_minio_password
SECRET_KEY=your_secret_key_here
```

**3. 初始化数据库**:
```bash
# 创建数据库表
docker-compose exec backend alembic upgrade head

# 初始化默认数据
docker-compose exec backend python scripts/init_data.py
```

**4. 启动服务**:
```bash
cd deployment
docker-compose up -d
```

**5. 验证部署**:
```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 健康检查
curl http://localhost/api/v1/health
```

### 9.4 备份策略

**数据库备份**:
```bash
# 每日定时备份
0 2 * * * /path/to/backup.sh

# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec -T postgres pg_dump -U stockuser stock_analysis > backup_$DATE.sql
# 上传到对象存储
```

**日志轮转**:
```bash
# logrotate配置
/var/log/stock-analysis/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
}
```

---

## 10. 开发计划

### 10.1 开发阶段划分

#### Phase 1: 基础框架搭建 (1周)

**目标**: 搭建可运行的基础框架

**后端任务**:
- [ ] 项目结构初始化
- [ ] 数据库设计与创建
- [ ] SQLAlchemy模型定义
- [ ] FastAPI基础路由
- [ ] JWT认证中间件
- [ ] 基础配置管理

**前端任务**:
- [ ] Vue项目初始化
- [ ] 路由配置
- [ ] Axios封装
- [ ] 登录页面
- [ ] Layout布局

**部署任务**:
- [ ] Dockerfile编写
- [ ] docker-compose配置
- [ ] 本地环境启动验证

**交付物**:
- 可运行的登录系统
- 数据库表创建完成
- Docker环境可启动

---

#### Phase 2: 数据导入功能 (1周)

**目标**: 完成CSV数据导入全流程

**后端任务**:
- [ ] 文件上传API
- [ ] CSV解析与验证
- [ ] 数据预览API
- [ ] 数据导入Service
- [ ] Celery任务配置
- [ ] 异步导入任务
- [ ] WebSocket进度推送
- [ ] 导入历史记录

**前端任务**:
- [ ] 文件上传组件
- [ ] 拖拽上传
- [ ] 数据预览页面
- [ ] 字段映射配置
- [ ] 进度条展示
- [ ] 导入历史列表

**测试数据**:
- [ ] 使用现有CSV文件测试
- [ ] 验证数据正确性

**交付物**:
- 完整的数据导入流程
- 支持概念映射和交易数据导入

---

#### Phase 3: 基础查询功能 (1周)

**目标**: 实现6大核心查询需求

**后端任务**:
- [ ] 股票查询API (需求1)
- [ ] 股票排名趋势API (需求2)
- [ ] 概念排名API (需求3)
- [ ] 上榜统计API (需求4)
- [ ] 排名历史API (需求5)
- [ ] 概念汇总API (需求6)
- [ ] 数据库查询优化
- [ ] 缓存机制实现

**前端任务**:
- [ ] 股票查询页面
- [ ] 股票详情页面
- [ ] 概念列表页面
- [ ] 概念详情页面
- [ ] 搜索组件
- [ ] 数据表格组件

**测试**:
- [ ] API单元测试
- [ ] 查询性能测试

**交付物**:
- 6大查询API全部可用
- 基础查询页面完成

---

#### Phase 4: 数据可视化 (1周)

**目标**: 实现图表和可视化功能

**后端任务**:
- [ ] 趋势数据聚合API
- [ ] 榜单数据API
- [ ] 对比分析API
- [ ] 数据格式优化

**前端任务**:
- [ ] ECharts集成
- [ ] 排名趋势图
- [ ] 概念总量趋势图
- [ ] 排名榜单页面
- [ ] 热力图
- [ ] 对比分析图表
- [ ] 图表配置项优化

**交付物**:
- 完整的可视化页面
- 多种图表类型支持

---

#### Phase 5: 用户管理 (3天)

**目标**: 完整的用户和权限管理

**后端任务**:
- [ ] 用户CRUD API
- [ ] 角色权限API
- [ ] 权限检查中间件
- [ ] 操作日志记录

**前端任务**:
- [ ] 用户列表页面
- [ ] 用户编辑页面
- [ ] 角色分配
- [ ] 权限管理
- [ ] 操作日志查看

**交付物**:
- 完整的用户管理系统
- 权限控制生效

---

#### Phase 6: 高级功能 (3天)

**目标**: 报表导出和系统完善

**后端任务**:
- [ ] Excel导出
- [ ] PDF报表生成
- [ ] 异步导出任务
- [ ] 系统配置API

**前端任务**:
- [ ] 导出功能集成
- [ ] 报表模板选择
- [ ] 系统设置页面

**交付物**:
- 多格式报表导出
- 系统配置功能

---

#### Phase 7: 性能优化与测试 (3天)

**目标**: 优化性能，完善测试

**任务**:
- [ ] 数据库索引优化
- [ ] SQL查询优化
- [ ] 缓存策略完善
- [ ] 前端性能优化
- [ ] 单元测试覆盖
- [ ] 集成测试
- [ ] 性能压测
- [ ] 安全测试

**交付物**:
- 性能达标 (P95 < 500ms)
- 测试覆盖率 > 70%

---

#### Phase 8: 部署上线 (2天)

**目标**: 生产环境部署

**任务**:
- [ ] 生产环境配置
- [ ] SSL证书配置
- [ ] 数据库迁移
- [ ] 服务启动
- [ ] 监控配置
- [ ] 备份策略
- [ ] 文档整理

**交付物**:
- 系统上线运行
- 完整部署文档

---

### 10.2 开发时间线

```
Week 1: Phase 1 (基础框架)
Week 2: Phase 2 (数据导入) + Phase 3 (查询功能)
Week 3: Phase 4 (可视化) + Phase 5 (用户管理)
Week 4: Phase 6 (高级功能) + Phase 7 (优化测试) + Phase 8 (部署)
```

**总计**: 约4周完成MVP版本

### 10.3 里程碑

| 里程碑 | 日期 | 目标 |
|--------|------|------|
| M1 | Week 1 End | 基础框架可运行 |
| M2 | Week 2 End | 数据导入和查询功能完成 |
| M3 | Week 3 End | 可视化和用户管理完成 |
| M4 | Week 4 End | MVP版本上线 |

---

## 11. 风险与挑战

### 11.1 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 数据库性能瓶颈 | 高 | 中 | 分区表、索引优化、预计算 |
| 导入大文件内存溢出 | 中 | 中 | 分批处理、流式读取 |
| 并发查询慢 | 高 | 中 | 缓存、连接池、查询优化 |
| WebSocket连接不稳定 | 中 | 低 | 重连机制、降级方案 |

### 11.2 业务风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 数据格式多样化 | 中 | 高 | 灵活的字段映射配置 |
| 需求变更频繁 | 中 | 中 | 模块化设计、敏捷开发 |
| 数据量超预期 | 高 | 低 | 预留性能优化空间 |

### 11.3 安全风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| SQL注入 | 高 | 低 | ORM参数化查询 |
| 未授权访问 | 高 | 中 | JWT + 权限中间件 |
| 数据泄露 | 高 | 低 | HTTPS、敏感数据加密 |
| DDoS攻击 | 中 | 低 | 限流、CDN |

---

## 12. 待完善事项

### 12.1 当前设计的不足

#### 🔴 高优先级

**1. 数据一致性保证**
- **问题**: 导入数据时，如何保证CSV中的概念名称与数据库中的概念一致？
- **现状**: 当前设计缺少概念标准化机制
- **建议**:
  - 添加概念映射表 (别名 → 标准名称)
  - 导入时进行概念名称标准化
  - 提供概念合并功能

**2. 数据版本管理**
- **问题**: 如果导入错误数据，如何回滚？
- **现状**: 缺少数据版本控制
- **建议**:
  - 每次导入生成版本快照
  - 提供回滚到指定版本的功能
  - 数据变更审计日志

**3. 性能监控**
- **问题**: 如何及时发现性能问题？
- **现状**: 缺少监控告警
- **建议**:
  - 集成Prometheus + Grafana
  - 慢查询日志分析
  - 关键指标告警

**4. 数据校验规则**
- **问题**: 导入数据的校验规则不够详细
- **现状**: 只有基本格式校验
- **建议**:
  - 股票代码格式验证
  - 日期范围验证
  - 数值合理性验证
  - 重复数据检测

#### 🟡 中优先级

**5. 增量导入优化**
- **问题**: 如何高效处理每日增量数据？
- **建议**:
  - 自动识别日期
  - 智能跳过已存在数据
  - 增量更新策略

**6. 多租户支持**
- **问题**: 是否需要支持多个独立用户组？
- **建议**: 预留租户ID字段

**7. 数据导出优化**
- **问题**: 大数据量导出可能超时
- **建议**:
  - 异步导出
  - 分批下载
  - 压缩文件

**8. 定时任务管理**
- **问题**: 缺少定时任务的配置和监控
- **建议**:
  - 使用Celery Beat
  - 任务执行日志
  - 失败重试机制

#### 🟢 低优先级

**9. 国际化支持**
- **建议**: i18n配置，支持多语言

**10. 移动端适配**
- **建议**: 响应式设计，PWA支持

**11. 数据分析报告**
- **建议**: 自动生成周报、月报

**12. AI智能推荐**
- **建议**: 基于历史数据推荐潜力股票

### 12.2 需要确认的设计决策

**1. 历史数据保留策略**
- 保留所有历史数据？
- 按时间归档冷数据？
- 定期清理超过N年的数据？

**2. 排名计算时机**
- 实时计算？
- 每日定时计算？
- 按需计算 + 缓存？

**3. 概念变更处理**
- 股票的概念会动态变化吗？
- 如何处理历史概念变更？
- 需要记录概念变更历史吗？

**4. 数据权限粒度**
- 是否需要限制用户查看特定概念？
- 是否需要限制查看的时间范围？
- 是否需要数据脱敏？

### 12.3 技术债务

**1. 测试覆盖**
- 当前设计缺少详细的测试策略
- 需要补充单元测试、集成测试计划

**2. API文档**
- 需要使用OpenAPI/Swagger自动生成文档
- 需要API使用示例

**3. 错误处理**
- 需要统一的错误处理机制
- 需要错误码文档

**4. 日志规范**
- 需要定义日志级别
- 需要日志格式规范
- 需要敏感信息脱敏规则

### 12.4 扩展性考虑

**未来可能需要的功能**:
- 股票价格实时推送
- 行情数据接入
- 策略回测功能
- 社区讨论功能
- 消息通知系统
- 第三方API集成

---

## 13. 总结

### 13.1 设计优点

✅ **架构清晰**: 分层明确，职责分离
✅ **技术现代**: FastAPI + Vue 3，高性能
✅ **可扩展性**: 模块化设计，易于扩展
✅ **安全完善**: JWT + RBAC，多层防护
✅ **性能优化**: 缓存、分区、预计算

### 13.2 核心价值

1. **数据管理**: 便捷的CSV导入，支持大文件
2. **多维分析**: 6大核心需求全覆盖
3. **可视化**: 直观的图表和趋势展示
4. **权限控制**: 完整的用户和权限体系
5. **部署简单**: Docker一键部署

### 13.3 下一步行动

1. **评审确认**: Review待完善事项，确认设计决策
2. **原型开发**: 快速搭建可演示的原型
3. **迭代优化**: 根据反馈不断完善
4. **正式开发**: 按照开发计划执行

---

**文档状态**: ✅ 设计评审中
**下次更新**: 根据评审反馈修订
**维护者**: 开发团队

---

## 14. 数据导入与重算机制（补充设计）

> **重要补充**: 完整设计请参考 [DATA_IMPORT_DESIGN.md](./DATA_IMPORT_DESIGN.md)

### 14.1 核心设计原则

**源数据与计算结果分离**:

```
CSV导入 → 源数据表（永久保留） → 数据处理 → 计算结果表（可重算）
```

**优势**:
- ✅ 源数据永久保留，可追溯
- ✅ 算法调整后可基于源数据重新计算
- ✅ 数据错误可修正后重算
- ✅ 支持不同计算策略对比

### 14.2 数据表设计

#### 源数据表（Raw Data）

```sql
-- 原始交易数据（永久保留）
CREATE TABLE stock_daily_data_raw (
    id BIGSERIAL,
    import_batch_id INTEGER NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    trade_value BIGINT,
    
    -- 元数据
    source_file VARCHAR(255),
    source_row_number INTEGER,
    raw_data JSONB,  -- 完整原始数据
    
    -- 状态标记
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);
```

#### 计算结果表（Computed Data）

```sql
-- 标准化后的数据（可重算）
CREATE TABLE stock_daily_data (
    id BIGSERIAL,
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    trade_value BIGINT,
    
    -- 计算元数据
    computed_from_batch_id INTEGER,
    computed_at TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT 'v1.0',
    
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);
```

### 14.3 重算API

```http
# 触发重算
POST /api/v1/recompute/trigger
{
  "recompute_type": "all",  // all, daily_data, ranks, summary
  "date_range": {
    "start": "2025-08-01",
    "end": "2025-08-31"
  },
  "options": {
    "clear_existing": true,
    "computation_version": "v1.1"
  }
}

# 基于导入批次重算
POST /api/v1/recompute/batch/{batch_id}

# 查询重算状态
GET /api/v1/recompute/status/{task_id}
```

### 14.4 重算流程

```
1. 读取源数据表（stock_daily_data_raw）
   ↓
2. 数据标准化（概念名称映射、数据清洗）
   ↓
3. 写入标准化数据（stock_daily_data）
   ↓
4. 计算排名（concept_stock_daily_rank）
   ↓
5. 计算汇总（concept_daily_summary）
   ↓
6. 更新缓存
```

### 14.5 重算策略

| 策略 | 场景 | 说明 |
|------|------|------|
| **增量重算** | 新增数据 | 只重算新导入的批次 |
| **全量重算** | 算法升级 | 重新处理所有历史数据 |
| **选择性重算** | 部分修正 | 只重算特定概念或股票 |
| **定时重算** | 数据维护 | 每周重算最近7天数据 |

### 14.6 用户界面

**导入页面增强**:
```
☑ 保留源数据 (Raw Data)
  源数据将永久保存，支持后续重新计算

计算选项:
  ● 立即计算
  ○ 稍后手动触发
```

**重算管理页面**:
- 重算任务列表（状态、进度）
- 快速重算（按日期范围）
- 批次重算（按导入批次）

### 14.7 数据流向

```
CSV文件
  ↓
stock_daily_data_raw (源数据，永久保留)
  ↓ 数据标准化
stock_daily_data (标准化数据，可重算)
  ↓ 排名计算
concept_stock_daily_rank (排名结果，可重算)
  ↓ 汇总计算
concept_daily_summary (汇总结果，可重算)
```

### 14.8 实现要点

1. **源数据完整性**
   - 保留完整的CSV原始数据（JSONB格式）
   - 记录源文件名和行号
   - 标记数据有效性

2. **计算版本管理**
   - 每次计算标记版本号
   - 支持多版本并存
   - 可对比不同版本结果

3. **重算任务管理**
   - 异步执行，不阻塞主流程
   - WebSocket实时推送进度
   - 失败自动重试

4. **性能优化**
   - 批量处理（1000条/批）
   - 并行计算（4个worker）
   - 增量更新（UPSERT）

---

**详细设计**: 请参考 [DATA_IMPORT_DESIGN.md](./DATA_IMPORT_DESIGN.md)


---

## 15. 多指标数据系统（补充设计）

> **重要补充**: 完整设计请参考 [MULTI_METRIC_DESIGN.md](./MULTI_METRIC_DESIGN.md)

### 15.1 需求背景

**多种数据文件类型**:
- `TTV.txt` - 交易总值指标
- `EEE.txt` - 交易活跃度指标  
- `EFV.txt` - 流动性指标（未来）
- `AAA.txt` - 其他指标（未来）

**关键特征**:
- ✅ 每种类型是独立的指标
- ✅ 同一类型可有多个文件（不同日期）
- ✅ 每种指标有独立的汇总逻辑
- ✅ 需支持动态扩展新指标

### 15.2 核心设计

**指标类型抽象**:
```sql
-- 指标类型配置表
CREATE TABLE metric_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,     -- TTV, EEE, EFV
    name VARCHAR(100) NOT NULL,           -- 显示名称
    file_pattern VARCHAR(100),            -- 文件识别模式
    field_mapping JSONB,                  -- 字段映射配置
    aggregation_config JSONB              -- 汇总规则配置
);
```

**统一源数据表**:
```sql
-- 多指标源数据表
CREATE TABLE stock_metric_data_raw (
    id BIGSERIAL,
    metric_type_id INTEGER NOT NULL,      -- 指标类型
    metric_code VARCHAR(50) NOT NULL,     -- 指标代码
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    value BIGINT,                         -- 主要数值
    raw_data JSONB,                       -- 完整原始数据
    PRIMARY KEY (id, trade_date)
) PARTITION BY RANGE (trade_date);
```

### 15.3 自动识别机制

```python
# 文件类型自动检测
detector.detect_metric_type("2025-08-21-TTV.txt")
# 返回: MetricType(code='TTV', name='交易总值')

detector.detect_metric_type("data-EEE-0821.txt")
# 返回: MetricType(code='EEE', name='交易活跃度')
```

### 15.4 多指标查询API

```http
# 查询股票在多个指标中的排名
GET /api/v1/stocks/{code}/metric-ranks?metrics=TTV,EEE&date=2025-08-21

# 概念多指标汇总
GET /api/v1/concepts/{id}/metric-summary?metrics=TTV,EEE,EFV

# 多指标对比分析
POST /api/v1/analysis/metric-comparison
{
  "concept_id": 1,
  "metrics": ["TTV", "EEE", "EFV"],
  "date_range": {"start": "2025-08-01", "end": "2025-08-31"}
}
```

### 15.5 新增指标流程

**添加新指标（如AAA）只需配置**:

1. 创建指标类型配置:
```json
{
  "code": "AAA",
  "name": "新指标AAA",
  "file_pattern": "*AAA*.txt",
  "field_mapping": {...},
  "aggregation_config": {...}
}
```

2. 系统自动支持:
- ✅ 自动识别AAA类型文件
- ✅ 使用配置的字段映射解析
- ✅ 按汇总配置计算结果
- ✅ 无需修改代码

### 15.6 指标配置示例

```json
{
  "TTV": {
    "file_pattern": "*TTV*.txt",
    "field_mapping": {
      "stock_code": {"column": 0, "type": "string"},
      "trade_date": {"column": 1, "type": "date"},
      "value": {"column": 2, "type": "bigint"}
    },
    "aggregation_config": {
      "concept_rank": {"enabled": true, "algorithm": "desc"},
      "concept_summary": {
        "enabled": true,
        "aggregations": ["sum", "avg", "max", "min"]
      }
    }
  }
}
```

### 15.7 核心优势

| 特性 | 说明 |
|------|------|
| **动态扩展** | 新增指标只需配置，无需改代码 |
| **统一管理** | 所有指标使用统一的导入查询接口 |
| **独立汇总** | 每种指标有独立的计算规则 |
| **多指标对比** | 支持多个指标的关联分析 |

---

**详细设计**: 请参考 [MULTI_METRIC_DESIGN.md](./MULTI_METRIC_DESIGN.md)

