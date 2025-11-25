# 📈 股票分析系统

> 企业级股票数据导入与分析平台

## 🚀 快速开始

### 1️⃣ 初始化环境

```bash
# 进入项目目录
cd /Users/peakom/work/stock-analysis

# 加载快速命令
source quick_commands.sh

# 显示所有可用命令
show_help
```

### 2️⃣ 创建数据库表和分区

```bash
# 创建分区表
create_partitions

# 优化索引
optimize_indexes
```

### 3️⃣ 导入数据

```bash
# 导入CSV文件（股票-概念映射）
import_csv /path/to/stock.csv

# 导入TXT文件（交易数据）
import_txt /path/to/trade.txt EEE

# 批量导入大文件（多日期并行）
batch_import /path/to/large.txt EEE 8

# 继续中断的导入
resume_import /path/to/large.txt EEE 8
```

---

## 📂 项目结构

```
stock-analysis/
├── 📄 README.md                  # ⭐ 项目主文档（你在这里）
├── 📄 quick_commands.sh          # 快速命令工具
│
├── 📁 docs/                      # 📚 项目文档
│   └── guides/                   # 使用指南
│       ├── 01_IMPORT_OVERVIEW.md
│       ├── 02_DIRECT_IMPORT.md
│       ├── 03_BATCH_IMPORT.md
│       └── 04_BATCH_IMPORT_COMPLETE.md
│
├── 📁 scripts/                   # 🔧 Python脚本
│   ├── imports/                  # 导入脚本
│   │   ├── direct_import.py
│   │   └── batch_import.py
│   ├── analysis/                 # 分析脚本（待开发）
│   └── maintenance/              # 维护脚本（待开发）
│
├── 📁 database/                  # 🗄️ 数据库管理
│   ├── scripts/                  # SQL脚本
│   │   ├── 01_create_partitions.sql
│   │   └── 02_optimize_indexes.sql
│   ├── migrations/               # 数据迁移（待开发）
│   └── seeds/                    # 种子数据（待开发）
│
├── 📁 backend/                   # 🛠️ 后端代码
│   ├── app/
│   │   ├── services/             # 业务服务
│   │   ├── models/               # 数据模型
│   │   └── core/                 # 核心配置
│   └── ...
│
├── 📁 frontend/                  # 🎨 前端代码
│   └── ...
│
└── 📁 deploy/                    # 🚀 部署配置
    └── ...
```

---

## 📚 文档中心

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [导入总览](docs/guides/01_IMPORT_OVERVIEW.md) | 导入系统概述 | 新手 |
| [直接导入指南](docs/guides/02_DIRECT_IMPORT.md) | 单文件快速导入 | 日常使用 |
| [批量导入快速版](docs/guides/03_BATCH_IMPORT.md) | 批量导入速查 | 快速参考 |
| [批量导入完整版](docs/guides/04_BATCH_IMPORT_COMPLETE.md) | 详细使用指南 | 深入学习 |

---

## 🎯 常见操作

### 导入数据

```bash
# CSV导入
python scripts/imports/direct_import.py data.csv --type CSV

# TXT导入
python scripts/imports/direct_import.py data.txt --type TXT --metric-code EEE

# 批量导入
python scripts/imports/batch_import.py large.txt --metric-code EEE --parallel 8

# 继续导入
python scripts/imports/batch_import.py large.txt --metric-code EEE --resume
```

### 快速命令

```bash
# 加载命令工具
source quick_commands.sh

# 显示所有命令
show_help

# 导入CSV
import_csv /path/to/data.csv

# 导入TXT
import_txt /path/to/data.txt EEE

# 批量导入
batch_import /path/to/large.txt EEE 8

# 查看统计
import_stats

# 创建分区
create_partitions

# 优化索引
optimize_indexes
```

---

## 📊 使用示例

### 导入300万条数据

```bash
# 1. 创建分区表
create_partitions

# 2. 开始导入（8个进程）
batch_import /Users/peakom/Documents/work/数据处理/EEE.txt EEE 8

# 3. 查看进度
check_progress EEE

# 4. 导入完成后验证
import_stats
```

### 中断后继续

```bash
# 继续导入
resume_import /path/to/EEE.txt EEE 8
```

---

## ⚙️ 配置

### 数据库配置

文件: `backend/app/core/config.py`

```python
DATABASE_URL = "postgresql://peakom:password@localhost/stock_analysis"
```

### 环境要求

- Python 3.8+
- PostgreSQL 12+
- 4GB+ 内存

---

## 🔗 快速链接

- [导入指南](docs/guides/)
- [SQL脚本](database/scripts/)
- [Python脚本](scripts/imports/)

---

**版本**: v2.0 | **更新**: 2024-11-25 | **维护者**: Stock Analysis Team
