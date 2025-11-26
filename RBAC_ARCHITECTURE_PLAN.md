# 🔐 权限管理架构改造方案

## 需求定义

**角色划分**：
- **Admin（管理员）**：可访问数据导入、数据管理功能
- **Customer/User（普通用户）**：可访问报表、查询功能

**访问控制**：
| 功能模块 | Admin | Customer | 说明 |
|---------|-------|----------|------|
| 股票列表 | ✅ | ✅ | 所有用户可查看 |
| 概念列表 | ✅ | ✅ | 所有用户可查看 |
| 排名查询 | ✅ | ✅ | 所有用户可查看 |
| **数据导入** | ✅ | ❌ | 仅管理员 |
| **导入记录** | ✅ | ❌ | 仅管理员 |
| **报表总览** | ❌ | ✅ | 仅普通用户 |
| **概念排名报表** | ❌ | ✅ | 仅普通用户 |
| **股票趋势报表** | ❌ | ✅ | 仅普通用户 |
| **Top N 分析** | ❌ | ✅ | 仅普通用户 |

---

## 后端改造方案

### 1. 数据库层（已有基础，需要初始化数据）

**已存在的模型**：
```
users → user_roles → roles ← role_permissions → permissions
```

**需要初始化的角色和权限**：

```sql
-- 1. 创建角色
INSERT INTO roles (name, display_name, description) VALUES
  ('admin', '管理员', '系统管理员，拥有所有权限'),
  ('customer', '普通用户', '普通用户，可查看报表'),
  ('viewer', '访客', '访客，只能查看部分功能');

-- 2. 创建权限
INSERT INTO permissions (resource, action, name, description) VALUES
  ('import', 'upload', 'import:upload', '上传导入文件'),
  ('import', 'view', 'import:view', '查看导入记录'),
  ('import', 'manage', 'import:manage', '管理导入'),
  ('report', 'view', 'report:view', '查看报表'),
  ('report', 'export', 'report:export', '导出报表'),
  ('stock', 'view', 'stock:view', '查看股票'),
  ('concept', 'view', 'concept:view', '查看概念'),
  ('ranking', 'view', 'ranking:view', '查看排名');

-- 3. 分配权限到角色
-- Admin 角色
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'admin' AND p.resource IN ('import', 'report', 'stock', 'concept', 'ranking');

-- Customer 角色（仅报表权限）
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'customer' AND p.resource IN ('report', 'stock', 'concept', 'ranking');

-- Viewer 角色（基础权限）
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'viewer' AND p.resource IN ('stock', 'concept', 'ranking');
```

### 2. 后端 API 改造

#### 2.1 创建权限检查依赖

**文件**：`backend/app/api/deps.py` 或在现有文件中添加

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user

async def require_role(
    required_roles: list[str]
):
    """权限检查装饰器工厂。

    Args:
        required_roles: 允许访问的角色列表，如 ['admin']
    """
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [role.name for role in current_user.roles]
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色: {', '.join(required_roles)}"
            )
        return current_user
    return check_role

