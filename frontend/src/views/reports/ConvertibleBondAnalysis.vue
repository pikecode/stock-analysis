<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { reportApi, conceptApi } from '@/api'
import dayjs from 'dayjs'
import StockRankingChart from '@/components/StockRankingChart.vue'
import ConceptDailyTradeChart from '@/components/ConceptDailyTradeChart.vue'

interface ConceptRankedItem {
  id: number
  concept_name: string
  category?: string
  trade_value?: number
  rank?: number
  concept_total_value?: number
  concept_stock_count?: number
  concept_avg_value?: number
  stocks?: StockItem[]
  stocksLoading?: boolean
  stocksPage?: number
  stocksTotal?: number
  isExpanded?: boolean
  showChart?: boolean
  chartStartDate?: string
  chartEndDate?: string
  chartDateRange?: string[]
  showDailyTradeChart?: boolean
}

interface StockItem {
  id?: number
  stock_code: string
  stock_name: string
  exchange_prefix?: string
  trade_value?: number
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

// 当前选中的概念
const selectedConcept = ref<ConceptRankedItem | null>(null)

// 移动端折叠面板展开的概念 ID
const expandedConceptId = ref<number | null>(null)

// 图表日期范围
const chartStartDate = ref('')
const chartEndDate = ref('')
const chartDateRange = ref<string[]>([])

// 控制图表显示
const showRankingChart = ref(false)
const showDailyTradeChart = ref(false)

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
    ElMessage.warning('请输入转债代码')
    return
  }

  if (!searchCode.value.trim().startsWith('1')) {
    ElMessage.warning('转债代码必须以1开头')
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
      ElMessage.info('该转债在该日期暂无关联概念数据')
    }
  } catch (error: any) {
    queryResult.value = null
    const errorMsg = error.response?.data?.detail || '查询失败，请检查转债代码和日期是否正确'
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

// 切换展开/收起
const toggleExpand = async (concept: ConceptRankedItem) => {
  concept.isExpanded = !concept.isExpanded

  // 展开时加载股票数据
  if (concept.isExpanded && !concept.stocks) {
    await loadConceptStocks(concept)
  }
}

// 加载概念下的股票列表
const loadConceptStocks = async (concept: ConceptRankedItem) => {
  if (concept.stocks) {
    // 已加载过，直接返回
    return
  }

  concept.stocksLoading = true
  concept.stocksPage = 1
  concept.stocks = []

  try {
    const response = await conceptApi.getStocks(concept.id, {
      page: 1,
      page_size: 10,
      trade_date: selectedDate.value,
      metric_code: metricCode.value,
    })

    if (response && response.stocks) {
      concept.stocks = response.stocks
      concept.stocksTotal = response.total
      concept.stocksPage = 1
    }
  } catch (error: any) {
    ElMessage.error('加载股票列表失败')
    concept.stocks = []
  } finally {
    concept.stocksLoading = false
  }
}

// 加载更多股票
const loadMoreStocks = async (concept: ConceptRankedItem) => {
  if (!concept.stocks || !concept.stocksPage) {
    return
  }

  const nextPage = concept.stocksPage + 1

  try {
    const response = await conceptApi.getStocks(concept.id, {
      page: nextPage,
      page_size: 10,
      trade_date: selectedDate.value,
      metric_code: metricCode.value,
    })

    if (response && response.stocks) {
      concept.stocks = [...(concept.stocks || []), ...response.stocks]
      concept.stocksPage = nextPage
    }
  } catch (error: any) {
    ElMessage.error('加载更多股票失败')
  }
}

// 选择概念（新的三步骤布局）
const selectConcept = async (concept: ConceptRankedItem) => {
  selectedConcept.value = concept
  expandedConceptId.value = concept.id

  // 初始化图表日期范围：默认最近30天
  if (!chartStartDate.value) {
    const endDate = dayjs(selectedDate.value)
    const startDate = endDate.subtract(30, 'days')
    chartStartDate.value = startDate.format('YYYY-MM-DD')
    chartEndDate.value = endDate.format('YYYY-MM-DD')
    chartDateRange.value = [chartStartDate.value, chartEndDate.value]
  }

  // 默认显示排名趋势图
  showRankingChart.value = true
  showDailyTradeChart.value = false

  // 加载该概念下的股票列表
  if (!concept.stocks) {
    await loadConceptStocks(concept)
  }

  console.log('已选择概念:', {
    conceptId: concept.id,
    conceptName: concept.concept_name,
    chartDateRange: chartDateRange.value
  })
}

// 更新图表日期范围（新版本）
const updateChartDateRange = (dateRange: string[] | null) => {
  console.log('日期范围改变事件:', { dateRange })
  if (dateRange && dateRange.length === 2) {
    chartStartDate.value = dateRange[0]
    chartEndDate.value = dateRange[1]
    chartDateRange.value = [...dateRange]
    console.log('已更新图表日期范围:', {
      startDate: chartStartDate.value,
      endDate: chartEndDate.value,
      chartDateRange: chartDateRange.value
    })
  } else {
    console.log('日期范围为空或格式不正确:', dateRange)
  }
}

// 旧版本函数已移除，现在使用新的三步骤布局

// 监听移动端折叠面板的展开
watch(expandedConceptId, (newId) => {
  if (newId && queryResult.value) {
    const concept = queryResult.value.concepts.find(c => c.id === newId)
    if (concept) {
      selectConcept(concept)
    }
  }
})
</script>

<template>
  <div class="dashboard">
    <!-- 查询卡片 -->
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span class="title">🔍 转债概念查询（按交易量排序）</span>
        </div>
      </template>

      <!-- 查询表单 -->
      <div class="query-form">
        <!-- 第一行：转债代码 -->
        <div class="form-row">
          <el-input
            v-model="searchCode"
            placeholder="输入转债代码（如：123456，必须以1开头）"
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

        <!-- 新的三步骤布局：概念列表 + 概念详情 -->
        <div v-if="queryResult.concepts.length > 0" class="concepts-section-new">
          <!-- 桌面端：左右分栏布局 -->
          <el-row :gutter="20" class="desktop-layout">
            <!-- 第二步：概念列表（左侧） -->
            <el-col :xs="24" :sm="24" :md="10" :lg="8">
              <el-card class="concept-list-card" shadow="never">
                <template #header>
                  <div class="section-header">
                    <h3>📋 关联概念列表</h3>
                    <el-tag type="info" size="small">共 {{ queryResult.concepts.length }} 个</el-tag>
                  </div>
                </template>

                <div class="concept-list">
                  <div
                    v-for="concept in queryResult.concepts"
                    :key="concept.id"
                    class="concept-item"
                    :class="{ active: selectedConcept?.id === concept.id }"
                    @click="selectConcept(concept)"
                  >
                    <div class="concept-item-header">
                      <div class="concept-name">
                        <el-icon class="icon-check" v-if="selectedConcept?.id === concept.id">
                          <Check />
                        </el-icon>
                        {{ concept.concept_name }}
                      </div>
                      <el-tag v-if="concept.rank" :type="concept.rank <= 3 ? 'danger' : 'info'" size="small">
                        排名 #{{ concept.rank }}
                      </el-tag>
                    </div>
                    <div class="concept-item-meta">
                      <span class="meta-item">
                        总交易量: {{ formatTradeValue(concept.concept_total_value) }}
                      </span>
                      <span class="meta-item">
                        股票数: {{ concept.concept_stock_count }}
                      </span>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>

            <!-- 第三步：概念详情区域（右侧） -->
            <el-col :xs="24" :sm="24" :md="14" :lg="16">
              <el-card v-if="selectedConcept" class="concept-detail-card" shadow="never">
                <template #header>
                  <div class="section-header">
                    <h3>📊 {{ selectedConcept.concept_name }} - 详细信息</h3>
                    <el-button type="primary" size="small" @click="selectedConcept = null">
                      关闭
                    </el-button>
                  </div>
                </template>

                <!-- 概念基本信息 -->
                <div class="concept-basic-info">
                  <el-descriptions :column="2" border size="small">
                    <el-descriptions-item label="概念名称">
                      {{ selectedConcept.concept_name }}
                    </el-descriptions-item>
                    <el-descriptions-item label="排名">
                      <el-tag v-if="selectedConcept.rank" :type="selectedConcept.rank <= 3 ? 'danger' : 'info'">
                        #{{ selectedConcept.rank }}
                      </el-tag>
                      <span v-else>-</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="概念总交易量">
                      {{ formatTradeValue(selectedConcept.concept_total_value) }}
                    </el-descriptions-item>
                    <el-descriptions-item label="概念股票数">
                      {{ selectedConcept.concept_stock_count }}
                    </el-descriptions-item>
                    <el-descriptions-item label="概念平均交易量" :span="2">
                      {{ formatTradeValue(selectedConcept.concept_avg_value) }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>

                <!-- 股票列表 -->
                <div class="concept-stocks-section" style="margin-top: 20px;">
                  <h4 style="margin-bottom: 12px;">概念下的股票列表</h4>
                  <div v-if="selectedConcept.stocksLoading" class="loading">
                    <el-skeleton :rows="3" animated />
                  </div>
                  <div v-else-if="selectedConcept.stocks && selectedConcept.stocks.length > 0">
                    <el-table :data="selectedConcept.stocks" stripe size="small" max-height="300">
                      <el-table-column prop="stock_code" label="股票代码" width="100" />
                      <el-table-column prop="stock_name" label="股票名称" min-width="120" />
                      <el-table-column label="交易量" min-width="120" align="right">
                        <template #default="{ row }">
                          <span v-if="row.trade_value" class="trade-value-highlight">
                            {{ formatTradeValue(row.trade_value) }}
                          </span>
                          <span v-else>-</span>
                        </template>
                      </el-table-column>
                    </el-table>
                    <div v-if="selectedConcept.stocks.length < selectedConcept.stocksTotal" class="load-more-btn">
                      <el-button type="primary" link size="small" @click="loadMoreStocks(selectedConcept)">
                        加载更多（{{ selectedConcept.stocks.length }}/{{ selectedConcept.stocksTotal }}）
                      </el-button>
                    </div>
                  </div>
                  <div v-else class="empty-stocks">
                    暂无股票数据
                  </div>
                </div>

                <!-- 图表区域 -->
                <div class="concept-charts-section" style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #ebeef5;">
                  <h4 style="margin-bottom: 12px;">趋势图表</h4>

                  <!-- 日期范围选择器 -->
                  <div class="date-range-selector" style="margin-bottom: 16px;">
                    <label style="font-size: 13px; color: #606266; margin-right: 8px;">日期范围：</label>
                    <el-date-picker
                      v-model="chartDateRange"
                      type="daterange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      size="small"
                      clearable
                      @update:model-value="updateChartDateRange"
                    />
                  </div>

                  <!-- 图表切换按钮 -->
                  <div class="chart-toggles" style="margin-bottom: 12px;">
                    <el-checkbox v-model="showRankingChart" label="显示排名趋势图" border size="small" />
                    <el-checkbox v-model="showDailyTradeChart" label="显示每日交易总和" border size="small" style="margin-left: 12px;" />
                  </div>

                  <!-- 排名趋势图 -->
                  <div v-if="showRankingChart && queryResult && chartStartDate && chartEndDate" class="chart-wrapper">
                    <StockRankingChart
                      :concept-id="selectedConcept.id"
                      :concept-name="selectedConcept.concept_name"
                      :stock-code="queryResult.stock_code"
                      :stock-name="queryResult.stock_name"
                      :metric-code="metricCode"
                      :start-date="chartStartDate"
                      :end-date="chartEndDate"
                    />
                  </div>

                  <!-- 每日交易总和图表 -->
                  <div v-if="showDailyTradeChart && queryResult && chartStartDate && chartEndDate" class="chart-wrapper" style="margin-top: 16px;">
                    <ConceptDailyTradeChart
                      :concept-id="selectedConcept.id"
                      :concept-name="selectedConcept.concept_name"
                      :metric-code="metricCode"
                      :start-date="chartStartDate"
                      :end-date="chartEndDate"
                    />
                  </div>
                </div>
              </el-card>

              <!-- 未选择概念时的提示 -->
              <el-card v-else class="concept-detail-placeholder" shadow="never">
                <el-empty description="请从左侧选择一个概念查看详细信息" />
              </el-card>
            </el-col>
          </el-row>

          <!-- 移动端：折叠面板布局 -->
          <div class="mobile-layout">
            <el-card shadow="never">
              <template #header>
                <div class="section-header">
                  <h3>📋 关联概念列表</h3>
                  <el-tag type="info" size="small">共 {{ queryResult.concepts.length }} 个</el-tag>
                </div>
              </template>

              <el-collapse v-model="expandedConceptId" accordion>
                <el-collapse-item
                  v-for="concept in queryResult.concepts"
                  :key="concept.id"
                  :name="concept.id"
                >
                  <template #title>
                    <div class="mobile-concept-header">
                      <div class="mobile-concept-title">
                        <span class="concept-name-text">{{ concept.concept_name }}</span>
                        <el-tag v-if="concept.rank" :type="concept.rank <= 3 ? 'danger' : 'info'" size="small">
                          #{{ concept.rank }}
                        </el-tag>
                      </div>
                      <div class="mobile-concept-meta">
                        <span>总交易: {{ formatTradeValue(concept.concept_total_value) }}</span>
                        <span>股票数: {{ concept.concept_stock_count }}</span>
                      </div>
                    </div>
                  </template>

                  <!-- 折叠面板内容 -->
                  <div class="mobile-concept-detail">
                    <!-- 概念基本信息 -->
                    <el-descriptions :column="1" border size="small" style="margin-bottom: 16px;">
                      <el-descriptions-item label="概念名称">
                        {{ concept.concept_name }}
                      </el-descriptions-item>
                      <el-descriptions-item label="排名">
                        <el-tag v-if="concept.rank" :type="concept.rank <= 3 ? 'danger' : 'info'">
                          #{{ concept.rank }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="概念总交易量">
                        {{ formatTradeValue(concept.concept_total_value) }}
                      </el-descriptions-item>
                      <el-descriptions-item label="概念股票数">
                        {{ concept.concept_stock_count }}
                      </el-descriptions-item>
                    </el-descriptions>

                    <!-- 股票列表 -->
                    <div v-if="concept.stocks && concept.stocks.length > 0" style="margin-bottom: 16px;">
                      <h4 style="font-size: 13px; margin-bottom: 8px;">股票列表</h4>
                      <div
                        v-for="stock in concept.stocks.slice(0, 5)"
                        :key="stock.stock_code"
                        class="mobile-stock-item"
                      >
                        <div class="stock-info">
                          <span class="stock-code">{{ stock.stock_code }}</span>
                          <span class="stock-name">{{ stock.stock_name }}</span>
                        </div>
                        <div class="stock-value">
                          {{ formatTradeValue(stock.trade_value) }}
                        </div>
                      </div>
                      <el-button
                        v-if="!concept.stocks || concept.stocks.length === 0"
                        type="primary"
                        link
                        size="small"
                        @click.stop="loadConceptStocks(concept)"
                      >
                        加载股票列表
                      </el-button>
                    </div>

                    <!-- 图表区域 -->
                    <div class="mobile-charts">
                      <h4 style="font-size: 13px; margin-bottom: 8px;">趋势图表</h4>

                      <!-- 日期范围选择 -->
                      <el-date-picker
                        v-model="chartDateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始"
                        end-placeholder="结束"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        size="small"
                        style="width: 100%; margin-bottom: 12px;"
                        @update:model-value="updateChartDateRange"
                      />

                      <!-- 图表切换 -->
                      <div style="margin-bottom: 12px;">
                        <el-checkbox v-model="showRankingChart" size="small">排名趋势</el-checkbox>
                        <el-checkbox v-model="showDailyTradeChart" size="small" style="margin-left: 12px;">交易总和</el-checkbox>
                      </div>

                      <!-- 排名趋势图 -->
                      <div v-if="showRankingChart && queryResult && chartStartDate && chartEndDate" style="margin-bottom: 12px;">
                        <StockRankingChart
                          :concept-id="concept.id"
                          :concept-name="concept.concept_name"
                          :stock-code="queryResult.stock_code"
                          :stock-name="queryResult.stock_name"
                          :metric-code="metricCode"
                          :start-date="chartStartDate"
                          :end-date="chartEndDate"
                        />
                      </div>

                      <!-- 每日交易总和图表 -->
                      <div v-if="showDailyTradeChart && queryResult && chartStartDate && chartEndDate">
                        <ConceptDailyTradeChart
                          :concept-id="concept.id"
                          :concept-name="concept.concept_name"
                          :metric-code="metricCode"
                          :start-date="chartStartDate"
                          :end-date="chartEndDate"
                        />
                      </div>
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </el-card>
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

.concept-total-value-highlight {
  color: #409eff;
  font-weight: bold;
  font-size: 14px;
}

/* 展开行样式 */
.stock-list-container {
  padding: 16px 0;
  background: #f9fafc;
  border-radius: 4px;
}

.stock-list-container h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  padding: 0 16px;
}

.stocks-list {
  padding: 0 16px;
}

.load-more-btn {
  text-align: center;
  padding: 12px 0;
  margin-top: 12px;
  border-top: 1px solid #ebeef5;
}

.all-loaded {
  text-align: center;
  padding: 12px 0;
  margin-top: 12px;
  color: #909399;
  font-size: 12px;
}

.loading {
  padding: 16px;
  background: #f9fafc;
  border-radius: 4px;
}

.empty-stocks {
  text-align: center;
  padding: 20px;
  color: #909399;
}

/* 图表区域 */
.chart-section {
  padding: 16px 0;
  border-top: 1px solid #ebeef5;
  margin-top: 12px;
}

.chart-header {
  padding: 0 16px 12px 16px;
}

.chart-header :deep(.el-button) {
  font-size: 13px;
  padding: 6px 12px;
}

.chart-container {
  padding: 0 16px 16px 16px;
  background: #f9fafc;
  border-radius: 4px;
}

.date-range-selector {
  padding: 12px 0;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.date-range-selector label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.date-range-selector :deep(.el-date-picker) {
  width: 100%;
  max-width: 400px;
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

/* 嵌套表格样式 */
:deep(.stock-list-container .el-table) {
  background: transparent !important;
  border: none;
}

:deep(.stock-list-container .el-table__header th) {
  background-color: #f5f7fa !important;
  border-top: 1px solid #ebeef5 !important;
  border-bottom: 1px solid #ebeef5 !important;
}

:deep(.stock-list-container .el-table__row) {
  background-color: transparent !important;
}

:deep(.stock-list-container .el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 新的三步骤布局样式 */
.concepts-section-new {
  margin-top: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.section-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* 概念列表卡片 */
.concept-list-card {
  height: 100%;
}

.concept-list {
  max-height: 600px;
  overflow-y: auto;
}

.concept-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fff;
}

.concept-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.concept-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.concept-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.concept-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-check {
  color: #67c23a;
  font-size: 16px;
}

.concept-item-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.meta-item {
  display: flex;
  align-items: center;
}

/* 概念详情卡片 */
.concept-detail-card {
  height: 100%;
  min-height: 600px;
}

.concept-detail-placeholder {
  height: 100%;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.concept-basic-info {
  margin-bottom: 16px;
}

.concept-stocks-section {
  margin-top: 20px;
}

.concept-stocks-section h4,
.concept-charts-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.chart-toggles {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-wrapper {
  background: #fafafa;
  border-radius: 4px;
  padding: 12px;
}

/* 桌面端和移动端布局切换 */
.desktop-layout {
  display: flex;
}

.mobile-layout {
  display: none;
}

/* 移动端折叠面板样式 */
.mobile-concept-header {
  width: 100%;
  padding: 4px 0;
}

.mobile-concept-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.concept-name-text {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.mobile-concept-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.mobile-concept-detail {
  padding: 12px 0;
}

.mobile-stock-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.stock-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.stock-code {
  font-size: 12px;
  font-weight: 500;
  color: #303133;
}

.stock-name {
  font-size: 12px;
  color: #606266;
}

.stock-value {
  font-size: 12px;
  font-weight: 500;
  color: #f56c6c;
}

.mobile-charts {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  /* 隐藏桌面端布局 */
  .desktop-layout {
    display: none !important;
  }

  /* 显示移动端布局 */
  .mobile-layout {
    display: block;
  }

  .concept-list {
    max-height: 400px;
  }

  .concept-detail-card,
  .concept-detail-placeholder {
    min-height: 400px;
  }

  .chart-toggles {
    flex-direction: column;
  }

  .chart-toggles :deep(.el-checkbox) {
    margin-left: 0 !important;
    margin-top: 8px;
  }

  /* 移动端图表优化 */
  .mobile-charts :deep(.chart-wrapper) {
    padding: 8px;
  }

  .mobile-charts :deep(.el-checkbox) {
    display: block;
    margin-bottom: 8px;
  }
}

@media (min-width: 769px) {
  /* 确保桌面端显示正确 */
  .desktop-layout {
    display: flex !important;
  }

  .mobile-layout {
    display: none !important;
  }
}
</style>
