<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { conceptApi, rankingApi, importApi } from '@/api'
import type { Concept, RankingItem, MetricType, StockRankingHistory } from '@/types'
import * as echarts from 'echarts'

const router = useRouter()
const loading = ref(false)
const concepts = ref<Concept[]>([])
const metrics = ref<MetricType[]>([])
const rankings = ref<RankingItem[]>([])
const stockHistory = ref<StockRankingHistory[]>([])
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

// Search mode: concept ranking or stock history
const mode = ref<'concept' | 'stock'>('concept')

const conceptParams = ref({
  concept_id: undefined as number | undefined,
  trade_date: new Date().toISOString().slice(0, 10),
  metric_code: '',
  limit: 20,
})

const stockParams = ref({
  stock_code: '',
  concept_id: undefined as number | undefined,
  start_date: '',
  end_date: '',
  metric_code: '',
})

const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  stockParams.value.start_date = start.toISOString().slice(0, 10)
  stockParams.value.end_date = end.toISOString().slice(0, 10)
}

const fetchConcepts = async () => {
  try {
    const res = await conceptApi.getList({ page_size: 1000 })
    concepts.value = res.items
  } catch {
    concepts.value = []
  }
}

const fetchMetrics = async () => {
  try {
    metrics.value = await importApi.getMetrics()
    if (metrics.value.length) {
      conceptParams.value.metric_code = metrics.value[0].code
      stockParams.value.metric_code = metrics.value[0].code
    }
  } catch {
    metrics.value = []
  }
}

const fetchConceptRanking = async () => {
  if (!conceptParams.value.concept_id) return
  loading.value = true
  try {
    const res = await rankingApi.getConceptRanking(conceptParams.value.concept_id, {
      trade_date: conceptParams.value.trade_date,
      metric_code: conceptParams.value.metric_code,
      limit: conceptParams.value.limit,
    })
    rankings.value = res.rankings
  } finally {
    loading.value = false
  }
}

const fetchStockHistory = async () => {
  if (!stockParams.value.stock_code || !stockParams.value.concept_id) return
  loading.value = true
  try {
    const res = await rankingApi.getStockHistory(stockParams.value.stock_code, {
      concept_id: stockParams.value.concept_id,
      start_date: stockParams.value.start_date,
      end_date: stockParams.value.end_date,
      metric_code: stockParams.value.metric_code,
    })
    stockHistory.value = res.history || []
    renderHistoryChart()
  } finally {
    loading.value = false
  }
}

const renderHistoryChart = () => {
  if (!chartRef.value || !stockHistory.value.length) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const dates = stockHistory.value.map(h => h.trade_date)
  const ranks = stockHistory.value.map(h => h.rank)
  const values = stockHistory.value.map(h => h.trade_value)

  chart.setOption({
    title: { text: `${stockParams.value.stock_code} 排名历史` },
    tooltip: { trigger: 'axis' },
    legend: { data: ['排名', '指标值'] },
    xAxis: { type: 'category', data: dates },
    yAxis: [
      { type: 'value', name: '排名', inverse: true },
      { type: 'value', name: '指标值' },
    ],
    series: [
      { name: '排名', type: 'line', data: ranks },
      { name: '指标值', type: 'bar', yAxisIndex: 1, data: values },
    ],
  })
}

const goToStock = (code: string) => {
  router.push(`/stocks/${code}`)
}

onMounted(async () => {
  initDateRange()
  await Promise.all([fetchConcepts(), fetchMetrics()])
})
</script>

<template>
  <div class="ranking-view">
    <div class="page-header">
      <h1 class="page-title">排名查询</h1>
    </div>

    <el-card>
      <el-tabs v-model="mode">
        <el-tab-pane label="概念排名" name="concept">
          <div class="search-form">
            <el-select
              v-model="conceptParams.concept_id"
              placeholder="选择概念"
              filterable
              style="width: 200px"
            >
              <el-option
                v-for="c in concepts"
                :key="c.id"
                :label="c.concept_name"
                :value="c.id"
              />
            </el-select>
            <el-date-picker
              v-model="conceptParams.trade_date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
            />
            <el-select v-model="conceptParams.metric_code" placeholder="指标" style="width: 120px">
              <el-option v-for="m in metrics" :key="m.code" :label="m.name" :value="m.code" />
            </el-select>
            <el-input-number v-model="conceptParams.limit" :min="5" :max="100" />
            <el-button type="primary" @click="fetchConceptRanking" :loading="loading">查询</el-button>
          </div>

          <el-table :data="rankings" stripe v-loading="loading">
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="stock_code" label="股票代码" width="120">
              <template #default="{ row }">
                <el-link type="primary" @click="goToStock(row.stock_code)">
                  {{ row.stock_code }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="stock_name" label="股票名称" />
            <el-table-column prop="trade_value" label="指标值">
              <template #default="{ row }">
                {{ row.trade_value?.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="percentile" label="百分位" width="100">
              <template #default="{ row }">
                {{ row.percentile ? (row.percentile * 100).toFixed(1) + '%' : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="个股历史排名" name="stock">
          <div class="search-form">
            <el-input v-model="stockParams.stock_code" placeholder="股票代码" style="width: 120px" />
            <el-select
              v-model="stockParams.concept_id"
              placeholder="选择概念"
              filterable
              style="width: 200px"
            >
              <el-option
                v-for="c in concepts"
                :key="c.id"
                :label="c.concept_name"
                :value="c.id"
              />
            </el-select>
            <el-date-picker
              v-model="stockParams.start_date"
              type="date"
              placeholder="开始日期"
              value-format="YYYY-MM-DD"
            />
            <el-date-picker
              v-model="stockParams.end_date"
              type="date"
              placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
            <el-select v-model="stockParams.metric_code" placeholder="指标" style="width: 120px">
              <el-option v-for="m in metrics" :key="m.code" :label="m.name" :value="m.code" />
            </el-select>
            <el-button type="primary" @click="fetchStockHistory" :loading="loading">查询</el-button>
          </div>

          <div ref="chartRef" class="chart-container"></div>

          <el-table :data="stockHistory" stripe max-height="300">
            <el-table-column prop="trade_date" label="日期" width="120" />
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="trade_value" label="指标值">
              <template #default="{ row }">
                {{ row.trade_value?.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="total_stocks" label="概念股票数" width="120" />
            <el-table-column prop="percentile" label="百分位" width="100">
              <template #default="{ row }">
                {{ row.percentile ? (row.percentile * 100).toFixed(1) + '%' : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
