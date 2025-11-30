<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import {
  DataAnalysis,
  TrendCharts,
  User,
  SwitchButton,
  Menu,
  Fold,
  Expand,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式状态
const isMobile = ref(false)
const drawerVisible = ref(false)
const windowWidth = ref(window.innerWidth)
const isCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')

// 计算是否是移动设备
const checkMobile = () => {
  windowWidth.value = window.innerWidth
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const activeMenu = computed(() => {
  const path = route.path
  // 精确匹配菜单项
  if (path === '/reports') return '/reports'
  if (path === '/reports/new-highs') return '/reports/new-highs'
  if (path === '/convertible-bonds') return '/convertible-bonds'
  if (path === '/profile' || path.startsWith('/profile/')) return '/profile'
  // 其他 /reports 下的路径默认高亮报表总览
  if (path.startsWith('/reports')) return '/reports'
  return path
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const handleNavigation = (index: string) => {
  router.push(index)
  // 移动端导航后关闭抽屉
  if (isMobile.value) {
    drawerVisible.value = false
  }
}

// 切换侧边栏展开/收起
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar-collapsed', isCollapsed.value.toString())
}

// 计算侧边栏宽度
const sidebarWidth = computed(() => {
  return isCollapsed.value ? '64px' : '200px'
})
</script>

<template>
  <el-container class="layout-container">
    <!-- 移动端顶部栏 -->
    <div v-if="isMobile" class="mobile-header">
      <el-button type="text" @click="drawerVisible = true" class="menu-btn">
        <el-icon><Menu /></el-icon>
      </el-button>
      <h1 class="logo-text">📈 数据分析</h1>
      <el-dropdown @command="handleLogout" class="user-dropdown">
        <el-button type="text" class="user-btn">
          <el-icon><User /></el-icon>
        </el-button>
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

    <!-- 移动端侧边栏（抽屉） -->
    <el-drawer
      v-model="drawerVisible"
      v-if="isMobile"
      :show-close="true"
      :append-to-body="true"
      size="250px"
      title="菜单导航"
    >
      <el-menu
        :default-active="activeMenu"
        @select="handleNavigation"
        background-color="#fff"
        text-color="#303133"
        active-text-color="#409EFF"
      >
        <!-- 报表总览 -->
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <span>报表总览</span>
        </el-menu-item>

        <!-- 创新高分析 -->
        <el-menu-item index="/reports/new-highs">
          <el-icon><DataAnalysis /></el-icon>
          <span>创新高分析</span>
        </el-menu-item>

        <!-- 转债分析 -->
        <el-menu-item index="/convertible-bonds">
          <el-icon><TrendCharts /></el-icon>
          <span>转债分析</span>
        </el-menu-item>

        <!-- 用户信息 -->
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>用户信息</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>

    <!-- PC 侧边栏 -->
    <el-aside v-if="!isMobile" :width="sidebarWidth" class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <div class="logo-content">
          <h2 v-if="!isCollapsed" class="logo-title">📈 数据分析</h2>
          <h2 v-else class="logo-title-collapsed">📈</h2>
        </div>
        <el-button
          type="text"
          class="toggle-btn"
          @click="toggleSidebar"
          :title="isCollapsed ? '展开菜单' : '收起菜单'"
        >
          <el-icon :class="{ 'icon-rotate': !isCollapsed }">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </el-button>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        :collapse="isCollapsed"
      >
        <!-- 报表总览 -->
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <span>报表总览</span>
        </el-menu-item>

        <!-- 创新高分析 -->
        <el-menu-item index="/reports/new-highs">
          <el-icon><DataAnalysis /></el-icon>
          <span>创新高分析</span>
        </el-menu-item>

        <!-- 转债分析 -->
        <el-menu-item index="/convertible-bonds">
          <el-icon><TrendCharts /></el-icon>
          <span>转债分析</span>
        </el-menu-item>

        <!-- 用户信息 -->
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>用户信息</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- PC 顶部栏 -->
      <el-header v-if="!isMobile" class="header">
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
  display: flex;
  flex-direction: column;
}

/* ========== PC 端样式 ========== */
@media (min-width: 768px) {
  .layout-container {
    flex-direction: row;
  }

  .sidebar {
    background-color: #304156;
    overflow-y: auto;
    flex-shrink: 0;
    transition: width 0.3s ease;
    position: relative;
  }

  .sidebar.collapsed {
    overflow-x: hidden;
  }

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    background-color: #263445;
    border-bottom: 1px solid #1f2a3a;
    transition: all 0.3s ease;
  }

  .logo-content {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
  }

  .logo-title {
    color: #fff;
    font-size: 15px;
    margin: 0;
    white-space: nowrap;
    font-weight: 600;
    flex-shrink: 0;
  }

  .logo-title-collapsed {
    color: #fff;
    font-size: 20px;
    margin: 0;
    text-align: center;
  }

  .toggle-btn {
    flex-shrink: 0;
    width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    margin: 0 -8px 0 8px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #bfcbd9 !important;
    border-radius: 4px;
    transition: all 0.3s ease;
  }

  .toggle-btn:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #409eff !important;
  }

  .toggle-btn .el-icon {
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s ease;
  }

  .toggle-btn .icon-rotate {
    transform: scaleX(-1);
  }

  .header {
    background: #fff;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    flex-shrink: 0;
    height: 60px;
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
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s ease;
  }

  .user-info:hover {
    background-color: #f5f7fa;
    color: #409EFF;
  }

  .user-info .el-icon {
    transition: all 0.2s ease;
  }

  .main-content {
    background-color: #f5f7fa;
    padding: 20px;
    overflow-y: auto;
    flex: 1;
  }

  .mobile-header {
    display: none;
  }
}

