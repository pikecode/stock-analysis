<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { reportApi } from '@/api'
import dayjs from 'dayjs'

interface ConceptRankedItem {
  id: number
  concept_name: string
  category?: string
  trade_value?: number
  rank?: number
  percentile?: number
}

interface QueryResult {
  stock_code: string
  stock_name: string
  trade_date: string
  metric_code: string
  total_concepts: number
  concepts: ConceptRankedItem[]
}

const searching = ref(false)
const searchCode = ref('')
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const metricCode = ref('EEE')
const queryResult = ref<QueryResult | null>(null)
const hasSearched = ref(false)

// 度量指标选项
const metricOptions = [
  { label: 'EEE - 行业活跃度', value: 'EEE' },
  { label: 'TTV - 交易交易量', value: 'TTV' },
  { label: 'TOP - Top指标', value: 'TOP' },
]

// 用于显示的数据
const stockInfo = computed(() => {
  if (!queryResult.value) return null
  return {
    code: queryResult.value.stock_code,
    name: queryResult.value.stock_name,
    date: queryResult.value.trade_date,
    conceptCount: queryResult.value.total_concepts,
  }
})

// 格式化日期显示
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY年MM月DD日')
}

// 格式化交易量（单位处理）
const formatTradeValue = (value?: number) => {
  if (value === null || value === undefined) return '-'
  if (value === 0) return '0'

  if (value >= 1e8) {
    return (value / 1e8).toFixed(2) + '亿'
  } else if (value >= 1e4) {
    return (value / 1e4).toFixed(2) + '万'
  } else {
    return value.toFixed(2)
  }
}

// 执行查询
const handleSearch = async () => {
  if (!searchCode.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  if (!selectedDate.value) {
    ElMessage.warning('请选择查询日期')
    return
  }

  searching.value = true
  hasSearched.value = true

  try {
    // 调用 API 获取股票下的概念（按交易量排序）
    const response = await reportApi.getStockConceptsRanked(
      searchCode.value.trim().toUpperCase(),
      {
        trade_date: selectedDate.value,
        metric_code: metricCode.value,
      }
    )

    queryResult.value = {
      stock_code: response.stock_code,
      stock_name: response.stock_name,
      trade_date: response.trade_date,
      metric_code: response.metric_code,
      total_concepts: response.total_concepts,
      concepts: response.concepts || [],
    }

    if (response.concepts && response.concepts.length > 0) {
      ElMessage.success(`找到 ${response.concepts.length} 个概念`)
    } else {
      ElMessage.info('该股票在该日期暂无关联概念数据')
    }
  } catch (error: any) {
    queryResult.value = null
    const errorMsg = error.response?.data?.detail || '查询失败，请检查股票代码和日期是否正确'
    ElMessage.error(errorMsg)
  } finally {
    searching.value = false
  }
}

// 回车键触发搜索
const handleKeyup = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleSearch()
  }
}

// 清除搜索结果
const clearSearch = () => {
  searchCode.value = ''
  selectedDate.value = dayjs().format('YYYY-MM-DD')
  metricCode.value = 'EEE'
  queryResult.value = null
  hasSearched.value = false
}

// 日期快捷选项
const handleToday = () => {
  selectedDate.value = dayjs().format('YYYY-MM-DD')
}

const handleYesterday = () => {
  selectedDate.value = dayjs().subtract(1, 'day').format('YYYY-MM-DD')
}

const handleLastWeek = () => {
  selectedDate.value = dayjs().subtract(7, 'day').format('YYYY-MM-DD')
}
</script>

