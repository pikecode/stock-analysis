# 📊 报表功能实现方案

## 方案选择

**推荐方案：选项 A - 集成到现有后台管理系统**

- 单一系统，单一 URL: `http://localhost:3000/reports`
- 统一的导航、认证、权限管理
- 快速开发（2-4 周）
- 低维护成本

---

## 1. 整体架构

### 1.1 前端架构

```
frontend/
├── src/
│   ├── views/
│   │   └── reports/                    # 📊 报表模块（新增）
│   │       ├── Dashboard.vue           # 报表总览/仪表板
│   │       ├── ConceptStockRanking.vue # 概念内股票排名
│   │       ├── StockConceptTrend.vue   # 股票概念趋势
│   │       └── StockTopNAnalysis.vue   # 股票 Top N 分析
│   │
│   ├── components/
│   │   └── reports/                    # 📊 报表共享组件（新增）
│   │       ├── ChartCard.vue           # 图表卡片容器
│   │       ├── DataTable.vue           # 数据表格
│   │       ├── FilterPanel.vue         # 筛选面板
│   │       └── ExportButton.vue        # 导出按钮
│   │
│   └── api/
│       └── index.ts                    # 添加 reportApi
```

### 1.2 后端无需修改

已有的 API 端点完全满足报表需求：
- `GET /stocks/{stock_code}/concepts-ranked` ✅ 已实现
- `GET /rankings/concept/{concept_id}/stocks-in-range` ✅ 已实现
- `GET /rankings/stock/{stock_code}` ✅ 已存在
- `GET /rankings/stock/{stock_code}/top-n-count` ✅ 已存在

---

## 2. 报表功能模块设计

### 2.1 Dashboard（报表总览）

**功能**：整合所有报表的主入口

**组成**：
- 概览卡片：显示数据统计摘要
- 快速查询：常用查询快捷按钮
- 最近查询历史（可选）
- 链接到其他报表模块

**预估工作量**：0.5 天

---

### 2.2 Concept Stock Ranking（概念内股票排名报表）

**使用 API**：`GET /rankings/concept/{concept_id}/stocks-in-range`

**功能**：
- 选择概念 ID、日期范围、指标代码
- 查询该概念下的股票排名
- 两种查询模式：
  - **最新日期模式**：显示范围内最新交易日的排名
  - **聚合模式**：显示范围内平均表现（最佳排名、平均交易值）

**UI 组件**：
- 筛选面板（概念 ID、开始日期、结束日期、指标、查询模式）
- 数据表格（股票代码、股票名称、排名、交易值、百分位）
- 排名变化柱状图（可选）
- 导出按钮（Excel、PDF）

**预估工作量**：1.5 天

---

### 2.3 Stock Concept Trend（股票概念趋势报表）

**使用 API**：`GET /stocks/{stock_code}/concepts-ranked`

**功能**：
- 输入股票代码、选择交易日期、指标代码
- 显示该股票所属的所有概念及其排名
- 按交易值从高到低排序

**UI 组件**：
- 股票搜索框或代码输入
- 日期选择器、指标选择器
- 概念列表表格（概念名称、交易值、排名、百分位）
- 概念分布饼图（可选）
- 导出按钮

**预估工作量**：1.5 天

---

### 2.4 Stock Top N Analysis（股票 Top N 分析报表）

**使用 API**：`GET /rankings/stock/{stock_code}/top-n-count`

**功能**：
- 输入股票代码、日期范围、Top N 阈值
- 显示该股票在各个概念中出现在 Top N 的次数及比例
- 识别股票的"热门概念"

**UI 组件**：
- 筛选面板（股票代码、日期范围、Top N 值）
- 概念排行表格（概念名称、Top N 出现次数、占比）
- 概念热度柱状图（可选）
- 导出按钮

**预估工作量**：1 天

---

## 3. 前端技术细节

### 3.1 组件库使用

已在 `package.json` 中安装：
- **ECharts + Vue-ECharts**：图表绘制
- **Element Plus**：UI 组件（表格、表单、对话框等）
- **dayjs**：日期处理

### 3.2 图表类型选择

