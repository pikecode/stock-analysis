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
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/stocks')) return '/stocks'
  if (path.startsWith('/concepts')) return '/concepts'
  if (path.startsWith('/rankings')) return '/rankings'
  if (path.startsWith('/import')) return '/import'
  return path
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>Stock Analysis</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/stocks">
          <el-icon><Document /></el-icon>
          <span>股票列表</span>
        </el-menu-item>
        <el-menu-item index="/concepts">
          <el-icon><Folder /></el-icon>
          <span>概念列表</span>
        </el-menu-item>
        <el-menu-item index="/rankings">
          <el-icon><TrendCharts /></el-icon>
          <span>排名查询</span>
        </el-menu-item>
        <el-sub-menu index="/import">
          <template #title>
            <el-icon><Upload /></el-icon>
            <span>数据导入</span>
          </template>
          <el-menu-item index="/import">上传文件</el-menu-item>
          <el-menu-item index="/import/batches">
            <el-icon><List /></el-icon>
            导入记录
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
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
  justify-content: flex-end;
  padding: 0 20px;
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
