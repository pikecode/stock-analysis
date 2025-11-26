<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import {
  Document,
  Folder,
  TrendCharts,
  Upload,
  List,
  User,
  SwitchButton,
  Setting,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/admin/stocks')) return '/admin/stocks'
  if (path.startsWith('/admin/concepts')) return '/admin/concepts'
  if (path.startsWith('/admin/rankings')) return '/admin/rankings'
  if (path.startsWith('/admin/import')) return '/admin/import'
  if (path.startsWith('/admin/settings')) return '/admin/settings'
  return path
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <!-- 管理员专用侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>📊 管理后台</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <!-- 数据管理 -->
        <el-menu-item index="/admin/stocks">
          <el-icon><Document /></el-icon>
          <span>股票管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/concepts">
          <el-icon><Folder /></el-icon>
          <span>概念管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/rankings">
          <el-icon><TrendCharts /></el-icon>
          <span>排名查询</span>
        </el-menu-item>

        <!-- 数据导入 - Admin 专用 -->
        <el-sub-menu index="/admin/import">
          <template #title>
            <el-icon><Upload /></el-icon>
            <span>📥 数据导入</span>
          </template>
          <el-menu-item index="/admin/import">上传文件</el-menu-item>
          <el-menu-item index="/admin/import/batches">
            <el-icon><List /></el-icon>
            导入记录
          </el-menu-item>
        </el-sub-menu>

        <!-- 系统设置 -->
        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <span class="title">库存分析系统 - 管理员</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleLogout">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ authStore.user?.username || '管理员' }}
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
