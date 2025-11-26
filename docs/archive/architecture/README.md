# 🏗️ 架构设计文档

本目录包含股票概念分析系统的完整架构和设计文档。

---

## 📂 文档结构

### 核心设计文档

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| **SYSTEM_DESIGN.md** | 系统整体架构设计、模块划分、流程图 | 架构师、项目经理 |
| **DATABASE_DESIGN.md** | 数据库表结构、关系图、索引策略 | 数据库管理员、后端开发 |
| **API_DESIGN.md** | API 端点设计、请求响应格式、错误处理 | 后端开发、前端开发 |

### 详细参考文档

以下为深度设计文档，供深入技术研究：

| 文档 | 说明 | 位置 |
|------|------|------|
| **DESIGN.md** | 完整的原始设计文档 | [../DESIGN.md](../DESIGN.md) |
| **OPTIMIZED_DESIGN.md** | 优化后的表设计和索引策略 | [../OPTIMIZED_DESIGN.md](../OPTIMIZED_DESIGN.md) |
| **DATA_IMPORT_DESIGN.md** | 数据导入系统设计 | [../DATA_IMPORT_DESIGN.md](../DATA_IMPORT_DESIGN.md) |
| **MULTI_METRIC_DESIGN.md** | 多指标系统设计和扩展方案 | [../MULTI_METRIC_DESIGN.md](../MULTI_METRIC_DESIGN.md) |
| **METRIC_STORAGE_STRATEGY.md** | 存储策略分析和优化建议 | [../METRIC_STORAGE_STRATEGY.md](../METRIC_STORAGE_STRATEGY.md) |
| **UNIFIED_IMPORT_LOGIC.md** | 统一导入逻辑设计 | [../UNIFIED_IMPORT_LOGIC.md](../UNIFIED_IMPORT_LOGIC.md) |

---

## 🎯 快速导航

### 场景 1: 我是新的架构师，需要了解系统

推荐阅读顺序：
1. 📖 本页 (README.md) - 了解文档结构
2. 🏗️ [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) - 系统整体架构
3. 🗄️ [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) - 数据库设计
4. 📡 [API_DESIGN.md](./API_DESIGN.md) - API 接口设计

---

### 场景 2: 我是数据库管理员

关注重点：
- 📊 [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) - 表结构和关系
- ⚡ [../OPTIMIZED_DESIGN.md](../OPTIMIZED_DESIGN.md) - 索引和性能优化
- 📈 [../METRIC_STORAGE_STRATEGY.md](../METRIC_STORAGE_STRATEGY.md) - 存储策略

---

### 场景 3: 我是后端开发人员

关注重点：
- 🏗️ [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) - 整体架构
- 📡 [API_DESIGN.md](./API_DESIGN.md) - API 设计规范
- 🗄️ [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) - 数据库操作
- 📥 [../DATA_IMPORT_DESIGN.md](../DATA_IMPORT_DESIGN.md) - 导入逻辑

---

### 场景 4: 我是前端开发人员

关注重点：
- 📡 [API_DESIGN.md](./API_DESIGN.md) - API 文档和规范
- 🏗️ [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) - 系统流程和交互

---

### 场景 5: 我需要优化系统性能

关注重点：
- ⚡ [../OPTIMIZED_DESIGN.md](../OPTIMIZED_DESIGN.md) - 优化策略
- 📈 [../METRIC_STORAGE_STRATEGY.md](../METRIC_STORAGE_STRATEGY.md) - 存储优化
- 📥 [../DATA_IMPORT_DESIGN.md](../DATA_IMPORT_DESIGN.md) - 导入优化

---

## 📊 系统设计总结

### 核心模块

```
┌─────────────────────────────────────────┐
│          API 层 (FastAPI)               │
│  - 股票管理  - 概念管理  - 数据查询     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      业务逻辑层 (Services)              │
│  - 数据导入  - 计算汇总  - 分析         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│     数据访问层 (SQLAlchemy ORM)        │
│  - 模型定义  - 查询构建  - 事务管理     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      数据库层 (PostgreSQL)              │
│  - 分区表   - 索引优化   - 备份        │
└─────────────────────────────────────────┘
```

### 数据流

```
外部数据 (CSV/TXT)
        ↓
    导入服务
        ↓
    数据解析和验证
        ↓
    批量插入/更新
        ↓
    计算汇总统计
        ↓
    数据库持久化
        ↓
    前端查询和展示
```

---

## 🔗 相关资源

### 与其他文档的关联

- **开发文档** - [docs/development/](../development/) - 编码规范、工作流
- **项目管理** - [docs/project/](../project/) - 进度、任务、规划
- **使用指南** - [docs/guides/](../guides/) - 如何使用系统
- **数据导入** - [imports/](../../imports/) - 导入工具文档

---

## 📝 维护说明

**最后更新：** 2024-11-25

**维护建议：**
- 架构变更时更新 SYSTEM_DESIGN.md
- 表结构变更时更新 DATABASE_DESIGN.md
- 新增 API 端点时更新 API_DESIGN.md
- 定期审查设计文档的准确性

---
