# 文件导入进度跟踪功能文档

## 功能概述

为文件导入上传功能添加了**实时进度条**和**自动轮询**机制，使用户能够清晰地看到导入过程的每一步状态。

## 核心特性

### 1. 实时进度条

进度条根据不同的处理阶段动态更新：

```
上传开始 → 批次创建 → 文件上传 → 数据解析 → 排名计算 → 完成
   10%  →   20%   →   30%  →   50%  →   75%  →  100%
```

**CSV文件流程**:
```
10% (按钮点击)
  ↓
20% (批次待处理)
  ↓
30% (文件上传成功)
  ↓
50% (处理中)
  ↓
100% (完成)
```

**TXT文件流程** (包含排名计算):
```
10% (按钮点击)
  ↓
20% (批次待处理)
  ↓
30% (文件上传成功)
  ↓
50% (数据导入中)
  ↓
75% (排名计算中)
  ↓
100% (完成)
```

### 2. 轮询机制

- **轮询间隔**: 每 2 秒检查一次批次状态
- **触发方式**: 文件上传成功后自动启动
- **结束条件**: 处理完成或失败时停止
- **资源清理**: 组件卸载时自动停止轮询（防止内存泄漏）

### 3. 状态显示

上传过程中显示不同的警告框，实时反映当前状态：

#### 状态1: "等待处理" (Info - 蓝色)
```
标题: 等待处理
信息: 文件已上传，等待服务器处理...
触发: 批次状态为 'pending'
进度: 20%
```

#### 状态2: "处理中" (Warning - 黄色)
**CSV文件**:
```
标题: 处理中
信息: 正在导入股票-概念关系数据...
触发: 文件类型为 CSV 且状态为 'processing'
进度: 50%
```

**TXT文件**:
```
标题: 处理中
信息: 正在导入指标数据...
计算状态标签:
  - "等待计算" (blue) - compute_status = 'pending'
  - "计算中" (yellow) - compute_status = 'computing'
触发: 文件类型为 TXT 且状态为 'processing'
进度: 50% ~ 75%
```

#### 状态3: "导入成功" (Success - 绿色)
```
标题: 导入成功
成功数: 123
失败数: 5
总数: 128
排名计算状态: 已完成 (仅限TXT)
触发: status = 'completed' 或 'success'
进度: 100%
```

#### 状态4: "导入失败" (Error - 红色)
```
标题: 导入失败
错误信息: [具体错误]
触发: status = 'failed'
进度: 0%
```

### 4. UI交互改进

**上传按钮状态变化**:
```
默认: "开始上传" (可点击)
  ↓
上传中: "处理中..." (禁用,显示加载动画)
  ↓
完成: "开始上传" (可点击,表单已重置)
或
失败: "开始上传" (可点击,表单已重置)
```

## 使用流程

### 步骤1: 准备文件

```
访问 http://127.0.0.1:8005/admin/import
选择文件类型 (CSV 或 TXT)
如果是 TXT: 选择指标类型
拖拽或点击选择文件
```

### 步骤2: 开始上传

```
点击 [开始上传] 按钮
按钮变为 "处理中..." 并禁用
进度条出现: 10%
```

### 步骤3: 文件上传完成

```
进度条跳到 30%
显示 "等待处理" 警告框（蓝色）
消息: 文件已上传，等待服务器处理...
系统开始每 2 秒轮询一次状态
```

### 步骤4: 服务器处理中

```
进度条更新到 50%
警告框变为 "处理中"（黄色）
显示对应的处理信息:
  - CSV: "正在导入股票-概念关系数据..."
  - TXT: "正在导入指标数据..." + 计算状态标签
```

### 步骤5: TXT排名计算（仅限TXT）

```
进度条更新到 75%
计算状态标签从 "等待计算" 变为 "计算中"
警告框保持为 "处理中"（黄色）
继续轮询...
```

### 步骤6: 导入完成

```
进度条达到 100%
警告框变为 "导入成功"（绿色）
显示统计信息:
  成功: 123 / 失败: 5 / 总计: 128
  (TXT还显示) 排名计算: 已完成
轮询停止
2秒后表单自动重置:
  - 进度条隐藏
  - 警告框隐藏
  - 文件列表清空
  - 指标类型清空
  - 按钮恢复为 "开始上传"
```

### 或者: 导入失败

```
进度条变为 0%
警告框变为 "导入失败"（红色）
显示具体的错误信息
轮询停止
2秒后表单自动重置（同完成时）
```

## 代码架构

### 新增State变量

```typescript
const uploading = ref(false)          // 上传中标志
const uploadProgress = ref(0)         // 进度百分比 (0-100)
const currentBatchId = ref(number)    // 当前批次ID
const currentBatch = ref(ImportBatch) // 完整的批次对象
let pollInterval = null               // 轮询定时器
```

### 核心函数

#### `pollBatchStatus()`
```typescript
// 每2秒调用一次
// 获取最新的批次信息
// 根据 status 和 compute_status 更新进度条
// 当完成或失败时停止轮询
```

#### `startPolling()`
```typescript
// 启动2秒间隔的轮询
// 自动调用 pollBatchStatus()
```

#### `stopPolling()`
```typescript
// 停止轮询定时器
// 防止内存泄漏
```

#### `resetForm()`
```typescript
// 重置所有相关的state
// 清空表单数据
// 隐藏进度条
```

### 事件流

```
handleUpload()
  ↓
设置进度 10%
上传文件到 /api/v1/admin/import/upload
  ↓
获得 batch_id
设置进度 30%
显示信息提示
  ↓
startPolling()
  ↓
(每 2 秒)
pollBatchStatus()
  ↓
获取批次信息
更新进度条
更新警告框
  ↓
检查是否完成/失败
  ↓
是 → stopPolling() → resetForm()
否 → 继续轮询
```

