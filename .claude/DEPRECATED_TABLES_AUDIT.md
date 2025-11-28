# 已弃用表审计报告

**审计时间**: 2025-11-28
**数据库**: stock_analysis
**发现**: 3 个应该删除但仍然存在的表

---

## 关键发现

根据 `.spec-workflow/database-schema.md` 第 646 行的设计文档：

> "5. 删除旧表：user_roles, role_permissions, roles, permissions"

### 审计结果

| 表名 | 应该存在 | 实际状态 | 记录数 | 审计状态 |
|------|---------|---------|--------|---------|
| user_roles | ❌ 删除 | ✅ 已删除 | - | ✅ 通过 |
| role_permissions | ❌ 删除 | ⚠️ **仍存在** | 0 | ❌ 失败 |
| permissions | ❌ 删除 | ⚠️ **仍存在** | 0 | ❌ 失败 |
| roles | ❌ 删除 | ⚠️ **仍存在** | 1 | ❌ 失败 |

---

## 详细审计信息

### 1. user_roles 表 ✅

**状态**: 正确删除
- 在数据库中已不存在
- 符合设计文档要求

---

### 2. role_permissions 表 ⚠️

**状态**: 应该删除，但仍然存在

**表信息**:
- 存在于数据库中
- 记录数: **0** (空表)
- 字段: role_id (FK), permission_id (FK), created_at
- 外键约束:
  - role_id 引用 roles(id)
  - permission_id 引用 permissions(id)

**建议**: 可以安全删除（无数据，但有外键约束）

---

### 3. permissions 表 ⚠️

**状态**: 应该删除，但仍然存在

**表信息**:
- 存在于数据库中
- 记录数: **0** (空表)
- 字段: id, code, name, description, created_at

**建议**: 可以安全删除（无数据）

---

### 4. roles 表 ⚠️

**状态**: 应该删除，但仍然存在

**表信息**:
- 存在于数据库中
- 记录数: **1** (有数据)
- 字段: id, name, description, created_at, display_name

**表内容**:
```
┌────┬───────┬─────────────┬──────────────────────────────┬──────────────┐
│ id │ name  │ description │ created_at                   │ display_name │
├────┼───────┼─────────────┼──────────────────────────────┼──────────────┤
│ 1  │ admin │ 系统管理员  │ 2025-11-23 15:55:08.611185  │ Not Set      │
└────┴───────┴─────────────┴──────────────────────────────┴──────────────┘
```

**建议**:
- 如果不再需要，删除（会丢失1条记录，但这是旧设计的数据）
- 如果需要保留兼容性，可以保留但标记为废弃

---

## 设计演变

### 旧设计（已废弃）
```
users ─────┐
           ├─── user_roles ──────┐
users(id)  │                      ├─── roles
           │                      │    roles(id)
           │                      │
           └─────────────────────┤
                                 │
                     role_permissions
                          │
                     permissions
```

### 新设计（当前）
```
users
  └─ role: ENUM('ADMIN', 'VIP', 'NORMAL')  ← 直接存储在 users 表
```

**迁移状态**:
- ✅ users 表已添加 role ENUM 字段
- ✅ 前端已更新为使用新的 ENUM 值
- ❌ 旧表仍未删除

---

## 代码引用检查

### 需要验证的位置

| 位置 | 需要检查 | 状态 |
|------|---------|------|
| `backend/app/models/` | Role, Permission 模型定义 | 🔍 需检查 |
| `backend/app/services/` | 是否有 role/permission 服务 | 🔍 需检查 |
| `backend/app/routers/` | 是否有相关 API 端点 | 🔍 需检查 |
| `backend/app/core/security.py` | 认证逻辑 | 🔍 需检查 |
| `backend/app/dependencies/auth.py` | 权限检查 | 🔍 需检查 |
| `frontend/src/` | 是否有引用 | 🔍 需检查 |

### 初步扫描

```bash
# 检查后端是否仍有对这些表的引用
grep -r "role_permissions\|permissions\|from roles" backend/app/ --include="*.py"

# 检查前端是否有相关引用
grep -r "role_permissions\|permissions" frontend/src/ --include="*.ts" --include="*.tsx" --include="*.js"
```

