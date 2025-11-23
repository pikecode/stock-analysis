<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { conceptApi, rankingApi, summaryApi, importApi } from '@/api'
import type { Concept, RankingItem, DailySummary, MetricType } from '@/types'
import { ArrowLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const concept = ref<Concept | null>(null)
const rankings = ref<RankingItem[]>([])
const summaries = ref<DailySummary[]>([])
const metrics = ref<MetricType[]>([])
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const conceptId = computed(() => Number(route.params.id))

const searchParams = ref({
  trade_date: new Date().toISOString().slice(0, 10),
  metric_code: 'TTV',
  limit: 20,
})

const dateRange = ref<[string, string]>(['', ''])

const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  dateRange.value = [
    start.toISOString().slice(0, 10),
    end.toISOString().slice(0, 10),
  ]
}

const fetchConcept = async () => {
  loading.value = true
  try {
    concept.value = await conceptApi.getDetail(conceptId.value)
  } finally {
    loading.value = false
  }
}

const fetchMetrics = async () => {
  try {
    metrics.value = await importApi.getMetrics()
    if (metrics.value.length && !searchParams.value.metric_code) {
      searchParams.value.metric_code = metrics.value[0].code
    }
  } catch {
    metrics.value = []
  }
}

const fetchRankings = async () => {
  try {
    const res = await rankingApi.getConceptRanking(conceptId.value, {
      trade_date: searchParams.value.trade_date,
      metric_code: searchParams.value.metric_code,
      limit: searchParams.value.limit,
    })
    rankings.value = res.rankings
  } catch {
    rankings.value = []
  }
}

const fetchSummaries = async () => {
  if (!dateRange.value[0] || !dateRange.value[1]) return
  try {
    const res = await summaryApi.getConceptSummary(conceptId.value, {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      metric_code: searchParams.value.metric_code,
    })
    summaries.value = res.summaries
    renderChart()
  } catch {
    summaries.value = []
  }
}

const renderChart = () => {
  if (!chartRef.value || !summaries.value.length) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const dates = summaries.value.map(s => s.trade_date)
  const totalValues = summaries.value.map(s => s.total_value)
  const avgValues = summaries.value.map(s => s.avg_value)

  chart.setOption({
    title: { text: '概念汇总趋势' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['总值', '均值'] },
    xAxis: { type: 'category', data: dates },
    yAxis: [
      { type: 'value', name: '总值' },
      { type: 'value', name: '均值' },
    ],
    series: [
      { name: '总值', type: 'bar', data: totalValues },
      { name: '均值', type: 'line', yAxisIndex: 1, data: avgValues },
    ],
  })
}

const goBack = () => {
  router.push('/concepts')
}

const goToStock = (code: string) => {
  router.push(`/stocks/${code}`)
}

watch(() => searchParams.value.metric_code, fetchRankings)

onMounted(async () => {
  initDateRange()
  await fetchMetrics()
  fetchConcept()
  fetchRankings()
  fetchSummaries()
})
</script>

<template>
  <div class="concept-detail">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <h1 class="page-title">{{ concept?.concept_name || '' }}</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card header="基本信息" v-loading="loading">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="ID">{{ concept?.id }}</el-descriptions-item>
            <el-descriptions-item label="概念名称">{{ concept?.concept_name }}</el-descriptions-item>
            <el-descriptions-item label="分类">
              <el-tag v-if="concept?.category" type="info">{{ concept.category }}</el-tag>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="描述">{{ concept?.description || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card header="当日排名">
          <div class="search-form">
            <el-date-picker
              v-model="searchParams.trade_date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              @change="fetchRankings"
            />
            <el-select v-model="searchParams.metric_code" placeholder="指标" style="width: 120px">
              <el-option
                v-for="m in metrics"
                :key="m.code"
                :label="m.name"
                :value="m.code"
              />
            </el-select>
            <el-input-number
              v-model="searchParams.limit"
              :min="5"
              :max="100"
              @change="fetchRankings"
            />
          </div>

          <el-table :data="rankings" stripe max-height="400">
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="stock_code" label="股票代码" width="120">
              <template #default="{ row }">
                <el-link type="primary" @click="goToStock(row.stock_code)">
                  {{ row.stock_code }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="stock_name" label="股票名称" />
            <el-table-column prop="trade_value" label="指标值" width="120">
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
        </el-card>
      </el-col>
    </el-row>

    <el-card header="汇总趋势" style="margin-top: 20px">
      <div class="search-form">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
        <el-button type="primary" @click="fetchSummaries">查询</el-button>
      </div>

      <div ref="chartRef" class="chart-container"></div>
    </el-card>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
</style>
