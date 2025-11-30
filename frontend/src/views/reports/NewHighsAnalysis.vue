<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import * as echarts from 'echarts'

interface ConceptData {
  concept_id: number
  concept_name: string
  total_trade_value: number
  daily_rank: number
  is_new_high: boolean
  stocks: StockData[]
}

interface StockData {
  code: string
  name: string
  trade_value: number
  price_change_pct: number
  rank: number
}

interface TrendData {
  date: string
  trade_value: number
  is_peak: boolean
}

const dateRange = ref<[Date, Date] | null>(null)
const days = ref(10)
const loading = ref(false)
const results = ref<ConceptData[]>([])
const expandedRows = ref<Set<number>>(new Set())
const isMobile = ref(false)

// Chart dialog state
const chartDialogVisible = ref(false)
const selectedConcept = ref<ConceptData | null>(null)
const trendData = ref<TrendData[]>([])
const chartLoading = ref(false)
const chartContainer = ref<HTMLDivElement>()

// Responsive dialog width
const dialogWidth = computed(() => {
  if (isMobile.value) return '95vw'
  if (window.innerWidth < 1200) return '85vw'
  return '80vw'
})

// Lifecycle
onMounted(() => {
  isMobile.value = window.innerWidth < 768
  window.addEventListener('resize', handleWindowResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize)
})

const handleWindowResize = () => {
  isMobile.value = window.innerWidth < 768
}

const pickerOptions = {
  shortcuts: [
    {
      text: '最近7天',
      value: () => {
        const end = new Date()
        const start = new Date()
        start.setDate(start.getDate() - 7)
        return [start, end]
      },
    },
    {
      text: '最近10天',
      value: () => {
        const end = new Date()
        const start = new Date()
        start.setDate(start.getDate() - 10)
        return [start, end]
      },
    },
    {
      text: '最近30天',
      value: () => {
        const end = new Date()
        const start = new Date()
        start.setDate(start.getDate() - 30)
        return [start, end]
      },
    },
  ],
}

const handleSearch = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期区间')
    return
  }

  loading.value = true
  try {
    const [startDate, endDate] = dateRange.value
    const response = await axios.get('/api/v1/reports/concept-new-highs', {
      params: {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        days: days.value,
      },
    })

    results.value = response.data
    expandedRows.value.clear()
    if (response.data.length > 0) {
      ElMessage.success(`查询完成，共找到 ${response.data.length} 个创新高概念`)
    } else {
      ElMessage.info('未找到符合条件的创新高概念')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '查询失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  dateRange.value = null
  days.value = 10
  results.value = []
  expandedRows.value.clear()
  ElMessage.info('已清空查询条件和结果')
}

const handleQuickSelect = (daysCount: number) => {
  days.value = daysCount
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - daysCount)
  dateRange.value = [start, end]
}

const toggleExpand = (conceptId: number) => {
  if (expandedRows.value.has(conceptId)) {
    expandedRows.value.delete(conceptId)
  } else {
    expandedRows.value.add(conceptId)
  }
}

const formatValue = (value: number) => {
  if (value >= 1e8) {
    return (value / 1e8).toFixed(2) + '亿'
  }
  if (value >= 1e4) {
    return (value / 1e4).toFixed(2) + '万'
  }
  return value.toFixed(0)
}

const formatPercent = (value: number) => {
  return (value >= 0 ? '+' : '') + value.toFixed(2) + '%'
}

// Handle concept chart display
const handleConceptChartClick = async (concept: ConceptData) => {
  selectedConcept.value = concept
  chartDialogVisible.value = true
  chartLoading.value = true
  trendData.value = []

  try {
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请先选择日期区间')
      return
    }

    const [startDate, endDate] = dateRange.value
    const response = await axios.get(
      `/api/v1/reports/concept-trend/${concept.concept_id}`,
      {
        params: {
          start_date: startDate.toISOString().split('T')[0],
          end_date: endDate.toISOString().split('T')[0],
        },
      }
    )

    trendData.value = response.data

    // Wait for DOM to render, then initialize chart
    await nextTick()
    initChart()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载趋势数据失败')
  } finally {
    chartLoading.value = false
  }
}

