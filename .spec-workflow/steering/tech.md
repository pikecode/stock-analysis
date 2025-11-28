# Technology Stack

## Project Type

全栈 Web 应用 - 前后端分离的股票数据分析和管理系统，支持多端访问（PC、平板、手机）。

## Core Technologies

### Primary Language(s)

**前端：**
- **TypeScript** - 类型安全，提高代码质量和开发效率
- **Runtime**: Node.js (v18+)
- **包管理**: npm

**后端：**
- **Python** - 3.10+，生态丰富，适合数据处理
- **Runtime**: Python 3.10+
- **包管理**: pip + requirements.txt

### Key Dependencies/Libraries

**前端依赖：**
- **Vue.js** 3.x (Composition API) - 渐进式前端框架，学习曲线平缓
- **Vite** 5.x - 现代前端构建工具，快速开发体验
- **TypeScript** - 类型安全编程
- **Element Plus** - 完整的 UI 组件库，提供专业的表单、表格、对话框等
- **Vue Router** 4.x - 客户端路由，支持嵌套路由和动态路由
- **Pinia** - 状态管理（选用），轻量级替代 Vuex
- **Axios** - HTTP 请求库，处理 API 通信

**后端依赖：**
- **FastAPI** 0.104+ - 现代异步 Web 框架，性能高，自动 API 文档
- **Uvicorn** - ASGI 应用服务器
- **SQLAlchemy** 2.x - ORM 框架，支持多数据库
- **Pydantic** - 数据验证和序列化
- **python-jose** - JWT 令牌生成和验证
- **passlib** + **bcrypt** - 密码哈希和安全存储
- **Celery** - 异步任务队列（用于后台任务）
- **Redis** - 消息中间件和缓存（支持 Celery）
- **APScheduler** - 任务调度（定时导入数据等）

### Application Architecture

**前端架构：**
```
Single Page Application (SPA) + Progressive Enhancement
- Vue 3 Composition API 组件化架构
- 三层路由系统：Public（公开）→ Client（客户端）→ Admin（管理员）
- 响应式设计：Mobile-first 开发方式（默认 mobile，768px+ tablet，1024px+ desktop）
- 组件库驱动：Element Plus 组件库提供一致的 UI
```

**后端架构：**
```
REST API + Async Processing
- FastAPI 异步 Web 框架提供高性能 API 端点
- MVC 分层：Models（数据）→ Routers（路由）→ Services（业务逻辑）→ Schemas（数据验证）
- SQLAlchemy ORM 统一数据库操作
- 权限控制：JWT + Role-Based Access Control (RBAC)
- 异步任务：Celery 处理长时任务（数据导入、报告生成）
```

