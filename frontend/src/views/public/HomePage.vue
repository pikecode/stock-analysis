<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search, TrendCharts, DataAnalysis, DocumentCopy } from '@element-plus/icons-vue'

const router = useRouter()
const searchValue = ref('')

// 快速搜索
const handleSearch = () => {
  if (searchValue.value) {
    router.push({ name: 'PublicStocks', query: { search: searchValue.value } })
  }
}

// 导航到功能页面
const navigateTo = (name: string) => {
  router.push({ name })
}

// 热门概念数据（模拟）
const hotConcepts = ref([
  { name: '新能源', count: 128, trend: 'up' },
  { name: '人工智能', count: 96, trend: 'up' },
  { name: '半导体', count: 85, trend: 'down' },
  { name: '医疗健康', count: 72, trend: 'up' },
])

// 今日排行（模拟）
const topStocks = ref([
  { code: '600519', name: '贵州茅台', change: 5.2 },
  { code: '000858', name: '五粮液', change: 4.8 },
  { code: '002415', name: '海康威视', change: 3.6 },
])
</script>

<template>
  <div class="home-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="container">
        <div class="logo">
          <span class="logo-icon">📈</span>
          <span class="logo-text">Stock Analysis</span>
        </div>

        <nav class="nav">
          <a @click="navigateTo('PublicStocks')">股票查询</a>
          <a @click="navigateTo('PublicConcepts')">概念板块</a>
          <a @click="navigateTo('PublicRankings')">排名榜单</a>
          <a @click="navigateTo('About')">关于我们</a>
        </nav>

        <div class="auth-buttons">
          <el-button @click="navigateTo('Login')">登录</el-button>
          <el-button type="primary" @click="navigateTo('Login')">注册</el-button>
        </div>
      </div>
    </header>

    <!-- 主横幅区域 -->
    <section class="hero">
      <div class="hero-content">
        <h1>专业的股票数据分析平台</h1>
        <p>实时追踪市场动态，深度分析概念板块，助力您的投资决策</p>

        <!-- 搜索框 -->
        <div class="search-box">
          <el-input
            v-model="searchValue"
            placeholder="搜索股票代码、名称或概念..."
            size="large"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </section>

    <!-- 功能卡片 -->
    <section class="features">
      <div class="container">
        <div class="feature-grid">
          <div class="feature-card" @click="navigateTo('PublicStocks')">
            <el-icon :size="48" color="#409EFF"><TrendCharts /></el-icon>
            <h3>股票查询</h3>
            <p>全面的股票信息查询，实时行情数据</p>
          </div>

          <div class="feature-card" @click="navigateTo('PublicConcepts')">
            <el-icon :size="48" color="#67C23A"><DataAnalysis /></el-icon>
            <h3>概念分析</h3>
            <p>深度挖掘概念板块，洞察市场热点</p>
          </div>

          <div class="feature-card" @click="navigateTo('PublicRankings')">
            <el-icon :size="48" color="#E6A23C"><DocumentCopy /></el-icon>
            <h3>排名榜单</h3>
            <p>多维度排名分析，发现潜力股票</p>
          </div>

          <div class="feature-card" @click="navigateTo('Reports')">
            <el-icon :size="48" color="#F56C6C"><DataAnalysis /></el-icon>
            <h3>专业报表</h3>
            <p>登录后查看专业分析报表</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据展示区 -->
    <section class="data-section">
      <div class="container">
        <div class="data-grid">
          <!-- 热门概念 -->
          <div class="data-card">
            <h3>🔥 热门概念</h3>
            <div class="concept-list">
              <div v-for="concept in hotConcepts" :key="concept.name" class="concept-item">
                <span class="concept-name">{{ concept.name }}</span>
                <span class="concept-count">{{ concept.count }} 只</span>
                <span :class="['concept-trend', concept.trend]">
                  {{ concept.trend === 'up' ? '↑' : '↓' }}
                </span>
              </div>
            </div>
            <el-link type="primary" @click="navigateTo('PublicConcepts')">查看更多 →</el-link>
          </div>

          <!-- 今日排行 -->
          <div class="data-card">
            <h3>📊 今日涨幅榜</h3>
            <div class="stock-list">
              <div v-for="stock in topStocks" :key="stock.code" class="stock-item">
                <div class="stock-info">
                  <span class="stock-code">{{ stock.code }}</span>
                  <span class="stock-name">{{ stock.name }}</span>
                </div>
                <span class="stock-change positive">+{{ stock.change }}%</span>
              </div>
            </div>
            <el-link type="primary" @click="navigateTo('PublicRankings')">查看完整榜单 →</el-link>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部 CTA -->
    <section class="cta">
      <div class="container">
        <h2>解锁更多专业功能</h2>
        <p>注册账号，免费使用专业分析报表和深度数据</p>
        <el-button type="primary" size="large" @click="navigateTo('Login')">
          立即注册
        </el-button>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2024 Stock Analysis. All rights reserved.</p>
        <p>
          <el-link @click="navigateTo('About')">关于我们</el-link>
          <span class="separator">|</span>
          <el-link @click="navigateTo('AdminLogin')">管理员登录</el-link>
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 头部导航 */
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
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
  font-size: 24px;
  margin-right: 0;
}

