<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { stockApi } from '@/api'
import type { Stock } from '@/types'
import { Search } from '@element-plus/icons-vue'
const loading = ref(false)
const stocks = ref<Stock[]>([])
const total = ref(0)

const searchParams = ref({
  keyword: '',
  exchange: '',
  page: 1,
  page_size: 20,
})

// Concepts dialog state
const showConceptsDialog = ref(false)
const selectedStockCode = ref('')
const selectedStockName = ref('')
const allConcepts = ref<any[]>([])
const conceptsLoading = ref(false)

const exchangeOptions = [
  { label: '全部', value: '' },
  { label: '上海', value: 'SH' },
  { label: '深圳', value: 'SZ' },
  { label: '北京', value: 'BJ' },
]

const fetchData = async () => {
  loading.value = true
  try {
    const res = await stockApi.getList(searchParams.value)
    stocks.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchParams.value.page = 1
  fetchData()
}

const handlePageChange = (page: number) => {
  searchParams.value.page = page
  fetchData()
}

const handleSizeChange = (size: number) => {
  searchParams.value.page_size = size
  searchParams.value.page = 1
  fetchData()
}

const showAllConcepts = async (stockCode: string, stockName: string) => {
  selectedStockCode.value = stockCode
  selectedStockName.value = stockName
  conceptsLoading.value = true
  try {
    const res = await stockApi.getConcepts(stockCode)
    allConcepts.value = res.concepts || []
    showConceptsDialog.value = true
  } catch (error) {
    console.error('Failed to fetch concepts:', error)
    allConcepts.value = []
  } finally {
    conceptsLoading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="stock-list">
    <div class="page-header">
      <h1 class="page-title">股票列表</h1>
    </div>

    <el-card>
      <div class="search-form">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索股票代码或名称"
          :prefix-icon="Search"
          clearable
          style="width: 240px"
          @keyup.enter="handleSearch"
        />
        <el-select v-model="searchParams.exchange" placeholder="交易所" style="width: 120px">
          <el-option
            v-for="opt in exchangeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>

      <el-table :data="stocks" v-loading="loading" stripe>
        <el-table-column prop="stock_code" label="股票代码" width="120" />
        <el-table-column prop="stock_name" label="股票名称" />
        <el-table-column label="所属概念" min-width="200">
          <template #default="{ row }">
            <div class="concepts-cell">
              <div class="concepts-tags" v-if="row.concepts && row.concepts.length > 0">
                <el-tag
                  v-for="(concept, idx) in row.concepts.slice(0, 3)"
                  :key="concept.id"
                  size="small"
                  effect="light"
                >
                  {{ concept.concept_name }}
                </el-tag>
                <el-button
                  v-if="row.concepts.length > 3"
                  type="primary"
                  link
                  size="small"
                  @click="showAllConcepts(row.stock_code, row.stock_name)"
                >
                  +{{ row.concepts.length - 3 }} 更多
                </el-button>
              </div>
              <span v-else class="no-concepts">-</span>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- Concepts Dialog -->
    <el-dialog
      v-model="showConceptsDialog"
      :title="`${selectedStockCode} - ${selectedStockName} 的所有概念`"
      width="500px"
    >
      <el-skeleton v-if="conceptsLoading" :rows="5" animated />
      <div v-else class="concepts-list">
        <div v-if="allConcepts.length === 0" class="empty-state">
          <p>该股票暂无概念分类</p>
        </div>
        <div v-else class="concepts-grid">
          <el-tag
            v-for="concept in allConcepts"
            :key="concept.id"
            size="large"
            effect="light"
            style="margin: 6px"
          >
            {{ concept.concept_name }}
          </el-tag>
        </div>
        <div class="concepts-count">共 {{ allConcepts.length }} 个概念</div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.stock-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: #303133;
}

.search-form {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.concepts-cell {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.concepts-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.no-concepts {
  color: #909399;
  font-size: 14px;
}

.concepts-list {
  padding: 10px 0;
}

.concepts-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 0;
}

.concepts-count {
  text-align: right;
  color: #909399;
  font-size: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-state p {
  margin: 0;
}
</style>
