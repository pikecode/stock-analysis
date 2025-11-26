# 🚀 系统初始化与启动指南

欢迎来到股票分析系统！本目录提供完整的系统初始化和启动脚本。

---

## 📋 目录结构

```
scripts/setup/
├── README.md                           📖 本文档（系统初始化指南）
├── init.sh                             🔧 完整初始化脚本（推荐）
├── init-db.sh                          🗄️ 数据库初始化脚本
├── start.sh                            ▶️ 服务启动脚本
│
└── SQL 初始化脚本/
    ├── 00_init_tables.sql              📊 创建所有数据库表
    ├── 01_create_partitions.sql        📈 创建分区表（性能优化）
    └── 02_optimize_indexes.sql         ⚡ 优化数据库索引
```

---

## 🎯 快速开始（三个步骤）

### 步骤 1️⃣：完整初始化（首次配置）

如果这是首次部署，运行完整初始化脚本：

```bash
cd /Users/peakom/work/stock-analysis
bash scripts/setup/init.sh
```

**这个脚本会自动：**
- ✅ 检查环境依赖（Python、Node.js、PostgreSQL、Redis）
- ✅ 创建 `.env` 配置文件
- ✅ 设置 Python 虚拟环境
- ✅ 安装 Python 和 npm 依赖
- ✅ 构建前端代码
- ✅ 创建和初始化数据库
- ✅ 创建默认管理员账户

**预期耗时：** 5-10 分钟

---

### 步骤 2️⃣：启动所有服务

```bash
bash scripts/setup/start.sh all
```

