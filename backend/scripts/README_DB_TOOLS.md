# 数据库工具脚本说明

## 1. 数据库结构对比工具

### compare_db_schemas.py

**用途**：对比本地和生产数据库的表结构差异

**使用方法**：

```bash
cd backend
python scripts/compare_db_schemas.py
```

**功能**：
- ✅ 列出只在本地存在的表（生产环境缺少）
- ✅ 列出只在生产存在的表（可能需要清理）
- ✅ 对比共同表的列定义差异
- ✅ 重点检查核心表（users, subscriptions等）

**输出示例**：

```
===============================================================================
表: subscriptions
===============================================================================

❌ 生产环境缺少的列:
  - transaction_id: character varying(100)
  - notes: text

⚠️  本地环境缺少的列（生产环境多余）:
  - is_valid: boolean DEFAULT true
  - valid_until: timestamp without time zone

⚠️  列定义不一致:
+-------------+---------------------------+---------------------------+
| 列名        | 生产环境                  | 本地环境                  |
+=============+===========================+===========================+
| status      | character varying(10)     | character varying(20)     |
+-------------+---------------------------+---------------------------+
```

**依赖**：
```bash
pip install psycopg2-binary tabulate
```

## 2. 数据库迁移脚本

### migrate_subscriptions_table.sql

添加subscriptions表的新字段

### migrate_subscription_logs.sql

添加subscription_logs表的新字段

### cleanup_subscription_tables.sql

清理subscriptions和subscription_logs表的旧字段

**使用方法**：

```bash
# 本地测试
psql -h localhost -U peak -d stock_analysis -f scripts/cleanup_subscription_tables.sql

# 生产环境
ssh ubuntu@82.157.28.35
cd /var/www/stock-analysis/backend/scripts
PGPASSWORD=stock_pass_2024 psql -h localhost -U stock_user -d stock_analysis -f cleanup_subscription_tables.sql
```

## 3. 初始化脚本

### init-db-full.sql

完整的数据库初始化脚本，包含所有表定义

**使用场景**：
- 新环境首次部署
- 重建测试数据库
- 创建开发环境

**使用方法**：

```bash
# 创建新数据库
createdb stock_analysis

# 执行初始化
psql -d stock_analysis -f backend/scripts/init-db-full.sql
```

### init_test_data.sql / init_test_data.py

初始化测试数据（用户、套餐）

**使用方法**：

```bash
# SQL方式
psql -d stock_analysis -f backend/scripts/init_test_data.sql

# Python方式
python backend/scripts/init_test_data.py
```

## 4. 定期检查流程

建议每次修改Model后执行以下检查：

1. **检查本地数据库是否同步**
   ```bash
   python scripts/compare_db_schemas.py
   ```

2. **生成Alembic迁移**
   ```bash
   alembic revision --autogenerate -m "描述变更"
   ```

3. **检查生成的迁移脚本**
   ```bash
   cat alembic/versions/<newest_file>.py
   ```

4. **应用到本地数据库**
   ```bash
   alembic upgrade head
   ```

5. **再次对比确认**
   ```bash
   python scripts/compare_db_schemas.py
   ```

6. **部署到生产环境**
   ```bash
   # 备份生产数据库
   ssh ubuntu@82.157.28.35 "PGPASSWORD=stock_pass_2024 pg_dump -h localhost -U stock_user stock_analysis > backup.sql"

   # 应用迁移
   ssh ubuntu@82.157.28.35 "cd /var/www/stock-analysis/backend && source venv/bin/activate && alembic upgrade head"
   ```

## 5. 常见问题

### Q: compare_db_schemas.py报错无法连接？

**A**: 检查数据库连接信息，确保：
- 本地PostgreSQL正在运行
- 生产服务器可访问
- 数据库用户名密码正确

### Q: 迁移脚本执行失败？

**A**: 检查：
1. 是否有数据依赖（外键、非空约束）
2. 是否需要先迁移数据
3. 查看完整错误信息

### Q: 如何回滚迁移？

**A**:
```bash
# 使用Alembic回滚
alembic downgrade -1

# 或手动执行
psql -d stock_analysis -c "DELETE FROM alembic_version;"
# 然后重新运行迁移
```

## 6. 最佳实践

1. ✅ 每次修改Model后立即对比数据库
2. ✅ 使用Alembic管理迁移（自动生成+手动审查）
3. ✅ 生产环境部署前在测试环境验证
4. ✅ 保留迁移脚本备份
5. ✅ 记录每次迁移的详细说明

## 7. 工具版本

- PostgreSQL: 12+
- Python: 3.8+
- psycopg2: 2.9+
- Alembic: 1.14+
