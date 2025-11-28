<template>
  <div class="subscription-expired-page">
    <div class="expired-container">
      <div class="expired-icon">
        <el-icon><Warning /></el-icon>
      </div>
      <h1>订阅已过期</h1>
      <p class="description">您的订阅已过期，无法访问报表和分析功能。</p>

      <div class="info-box">
        <p v-if="subscription">
          <span class="label">过期时间：</span>
          <span class="value">{{ formatDate(subscription.end_date) }}</span>
        </p>
        <p v-if="subscription">
          <span class="label">剩余天数：</span>
          <span class="value expired-text">{{ subscription.days_remaining }} 天</span>
        </p>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" @click="goToPlans">
          <el-icon><ShoppingCart /></el-icon>
          查看套餐并续费
        </el-button>
        <el-button size="large" @click="goHome">
          返回首页
        </el-button>
      </div>

      <div class="tips">
        <h3>续费提示</h3>
        <ul>
          <li>购买新的订阅套餐可继续享受报表分析功能</li>
          <li>系统会保存您的所有历史数据</li>
          <li>续费后可立即恢复访问权限</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { Warning, ShoppingCart } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const subscription = computed(() => authStore.subscription)

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const goToPlans = () => {
  // 将重定向到套餐页面（需要创建）
  router.push({ path: '/plans' })
}

const goHome = () => {
  router.push({ path: '/' })
}
</script>

<style scoped>
.subscription-expired-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.expired-container {
  background: white;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.expired-icon {
  font-size: 80px;
  color: #f56c6c;
  margin-bottom: 30px;
}

h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 16px 0;
}

.description {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

.info-box {
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
  padding: 20px;
  margin-bottom: 30px;
  text-align: left;
}

.info-box p {
  margin: 10px 0;
  font-size: 14px;
}

.label {
  color: #666;
  display: inline-block;
  width: 100px;
}

.value {
  color: #333;
  font-weight: 500;
}

.expired-text {
  color: #f56c6c;
}

.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.actions :deep(.el-button) {
  flex: 1;
}

.tips {
  text-align: left;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 6px;
}

.tips h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.tips ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #666;
}

.tips li {
  margin: 8px 0;
}

@media (max-width: 768px) {
  .expired-container {
    padding: 40px 20px;
  }

  .expired-icon {
    font-size: 60px;
  }

  h1 {
    font-size: 22px;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
