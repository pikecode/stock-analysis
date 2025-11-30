<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stockApi, rankingApi } from '@/api'
import type { StockWithConcepts, TopNCountItem } from '@/types'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const stock = ref<StockWithConcepts | null>(null)
const topNStats = ref<TopNCountItem[]>([])

const stockCode = computed(() => route.params.code as string)

const dateRange = ref<[string, string]>(['', ''])

// Default to last 30 days
const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  dateRange.value = [
    start.toISOString().slice(0, 10),
    end.toISOString().slice(0, 10),
  ]
}

const fetchStock = async () => {
  loading.value = true
  try {
    stock.value = await stockApi.getDetail(stockCode.value)
  } finally {
    loading.value = false
  }
}

const fetchTopNStats = async () => {
  if (!dateRange.value[0] || !dateRange.value[1]) return
  try {
    const res = await rankingApi.getTopNCount(stockCode.value, {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      top_n: 10,
    })
    topNStats.value = res.statistics
  } catch {
    topNStats.value = []
  }
}

const goBack = () => {
  router.push('/stocks')
}

const goToConcept = (conceptId: number) => {
  router.push(`/concepts/${conceptId}`)
}

onMounted(() => {
  initDateRange()
  fetchStock()
  fetchTopNStats()
})
</script>

<template>
  <div class="stock-detail">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <h1 class="page-title">{{ stock?.stock_name || stockCode }} ({{ stockCode }})</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="基本信息" v-loading="loading">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="股票代码">{{ stock?.stock_code }}</el-descriptions-item>
            <el-descriptions-item label="股票名称">{{ stock?.stock_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="交易所">
              <el-tag v-if="stock?.exchange_prefix === 'SH'" type="danger">上海</el-tag>
              <el-tag v-else-if="stock?.exchange_prefix === 'SZ'" type="primary">深圳</el-tag>
              <el-tag v-else-if="stock?.exchange_prefix === 'BJ'" type="warning">北京</el-tag>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ stock?.created_at?.slice(0, 19).replace('T', ' ') }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="所属概念">
          <div v-if="stock?.concepts?.length">
            <el-tag
              v-for="concept in stock.concepts"
              :key="concept.id"
              class="concept-tag"
              @click="goToConcept(concept.id)"
              style="cursor: pointer; margin: 4px"
            >
              {{ concept.concept_name }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无所属概念" />
        </el-card>
      </el-col>
    </el-row>

    <el-card header="Top N 统计" style="margin-top: 20px">
      <div class="search-form">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
        <el-button type="primary" @click="fetchTopNStats">查询</el-button>
      </div>

      <el-table :data="topNStats" stripe>
        <el-table-column prop="concept_name" label="概念名称">
          <template #default="{ row }">
            <el-link type="primary" @click="goToConcept(row.concept_id)">
              {{ row.concept_name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="top_n_count" label="进入Top10次数" width="150" />
        <el-table-column prop="top_n_rate" label="Top10占比" width="150">
          <template #default="{ row }">
            {{ (row.top_n_rate * 100).toFixed(1) }}%
          </template>
        </el-table-column>
      </el-table>
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

.concept-tag:hover {
  background-color: #409eff;
  color: #fff;
}
</style>
