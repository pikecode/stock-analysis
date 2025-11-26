<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
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
const isMobile = ref(false)
const windowWidth = ref(window.innerWidth)

// 检查是否是移动设备
const checkMobile = () => {
  windowWidth.value = window.innerWidth
  isMobile.value = window.innerWidth < 768
}

// 从 URL 参数获取搜索关键词
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)

  const search = route.query.search as string
  if (search) {
    searchKeyword.value = search
  }
  fetchStocks()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
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

      <!-- 股票列表 - 桌面版表格 -->
      <div v-if="!isMobile" v-loading="loading" class="stock-table">
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

      <!-- 股票列表 - 移动版卡片 -->
      <div v-if="isMobile" class="stock-card-list">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="stocks.length === 0" class="empty-container">
          <el-empty description="暂无数据" />
        </div>
        <div v-else class="card-grid">
          <div
            v-for="stock in stocks"
            :key="stock.code"
            class="stock-card"
            @click="viewDetail(stock)"
          >
            <div class="card-header">
              <div class="stock-info">
                <div class="stock-code">{{ stock.code }}</div>
                <div class="stock-name">{{ stock.name }}</div>
              </div>
              <div
                class="change-badge"
                :class="stock.change_percent >= 0 ? 'positive' : 'negative'"
              >
                {{ stock.change_percent ? stock.change_percent.toFixed(2) + '%' : '-' }}
              </div>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">最新价</span>
                <span class="value">¥{{ stock.latest_price ? formatNumber(stock.latest_price) : '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">交易所</span>
                <span class="value">{{ stock.exchange || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">行业</span>
                <span class="value">{{ stock.industry || '-' }}</span>
              </div>
            </div>
            <div class="card-footer">
              <el-button type="primary" size="small" @click.stop="viewDetail(stock)">
                查看详情
              </el-button>
            </div>
          </div>
        </div>

        <!-- 移动端分页 -->
        <div class="pagination-mobile">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 16px;
  margin-bottom: 16px;
}

.header .container {
  max-width: 1200px;
  margin: 0 auto;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  gap: 4px;
}

.logo-icon {
  font-size: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.main-content {
  padding: 20px 16px;
}

h1 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #303133;
}

.search-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar .el-input {
  flex: 1;
}

.stock-table {
  background: white;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  overflow-x: auto;
}

.stock-card-list {
  margin-bottom: 20px;
}

.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.stock-card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: box-shadow 0.3s, transform 0.3s;
  border: 1px solid #f0f0f0;
}

.stock-card:active {
  transform: scale(0.98);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.stock-info {
  flex: 1;
}

.stock-code {
  font-weight: bold;
  color: #409eff;
  font-size: 14px;
}

.stock-name {
  font-size: 13px;
  color: #606266;
  margin-top: 2px;
}

.change-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: bold;
  min-width: 50px;
  text-align: center;
}

.change-badge.positive {
  color: #f56c6c;
  background-color: #fef0f0;
}

.change-badge.negative {
  color: #67c23a;
  background-color: #f0f9ff;
}

.card-body {
  margin-bottom: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}

.info-row .label {
  color: #909399;
}

.info-row .value {
  font-weight: 500;
  color: #303133;
}

.card-footer {
  display: flex;
  gap: 8px;
}

.card-footer :deep(.el-button) {
  flex: 1;
  margin: 0;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px 20px;
  text-align: center;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #67c23a;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.pagination-mobile {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.tip-card {
  margin-top: 20px;
}

.tip-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

/* 平板设备 */
@media (min-width: 768px) {
  .header {
    padding: 0 20px;
    margin-bottom: 24px;
  }

  .header .container {
    height: 64px;
  }

  .logo {
    font-size: 18px;
    gap: 8px;
  }

  .logo-icon {
    font-size: 24px;
  }

  .container {
    padding: 0 20px;
  }

  .main-content {
    padding: 40px 20px;
  }

  h1 {
    font-size: 24px;
    margin-bottom: 20px;
  }

  .search-bar {
    flex-direction: row;
    gap: 12px;
    margin-bottom: 24px;
  }

  .stock-table {
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 24px;
  }

  .card-grid {
    gap: 16px;
  }

  .stock-card {
    padding: 16px;
    border-radius: 8px;
  }

  .stock-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .stock-code {
    font-size: 15px;
  }

  .stock-name {
    font-size: 14px;
  }

  .info-row {
    font-size: 14px;
    padding: 8px 0;
  }

  .change-badge {
    padding: 6px 12px;
    font-size: 14px;
  }

  .pagination {
    justify-content: flex-end;
  }

  .tip-content {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .header {
    padding: 0 20px;
    margin-bottom: 24px;
  }

  .logo {
    font-size: 20px;
  }

  .main-content {
    padding: 40px 20px;
  }

  h1 {
    font-size: 28px;
    margin-bottom: 24px;
  }

  .search-bar {
    gap: 12px;
    margin-bottom: 24px;
  }

  .stock-table {
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 24px;
  }

  .pagination {
    margin-top: 24px;
  }

  .tip-card {
    margin-top: 24px;
  }
}
</style>