async def require_permission(
    required_permission: str
):
    """权限检查装饰器工厂。

    Args:
        required_permission: 权限名称，如 'import:upload'
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = []
        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.append(permission.name)

        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要权限: {required_permission}"
            )
        return current_user
    return check_permission
```

#### 2.2 修改导入 API（仅 Admin）

**文件**：`backend/app/api/imports.py`

```python
from app.api.deps import require_role

@router.post("/upload")
async def upload_import(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(['admin']))
):
    """上传导入文件 - 仅管理员可用"""
    # 现有逻辑
    ...

@router.get("/batches")
async def get_import_batches(
    current_user: User = Depends(require_role(['admin']))
):
    """查看导入批次 - 仅管理员可用"""
    # 现有逻辑
    ...
```

#### 2.3 修改报表 API（仅 Customer）

**文件**：`backend/app/api/rankings.py` (新增报表端点时)

```python
@router.get("/concept/{concept_id}/stocks-in-range")
async def get_concept_stocks_in_date_range(
    concept_id: int,
    ...,
    current_user: User = Depends(require_role(['customer']))
):
    """获取概念股票排名 - 仅普通用户可用"""
    # 现有逻辑
    ...
```

#### 2.4 修改 Auth API 响应

**文件**：`backend/app/schemas/user.py`

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    status: str
    created_at: datetime
    roles: list[str]  # 已有
    permissions: list[str]  # 新增

class Config:
    from_attributes = True
```

**修改 auth.py 中的 get_me 端点**：

```python
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    permissions = []
    for role in current_user.roles:
        for permission in role.permissions:
            permissions.append(permission.name)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        status=current_user.status,
        created_at=current_user.created_at,
        roles=[role.name for role in current_user.roles],
        permissions=permissions,  # 新增
    )
```

---

## 前端改造方案

### 1. 更新用户 Store

**文件**：`frontend/src/stores/auth.ts`

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const roles = computed(() => user.value?.roles || [])
  const permissions = computed(() => user.value?.permissions || [])

  // 检查是否有某个角色
  const hasRole = (role: string) => {
    return roles.value.includes(role)
  }

  // 检查是否有某个权限
  const hasPermission = (permission: string) => {
    return permissions.value.includes(permission)
  }

  // 检查是否为管理员
  const isAdmin = computed(() => {
    return hasRole('admin')
  })

  // 检查是否为普通用户
  const isCustomer = computed(() => {
    return hasRole('customer')
  })

  // 初始化（登录后）
  const initUser = async () => {
    try {
      const response = await authApi.getMe()
      user.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to init user:', error)
      user.value = null
    }
  }

  // 登出
  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  return {
    user,
    roles,
    permissions,
    isAdmin,
    isCustomer,
    hasRole,
    hasPermission,
    initUser,
    logout,
  }
})
```

### 2. 修改导航菜单

**文件**：`frontend/src/layouts/MainLayout.vue`

```vue
<script setup lang="ts">
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()
</script>

<template>
  <el-menu>
    <!-- 共享菜单 - 所有用户可见 -->
    <el-menu-item index="/stocks">
      <el-icon><Document /></el-icon>
      <span>股票列表</span>
    </el-menu-item>

    <el-menu-item index="/concepts">
      <el-icon><Folder /></el-icon>
      <span>概念列表</span>
    </el-menu-item>

    <el-menu-item index="/rankings">
      <el-icon><TrendCharts /></el-icon>
      <span>排名查询</span>
    </el-menu-item>

    <!-- 管理员菜单 - 仅 Admin 可见 -->
    <el-sub-menu v-if="authStore.isAdmin" index="/import">
      <template #title>
        <el-icon><Upload /></el-icon>
        <span>数据导入</span>
      </template>
      <el-menu-item index="/import">上传文件</el-menu-item>
      <el-menu-item index="/import/batches">导入记录</el-menu-item>
    </el-sub-menu>

    <!-- 普通用户菜单 - 仅 Customer 可见 -->
    <el-sub-menu v-if="authStore.isCustomer" index="/reports">
      <template #title>
        <el-icon><DataAnalysis /></el-icon>
        <span>📊 报表</span>
      </template>
      <el-menu-item index="/reports">总览</el-menu-item>
      <el-menu-item index="/reports/concept-ranking">概念排名</el-menu-item>
      <el-menu-item index="/reports/stock-trend">股票趋势</el-menu-item>
      <el-menu-item index="/reports/top-n">Top N 分析</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>
```

### 3. 路由权限保护

**文件**：`frontend/src/router/index.ts`

```typescript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 权限检查
  const requiredRole = to.meta.requiredRole as string | undefined
  if (requiredRole && !authStore.hasRole(requiredRole)) {
    next({ path: '/' })
    return
  }

  const requiredPermission = to.meta.requiredPermission as string | undefined
  if (requiredPermission && !authStore.hasPermission(requiredPermission)) {
    next({ path: '/' })
    return
  }

  next()
})

// 路由配置中添加权限元数据
const routes = [
  {
    path: '/import',
    component: () => import('@/views/import/ImportView.vue'),
    meta: {
      title: '数据导入',
      requiredRole: 'admin',  // 新增
    },
  },
  {
    path: '/reports',
    component: () => import('@/views/reports/Dashboard.vue'),
    meta: {
      title: '报表总览',
      requiredRole: 'customer',  // 新增
    },
  },
]
```

### 4. API 调用时自动处理权限错误

**文件**：`frontend/src/api/request.ts`

```typescript
// 在响应拦截器中处理 403 错误
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      ElMessage.error('您没有权限访问此功能')
      // 可选：重定向到首页
      // router.push('/')
    }
    return Promise.reject(error)
  }
)
```

---

## 数据库初始化脚本

**文件**：`backend/scripts/init_rbac.sql`

```sql
-- 创建角色
INSERT INTO roles (name, display_name, description) VALUES
  ('admin', '管理员', '系统管理员，拥有所有权限') ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (name, display_name, description) VALUES
  ('customer', '普通用户', '普通用户，可查看报表') ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (name, display_name, description) VALUES
  ('viewer', '访客', '访客，只能查看部分功能') ON CONFLICT (name) DO NOTHING;

-- 创建权限
INSERT INTO permissions (resource, action, name, description) VALUES
  ('import', 'upload', 'import:upload', '上传导入文件') ON CONFLICT (name) DO NOTHING;
INSERT INTO permissions (resource, action, name, description) VALUES
  ('import', 'view', 'import:view', '查看导入记录') ON CONFLICT (name) DO NOTHING;
INSERT INTO permissions (resource, action, name, description) VALUES
  ('import', 'manage', 'import:manage', '管理导入') ON CONFLICT (name) DO NOTHING;

INSERT INTO permissions (resource, action, name, description) VALUES
  ('report', 'view', 'report:view', '查看报表') ON CONFLICT (name) DO NOTHING;
INSERT INTO permissions (resource, action, name, description) VALUES
  ('report', 'export', 'report:export', '导出报表') ON CONFLICT (name) DO NOTHING;

INSERT INTO permissions (resource, action, name, description) VALUES
  ('stock', 'view', 'stock:view', '查看股票') ON CONFLICT (name) DO NOTHING;
INSERT INTO permissions (resource, action, name, description) VALUES
  ('concept', 'view', 'concept:view', '查看概念') ON CONFLICT (name) DO NOTHING;
INSERT INTO permissions (resource, action, name, description) VALUES
  ('ranking', 'view', 'ranking:view', '查看排名') ON CONFLICT (name) DO NOTHING;

-- 分配权限到 Admin 角色（所有权限）
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- 分配权限到 Customer 角色（报表 + 查看权限）
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'customer' AND p.resource IN ('report', 'stock', 'concept', 'ranking')
ON CONFLICT DO NOTHING;

-- 分配权限到 Viewer 角色（仅查看权限）
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'viewer' AND p.resource IN ('stock', 'concept', 'ranking')
ON CONFLICT DO NOTHING;

-- 创建测试用户（可选）
INSERT INTO users (username, email, password_hash, status) VALUES
  ('admin', 'admin@example.com', '$2b$12$...', 'active') ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, email, password_hash, status) VALUES
  ('customer', 'customer@example.com', '$2b$12$...', 'active') ON CONFLICT (username) DO NOTHING;

-- 分配角色到用户
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'customer' AND r.name = 'customer'
ON CONFLICT DO NOTHING;
```

---

## 实施步骤

### Phase 1：后端权限系统（2-3 天）
- [ ] 在数据库中初始化角色和权限
- [ ] 创建 `require_role()` 和 `require_permission()` 装饰器
- [ ] 修改导入 API，添加 `@require_role(['admin'])`
- [ ] 修改获取当前用户的端点，返回权限列表
- [ ] 测试权限检查是否有效

### Phase 2：前端权限系统（1-2 天）
- [ ] 更新 auth Store，添加 `hasRole()`, `hasPermission()`, `isAdmin()`, `isCustomer()`
- [ ] 修改 MainLayout.vue，根据角色显示/隐藏菜单项
- [ ] 修改路由，添加权限元数据和保护
- [ ] 更新 API 请求拦截器，处理 403 错误

### Phase 3：报表开发（6-7 天）
- [ ] 创建报表组件和页面
- [ ] 集成权限检查（报表仅 customer 可见）
- [ ] 测试权限系统

**总计：9-12 天**

---

## 权限检查清单

### 后端检查
- [ ] 导入端点返回 403（非 Admin 用户）
- [ ] 报表端点返回 403（非 Customer 用户）
- [ ] `/auth/me` 返回用户的所有权限
- [ ] 日志记录所有权限检查失败

### 前端检查
- [ ] Admin 用户可见导入菜单
- [ ] Customer 用户可见报表菜单
- [ ] Admin 用户无法访问报表路由（重定向到首页）
- [ ] Customer 用户无法访问导入路由（重定向到首页）
- [ ] 权限错误显示友好提示信息

---

## 测试场景

### 场景 1：管理员用户
```
用户：admin
角色：['admin']
权限：['import:upload', 'import:view', 'import:manage', 'report:view', ...]
```
**预期**：
- ✅ 可访问导入功能
- ❌ 无法访问报表功能（404 或 403）

### 场景 2：普通用户
```
用户：customer
角色：['customer']
权限：['report:view', 'report:export', 'stock:view', ...]
```
**预期**：
- ❌ 无法访问导入功能（403）
- ✅ 可访问报表功能

### 场景 3：访客用户
```
用户：guest
角色：['viewer']
权限：['stock:view', 'concept:view', 'ranking:view']
```
**预期**：
- ❌ 无法访问导入和报表
- ✅ 可访问股票、概念、排名

---

## 最终架构图

```
┌─────────────────────────────────────────────────────────┐
│                   前端（Vue 3）                          │
│                                                          │
│  AdminLayout（显示导入） ← 用户角色: admin              │
│  CustomerLayout（显示报表）← 用户角色: customer          │
│  ViewerLayout（仅查看）← 用户角色: viewer               │
└────────────────┬─────────────────────────────────────────┘
                 │ JWT Token + 用户角色
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   后端（FastAPI）                        │
│                                                          │
│  /import → @require_role(['admin']) ✅                  │
│  /reports → @require_role(['customer']) ✅              │
│  /stocks → @require_role(['admin', 'customer']) ✅      │
│  /auth/me → 返回 roles + permissions ✅                 │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              数据库（PostgreSQL）                        │
│                                                          │
│  users → user_roles ← roles ← role_permissions → perm   │
└─────────────────────────────────────────────────────────┘
```

---

## 总结

**这个方案提供**：

1. ✅ **细粒度的权限控制** - 基于角色和权限
2. ✅ **前后端统一** - 前端显示+路由保护 + 后端 API 保护
3. ✅ **易于扩展** - 可轻松添加新角色和权限
4. ✅ **安全可靠** - 后端拒绝未授权请求，前端优化 UX
5. ✅ **清晰的业务逻辑** - Admin 管数据，Customer 看报表

**确认问题**：
1. ✅ 角色划分（Admin + Customer）是否合适？
2. ✅ 是否需要添加更多角色（如 Manager、Analyst）？
3. ✅ 权限粒度是否足够细？
4. ✅ 是否需要额外的审计日志？
