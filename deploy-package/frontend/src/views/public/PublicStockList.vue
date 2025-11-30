<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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
    const response = await stockApi.getList({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value
    })
    stocks.value = response.items
    total.value = response.total

    if (stocks.value.length === 0 && searchKeyword.value) {
      ElMessage.info('未找到匹配的股票')
    }
  } catch (error: any) {
    console.error('Failed to fetch stocks:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    })
    ElMessage.error('获取股票列表失败，请稍后重试')
    stocks.value = []
    total.value = 0
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
          <el-table-column prop="stock_code" label="股票代码" width="120" />
          <el-table-column prop="stock_name" label="股票名称" width="150" />
          <el-table-column label="所属概念" min-width="300">
            <template #default="{ row }">
              <div class="concepts-cell">
                <div v-if="row.concepts && row.concepts.length > 0" class="concepts-tags">
                  <el-tag
                    v-for="concept in row.concepts"
                    :key="concept.id"
                    size="small"
                    effect="light"
                  >
                    {{ concept.concept_name }}
                  </el-tag>
                </div>
                <span v-else class="no-concepts">-</span>
              </div>
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
            :key="stock.stock_code"
            class="stock-card"
          >
            <div class="card-header">
              <div class="stock-info">
                <div class="stock-code">{{ stock.stock_code }}</div>
                <div class="stock-name">{{ stock.stock_name }}</div>
              </div>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">所属概念</span>
              </div>
              <div class="concepts-mobile">
                <div v-if="stock.concepts && stock.concepts.length > 0" class="concepts-tags-mobile">
                  <el-tag
                    v-for="concept in stock.concepts"
                    :key="concept.id"
                    size="small"
                    effect="light"
                  >
                    {{ concept.concept_name }}
                  </el-tag>
                </div>
                <span v-else class="no-concepts">暂无概念分类</span>
              </div>
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
  border: 1px solid #f0f0f0;
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

.concepts-mobile {
  margin-top: 8px;
}

.concepts-tags-mobile {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.no-concepts {
  color: #909399;
  font-size: 14px;
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