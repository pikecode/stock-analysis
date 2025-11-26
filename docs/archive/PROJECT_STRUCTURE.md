# 📂 项目结构说明

## 新的规范化目录结构

```
backend/
│
├── 📄 README_PROJECT_INDEX.md    # 🎯 主索引文档（从这里开始）
├── 📄 PROJECT_STRUCTURE.md       # 本文档
├── 📄 quick_commands.sh           # 快速命令工具
│
├── 📁 app/                        # 应用核心代码
│   ├── 📁 services/              # 业务服务
│   │   ├── optimized_csv_import.py    # CSV导入服务
│   │   ├── optimized_txt_import.py    # TXT导入服务
│   │   └── import_service.py          # 导入基础服务
│   ├── 📁 models/                # 数据模型
│   │   └── stock.py                   # 股票相关模型
│   └── 📁 core/                  # 核心配置
│       └── config.py                  # 配置文件
│
├── 📁 database/                   # 🗄️ 数据库相关（新增）
│   ├── 📁 scripts/               # SQL脚本
│   │   ├── 01_create_partitions.sql  # 创建分区表
│   │   └── 02_optimize_indexes.sql   # 优化索引
│   ├── 📁 migrations/            # 数据迁移（待添加）
│   └── 📁 seeds/                 # 种子数据（待添加）
│
├── 📁 scripts/                    # 🔧 Python脚本
│   ├── 📁 imports/               # 导入脚本（整理后）
│   │   ├── direct_import.py          # 直接导入
│   │   └── batch_import.py           # 批量导入
│   ├── 📁 analysis/              # 分析脚本（待开发）
│   └── 📁 maintenance/           # 维护脚本（待开发）
│
├── 📁 docs/                       # 📚 项目文档
│   ├── 📁 guides/                # 使用指南（整理后）
│   │   ├── 01_IMPORT_OVERVIEW.md     # 导入总览
│   │   ├── 02_DIRECT_IMPORT.md       # 直接导入指南
│   │   ├── 03_BATCH_IMPORT.md        # 批量导入快速版
│   │   └── 04_BATCH_IMPORT_COMPLETE.md # 批量导入完整版
│   ├── 📁 api/                   # API文档（待添加）
│   └── 📁 database/              # 数据库文档（待添加）
│
└── 📄 init_tables.sql             # 初始化表结构
```

## 🔄 文件移动记录

### 已移动的文件

| 原位置 | 新位置 | 说明 |
|--------|--------|------|
| `scripts/create_missing_partitions.sql` | `database/scripts/01_create_partitions.sql` | SQL脚本归类 |
| `scripts/optimize_database.sql` | `database/scripts/02_optimize_indexes.sql` | SQL脚本归类 |
| `scripts/direct_import.py` | `scripts/imports/direct_import.py` | Python脚本分类 |
| `scripts/batch_import.py` | `scripts/imports/batch_import.py` | Python脚本分类 |
| `scripts/IMPORT_GUIDE.md` | `docs/guides/01_IMPORT_OVERVIEW.md` | 文档规范化 |
| `docs/DIRECT_IMPORT_GUIDE.md` | `docs/guides/02_DIRECT_IMPORT.md` | 文档规范化 |
| `docs/BATCH_IMPORT_GUIDE.md` | `docs/guides/03_BATCH_IMPORT.md` | 文档规范化 |
| `docs/批量导入工具完整指南.md` | `docs/guides/04_BATCH_IMPORT_COMPLETE.md` | 文档规范化 |

## 📝 命名规范

### 文件命名

- **SQL脚本**: `序号_功能描述.sql` (如: `01_create_partitions.sql`)
- **Python脚本**: `功能_类型.py` (如: `direct_import.py`, `batch_import.py`)
- **文档**: `序号_大写标题.md` (如: `01_IMPORT_OVERVIEW.md`)

### 目录命名

- 使用小写字母
- 多词用下划线分隔（Python风格）
- 功能明确、简洁

## 🎯 使用建议

### 1. 新手入门
```bash
# 1. 查看主索引
cat README_PROJECT_INDEX.md

# 2. 加载快速命令
source quick_commands.sh

# 3. 显示帮助
show_help
```

### 2. 日常使用
```bash
# 使用快速命令
import_csv /path/to/data.csv
import_txt /path/to/data.txt EEE
batch_import /path/to/large.txt EEE 8
```

### 3. 开发参考
```bash
# 查看项目结构
cat PROJECT_STRUCTURE.md

# 查看具体文档
cat docs/guides/04_BATCH_IMPORT_COMPLETE.md
```

## ✅ 改进效果

### Before（之前）
- ❌ 文档散落在多个目录
- ❌ SQL和Python脚本混在一起
- ❌ 文档命名不统一（中英文混合）
- ❌ 没有统一入口

### After（现在）
- ✅ 清晰的目录结构
- ✅ 文件分类存放
- ✅ 统一的命名规范
- ✅ 主索引文档作为入口
- ✅ 快速命令工具提高效率

## 🚀 下一步计划

1. **待开发脚本**
   - `scripts/analysis/` - 数据分析脚本
   - `scripts/maintenance/` - 系统维护脚本

2. **待补充文档**
   - `docs/api/` - API接口文档
   - `docs/database/` - 数据库设计文档

3. **待添加功能**
   - `database/migrations/` - 数据库版本管理
   - `database/seeds/` - 测试数据

---

更新时间: 2024-11-25
维护者: Stock Analysis Team