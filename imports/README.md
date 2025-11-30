# 📥 导入工具集 (Import Tools)

欢迎来到股票分析系统的导入工具目录。本目录统一管理所有数据导入脚本和使用文档，方便快速查阅和使用。

## 📁 脚本概览

本目录包含三个数据导入脚本，适用于不同的导入场景：

| 脚本 | 用途 | 适用场景 |
|------|------|---------|
| **direct_import.py** | 单文件直接导入 | 导入单个CSV或TXT文件 |
| **batch_import.py** | 混合日期批量导入 | 一个文件包含多个日期的数据 |
| **folder_import.py** | 文件夹批量导入 ⭐ | 文件夹下有多个单日期TXT文件 |

---

## 🚀 快速开始

### 1️⃣ direct_import.py - 单文件直接导入

#### CSV文件导入
```bash
# 导入股票概念关系数据
python imports/direct_import.py test-data/concept_stock.csv --type CSV
```

#### TXT文件导入
```bash
# 自动提取日期
python imports/direct_import.py test-data/EEE_2025-11-18.txt \
  --type TXT \
  --metric-code EEE

# 手动指定日期
python imports/direct_import.py test-data/TTV_2025-11-25.txt \
  --type TXT \
  --metric-code TTV \
  --date 2025-11-25
```

**参数说明**:
- `file_path` **(必需)** - 文件路径
- `--type` **(必需)** - 文件类型：`CSV` 或 `TXT`
- `--metric-code` **(TXT必需)** - 指标代码
- `--date` **(可选)** - 数据日期，不指定则自动提取
- `--user-id` **(可选)** - 用户ID，默认为1
- `--verbose` **(可选)** - 显示详细输出

---

### 2️⃣ batch_import.py - 混合日期批量导入

用于处理**一个文件包含多个日期**的情况，自动拆分并并行导入。

```bash
# 基础导入（默认4个并行进程）
python imports/batch_import.py test-data/EEE_mixed_dates.txt \
  --type TXT \
  --metric-code EEE

# 自定义并行进程数
python imports/batch_import.py test-data/TTV_mixed_dates.txt \
  --type TXT \
  --metric-code TTV \
  --parallel 8

# 只处理特定日期范围
python imports/batch_import.py test-data/EEE_mixed_dates.txt \
  --type TXT \
  --metric-code EEE \
  --start-date 2025-11-19 \
  --end-date 2025-11-21

# 从上次中断处继续
python imports/batch_import.py test-data/EEE_mixed_dates.txt \
  --type TXT \
  --metric-code EEE \
  --resume
```

**参数说明**:
- `file` **(必需)** - 文件路径
- `--type` **(必需)** - 文件类型，目前仅支持 `TXT`
- `--metric-code` **(必需)** - 指标代码
- `--parallel` **(可选)** - 并行进程数，默认4
- `--resume` **(可选)** - 从上次中断处继续
- `--start-date` **(可选)** - 开始日期 `YYYY-MM-DD`
- `--end-date` **(可选)** - 结束日期 `YYYY-MM-DD`

---

### 3️⃣ folder_import.py - 文件夹批量导入 ⭐ 新增

用于批量导入文件夹下的所有TXT文件，自动识别指标和日期。

#### 支持的文件名格式
```
EEE_2025-11-18.txt      # METRIC_YYYY-MM-DD.txt
TTV_20251125.txt        # METRIC_YYYYMMDD.txt
EEE_2025_11_18.txt      # METRIC_YYYY_MM_DD.txt
```

#### 基本用法

```bash
# 导入文件夹下所有TXT文件
python imports/folder_import.py test-data

# 只导入EEE指标
python imports/folder_import.py test-data --metric-code EEE

# 只导入特定日期范围
python imports/folder_import.py test-data \
  --start-date 2025-11-18 \
  --end-date 2025-11-21

# 并行处理（4个进程）
python imports/folder_import.py test-data --parallel 4

# 跳过已导入的文件
python imports/folder_import.py test-data --skip-existing

# 组合使用
python imports/folder_import.py test-data \
  --metric-code EEE \
  --start-date 2025-11-18 \
  --end-date 2025-11-21 \
  --parallel 4 \
  --skip-existing
```

**参数说明**:
- `folder` **(必需)** - 文件夹路径
- `--metric-code` **(可选)** - 只导入指定指标
- `--start-date` **(可选)** - 开始日期 `YYYY-MM-DD`
- `--end-date` **(可选)** - 结束日期 `YYYY-MM-DD`
- `--parallel` **(可选)** - 并行进程数，默认1
- `--skip-existing` **(可选)** - 跳过已成功导入的文件

---

## 🎯 使用场景推荐

### 场景1: 每日导入单个文件
```bash
# 使用 direct_import.py
python imports/direct_import.py /path/to/EEE_2025-11-30.txt \
  --type TXT --metric-code EEE
```

### 场景2: 补充历史数据（一个大文件包含多个日期）
```bash
# 使用 batch_import.py
python imports/batch_import.py /path/to/EEE_history.txt \
  --type TXT \
  --metric-code EEE \
  --parallel 8
```