const initChart = () => {
  if (!chartContainer.value) return

  const chart = echarts.init(chartContainer.value)

  const dates = trendData.value.map((d) => d.date)
  const values = trendData.value.map((d) => d.trade_value)
  const peakIndex = trendData.value.findIndex((d) => d.is_peak)

  // Prepare data items with special styling for peak day
  const dataItems = values.map((value, index) => {
    if (index === peakIndex) {
      return {
        value,
        itemStyle: {
          color: '#f56c6c', // Red for peak day
          borderColor: '#f56c6c',
        },
        symbolSize: isMobile.value ? 8 : 10,
      }
    }
    return value
  })

  // Responsive grid settings
  const gridConfig = isMobile.value
    ? { left: 45, right: 15, top: 50, bottom: 40, containLabel: true }
    : { left: 60, right: 30, top: 60, bottom: 50, containLabel: true }

  const option = {
    title: {
      text: '交易量趋势',
      left: 'center',
      textStyle: {
        color: '#303133',
        fontSize: isMobile.value ? 14 : 16,
        fontWeight: 600,
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: '#333',
      textStyle: {
        color: '#fff',
        fontSize: isMobile.value ? 11 : 12,
      },
      formatter: (params: any) => {
        if (params.length > 0) {
          const param = params[0]
          const isNewHigh = trendData.value[param.dataIndex]?.is_peak
          let html = `<div style="margin-bottom: 4px;">${param.axisValue}</div>`
          html += `<div>交易量: ${formatValue(param.value)}</div>`
          if (isNewHigh) {
            html += '<div style="color: #f56c6c; font-weight: bold; margin-top: 4px;">★ 创新高</div>'
          }
          return html
        }
        return ''
      },
    },
    grid: gridConfig,
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#d3d3d3',
        },
      },
      axisLabel: {
        color: '#606266',
        fontSize: isMobile.value ? 10 : 12,
        rotate: isMobile.value ? 30 : 45,
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#d3d3d3',
        },
      },
      axisLabel: {
        color: '#606266',
        fontSize: isMobile.value ? 10 : 12,
        formatter: (value: number) => formatValue(value),
      },
      splitLine: {
        lineStyle: {
          color: '#eaeaea',
        },
      },
    },
    series: [
      {
        name: '交易量',
        type: 'line',
        data: dataItems,
        smooth: true,
        itemStyle: {
          color: '#409eff',
          borderColor: '#409eff',
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(64, 158, 255, 0.3)',
              },
              {
                offset: 1,
                color: 'rgba(64, 158, 255, 0.1)',
              },
            ],
          },
        },
        lineStyle: {
          color: '#409eff',
          width: 2,
        },
        symbolSize: isMobile.value ? 6 : 8,
        showSymbol: true,
      },
    ],
  }

  chart.setOption(option)

  // Add resize listener
  const resizeHandler = () => {
    chart.resize()
  }
  window.addEventListener('resize', resizeHandler)

  // Store handler reference for cleanup
  ;(chart as any)._resizeHandler = resizeHandler
}

const closeChartDialog = () => {
  chartDialogVisible.value = false
  selectedConcept.value = null
  trendData.value = []
}
</script>

