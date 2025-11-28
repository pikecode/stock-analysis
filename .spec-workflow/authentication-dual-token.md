# 双Token独立存储认证架构

## 概述

该项目实现了一套完整的双Token独立存储认证系统，支持同一用户在不同身份（管理员、客户端）间的切换和并行运行。

**版本**：2.0 (实现完成日期：2024-11-28)
**状态**：已实现并通过测试

## 核心设计原则

### 1. 身份隔离
- **管理员身份** (`admin_*`) - 后台管理系统访问
- **客户端身份** (`client_*`) - 普通用户功能访问
- 两个身份完全独立，不相互污染
- 一个浏览器可同时保持两个身份登录

### 2. Token 分离
前端 localStorage 中存储4个Token：

```javascript
// 管理员身份
admin_access_token      // 有效期：30分钟
admin_refresh_token     // 有效期：7天

// 客户端身份
client_access_token     // 有效期：30分钟
client_refresh_token    // 有效期：7天
```

### 3. 请求路由
根据请求URL路径自动选择Token：
- 包含 `/admin` 的路径 → 使用 `admin_access_token`
- 其他路径 → 使用 `client_access_token`

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                   浏览器 / localStorage                      │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │  Admin 身份          │  │  Client 身份             │   │
│  │  ├─ admin_access    │  │  ├─ client_access       │   │
│  │  └─ admin_refresh   │  │  └─ client_refresh      │   │
│  └──────────────────────┘  └──────────────────────────┘   │
└─────────────┬───────────────────────────────────────────────┘
              │
         请求拦截器
    ↓                            ↓
包含 /admin 的请求    包含 /reports, /analysis 的请求
   ↓                            ↓
使用 admin_access       使用 client_access
   ↓                            ↓
┌───────────────────────────────────────────┐
│         FastAPI 后端                      │
│  ┌────────────────────────────────────┐  │
│  │    JWT 令牌验证中间件              │  │
│  │    - 验证签名和有效期              │  │
│  │    - 提取用户信息                  │  │
│  └────────────────────────────────────┘  │
│           ↓                               │
│  ┌────────────────────────────────────┐  │
│  │  路由处理 (Admin / Client)          │  │
│  │  - 权限检查                        │  │
│  │  - 数据操作                        │  │
│  └────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

## 前端实现详情

### 1. Pinia Auth Store (`frontend/src/stores/auth.ts`)

#### 状态管理
```typescript
// 分离的用户信息
adminUser: ref<User | null>(null)      // 管理员用户
clientUser: ref<User | null>(null)     // 客户端用户

// 聚合的计算属性
user: computed(() => adminUser.value || clientUser.value)  // 当前活跃用户
isAdmin: computed(() => adminUser.value?.role === 'ADMIN')
isVip: computed(() => clientUser.value?.role === 'VIP')
```

#### 关键方法

**1. login(credentials, loginType)**
```typescript
// loginType: 'admin' | 'client'
const success = await authStore.login(form, 'admin')
// - 调用 POST /api/v1/auth/login
// - 根据 loginType 存储不同的 token
// - 调用对应的 fetchAdminUser() 或 fetchClientUser()
// - 返回 true/false
```

**2. fetchAdminUser()**
```typescript
// 获取管理员用户信息
// - 从 localStorage 获取 admin_access_token
// - 使用原生 fetch 直接发送请求，明确指定 token
// - 避免请求拦截器混淆 token 选择
// - 成功后设置 adminUser
```

**3. fetchClientUser()**
```typescript
// 获取客户端用户信息
// - 从 localStorage 获取 client_access_token
// - 使用原生 fetch 直接发送请求，明确指定 token
// - 成功后设置 clientUser 和调用 fetchSubscription()
```

**4. logout(logoutType)**
```typescript
// logoutType: 'admin' | 'client' | 'all'
await authStore.logout('admin')  // 仅登出管理员身份
// - 清除相应的 token
// - 清除相应的用户信息
// - 调用后端 logout 接口（可选）
```

### 2. 请求拦截器 (`frontend/src/api/request.ts`)

#### 请求阶段
```typescript
// 根据 URL 选择 token
if (config.url?.includes('/admin')) {
  token = localStorage.getItem('admin_access_token')
} else {
  token = localStorage.getItem('client_access_token')
}

// 添加到请求头
if (token) {
  config.headers.Authorization = `Bearer ${token}`
}
```

#### 响应阶段（401 处理）
```typescript
// Token 过期时自动刷新
const isAdminPath = error.config?.url?.includes('/admin')
const tokenKey = isAdminPath ? 'admin_refresh_token' : 'client_refresh_token'

// 使用对应的 refresh token 获取新的 access token
const res = await axios.post('/api/v1/auth/refresh', {
  refresh_token: refreshToken,
})

// 更新存储并重试请求
localStorage.setItem(accessTokenKey, access_token)
return request(error.config)  // 自动重试
```

### 3. 路由守卫 (`frontend/src/router/index.ts`)