**启动的服务：**
- 🔵 后端 API (http://localhost:8000)
- 🟢 前端应用 (http://localhost:3000)
- 🟣 Celery 任务队列
- 🗄️ PostgreSQL 数据库
- 💾 Redis 缓存

---

### 步骤 3️⃣：验证和登录

访问 http://localhost:3000，使用默认账户登录：
- **用户名:** admin
- **密码:** admin123

⚠️ **安全提示：** 首次登录后立即修改密码！

---

## 📖 详细说明

### 脚本用途详解

#### `init.sh` - 完整初始化（推荐）

**用途：** 从零开始设置整个项目环境

**步骤：**
1. 环境检查（Python、Node、PostgreSQL、Redis）
2. 创建 `.env` 配置文件
3. 创建 Python 虚拟环境和安装依赖
4. 安装前端依赖
5. 构建前端
6. 初始化数据库
7. 创建默认管理员

**何时使用：**
- 首次部署
- 重新配置环境
- 需要完整的环境设置

**命令：**
```bash
bash scripts/setup/init.sh
```

---

#### `init-db.sh` - 仅数据库初始化

**用途：** 只初始化数据库（跳过前端和依赖安装）

**步骤：**
1. 检查 PostgreSQL 运行状态
2. 创建 stock_analysis 数据库
3. 执行表结构初始化 SQL
4. 创建默认用户和指标类型

**何时使用：**
- 需要重置数据库
- 其他组件已经初始化
- 快速重新初始化

**命令：**
```bash
bash scripts/setup/init-db.sh
```

---

#### `start.sh` - 服务启动和管理

**用途：** 启动、停止、查看系统服务状态

**命令选项：**

```bash
# 启动所有服务（后端、前端、Celery）
bash scripts/setup/start.sh all

# 仅启动后端
bash scripts/setup/start.sh backend

# 仅启动前端
bash scripts/setup/start.sh frontend

# 仅启动 Celery
bash scripts/setup/start.sh celery

# 停止所有服务
bash scripts/setup/start.sh stop

# 查看服务状态
bash scripts/setup/start.sh status

# 查看后端日志
bash scripts/setup/start.sh logs backend

# 显示帮助
bash scripts/setup/start.sh help
```

---

### SQL 脚本详解

#### `00_init_tables.sql` - 数据库表初始化

**内容：** 完整的数据库表结构定义

**包括的表：**
- 用户认证：users, roles, user_roles, permissions
- 股票数据：stocks, stock_industries, stock_concepts
- 行业和概念：industries, concepts
- 核心数据：stock_metric_data_raw, concept_stock_daily_rank
- 辅助数据：stock_concept_mapping_raw, import_batches
- 汇总数据：concept_daily_summary

**自动执行：** 在 `init.sh` 或 `init-db.sh` 中自动执行

**手动执行：**
```bash
psql -U postgres -d stock_analysis -f scripts/setup/00_init_tables.sql
```

---

#### `01_create_partitions.sql` - 分区表创建

**目的：** 按日期分区大表以提高查询性能

**分区范围：** 2023-06 到 2024-12（月粒度）

**分区的表：**
- stock_metric_data_raw_{YYYY_MM}
- concept_stock_daily_rank_{YYYY_MM}

**何时运行：**
- 导入大量历史数据前
- 需要优化查询性能时

**手动执行：**
```bash
psql -U postgres -d stock_analysis -f scripts/setup/01_create_partitions.sql
```

---

#### `02_optimize_indexes.sql` - 索引优化

**目的：** 为常用查询创建索引以加速数据库操作

**创建的索引：**
- metric_type_id, trade_date, stock_code 等热点字段
- 复合索引用于多条件查询

**何时运行：**
- 导入数据后
- 发现查询变慢时
- 定期性能维护

**手动执行：**
```bash
psql -U postgres -d stock_analysis -f scripts/setup/02_optimize_indexes.sql
```

---

## 🔧 各环境初始化方式

### 本地开发环境（macOS/Linux）

```bash
# 1. 完整初始化（推荐）
bash scripts/setup/init.sh

# 2. 启动服务
bash scripts/setup/start.sh all

# 3. 访问应用
# 前端: http://localhost:3000
# API: http://localhost:8000/docs
```

### Docker 环境（推荐用于生产）

```bash
# 使用 docker-compose 一键启动（如果有 docker-compose.yml）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

---

## ⚙️ 环境要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端开发 |
| Node.js | 18+ | 前端开发 |
| PostgreSQL | 12+ | 数据库 |
| Redis | 6+ | 缓存 |

### 安装依赖

**macOS（使用 Homebrew）：**
```bash
brew install python@3.11 node postgresql@15 redis
brew services start postgresql@15
brew services start redis
```

**Ubuntu/Debian：**
```bash
sudo apt install python3.11 python3.11-venv nodejs npm postgresql redis-server
sudo systemctl start postgresql
sudo systemctl start redis-server
```

---

## 🚨 常见问题排查

### Q1: PostgreSQL 未运行

**错误消息：** `PostgreSQL 未运行`

**解决方案：**
```bash
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql
```

---

### Q2: Redis 未运行

**错误消息：** `Redis 未运行`

**解决方案：**
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server
```

---

### Q3: 数据库连接失败

**错误消息：** `could not connect to server`

**解决方案：**
1. 检查 PostgreSQL 是否运行
2. 验证 .env 中的 DATABASE_URL 是否正确
3. 检查数据库用户是否存在

```bash
# 验证数据库连接
psql -U postgres -c "SELECT 1"

# 检查数据库用户
psql -U postgres -l
```

---

### Q4: 端口被占用

**错误消息：** `端口 8000 已被占用`

**解决方案：**
```bash
# 查看占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用 start.sh stop 命令
bash scripts/setup/start.sh stop
```

---

### Q5: 前端构建失败

**错误消息：** `npm ERR!`

**解决方案：**
```bash
# 清理缓存
cd frontend
rm -rf node_modules package-lock.json
npm install

# 重新构建
npm run build
```

---

## 📊 初始化后的系统状态

初始化完成后，系统包含：

**数据库：** stock_analysis

**数据库表：** 18 个（含分区表）

**默认账户：**
- 用户名: admin
- 密码: admin123（首次登录后需修改）

**可用的指标类型：**
- TTV：总交易额
- EEE：有效交易额

**服务监听地址：**
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 前端应用: http://localhost:3000

---

## 📚 后续步骤

初始化完成后的下一步：

1. **导入数据**
   - 查看 `/imports/README.md` 了解如何导入数据
   - 使用 `bash scripts/setup/start.sh all` 启动服务后即可导入

2. **开发代码**
   - 后端代码在 `backend/app/`
   - 前端代码在 `frontend/src/`
   - 查看 `docs/development/` 了解编码规范

3. **查看文档**
   - 架构设计：`docs/architecture/`
   - 开发指南：`docs/development/`
   - 项目进度：`docs/project/`

---

## 🔗 相关文档

| 文档 | 位置 | 用途 |
|------|------|------|
| **数据导入指南** | `/imports/README.md` | 如何导入 CSV/TXT 数据 |
| **开发环境配置** | `docs/development/SETUP.md` | 详细的开发环境说明 |
| **架构设计** | `docs/architecture/SYSTEM_DESIGN.md` | 系统架构详解 |
| **数据库设计** | `docs/architecture/DATABASE_DESIGN.md` | 数据库表设计说明 |
| **API 文档** | http://localhost:8000/docs | 运行后在线查看 |
| **项目进度** | `docs/project/PROGRESS.md` | 当前开发进度 |

---

## ✨ 提示和最佳实践

**1. 环境变量管理**
- `.env` 文件包含敏感信息，不应提交到 Git
- 生产环境应使用环境变量而非文件

**2. 数据库备份**
- 重新初始化前请备份数据库
```bash
pg_dump stock_analysis > backup.sql
```

**3. 定期维护**
- 定期运行 `02_optimize_indexes.sql` 优化性能
- 监控数据库大小和性能

**4. 升级部署**
- 始终在非生产环境测试初始化脚本
- 保留旧的初始化记录用于问题排查

---

## 📞 需要帮助？

遇到问题或有疑问？

1. 检查上面的常见问题部分
2. 查看脚本中的注释和说明
3. 查看相关的文档文件
4. 运行脚本时加上 `-v` 或 `--verbose` 获取详细输出

---

**最后更新：** 2024-11-25
**版本：** v2.0
**状态：** ✅ 完成