| 报表 | 主图表类型 | 辅助图表 |
|------|-----------|--------|
| Concept Stock Ranking | 表格 | 柱状图（排名变化） |
| Stock Concept Trend | 表格 | 饼图（概念分布） |
| Stock Top N Analysis | 表格 | 柱状图（概念热度） |

### 3.3 共享组件

已规划的可复用组件：

**ChartCard.vue**
- 图表卡片容器
- Props：title, subtitle, loading, height
- 使用：包装所有图表

**DataTable.vue**
- 通用数据表格
- Props：data, columns, loading, maxHeight
- 使用：所有报表的表格展示

**FilterPanel.vue**
- 筛选面板
- Props：showConceptId, showStockCode, showTopN, loading
- 使用：所有报表的查询条件

**ExportButton.vue**（新增）
- 导出功能
- 支持：Excel、PDF、CSV
- 使用：所有报表

---

## 4. 导航集成

### 4.1 修改 MainLayout.vue

在菜单中添加报表菜单项：

```vue
<el-menu-item index="/reports">
  <el-icon><DataAnalysis /></el-icon>
  <span>📊 报表</span>
</el-menu-item>
```

或作为子菜单：

```vue
<el-sub-menu index="/reports">
  <template #title>
    <el-icon><DataAnalysis /></el-icon>
    <span>📊 报表</span>
  </template>
  <el-menu-item index="/reports">总览</el-menu-item>
  <el-menu-item index="/reports/concept-ranking">概念排名</el-menu-item>
  <el-menu-item index="/reports/stock-trend">股票趋势</el-menu-item>
  <el-menu-item index="/reports/top-n">Top N 分析</el-menu-item>
</el-sub-menu>
```

### 4.2 修改 router/index.ts

```typescript
{
  path: 'reports',
  name: 'Reports',
  component: () => import('@/views/reports/Dashboard.vue'),
  meta: { title: '报表总览' },
},
{
  path: 'reports/concept-ranking',
  name: 'ConceptStockRanking',
  component: () => import('@/views/reports/ConceptStockRanking.vue'),
  meta: { title: '概念股票排名' },
},
{
  path: 'reports/stock-trend',
  name: 'StockConceptTrend',
  component: () => import('@/views/reports/StockConceptTrend.vue'),
  meta: { title: '股票概念趋势' },
},
{
  path: 'reports/top-n',
  name: 'StockTopNAnalysis',
  component: () => import('@/views/reports/StockTopNAnalysis.vue'),
  meta: { title: 'Top N 分析' },
},
```

---

## 5. API 调用层设计

### 5.1 reportApi（新增到 api/index.ts）

```typescript
export const reportApi = {
  // 概念内股票排名
  getConceptStocksInRange(conceptId: number, params: {
    start_date: string
    end_date: string
    metric_code?: string
    limit?: number
    use_latest_date?: boolean
  }) {
    return request.get(`/rankings/concept/${conceptId}/stocks-in-range`, { params })
  },

  // 股票概念排名
  getStockConceptsRanked(stockCode: string, params: {
    trade_date: string
    metric_code?: string
  }) {
    return request.get(`/stocks/${stockCode}/concepts-ranked`, { params })
  },

  // 股票 Top N 出现次数
  getStockTopNCount(stockCode: string, params: {
    start_date: string
    end_date: string
    top_n?: number
    concept_id?: number
    metric_code?: string
  }) {
    return request.get(`/rankings/stock/${stockCode}/top-n-count`, { params })
  },

  // 股票排名历史
  getStockRankingHistory(stockCode: string, params: {
    concept_id: number
    start_date: string
    end_date: string
    metric_code?: string
  }) {
    return request.get(`/rankings/stock/${stockCode}`, { params })
  },
}
```

---

## 6. 数据导出功能

### 6.1 ExportButton 组件

```vue
<el-button-group>
  <el-button type="success" @click="exportExcel">
    <el-icon><Download /></el-icon>
    Excel
  </el-button>
  <el-button type="success" @click="exportCSV">
    <el-icon><Download /></el-icon>
    CSV
  </el-button>
  <el-button type="success" @click="exportPDF">
    <el-icon><Download /></el-icon>
    PDF
  </el-button>
</el-button-group>
```

### 6.2 导出依赖库

