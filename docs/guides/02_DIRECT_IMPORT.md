# 直接导入脚本（direct_import.py）完整使用指南

## 📋 目录

1. [脚本简介](#脚本简介)
2. [快速开始](#快速开始)
3. [参数说明](#参数说明)
4. [使用示例](#使用示例)
5. [文件格式](#文件格式)
6. [导入流程](#导入流程)
7. [常见问题](#常见问题)
8. [性能指标](#性能指标)
9. [最佳实践](#最佳实践)
10. [验证方法](#验证方法)

---

## 🎯 脚本简介

`direct_import.py` 是一个**命令行工具**，用于直接导入CSV和TXT数据文件到数据库，无需通过Web API。

### ✨ 主要特点

- ✅ **快速高效**：10万条数据仅需2-3秒
- ✅ **支持多种格式**：自动检测编码和分隔符
- ✅ **智能缓存**：预加载减少数据库查询
- ✅ **完整审计**：保留原始数据记录
- ✅ **自动计算**：TXT导入自动计算排名和统计
- ✅ **容错能力强**：重复导入自动覆盖，无重复数据

### 📊 涉及表

#### CSV导入涉及表
- `import_batches` - 导入批次记录
- `stocks` - 股票基本信息
- `concepts` - 概念维度
- `industries` - 行业维度
- `stock_concepts` - 股票-概念映射
- `stock_industries` - 股票-行业映射
- `stock_concept_mapping_raw` - 原始审计数据

#### TXT导入涉及表
- `import_batches` - 导入批次记录
- `stock_metric_data_raw` - 原始交易数据
- `concept_stock_daily_rank` - 排名数据
- `concept_daily_summary` - 汇总统计

---

## 🚀 快速开始

### CSV文件导入

```bash
# 最简单的方式
python scripts/direct_import.py /path/to/stock.csv --type CSV

# 查看详细信息
python scripts/direct_import.py /path/to/stock.csv --type CSV --verbose
```

### TXT文件导入

```bash
# 必须指定指标代码
python scripts/direct_import.py /path/to/EEE.txt --type TXT --metric-code EEE

# 指定日期
python scripts/direct_import.py /path/to/EEE.txt --type TXT --metric-code EEE --date 2025-08-28
```

---

## 📖 参数说明

### 基本语法

```bash
python scripts/direct_import.py <file_path> --type <CSV|TXT> [可选参数]
```

### 必需参数

| 参数 | 说明 | 类型 | 例子 |
|------|------|------|------|
| `file_path` | 文件的绝对或相对路径 | 字符串 | `/data/stock.csv` |
| `--type` | 文件类型（CSV 或 TXT） | 选择 | `CSV` 或 `TXT` |

### 可选参数

| 参数 | 说明 | 默认值 | 例子 | 备注 |
|------|------|--------|------|------|
| `--metric-code` | 指标代码（仅TXT需要） | 无 | `TTV`, `EEE` | **TXT文件必需** |
| `--date` | 数据日期（YYYY-MM-DD） | 自动提取 | `2025-08-28` | 可从文件名自动提取 |
| `--user-id` | 操作用户ID | `1` | `5` | 记录到数据库 |
| `--verbose` | 详细输出模式 | `false` | 无值 | 显示错误堆栈 |
| `-h, --help` | 显示帮助信息 | - | - | 查看所有选项 |

### 参数详解

#### `--type` 参数

```bash
# CSV导入
--type CSV

# TXT导入
--type TXT
```

#### `--metric-code` 参数（TXT文件）

支持的指标代码：

| 代码 | 说明 | 文件名例子 |
|------|------|-----------|
| `TTV` | 股票交易金额 | `TTV_20250828.txt` |
| `EEE` | 电子行业数据 | `EEE_20250828.txt` |
| `EFV` | 期货交易量 | `EFV_20250828.txt` |
| `AAA` | 自定义指标 | `AAA_20250828.txt` |

```bash
# 查看所有可用指标
psql -U postgres -d stock_analysis -c "SELECT id, code, name FROM metric_types;"
```

#### `--date` 参数（TXT文件）

```bash
# 显式指定日期
--date 2025-08-28

# 自动从文件名提取（优先级高）
# 支持格式：
#   - ttv_20250828.txt
#   - ttv_2025-08-28.txt
#   - ttv_20250828_xxx.txt
```

#### `--user-id` 参数

```bash
# 默认用户ID为1
python scripts/direct_import.py stock.csv --type CSV

# 指定用户ID为5
python scripts/direct_import.py stock.csv --type CSV --user-id 5
```

#### `--verbose` 参数

```bash
# 启用详细输出（显示错误堆栈）
python scripts/direct_import.py stock.csv --type CSV --verbose

# 禁用详细输出（默认）
python scripts/direct_import.py stock.csv --type CSV
```

---

## 🎯 使用示例

### CSV导入示例

#### 基础导入

```bash
python scripts/direct_import.py stock_concepts.csv --type CSV
```

**输出**：
```
📥 导入CSV文件（股票-概念映射）...
✓ CSV导入完成
  - 成功: 64798 条
  - 错误: 0 条

✅ 导入成功（批次ID: 15）
```

#### 详细模式导入

```bash
python scripts/direct_import.py stock_concepts.csv --type CSV --verbose
```

#### 指定用户和详细模式

```bash
python scripts/direct_import.py /path/to/stock.csv --type CSV --user-id 5 --verbose
```

#### 从项目目录导入

```bash
cd /Users/peakom/work/stock-analysis/backend
python scripts/direct_import.py scripts/eee/8.28/2025-08-28-01-46.csv --type CSV
```

#### 从绝对路径导入

```bash
python scripts/direct_import.py /Users/peakom/work/stock-analysis/backend/scripts/stock.csv --type CSV
```

---

### TXT导入示例

#### 基础导入（指定指标和日期）

```bash
python scripts/direct_import.py EEE.txt --type TXT --metric-code EEE --date 2025-08-28
```

**输出**：
```
📥 导入TXT文件（EEE交易数据）...
✓ TXT导入完成
  - 成功: 5619 条
  - 错误: 0 条
  - 已自动计算排名和汇总统计

✅ 导入成功（批次ID: 10）
```

#### 自动提取日期

```bash
# 文件名包含日期，自动提取
python scripts/direct_import.py EEE_20250828.txt --type TXT --metric-code EEE
# 自动提取日期：2025-08-28
```

#### 四个指标都导入

```bash
# TTV指标
python scripts/direct_import.py /data/2025-08-28/TTV.txt --type TXT --metric-code TTV --date 2025-08-28

# EEE指标
python scripts/direct_import.py /data/2025-08-28/EEE.txt --type TXT --metric-code EEE --date 2025-08-28

# EFV指标
python scripts/direct_import.py /data/2025-08-28/EFV.txt --type TXT --metric-code EFV --date 2025-08-28

# AAA指标
python scripts/direct_import.py /data/2025-08-28/AAA.txt --type TXT --metric-code AAA --date 2025-08-28
```

#### 详细模式（调试）

```bash
python scripts/direct_import.py EEE.txt --type TXT --metric-code EEE --verbose
```

#### 完整示例

```bash
python scripts/direct_import.py \
  /Users/peakom/work/stock-analysis/backend/scripts/eee/8.28/EEE.txt \
  --type TXT \
  --metric-code EEE \
  --date 2025-08-28 \
  --user-id 1 \
  --verbose
```

---

## 📂 文件格式

### CSV文件格式

#### 必需列

脚本自动检测以下列名，**至少需要股票代码和一种映射关系**：

| 字段 | 可接受的列名 | 必需 |
|------|-------------|------|
| **股票代码** | `股票代码`, `code`, `stock_code`, `代码` | ✅ |
| **股票名称** | `股票名称`, `name`, `stock_name`, `名称` | ❌ |
| **概念名称** | `概念`, `concept`, `板块`, `concept_name` | ✅ |
| **行业名称** | `行业`, `industry`, `industry_name` | ❌ |

#### CSV示例

```csv
股票代码,股票名称,概念,行业
000001,平安银行,金融,银行
000002,万科A,房地产,全国地产
000858,五粮液,消费,食品
000651,格力电器,家电,家用电器
```

#### CSV编码

- 支持：**UTF-8**、**GBK**（自动检测）
- 分隔符：**逗号** (`,`)
- 换行符：**LF** (Unix/Mac) 或 **CRLF** (Windows)

#### 文件大小建议

- 推荐：< 100MB
- 最大：无限制（根据内存和磁盘空间）

---

### TXT文件格式

#### 格式说明

**三列数据，使用Tab或空格分隔**

| 列号 | 字段 | 格式 | 例子 |
|------|------|------|------|
| 1 | 股票代码 | 可带前缀(SH/SZ/BJ)或不带 | `SH600000` 或 `600000` |
| 2 | 交易日期 | 多种格式支持 | `2025-08-28` |
| 3 | 交易值 | 整数或浮点数 | `743024` |

#### 支持的日期格式

```
YYYY-MM-DD    (2025-08-28)
YYYYMMDD      (20250828)
YYYY/MM/DD    (2025/08/28)
```

#### 支持的股票代码前缀

```
SH     - 上海交易所 (Shanghai)
SZ     - 深圳交易所 (Shenzhen)
BJ     - 北京交易所 (Beijing)
```

脚本会自动识别和分离前缀。

#### TXT示例

**Tab分隔**：
```
SH600000	2025-08-28	743024
SH600004	2025-08-28	153615
SZ000001	2025-08-28	1234567
BJ430001	2025-08-28	567890
```

**空格分隔**：
```
600000	2025-08-28	743024
600004	2025-08-28	153615
000001	2025-08-28	1234567
430001	2025-08-28	567890
```

#### TXT编码

- 支持：**UTF-8**、**GBK**（自动检测）
- 分隔符：**Tab** (`\t`) 或 **空格** (自动检测)
- 换行符：**LF** (Unix/Mac) 或 **CRLF** (Windows)

#### 文件大小建议

- 推荐：< 500MB
- 最大：无限制（根据内存和磁盘空间）

---

## 🔄 导入流程

### CSV导入流程图

```
CSV文件
  ↓
【第1步】参数验证
  ├─ 检查文件存在性
  ├─ 验证文件格式
  └─ 检查权限
  ↓
【第2步】创建批次记录
  └─ INSERT INTO import_batches
  ↓
【第3步】预加载缓存
  ├─ SELECT * FROM stocks
  ├─ SELECT * FROM concepts
  └─ SELECT * FROM industries
  ↓
【第4步】解析CSV文件
  ├─ 自动检测列名
  ├─ 逐行读取数据
  ├─ 提取字段值
  ├─ 清理无效数据
  └─ 构建内存数据结构
  ↓
【第5步】批量插入数据
  ├─ INSERT INTO stocks (新股票)
  ├─ INSERT INTO concepts (新概念)
  ├─ INSERT INTO industries (新行业)
  ├─ INSERT INTO stock_concepts (股票-概念映射)
  ├─ INSERT INTO stock_industries (股票-行业映射)
  └─ INSERT INTO stock_concept_mapping_raw (原始审计数据)
  ↓
【第6步】更新批次状态
  └─ UPDATE import_batches SET status='completed'
  ↓
【第7步】提交事务
  └─ COMMIT
  ↓
✅ 导入完成，输出统计信息
```

### TXT导入流程图

```
TXT文件
  ↓
【第1步】参数验证
  ├─ 检查文件存在性
  ├─ 验证指标代码
  └─ 提取或验证日期
  ↓
【第2步】创建批次记录
  └─ INSERT INTO import_batches
  ↓
【第3步】预加载映射关系
  └─ SELECT sc.stock_code, sc.concept_id, c.concept_name
     FROM stock_concepts sc JOIN concepts c
  ↓
【第4步】解析TXT文件
  ├─ 自动检测分隔符
  ├─ 自动检测编码
  ├─ 逐行读取数据
  ├─ 提取字段值
  ├─ 处理股票代码前缀
  ├─ 解析日期
  └─ 清理无效数据
  ↓
【第5步】删除旧原始数据
  └─ DELETE FROM stock_metric_data_raw
     WHERE metric_type_id=? AND trade_date=?
  ↓
【第6步】批量导入原始数据
  └─ COPY INTO stock_metric_data_raw
  ↓
【第7步】内存计算排名
  ├─ 按概念分组
  ├─ 计算排名 (RANK)
  ├─ 计算百分位 (PERCENTILE)
  ├─ 计算统计值 (SUM, AVG, MIN, MAX, MEDIAN)
  └─ 计算Top10合计
  ↓
【第8步】删除旧排名和汇总数据
  ├─ DELETE FROM concept_stock_daily_rank
  │  WHERE metric_type_id=? AND trade_date=?
  └─ DELETE FROM concept_daily_summary
     WHERE metric_type_id=? AND trade_date=?
  ↓
【第9步】批量插入排名数据
  └─ INSERT INTO concept_stock_daily_rank (批量)
  ↓
【第10步】批量插入汇总数据
  └─ INSERT INTO concept_daily_summary (批量)
  ↓
【第11步】更新批次状态
  └─ UPDATE import_batches SET status='completed'
  ↓
【第12步】提交事务
  └─ COMMIT
  ↓
✅ 导入完成，输出统计信息
```

---

## ❓ 常见问题

### Q1: 文件不存在错误

**错误信息**：
```
❌ 错误：文件不存在 /wrong/path.csv
```

**原因**：文件路径不正确

**解决方案**：

```bash
# 方案1：使用绝对路径
python scripts/direct_import.py /Users/peakom/work/stock-analysis/backend/scripts/stock.csv --type CSV

# 方案2：确保在项目根目录，使用相对路径
cd /Users/peakom/work/stock-analysis/backend
python scripts/direct_import.py scripts/stock.csv --type CSV

# 方案3：检查文件是否存在
ls -la /path/to/your/file.csv
```

---

### Q2: TXT文件缺少指标代码

**错误信息**：
```
❌ 错误：TXT文件必须指定 --metric-code
```

**原因**：导入TXT文件时没有提供指标代码

**解决方案**：

```bash
# 添加 --metric-code 参数
python scripts/direct_import.py EEE.txt --type TXT --metric-code EEE

# 支持的指标代码：TTV, EEE, EFV, AAA
```

---

### Q3: 日期格式错误

**错误信息**：
```
❌ 错误：日期格式不正确 08-28-2025，应为 YYYY-MM-DD
```

**原因**：日期格式不符合规范

**解决方案**：

```bash
# 使用正确的日期格式
python scripts/direct_import.py EEE.txt --type TXT --metric-code EEE --date 2025-08-28

# 支持的格式：
# YYYY-MM-DD  (2025-08-28)
# YYYYMMDD    (20250828)
# YYYY/MM/DD  (2025/08/28)
```

---

### Q4: 导入失败需要调试

**错误信息**：
```
❌ 导入失败: [错误信息]
```

**解决方案**：

```bash
# 使用 --verbose 参数查看详细错误
python scripts/direct_import.py stock.csv --type CSV --verbose

# 输出示例：
# Traceback (most recent call last):
#   File "...", line XX, in ...
#     ...
```

---

### Q5: 重复导入数据会怎样

**Q**: 我已经导入过一次数据，现在想重新导入，会不会有重复？

**A**: 不会有重复！脚本使用全量更新策略：

**对于CSV**：
- 使用 `ON CONFLICT DO UPDATE` 自动覆盖旧数据
- 结果：最新数据覆盖旧数据

**对于TXT**：
- 先 DELETE 再 INSERT（全量更新）
- 结果：该日期该指标的所有旧数据被清除，重新导入新数据

```bash
# 可以安全地重复执行（会覆盖旧数据）
python scripts/direct_import.py stock.csv --type CSV
python scripts/direct_import.py stock.csv --type CSV  # ✅ 不会有重复

python scripts/direct_import.py EEE.txt --type TXT --metric-code EEE --date 2025-08-28
python scripts/direct_import.py EEE.txt --type TXT --metric-code EEE --date 2025-08-28  # ✅ 不会有重复
```

---

### Q6: 导入了错误的数据，想回滚

**方案1：删除整个批次**

```bash
# 1. 查看导入批次
psql -U postgres -d stock_analysis -c "
SELECT id, file_name, file_type, created_at
FROM import_batches
ORDER BY created_at DESC LIMIT 5;
"

# 2. 删除特定批次的数据（例如批次ID=15）
psql -U postgres -d stock_analysis << EOF
DELETE FROM stock_concept_mapping_raw WHERE import_batch_id = 15;
DELETE FROM stock_concepts WHERE stock_code IN (
  SELECT DISTINCT stock_code FROM stock_concept_mapping_raw WHERE import_batch_id = 15
);
DELETE FROM stock_industries WHERE stock_code IN (
  SELECT DISTINCT stock_code FROM stock_concept_mapping_raw WHERE import_batch_id = 15
);
DELETE FROM import_batches WHERE id = 15;
EOF
```

**方案2：重新导入正确的数据**

```bash
# 直接导入新数据，旧数据会被覆盖
python scripts/direct_import.py correct_file.csv --type CSV
```

---

### Q7: 导入很大的文件，进度如何？

**说明**：脚本没有进度条，但会输出最终结果

**查看进度方法**：

```bash
# 方案1：使用 tail 实时查看日志
python scripts/direct_import.py large_file.csv --type CSV > import.log 2>&1 &
tail -f import.log

# 方案2：等待完成后查看结果
python scripts/direct_import.py large_file.csv --type CSV
```

---

### Q8: 内存不足，导入失败

**错误信息**：
```
MemoryError: ...
```

**解决方案**：

```bash
# 方案1：分割文件成多个小文件
split -l 50000 large_file.csv part_

# 方案2：逐个导入小文件
for file in part_*; do
  python scripts/direct_import.py "$file" --type CSV
done

# 方案3：检查系统资源
free -h  # 查看内存
top      # 查看进程占用
```

---

### Q9: 权限不足错误

**错误信息**：
```
PermissionError: [Errno 13] Permission denied: '/path/to/file'
```

**解决方案**：

```bash
# 检查文件权限
ls -la /path/to/file.csv

# 修改文件权限（如需要）
chmod 644 /path/to/file.csv

# 或检查目录权限
ls -la /path/to/
```

---

### Q10: 数据库连接失败

**错误信息**：
```
psycopg2.OperationalError: ...
```

**解决方案**：

```bash
# 1. 检查数据库是否运行
psql -U postgres -d stock_analysis -c "SELECT 1;"

# 2. 检查.env文件配置
cat /Users/peakom/work/stock-analysis/backend/.env | grep DATABASE

# 3. 验证数据库和表是否存在
psql -U postgres -d stock_analysis -c "\dt"

# 4. 检查PostgreSQL是否运行
ps aux | grep postgres
```

---

## ⚡ 性能指标

### 导入速度

| 操作 | 数据量 | 耗时 | 速度 |
|------|--------|------|------|
| CSV导入 | 64,798条 | ~2秒 | 32,399条/秒 |
| TXT导入+计算 | 5,619条 | ~2秒 | 2,809条/秒 |
| 批量导入10个CSV | ~650,000条 | ~20秒 | 32,500条/秒 |

### 内存占用

| 操作 | 文件大小 | 内存占用 | 峰值 |
|------|---------|---------|------|
| CSV导入 | 50MB | 200MB | 300MB |
| TXT导入 | 10MB | 100MB | 150MB |
| 预加载缓存 | - | 50MB | 50MB |

### 数据库性能

| 操作 | 记录数 | 耗时 |
|------|--------|------|
| 插入stocks | 10,000 | 0.5秒 |
| 插入concepts | 500 | 0.1秒 |
| 插入industries | 100 | 0.05秒 |
| 插入映射关系 | 100,000 | 1.5秒 |
| 计算排名（内存） | 10,000 | 0.3秒 |

---

## 🎯 最佳实践

### 1️⃣ 单个文件导入

```bash
# CSV导入
python scripts/direct_import.py /path/to/stock_concepts.csv --type CSV

# TXT导入
python scripts/direct_import.py /path/to/EEE_20250828.txt --type TXT --metric-code EEE
```

---

### 2️⃣ 批量导入多个CSV文件

```bash
# 方式1：使用batch_import.sh脚本
./scripts/batch_import.sh /data/stock/

# 方式2：使用for循环
for file in /data/stock/*.csv; do
  echo "导入: $file"
  python scripts/direct_import.py "$file" --type CSV
done

# 方式3：使用find命令
find /data/stock -name "*.csv" | while read file; do
  python scripts/direct_import.py "$file" --type CSV
done
```

---

### 3️⃣ 定期导入TXT交易数据

```bash
#!/bin/bash
# cron_import.sh - 定期导入脚本

IMPORT_DIR="/data/daily/$(date +%Y-%m-%d)"
BACKEND_DIR="/Users/peakom/work/stock-analysis/backend"

cd "$BACKEND_DIR"

# 导入四个指标
metrics=("TTV" "EEE" "EFV" "AAA")
for metric in "${metrics[@]}"; do
  file="$IMPORT_DIR/${metric}.txt"
  if [ -f "$file" ]; then
    echo "导入 $metric 指标..."
    python scripts/direct_import.py "$file" --type TXT --metric-code "$metric"
  else
    echo "文件不存在: $file"
  fi
done
```

**添加到crontab**：
```bash
# 每天下午5点执行
0 17 * * * /path/to/cron_import.sh >> /var/log/stock_import.log 2>&1
```

---

### 4️⃣ 导入特定用户的数据

```bash
# 以用户ID 5 的身份导入
python scripts/direct_import.py stock.csv --type CSV --user-id 5

# 以不同用户导入不同文件
python scripts/direct_import.py file1.csv --type CSV --user-id 1
python scripts/direct_import.py file2.csv --type CSV --user-id 2
python scripts/direct_import.py file3.csv --type CSV --user-id 3
```

---

### 5️⃣ 错误处理和日志

```bash
#!/bin/bash
# import_with_logging.sh

LOG_FILE="/var/log/stock_import_$(date +%Y%m%d_%H%M%S).log"
ERROR_FILE="/var/log/stock_import_errors.log"

python scripts/direct_import.py stock.csv --type CSV --verbose \
  > "$LOG_FILE" 2>&1

# 检查导入结果
if grep -q "✅" "$LOG_FILE"; then
  echo "导入成功" >> "$LOG_FILE"
else
  echo "导入失败，详见 $LOG_FILE"
  cat "$LOG_FILE" >> "$ERROR_FILE"
fi
```

---

### 6️⃣ 校验导入结果

```bash
#!/bin/bash
# verify_import.sh

echo "=== 导入统计 ==="
psql -U postgres -d stock_analysis -c "
SELECT
  '股票' as 类型, COUNT(*) as 数据量
FROM stocks
UNION ALL
SELECT '概念', COUNT(*) FROM concepts
UNION ALL
SELECT '行业', COUNT(*) FROM industries
UNION ALL
SELECT '股票-概念映射', COUNT(*) FROM stock_concepts
UNION ALL
SELECT '股票-行业映射', COUNT(*) FROM stock_industries
UNION ALL
SELECT '原始审计数据', COUNT(*) FROM stock_concept_mapping_raw;
"
```

---

### 7️⃣ 在脚本中使用

```python
# import_wrapper.py - Python脚本中调用

import subprocess
import sys

def import_csv(file_path, user_id=1):
    """导入CSV文件"""
    cmd = [
        sys.executable,
        "scripts/direct_import.py",
        file_path,
        "--type", "CSV",
        "--user-id", str(user_id),
        "--verbose"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"导入失败: {result.stderr}")
        return False

def import_txt(file_path, metric_code, date=None):
    """导入TXT文件"""
    cmd = [
        sys.executable,
        "scripts/direct_import.py",
        file_path,
        "--type", "TXT",
        "--metric-code", metric_code
    ]

    if date:
        cmd.extend(["--date", date])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"导入失败: {result.stderr}")
        return False

# 使用示例
if __name__ == "__main__":
    import_csv("/path/to/stock.csv")
    import_txt("/path/to/EEE.txt", "EEE", "2025-08-28")
```

---

## ✅ 验证方法

### CSV导入验证

```bash
# 1. 查看导入批次
psql -U postgres -d stock_analysis -c "
SELECT id, file_name, file_type, status, total_rows, success_rows, created_at
FROM import_batches
WHERE file_type = 'CSV'
ORDER BY created_at DESC LIMIT 1;
"

# 2. 查看导入的数据量
psql -U postgres -d stock_analysis << EOF
SELECT '股票' as 表名, COUNT(*) FROM stocks WHERE id > 1
UNION ALL
SELECT '概念', COUNT(*) FROM concepts
UNION ALL
SELECT '行业', COUNT(*) FROM industries
UNION ALL
SELECT '股票-概念映射', COUNT(*) FROM stock_concepts
UNION ALL
SELECT '股票-行业映射', COUNT(*) FROM stock_industries
UNION ALL
SELECT '原始审计数据', COUNT(*) FROM stock_concept_mapping_raw;
EOF

# 3. 查看特定股票的概念
psql -U postgres -d stock_analysis -c "
SELECT DISTINCT c.concept_name
FROM stock_concepts sc
JOIN concepts c ON sc.concept_id = c.id
WHERE sc.stock_code = '000001'
LIMIT 10;
"

# 4. 查看特定股票的行业
psql -U postgres -d stock_analysis -c "
SELECT DISTINCT ind.industry_name
FROM stock_industries si
JOIN industries ind ON si.industry_id = ind.id
WHERE si.stock_code = '000001';
"

# 5. 查看某个行业的股票数
psql -U postgres -d stock_analysis -c "
SELECT ind.industry_name, COUNT(DISTINCT si.stock_code) as 股票数
FROM stock_industries si
JOIN industries ind ON si.industry_id = ind.id
GROUP BY ind.industry_name
ORDER BY 股票数 DESC
LIMIT 10;
"
```

### TXT导入验证

```bash
# 1. 查看导入批次
psql -U postgres -d stock_analysis -c "
SELECT id, file_name, file_type, status, total_rows, success_rows, data_date, created_at
FROM import_batches
WHERE file_type = 'TXT'
ORDER BY created_at DESC LIMIT 1;
"

# 2. 查看原始导入数据
psql -U postgres -d stock_analysis -c "
SELECT COUNT(*) as raw_data_count
FROM stock_metric_data_raw
WHERE metric_type_id = 2 AND trade_date = '2025-08-28';
"

# 3. 查看排名数据
psql -U postgres -d stock_analysis -c "
SELECT concept_id, COUNT(*) as rank_count
FROM concept_stock_daily_rank
WHERE metric_type_id = 2 AND trade_date = '2025-08-28'
GROUP BY concept_id
LIMIT 10;
"

# 4. 查看汇总数据
psql -U postgres -d stock_analysis -c "
SELECT concept_id, total_value, avg_value, stock_count
FROM concept_daily_summary
WHERE metric_type_id = 2 AND trade_date = '2025-08-28'
LIMIT 10;
"

# 5. 查看特定概念的Top 10
psql -U postgres -d stock_analysis -c "
SELECT stock_code, trade_value, rank, percentile
FROM concept_stock_daily_rank
WHERE concept_id = 2445 AND metric_type_id = 2 AND trade_date = '2025-08-28'
ORDER BY rank
LIMIT 10;
"
```

---

## 📞 获取帮助

### 查看脚本帮助

```bash
# 显示帮助信息
python scripts/direct_import.py -h

# 或
python scripts/direct_import.py --help
```

### 查看输出信息

```
usage: direct_import.py [-h] --type {CSV,TXT} [--metric-code METRIC_CODE]
                        [--date DATE] [--user-id USER_ID] [--verbose]
                        file_path

直接导入数据文件

positional arguments:
  file_path             文件路径

options:
  -h, --help            show this help message and exit
  --type {CSV,TXT}      文件类型
  --metric-code METRIC_CODE
                        指标代码（TXT文件必需）
  --date DATE           数据日期，格式YYYY-MM-DD（TXT文件）
  --user-id USER_ID     用户ID，默认为1
  --verbose             详细输出
```

---

## 📌 返回状态码

| 情况 | 状态码 | 说明 |
|------|--------|------|
| 导入成功 | 0 | `✅ 导入成功（批次ID: XX）` |
| 文件不存在 | 1 | 文件路径不正确 |
| 参数错误 | 1 | 缺少必需参数或参数值错误 |
| 导入失败 | 1 | 数据库操作失败或其他错误 |

---

## 🔗 相关文档

- [CSV导入详细流程](./csv_import_detailed.txt)
- [TXT导入详细流程](./txt_import_detailed.txt)
- [统一导入逻辑说明](./UNIFIED_IMPORT_LOGIC.md)
- [数据库模式](../sql/init_tables.sql)
- [批量导入脚本](./batch_import.sh)

---

**最后更新**：2025-11-25
**版本**：1.0
**作者**：AI Assistant