**整体系统架构：**
```
┌─────────────────────────────────────────────────────────────┐
│                      Browser / Mobile Client                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                    RESTful API + WebSocket
                             │
┌────────────────────────────▼────────────────────────────────┐
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           FastAPI Web Server (Uvicorn)              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │  │
│  │  │   Routers   │  │  Middleware  │  │ WebSocket │ │  │
│  │  │  (/api/*)   │  │    (Auth)    │  │  Server   │ │  │
│  │  └─────────────┘  └──────────────┘  └───────────┘ │  │
│  │           ↓                                         │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │      Services & Business Logic               │ │  │
│  │  │  - Stock Service  - Concept Service         │ │  │
│  │  │  - User Service   - Auth Service            │ │  │
│  │  │  - Report Service - Import Service          │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │           ↓                                         │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │      SQLAlchemy ORM Layer                     │ │  │
│  │  │  - User Models  - Stock Models              │ │  │
│  │  │  - Role Models  - Concept Models            │ │  │
│  │  │  - Permission   - Ranking Models            │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↓                    ↓                    ↓       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   SQLite     │  │   Celery     │  │   Redis Cache    │  │
│  │   Database   │  │   Worker     │  │  & Message Queue │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Data Storage

- **Primary storage** - SQLite (开发环境) / PostgreSQL (生产环境可选升级)
  - 完整的关系数据库支持
  - 自动迁移管理（考虑集成 Alembic）
  - 支持事务和约束

- **Caching** - Redis (可选)
  - 缓存用户认证令牌
  - 缓存热点数据（股票排名、概念分析）
  - 支持 Celery 消息队列

- **Data formats**
  - REST API 统一使用 JSON
  - Pydantic 进行序列化/反序列化
  - 数据库存储关系数据

### External Integrations

- **数据源** - 支持外部股票数据 API 集成（未来考虑对接实时行情提供商）
- **协议** - 主要使用 HTTP/REST，支持 WebSocket 实时更新
- **认证** - 使用 JWT（JSON Web Token）实现无状态认证
- **跨域** - CORS 配置支持多域名访问

### Monitoring & Dashboard Technologies

- **前端框架** - Vue 3 + Element Plus，响应式设计，完全支持移动端
- **实时通信** - WebSocket（实现实时数据推送，目前可选）
- **可视化库** - Element Plus 内置图表组件，可选集成 ECharts 做更复杂可视化
- **状态管理** - Pinia (轻量) 或 localStorage (当前简单使用)

## Development Environment

### Build & Development Tools

- **Build System**
  - 前端：Vite (npm scripts)
  - 后端：Python setuptools (可选打包为 wheel)

- **Package Management**
  - 前端：npm (package.json + package-lock.json)
  - 后端：pip (requirements.txt)

- **Development workflow**
  - 前端：Vite 热更新 HMR (hot module replacement)
  - 后端：FastAPI 自动重载 (--reload)
  - 编辑器：VS Code + 相应插件

### Code Quality Tools

- **Static Analysis**
  - 前端：TypeScript 编译时检查
  - 后端：pylint / flake8（可选）

- **Formatting**
  - 前端：Prettier / ESLint
  - 后端：black / isort（可选）

- **Testing Framework**
  - 前端：Vitest / Jest（可选）
  - 后端：pytest（可选，当前未设置）

- **Documentation**
  - 后端：FastAPI 自动生成 OpenAPI 文档 (Swagger UI 和 ReDoc)
  - 前端：Markdown 文档（README.md）

### Version Control & Collaboration

- **VCS** - Git
- **Branching Strategy** - GitHub Flow（简单模型：main + feature branches）
- **Code Review Process** - Pull Request 流程，主分支保护

### Development Proxy Configuration

- **Vite 代理** - 配置代理到后端 API
  - 开发环境：`http://127.0.0.1:8000`（使用具体 IP 避免 IPv6 问题）
  - 支持请求路径重写和 WebSocket 代理

### Dashboard Development

- **Live Reload** - Vite HMR，文件保存即时更新
- **Port Management** - 前端默认 3000，后端默认 8000
- **Multi-Instance Support** - 支持同时运行多个开发实例

## Deployment & Distribution

- **Target Platform(s)**
  - Web 应用，支持所有现代浏览器（Chrome、Firefox、Safari、Edge）
  - 响应式设计，完全支持移动端访问

- **Distribution Method**
  - 前端：构建 SPA，部署到 Web 服务器（Nginx、Apache）或 CDN
  - 后端：部署为 Docker 容器或直接运行 Uvicorn 服务

- **Installation Requirements**
  - 前端：Node.js 18+，npm
  - 后端：Python 3.10+，pip
  - 可选：Docker，Redis，PostgreSQL

- **Update Mechanism**
  - 前端：CDN 缓存破坏 + 版本化文件名
  - 后端：零停机部署（蓝绿部署或滚动更新）

## Technical Requirements & Constraints

### Performance Requirements

- **API 响应时间** - 平均 < 200ms，P95 < 500ms
- **页面加载** - 首屏加载 < 2 秒（移动端 < 3 秒）
- **并发用户** - 支持 1000+ 并发连接（初期目标）
- **数据库查询** - 单表查询 < 100ms，复杂查询 < 500ms
- **实时更新延迟** - WebSocket 数据推送 < 1 秒

