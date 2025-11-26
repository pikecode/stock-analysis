<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import {
  Document,
  Folder,
  TrendCharts,
  DataAnalysis,
  User,
  SwitchButton,
  Setting,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/reports')) return path
  if (path.startsWith('/analysis')) return path
  if (path.startsWith('/profile')) return path
  return path
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <!-- 客户端专用侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>📈 数据分析</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <!-- 报表分析 -->
        <el-sub-menu index="/reports">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>报表分析</span>
          </template>
          <el-menu-item index="/reports">报表总览</el-menu-item>
          <el-menu-item index="/reports/concept-ranking">概念排名</el-menu-item>
          <el-menu-item index="/reports/stock-trend">股票趋势</el-menu-item>
          <el-menu-item index="/reports/top-n">Top N 分析</el-menu-item>
        </el-sub-menu>

        <!-- 数据分析 -->
        <el-sub-menu index="/analysis">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>数据分析</span>
          </template>
          <el-menu-item index="/analysis/portfolio">投资组合</el-menu-item>
          <el-menu-item index="/analysis/performance">业绩分析</el-menu-item>
        </el-sub-menu>

        <!-- 个人中心 -->
        <el-sub-menu index="/profile">
          <template #title>
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </template>
          <el-menu-item index="/profile">用户信息</el-menu-item>
          <el-menu-item index="/profile/settings">账户设置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <span class="title">库存分析系统 - 客户端</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleLogout">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ authStore.user?.username || '用户' }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow-y: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
  border-bottom: 1px solid #1f2a3a;
}

.logo h2 {
  color: #fff;
  font-size: 16px;
  margin: 0;
}

.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #606266;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