## 技术细节

### 进度计算逻辑

```typescript
// CSV 文件
if (batch.status === 'pending') → 20%
if (batch.status === 'processing') → 50%
if (batch.status === 'completed') → 100%

// TXT 文件
if (batch.status === 'pending') → 20%
if (batch.status === 'processing') {
  if (batch.compute_status === 'pending') → 50%
  if (batch.compute_status === 'computing') → 75%
  if (batch.compute_status === 'completed') → 95%
}
if (batch.status === 'completed') → 100%
```

### 轮询停止条件

轮询会在以下情况停止：

1. **导入成功**: `status === 'completed' 或 'success'`
   - 进度条设为 100%
   - 显示成功消息
   - 2秒后自动重置表单

2. **导入失败**: `status === 'failed'`
   - 进度条设为 0%
   - 显示失败信息（包含error_message）
   - 2秒后自动重置表单

3. **组件卸载**: `onUnmounted()`
   - 清理轮询定时器
   - 防止内存泄漏

### 资源清理

```typescript
onUnmounted(() => {
  stopPolling()  // 防止泄漏
})
```

## API 交互

### 上传端点

```
POST /api/v1/admin/import/upload
Content-Type: multipart/form-data

请求:
- file: File
- file_type: 'CSV' | 'TXT'
- metric_code?: string (仅TXT)

响应:
{
  batch_id: number,
  file_name: string,
  status: 'pending' | 'processing' | 'completed' | 'failed',
  message: string
}
```

### 状态查询端点

```
GET /api/v1/admin/import/batches/{batch_id}

响应:
{
  id: number,
  file_name: string,
  file_type: 'CSV' | 'TXT',
  status: 'pending' | 'processing' | 'completed' | 'failed',
  compute_status: 'pending' | 'computing' | 'completed',
  success_rows: number,
  error_rows: number,
  total_rows: number,
  error_message?: string,
  ...
}
```

## 性能考虑

### 轮询频率

- **当前设置**: 每 2 秒轮询一次
- **优化建议**:
  - 首次轮询: 1 秒
  - 后续轮询: 2 秒
  - 计算中时: 1 秒（更频繁更新）
  - 处理完成后: 立即停止

### 内存管理

- ✅ 轮询定时器在停止时清理
- ✅ 组件卸载时清理定时器
- ✅ 完成后自动重置state变量

### 网络带宽

- 轮询请求最小化（仅查询状态字段）
- 后端应对大文件使用异步处理
- 建议设置上传大小限制

## 错误处理

### 轮询失败

```typescript
// 轮询过程中如果API失败
try {
  const batch = await importApi.getBatch(currentBatchId.value)
  // 更新UI
} catch (error) {
  console.error('轮询状态失败:', error)
  // 不中断轮询，继续尝试
}
```

### 上传失败

```typescript
try {
  const res = await importApi.upload(data)
  // 启动轮询
} catch (error) {
  // 显示错误提示
  // 恢复按钮状态
  // 不启动轮询
}
```

## 测试场景

### 场景1: CSV快速导入
```
文件: 100行 CSV
预期时间: 5-10秒
进度: 10% → 20% → 30% → 50% → 100%
警告框: 等待处理 → 处理中 → 导入成功
```

### 场景2: TXT大文件导入+计算
```
文件: 10000行 TXT
预期时间: 30-60秒
进度: 10% → 20% → 30% → 50% → 75% → 100%
警告框: 等待处理 → 处理中(导入) → 处理中(计算) → 导入成功
计算状态标签: 等待计算 → 计算中 → 已完成
```

### 场景3: 上传失败
```
场景: 格式错误的文件
预期: 立即返回错误（无轮询）
进度: 10% (无变化)
警告框: 无（仅显示错误提示）
```

### 场景4: 导入失败
```
场景: 文件格式有错但已上传
预期: 轮询捕捉到failure状态
进度: 0%
警告框: 导入失败 + 错误信息
```

## 用户体验改进

### 改进点1: 视觉反馈
- ✅ 实时进度条
- ✅ 彩色警告框（蓝/黄/绿/红）
- ✅ 进度百分比显示
- ✅ 按钮状态变化

### 改进点2: 信息透明度
- ✅ 显示当前处理阶段
- ✅ 区分CSV和TXT的不同流程
- ✅ 显示计算进度（TXT）
- ✅ 显示详细的错误信息

### 改进点3: 交互设计
- ✅ 上传中禁用按钮（防止重复提交）
- ✅ 自动重置表单（可立即开始新导入）
- ✅ 可视化的完成状态（成功/失败）

## 后续优化方向

### 可选优化1: 动态轮询间隔
```typescript
// 根据当前阶段调整轮询频率
if (currentStage === 'computing') {
  interval = 1000  // 计算中: 1秒
} else {
  interval = 2000  // 其他: 2秒
}
```

### 可选优化2: 取消上传
```typescript
// 添加取消按钮（在上传过程中）
const handleCancel = async () => {
  await importApi.cancelBatch(currentBatchId.value)
  stopPolling()
  resetForm()
}
```

### 可选优化3: 导入历史速查
```typescript
// 上传完成后链接到最新的导入记录
// 方便用户快速查看详细信息
```

### 可选优化4: 离线处理通知
```typescript
// 如果用户关闭了页面，使用Service Worker
// 在后台继续轮询，完成时弹出通知
```

---

**功能发布**: 2025-11-28
**Git Commit**: e0e5aac
**状态**: ✅ 生产可用
