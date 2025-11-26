# 📚 项目文档组织结构（v2.0）

项目文档已重新组织，按照功能和用途分类，便于快速查找。

---

## 🎯 快速导航地图

```
股票分析系统
│
├─ 🚀 系统初始化与启动
│  └─ scripts/setup/README.md        ← 从这里开始！
│
├─ 📥 数据导入工具
│  └─ imports/README.md               ← 如何导入数据
│
├─ 📚 项目文档
│  │
│  ├─ 🏗️ 架构设计 (docs/architecture/)
│  │  ├─ README.md                   导航和快速指南
│  │  ├─ SYSTEM_DESIGN.md            系统整体架构
│  │  ├─ DATABASE_DESIGN.md          数据库表设计
│  │  └─ API_DESIGN.md               API 端点设计
│  │
│  ├─ 🛠️ 开发文档 (docs/development/)
│  │  ├─ README.md                   导航和工作流
│  │  ├─ SETUP.md                    环境搭建指南
│  │  ├─ CODING_STANDARDS.md         编码规范
│  │  └─ GIT_WORKFLOW.md             Git 工作流
│  │
│  ├─ 📊 项目管理 (docs/project/)
│  │  ├─ README.md                   导航和状态概览
│  │  ├─ ROADMAP.md                  长期规划和里程碑
│  │  ├─ PROGRESS.md                 当前开发进度
│  │  └─ TASKS.md                    详细任务列表
│  │
│  ├─ 📖 使用指南 (docs/guides/)
│  │  ├─ 01_IMPORT_OVERVIEW.md       导入系统概览
│  │  ├─ 02_DIRECT_IMPORT.md         直接导入指南
│  │  ├─ 03_BATCH_IMPORT.md          批量导入快速参考
│  │  └─ 04_BATCH_IMPORT_COMPLETE.md 批量导入完整指南
│  │
│  └─ docs/README.md                 📋 文档总导航（推荐首先阅读！）
│
├─ 🔧 快速命令
│  └─ quick_commands.sh               Shell 快速命令工具
│
└─ 📖 项目主文档
   └─ README.md                       项目概览和快速开始
```

---

## 📍 按用户角色的文档路线图

### 👨‍💼 项目经理

**推荐阅读顺序：**
1. 📖 `/docs/README.md` - 文档总览
2. 📊 `/docs/project/README.md` - 项目管理总览
3. 🗺️ `/docs/project/ROADMAP.md` - 长期规划
4. 📈 `/docs/project/PROGRESS.md` - 当前进度
5. ✅ `/docs/project/TASKS.md` - 任务详情

---

### 👨‍💻 后端开发

**推荐阅读顺序：**
1. 📖 `/docs/README.md` - 文档总览
2. 🚀 `/scripts/setup/README.md` - 系统初始化
3. 🛠️ `/docs/development/README.md` - 开发文档总览
4. 🔧 `/docs/development/SETUP.md` - 开发环境配置
5. 📝 `/docs/development/CODING_STANDARDS.md` - 编码规范
6. 🏗️ `/docs/architecture/README.md` - 架构文档总览
7. 🗄️ `/docs/architecture/DATABASE_DESIGN.md` - 数据库设计
8. 📡 `/docs/architecture/API_DESIGN.md` - API 设计

---

### 👨‍🎨 前端开发

**推荐阅读顺序：**
1. 📖 `/docs/README.md` - 文档总览
2. 🚀 `/scripts/setup/README.md` - 系统初始化
3. 🛠️ `/docs/development/README.md` - 开发文档总览
4. 🔧 `/docs/development/SETUP.md` - 开发环境配置
5. 📝 `/docs/development/CODING_STANDARDS.md` - 编码规范
6. 📡 `/docs/architecture/API_DESIGN.md` - API 设计和文档

---

### 👨‍🔧 系统管理员/DevOps