需要添加到 package.json：
- `xlsx`：Excel 导出
- `pdfmake`：PDF 导出
- `html2canvas`：截图导出（可选）

安装命令：
```bash
npm install xlsx pdfmake html2canvas
```

---

## 7. 开发计划（分阶段）

### Phase 1：基础设施（1 天）
- [ ] 创建报表目录结构
- [ ] 创建共享组件（ChartCard、DataTable、FilterPanel）
- [ ] 添加 reportApi 到 API 层
- [ ] 更新路由配置
- [ ] 更新导航菜单

### Phase 2：Dashboard（0.5 天）
- [ ] 创建 Dashboard.vue
- [ ] 设计总览界面
- [ ] 添加快速导航

### Phase 3：Concept Stock Ranking（1.5 天）
- [ ] 创建 ConceptStockRanking.vue
- [ ] 实现两种查询模式
- [ ] 集成表格展示
- [ ] 添加可选的排名变化图表
- [ ] 实现导出功能

### Phase 4：Stock Concept Trend（1.5 天）
- [ ] 创建 StockConceptTrend.vue
- [ ] 实现股票搜索和概念查询
- [ ] 集成表格和饼图
- [ ] 实现导出功能

### Phase 5：Stock Top N Analysis（1 天）
- [ ] 创建 StockTopNAnalysis.vue
- [ ] 实现 Top N 统计
- [ ] 集成表格和柱状图
- [ ] 实现导出功能

### Phase 6：测试和优化（1 天）
- [ ] 功能测试
- [ ] 性能优化
- [ ] UI/UX 优化
- [ ] 响应式设计调整

**总计：6-7 天**

---

## 8. 技术选型对比

| 方面 | 当前方案 | 说明 |
|------|--------|------|
| 图表库 | ECharts | ✅ 已安装，功能强大 |
| UI 框架 | Element Plus | ✅ 已安装，用户熟悉 |
| 部署 | 单一前端项目 | ✅ 简单，与现有系统无缝集成 |
| 开发速度 | 快 | ✅ 复用现有组件和认证 |
| 维护成本 | 低 | ✅ 单个代码库，一套部署流程 |
| 未来升级 | 可升级到 Option B | ✅ 有清晰的迁移路径 |

---

## 9. 关键决策点

### 9.1 图表数据刷新策略

**推荐方案**：按需查询（用户点击查询按钮后获取）

- 优点：数据实时，不占用前端资源
- 缺点：需要等待 API 响应

**替代方案**：自动轮询（每 30 秒刷新一次）

- 优点：数据更新及时
- 缺点：增加服务器负载

### 9.2 表格行数限制

**推荐方案**：limit 默认 100，最多 500

- 理由：平衡性能和数据完整性

### 9.3 日期范围限制

**推荐方案**：最多查询 1 年内数据（365 天）

- 理由：避免大数据量导致查询缓慢

### 9.4 导出文件格式

**推荐**：
1. Excel（.xlsx）- 主要格式，便于后续分析
2. CSV（.csv）- 通用格式
3. PDF（.pdf）- 报告分享

---

## 10. 成功标准

✅ 实现完成的标准：

- [ ] 所有报表页面都能正常加载
- [ ] API 调用成功且返回预期数据
- [ ] 表格数据正确显示和排序
- [ ] 图表正确渲染和交互
- [ ] 导出功能正常工作
- [ ] 响应式设计适配各种屏幕
- [ ] 用户体验流畅，加载速度 < 2 秒
- [ ] 与现有系统（股票、概念、导入）导航流畅

---

## 总结

**推荐方案**：选项 A（集成到后台管理）

**核心优势**：
- ✅ 快速实现（6-7 天）
- ✅ 统一用户体验
- ✅ 低维护成本
- ✅ 清晰的升级路径
- ✅ 充分利用现有基础设施

**何时升级到 Option B**：
- 报表功能需求大幅增加
- 需要专业 BI 工具集成（Metabase）
- 用户量和数据量大幅增长
- 需要支持复杂的自定义报表

---

**确认问题**：
1. ✅ 同意这个整体方案吗？
2. ✅ 是否需要调整任何报表功能？
3. ✅ 导出格式是否满足需求？
4. ✅ 是否需要添加或删除任何报表类型？
