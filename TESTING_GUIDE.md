# 🧪 路由隔离测试指南

## 准备工作

### 1. 确保后端服务正常运行

```bash
# 打开新的终端窗口，进入项目目录
cd /Users/peakom/work/stock-analysis

# 启动后端服务
bash scripts/backend/start.sh
```

**预期输出**：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. 启动前端应用

```bash
# 打开新的终端窗口，进入前端目录
cd /Users/peakom/work/stock-analysis/frontend

# 安装依赖（如果还没有）
npm install

# 启动开发服务器
npm run dev
```

**预期输出**：
```
  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

---

## ✅ 测试场景 1：Admin 用户完整流程

### 第一步：访问登录页面

1. 在浏览器打开：`http://localhost:3000`
2. 应该看到登录界面，标题为"Stock Analysis 股票概念分析系统"

### 第二步：使用 Admin 用户登录

1. **用户名**：`admin`
2. **密码**：`admin`
3. 点击"登录"按钮

**预期结果**：
- ✅ 显示"登录成功"提示信息
- ✅ 自动跳转到 `/admin/stocks`
- ✅ 地址栏显示：`http://localhost:3000/admin/stocks`

### 第三步：验证 Admin 布局

进入 Admin 页面后检查：

1. **侧边栏标题**
   - 应该显示：`📊 管理后台`

2. **左侧菜单**（从上到下）
   - ✅ 股票管理（当前高亮）
   - ✅ 概念管理
   - ✅ 排名查询
   - ✅ 📥 数据导入（可展开）
     - 上传文件
     - 导入记录
   - ✅ 系统设置

3. **右上角用户区域**
   - 应该显示用户名：`admin`
   - 点击下拉菜单应该有"退出登录"选项

### 第四步：测试 Admin 菜单导航

点击菜单中的各个项目：

| 菜单项 | 预期 URL | 备注 |
|------|----------|------|
| 股票管理 | `/admin/stocks` | 默认选中 |
| 概念管理 | `/admin/concepts` | - |
| 排名查询 | `/admin/rankings` | - |
| 上传文件 | `/admin/import` | 展开 📥 数据导入 |
| 导入记录 | `/admin/import/batches` | 展开 📥 数据导入 |
| 系统设置 | `/admin/settings` | - |

✅ **预期结果**：所有链接都应该正常跳转，菜单项应该高亮对应的路由。

### 第五步：测试权限隔离 - 尝试访问客户端路由

1. 在地址栏手动输入：`http://localhost:3000/client/reports`
2. 按 Enter

**预期结果**：
- ❌ 页面重定向到 `/`（首页）
- ℹ️ 浏览器开发者工具控制台（F12 → Console）显示：
  ```
  User does not have required role: customer
  ```

### 第六步：查看 Admin 设置页面

1. 点击菜单中的"系统设置"
2. 地址栏应显示：`http://localhost:3000/admin/settings`

**预期显示内容**：
- 用户信息部分
  - 用户名：`admin`
  - 邮箱：显示 email 地址
  - 角色：`admin`（绿色标签）
  - 权限数：`8`

- 权限列表
  - `import:upload`
  - `import:view`
  - `import:manage`
  - `report:view`
  - `report:export`
  - `stock:view`
  - `concept:view`
  - `ranking:view`

### 第七步：退出登录

1. 点击右上角用户区域
2. 点击"退出登录"

**预期结果**：
- ✅ 显示"已退出登录"提示
- ✅ 重定向到登录页面
- ✅ 地址栏显示：`http://localhost:3000/login`

---

## ✅ 测试场景 2：Customer 用户完整流程

### 第一步：使用 Customer 用户登录

1. 在登录页面输入：
   - **用户名**：`customer`
   - **密码**：`customer`
2. 点击"登录"按钮

**预期结果**：
- ✅ 显示"登录成功"提示
- ✅ 自动跳转到 `/client/reports`
- ✅ 地址栏显示：`http://localhost:3000/client/reports`

### 第二步：验证 Client 布局