/* ========== 移动端样式 ========== */
@media (max-width: 767px) {
  .layout-container {
    flex-direction: column;
  }

  .sidebar {
    display: none;
  }

  .header {
    display: none;
  }

  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    flex-shrink: 0;
    height: 56px;
    z-index: 100;
    border-bottom: 1px solid #f0f0f0;
  }

  .menu-btn {
    font-size: 22px;
    padding: 8px;
    min-width: auto;
    width: 44px !important;
    height: 44px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .menu-btn:hover {
    background-color: rgba(64, 158, 255, 0.1) !important;
  }

  .menu-btn:active {
    background-color: rgba(64, 158, 255, 0.2) !important;
  }

  .logo-text {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0;
    flex: 1;
    text-align: center;
    white-space: nowrap;
  }

  .user-btn {
    font-size: 22px;
    padding: 8px;
    min-width: auto;
    width: 44px !important;
    height: 44px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .user-btn:hover {
    background-color: rgba(64, 158, 255, 0.1) !important;
  }

  .user-btn:active {
    background-color: rgba(64, 158, 255, 0.2) !important;
  }

  .user-dropdown {
    margin-left: 4px;
  }

  .main-content {
    background-color: #f5f7fa;
    padding: 12px 16px;
    overflow-y: auto;
    flex: 1;
  }

  /* 移动端菜单样式 */
  :deep(.el-drawer) {
    width: 280px !important;
  }

  :deep(.el-drawer__header) {
    padding: 16px;
    border-bottom: 1px solid #ebeef5;
    margin-bottom: 0;
  }

  :deep(.el-drawer__title) {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
  }

  :deep(.el-drawer__body) {
    padding: 0 !important;
    overflow-y: auto;
  }

  :deep(.el-drawer__close) {
    width: 44px;
    height: 44px;
    font-size: 18px;
  }

  :deep(.el-menu) {
    border: none;
  }

  /* 移动端菜单项优化 */
  :deep(.el-menu--vertical.el-menu) {
    border-right: none;
  }

  :deep(.el-menu-item) {
    height: 52px !important;
    line-height: 52px !important;
    padding: 0 16px !important;
    font-size: 15px;
    transition: all 0.2s ease;
  }

  :deep(.el-menu-item .el-icon) {
    margin-right: 12px !important;
    font-size: 18px;
    transition: all 0.2s ease;
  }

  :deep(.el-menu-item:hover) {
    background-color: rgba(64, 158, 255, 0.1) !important;
  }

  :deep(.el-menu-item.is-active) {
    background-color: rgba(64, 158, 255, 0.15) !important;
    border-right: 3px solid #409EFF;
    color: #409EFF !important;
    padding-right: 13px !important;
  }

  :deep(.el-menu-item.is-active .el-icon) {
    color: #409EFF;
  }
}

/* ========== 通用样式 ========== */
.layout-container {
  width: 100%;
}

:deep(.el-container) {
  display: flex;
  flex-direction: column;
}

/* Element Plus 菜单样式优化 */
:deep(.el-menu) {
  transition: width 0.3s ease;
}

:deep(.el-menu-item) {
  height: 48px !important;
  line-height: 48px !important;
  transition: all 0.2s ease;
}

:deep(.el-menu-item .el-icon) {
  margin-right: 10px !important;
  transition: all 0.2s ease;
  font-size: 16px;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #409EFF !important;
}

:deep(.el-menu-item:hover .el-icon) {
  color: #409EFF;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(64, 158, 255, 0.2) !important;
  border-left: 3px solid #409EFF;
  padding-left: 9px !important;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #409EFF;
}

/* PC端菜单折叠样式 */
:deep(.el-menu--collapse) {
  width: 64px;
}

:deep(.el-menu--collapse .el-menu-item) {
  padding: 0 !important;
  text-align: center;
}

:deep(.el-menu--collapse .el-menu-item span) {
  display: none;
}

:deep(.el-menu--collapse .el-menu-item [class*='el-icon']) {
  margin: 0 !important;
}

:deep(.el-menu--collapse .el-menu-item.is-active) {
  border-left: none;
  border-bottom: 3px solid #409EFF;
  padding-left: 0 !important;
}

/* 全局下拉菜单样式优化 */
:deep(.el-dropdown-menu) {
  min-width: 160px;
  border-radius: 4px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #ebeef5;
  overflow: hidden;
}

:deep(.el-dropdown-menu__item) {
  height: 44px;
  line-height: 44px;
  padding: 0 16px;
  font-size: 14px;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f5f7fa;
  color: #409EFF;
}

:deep(.el-dropdown-menu__item .el-icon) {
  margin-right: 8px;
  transition: all 0.2s ease;
}

/* 菜单项工具提示 */
:deep(.el-popper.is-dark) {
  background-color: rgba(16, 16, 16, 0.95);
  border-color: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  font-size: 12px;
  padding: 8px 12px;
}

:deep(.el-popper.is-dark[role='tooltip'] .popper__arrow::after) {
  border-top-color: rgba(16, 16, 16, 0.95);
}

/* 收起状态下侧边栏的额外优化 */
@media (min-width: 768px) {
  .sidebar.collapsed .logo {
    padding: 0;
    justify-content: center;
  }

  .sidebar.collapsed .logo-content {
    flex: 0;
  }

  .sidebar.collapsed .toggle-btn {
    margin: 0 !important;
  }
}
</style>
