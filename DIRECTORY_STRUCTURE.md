# 📂 项目目录结构说明

## 全景视图

```
stock-analysis/                      # 项目根目录
│
├── 📄 README.md                     # ⭐ 项目主文档（从这里开始）
├── 📄 quick_commands.sh             # 🚀 快速命令工具
├── 📄 DIRECTORY_STRUCTURE.md        # 📋 本文档
├── 📄 PROJECT_STRUCTURE.md          # 项目结构详解（已弃用）
├── 📄 README_PROJECT_INDEX.md       # 项目索引详解（已弃用）
│
├── 📁 docs/                         # 📚 项目文档（统一管理）
│   ├── guides/                      # 使用指南
│   │   ├── 01_IMPORT_OVERVIEW.md   # 导入系统总览
│   │   ├── 02_DIRECT_IMPORT.md     # 直接导入指南
│   │   ├── 03_BATCH_IMPORT.md      # 批量导入快速版
│   │   └── 04_BATCH_IMPORT_COMPLETE.md # 批量导入完整版
│   ├── api/                         # API文档（待开发）
│   └── database/                    # 数据库文档（待开发）
│
├── 📁 scripts/                      # 🔧 Python脚本（统一管理）
│   ├── imports/                     # 导入脚本
│   │   ├── direct_import.py        # 单文件直接导入
│   │   └── batch_import.py         # 大文件批量导入
│   ├── analysis/                    # 分析脚本（待开发）
│   │   └── .gitkeep                # 占位符
│   └── maintenance/                 # 维护脚本（待开发）
│       └── .gitkeep                # 占位符
│
├── 📁 database/                     # 🗄️ 数据库管理（统一管理）
│   ├── scripts/                     # SQL脚本
│   │   ├── 01_create_partitions.sql # 创建分区表
│   │   └── 02_optimize_indexes.sql  # 优化索引
│   ├── migrations/                  # 数据迁移（待开发）
│   │   └── .gitkeep                # 占位符
│   └── seeds/                       # 种子数据（待开发）
│       └── .gitkeep                # 占位符
│
├── 📁 backend/                      # 🛠️ 后端应用代码
│   ├── app/
│   │   ├── services/               # 业务服务
│   │   │   ├── optimized_csv_import.py
│   │   │   ├── optimized_txt_import.py
│   │   │   ├── import_service.py
│   │   │   └── compute_service.py
│   │   ├── models/                 # 数据模型
│   │   ├── api/                    # API路由
│   │   ├── core/                   # 核心配置
│   │   └── __init__.py
│   ├── tests/                      # 测试代码
│   ├── requirements.txt            # Python依赖
│   ├── init_tables.sql            # 初始化表结构
│   └── ...
│
├── 📁 frontend/                     # 🎨 前端应用
│   ├── src/
│   ├── package.json
│   └── ...
│
├── 📁 deploy/                       # 🚀 部署配置
│   ├── native/
│   └── ...
│
├── 📁 .spec-workflow/              # 📋 规范工作流（CI/CD）
│   └── ...
│
├── .env.example                    # 环境变量示例
├── .gitignore                      # Git忽略配置
├── Makefile                        # 构建脚本
└── ...
```

---

## 按功能分类

### 📚 文档

| 位置 | 说明 |
|------|------|
| `docs/guides/01_IMPORT_OVERVIEW.md` | 导入系统概述 |
| `docs/guides/02_DIRECT_IMPORT.md` | 直接导入详解 |
| `docs/guides/03_BATCH_IMPORT.md` | 批量导入快速版 |
| `docs/guides/04_BATCH_IMPORT_COMPLETE.md` | 批量导入完整版 |

### 🔧 脚本

| 位置 | 说明 |
|------|------|
| `scripts/imports/direct_import.py` | 单文件导入 |
| `scripts/imports/batch_import.py` | 批量导入 |
| `quick_commands.sh` | 快速命令工具 |

### 🗄️ 数据库

| 位置 | 说明 |
|------|------|
| `database/scripts/01_create_partitions.sql` | 创建分区表 |
| `database/scripts/02_optimize_indexes.sql` | 优化索引 |
| `backend/init_tables.sql` | 初始化表 |

### 🛠️ 后端代码

| 位置 | 说明 |
|------|------|
| `backend/app/services/` | 业务逻辑 |
| `backend/app/models/` | 数据模型 |
| `backend/app/core/config.py` | 配置文件 |

---

## 使用指南

### 导入数据

```bash
# 从项目根目录
cd /Users/peakom/work/stock-analysis

# 加载快速命令
source quick_commands.sh

# 导入CSV
import_csv /path/to/data.csv

# 导入TXT
import_txt /path/to/data.txt EEE

# 批量导入
batch_import /path/to/large.txt EEE 8
```

### 执行SQL脚本

```bash
# 创建分区表
psql -U peakom -d stock_analysis -f database/scripts/01_create_partitions.sql

# 优化索引
psql -U peakom -d stock_analysis -f database/scripts/02_optimize_indexes.sql
```

### 查看文档

```bash
# 打开导入指南
cat docs/guides/02_DIRECT_IMPORT.md

# 打开批量导入完整指南
cat docs/guides/04_BATCH_IMPORT_COMPLETE.md
```

---

## 目录规范

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 目录 | 小写，多词用下划线 | `scripts/imports/` |
| 脚本 | 功能_类型.py | `batch_import.py` |
| SQL | 序号_功能.sql | `01_create_partitions.sql` |
| 文档 | 序号_标题.md | `01_IMPORT_OVERVIEW.md` |

### 目录职责

| 目录 | 职责 | 说明 |
|------|------|------|
| `docs/` | 所有文档 | 按功能分类 |
| `scripts/` | 所有脚本 | 按类型分类（imports/analysis/maintenance） |
| `database/` | 数据库管理 | SQL脚本、迁移、种子数据 |
| `backend/` | 后端代码 | 核心业务逻辑 |
| `frontend/` | 前端代码 | UI/UX实现 |

---

## 快速导航

### 🎯 我想...

| 任务 | 命令 | 位置 |
|------|------|------|
| 导入CSV数据 | `import_csv file.csv` | `scripts/imports/direct_import.py` |
| 导入TXT数据 | `import_txt file.txt EEE` | `scripts/imports/direct_import.py` |
| 批量导入 | `batch_import file.txt EEE` | `scripts/imports/batch_import.py` |
| 查看导入指南 | `cat docs/guides/02_DIRECT_IMPORT.md` | `docs/guides/` |
| 创建分区表 | `create_partitions` | `database/scripts/01_create_partitions.sql` |
| 查看快速命令 | `show_help` | `quick_commands.sh` |

---

## 重要说明

### ✅ 已整理到项目根目录

- ✅ 所有文档统一到 `docs/`
- ✅ 所有脚本统一到 `scripts/`
- ✅ 所有SQL脚本统一到 `database/`
- ✅ 创建了主 `README.md`
- ✅ 更新了脚本路径引用

### ⚠️ 原backend目录

`backend/` 目录下仍保留了备份：
- `backend/docs/` - 原文档备份
- `backend/scripts/` - 原脚本备份
- `backend/database/` - 原SQL脚本备份

这些是为了兼容性保留的，实际上所有文件已经复制到项目根目录。

### 🚀 下一步

1. ✅ 已完成：规范化项目目录结构
2. 待做：删除backend下的备份文件（可选）
3. 待做：补充API文档
4. 待做：开发分析脚本

---

**最后更新**: 2024-11-25
**版本**: v2.0
**作者**: Stock Analysis Team