进入 Client 页面后检查：

1. **侧边栏标题**
   - 应该显示：`📈 数据分析`

2. **左侧菜单**（从上到下）
   - ✅ 股票查询
   - ✅ 概念查询
   - ✅ 排名查询
   - ✅ 📊 报表分析（当前高亮，可展开）
     - 报表总览
     - 概念排名
     - 股票趋势
     - Top N 分析
   - ✅ 用户设置

3. **右上角用户区域**
   - 应该显示用户名：`customer`

### 第三步：测试 Client 菜单导航

点击菜单中的各个项目：

| 菜单项 | 预期 URL | 备注 |
|------|----------|------|
| 股票查询 | `/client/stocks` | - |
| 概念查询 | `/client/concepts` | - |
| 排名查询 | `/client/rankings` | - |
| 报表总览 | `/client/reports` | 默认选中 |
| 概念排名 | `/client/reports/concept-ranking` | 展开 📊 报表分析 |
| 股票趋势 | `/client/reports/stock-trend` | 展开 📊 报表分析 |
| Top N 分析 | `/client/reports/top-n` | 展开 📊 报表分析 |
| 用户设置 | `/client/settings` | - |

✅ **预期结果**：所有链接都应该正常跳转，菜单项应该高亮对应的路由。

### 第四步：测试权限隔离 - 尝试访问管理员路由

1. 在地址栏手动输入：`http://localhost:3000/admin/import`
2. 按 Enter

**预期结果**：
- ❌ 页面重定向到 `/`（首页）
- ℹ️ 浏览器控制台显示：
  ```
  User does not have required role: admin
  ```

### 第五步：查看 Client 设置页面

1. 点击菜单中的"用户设置"
2. 地址栏应显示：`http://localhost:3000/client/settings`

**预期显示内容**：
- 个人信息部分
  - 用户名：`customer`
  - 邮箱：显示 email 地址
  - 联系方式：显示 phone（如果有）

- 账户权限部分
  - 可用功能列表（绿色标签）：
    - `report:view`
    - `report:export`
    - `stock:view`
    - `concept:view`
    - `ranking:view`

- 温馨提示
  - 显示："您当前拥有以下权限：股票查询、概念查询、排名查询和报表分析。如需获取更多功能，请联系系统管理员。"

### 第六步：退出登录

1. 点击右上角用户区域
2. 点击"退出登录"

**预期结果**：
- ✅ 显示"已退出登录"提示
- ✅ 重定向到登录页面

---

## ✅ 测试场景 3：菜单隔离验证

### 目标
验证不同角色的用户只能看到属于自己的菜单项。

### Admin 用户菜单
```
📊 管理后台
├── 股票管理 ✅
├── 概念管理 ✅
├── 排名查询 ✅
├── 📥 数据导入 ✅
│   ├── 上传文件 ✅
│   └── 导入记录 ✅
└── 系统设置 ✅

❌ 不应该看到 📊 报表分析
```

### Customer 用户菜单
```
📈 数据分析
├── 股票查询 ✅
├── 概念查询 ✅
├── 排名查询 ✅
├── 📊 报表分析 ✅
│   ├── 报表总览 ✅
│   ├── 概念排名 ✅
│   ├── 股票趋势 ✅
│   └── Top N 分析 ✅
└── 用户设置 ✅

❌ 不应该看到 📥 数据导入
```

---

## 🔍 浏览器开发者工具验证

### 打开开发者工具
按 **F12** 或 **Cmd+Option+I**（Mac）

### 检查 Network 标签

1. 在 Admin 用户状态下，尝试访问 `/client/reports`
   - 应该看到路由守卫被触发
   - 地址栏会显示重定向发生

2. 在 Customer 用户状态下，尝试访问 `/admin/import`
   - 应该看到相同的重定向行为

### 检查 Console 标签

当权限被拒绝时，应该看到：
```
User does not have required role: admin
```

或

```
User does not have required role: customer
```

### 检查 Application 标签