#### 初始认证检查
```typescript
// 1. 检查是否需要登录
if (requiresAuth) {
  if (isAdminPath && !hasAdminToken) {
    // 管理员路径缺少 admin token → 重定向到 /admin-login
    next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
    return
  }

  if (!isAdminPath && !hasClientToken) {
    // 客户端路径缺少 client token → 重定向到 /login
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
}
```

#### 已登录访问登录页处理
```typescript
// 2. 如果已有对应身份的 token，不允许重新登录
if (to.name === 'Login' && hasClientToken) {
  // 客户端用户已登录，重定向到首页
  next({ path: '/' })
  return
}

if (to.name === 'AdminLogin' && hasAdminToken) {
  // 管理员已登录，重定向到管理后台
  next({ path: '/admin' })
  return
}

// 3. 否则允许访问登录页（支持跨身份认证）
```

#### 角色权限检查
```typescript
// 特殊处理 'customer' 角色（后端返回 VIP 或 NORMAL）
const isRequiredRoleCustomer = requiredRole === 'customer'

if (isRequiredRoleCustomer && hasClientToken) {
  // 检查订阅状态而不检查具体角色值
  if (requiresSubscription && !authStore.hasValidSubscription) {
    next({ name: 'SubscriptionExpired' })
  } else {
    next()
  }
}

// 其他角色使用精确匹配
if (!isRequiredRoleCustomer) {
  const user = isAdminPath ? authStore.adminUser : authStore.clientUser
  if (!user || !authStore.hasRole(requiredRole)) {
    // 角色不匹配，登出并重定向
    authStore.logout(isAdminPath ? 'admin' : 'client')
    next({ name: isAdminPath ? 'AdminLogin' : 'Login' })
  }
}
```

### 4. 登录页面实现

**AdminLogin.vue** 和 **Login.vue** 的关键逻辑：

```typescript
const handleLogin = async () => {
  // 1. 调用 login 并指定身份类型
  const success = await authStore.login(form, 'admin')

  if (!success) {
    ElMessage.error('用户名或密码错误')
    return
  }

  // 2. 验证身份（管理员登录要求 role === 'ADMIN'）
  if (!authStore.isAdmin) {
    ElMessage.error(`角色错误: ${authStore.adminUser?.role}`)
    await authStore.logout('admin')
    return
  }

  // 3. 重定向到目标页面或默认首页
  const redirect = route.query.redirect || '/admin'
  router.push(redirect)
}
```

## 后端实现详情

### 1. JWT 令牌配置

后端需要在环境变量或配置文件中设置：
```
ACCESS_TOKEN_EXPIRE_MINUTES=30      # Access token 有效期
REFRESH_TOKEN_EXPIRE_DAYS=7         # Refresh token 有效期
SECRET_KEY=your-secret-key          # JWT 签名密钥
ALGORITHM=HS256                     # 签名算法
```

### 2. 认证路由

```python
# POST /api/v1/auth/login
# - 验证用户名和密码
# - 返回 access_token 和 refresh_token（后端无需区分类型）
# - 前端根据登录页面自动分类存储

# POST /api/v1/auth/refresh
# - 验证 refresh_token 有效性
# - 返回新的 access_token 和 refresh_token

# POST /api/v1/auth/logout
# - 清除用户会话（可选，JWT 无状态）

# GET /api/v1/auth/me
# - 返回当前认证用户的完整信息
# - 包括 username, email, role, id 等
```

### 3. 权限检查中间件

```python
def require_role(required_role: str):
    """
    权限检查依赖
    用法: @router.get("/admin")
          async def get_admin(user = Depends(require_role("admin"))):
    """
    # - 从 Authorization header 提取 JWT token
    # - 验证签名和有效期
    # - 检查用户角色是否匹配
    # - 不匹配则返回 403 Forbidden
```

## 使用流程

### 场景 1：客户端用户独立登录

```
1. 用户访问 http://127.0.0.1:3000/login
2. 输入客户端凭证（如 customer / customer123）
3. 前端调用 authStore.login(credentials, 'client')
4. Token 保存到 localStorage:
   - client_access_token
   - client_refresh_token
5. 重定向到 / 或 /reports（如果有有效订阅）
6. 后续访问 /reports, /analysis 等使用 client token
```

### 场景 2：管理员用户独立登录

```
1. 用户访问 http://127.0.0.1:3000/admin-login
2. 输入管理员凭证（如 admin / Admin@123）
3. 前端调用 authStore.login(credentials, 'admin')
4. Token 保存到 localStorage:
   - admin_access_token
   - admin_refresh_token
5. 重定向到 /admin/dashboard
6. 后续访问 /admin/* 使用 admin token
```

### 场景 3：跨身份认证（双身份并行）

```
步骤 1：以客户端身份登录
  - 访问 /login，输入客户端凭证
  - 获得 client_access_token 和 client_refresh_token
  - 可访问客户端功能

步骤 2：切换为管理员身份
  - 访问 /admin → 路由守卫检查 admin_access_token（不存在）
  - 重定向到 /admin-login（而不是拒绝）
  - 输入管理员凭证
  - 获得 admin_access_token 和 admin_refresh_token

结果：
  - localStorage 中同时存在两个 token 对
  - 用户可在两个身份间快速切换
  - 访问 /admin/* 使用 admin token
  - 访问 /reports/* 使用 client token
  - 访问公开页面 / 使用任意 token
```

