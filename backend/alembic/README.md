# Alembic 数据库迁移工具使用指南

## 什么是Alembic？

Alembic是SQLAlchemy的数据库迁移工具，用于管理数据库结构的版本变更。

## 常用命令

### 1. 生成迁移脚本

当你修改了Model定义后，运行：

```bash
cd backend
alembic revision --autogenerate -m "描述这次变更"
```

这会在 `alembic/versions/` 目录下生成一个迁移脚本，包含：
- `upgrade()` - 应用变更
- `downgrade()` - 回滚变更

**示例**：
```bash
alembic revision --autogenerate -m "add subscription tables"
```

### 2. 应用迁移

应用所有未执行的迁移：

```bash
alembic upgrade head
```

应用到特定版本：

```bash
alembic upgrade <revision_id>
```

### 3. 回滚迁移

回滚一个版本：

```bash
alembic downgrade -1
```

回滚到特定版本：

```bash
alembic downgrade <revision_id>
```

回滚所有迁移：

```bash
alembic downgrade base
```

### 4. 查看迁移历史

查看当前数据库版本：

```bash
alembic current
```

查看所有迁移记录：

```bash
alembic history
```

查看详细历史（包括提交信息）：

```bash
alembic history --verbose
```

### 5. 查看待应用的迁移

```bash
alembic show head
```

## 工作流程示例

### 场景1：添加新表

1. 在 `app/models/` 中创建新Model
2. 在 `app/models/__init__.py` 中导入新Model
3. 生成迁移：`alembic revision --autogenerate -m "add new table"`
4. 检查生成的迁移脚本（`alembic/versions/`）
5. 应用迁移：`alembic upgrade head`

### 场景2：修改表结构

1. 修改 `app/models/` 中的Model定义
2. 生成迁移：`alembic revision --autogenerate -m "modify table structure"`
3. **重要**：检查迁移脚本，确认变更正确
4. 应用迁移：`alembic upgrade head`

### 场景3：在生产环境应用迁移

1. 备份数据库：
   ```bash
   pg_dump -h localhost -U stock_user stock_analysis > backup.sql
   ```

2. 应用迁移：
   ```bash
   cd /var/www/stock-analysis/backend
   source venv/bin/activate
   alembic upgrade head
   ```

3. 验证：检查应用功能是否正常

4. 如需回滚：
   ```bash
   alembic downgrade -1
   ```

## 注意事项

### ⚠️ 重要提醒

1. **生成迁移后必须检查**
   - Alembic自动检测可能不完美
   - 特别注意ENUM类型、索引、外键的变更
   - 检查数据迁移逻辑（如字段重命名）

2. **生产环境操作**
   - 总是先备份数据库
   - 在测试环境先验证迁移
   - 准备回滚方案

3. **团队协作**
   - 迁移脚本提交到git
   - 保持迁移历史线性（避免分支）
   - 冲突时重新生成迁移

4. **数据迁移**
   - 添加/删除字段时考虑默认值
   - 重命名字段需要手动编写数据迁移
   - 大数据量迁移考虑分批处理

## 配置文件说明

- **alembic.ini** - Alembic主配置文件
- **alembic/env.py** - 环境配置（数据库连接、Model导入）
- **alembic/script.py.mako** - 迁移脚本模板
- **alembic/versions/** - 迁移脚本存放目录

## 常见问题

### Q: 如何手动创建迁移脚本？

```bash
alembic revision -m "manual migration"
```

然后手动编辑生成的文件。

### Q: 如何跳过某个迁移？

```bash
alembic stamp <target_revision>
```

这只更新版本标记，不执行SQL。

### Q: 迁移脚本冲突了怎么办？

1. 回滚到冲突前：`alembic downgrade <base_revision>`
2. 删除冲突的迁移文件
3. 重新生成：`alembic revision --autogenerate -m "merged changes"`

### Q: 如何在多个数据库上应用相同迁移？

使用相同的迁移脚本即可。Alembic会追踪每个数据库的版本。

## 最佳实践

1. ✅ 每次Model变更后立即生成迁移
2. ✅ 迁移消息清晰描述变更内容
3. ✅ 定期合并旧迁移（压缩历史）
4. ✅ 迁移脚本加入代码审查流程
5. ✅ 保持本地数据库与代码同步

## 参考资料

- [Alembic官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