**推荐阅读顺序：**
1. 📖 `/docs/README.md` - 文档总览
2. 🚀 `/scripts/setup/README.md` - 系统初始化和启动
3. 🏗️ `/docs/architecture/DATABASE_DESIGN.md` - 数据库设计
4. ⚡ `/docs/architecture/README.md` - 架构文档（性能优化部分）

---

### 📊 数据分析员/数据工程师

**推荐阅读顺序：**
1. 📖 `/docs/README.md` - 文档总览
2. 📥 `/imports/README.md` - 导入工具总览
3. 📖 `/imports/01_IMPORT_OVERVIEW.md` - 导入系统详解
4. 📈 根据需要选择相应的导入指南

---

### 🎓 新加入团队的人员

**推荐学习路线：**
1. 📖 `/README.md` - 项目简介
2. 📖 `/docs/README.md` - 文档总览
3. 🚀 `/scripts/setup/README.md` - 系统初始化
4. 🛠️ `/docs/development/SETUP.md` - 开发环境配置
5. 🏗️ `/docs/architecture/SYSTEM_DESIGN.md` - 系统架构理解
6. 📝 `/docs/development/CODING_STANDARDS.md` - 编码规范
7. 🌳 `/docs/development/GIT_WORKFLOW.md` - 工作流程
8. 按照自己的角色补充阅读专业文档

---

## 📊 文档总览表

### 初始化和启动（scripts/setup/）

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| README.md | 系统初始化和启动指南 | **首次部署或重新配置** |
| init.sh | 完整的本地初始化脚本 | 首次设置开发环境 |
| init-db.sh | 数据库初始化脚本 | 需要重置数据库 |
| start.sh | 服务启动和管理脚本 | 日常开发时使用 |
| SQL 脚本 | 数据库表和索引创建 | 自动执行，特殊情况手动执行 |

### 数据导入（imports/）

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| README.md | 导入工具总览 | **开始导入数据前** |
| 01_IMPORT_OVERVIEW.md | 导入系统完整说明 | 需要理解导入原理 |
| 02_DIRECT_IMPORT.md | 单文件导入指南 | 导入 CSV 或小文件 |
| 03_BATCH_IMPORT.md | 批量导入快速参考 | 快速查阅命令 |
| 04_BATCH_IMPORT_COMPLETE.md | 批量导入完整指南 | 导入大文件或需要深入了解 |

### 架构设计（docs/architecture/）

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| README.md | 架构文档导航 | **开始技术研究前** |
| SYSTEM_DESIGN.md | 系统整体架构 | 理解系统设计 |
| DATABASE_DESIGN.md | 数据库表结构 | 数据库开发和优化 |
| API_DESIGN.md | API 端点和规范 | API 开发和调用 |

### 开发指南（docs/development/）

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| README.md | 开发文档导航 | **新开发人员入职** |
| SETUP.md | 开发环境搭建 | **首次配置环境** |
| CODING_STANDARDS.md | 编码规范 | 开发前和 Code Review 时 |
| GIT_WORKFLOW.md | Git 工作流 | **首次提交代码前** |

### 项目管理（docs/project/）

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| README.md | 项目管理导航 | **了解项目状态** |
| ROADMAP.md | 长期规划 | 了解项目方向 |
| PROGRESS.md | 当前进度 | **定期检查进度** |
| TASKS.md | 详细任务 | 分配任务或查看工作内容 |

### 使用指南（docs/guides/）

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| 01_IMPORT_OVERVIEW.md | 导入概览 | 开始导入前 |
| 02_DIRECT_IMPORT.md | 直接导入 | 单文件导入 |
| 03_BATCH_IMPORT.md | 批量导入参考 | 快速查阅 |
| 04_BATCH_IMPORT_COMPLETE.md | 完整导入指南 | 复杂场景导入 |

---

## 🔍 文档查找速查表

### 我想了解...

