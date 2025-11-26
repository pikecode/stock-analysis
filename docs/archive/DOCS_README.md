# 📚 项目文档总览

欢迎来到股票分析系统的完整文档库。本文档提供了整个项目的导航和快速查找。

---

## 📂 文档分类

### 🏗️ 架构设计文档 (`/docs/architecture/`)

系统的架构设计、数据库设计、API 设计等技术文档。

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| **SYSTEM_DESIGN.md** | 系统整体架构设计 | 项目经理、架构师 |
| **DATABASE_DESIGN.md** | 数据库表结构和关系 | 数据库管理员、后端开发 |
| **API_DESIGN.md** | API 端点设计和规范 | 后端开发、前端开发 |
| **README.md** | 架构文档导航 | 所有人 |

---

### 🛠️ 开发文档 (`/docs/development/`)

开发环境设置、编码规范、工作流等开发相关文档。

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| **SETUP.md** | 开发环境配置详细指南 | 新开发成员 |
| **CODING_STANDARDS.md** | 编码规范和最佳实践 | 所有开发人员 |
| **GIT_WORKFLOW.md** | Git 工作流和提交规范 | 所有开发人员 |
| **README.md** | 开发文档导航 | 开发人员 |

---

### 📊 项目管理文档 (`/docs/project/`)

项目的进度跟踪、任务列表、路线图等管理文档。

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| **PROGRESS.md** | 当前开发进度和完成情况 | 项目经理、团队成员 |
| **TASKS.md** | 当前任务列表和待办项 | 项目经理、开发团队 |
| **ROADMAP.md** | 项目长期规划和里程碑 | 产品经理、项目经理 |
| **README.md** | 项目文档导航 | 项目团队 |

---

### 📖 使用指南 (`/docs/guides/`)

系统使用和功能说明文档。

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| **01_IMPORT_OVERVIEW.md** | 导入系统概览 | 数据管理人员 |
| **02_DIRECT_IMPORT.md** | 单文件导入使用指南 | 数据管理人员 |
| **03_BATCH_IMPORT.md** | 批量导入快速参考 | 数据管理人员 |
| **04_BATCH_IMPORT_COMPLETE.md** | 批量导入完整指南 | 数据管理人员 |

---

### 🚀 系统初始化 (`/scripts/setup/`)

系统初始化和启动脚本的说明。

| 脚本 | 用途 | 说明 |
|------|------|------|
| **README.md** | 系统初始化完整指南 | 系统管理员、开发人员 |
| **init.sh** | 完整初始化脚本 | 首次部署 |
| **init-db.sh** | 数据库初始化脚本 | 数据库重置 |
| **start.sh** | 服务启动和管理脚本 | 日常操作 |

---

### 📥 数据导入 (`/imports/`)

数据导入工具和使用指南。

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| **README.md** | 导入工具总览 | 数据管理人员 |
| **01_IMPORT_OVERVIEW.md** | 导入系统详细说明 | 技术人员 |
| **02_DIRECT_IMPORT.md** | 直接导入使用指南 | 数据管理人员 |
| **03_BATCH_IMPORT.md** | 批量导入快速参考 | 数据管理人员 |
| **04_BATCH_IMPORT_COMPLETE.md** | 批量导入完整指南 | 技术人员 |

---

## 🎯 快速导航

### 我是新开发成员

从这里开始：