1. 查看 **Local Storage**
2. 找到 `access_token` 键值
3. 验证 token 存在且有效

---

## 📋 完整测试清单

### Admin 用户测试
- [ ] 登录成功，跳转到 `/admin/stocks`
- [ ] 显示 AdminLayout（标题："📊 管理后台"）
- [ ] 菜单显示 6 个顶级项目（包含数据导入子菜单）
- [ ] 所有 /admin/* 路由可以正常访问
- [ ] 尝试访问 /client/* 被重定向
- [ ] 控制台显示权限错误信息
- [ ] 设置页面显示 8 个权限
- [ ] 退出登录成功

### Customer 用户测试
- [ ] 登录成功，跳转到 `/client/reports`
- [ ] 显示 ClientLayout（标题："📈 数据分析"）
- [ ] 菜单显示 5 个顶级项目（包含报表分析子菜单）
- [ ] 所有 /client/* 路由可以正常访问
- [ ] 尝试访问 /admin/* 被重定向
- [ ] 控制台显示权限错误信息
- [ ] 设置页面显示 5 个权限
- [ ] 退出登录成功

### 菜单隔离测试
- [ ] Admin 看不到"📊 报表分析"菜单
- [ ] Customer 看不到"📥 数据导入"菜单
- [ ] 菜单高亮正确跟随当前路由

---

## 🐛 常见问题排查

### 问题 1：登录失败，显示"用户名或密码错误"

**解决方案**：
1. 确认输入正确：
   - Admin 用户：用户名 `admin`，密码 `admin`
   - Customer 用户：用户名 `customer`，密码 `customer`
2. 检查后端是否正常运行
3. 检查浏览器控制台是否有错误信息

### 问题 2：登录后页面一片空白

**解决方案**：
1. 刷新页面（F5）
2. 检查浏览器控制台（F12）是否有 JavaScript 错误
3. 检查 Network 标签是否有 API 调用失败
4. 确认后端服务正常运行

### 问题 3：路由不跳转，地址栏没变

**解决方案**：
1. 检查是否已登录（Local Storage 中有 `access_token`）
2. 刷新页面试试
3. 检查浏览器控制台是否有错误

### 问题 4：菜单项显示不正确

**解决方案**：
1. 刷新页面
2. 登出重新登录
3. 检查 auth store 中的 roles 和 permissions 是否正确

---

## 💡 进阶验证

### 使用 curl 测试后端权限

```bash
# 1. Admin 用户登录
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 2. 使用 Admin token 访问导入端点（应该成功）
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/import/batches

# 3. Customer 用户登录
CUSTOMER_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "customer", "password": "customer"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 4. 使用 Customer token 访问导入端点（应该返回 403 Forbidden）
curl -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  http://localhost:8000/api/v1/import/batches
```

**预期结果**：
- Admin 的请求返回 200 和导入批次列表
- Customer 的请求返回 403 和错误信息：`"detail": "Insufficient permissions. Required roles: admin"`

---

## 📝 测试结果记录

完成测试后，请记录以下内容：

- [ ] 测试日期：_______________
- [ ] 测试人员：_______________
- [ ] 测试环境：
  - 前端地址：http://localhost:3000
  - 后端地址：http://localhost:8000
  - 浏览器：_______________
- [ ] Admin 用户测试：✅ 通过 / ❌ 失败
- [ ] Customer 用户测试：✅ 通过 / ❌ 失败
- [ ] 菜单隔离测试：✅ 通过 / ❌ 失败
- [ ] 权限隔离测试：✅ 通过 / ❌ 失败
- [ ] 问题描述（如有）：_______________

---

## ✨ 总结

按照本指南逐步测试，应该能够验证：
1. ✅ 路由隔离正确实施
2. ✅ Admin 和 Customer 用户体验隔离
3. ✅ 权限检查生效
4. ✅ 菜单条件显示正确
5. ✅ 登录重定向逻辑正确

所有测试通过后，您可以放心地继续进行其他功能开发！

