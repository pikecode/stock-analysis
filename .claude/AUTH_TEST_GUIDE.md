# 认证修复测试指南

## 快速测试步骤

### 前置条件
- 系统已启动：`./scripts/start.sh all`
- 浏览器打开 F12 开发者工具 → Console 标签
- 清理 localStorage：F12 → Application → LocalStorage → 删除所有旧数据

---

## 测试场景1: ADMIN用户尝试通过客户端登陆

### 步骤
1. 打开 `http://127.0.0.1:8005/login`
2. 输入凭证
   - 用户名: `admin`
   - 密码: `admin` (或 `Admin@123` 取决于初始化脚本)
3. 点击【登录】按钮
4. 观察结果和控制台日志

### 期望结果 ✅
- **用户界面**: 显示错误提示 "管理员用户请使用管理员登录页面"
- **页面状态**: 仍停留在登陆页，表单被清空
- **localStorage**: 被清除（`client_access_token` 被删除）
- **控制台日志** (应包含):
  ```
  🔍 检查用户角色，clientUser.role: ADMIN
  ❌ 管理员用户不能访问客户端
  ```

### 验证成功标志
✅ 如果看到上述提示和日志 → 修复生效！

---

## 测试场景2: 客户端用户正常登陆

### 前置条件
确保数据库中存在一个非ADMIN客户端用户，例如：
- 用户名: `customer`
- 密码: `customer123` (或在 init 脚本中定义的密码)
- 角色: `NORMAL` 或 `VIP`

### 步骤
1. 打开 `http://127.0.0.1:8005/login`
2. 输入客户端凭证
   - 用户名: `customer`
   - 密码: `customer123`
3. 点击【登录】按钮
4. 观察结果和控制台日志

### 期望结果 ✅
- **用户界面**: 显示成功提示 "登录成功" → 重定向到首页
- **页面状态**: 成功重定向到 `/` (首页)
- **localStorage**: 包含 `client_access_token` 和 `client_refresh_token`
- **控制台日志** (应包含):
  ```
  🔍 检查用户角色，clientUser.role: NORMAL  (或 VIP)
  ✅ 登录成功！
  📍 重定向到: /
  ```

### 验证成功标志
✅ 成功登陆并重定向到首页 → 客户端用户正常工作！

### 后续验证
登陆后，验证能够访问受限功能：
1. 点击页面导航访问 `/reports` (报表)
2. 应该成功加载报表页面
3. 如果提示"订阅已过期"是正常的（取决于订阅设置）

---

## 测试场景3: ADMIN用户通过管理员登陆

### 步骤
1. 打开 `http://127.0.0.1:8005/admin-login`
2. 输入管理员凭证
   - 用户名: `admin`
   - 密码: `admin` (或 `Admin@123`)
3. 点击【登录】按钮
4. 观察结果和控制台日志

### 期望结果 ✅
- **用户界面**: 显示成功提示 "登录成功"
- **页面状态**: 重定向到 `/admin` (管理后台)
- **localStorage**: 包含 `admin_access_token` 和 `admin_refresh_token`
- **控制台日志** (应包含):
  ```
  🔍 检查用户角色，adminUser.role: ADMIN
  ✅ 管理员登录成功！
  📍 重定向到: /admin
  ```

### 验证成功标志
✅ 成功进入管理后台 → ADMIN用户正常工作！

---

## 测试场景4: 非ADMIN用户尝试通过管理员登陆

### 步骤
1. 打开 `http://127.0.0.1:8005/admin-login`
2. 输入客户端凭证
   - 用户名: `customer`
   - 密码: `customer123`
3. 点击【登录】按钮
4. 观察结果和控制台日志

### 期望结果 ✅
- **用户界面**: 显示错误提示 "此页面仅限管理员访问。您的角色为: NORMAL"
- **页面状态**: 仍停留在管理员登陆页，表单被清空
- **localStorage**: 被清除
- **控制台日志** (应包含):
  ```
  🔍 检查用户角色，adminUser.role: NORMAL
  ❌ 用户不是管理员，角色为: NORMAL
  ```

### 验证成功标志
✅ 看到角色检查和拒绝提示 → 非ADMIN用户被正确拒绝！

---

## 调试技巧