.nav {
  display: none;
  gap: 24px;
}

.nav a {
  color: #606266;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s;
  font-size: 14px;
}

.nav a:hover {
  color: #409EFF;
}

/* 平板设备 */
@media (min-width: 768px) {
  .header .container {
    height: 64px;
    padding: 0 20px;
  }

  .logo {
    font-size: 18px;
    gap: 8px;
  }

  .logo-icon {
    font-size: 28px;
  }

  .nav {
    display: flex;
    gap: 28px;
  }

  .nav a {
    font-size: 15px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .logo {
    font-size: 20px;
  }

  .nav {
    gap: 32px;
  }

  .nav a {
    font-size: 16px;
  }
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

/* 主横幅 */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.hero-content h1 {
  font-size: 28px;
  margin-bottom: 12px;
  line-height: 1.2;
}

.hero-content p {
  font-size: 16px;
  margin-bottom: 30px;
  opacity: 0.9;
  line-height: 1.5;
}

.search-box {
  max-width: 100%;
  margin: 0 auto;
  padding: 0 0;
}

/* 平板设备 */
@media (min-width: 768px) {
  .hero {
    padding: 80px 20px;
  }

  .hero-content h1 {
    font-size: 36px;
    margin-bottom: 16px;
  }

  .hero-content p {
    font-size: 18px;
    margin-bottom: 36px;
  }

  .search-box {
    max-width: 500px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .hero {
    padding: 100px 20px;
  }

  .hero-content h1 {
    font-size: 48px;
  }

  .hero-content p {
    font-size: 20px;
    margin-bottom: 40px;
  }

  .search-box {
    max-width: 600px;
  }
}

/* 功能卡片 */
.features {
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.feature-card {
  background: white;
  padding: 24px 16px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}

.feature-card h3 {
  margin: 12px 0 8px;
  font-size: 16px;
}

.feature-card p {
  color: #909399;
  line-height: 1.6;
  font-size: 14px;
}

/* 平板设备 */
@media (min-width: 768px) {
  .features {
    padding: 60px 20px;
  }

  .container {
    padding: 0 20px;
  }

  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .feature-card {
    padding: 28px 20px;
    border-radius: 10px;
  }

  .feature-card h3 {
    font-size: 18px;
  }

  .feature-card p {
    font-size: 15px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .features {
    padding: 80px 20px;
  }

  .feature-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
  }

  .feature-card {
    padding: 32px;
    border-radius: 12px;
  }

  .feature-card h3 {
    font-size: 20px;
  }

  .feature-card p {
    font-size: 16px;
  }

  .feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.1);
  }
}

/* 数据展示 */
.data-section {
  padding: 40px 20px;
  background: #f0f2f5;
}

.data-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.data-card {
  background: white;
  padding: 20px 16px;
  border-radius: 8px;
}

.data-card h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
}

.concept-list, .stock-list {
  margin-bottom: 16px;
}

.concept-item, .stock-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #EBEEF5;
  font-size: 14px;
}

