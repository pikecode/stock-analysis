# 📚 股票分析系统 - 项目文档与脚本索引

> 项目所有文档、脚本和工具的统一入口

## 🗂️ 项目结构概览

```
stock-analysis/backend/
├── 📁 app/                     # 应用核心代码
│   ├── 📁 services/           # 业务服务
│   ├── 📁 models/             # 数据模型
│   └── 📁 api/                # API接口
├── 📁 database/                # 数据库相关
│   ├── 📁 migrations/         # 数据迁移文件
│   ├── 📁 scripts/            # SQL脚本
│   └── 📁 seeds/              # 种子数据
├── 📁 scripts/                 # Python脚本工具
│   ├── 📁 imports/            # 导入脚本
│   ├── 📁 analysis/           # 分析脚本
│   └── 📁 maintenance/        # 维护脚本
├── 📁 docs/                    # 项目文档
│   ├── 📁 guides/             # 使用指南
│   ├── 📁 api/                # API文档
│   └── 📁 database/           # 数据库文档
└── 📁 tests/                   # 测试代码
```

---

## 🚀 快速导航

### 一、数据导入工具

| 工具 | 位置 | 用途 | 文档 |
|------|------|------|------|
| **直接导入** | `scripts/imports/direct_import.py` | 单文件快速导入 | [使用指南](docs/guides/02_DIRECT_IMPORT.md) |
| **批量导入** | `scripts/imports/batch_import.py` | 大文件并行导入 | [完整指南](docs/guides/04_BATCH_IMPORT_COMPLETE.md) |

#### 🎯 快速开始

```bash
# CSV导入（股票-概念映射）
python scripts/imports/direct_import.py data.csv --type CSV

# TXT导入（交易数据）
python scripts/imports/direct_import.py data.txt --type TXT --metric-code EEE

# 批量导入（大文件）
python scripts/imports/batch_import.py large_file.txt --metric-code EEE --parallel 8
```

---

## 📖 文档中心

### 1️⃣ 使用指南 (`docs/guides/`)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [01_IMPORT_OVERVIEW.md](docs/guides/01_IMPORT_OVERVIEW.md) | 导入系统总览 | 新手入门 |
| [02_DIRECT_IMPORT.md](docs/guides/02_DIRECT_IMPORT.md) | 直接导入详解 | 日常使用 |
| [03_BATCH_IMPORT.md](docs/guides/03_BATCH_IMPORT.md) | 批量导入快速版 | 快速参考 |
| [04_BATCH_IMPORT_COMPLETE.md](docs/guides/04_BATCH_IMPORT_COMPLETE.md) | 批量导入完整版 | 深入学习 |

### 2️⃣ 数据库文档 (`docs/database/`)

| 文档 | 说明 |
|------|------|
| 表结构说明 | 所有表的字段说明 |
| 分区表管理 | 分区表创建和维护 |
| 索引优化 | 查询性能优化 |

### 3️⃣ API文档 (`docs/api/`)

| 文档 | 说明 |
|------|------|
| RESTful API | HTTP接口说明 |
| 错误码参考 | 错误处理指南 |

---

## 🛠️ 脚本工具箱

### 📥 导入脚本 (`scripts/imports/`)

```bash
scripts/imports/
├── direct_import.py        # 单文件导入
├── batch_import.py         # 批量并行导入
└── validate_import.py      # 导入验证（待开发）
```

### 📊 分析脚本 (`scripts/analysis/`)

```bash
scripts/analysis/
├── daily_ranking.py        # 日排名分析（待开发）
├── concept_analysis.py     # 概念板块分析（待开发）
└── trend_analysis.py       # 趋势分析（待开发）
```

### 🔧 维护脚本 (`scripts/maintenance/`)

```bash
scripts/maintenance/
├── cleanup_old_data.py     # 清理历史数据（待开发）
├── backup_database.py      # 数据库备份（待开发）
└── health_check.py         # 健康检查（待开发）
```

---

## 💾 数据库脚本

### SQL脚本 (`database/scripts/`)

| 脚本 | 用途 | 使用方法 |
|------|------|----------|
| `01_create_partitions.sql` | 创建分区表 | `psql -f database/scripts/01_create_partitions.sql` |
| `02_optimize_indexes.sql` | 优化索引 | `psql -f database/scripts/02_optimize_indexes.sql` |
| `init_tables.sql` | 初始化表结构 | `psql -f init_tables.sql` |

