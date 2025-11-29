<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { conceptApi } from '@/api'
import type { Concept } from '@/types'
import { Search } from '@element-plus/icons-vue'

const loading = ref(false)
const concepts = ref<Concept[]>([])
const total = ref(0)

const searchParams = ref({
  keyword: '',
  category: '',
  page: 1,
  page_size: 20,
})

// Stocks dialog state
const showStocksDialog = ref(false)
const selectedConceptId = ref<number | null>(null)
const selectedConceptName = ref('')
const conceptStocks = ref<any[]>([])
const stocksLoading = ref(false)
const stocksTotal = ref(0)
const stocksParams = ref({
  page: 1,
  page_size: 20,
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await conceptApi.getList(searchParams.value)
    concepts.value = res.items
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

const fetchConceptStocks = async () => {
  if (!selectedConceptId.value) return

  stocksLoading.value = true
  try {
    const res = await conceptApi.getStocks(selectedConceptId.value, stocksParams.value)
    conceptStocks.value = res.stocks || []
    stocksTotal.value = res.total || 0
  } catch (error) {
    console.error('Failed to fetch stocks:', error)
    conceptStocks.value = []
    stocksTotal.value = 0
  } finally {
    stocksLoading.value = false
  }
}

const showConceptStocks = async (conceptId: number, conceptName: string) => {
  selectedConceptId.value = conceptId
  selectedConceptName.value = conceptName
  stocksParams.value.page = 1
  showStocksDialog.value = true
  await fetchConceptStocks()
}

const handleStocksPageChange = (page: number) => {
  stocksParams.value.page = page
  fetchConceptStocks()
}

const handleStocksSizeChange = (size: number) => {
  stocksParams.value.page_size = size
  stocksParams.value.page = 1
  fetchConceptStocks()
}

onMounted(fetchData)
</script>

<template>
  <div class="concept-list">
    <div class="page-header">
      <h1 class="page-title">概念列表</h1>
    </div>

    <el-card>
      <div class="search-form">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索概念名称"
          :prefix-icon="Search"
          clearable
          style="width: 240px"
          @keyup.enter="handleSearch"
        />
        <el-input
          v-model="searchParams.category"
          placeholder="分类"
          clearable
          style="width: 150px"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>

      <el-table :data="concepts" v-loading="loading" stripe>
        <el-table-column prop="concept_name" label="概念名称" />
        <el-table-column label="下属股票" width="120">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="showConceptStocks(row.id, row.concept_name)"
            >
              查看股票
            </el-button>
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

    <!-- Stocks Dialog -->
    <el-dialog
      v-model="showStocksDialog"
      :title="`${selectedConceptName} - 所属股票`"
      width="600px"
    >
      <el-skeleton v-if="stocksLoading" :rows="5" animated />
      <div v-else class="stocks-list">
        <div v-if="conceptStocks.length === 0" class="empty-state">
          <p>该概念暂无关联股票</p>
        </div>
        <div v-else>
          <el-table :data="conceptStocks" stripe>
            <el-table-column prop="stock_code" label="股票代码" width="120" />
            <el-table-column prop="stock_name" label="股票名称" />
          </el-table>
          <div class="stocks-pagination">
            <el-pagination
              v-model:current-page="stocksParams.page"
              v-model:page-size="stocksParams.page_size"
              :total="stocksTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="handleStocksPageChange"
              @size-change="handleStocksSizeChange"
            />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.concept-list {
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

.stocks-list {
  padding: 10px 0;
}

.stocks-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
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