<template>
  <div class="new-highs-container">
    <!-- 查询面板 -->
    <el-card class="query-panel">
      <template #header>
        <div class="card-header">
          <span class="header-title">📊 创新高概念分析</span>
        </div>
      </template>

      <div class="query-form">
        <!-- 日期选择和快速选择在一行 -->
        <div class="form-row">
          <div class="form-group">
            <label>日期区间</label>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :picker-options="pickerOptions"
              class="date-picker"
            />
          </div>

          <div class="form-group">
            <label>快速选择</label>
            <div class="quick-select">
              <el-button
                v-for="d in [7, 10, 30]"
                :key="d"
                :type="days === d ? 'primary' : 'default'"
                size="small"
                @click="handleQuickSelect(d)"
              >
                {{ d }}天
              </el-button>
            </div>
          </div>
        </div>

        <!-- 查询和清空按钮 -->
        <div class="form-actions">
          <el-button type="primary" :loading="loading" @click="handleSearch" size="large">
            <el-icon><Search /></el-icon>
            <span>查询创新高</span>
          </el-button>
          <el-button v-if="results.length > 0" :disabled="loading" @click="handleReset" size="large">
            <el-icon><Delete /></el-icon>
            <span>清空</span>
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 结果展示 -->
    <el-card v-if="results.length > 0" class="results-panel">
      <template #header>
        <div class="card-header">
          <span class="header-title">🎯 发现 {{ results.length }} 个创新高概念</span>
        </div>
      </template>

      <div class="results-list">
        <div
          v-for="(concept, index) in results"
          :key="concept.concept_id"
          class="concept-item"
          :class="{ 'rank-top': index < 3 }"
        >
          <!-- 概念头部 -->
          <div class="concept-header" @click="toggleExpand(concept.concept_id)">
            <!-- 排名徽章 -->
            <div class="rank-medal" v-if="index < 3">
              <span v-if="index === 0" class="medal gold">🥇</span>
              <span v-else-if="index === 1" class="medal silver">🥈</span>
              <span v-else-if="index === 2" class="medal bronze">🥉</span>
            </div>
            <div v-else class="rank-number">{{ index + 1 }}</div>

            <div class="concept-content">
              <div class="concept-title">
                <span class="expand-icon" :class="{ expanded: expandedRows.has(concept.concept_id) }">
                  ▼
                </span>
                <span class="concept-name">{{ concept.concept_name }}</span>
                <el-tag type="success" size="small" class="new-high-tag">新高</el-tag>
              </div>
              <div class="concept-stats">
                <div class="stat-item">
                  <span class="stat-label">交易量</span>
                  <span class="stat-value">{{ formatValue(concept.total_trade_value) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">成分股</span>
                  <span class="stat-value">{{ concept.stocks.length }} 只</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 展开的股票列表 -->
          <transition name="expand">
            <div v-if="expandedRows.has(concept.concept_id)" class="stocks-container">
              <!-- 查看趋势图表按钮 -->
              <div class="trend-chart-btn-wrapper">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleConceptChartClick(concept)"
                >
                  📈 查看趋势图表
                </el-button>
              </div>

              <!-- PC 端表格视图 -->
              <div v-if="!isMobile" class="stocks-list-desktop">
                <div class="stocks-header">
                  <span class="col-code">代码</span>
                  <span class="col-name">名称</span>
                  <span class="col-trade">交易量</span>
                  <span class="col-change">涨跌幅</span>
                  <span class="col-rank">排名</span>
                </div>

                <div v-for="stock in concept.stocks" :key="stock.code" class="stock-row">
                  <span class="col-code">{{ stock.code }}</span>
                  <span class="col-name">{{ stock.name }}</span>
                  <span class="col-trade">{{ formatValue(stock.trade_value) }}</span>
                  <span
                    class="col-change"
                    :class="{ positive: stock.price_change_pct > 0, negative: stock.price_change_pct < 0 }"
                  >
                    {{ formatPercent(stock.price_change_pct) }}
                  </span>
                  <span class="col-rank">{{ stock.rank }}</span>
                </div>
              </div>

              <!-- 移动端卡片视图 -->
              <div v-else class="stocks-list-mobile">
                <div v-for="(stock, index) in concept.stocks" :key="stock.code" class="stock-card">
                  <div class="card-rank">第 {{ index + 1 }} 名</div>
                  <div class="card-body">
                    <div class="stock-info">
                      <div class="stock-code">{{ stock.code }}</div>
                      <div class="stock-name">{{ stock.name }}</div>
                    </div>
                    <div class="stock-metrics">
                      <div class="metric-item">
                        <span class="metric-label">交易量</span>
                        <span class="metric-value">{{ formatValue(stock.trade_value) }}</span>
                      </div>
                      <div class="metric-item">
                        <span class="metric-label">涨跌</span>
                        <span
                          class="metric-value"
                          :class="{ positive: stock.price_change_pct > 0, negative: stock.price_change_pct < 0 }"
                        >
                          {{ formatPercent(stock.price_change_pct) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="concept.stocks.length === 0" class="empty-tips">
                暂无股票数据
              </div>
            </div>
          </transition>
        </div>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-card v-if="!loading && results.length === 0" class="empty-state-card">
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">开始查询创新高概念</div>
        <div class="empty-desc">选择日期区间，点击"查询创新高"按钮开始分析</div>
        <div class="empty-tips">
          <div class="tip-item">💡 建议使用最近 10-30 天的数据</div>
          <div class="tip-item">📈 数据每日更新，反映最新市场动态</div>
        </div>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <el-card v-if="loading" class="loading-state-card">
      <div class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
    </el-card>

    <!-- 趋势图表对话框 -->
    <el-dialog
      v-model="chartDialogVisible"
      :title="selectedConcept?.concept_name"
      :width="dialogWidth"
      :fullscreen="isMobile"
      class="chart-dialog"
      @close="closeChartDialog"
    >
      <div v-loading="chartLoading" class="chart-dialog-content">
        <div ref="chartContainer" class="chart-container"></div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.new-highs-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  min-height: 100vh;
}

.query-panel {
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.query-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 240px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  letter-spacing: 0.3px;
}

.date-picker {
  width: 100%;
}

.quick-select {
  display: flex;
  gap: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px dashed #e4e7ed;
}

.results-panel {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.concept-item {
  border: 2px solid #ebeef5;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
}

.concept-item:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.concept-item.rank-top {
  border-color: #ffd700;
  background: linear-gradient(135deg, #fff 0%, #fffbf0 100%);
}

.concept-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  cursor: pointer;
  transition: all 0.3s ease;
}

.concept-header:hover {
  background: linear-gradient(135deg, #eef2f8 0%, #f5f7fa 100%);
}

.rank-medal {
  font-size: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
}

.rank-number {
  font-size: 18px;
  font-weight: 700;
  color: #909399;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 8px;
  border: 2px solid #e4e7ed;
}

.concept-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.concept-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
  color: #909399;
  font-size: 10px;
  font-weight: bold;
}

.expand-icon.expanded {
  transform: rotate(-180deg);
}

.concept-name {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
}

.new-high-tag {
  margin-left: auto;
}

.concept-stats {
  display: flex;
  gap: 24px;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: #409eff;
}

.stocks-container {
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #ebeef5;
}

.trend-chart-btn-wrapper {
  margin-bottom: 16px;
  text-align: left;
}

.stocks-header {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1.2fr 1fr 0.8fr;
  gap: 12px;
  padding: 12px 0;
  font-weight: 600;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 8px;
}

.stock-row {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1.2fr 1fr 0.8fr;
  gap: 12px;
  padding: 12px 0;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  color: #606266;
}

.stock-row:last-child {
  border-bottom: none;
}

.col-code {
  font-weight: 600;
  color: #303133;
}

.col-name {
  color: #303133;
}

.col-change {
  text-align: right;
  font-weight: 500;
}

.col-change.positive {
  color: #f56c6c;
}

.col-change.negative {
  color: #67c23a;
}

.col-rank {
  text-align: center;
  color: #909399;
}

.col-trade,
.col-change,
.col-rank {
  text-align: right;
}

.empty-tips {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 扩展动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from {
  opacity: 0;
  max-height: 0;
}

.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.chart-dialog-content {
  width: 100%;
  min-height: 450px;
  padding: 0;
  margin: -20px -30px 0;
}

.chart-container {
  width: 100%;
  height: 450px;
}

/* 覆盖对话框默认样式 */
:deep(.chart-dialog .el-dialog__body) {
  padding: 0 !important;
}

.empty-state-card,
.loading-state-card {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 12px;
}

.empty-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 32px;
}

.empty-tips {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.tip-item {
  font-size: 13px;
  color: #909399;
  padding: 8px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.loading-state {
  padding: 30px 20px;
}

.form-btn-group {
  display: flex;
  gap: 8px !important;
  flex-wrap: wrap;
}

/* 移动端股票列表卡片 */
.stocks-list-mobile {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stock-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
  transition: all 0.2s ease;
}

.stock-card:active {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.card-rank {
  display: inline-block;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin: 8px;
}

.card-body {
  padding: 0 12px 12px;
}

.stock-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.stock-code {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  min-width: 60px;
}

.stock-name {
  font-size: 13px;
  color: #606266;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stock-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  font-weight: 500;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.metric-value.positive {
  color: #f56c6c;
}

.metric-value.negative {
  color: #67c23a;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .new-highs-container {
    padding: 12px;
  }

  .query-panel,
  .results-panel {
    margin-bottom: 16px;
    border-radius: 8px;
  }

  .header-title {
    font-size: 14px;
  }

  .form-row {
    flex-direction: column;
    gap: 16px;
  }

  .form-group {
    width: 100%;
    min-width: unset;
  }

  .form-group label {
    font-size: 12px;
  }

  .quick-select {
    width: 100%;
  }

  .quick-select .el-button {
    flex: 1;
  }

  .form-actions {
    flex-direction: column;
    gap: 8px;
  }

  .form-actions .el-button {
    width: 100%;
  }

  .results-list {
    gap: 12px;
  }

  .concept-item {
    border-radius: 8px;
  }

  .concept-header {
    flex-direction: row;
    padding: 12px;
    gap: 12px;
  }

  .rank-medal {
    font-size: 24px;
    width: 36px;
    height: 36px;
  }

  .rank-number {
    font-size: 14px;
    width: 36px;
    height: 36px;
    border-radius: 6px;
  }

  .concept-content {
    gap: 8px;
  }

  .concept-name {
    font-size: 15px;
  }

  .concept-stats {
    flex-direction: row;
    gap: 16px;
  }

  .stat-label {
    font-size: 11px;
  }

  .stat-value {
    font-size: 14px;
  }

  .trend-chart-btn-wrapper {
    margin-bottom: 12px;
  }

  .trend-chart-btn-wrapper .el-button {
    width: 100%;
  }

  .stocks-container {
    padding: 12px;
  }

  .stocks-list-desktop {
    overflow-x: auto;
  }

  .stocks-header,
  .stock-row {
    grid-template-columns: 0.8fr 1fr 1fr;
    gap: 6px;
    padding: 8px 0;
    font-size: 12px;
  }

  .col-code {
    grid-column: 1;
    font-size: 14px;
  }

  .col-name {
    grid-column: 2;
    font-size: 12px;
  }

  .col-trade {
    grid-column: 3;
  }

  .col-change,
  .col-rank {
    display: none;
  }

  .results-panel {
    margin-bottom: 12px;
  }

  .card-header {
    font-size: 14px;
  }

  .empty-state {
    padding: 40px 16px;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 16px;
    margin-bottom: 8px;
  }

  .empty-desc {
    font-size: 13px;
    margin-bottom: 24px;
  }

  .empty-tips {
    width: 100%;
  }

  .tip-item {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>
