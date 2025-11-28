import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

const routes: RouteRecordRaw[] = [
  // ========== 公开页面（无需登录） ==========
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/public/HomePage.vue'),
    meta: { requiresAuth: false, title: '首页' },
  },
  {
    path: '/stocks',
    name: 'PublicStocks',
    component: () => import('@/views/public/PublicStockList.vue'),
    meta: { requiresAuth: false, title: '股票查询' },
  },
  {
    path: '/stocks/:code',
    name: 'PublicStockDetail',
    component: () => import('@/views/public/PublicStockDetail.vue'),
    meta: { requiresAuth: false, title: '股票详情' },
  },
  {
    path: '/concepts',
    name: 'PublicConcepts',
    component: () => import('@/views/public/PublicConceptList.vue'),
    meta: { requiresAuth: false, title: '概念查询' },
  },
  {
    path: '/concepts/:id',
    name: 'PublicConceptDetail',
    component: () => import('@/views/public/PublicConceptDetail.vue'),
    meta: { requiresAuth: false, title: '概念详情' },
  },
  {
    path: '/rankings',
    name: 'PublicRankings',
    component: () => import('@/views/public/PublicRankingView.vue'),
    meta: { requiresAuth: false, title: '排名榜单' },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/public/AboutPage.vue'),
    meta: { requiresAuth: false, title: '关于我们' },
  },

  // ========== 客户端需要登录的页面 ==========
  {
    path: '/reports',
    component: () => import('@/layouts/ClientLayout.vue'),
    meta: { requiresAuth: true, requiredRole: 'customer', requiresSubscription: true },
    children: [
      {
        path: '',
        name: 'Reports',
        component: () => import('@/views/reports/Dashboard.vue'),
        meta: { title: '报表总览' },
      },
      {
        path: 'concept-ranking',
        name: 'ConceptRanking',
        component: () => import('@/views/reports/ConceptStockRanking.vue'),
        meta: { title: '概念排名' },
      },
      {
        path: 'stock-trend',
        name: 'StockTrend',
        component: () => import('@/views/reports/StockConceptTrend.vue'),
        meta: { title: '股票趋势' },
      },
      {
        path: 'top-n',
        name: 'TopNAnalysis',
        component: () => import('@/views/reports/StockTopNAnalysis.vue'),
        meta: { title: 'Top N 分析' },
      },
    ],
  },

  {
    path: '/analysis',
    component: () => import('@/layouts/ClientLayout.vue'),
    meta: { requiresAuth: true, requiredRole: 'customer', requiresSubscription: true },
    children: [
      {
        path: 'portfolio',
        name: 'Portfolio',
        component: () => import('@/views/analysis/PortfolioAnalysis.vue'),
        meta: { title: '投资组合分析' },
      },
      {
        path: 'performance',
        name: 'Performance',
        component: () => import('@/views/analysis/PerformanceAnalysis.vue'),
        meta: { title: '业绩分析' },
      },
    ],
  },

  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/layouts/ClientLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'UserProfile',
        component: () => import('@/views/profile/UserProfile.vue'),
        meta: { title: '个人中心' },
      },
      {
        path: 'settings',
        name: 'UserSettings',
        component: () => import('@/views/profile/UserSettings.vue'),
        meta: { title: '账户设置' },
      },
    ],
  },

  // ========== 管理员路由（必须登录且为管理员） ==========
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiredRole: 'admin' },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '管理后台' },
      },
      {
        path: 'stocks',
        name: 'AdminStocks',
        component: () => import('@/views/stocks/StockList.vue'),
        meta: { title: '股票管理' },
      },
      {
        path: 'stocks/:code',
        name: 'AdminStockDetail',
        component: () => import('@/views/stocks/StockDetail.vue'),
        meta: { title: '股票详情' },
      },
      {
        path: 'concepts',
        name: 'AdminConcepts',
        component: () => import('@/views/concepts/ConceptList.vue'),
        meta: { title: '概念管理' },
      },
      {
        path: 'concepts/:id',
        name: 'AdminConceptDetail',
        component: () => import('@/views/concepts/ConceptDetail.vue'),
        meta: { title: '概念详情' },
      },
      {
        path: 'rankings',
        name: 'AdminRankings',
        component: () => import('@/views/rankings/RankingView.vue'),
        meta: { title: '排名查询' },
      },
      {
        path: 'import',
        name: 'AdminImport',
        component: () => import('@/views/import/ImportView.vue'),
        meta: { title: '数据导入' },
      },
      {
        path: 'import/batches',
        name: 'AdminImportBatches',
        component: () => import('@/views/import/BatchList.vue'),
        meta: { title: '导入记录' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'plans',
        name: 'AdminPlans',
        component: () => import('@/views/admin/PlanManagement.vue'),
        meta: { title: '套餐管理' },
      },
      {
        path: 'subscriptions',
        name: 'AdminSubscriptions',
        component: () => import('@/views/admin/SubscriptionManagement.vue'),
        meta: { title: '订阅管理' },
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/settings/AdminSettings.vue'),
        meta: { title: '系统设置' },
      },
    ],
  },

  // ========== 认证相关页面 ==========
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/admin-login',
    name: 'AdminLogin',
    component: () => import('@/views/AdminLogin.vue'),
    meta: { requiresAuth: false, title: '管理员登录' },
  },
  {
    path: '/subscription-expired',
    name: 'SubscriptionExpired',
    component: () => import('@/views/SubscriptionExpired.vue'),
    meta: { requiresAuth: false, title: '订阅已过期' },
  },

  // ========== 404 页面 ==========
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { requiresAuth: false },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth !== false

  // 1. 需要登录但没有 token
  if (requiresAuth && !token) {
    // 如果是访问管理员页面，重定向到管理员登录页
    if (to.path.startsWith('/admin')) {
      next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
    } else {
      // 否则重定向到普通登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
    }
    return
  }

  // 2. 已登录访问登录页，重定向到对应的首页
  if ((to.name === 'Login' || to.name === 'AdminLogin') && token) {
    if (authStore.isAdmin) {
      next({ path: '/admin' })
    } else {
      next({ path: '/' })
    }
    return
  }

  // 3. 角色权限检查
  const requiredRole = to.meta.requiredRole as string | undefined
  const requiresSubscription = to.meta.requiresSubscription as boolean | undefined

  if (requiredRole && token) {
    // 确保用户信息已加载
    if (!authStore.user) {
      authStore.fetchUser().then(() => {
        if (!authStore.hasRole(requiredRole)) {
          console.warn(`User does not have required role: ${requiredRole}`)
          // 如果是管理员页面但不是管理员，重定向到首页
          if (requiredRole === 'admin') {
            next({ path: '/' })
          } else {
            // 客户端角色不足，重定向到公开页面
            next({ path: '/' })
          }
        } else if (requiresSubscription && !authStore.hasValidSubscription) {
          // 需要订阅但订阅已过期
          console.warn('User subscription expired or invalid')
          next({ name: 'SubscriptionExpired', query: { redirect: to.fullPath } })
        } else {
          next()
        }
      }).catch(() => {
        // token 无效，清除并重定向到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        if (to.path.startsWith('/admin')) {
          next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
        } else {
          next({ name: 'Login', query: { redirect: to.fullPath } })
        }
      })
      return
    }

    if (!authStore.hasRole(requiredRole)) {
      console.warn(`User does not have required role: ${requiredRole}`)
      next({ path: '/' })
      return
    }

    if (requiresSubscription && !authStore.hasValidSubscription) {
      console.warn('User subscription expired or invalid')
      next({ name: 'SubscriptionExpired', query: { redirect: to.fullPath } })
      return
    }
  }

  next()
})

// 设置页面标题
router.afterEach((to) => {
  const title = to.meta.title as string
  document.title = title ? `${title} - Stock Analysis` : 'Stock Analysis'
})

export default router