### Compatibility Requirements

- **浏览器支持** - 现代浏览器（ES6+）
- **操作系统** - Windows, macOS, Linux
- **Python 版本** - 3.10+
- **Node.js 版本** - 18+
- **数据库** - SQLite（开发）→ PostgreSQL（生产可选）

### Security & Compliance

- **认证方案** - JWT token（双Token独立存储），支持刷新令牌
  - 使用 `admin_access_token` / `admin_refresh_token` 隔离管理员身份
  - 使用 `client_access_token` / `client_refresh_token` 隔离客户端身份
  - 两个身份体系独立运行，防止权限污染
  - Token 有效期：Access Token 30分钟，Refresh Token 7天（后端配置）

- **密码存储** - bcrypt 哈希，不存储明文密码

- **API 安全**
  - CORS 配置，仅允许同域名请求
  - CSRF 保护：Token-based 防御
  - 请求拦截器自动补充 Authorization 头
  - 401 错误自动刷新 token 并重试请求

- **跨身份认证安全**
  - 前端路由守卫确保用户访问正确的登录页面
  - 管理员路由（`/admin/*`）仅接受 `admin_access_token`
  - 客户端路由（`/reports/*` 等）仅接受 `client_access_token`
  - 不同身份的 token 不可互换

- **HTTPS** - 生产环境必须使用 HTTPS
  - 防止 Token 在传输过程中被拦截
  - 特别重要：localStorage 中的 Token 在 HTTP 下容易被 XSS 窃取

- **SQL 注入防护** - SQLAlchemy ORM 参数化查询

- **XSS 防护** - Vue 模板自动转义，HTTP 响应头配置

- **数据保护** - 敏感数据不在日志中记录，Token 不在页面加载时显示

### Scalability & Reliability

- **预期负载** - 初期 1,000+ 日活用户，可扩展到 100,000+
- **可用性目标** - 99.5% 正常运行时间
- **容灾恢复** - 数据库定期备份，异地灾备方案（长期规划）
- **扩展性规划**
  - 数据库：SQLite → PostgreSQL + 读写分离
  - 缓存层：引入 Redis 提升热点数据访问性能
  - API 网关：前置 API 网关实现限流和负载均衡
  - 微服务：拆分核心服务模块（如数据导入、报告生成）

## Technical Decisions & Rationale

### Decision Log

1. **Vue 3 + Composition API**
   - 选择理由：学习曲线适中，生态完善，支持 TypeScript，响应式数据管理清晰
   - 备选方案考虑：React（学习陡峭，但生态更大）、Svelte（编译型，性能优）
   - 权衡：选择生态+学习曲线最优方案

2. **FastAPI**
   - 选择理由：异步支持好，自动生成 API 文档，性能高，开发效率高
   - 备选方案：Flask（轻量但功能少）、Django（功能全但重）
   - 权衡：在灵活性和功能完整性之间找到最佳平衡

3. **SQLAlchemy ORM**
   - 选择理由：支持多数据库，类型系统完善，关系管理清晰
   - 备选方案：Tortoise ORM（异步）、Peewee（轻量）
   - 权衡：选择成熟度高、文档完善的方案

4. **JWT 认证（双Token独立存储）**
   - 选择理由：无状态、易扩展、支持分布式，特别适合前后端分离
   - 备选方案：Session（有状态，扩展性差）、OAuth（功能过重）
   - 权衡：简单高效，满足当前需求

   **双Token独立存储架构说明：**
   - **adminToken 系统**：用于管理员后台访问
     - `admin_access_token` - 有效期短（如30分钟），用于 API 请求认证
     - `admin_refresh_token` - 有效期长（如7天），用于获取新的 access token
     - 存储在 localStorage 中：`admin_access_token` 和 `admin_refresh_token`

   - **clientToken 系统**：用于普通客户端用户访问
     - `client_access_token` - 有效期短（如30分钟），用于 API 请求认证
     - `client_refresh_token` - 有效期长（如7天），用于获取新的 access token
     - 存储在 localStorage 中：`client_access_token` 和 `client_refresh_token`

   - **跨身份认证支持**：用户可以在保持一个身份登录的同时，切换到另一个身份进行认证
     - 例如：客户端用户访问 `/admin` 时，重定向到 `/admin-login` 可在同一浏览器中添加管理员身份
     - 两个 token 可以同时存在，允许用户在两个身份间快速切换

   - **前端请求拦截**：
     - 登录/刷新 token 时：直接使用 fetch 指定正确的 token
     - 普通 API 请求时：根据 URL 路径判断（包含 `/admin` 使用 admin token，否则使用 client token）