### 场景 4：Token 自动刷新

```
1. 发送请求时，使用 access_token
2. 服务器返回 401 Unauthorized（token 过期）
3. 前端拦截器自动：
   a. 根据路径判断是哪个身份的 token
   b. 从 localStorage 获取 refresh_token
   c. 发送 POST /api/v1/auth/refresh
   d. 获得新的 access_token
   e. 重试原始请求
4. 用户无感知，继续操作
```

## 数据库角色定义

后端数据库中的用户角色定义：

```sql
-- 用户表 users
id, username, email, password_hash, role, created_at, updated_at

-- 角色枚举值
- 'ADMIN'   - 管理员（后台管理系统访问权限）
- 'VIP'     - VIP 客户（高级功能访问权限）
- 'NORMAL'  - 普通客户（基础功能访问权限）
```

**重要注意**：
- 后端只存储用户的单个 role 字段
- 前端 Pinia store 中 `adminUser` 和 `clientUser` 是分离的
- 后端无需感知前端的双Token架构，仅根据 JWT 中的 role 进行权限检查

## 路由配置

### 公开页面（无需登录）
```typescript
{
  path: '/',
  meta: { requiresAuth: false }
}
```

### 客户端页面（需要 client token）
```typescript
{
  path: '/reports',
  meta: {
    requiresAuth: true,
    requiredRole: 'customer',      // 特殊值：表示 VIP 或 NORMAL
    requiresSubscription: true      // 检查订阅状态
  }
}
```

### 管理员页面（需要 admin token）
```typescript
{
  path: '/admin',
  meta: {
    requiresAuth: true,
    requiredRole: 'admin'           // 精确值：role === 'ADMIN'
  }
}
```

## 安全考虑

### 优点
1. **身份隔离** - 两个身份互不影响，权限污染最小
2. **灵活认证** - 支持在同一浏览器中进行多身份操作
3. **Token 隔离** - Access Token 和 Refresh Token 分离，减少 Access Token 暴露风险
4. **自动刷新** - 过期 Token 自动刷新，用户体验无缝

### 风险
1. **XSS 攻击** - localStorage 中的 Token 可被 JavaScript 访问
   - 缓解：使用 HttpOnly Cookie（需后端支持）
   - 当前方案：确保代码无 XSS 漏洞，DOMPurify 清理用户输入

2. **Token 泄露** - 在 HTTP 连接上会被中间人拦截
   - 缓解：生产环境必须使用 HTTPS

3. **Token 伪造** - 如果 SECRET_KEY 泄露，Token 可被伪造
   - 缓解：定期轮换 SECRET_KEY，监控异常登录

### 最佳实践
1. 定期更换 SECRET_KEY
2. 生产环境使用 HTTPS
3. 设置合理的 Token 过期时间（太短降低体验，太长增加风险）
4. 监控和记录异常登录（如从不同地区快速登录）
5. 实现"登出所有设备"功能（需后端维护黑名单）

## 测试检查清单

- [x] 客户端用户可独立登录和访问客户端功能
- [x] 管理员用户可独立登录和访问管理后台
- [x] 支持跨身份认证（客户端用户可添加管理员身份）
- [x] Token 自动刷新机制正常工作
- [x] 路由守卫正确拦截无权限访问
- [x] 角色权限检查正常（特殊处理 'customer' 角色）
- [x] logout 可正确清除 token 和用户信息
- [x] 浏览器刷新后 token 仍有效
- [ ] 生产环境 HTTPS 配置
- [ ] Token 有效期配置验证
- [ ] 异常登录监控日志

## 相关文件

### 前端
- `frontend/src/stores/auth.ts` - Pinia 认证 store
- `frontend/src/api/request.ts` - Axios 请求拦截器
- `frontend/src/router/index.ts` - Vue Router 路由守卫
- `frontend/src/views/Login.vue` - 客户端登录页
- `frontend/src/views/AdminLogin.vue` - 管理员登录页

### 后端
- `backend/app/api/auth.py` - 认证 API 路由
- `backend/app/core/security.py` - JWT 令牌管理
- `backend/app/dependencies/auth.py` - 认证依赖和权限检查
- `backend/app/models/user.py` - 用户数据模型

### 文档
- `.spec-workflow/steering/tech.md` - 技术文档（包含双Token说明）
- `.spec-workflow/database-schema.md` - 数据库设计
- `.spec-workflow/authentication-dual-token.md` - 本文件

## 未来改进

1. **HTTP-Only Cookie** - 将 Token 存储在 HttpOnly Cookie 中（防止 XSS）
2. **Refresh Token Rotation** - 每次刷新 Token 时生成新的 Refresh Token
3. **Token Blacklist** - 实现 Token 黑名单，支持"登出所有设备"
4. **多设备管理** - 记录用户登录设备，支持远程登出特定设备
5. **二次认证** - 管理员操作敏感功能时要求二次验证
6. **审计日志** - 记录所有重要操作（登录、权限变更等）
