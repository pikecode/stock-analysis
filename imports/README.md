# 📥 导入工具集 (Import Tools)

欢迎来到股票分析系统的导入工具目录。本目录统一管理所有数据导入脚本和使用文档，方便快速查阅和使用。

## 📁 目录内容

本目录包含以下内容：

### 脚本文件 (Python Scripts)

| 脚本文件 | 用途 | 适用场景 |
|---------|------|---------|
| **direct_import.py** | 单文件直接导入 | CSV/TXT 文件快速导入 |
| **batch_import.py** | 批量导入（自动分组+并行处理） | 大文件（>100M）、多日期混合数据 |

### 文档文件 (Documentation)

| 文档 | 内容 | 推荐阅读对象 |
|------|------|-----------|
| **01_IMPORT_OVERVIEW.md** | 导入系统概览 | 首次了解导入系统的用户 |
| **02_DIRECT_IMPORT.md** | 直接导入使用指南 | 需要导入单个文件的用户 |
| **03_BATCH_IMPORT.md** | 批量导入快速参考 | 需要快速查阅批量导入命令 |
| **04_BATCH_IMPORT_COMPLETE.md** | 批量导入完整指南 | 需要深入了解批量导入的用户 |

---

## 🚀 快速开始

### 1. CSV 导入（股票-概念映射）

```bash
python imports/direct_import.py /path/to/stock_concept.csv --type CSV
```

### 2. TXT 导入（交易数据 - 单文件）

```bash
python imports/direct_import.py /path/to/trading_data.txt --type TXT --metric-code EEE
```

### 3. TXT 批量导入（交易数据 - 大文件）

```bash
python imports/batch_import.py /path/to/large_file.txt --metric-code EEE --parallel 8
```

### 4. 批量导入 - 继续中断的任务

```bash
python imports/batch_import.py /path/to/large_file.txt --metric-code EEE --parallel 8 --resume
```

---

## 📖 文档导航

根据你的需求选择相应的文档：

### 第一次使用？
➡️ 从 **01_IMPORT_OVERVIEW.md** 开始了解导入系统的架构

### 需要导入单个文件？
➡️ 查看 **02_DIRECT_IMPORT.md** 了解直接导入的用法

### 需要导入大文件？
➡️ 查看 **03_BATCH_IMPORT.md** 快速上手，或 **04_BATCH_IMPORT_COMPLETE.md** 深入学习

---

## 🎯 使用场景对应表

| 场景 | 文件大小 | 日期范围 | 推荐方案 | 命令 |
|------|---------|---------|---------|------|
| 导入 CSV 映射 | <10M | - | 直接导入 | `direct_import.py ... --type CSV` |
| 导入单日 TXT | <100M | 1 天 | 直接导入 | `direct_import.py ... --type TXT` |
| 导入大文件 | >100M | 多天 | 批量导入 | `batch_import.py ... --parallel 8` |
| 继续中断导入 | >100M | 多天 | 批量导入 | `batch_import.py ... --resume` |

---

## 🔧 系统要求

- **Python**: 3.8+
- **数据库**: PostgreSQL 12+
- **依赖包**: 见 `backend/requirements.txt`

---

## 💡 常见问题

### Q: 怎样选择直接导入还是批量导入？

**A:**
- 文件 < 100M：使用 `direct_import.py`
- 文件 > 100M 或包含多个日期：使用 `batch_import.py`

### Q: 批量导入失败后如何恢复？

**A:** 使用 `--resume` 标志从中断处继续：
```bash
python imports/batch_import.py /path/to/file.txt --metric-code EEE --resume
```

### Q: 如何查看导入进度？

**A:** 批量导入会显示进度条，或使用 shell 命令查看：
```bash
source quick_commands.sh
check_progress EEE
```

### Q: 导入数据后如何验证？

**A:** 查看导入统计：
```bash
source quick_commands.sh
import_stats
```

### Q: 如何指定导入日期？

**A:** 对于 TXT 文件，系统会自动从文件内容提取日期，也可显式指定：
```bash
python imports/direct_import.py file.txt --type TXT --metric-code EEE --date 2024-11-25
```

---

## 📊 性能指标

基于实际测试的性能数据：

| 指标 | 直接导入 | 批量导入 (--parallel 8) |
|------|---------|----------------------|
| 100M 文件 | ~2-3 分钟 | ~30 秒 |
| 500M 文件 | ~10-15 分钟 | ~2 分钟 |
| 内存占用 | ~200MB | ~500MB |

---

## 🛠️ 集成方式

### 通过 Shell 快速命令

项目根目录提供了 `quick_commands.sh` 脚本，封装了常用命令：

```bash
# 加载快速命令
source quick_commands.sh

# 使用快速命令
import_csv data.csv
import_txt data.txt EEE
batch_import large.txt EEE 8
resume_import large.txt EEE 8
```

### 直接调用 Python 脚本

```bash
# 直接导入
python /Users/peakom/work/stock-analysis/imports/direct_import.py file.csv --type CSV

# 批量导入
python /Users/peakom/work/stock-analysis/imports/batch_import.py file.txt --metric-code EEE --parallel 8
```

---

## 📝 输出和日志

### 标准输出示例

```
📥 导入CSV文件（股票-概念映射）...
✓ CSV导入完成
  - 成功: 1500 条
  - 错误: 0 条

✅ 导入成功（批次ID: 123）
```

### 进度文件

批量导入会在 `/tmp/batch_import_{metric_code}.json` 生成进度文件，包含：
- 已处理日期数
- 成功/失败统计
- 当前处理进度

---

## ✅ 最佳实践

1. **大文件优先使用批量导入**: 文件 > 100M 时使用 `batch_import.py`，获得 6-8 倍的性能提升

2. **监控导入进度**: 批量导入过程中会显示 tqdm 进度条，实时了解导入状态

3. **验证数据完整性**: 导入完成后，使用 `import_stats` 命令查看导入统计

4. **合理设置并行度**:
   - CPU 密集任务：`--parallel = CPU 核心数`
   - 数据库连接有限：`--parallel = 4-8`

5. **保留重要数据**: 导入前确保已备份原始数据文件

6. **及时清理进度文件**: 导入完成后可删除 `/tmp/batch_import_*.json` 文件

---

## 🔍 故障排查

### 导入失败：ModuleNotFoundError

**原因**: 脚本找不到 `app` 模块

**解决**: 确保在项目根目录运行脚本：
```bash
cd /Users/peakom/work/stock-analysis
python imports/direct_import.py ...
```

### 导入失败：数据库连接错误

**原因**: 数据库未启动或连接信息错误

**解决**: 检查 `.env` 文件中的 `DATABASE_URL` 配置

### 导入超时

**原因**: 文件太大或并行度设置过高

**解决**:
- 降低 `--parallel` 值
- 使用 `--resume` 从中断处继续

---

## 📚 扩展阅读

详细的导入系统架构说明，请查看：
- **完整指南**: `04_BATCH_IMPORT_COMPLETE.md` - 30+ 章节详解
- **快速参考**: `03_BATCH_IMPORT.md` - 快速查阅命令
- **系统概览**: `01_IMPORT_OVERVIEW.md` - 整体架构说明

---

## 📞 支持

如遇到问题：

1. 查看相应的文档文件
2. 运行 `python imports/direct_import.py --help` 查看帮助
3. 检查 `/tmp/batch_import_*.json` 的进度文件
4. 使用 `--verbose` 标志获取详细输出

---

**最后更新**: 2024-11-25
**版本**: v2.0
**状态**: ✅ 完成