| 需要 | 位置 | 优先级 |
|------|------|--------|
| **系统如何初始化** | `/scripts/setup/README.md` | 🔴 首先 |
| **项目整体架构** | `/docs/architecture/SYSTEM_DESIGN.md` | 🟠 次要 |
| **数据库表结构** | `/docs/architecture/DATABASE_DESIGN.md` | 🟠 次要 |
| **API 如何使用** | `/docs/architecture/API_DESIGN.md` | 🟡 按需 |
| **如何导入数据** | `/imports/README.md` | 🔴 首先 |
| **开发环境配置** | `/docs/development/SETUP.md` | 🔴 首先 |
| **编码规范** | `/docs/development/CODING_STANDARDS.md` | 🟠 次要 |
| **Git 工作流** | `/docs/development/GIT_WORKFLOW.md` | 🟠 次要 |
| **项目进度** | `/docs/project/PROGRESS.md` | 🟡 按需 |
| **项目规划** | `/docs/project/ROADMAP.md` | 🟡 按需 |

---

## 📈 文档更新频率

| 文档 | 更新频率 | 维护责任 |
|------|---------|---------|
| `/scripts/setup/README.md` | 有变更时 | 系统管理员 |
| `/imports/README.md` | 有变更时 | 数据工程师 |
| `/docs/architecture/*` | 设计变更时 | 架构师 |
| `/docs/development/*` | 规范变更时 | Tech Lead |
| `/docs/project/PROGRESS.md` | 每周 | 项目经理 |
| `/docs/project/ROADMAP.md` | 里程碑时 | 产品经理 |
| `/docs/project/TASKS.md` | 任务变更时 | 项目经理 |

---

## ✨ 文档组织优势

### 之前（分散）
```
docs/
├── DESIGN.md
├── DESIGN_REVIEW.md
├── OPTIMIZED_DESIGN.md
├── DATA_IMPORT_DESIGN.md
├── MULTI_METRIC_DESIGN.md
├── METRIC_STORAGE_STRATEGY.md
├── UNIFIED_IMPORT_LOGIC.md
├── OPTIMIZATION_IMPLEMENTATION_GUIDE.md
├── QUICK_START.md
├── design/
├── development/
├── project/
├── guides/
└── ...（混乱）
```

**问题：**
- ❌ 难以找到相关文档
- ❌ 文档关系不清晰
- ❌ 重复和冗余
- ❌ 导航困难

### 现在（组织化）
```
docs/
├── README.md                        ← 统一入口
├── architecture/                    ← 架构设计
│   ├── README.md                   ← 导航
│   ├── SYSTEM_DESIGN.md
│   ├── DATABASE_DESIGN.md
│   └── API_DESIGN.md
├── development/                     ← 开发文档
│   ├── README.md                   ← 导航
│   ├── SETUP.md
│   ├── CODING_STANDARDS.md
│   └── GIT_WORKFLOW.md
├── project/                         ← 项目管理
│   ├── README.md                   ← 导航
│   ├── PROGRESS.md
│   ├── ROADMAP.md
│   └── TASKS.md
└── guides/                          ← 使用指南
    └── *.md
```

**优势：**
- ✅ 清晰的分类和层级
- ✅ 每个目录有 README 导航
- ✅ 快速找到所需文档
- ✅ 文档关系明确
- ✅ 易于维护和更新

---

## 🚀 推荐的文档阅读起点

### 首次接触项目
1. `/README.md` - 了解项目是什么
2. `/docs/README.md` - 了解文档结构
3. `/scripts/setup/README.md` - 初始化系统
4. 选择按角色的推荐路线继续

### 日常开发
- 需要查找命令：`source quick_commands.sh && show_help`
- 需要查找文档：`cat /docs/README.md`
- 需要查找代码规范：`cat /docs/development/CODING_STANDARDS.md`

### 遇到问题
1. 在相应的 README 中查找
2. 在文档中搜索关键词
3. 查看常见问题部分
4. 联系相关人员

---

## 📞 文档支持

**如果文档有问题：**
1. 检查是否有更新的版本
2. 查看维护说明
3. 报告问题给维护负责人

**如果文档不完整：**
1. 提交改进建议
2. 帮助更新文档
3. 共同完善知识库

---

**最后更新：** 2024-11-25
**版本：** v2.0
**状态：** ✅ 完成