### 常用SQL命令

```sql
-- 查看分区表
SELECT tablename FROM pg_tables
WHERE tablename LIKE '%_2024_%'
ORDER BY tablename;

-- 查看导入数据统计
SELECT metric_code, COUNT(DISTINCT trade_date) as days, COUNT(*) as records
FROM concept_stock_daily_rank
GROUP BY metric_code;

-- 清理测试数据
DELETE FROM import_batches WHERE file_name LIKE '%TEST%';
```

---

## 📋 标准操作流程

### 1. 首次部署

```bash
# 1. 初始化数据库
psql -U peakom -d stock_analysis -f init_tables.sql

# 2. 创建分区表
psql -U peakom -d stock_analysis -f database/scripts/01_create_partitions.sql

# 3. 优化索引
psql -U peakom -d stock_analysis -f database/scripts/02_optimize_indexes.sql
```

### 2. 日常导入

```bash
# CSV导入
python scripts/imports/direct_import.py /path/to/stock.csv --type CSV

# TXT导入（单日）
python scripts/imports/direct_import.py /path/to/trade.txt --type TXT --metric-code EEE --date 2024-11-25

# TXT批量导入（多日）
python scripts/imports/batch_import.py /path/to/large.txt --metric-code EEE --parallel 8
```

### 3. 数据验证

```sql
-- 验证导入结果
psql -U peakom -d stock_analysis << EOF
SELECT
    metric_code,
    MIN(trade_date) as 开始日期,
    MAX(trade_date) as 结束日期,
    COUNT(DISTINCT trade_date) as 天数,
    COUNT(*) as 记录数
FROM concept_stock_daily_rank
GROUP BY metric_code;
EOF
```

---

## ⚙️ 配置文件

| 文件 | 位置 | 说明 |
|------|------|------|
| 数据库配置 | `app/core/config.py` | 数据库连接配置 |
| 环境变量 | `.env` | 敏感配置信息 |
| Git配置 | `.git/config` | Git账号配置 |

---

## 🐛 故障排查

### 常见问题快速索引

| 问题 | 解决方案 | 详细文档 |
|------|----------|----------|
| 分区表不存在 | 运行 `01_create_partitions.sql` | [批量导入指南#分区表管理](docs/guides/04_BATCH_IMPORT_COMPLETE.md#5-分区表管理) |
| 导入中断 | 使用 `--resume` 参数继续 | [批量导入指南#断点续传](docs/guides/04_BATCH_IMPORT_COMPLETE.md#6-进度管理与断点续传) |
| 内存不足 | 减少 `--parallel` 参数 | [性能优化](docs/guides/04_BATCH_IMPORT_COMPLETE.md#7-性能优化建议) |
| 编码错误 | 文件转换为UTF-8 | [常见问题](docs/guides/04_BATCH_IMPORT_COMPLETE.md#8-常见问题与解决) |

---

## 📊 项目统计

```bash
# 查看项目规模
echo "Python文件数: $(find . -name "*.py" | wc -l)"
echo "SQL文件数: $(find . -name "*.sql" | wc -l)"
echo "文档数: $(find . -name "*.md" | wc -l)"
echo "代码行数: $(find . -name "*.py" -exec wc -l {} + | tail -1)"
```

---

## 🔄 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2024-11-25 | v2.0 | 规范化目录结构，整理文档 |
| 2024-11-25 | v1.5 | 添加批量导入工具 |
| 2024-11-24 | v1.0 | 初始版本，基础导入功能 |

---

## 📞 联系与支持

- **问题反馈**: 查看相关文档或检查日志文件
- **技术支持**: 参考故障排查指南
- **贡献代码**: Fork项目并提交PR

---

## 🔗 快捷链接

- [导入概览](docs/guides/01_IMPORT_OVERVIEW.md)
- [直接导入指南](docs/guides/02_DIRECT_IMPORT.md)
- [批量导入完整指南](docs/guides/04_BATCH_IMPORT_COMPLETE.md)
- [数据库脚本](database/scripts/)
- [导入脚本](scripts/imports/)

---

**项目根目录**: `/Users/peakom/work/stock-analysis/backend`
**最后更新**: 2024-11-25
**维护者**: Stock Analysis Team

---