<template>
  <div class="dashboard">
    <!-- 查询卡片 -->
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span class="title">🔍 股票概念查询（按交易量排序）</span>
        </div>
      </template>

      <!-- 查询表单 -->
      <div class="query-form">
        <!-- 第一行：股票代码 -->
        <div class="form-row">
          <el-input
            v-model="searchCode"
            placeholder="输入股票代码（如：600519）"
            size="large"
            clearable
            @keyup="handleKeyup"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- 第二行：日期和指标 -->
        <div class="form-row filters">
          <!-- 日期选择 -->
          <div class="date-selector">
            <label class="filter-label">📅 查询日期：</label>
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              size="large"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="flex: 1"
            />
          </div>

          <!-- 度量指标选择 -->
          <div class="metric-selector">
            <label class="filter-label">📊 度量指标：</label>
            <el-select
              v-model="metricCode"
              placeholder="选择指标"
              size="large"
              style="flex: 1"
            >
              <el-option
                v-for="option in metricOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </div>
        </div>

        <!-- 第三行：按钮 -->
        <div class="form-row buttons">
          <el-button
            type="primary"
            size="large"
            :loading="searching"
            @click="handleSearch"
            style="flex: 1"
          >
            查询
          </el-button>
          <el-button
            type="info"
            plain
            size="large"
            @click="clearSearch"
          >
            清空
          </el-button>
        </div>

        <!-- 快捷日期按钮 -->
        <div class="quick-date-buttons">
          <el-button link size="small" @click="handleToday">今天</el-button>
          <el-divider direction="vertical" />
          <el-button link size="small" @click="handleYesterday">昨天</el-button>
          <el-divider direction="vertical" />
          <el-button link size="small" @click="handleLastWeek">一周前</el-button>
        </div>
      </div>
    </el-card>

    <!-- 查询结果卡片 -->
    <el-card v-if="hasSearched" class="result-card">
      <template #header>
        <div class="card-header">
          <span class="title">📊 查询结果</span>
          <span v-if="queryResult" class="result-meta">
            {{ formatDate(queryResult.trade_date) }} | {{ metricCode }} 指标
          </span>
        </div>
      </template>

      <div v-if="queryResult" class="result-content">
        <!-- 股票信息 -->
        <div class="stock-info">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ stockInfo?.code }}</span>
            </div>
            <div class="info-item">
              <span class="label">股票名称：</span>
              <span class="value">{{ stockInfo?.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">查询日期：</span>
              <span class="value">{{ formatDate(stockInfo?.date || '') }}</span>
            </div>
            <div class="info-item">
              <span class="label">概念数量：</span>
              <el-tag type="success">{{ stockInfo?.conceptCount }}</el-tag>
            </div>
          </div>
        </div>

        <!-- 概念列表 -->
        <div v-if="queryResult.concepts.length > 0" class="concepts-section">
          <h3>概念列表（按 {{ metricCode }} 交易量从高到低排序）</h3>
          <el-table
            :data="queryResult.concepts"
            stripe
            style="width: 100%"
            :default-sort="{ prop: 'trade_value', order: 'descending' }"
          >
            <el-table-column prop="concept_name" label="概念名称" min-width="150" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column
              prop="trade_value"
              label="交易量"
              width="150"
              align="center"
              sortable="custom"
            >
              <template #default="{ row }">
                <span v-if="row.trade_value" class="trade-value-highlight">
                  {{ formatTradeValue(row.trade_value) }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="rank" label="排名" width="100" align="center">
              <template #default="{ row }">
                <span v-if="row.rank">
                  <el-tag v-if="row.rank <= 3" type="danger">#{{ row.rank }}</el-tag>
                  <el-tag v-else type="info">#{{ row.rank }}</el-tag>
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="percentile" label="百分位" width="120" align="center">
              <template #default="{ row }">
                <span v-if="row.percentile !== null && row.percentile !== undefined">
                  {{ (row.percentile * 100).toFixed(1) }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="concept_total_value" label="概念总交易量" min-width="140" align="center">
              <template #default="{ row }">
                <span v-if="row.concept_total_value">
                  {{ formatTradeValue(row.concept_total_value) }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="concept_stock_count" label="概念股票数" width="110" align="center">
              <template #default="{ row }">
                <span v-if="row.concept_stock_count">
                  <el-tag>{{ row.concept_stock_count }}</el-tag>
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="concept_avg_value" label="概念平均交易量" min-width="140" align="center">
              <template #default="{ row }">
                <span v-if="row.concept_avg_value">
                  {{ formatTradeValue(row.concept_avg_value) }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 数据说明 -->
          <div class="data-tips">
            <el-alert type="info" :closable="false">
              <template #title>
                <div class="tips-content">
                  <p><strong>数据说明：</strong></p>
                  <ul>
                    <li><strong>交易量：</strong>该股票在该概念下的 {{ metricCode }} 指标值</li>
                    <li><strong>排名：</strong>该概念在该股票、该日期、该指标下的排名位次</li>
                    <li><strong>百分位：</strong>该概念在所有概念中的相对排名（0-1）</li>
                    <li><strong>概念总交易量：</strong>该概念在该日期、该指标下所有股票的总交易量</li>
                    <li><strong>概念股票数：</strong>该概念包含的股票数量</li>
                    <li><strong>概念平均交易量：</strong>该概念在该日期、该指标下的平均交易量（总交易量 ÷ 股票数）</li>
                  </ul>
                </div>
              </template>
            </el-alert>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="该股票在该日期暂无关联概念数据" />
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-else class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0;
}

/* 查询卡片 */
.query-card {
  margin-bottom: 20px;
}

.query-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-row.filters {
  gap: 20px;
  flex-wrap: wrap;
}

.date-selector,
.metric-selector {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
  min-width: 280px;
}

.filter-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.date-selector :deep(.el-date-picker),
.metric-selector :deep(.el-select) {
  width: 100%;
}

.form-row.buttons {
  justify-content: flex-start;
  gap: 12px;
}

.form-row.buttons :deep(.el-button) {
  min-width: 120px;
}

.quick-date-buttons {
  padding: 8px 0;
  text-align: center;
  border-top: 1px solid #ebeef5;
  margin-top: 8px;
}

.quick-date-buttons :deep(.el-button) {
  font-size: 13px;
  padding: 6px 8px;
}

/* 结果卡片 */
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 16px;
}

.title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.result-meta {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 4px;
}

/* 结果内容 */
.result-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stock-info {
  background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.value {
  color: #303133;
  font-size: 14px;
}

/* 概念表格 */
.concepts-section {
  margin-top: 20px;
}

.concepts-section h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.trade-value-highlight {
  color: #f56c6c;
  font-weight: bold;
  font-size: 14px;
}

.data-tips {
  margin-top: 16px;
}

.tips-content {
  font-size: 13px;
  line-height: 1.8;
  color: #606266;
}

.tips-content p {
  margin: 0 0 8px 0;
}

.tips-content ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
  list-style: disc;
}

.tips-content li {
  margin: 4px 0;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.loading-state {
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row.filters {
    flex-direction: column;
    gap: 12px;
  }

  .date-selector,
  .metric-selector {
    flex-direction: column;
    align-items: flex-start;
    min-width: 100%;
  }

  .filter-label {
    min-width: auto;
  }

  .date-selector :deep(.el-date-picker),
  .metric-selector :deep(.el-select) {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .label {
    min-width: auto;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .result-meta {
    font-size: 12px;
    margin-left: 0;
  }

  :deep(.el-table) {
    font-size: 13px;
  }

  :deep(.el-table__header th) {
    padding: 8px !important;
  }

  :deep(.el-table__body td) {
    padding: 8px !important;
  }
}

@media (max-width: 1024px) {
  .form-row.filters {
    flex-wrap: wrap;
  }

  .date-selector,
  .metric-selector {
    flex: 1;
    min-width: 200px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) {
  .form-row.buttons {
    width: 300px;
  }
}
</style>