5. **SQLite 初期存储**
   - 选择理由：零配置，无依赖，适合开发和小型应用
   - 迁移路径：生产环境可无缝升级到 PostgreSQL
   - 长期计划：数据规模增长后迁移到 PostgreSQL

6. **Celery + Redis 异步任务**
   - 选择理由：支持后台处理（数据导入、报告生成），支持定时任务
   - 备选方案：APScheduler（单机）、Huey（轻量）
   - 权衡：选择社区活跃、功能完善的方案

7. **响应式设计（Mobile-First）**
   - 选择理由：优先适配移动端，然后向上升级；现代用户大多使用手机访问
   - 实现方式：CSS Media Queries（768px + 1024px 断点）
   - 权衡：单代码库支持多终端，开发效率高

8. **Element Plus 组件库**
   - 选择理由：组件齐全、设计专业、中文文档好、国内用户多
   - 备选方案：Ant Design Vue（重企业）、Vuetify（Material Design）
   - 权衡：选择开箱即用、文档支持好的方案

### Architecture Decisions

1. **三层路由系统** - 公开页面、客户端页面、管理员页面分离，不同权限要求
2. **前后端完全分离** - 独立部署，通过 API 通信，便于独立扩展和开发
3. **权限控制下沉** - 后端 API 层面进行权限验证，前端 UI 层面隐藏功能
4. **关注点分离** - 前端专注 UI/UX，后端专注业务逻辑和数据一致性

## Known Limitations

### 当前实现的限制

1. **数据库扩展性** - SQLite 单文件存储，并发写入能力有限
   - 解决方案：生产环境升级到 PostgreSQL
   - 时间表：用户数达到 10,000+ 时进行迁移

2. **实时数据更新** - 目前缺少 WebSocket 实现，仅支持轮询或手动刷新
   - 解决方案：集成 WebSocket 支持实时数据推送
   - 优先级：中期（3-6 个月）

3. **文件上传限制** - 当前导入功能缺少大文件支持和进度显示
   - 解决方案：分块上传、背景进度跟踪、断点续传
   - 优先级：低（用户反馈后优化）

4. **缓存策略** - 未集成 Redis，热点数据每次都从数据库查询
   - 解决方案：引入 Redis，缓存排名数据和热点查询
   - 优先级：中期性能优化项

5. **API 限流** - 缺少速率限制，容易被滥用
   - 解决方案：在 FastAPI 中间件添加限流器
   - 优先级：上线前必须实现

6. **日志和监控** - 基础日志实现，缺少集中式日志和性能监控
   - 解决方案：集成 ELK Stack 或云日志服务
   - 优先级：生产环境必须实现

### 技术债

1. 考虑添加自动化测试（pytest + Vitest）
2. 完善异常处理和错误日志
3. 添加 API 版本控制策略

## 参考文档

详细的数据库设计、表结构、字段含义和计算逻辑见：**`.spec-workflow/database-schema.md`**

该文档包含：
- 所有核心表的完整设计和字段说明
- 用户认证、主数据、导入处理、预计算数据的四层架构
- 数据流向图和计算逻辑解释
- 关键概念（trade_value含义、概念vs行业等）
- 常见查询示例和性能优化策略

功能开发时参考此文档可避免重复确认数据逻辑。
