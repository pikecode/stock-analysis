# 股票概念分析系统

<div align="center">

**一个强大的股票概念数据分析与可视化平台**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen.svg)](https://vuejs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[功能特性](#-功能特性) •
[快速开始](#-快速开始) •
[文档](#-文档) •
[技术栈](#-技术栈) •
[开发计划](#-开发计划)

</div>

---

## 📖 项目简介

股票概念分析系统是一个专业的数据分析平台，用于管理和分析股票与概念的关联关系，提供多维度的数据查询、排名分析和可视化展示。

### 核心价值

- 🎯 **精准分析**: 6大核心分析功能，全面覆盖股票概念分析需求
- 📊 **可视化**: 直观的图表展示，趋势一目了然
- 🚀 **高性能**: 分区表、索引优化、多级缓存，毫秒级响应
- 🔒 **安全可靠**: 完整的权限控制体系，数据安全有保障
- 💼 **易用性**: 便捷的数据导入，灵活的查询条件

### 适用场景

- ✅ 股票概念数据管理
- ✅ 多维度排名分析
- ✅ 趋势跟踪与可视化
- ✅ 概念热度统计
- ✅ 投资决策辅助

---

## ✨ 功能特性

### 数据管理

- 📤 **CSV数据导入**: 支持大文件上传，实时进度显示
- 🔍 **数据预览**: 导入前预览，确保数据正确
- 🗺️ **字段映射**: 灵活的字段映射配置
- 📝 **导入历史**: 完整的导入记录和错误日志

### 核心查询（6大功能）

1. **股票所属概念查询**: 快速查看股票归属的所有概念和行业
2. **每日排名查询**: 股票在各概念中每天的排名变化
3. **概念股票排名**: 查看概念中股票按交易值的排名
4. **上榜次数统计**: 统计股票在指定概念中进入前N名的次数
5. **排名历史分析**: 分析股票在概念中的排名趋势和统计信息
6. **概念数据汇总**: 每日概念总量、平均值、最大值等统计

### 数据可视化

- 📈 **趋势图**: 股票/概念的时间序列趋势
- 📊 **排名榜**: 日榜/周榜/月榜多维度展示
- 🔥 **热力图**: 概念相关性分析
- 📉 **对比图**: 多股票/多概念对比分析

### 用户管理

- 👥 **用户管理**: 完整的用户CRUD操作
- 🔐 **权限控制**: 基于角色的访问控制(RBAC)
- 📋 **操作日志**: 完整的审计日志记录
- 🔑 **JWT认证**: 安全的Token认证机制

### 报表导出

- 📄 **Excel导出**: 支持自定义列和筛选条件
- 📰 **PDF报告**: 专业的PDF报表生成
- 📁 **CSV导出**: 标准CSV格式导出

---

## 🚀 快速开始

### 前置要求

- Docker 24+
- Docker Compose 2.20+
- 8GB+ RAM
- 20GB+ 磁盘空间

### 一键启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd stock-analysis

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 启动所有服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/init_data.py

# 5. 访问系统
# 后台管理: http://localhost:8080
# 用户展示: http://localhost:8081
# API文档: http://localhost:8000/docs
```

### 默认登录

- 用户名: `admin`
- 密码: `admin123`

> 详细开发指南请参考: [快速开始文档](docs/QUICK_START.md)

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [设计文档](docs/DESIGN.md) | 完整的系统设计文档 |
| [设计评审](docs/DESIGN_REVIEW.md) | 设计评审和改进建议 |
| [快速开始](docs/QUICK_START.md) | 开发环境搭建指南 |
| [API文档](http://localhost:8000/docs) | 在线API文档（启动后访问） |

---

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.11+ | 编程语言 |
| **FastAPI** | 0.115+ | Web框架 |
| **SQLAlchemy** | 2.0+ | ORM |
| **PostgreSQL** | 15+ | 主数据库 |
| **Redis** | 7+ | 缓存 |
| **Celery** | 5.3+ | 异步任务 |
| **Alembic** | 1.13+ | 数据库迁移 |

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue** | 3.4+ | 前端框架 |
| **TypeScript** | 5.0+ | 类型系统 |
| **Element Plus** | 2.8+ | UI组件库（后台） |
| **Ant Design Vue** | 4.0+ | UI组件库（前台） |
| **ECharts** | 5.5+ | 数据可视化 |
| **Pinia** | 2.1+ | 状态管理 |
| **Vite** | 5.0+ | 构建工具 |

### 基础设施

| 技术 | 说明 |
|------|------|
| **Docker** | 容器化 |
| **Nginx** | 反向代理 |
| **MinIO** | 对象存储 |
| **Prometheus** | 监控 |
| **Grafana** | 可视化 |

---

## 📐 系统架构

```
┌─────────────────────────────────────────────────┐
│                  用户层                          │
│  ┌──────────────┐      ┌──────────────┐        │
│  │ 后台管理端   │      │  用户展示端  │        │
│  │ Vue + Element│      │ Vue + Ant D  │        │
│  └──────────────┘      └──────────────┘        │
└─────────────────────────────────────────────────┘
                    │ HTTPS
┌─────────────────────────────────────────────────┐
│              Nginx (API网关)                     │
└─────────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────────┐
│           FastAPI 应用服务                       │
│  ┌─────────┬─────────┬─────────┬─────────┐     │
│  │认证服务 │查询服务 │导入服务 │统计服务 │     │
│  └─────────┴─────────┴─────────┴─────────┘     │
│                                                  │
│  ┌──────────────────────────────────────┐      │
│  │    Celery Worker (异步任务)          │      │
│  └──────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
                    │
┌──────────┬──────────────┬──────────────┐
│PostgreSQL│    Redis     │    MinIO     │
│  (主库)  │   (缓存)     │  (文件存储)  │
└──────────┴──────────────┴──────────────┘
```

---

## 📊 核心功能演示

### 1. 数据导入

```
上传CSV文件 → 数据预览 → 字段映射 → 执行导入 → 实时进度 → 完成
```

### 2. 股票查询

```python
# API示例
GET /api/v1/stocks/600000/concepts

# 响应
{
  "stock_code": "600000",
  "stock_name": "浦发银行",
  "concepts": [
    {"id": 1, "name": "银行"},
    {"id": 2, "name": "上海板块"}
  ]
}
```

### 3. 排名分析

```python
# 股票在概念中的每日排名
POST /api/v1/analysis/stock-rank-trend
{
  "stock_code": "600000",
  "concept_ids": [1, 2],
  "start_date": "2025-08-01",
  "end_date": "2025-08-30"
}

# 响应包含每日排名趋势数据
```

---

## 📅 开发计划

### Phase 1: 基础框架 (Week 1)
- [x] 项目初始化
- [x] 数据库设计
- [x] 基础认证
- [ ] Docker环境

### Phase 2: 数据导入 (Week 2)
- [ ] 文件上传
- [ ] CSV解析
- [ ] 异步导入
- [ ] 进度推送

### Phase 3: 查询功能 (Week 2)
- [ ] 6大核心查询API
- [ ] 缓存优化
- [ ] 查询页面

### Phase 4: 可视化 (Week 3)
- [ ] ECharts集成
- [ ] 趋势图表
- [ ] 排名榜单

### Phase 5: 用户管理 (Week 3)
- [ ] 用户CRUD
- [ ] 权限控制
- [ ] 操作日志

### Phase 6-8: 完善上线 (Week 4)
- [ ] 报表导出
- [ ] 性能优化
- [ ] 测试部署

**预计完成时间**: 5.5周

当前进度: 🟩🟩⬜⬜⬜⬜⬜⬜ (25%)

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### Commit规范

使用 [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

---

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 📧 联系方式

- **项目维护者**: Stock Analysis Team
- **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [PostgreSQL](https://www.postgresql.org/) - 世界上最先进的开源数据库
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [Apache ECharts](https://echarts.apache.org/) - 强大的可视化库

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个⭐️！**

Made with ❤️ by the Stock Analysis Team

</div>