1. 📖 阅读 [项目概览](#项目概览)
2. 🔧 跟随 [docs/development/SETUP.md](development/SETUP.md) 配置开发环境
3. 📝 查看 [docs/development/CODING_STANDARDS.md](development/CODING_STANDARDS.md) 了解编码规范
4. 🌳 阅读 [docs/development/GIT_WORKFLOW.md](development/GIT_WORKFLOW.md) 学习 Git 工作流
5. 🏗️ 查看 [docs/architecture/](architecture/) 理解系统设计

---

### 我想了解系统架构

推荐阅读顺序：

1. 🏗️ [docs/architecture/SYSTEM_DESIGN.md](architecture/SYSTEM_DESIGN.md) - 系统整体设计
2. 🗄️ [docs/architecture/DATABASE_DESIGN.md](architecture/DATABASE_DESIGN.md) - 数据库结构
3. 📡 [docs/architecture/API_DESIGN.md](architecture/API_DESIGN.md) - API 接口设计

---

### 我需要导入数据

按照这个顺序：

1. 🚀 [scripts/setup/README.md](../scripts/setup/README.md) - 确保系统已初始化
2. 📥 [imports/README.md](../imports/README.md) - 了解导入工具
3. 📖 [imports/01_IMPORT_OVERVIEW.md](../imports/01_IMPORT_OVERVIEW.md) - 导入系统概览
4. 📝 根据文件类型选择对应的导入文档

---

### 我要初始化系统

按照这个顺序：

1. 🚀 [scripts/setup/README.md](../scripts/setup/README.md) - 系统初始化完整指南
2. 执行初始化脚本
3. 📖 [docs/development/SETUP.md](development/SETUP.md) - 开发环境详细配置

---

### 我想查看项目进度

访问项目管理文档：

1. 📊 [docs/project/PROGRESS.md](project/PROGRESS.md) - 当前进度
2. ✅ [docs/project/TASKS.md](project/TASKS.md) - 任务列表
3. 🗺️ [docs/project/ROADMAP.md](project/ROADMAP.md) - 长期规划

---

## 📋 项目概览

### 项目简介

股票分析系统是一个专注于概念股票分析和数据可视化的综合平台。

**核心功能：**
- 📊 股票-概念映射管理
- 📈 概念交易数据分析
- 🔍 多维度数据查询
- 📥 批量数据导入和处理
- 📊 数据可视化展示

---

### 技术栈

**后端：**
- Python 3.11+
- FastAPI
- SQLAlchemy ORM
- PostgreSQL 15+
- Redis 7+
- Celery 任务队列

**前端：**
- React 18+
- TypeScript
- Vite
- TailwindCSS
- ECharts 可视化

**DevOps：**
- Docker & Docker Compose
- PostgreSQL 数据库
- Redis 缓存
- Nginx 反向代理

---

### 目录结构

```
stock-analysis/
├── scripts/setup/               🚀 系统初始化和启动
│   ├── README.md                📖 初始化指南
│   ├── init.sh                  初始化脚本
│   ├── start.sh                 启动脚本
│   └── *.sql                    数据库初始化SQL
│
├── imports/                     📥 数据导入工具
│   ├── README.md                导入工具总览
│   ├── direct_import.py         单文件导入脚本
│   ├── batch_import.py          批量导入脚本
│   └── *.md                     导入指南文档
│
├── docs/                        📚 项目文档
│   ├── README.md                📋 本文档
│   ├── architecture/            🏗️ 架构设计
│   ├── development/             🛠️ 开发文档
│   ├── project/                 📊 项目管理
│   └── guides/                  📖 使用指南
│
├── backend/                     🛠️ 后端代码
│   ├── app/                     FastAPI 应用
│   ├── requirements.txt         依赖列表
│   └── venv/                    虚拟环境
│
├── frontend/                    🎨 前端代码
│   ├── src/                     React 源码
│   ├── package.json             npm 依赖
│   └── dist/                    构建输出
│
├── database/                    🗄️ 数据库脚本
│   ├── scripts/                 SQL 脚本
│   ├── migrations/              迁移文件
│   └── seeds/                   种子数据
│
├── .env                         ⚙️ 环境配置
├── quick_commands.sh            🚀 快速命令工具
├── README.md                    📖 项目主文档
└── docker-compose.yml           🐳 Docker 配置
```

---

## 🔗 相关资源

### 在线文档

- **API 文档**（运行后）: http://localhost:8000/docs
- **源代码**: backend/app/, frontend/src/
- **数据库**: PostgreSQL 连接见 .env

### 工具和命令

```bash
# 系统初始化
bash scripts/setup/init.sh

# 启动所有服务
bash scripts/setup/start.sh all

# 加载快速命令
source quick_commands.sh
show_help

# 查看导入指南
cat imports/README.md
```

---

## ❓ 文档索引

### 按主题分类

**系统部署：**
- `scripts/setup/README.md` - 系统初始化指南
- `docs/development/SETUP.md` - 开发环境配置

**架构和设计：**
- `docs/architecture/SYSTEM_DESIGN.md` - 系统架构
- `docs/architecture/DATABASE_DESIGN.md` - 数据库设计
- `docs/architecture/API_DESIGN.md` - API 设计

**开发工作：**
- `docs/development/CODING_STANDARDS.md` - 编码规范
- `docs/development/GIT_WORKFLOW.md` - Git 工作流

**数据导入：**
- `imports/README.md` - 导入工具总览
- `imports/01_IMPORT_OVERVIEW.md` - 导入系统概览
- `imports/04_BATCH_IMPORT_COMPLETE.md` - 批量导入完整指南

**项目管理：**
- `docs/project/PROGRESS.md` - 当前进度
- `docs/project/TASKS.md` - 任务列表
- `docs/project/ROADMAP.md` - 项目规划

---

## 📞 获取帮助

**遇到问题？**

1. 在相应的文档中查找
2. 检查文档的常见问题部分
3. 查看脚本中的注释和帮助信息
4. 联系项目团队

**查找特定信息？**

使用下面的快速索引：

| 需要 | 查看 |
|------|------|
| 系统如何初始化 | `scripts/setup/README.md` |
| 如何导入数据 | `imports/README.md` |
| 开发环境配置 | `docs/development/SETUP.md` |
| 编码规范 | `docs/development/CODING_STANDARDS.md` |
| 数据库表结构 | `docs/architecture/DATABASE_DESIGN.md` |
| API 文档 | http://localhost:8000/docs |
| 项目进度 | `docs/project/PROGRESS.md` |
| Git 工作流 | `docs/development/GIT_WORKFLOW.md` |

---

## 🔄 文档维护

**更新建议：**
- 新功能添加后更新相应的设计文档
- 架构变更需更新 SYSTEM_DESIGN.md
- 新 API 端点需更新 API_DESIGN.md
- 定期更新项目进度
- 保持 README 和导航文档最新

---

**最后更新：** 2024-11-25
**版本：** v2.0
**维护者：** 项目团队

