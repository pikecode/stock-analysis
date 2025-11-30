<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { Search, Check, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const searchValue = ref('')
const plans = ref<any[]>([])

// 快速搜索
const handleSearch = () => {
  if (!searchValue.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  router.push({ name: 'PublicStocks', query: { search: searchValue.value } })
}

// 退出登录
const handleLogout = async () => {
  await authStore.logout()
  ElMessage.success('已退出登录')
  router.push({ name: 'Home' })
}

// 导航到功能页面
const navigateTo = (name: string) => {
  router.push({ name })
}

// 购买套餐
const handleBuyPlan = (plan: any) => {
  router.push({ name: 'Login' })
}

// 加载套餐数据
const loadPlans = async () => {
  try {
    const response = await fetch('/api/v1/plans')
    if (response.ok) {
      const data = await response.json()
      plans.value = data.sort((a: any, b: any) => a.sort_order - b.sort_order)
    }
  } catch (error) {
    console.error('Failed to load plans:', error)
  }
}


onMounted(() => {
  loadPlans()
})
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


        <div class="auth-buttons">
          <!-- 未登录状态 -->
          <template v-if="!authStore.isLoggedIn">
            <el-button @click="navigateTo('Login')">登录</el-button>
            <el-button type="primary" @click="navigateTo('Login')">注册</el-button>
          </template>

          <!-- 已登录状态 -->
          <template v-else>
            <el-dropdown>
              <span class="el-dropdown-link">
                👤 {{ authStore.user?.username }}
                <el-icon class="is-icon"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="navigateTo('Reports')" v-if="authStore.isCustomer">
                    📊 查看报表
                  </el-dropdown-item>
                  <el-dropdown-item @click="navigateTo('UserProfile')">
                    👤 个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="navigateTo('UserSettings')">
                    ⚙️ 账户设置
                  </el-dropdown-item>
                  <el-divider />
                  <el-dropdown-item @click="handleLogout">
                    🚪 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
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



    <!-- 套餐价格区域 -->
    <section class="pricing-section">
      <div class="container">
        <h2>选择适合您的套餐</h2>
        <p>解锁专业分析功能，享受实时数据和深度报表</p>
        <div class="pricing-grid">
          <div
            v-for="plan in plans"
            :key="plan.id"
            class="pricing-card"
            :class="{ featured: plan.name === 'yearly' }"
          >
            <div v-if="plan.original_price" class="discount-badge">
              {{ Math.round((1 - parseFloat(plan.price) / parseFloat(plan.original_price)) * 100) }}% 折扣
            </div>
            <h3>{{ plan.display_name }}</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">{{ parseInt(plan.price) }}</span>
              <span class="period">/{{ plan.duration_days }}天</span>
            </div>
            <p v-if="plan.original_price" class="original-price">
              原价: ¥{{ parseInt(plan.original_price) }}
            </p>
            <p class="description">{{ plan.description }}</p>
            <div class="features">
              <div class="feature-item">
                <el-icon><Check /></el-icon>
                <span>{{ plan.duration_days }}天有效期</span>
              </div>
              <div class="feature-item">
                <el-icon><Check /></el-icon>
                <span>每日实时数据更新</span>
              </div>
              <div class="feature-item">
                <el-icon><Check /></el-icon>
                <span>专业分析报表</span>
              </div>
              <div class="feature-item">
                <el-icon><Check /></el-icon>
                <span>概念板块深度分析</span>
              </div>
              <div v-if="plan.name !== 'monthly'" class="feature-item">
                <el-icon><Check /></el-icon>
                <span>数据导出功能</span>
              </div>
            </div>
            <el-button
              :type="plan.name === 'yearly' ? 'primary' : 'default'"
              size="large"
              class="buy-button"
              @click="handleBuyPlan(plan)"
            >
              现在购买
            </el-button>
          </div>
        </div>
      </div>
    </section>


    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2024 Stock Analysis. All rights reserved.</p>
        <p>
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
}

/* PC 设备 */
@media (min-width: 1024px) {
  .logo {
    font-size: 20px;
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

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

/* 套餐价格区域 */
.pricing-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f5 100%);
  padding: 60px 20px;
}

.pricing-section h2 {
  font-size: 28px;
  margin-bottom: 8px;
  text-align: center;
  color: #303133;
}

.pricing-section > .container > p {
  text-align: center;
  color: #909399;
  margin-bottom: 40px;
  font-size: 15px;
}

.pricing-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.pricing-card {
  background: white;
  border-radius: 10px;
  padding: 32px 24px;
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s;
}

.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.pricing-card.featured {
  border: 2px solid #409EFF;
  transform: scale(1.05);
  box-shadow: 0 12px 24px rgba(64, 158, 255, 0.2);
}

.discount-badge {
  position: absolute;
  top: -12px;
  right: 20px;
  background: #f56c6c;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.pricing-card h3 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #303133;
}

.price {
  margin-bottom: 12px;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 18px;
  color: #606266;
}

.amount {
  font-size: 40px;
  font-weight: bold;
  color: #409EFF;
}

.period {
  font-size: 14px;
  color: #909399;
}

.original-price {
  font-size: 13px;
  color: #909399;
  text-decoration: line-through;
  margin-bottom: 12px;
}

.description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.5;
}

.features {
  margin-bottom: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  padding: 8px 0;
}

.feature-item :deep(.el-icon) {
  color: #67C23A;
  flex-shrink: 0;
}

.buy-button {
  width: 100%;
}

/* 平板设备 */
@media (min-width: 768px) {
  .pricing-section {
    padding: 80px 20px;
  }

  .pricing-section h2 {
    font-size: 32px;
    margin-bottom: 12px;
  }

  .pricing-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .pricing-card {
    padding: 36px 28px;
  }

  .pricing-card.featured {
    grid-column: span 2;
    max-width: 50%;
    margin: 0 auto;
  }
}

/* PC 设备 */
@media (min-width: 1024px) {
  .pricing-section {
    padding: 100px 20px;
  }

  .pricing-section h2 {
    font-size: 36px;
  }

  .pricing-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 28px;
  }

  .pricing-card {
    padding: 40px 28px;
  }

  .pricing-card.featured {
    grid-column: span 1;
    max-width: 100%;
    transform: scale(1.08);
  }

  .price {
    margin-bottom: 16px;
  }

  .amount {
    font-size: 44px;
  }

  .description {
    margin-bottom: 24px;
  }

  .features {
    margin-bottom: 32px;
  }

  .feature-item {
    padding: 10px 0;
    font-size: 14px;
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