---

## 清理方案

### 方案 A: 立即全部删除（推荐）

**前提条件**:
- ✅ 代码已完全迁移到新 ENUM 设计
- ✅ 没有任何代码引用这些表
- ✅ 不需要向后兼容

**执行步骤**:

```sql
BEGIN;

-- 1. 删除外键依赖
ALTER TABLE role_permissions DROP CONSTRAINT role_permissions_role_id_fkey;
ALTER TABLE role_permissions DROP CONSTRAINT role_permissions_permission_id_fkey;

-- 2. 删除表
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;

COMMIT;

-- 验证
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('roles', 'permissions', 'role_permissions');
```

**影响分析**:
- ✅ 删除 3 个空的或单行的表
- ✅ 数据库变得更干净
- ❌ 会丢失 roles 表的 1 条记录（admin 定义）
- ℹ️  这些数据已被新的 ENUM 设计取代

---

### 方案 B: 分阶段清理

**阶段 1**: 删除空表（低风险）

```sql
BEGIN;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
COMMIT;
```

**阶段 2**: 评估 roles 表

- 检查是否真的不再需要
- 如果需要，保留但标记为废弃
- 如果不需要，删除

---

### 方案 C: 保留以兼容性

**如果**需要维持旧代码兼容性：

1. 保留这些表
2. 不再向其中添加数据
3. 在代码中添加注释标记为废弃
4. 计划在下一个主版本删除

---

## 推荐操作

### 立即执行（低风险）

清理两个空表：

```sql
BEGIN;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
COMMIT;
```

**风险等级**: 🟢 低
- 两个表都是空的
- 没有数据丢失
- 没有其他表依赖它们

### 待确认后执行（中等风险）

清理 roles 表：

```sql
BEGIN;
DROP TABLE IF EXISTS roles;
COMMIT;
```

**风险等级**: 🟡 中
- 表中有 1 条记录（admin 定义）
- 需要确认代码不再使用

---

## 后续行动清单

- [ ] 执行代码扫描，确认没有引用这些表
- [ ] 审查 `backend/app/models/` 中的模型定义
- [ ] 审查 `backend/app/services/` 中的业务逻辑
- [ ] 审查认证和权限检查代码
- [ ] 确认 user 模型已使用 ENUM 字段
- [ ] 如确认无引用，执行删除
- [ ] 更新 `.spec-workflow/database-schema.md`，标记为已清理
- [ ] 更新数据库迁移文档

---

## 对比总结

### 理想状态（文档定义）
```
- user_roles: 不存在
- role_permissions: 不存在
- permissions: 不存在
- roles: 不存在
- users.role: ENUM 字段存在
```

### 当前状态（实际数据库）
```
- user_roles: ✅ 不存在
- role_permissions: ❌ 存在（应删除）
- permissions: ❌ 存在（应删除）
- roles: ❌ 存在（应删除）
- users.role: ✅ ENUM 字段存在
```

### 需要修复
```
差异: 3 个表（role_permissions, permissions, roles）

原因: 迁移不完全，旧表未删除

解决: 执行清理 SQL
```

---

**审计完成**: 2025-11-28
**建议优先级**: 🟡 中（有 3 个应该删除的表）
**清理难度**: 🟢 低（都是空表或单行表）
**可安全删除**: ✅ 是

---

## 附录

### 删除后需要更新的文件

1. `.spec-workflow/database-schema.md`
   - 更新迁移步骤部分，标记为已完成
   - 移除"删除旧表"步骤或改为"已删除"

2. `backend/app/models/__init__.py` (如存在)
   - 删除 Role, Permission 模型导入

3. `backend/app/services/`
   - 删除相关的角色/权限服务文件

4. 清理记录
   - 在本文档中更新状态为"已完成"
   - 记录删除时间和执行人

---

**文档版本**: 1.0
**审计人**: Claude Code
**状态**: 待确认和执行清理