### 查看完整的登陆流程日志
1. 打开 F12 Console
2. 过滤日志，只显示认证相关：
   ```javascript
   // 在控制台输入以下命令查看所有token
   console.table({
     admin_token: localStorage.getItem('admin_access_token')?.slice(0, 20) + '...',
     client_token: localStorage.getItem('client_access_token')?.slice(0, 20) + '...',
     admin_user: JSON.parse(sessionStorage.getItem('adminUser') || '{}'),
     client_user: JSON.parse(sessionStorage.getItem('clientUser') || '{}')
   })
   ```

### 重置测试状态
```javascript
// 清除所有认证数据
localStorage.removeItem('admin_access_token')
localStorage.removeItem('admin_refresh_token')
localStorage.removeItem('client_access_token')
localStorage.removeItem('client_refresh_token')
// 页面会自动重定向到登陆页
```

### 查看当前用户信息
```javascript
// 在Console中执行以查看当前认证状态
JSON.stringify({
  adminToken: !!localStorage.getItem('admin_access_token'),
  clientToken: !!localStorage.getItem('client_access_token'),
}, null, 2)
```

---

## 测试结果记录表

| 场景 | 用户名 | 预期结果 | 实际结果 | 是否通过 | 备注 |
|------|--------|---------|---------|---------|------|
| 场景1 | admin | ❌ 拒绝 | | | |
| 场景2 | customer | ✅ 成功 | | | |
| 场景3 | admin | ✅ 成功 | | | |
| 场景4 | customer | ❌ 拒绝 | | | |

---

## 常见问题排查

### Q: 登陆后被自动登出？
**A**: 检查 localStorage 中的 token 是否被正确保存。可能原因：
- API端点返回错误
- 后端未正确生成token
- 网络连接问题

**解决**: 打开 F12 → Network 标签，观察 `/api/v1/auth/login` 的响应。

### Q: 修改前后日志相同？
**A**: 可能是浏览器缓存问题。解决方式：
1. F12 → Application → Storage → 清除所有
2. 按 Ctrl+Shift+Delete 清除浏览器缓存
3. 或使用浏览器的隐身模式重新测试

### Q: 修改后仍能访问 /reports？
**A**: 这可能是：
1. 路由守卫未生效（刷新页面试试）
2. 仍有有效的 client_access_token
3. localStorage 中仍有旧数据

**排查**: 清空所有 localStorage 后重试。

### Q: 无法访问管理员登陆页面？
**A**: 这是正常的路由守卫行为。如果你有 client_access_token，访问 `/admin-login` 会被重定向。
**解决**: 先清除所有token再试。

---

## 完整测试清单

```
认证修复验证清单
===========================

场景1: ADMIN用户客户端登陆拒绝测试
  - [ ] 进入 /login 页面
  - [ ] 输入 admin/admin 凭证
  - [ ] 点击登录
  - [ ] 收到错误提示 ✅
  - [ ] 表单被清空 ✅
  - [ ] 控制台显示 ADMIN 角色检查 ✅

场景2: 客户端用户正常登陆测试
  - [ ] 进入 /login 页面
  - [ ] 输入 customer/customer123 凭证
  - [ ] 点击登录
  - [ ] 重定向到首页 ✅
  - [ ] token 被保存到 localStorage ✅
  - [ ] 能访问 /reports ✅

场景3: ADMIN用户管理员登陆成功测试
  - [ ] 进入 /admin-login 页面
  - [ ] 输入 admin/admin 凭证
  - [ ] 点击登录
  - [ ] 重定向到 /admin ✅
  - [ ] admin token 被保存 ✅
  - [ ] 能访问管理功能 ✅

场景4: 客户端用户管理员登陆拒绝测试
  - [ ] 进入 /admin-login 页面
  - [ ] 输入 customer/customer123 凭证
  - [ ] 点击登录
  - [ ] 收到错误提示（角色为NORMAL/VIP）✅
  - [ ] 表单被清空 ✅
  - [ ] 控制台显示角色检查 ✅

总体状态：
  - [ ] 所有4个场景都通过 ✅
  - [ ] 修复已生效
  - [ ] 可上线
```

---

**测试日期**: ___________
**测试人员**: ___________
**结果**: ___________