### 场景3: 批量导入历史数据（文件夹包含多个单日期文件）
```bash
# 使用 folder_import.py
python imports/folder_import.py /path/to/data_folder \
  --parallel 4 \
  --skip-existing
```

### 场景4: 只导入特定时间范围的数据
```bash
# 使用 folder_import.py
python imports/folder_import.py /path/to/data_folder \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --parallel 8
```

### 场景5: 重新导入某个指标的所有数据
```bash
# 使用 folder_import.py
python imports/folder_import.py /path/to/data_folder \
  --metric-code EEE \
  --parallel 8
```

---

## ⚙️ 统一导入逻辑

所有脚本都调用相同的底层导入方法（`ImportService.import_txt_file()` 和 `ImportService.import_csv_file()`），确保：

1. ✅ **数据一致性** - 使用相同的验证和处理逻辑
2. 🔒 **数据库锁** - 防止并发导入冲突
3. 🗑️ **自动删除旧数据** - 相同指标+日期的数据会被新数据替换
4. 📊 **自动计算排名和汇总** - 导入后自动计算股票排名和概念汇总

### 导入流程
```
1. 创建导入批次记录
   ↓
2. 更新状态为 processing
   ↓
3. 🔒 获取数据库锁（防止并发）
   ↓
4. 删除旧数据（相同指标+日期）
   ↓
5. 导入新数据
   ↓
6. 计算排名和汇总
   ↓
7. 更新状态为 completed
   ↓
8. 释放锁
```

---

## 📊 性能对比

| 脚本 | 单个文件 | 10个文件 | 并行优势 |
|------|---------|---------|---------|
| direct_import.py | 0.5秒 | 5秒 | - |
| folder_import.py (--parallel 1) | 0.5秒 | 5秒 | - |
| folder_import.py (--parallel 4) | 0.5秒 | 1.5秒 | **3.3倍提升** |
| batch_import.py (--parallel 4) | - | - | 按日期并行 |

---

## 🔧 常见问题

### Q1: 如何查看已导入的批次？
访问管理后台 → 数据导入页面，可以查看所有导入批次的状态。

### Q2: 导入失败如何处理？
- 查看错误信息定位问题
- 修复后重新导入（会自动覆盖旧数据）
- 使用 `--verbose` 参数查看详细日志

### Q3: 如何提高导入速度？
- 使用 `--parallel` 参数增加并行进程数
- 推荐设置为 CPU 核心数的 1-2 倍
- 例如：8 核 CPU 可以设置 `--parallel 8`

### Q4: 可以同时导入多个指标吗？
- `batch_import.py` 和 `direct_import.py` 只能处理单个指标
- `folder_import.py` 可以同时导入多个指标（不需要指定 `--metric-code`）

### Q5: 导入会删除原有数据吗？
是的，导入时会删除**相同指标+相同日期**的旧数据，然后导入新数据。这样确保数据不会重复。

### Q6: 支持哪些指标类型？
- 系统预定义：`EEE`（游资净买额）、`TTV`（总成交额）
- 也可以导入自定义指标，系统会自动创建新的指标类型

### Q7: 三个脚本有什么区别？
- `direct_import.py` - 最简单，适合单个文件，支持CSV和TXT
- `batch_import.py` - 处理混合日期文件，按日期拆分后并行导入
- `folder_import.py` - 扫描整个文件夹，自动识别并批量导入

---

## 📝 注意事项

1. **虚拟环境** - 运行前需要激活虚拟环境：`source backend/venv/bin/activate`
2. **数据库** - 确保数据库服务正常运行
3. **文件编码** - 支持 UTF-8、GBK、GB2312 编码
4. **文件格式** - TXT文件必须是 TSV 格式（制表符分隔）
5. **并发限制** - 数据库锁会自动防止同一指标的并发导入
6. **临时文件** - `batch_import.py` 会在 `/tmp` 下创建临时文件，完成后自动清理

---

## 💡 最佳实践

1. **大文件优先使用批量导入**: 文件 > 100M 时使用 `batch_import.py`
2. **文件夹导入使用 folder_import.py**: 多个单日期文件用 `folder_import.py` 更方便
3. **合理设置并行度**: CPU 核心数 × 1.5 ~ 2
4. **使用 --skip-existing**: 避免重复导入已成功的文件
5. **监控导入进度**: 观察 tqdm 进度条实时了解状态
6. **验证数据完整性**: 导入完成后检查批次记录

---

## 📖 详细文档

查看目录下的其他文档文件获取更多详细信息：
- `01_IMPORT_OVERVIEW.md` - 导入系统概览
- `02_DIRECT_IMPORT.md` - 直接导入使用指南
- `03_BATCH_IMPORT.md` - 批量导入快速参考
- `04_BATCH_IMPORT_COMPLETE.md` - 批量导入完整指南

---

**最后更新**: 2025-11-30
**版本**: v3.0
**状态**: ✅ 完成（新增 folder_import.py）
