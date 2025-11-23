# 文档索引

**股票概念分析系统 - 完整文档导航**

**最后更新**: 2025-11-23
**文档版本**: v2.0

---

## 文档结构

```
docs/
├── INDEX.md                    # 本文件 - 文档导航
├── README.md                   # 项目总览
│
├── design/                     # 设计文档
│   ├── README.md              # 设计文档导航
│   ├── SYSTEM_DESIGN.md       # 系统设计
│   ├── DATABASE_DESIGN.md     # 数据库设计
│   └── API_DESIGN.md          # API设计
│
├── development/                # 开发文档
│   ├── README.md              # 开发文档导航
│   ├── SETUP.md               # 环境搭建
│   ├── CODING_STANDARDS.md    # 编码规范
│   └── GIT_WORKFLOW.md        # Git工作流
│
├── project/                    # 项目管理
│   ├── README.md              # 项目管理导航
│   ├── ROADMAP.md             # 项目路线图
│   ├── PROGRESS.md            # 开发进度
│   └── TASKS.md               # 详细任务
│
├── sql/                        # SQL脚本
│   └── init_tables.sql        # 建表脚本
│
└── (详细设计文档)
    ├── OPTIMIZED_DESIGN.md    # 优化后的表设计
    ├── DATA_IMPORT_DESIGN.md  # 数据导入设计
    ├── MULTI_METRIC_DESIGN.md # 多指标系统设计
    └── METRIC_STORAGE_STRATEGY.md # 存储策略分析
```

---

## 快速导航

### 我是新加入的开发人员

1. 阅读 [README.md](../README.md) - 了解项目
2. 阅读 [development/SETUP.md](./development/SETUP.md) - 搭建环境
3. 阅读 [development/CODING_STANDARDS.md](./development/CODING_STANDARDS.md) - 了解规范
4. 浏览 [design/SYSTEM_DESIGN.md](./design/SYSTEM_DESIGN.md) - 理解架构

### 我要了解系统设计

→ 进入 [design/](./design/) 目录
- [系统设计](./design/SYSTEM_DESIGN.md)
- [数据库设计](./design/DATABASE_DESIGN.md)
- [API设计](./design/API_DESIGN.md)

### 我要了解数据导入逻辑

→ 阅读 [OPTIMIZED_DESIGN.md](./OPTIMIZED_DESIGN.md)

### 我要查看项目进度

→ 进入 [project/](./project/) 目录
- [项目路线图](./project/ROADMAP.md)
- [开发进度](./project/PROGRESS.md)
- [详细任务](./project/TASKS.md)

### 我要初始化数据库

→ 执行 [sql/init_tables.sql](./sql/init_tables.sql)

```bash
psql -d stock_analysis -f docs/sql/init_tables.sql
```

---

## 文档列表

### 设计文档 (`design/`)

| 文档 | 说明 | 状态 |
|-----|------|------|
| [SYSTEM_DESIGN.md](./design/SYSTEM_DESIGN.md) | 系统架构、技术栈、模块设计 | ✅ |
| [DATABASE_DESIGN.md](./design/DATABASE_DESIGN.md) | 表结构、ER图、索引策略 | ✅ |
| [API_DESIGN.md](./design/API_DESIGN.md) | API接口定义、请求响应格式 | ✅ |

### 详细设计文档

| 文档 | 说明 | 状态 |
|-----|------|------|
| [OPTIMIZED_DESIGN.md](./OPTIMIZED_DESIGN.md) | 优化后的表设计和导入计算逻辑 | ✅ |
| [DATA_IMPORT_DESIGN.md](./DATA_IMPORT_DESIGN.md) | 源数据保留与重算机制 | ✅ |
| [MULTI_METRIC_DESIGN.md](./MULTI_METRIC_DESIGN.md) | 多指标数据系统设计 | ✅ |
| [METRIC_STORAGE_STRATEGY.md](./METRIC_STORAGE_STRATEGY.md) | 多指标存储策略分析 | ✅ |

### 开发文档 (`development/`)

| 文档 | 说明 | 状态 |
|-----|------|------|
| [SETUP.md](./development/SETUP.md) | 开发环境搭建指南 | ✅ |
| [CODING_STANDARDS.md](./development/CODING_STANDARDS.md) | 编码规范（Python/TS/SQL） | ✅ |
| [GIT_WORKFLOW.md](./development/GIT_WORKFLOW.md) | Git分支策略和提交规范 | ✅ |

### 项目管理文档 (`project/`)

| 文档 | 说明 | 状态 |
|-----|------|------|
| [ROADMAP.md](./project/ROADMAP.md) | 项目路线图和里程碑 | ✅ |
| [PROGRESS.md](./project/PROGRESS.md) | 开发进度跟踪 | ✅ |
| [TASKS.md](./project/TASKS.md) | 详细任务分解（WBS） | ✅ |

### SQL脚本 (`sql/`)

| 文件 | 说明 | 状态 |
|-----|------|------|
| [init_tables.sql](./sql/init_tables.sql) | 完整建表脚本（11张表+存储过程） | ✅ |

---

## 按角色阅读建议

### 产品经理

1. [README.md](../README.md) - 产品概述
2. [project/ROADMAP.md](./project/ROADMAP.md) - 项目规划
3. [project/PROGRESS.md](./project/PROGRESS.md) - 进度跟踪

### 架构师

1. [design/SYSTEM_DESIGN.md](./design/SYSTEM_DESIGN.md) - 系统架构
2. [design/DATABASE_DESIGN.md](./design/DATABASE_DESIGN.md) - 数据库设计
3. [METRIC_STORAGE_STRATEGY.md](./METRIC_STORAGE_STRATEGY.md) - 存储决策

### 后端开发

1. [development/SETUP.md](./development/SETUP.md) - 环境搭建
2. [development/CODING_STANDARDS.md](./development/CODING_STANDARDS.md) - 编码规范
3. [design/API_DESIGN.md](./design/API_DESIGN.md) - API设计
4. [OPTIMIZED_DESIGN.md](./OPTIMIZED_DESIGN.md) - 表设计和导入逻辑
5. [sql/init_tables.sql](./sql/init_tables.sql) - 建表脚本

### 前端开发

1. [development/SETUP.md](./development/SETUP.md) - 环境搭建
2. [development/CODING_STANDARDS.md](./development/CODING_STANDARDS.md) - 编码规范
3. [design/API_DESIGN.md](./design/API_DESIGN.md) - API接口

### DBA

1. [design/DATABASE_DESIGN.md](./design/DATABASE_DESIGN.md) - 数据库设计
2. [sql/init_tables.sql](./sql/init_tables.sql) - 建表脚本
3. [OPTIMIZED_DESIGN.md](./OPTIMIZED_DESIGN.md) - 分区和索引策略

---

## 文档统计

| 类别 | 数量 | 说明 |
|-----|------|------|
| 设计文档 | 7 | 系统/数据库/API/详细设计 |
| 开发文档 | 3 | 环境/规范/Git |
| 项目文档 | 3 | 路线图/进度/任务 |
| SQL脚本 | 1 | 建表脚本 |
| **总计** | **14** | |

---

## 文档维护

### 更新原则

- 代码变更时同步更新文档
- 设计变更需更新相关设计文档
- 进度变更需更新project/PROGRESS.md

### 版本历史

| 版本 | 日期 | 变更 |
|-----|------|------|
| v1.0 | 2025-11-22 | 初始设计文档 |
| v2.0 | 2025-11-23 | 整合设计/开发/项目文档 |
