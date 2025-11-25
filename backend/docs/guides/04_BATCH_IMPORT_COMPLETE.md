# 批量导入工具完整使用指南

> 适用于处理包含多个日期的大型TXT交易数据文件的高效导入工具

## 目录

1. [工具概述](#1-工具概述)
2. [快速开始](#2-快速开始)
3. [命令参数详解](#3-命令参数详解)
4. [使用场景示例](#4-使用场景示例)
5. [分区表管理](#5-分区表管理)
6. [进度管理与断点续传](#6-进度管理与断点续传)
7. [性能优化建议](#7-性能优化建议)
8. [常见问题与解决](#8-常见问题与解决)
9. [验证与查询](#9-验证与查询)
10. [最佳实践](#10-最佳实践)

---

## 1. 工具概述

### 1.1 功能特性

| 特性 | 说明 |
|------|------|
| **自动日期分组** | 自动识别文件中的所有日期并分组处理 |
| **多进程并行** | 支持1-CPU核心数的并行处理，大幅提升导入速度 |
| **断点续传** | 中断后可从上次位置继续，不会重复导入 |
| **进度可视化** | 实时显示处理进度条和状态信息 |
| **智能编码检测** | 自动检测UTF-8/GBK编码 |
| **错误追踪** | 详细记录失败的日期和原因 |
| **日期范围过滤** | 支持只导入指定日期范围的数据 |

### 1.2 适用场景

- 包含**多个日期**的大型交易数据文件（如：300万条，585个日期）
- 需要**批量导入**历史数据
- 需要**增量更新**特定日期范围的数据
- 导入过程可能**中断**需要续传的场景

### 1.3 文件格式要求

```
股票代码	日期	交易值
SH600000	2024-11-20	1000000
SZ000001	2024-11-20	1500000
SH600519	2024-11-21	2000000
```

- 字段分隔符：制表符（\t）或空格
- 日期格式：YYYY-MM-DD
- 交易值：整数或浮点数

---

## 2. 快速开始

### 2.1 基础命令

```bash
# 切换到项目目录
cd /Users/peakom/work/stock-analysis/backend

# 最简单的用法（默认4个进程）
python scripts/batch_import.py /path/to/data.txt --metric-code EEE
```

### 2.2 实际案例

```bash
# 导入你的EEE文件
python scripts/batch_import.py /Users/peakom/Documents/work/数据处理/EEE.txt --metric-code EEE

# 使用8个进程加速
python scripts/batch_import.py /Users/peakom/Documents/work/数据处理/EEE.txt --metric-code EEE --parallel 8
```

---

## 3. 命令参数详解

### 3.1 参数列表

| 参数 | 必需 | 默认值 | 说明 | 示例 |
|------|------|--------|------|------|
| `file` | ✅ | - | TXT文件路径 | `/path/to/EEE.txt` |
| `--metric-code` | ✅ | - | 指标代码 | `EEE`, `AAA`, `BBB` |
| `--type` | ❌ | `TXT` | 文件类型 | `TXT` |
| `--parallel` | ❌ | `4` | 并行进程数 | `1-16` |
| `--resume` | ❌ | `False` | 断点续传 | 添加则启用 |
| `--start-date` | ❌ | - | 开始日期 | `2024-01-01` |
| `--end-date` | ❌ | - | 结束日期 | `2024-12-31` |

### 3.2 参数详细说明

#### `--parallel` 并行进程数
```bash
# 单进程（最稳定，适合调试）
--parallel 1

# 中等并行（推荐）
--parallel 4

# 高并行（大文件，强CPU）
--parallel 8
```

#### `--resume` 断点续传
```bash
# 从上次中断的位置继续
python scripts/batch_import.py file.txt --metric-code EEE --resume
```

#### `--start-date` 和 `--end-date` 日期范围
```bash
# 只导入2024年的数据
--start-date 2024-01-01 --end-date 2024-12-31

# 只导入最近一个月
--start-date 2025-10-01
```

---

## 4. 使用场景示例

### 4.1 场景一：首次导入大文件

**情况**：有一个300万条数据、585个日期的文件需要导入

```bash
# 第1步：查看CPU核心数
python -c "import multiprocessing; print(f'CPU核心数: {multiprocessing.cpu_count()}')"
# 输出：CPU核心数: 8

# 第2步：使用合适的并行度导入
python scripts/batch_import.py /Users/peakom/Documents/work/数据处理/EEE.txt \
    --metric-code EEE \
    --parallel 6
```

**预期输出**：
```
开始扫描文件: /Users/peakom/Documents/work/数据处理/EEE.txt
扫描文件: 100%|████████| 3078302/3078302 [00:05<00:00, 615660.40it/s]
扫描完成: 585个日期, 3078302条数据

============================================================
📊 文件统计:
  总日期数: 585
  总数据量: 3078302
  已处理: 0
  失败: 0
============================================================

准备处理 585 个日期，使用 6 个进程
导入进度: 100%|████████| 585/585 [18:30<00:00, 1.90s/it]

============================================================
✅ 导入完成:
  成功: 585/585
  失败: 0
  耗时: 0:18:30
============================================================
```

### 4.2 场景二：导入被中断

**情况**：导入过程中网络中断或手动停止

```bash
# 原始命令被中断
python scripts/batch_import.py file.txt --metric-code EEE --parallel 8
^C
接收到中断信号，保存进度...

# 查看进度文件
cat /tmp/batch_import_EEE.json

# 继续导入（自动跳过已完成的）
python scripts/batch_import.py file.txt --metric-code EEE --parallel 8 --resume
```

**输出显示续传状态**：
```
============================================================
📊 文件统计:
  总日期数: 585
  总数据量: 3078302
  已处理: 234  ← 已完成的
  失败: 5      ← 之前失败的
  继续从: 2024-05-15
============================================================
```

### 4.3 场景三：增量更新最新数据

**情况**：每天更新最新一周的数据

```bash
# 只导入最近7天的数据
python scripts/batch_import.py daily_update.txt \
    --metric-code EEE \
    --start-date 2025-11-18 \
    --end-date 2025-11-25 \
    --parallel 2
```

### 4.4 场景四：处理分区表缺失错误

**情况**：导入失败，提示分区不存在

```bash
# 错误信息
ERROR: no partition of relation "stock_metric_data_raw" found for row
DETAIL: Partition key of the failing row contains (trade_date) = (2024-03-15).
```

**解决步骤**：
```bash
# 第1步：运行分区创建脚本
psql -U peakom -d stock_analysis -f scripts/create_missing_partitions.sql

# 第2步：继续导入
python scripts/batch_import.py file.txt --metric-code EEE --resume
```

---

## 5. 分区表管理

### 5.1 检查现有分区

```sql
-- 查看所有分区表
psql -U peakom -d stock_analysis -c "
SELECT tablename,
       SUBSTRING(tablename FROM '\d{4}_\d{2}$') as year_month
FROM pg_tables
WHERE tablename LIKE 'stock_metric_data_raw_%'
   OR tablename LIKE 'concept_stock_daily_rank_%'
ORDER BY tablename;"
```

### 5.2 创建缺失分区

使用提供的SQL脚本：
```bash
psql -U peakom -d stock_analysis -f scripts/create_missing_partitions.sql
```

### 5.3 手动创建特定月份分区

```sql
-- 创建2024年3月的分区
CREATE TABLE IF NOT EXISTS stock_metric_data_raw_2024_03
PARTITION OF stock_metric_data_raw
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

CREATE TABLE IF NOT EXISTS concept_stock_daily_rank_2024_03
PARTITION OF concept_stock_daily_rank
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
```

---

## 6. 进度管理与断点续传

### 6.1 进度文件位置

进度文件自动保存在 `/tmp/` 目录：
```
/tmp/batch_import_EEE.json    # EEE指标的进度
/tmp/batch_import_AAA.json    # AAA指标的进度
```

### 6.2 进度文件结构

```json
{
  "file_path": "/path/to/EEE.txt",
  "file_hash": "a1b2c3d4e5f6",
  "total_dates": 585,
  "processed_dates": [
    "2024-01-01",
    "2024-01-02",
    "2024-01-03"
  ],
  "failed_dates": [
    "2024-03-15"
  ],
  "start_time": "2024-11-25T10:00:00",
  "last_update": "2024-11-25T10:15:23"
}
```

### 6.3 管理进度

```bash
# 查看进度
cat /tmp/batch_import_EEE.json | python -m json.tool

# 监控进度（实时更新）
watch -n 1 'cat /tmp/batch_import_EEE.json | python -m json.tool | grep processed_dates -A 1'

# 清理进度文件（重新开始）
rm /tmp/batch_import_EEE.json
```

---

## 7. 性能优化建议

### 7.1 并行度选择

| CPU核心数 | 推荐并行度 | 说明 |
|-----------|-----------|------|
| 2-4核 | 2-3 | 避免过载 |
| 6-8核 | 4-6 | 平衡性能 |
| 12-16核 | 8-10 | 高性能 |
| >16核 | 12-16 | 考虑数据库连接限制 |

### 7.2 性能基准测试

| 数据规模 | 进程数 | 预计耗时 |
|---------|--------|----------|
| 100个日期，50万条 | 1 | ~5分钟 |
| 100个日期，50万条 | 4 | ~2分钟 |
| 585个日期，300万条 | 1 | ~60分钟 |
| 585个日期，300万条 | 4 | ~20分钟 |
| 585个日期，300万条 | 8 | ~15分钟 |

### 7.3 优化建议

1. **分时导入**：避开数据库高峰期
2. **分批处理**：超大文件可按月份拆分
3. **监控资源**：
   ```bash
   # 监控CPU和内存
   top -p $(pgrep -f batch_import)

   # 监控数据库连接
   psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'stock_analysis';"
   ```

---

## 8. 常见问题与解决

### 8.1 编码错误

**问题**：
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**解决**：
- 工具已自动处理UTF-8和GBK编码
- 如仍有问题，先转换文件编码：
  ```bash
  iconv -f GBK -t UTF-8 input.txt > output.txt
  ```

### 8.2 内存不足

**问题**：
```
MemoryError: Unable to allocate array
```

**解决**：
1. 减少并行进程数：`--parallel 2`
2. 分批处理文件
3. 增加系统swap空间

### 8.3 数据库连接超限

**问题**：
```
FATAL: too many connections for role "peakom"
```

**解决**：
```bash
# 减少并行度
--parallel 2

# 或调整数据库配置
psql -c "ALTER SYSTEM SET max_connections = 200;"
psql -c "SELECT pg_reload_conf();"
```

### 8.4 分区表不存在

**问题**：
```
ERROR: no partition of relation "stock_metric_data_raw" found for row
DETAIL: Partition key of the failing row contains (trade_date) = (2024-03-15)
```

**解决**：
```bash
# 运行分区创建脚本
psql -U peakom -d stock_analysis -f scripts/create_missing_partitions.sql

# 然后继续导入
python scripts/batch_import.py file.txt --metric-code EEE --resume
```

### 8.5 部分股票没有概念关联

**问题**：部分数据被跳过

**原因**：股票没有概念关联，被过滤

**验证**：
```sql
-- 查看哪些股票没有概念
SELECT DISTINCT stock_code
FROM stock_metric_data_raw
WHERE stock_code NOT IN (
    SELECT DISTINCT stock_code FROM stock_concepts
);
```

---

## 9. 验证与查询

### 9.1 验证导入结果

```sql
-- 查看导入的日期范围和数据量
SELECT
    metric_code,
    MIN(trade_date) as 开始日期,
    MAX(trade_date) as 结束日期,
    COUNT(DISTINCT trade_date) as 日期数,
    COUNT(DISTINCT stock_code) as 股票数,
    COUNT(*) as 总记录数
FROM concept_stock_daily_rank
WHERE metric_code = 'EEE'
GROUP BY metric_code;

-- 查看每日数据分布
SELECT
    trade_date,
    COUNT(DISTINCT concept_id) as 概念数,
    COUNT(DISTINCT stock_code) as 股票数,
    COUNT(*) as 排名记录数,
    MAX(rank) as 最大排名
FROM concept_stock_daily_rank
WHERE metric_code = 'EEE'
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;

-- 查看汇总统计
SELECT
    trade_date,
    COUNT(*) as 概念数,
    SUM(stock_count) as 总股票数,
    AVG(avg_value)::INTEGER as 平均交易值
FROM concept_daily_summary
WHERE metric_code = 'EEE'
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;
```

### 9.2 查看导入批次

```sql
-- 查看最近的导入批次
SELECT
    id,
    file_name,
    status,
    total_rows,
    success_rows,
    error_rows,
    created_at,
    completed_at,
    CASE
        WHEN completed_at IS NOT NULL
        THEN (completed_at - created_at)::TEXT
        ELSE NULL
    END as 耗时
FROM import_batches
WHERE file_name LIKE '%EEE%'
ORDER BY created_at DESC
LIMIT 20;
```

### 9.3 检查失败记录

```bash
# 查看进度文件中的失败日期
cat /tmp/batch_import_EEE.json | python -c "
import json, sys
data = json.load(sys.stdin)
print(f'失败的日期 ({len(data["failed_dates"])}个):')
for date in sorted(data['failed_dates'])[:20]:
    print(f'  - {date}')
if len(data['failed_dates']) > 20:
    print(f'  ... 还有 {len(data["failed_dates"]) - 20} 个')
"
```

---

## 10. 最佳实践

### 10.1 导入流程建议

```bash
# 1. 预检查
echo "检查文件大小和行数..."
wc -l /path/to/data.txt

# 2. 小样本测试
echo "创建测试文件..."
head -1000 /path/to/data.txt > test_sample.txt
python scripts/batch_import.py test_sample.txt --metric-code TEST --parallel 1

# 3. 正式导入
echo "开始正式导入..."
python scripts/batch_import.py /path/to/data.txt --metric-code EEE --parallel 6

# 4. 验证结果
psql -U peakom -d stock_analysis -c "
SELECT COUNT(DISTINCT trade_date) as dates,
       COUNT(*) as records
FROM concept_stock_daily_rank
WHERE metric_code = 'EEE';"
```

### 10.2 定期任务配置

创建定时任务脚本 `daily_import.sh`：
```bash
#!/bin/bash
# 每日数据导入脚本

LOG_DIR="/var/log/stock_import"
DATA_DIR="/path/to/daily_data"
TODAY=$(date +%Y-%m-%d)

# 创建日志目录
mkdir -p $LOG_DIR

# 导入今日数据
python /path/to/scripts/batch_import.py \
    $DATA_DIR/EEE_$TODAY.txt \
    --metric-code EEE \
    --parallel 4 \
    2>&1 | tee $LOG_DIR/import_$TODAY.log

# 发送通知（可选）
if [ $? -eq 0 ]; then
    echo "导入成功" | mail -s "股票数据导入完成 $TODAY" admin@example.com
else
    echo "导入失败，请检查日志" | mail -s "股票数据导入失败 $TODAY" admin@example.com
fi
```

配置crontab：
```bash
# 每天凌晨2点执行
0 2 * * * /path/to/daily_import.sh
```

### 10.3 监控建议

1. **设置告警**：
   - 导入耗时超过预期
   - 失败日期数超过阈值
   - 数据库连接数异常

2. **保留日志**：
   ```bash
   python scripts/batch_import.py file.txt \
       --metric-code EEE \
       2>&1 | tee import_$(date +%Y%m%d_%H%M%S).log
   ```

3. **定期清理**：
   ```bash
   # 清理30天前的进度文件
   find /tmp -name "batch_import_*.json" -mtime +30 -delete
   ```

---

## 附录A：快速参考卡

```bash
# 基础导入
python scripts/batch_import.py file.txt --metric-code EEE

# 高速导入
python scripts/batch_import.py file.txt --metric-code EEE --parallel 8

# 断点续传
python scripts/batch_import.py file.txt --metric-code EEE --resume

# 日期范围
python scripts/batch_import.py file.txt --metric-code EEE \
    --start-date 2024-01-01 --end-date 2024-12-31

# 创建分区
psql -U peakom -d stock_analysis -f scripts/create_missing_partitions.sql

# 查看进度
cat /tmp/batch_import_EEE.json | python -m json.tool

# 验证结果
psql -U peakom -d stock_analysis -c "
SELECT COUNT(*) FROM concept_stock_daily_rank WHERE metric_code='EEE';"
```

---

## 附录B：故障排查流程图

```
导入失败
    ├── 分区表不存在？
    │   └── 运行 create_missing_partitions.sql
    ├── 内存不足？
    │   └── 减少 --parallel 参数
    ├── 数据库连接超限？
    │   └── 减少 --parallel 或增加 max_connections
    ├── 编码错误？
    │   └── 转换文件编码为 UTF-8
    └── 部分日期失败？
        └── 使用 --resume 继续导入
```

---

**文档版本**: v2.0
**更新日期**: 2024-11-25
**作者**: Stock Analysis Team
**支持**: 如有问题，请查看日志文件或联系技术支持

---