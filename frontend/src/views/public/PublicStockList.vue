<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { stockApi } from '@/api'
import type { Stock } from '@/types'

const router = useRouter()
const route = useRoute()

const stocks = ref<Stock[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 从 URL 参数获取搜索关键词
onMounted(() => {
  const search = route.query.search as string
  if (search) {
    searchKeyword.value = search
  }
  fetchStocks()
})

// 获取股票列表
const fetchStocks = async () => {
  loading.value = true
  try {
    const response = await stockApi.list({
      page: currentPage.value,
      size: pageSize.value,
      search: searchKeyword.value
    })
    stocks.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('Failed to fetch stocks:', error)
    stocks.value = []
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchStocks()
}

// 分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchStocks()
}

// 查看详情
const viewDetail = (stock: Stock) => {
  router.push({
    name: 'PublicStockDetail',
    params: { code: stock.code }
  })
}

// 格式化数字
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}
</script>

<template>
  <div class="public-stock-list">
    <!-- 简单导航栏 -->
    <header class="header">
      <div class="container">
        <div class="logo" @click="router.push('/')">
          <span class="logo-icon">📈</span>
          <span class="logo-text">Stock Analysis</span>
        </div>
        <el-button type="primary" @click="router.push('/login')">
          登录查看更多
        </el-button>
      </div>
    </header>

    <div class="container main-content">
      <h1>股票查询</h1>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索股票代码、名称..."
          size="large"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch">
          搜索
        </el-button>
      </div>

      <!-- 股票列表 -->
      <div v-loading="loading" class="stock-table">
        <el-table :data="stocks" stripe style="width: 100%">
          <el-table-column prop="code" label="股票代码" width="120" />
          <el-table-column prop="name" label="股票名称" width="150" />
          <el-table-column prop="exchange" label="交易所" width="100" />
          <el-table-column label="最新价" width="120">
            <template #default="{ row }">
              {{ row.latest_price ? formatNumber(row.latest_price) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="涨跌幅" width="120">
            <template #default="{ row }">
              <span :class="row.change_percent >= 0 ? 'positive' : 'negative'">
                {{ row.change_percent ? row.change_percent.toFixed(2) + '%' : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="industry" label="所属行业" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <!-- 提示信息 -->
      <div class="tip-card">
        <el-alert type="info" :closable="false">
          <template #title>
            <div class="tip-content">
              <span>💡 提示：登录后可查看更详细的股票数据、概念关联和专业分析报表</span>
              <el-button type="primary" size="small" @click="router.push('/login')">
                立即登录
              </el-button>
            </div>
          </template>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<style scoped>
.public-stock-list {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 0 20px;
  margin-bottom: 24px;
}

.header .container {
  max-width: 1200px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
}

.logo-icon {
  font-size: 28px;
  margin-right: 8px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.main-content {
  padding: 40px 20px;
}

h1 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #303133;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-bar .el-input {
  flex: 1;
}

.stock-table {
  background: white;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.positive {
  color: #F56C6C;
}

.negative {
  color: #67C23A;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.tip-card {
  margin-top: 24px;
}

.tip-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>