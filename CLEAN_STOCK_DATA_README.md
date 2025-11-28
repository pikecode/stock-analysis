# 股票数据清理脚本使用指南

## 概述

本脚本用于快速清空数据库中的所有股票相关数据，保留表结构，便于重新进行导入测试。

## 包含的脚本文件

根目录中：
- `clean_stock_data.sql` - SQL 清理脚本
- `clean_stock_data.sh` - Bash 包装脚本（推荐使用）
- `CLEAN_STOCK_DATA_README.md` - 本文件

## 清理范围

本脚本会清空以下表中的所有数据：

### 分析结果表
- `concept_stock_daily_rank` - 排名数据（分区表）
- `concept_daily_summary` - 汇总数据

### 原始导入数据表
- `stock_metric_data_raw` - 指标数据（分区表）
- `stock_concept_mapping_raw` - CSV 原始导入数据
- `import_batches` - 导入批次记录

### 关系映射表
- `stock_concepts` - 股票-概念关系
- `stock_industries` - 股票行业关系

### 主数据表
- `stocks` - 股票主数据
- `concepts` - 概念分类
- `industries` - 行业分类

**总共：10 个表**

## 使用方法

### 方法 1: 使用 Bash 脚本（推荐）

最简单的方法，包含确认提示：

```bash
cd /Users/peak/work/pikecode/stock-analysis
./clean_stock_data.sh
```

脚本会：
1. 显示配置信息
2. 要求用户确认（防止误操作）
3. 执行 SQL 清理脚本
4. 显示验证结果

### 方法 2: 直接使用 SQL 脚本

如果需要跳过确认提示：

```bash
psql -U peak -d stock_analysis -f clean_stock_data.sql
```

### 方法 3: 自定义用户和数据库名

如果使用不同的用户名或数据库名：

```bash
# 使用环境变量指定
DB_USER=your_user DB_NAME=your_db_name ./clean_stock_data.sh

# 或直接使用 psql
psql -U your_user -d your_db_name -f clean_stock_data.sql
```

## 清理过程

脚本按照外键依赖关系进行清理，顺序如下：

```
1. 删除排名数据和汇总数据
   ↓
2. 删除原始指标数据和导入记录
   ↓
3. 删除关系映射表
   ↓
4. 删除主数据表
   ↓
5. 验证所有表都已清空
```

## 验证结果

脚本执行完毕后会显示验证结果，格式如下：

```
项目                              | 记录数
----------------------------------+-------
汇总数据表 (concept_daily_summary) |    0
排名数据表 (concept_stock_daily_rank) |  0
概念表 (concepts)                 |    0
导入批次表 (import_batches)        |    0
行业表 (industries)               |    0
... (其他表) ...                  |    0
```

所有记录数都应为 0。

## 使用场景

### 场景 1: 测试导入逻辑

清空数据后导入新的测试数据：

```bash
# 1. 清空数据
./clean_stock_data.sh

# 2. 启动前端和后端
# 终端 1:
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 终端 2:
cd frontend
npm run dev

# 3. 导入测试数据
# 浏览器打开: http://127.0.0.1:5173/admin/import
# 按照 test-data/QUICK_START.md 操作
```

### 场景 2: 完整功能测试

多次重复测试导入流程：

```bash
# 第一轮测试
./clean_stock_data.sh
# ... 进行导入和测试 ...

# 第二轮测试（清空旧数据后再导入新数据）
./clean_stock_data.sh
# ... 再次进行导入和测试 ...
```

### 场景 3: 数据回滚

如果导入过程中出错，使用此脚本快速回滚：

```bash
./clean_stock_data.sh
# 然后重新导入
```

## 注意事项

### ⚠️ 重要警告

- **此脚本会永久删除数据**，执行前请确保已备份重要数据
- 脚本会要求用户确认，请仔细阅读提示信息
- 删除是不可逆的，执行后数据无法恢复

### 📌 最佳实践

1. **定期备份数据库**
   ```bash
   pg_dump -U peak stock_analysis > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **在测试环境中使用**
   - 不要在生产数据库上运行此脚本
   - 确保在开发/测试环境中执行

3. **检查依赖关系**
   - 清理前确保没有其他应用正在访问这些表
   - 确保没有其他数据库连接在活跃

## 常见问题

### Q: 脚本执行时出现 "role does not exist" 错误

**A:** 检查数据库用户名是否正确：
```bash
# 指定正确的用户
DB_USER=your_actual_username ./clean_stock_data.sh
```

### Q: 脚本执行时出现外键约束错误

**A:** 说明有新增的外键关系未在脚本中处理，请：
1. 查看错误信息中的表名和约束名
2. 在 `clean_stock_data.sql` 中添加相应的 DELETE 语句
3. 保持删除顺序（先删依赖表，再删主表）

### Q: 如何恢复被删除的数据

**A:** 如果之前有备份，可以恢复：
```bash
# 恢复整个数据库
psql -U peak -d stock_analysis < backup_20250101_120000.sql

# 或仅恢复特定表
pg_restore -U peak -d stock_analysis -t stocks backup.dump
```

## 性能说明

- 脚本使用单个事务，全部成功或全部失败
- 删除 ~580,000 条记录通常需要 5-10 秒
- 分区表的删除可能比普通表更快

## 相关文档

- `test-data/QUICK_START.md` - 快速导入指南
- `test-data/README.md` - 完整导入指南
- `../app/core/database.py` - 数据库配置

---

**创建时间**: 2025-11-28
**最后更新**: 2025-11-28
**维护者**: Claude Code