.concept-item:last-child, .stock-item:last-child {
  border-bottom: none;
}

.concept-name {
  flex: 1;
  font-weight: 500;
}

.concept-count {
  color: #909399;
  margin-right: 12px;
  font-size: 12px;
}

.concept-trend {
  font-size: 16px;
  font-weight: bold;
}

.concept-trend.up {
  color: #F56C6C;
}

.concept-trend.down {
  color: #67C23A;
}

.stock-info {
  flex: 1;
  display: flex;
  gap: 8px;
  align-items: center;
}

.stock-code {
  font-weight: bold;
  color: #409EFF;
  font-size: 13px;
}

.stock-name {
  font-size: 14px;
}

.stock-change {
  font-weight: bold;
  font-size: 14px;
  min-width: 60px;
  text-align: right;
}

.stock-change.positive {
  color: #F56C6C;
}

/* 平板设备 */
@media (min-width: 768px) {
  .data-section {
    padding: 60px 20px;
  }

  .data-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .data-card {
    padding: 24px;
    border-radius: 10px;
  }

  .data-card h3 {
    margin-bottom: 18px;
    font-size: 18px;
  }

  .concept-list, .stock-list {
    margin-bottom: 18px;
  }

  .concept-item, .stock-item {
    padding: 12px 0;
    font-size: 15px;
  }

  .concept-count {
    margin-right: 16px;
    font-size: 13px;
  }

  .stock-code {
    font-size: 14px;
  }

  .stock-name {
    font-size: 15px;
  }

  .stock-change {
    font-size: 15px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .data-section {
    padding: 80px 20px;
  }

  .data-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .data-card {
    padding: 28px;
    border-radius: 12px;
  }

  .data-card h3 {
    margin-bottom: 20px;
    font-size: 20px;
  }

  .concept-list, .stock-list {
    margin-bottom: 20px;
  }

  .concept-item, .stock-item {
    padding: 14px 0;
    font-size: 15px;
  }

  .concept-count {
    margin-right: 16px;
    font-size: 14px;
  }

  .stock-code {
    font-size: 15px;
  }

  .stock-name {
    font-size: 15px;
  }

  .stock-change {
    font-size: 15px;
  }
}

/* CTA 区域 */
.cta {
  background: white;
  padding: 60px 20px;
  text-align: center;
}

.cta h2 {
  font-size: 24px;
  margin-bottom: 12px;
  font-weight: 600;
}

.cta p {
  font-size: 15px;
  color: #606266;
  margin-bottom: 24px;
}

/* 平板设备 */
@media (min-width: 768px) {
  .cta {
    padding: 80px 20px;
  }

  .cta h2 {
    font-size: 28px;
    margin-bottom: 14px;
  }

  .cta p {
    font-size: 16px;
    margin-bottom: 28px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .cta {
    padding: 100px 20px;
  }

  .cta h2 {
    font-size: 32px;
    margin-bottom: 16px;
  }

  .cta p {
    font-size: 18px;
    margin-bottom: 32px;
  }
}

/* 页脚 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 24px 16px;
  text-align: center;
  font-size: 13px;
}

.footer p {
  margin: 8px 0;
  line-height: 1.5;
}

.footer .el-link {
  color: #ecf0f1;
  font-size: 13px;
}

.separator {
  margin: 0 8px;
  opacity: 0.5;
}

/* 平板设备 */
@media (min-width: 768px) {
  .footer {
    padding: 32px 20px;
    font-size: 14px;
  }

  .footer p {
    margin: 10px 0;
  }

  .footer .el-link {
    font-size: 14px;
  }

  .separator {
    margin: 0 12px;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .footer {
    padding: 40px 20px;
    font-size: 14px;
  }

  .footer p {
    margin: 12px 0;
  }
}
</style>