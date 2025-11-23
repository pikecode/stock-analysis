<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stockApi } from '@/api'
import type { Stock } from '@/types'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const stocks = ref<Stock[]>([])
const total = ref(0)

const searchParams = ref({
  keyword: '',
  exchange: '',
  page: 1,
  page_size: 20,
})

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

const goToDetail = (code: string) => {
  router.push(`/stocks/${code}`)
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
        <el-table-column prop="stock_code" label="股票代码" width="120">
          <template #default="{ row }">
            <el-link type="primary" @click="goToDetail(row.stock_code)">
              {{ row.stock_code }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="stock_name" label="股票名称" />
        <el-table-column prop="exchange_prefix" label="交易所" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.exchange_prefix === 'SH'" type="danger">上海</el-tag>
            <el-tag v-else-if="row.exchange_prefix === 'SZ'" type="primary">深圳</el-tag>
            <el-tag v-else-if="row.exchange_prefix === 'BJ'" type="warning">北京</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="exchange_name" label="交易所名称" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToDetail(row.stock_code)"> 详情 </el-button>
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
  </div>
</template>
