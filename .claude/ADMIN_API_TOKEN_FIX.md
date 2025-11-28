# 管理员API Token选择修复

## 问题

访问 `http://127.0.0.1:8005/admin/import/batches` 页面时，浏览器控制台返回：

```
{"detail":"Not authenticated"}
```

## 根本原因

### 令牌选择机制

前端的axios拦截器 (`frontend/src/api/request.ts:20`) 根据**URL路径**决定使用哪个token：

```typescript
if (config.url?.includes('/admin')) {
  token = localStorage.getItem('admin_access_token')  // ← 管理员token
} else {
  token = localStorage.getItem('client_access_token')  // ← 客户端token
}
```

### 问题流程

```
1. 用户登陆admin账户
   ↓
2. localStorage 中只有 admin_access_token (client_access_token 为空)
   ↓
3. 访问 http://127.0.0.1:8005/admin/import/batches 页面
   ↓
4. 前端调用 importApi.getBatches()
   → 请求 URL: /api/v1/import/batches (路径中无 /admin)
   ↓
5. Axios拦截器检查 URL
   ❌ URL不包含'/admin' → 选择 client_access_token
   ✅ 但 client_access_token 为空
   ↓
6. 请求发送时无Authorization header
   ↓
7. 后端返回 401 "Not authenticated"
```

### 为什么后端会返回401？

后端的导入API端点要求admin角色：

```python
@router.get("/batches")
async def list_batches(
    ...
    current_user: User = Depends(require_role(["admin"])),
):
    """Get import batch list - Admin only."""
```

但前端发送的请求没有包含有效的authorization header，所以被拒绝了。

## 解决方案

采用**与现有系统一致的URL前缀模式**。

### 系统中的令牌选择模式

**现有的一致模式**：
- 用户API: `/users/admin` ← 路径中包含 `/admin`
- 导入API（修复前）: `/import/batches` ← 路径中**不包含** `/admin` ❌
- 导入API（修复后）: `/admin/import/batches` ← 路径中包含 `/admin` ✅

### 修改1: 后端路由前缀

**文件**: `backend/app/api/imports.py`

```python
# 修改前
router = APIRouter(prefix="/import", tags=["Import"])

# 修改后
router = APIRouter(prefix="/admin/import", tags=["Import"])
```

**影响的端点**：
```
修改前                              修改后
/api/v1/import/upload          →  /api/v1/admin/import/upload
/api/v1/import/batches         →  /api/v1/admin/import/batches
/api/v1/import/batches/{id}    →  /api/v1/admin/import/batches/{id}
/api/v1/import/metrics         →  /api/v1/admin/import/metrics
```

### 修改2: 前端API调用

**文件**: `frontend/src/api/index.ts`

```typescript
// 修改前
export const importApi = {
  upload(formData: FormData) {
    return request.post('/import/upload', formData, ...)
  },
  getBatches(params) {
    return request.get('/import/batches', { params })
  },
  // ... 其他方法
}

// 修改后
export const importApi = {
  upload(formData: FormData) {
    return request.post('/admin/import/upload', formData, ...)
  },
  getBatches(params) {
    return request.get('/admin/import/batches', { params })
  },
  // ... 其他方法
}
```

## 修复效果验证

### 修复前后对比

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| admin用户访问/admin/import/batches | ❌ 401 "Not authenticated" | ✅ 成功加载 |
| 选择的Token | client_access_token (空) | admin_access_token (有效) |
| axios拦截器判断 | URL不含/admin | URL含/admin ✅ |

### 验证步骤

1. **登陆admin账户**
   ```
   访问 http://127.0.0.1:8005/admin-login
   输入 admin / admin
   ```

2. **导航到导入记录页面**
   ```
   访问 http://127.0.0.1:8005/admin/import/batches
   或点击左侧菜单 "数据导入" → "导入记录"
   ```

3. **打开浏览器开发者工具** (F12)
   - **Console**: 查看是否有错误日志
   - **Network**: 观察 API 请求
     - 查看 `/api/v1/admin/import/batches` 请求
     - 检查 Request Headers → Authorization: `Bearer <admin_token>`
     - 检查 Response Status: 应该是 200 而不是 401

4. **验证页面加载**
   - 页面应显示导入记录列表
   - 不应显示"Not authenticated"错误

## 深层分析

### 为什么需要URL路径包含/admin？

当系统支持多种身份（admin和client）时，前端需要根据请求类型选择正确的token：

```typescript
// 场景1: 请求管理员功能 → 需要 admin_access_token
GET /api/v1/admin/import/batches
Authorization: Bearer <admin_access_token>

// 场景2: 请求客户端功能 → 需要 client_access_token
GET /api/v1/reports/dashboard
Authorization: Bearer <client_access_token>
```

**URL路径**是最直接、最可靠的标志，因为：
1. 在axios拦截器运行时就可用
2. 不需要维护复杂的API端点映射表
3. 遵循REST规范中的前缀模式

### 为什么是/admin而不是其他前缀？

选择 `/admin` 前缀而不是其他名称的原因：

1. **语义清晰**: `/admin` 明确表示这是管理员资源
2. **现有一致性**: 用户API已经使用了 `/users/admin` 模式
3. **易于维护**: 开发者一眼就能看出这是admin-only的端点
4. **安全性**: 清晰的标记减少意外暴露admin功能的风险

## 其他相关的admin-only API

以下API也都需要在URL中包含/admin，以便正确的token选择：

```typescript
// ✅ 已正确使用 /admin 前缀
subscriptionApi.create('/subscriptions/admin')
usersApi.listUsers('/users/admin')
plansApi.getList  // 注意: /plans 不需要admin token (公开)

// ✅ 现在也包含了 /admin 前缀
importApi.getBatches('/admin/import/batches')
```

## 修复日志

**Git Commit**: 56b3ab4
```
fix: move import API endpoints under /admin prefix for proper token selection
```

**修改的文件**:
1. `backend/app/api/imports.py` (1行)
2. `frontend/src/api/index.ts` (7行)

**部署步骤**:
1. 停止后端: `./scripts/start.sh stop`
2. 部署新代码
3. 启动后端: `./scripts/start.sh backend`
4. 刷新前端页面

## 常见问题

### Q: 为什么只改进口路径而不改变拦截器逻辑？
**A**: 改变拦截器逻辑会很复杂（需要维护API端点到token类型的映射表）。改变URL前缀是更简单、更一致的方案。

### Q: 其他admin-only的API需要改吗？
**A**: 用户API (`/users/admin`) 已经遵循了这个模式。未来的admin-only API应该都使用 `/admin` 前缀。

### Q: 如果有客户端和admin都能用的API怎么办？
**A**: 使用基路径（如 `/reports`），不要添加 `/admin` 前缀。拦截器会尝试使用client token。

### Q: 这会不会改变API的版本兼容性？
**A**: 是的，这是一个breaking change。现有代码需要更新到新的URL。但由于这是内部API（没有外部用户），影响范围受控。

---

**修复日期**: 2025-11-28
**修复者**: Claude Code
**状态**: ✅ 完成并验证
