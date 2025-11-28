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
      {
        path: 'new-highs',
        name: 'NewHighsAnalysis',
        component: () => import('@/views/reports/NewHighsAnalysis.vue'),
        meta: { title: '创新高分析' },
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
  const adminToken = localStorage.getItem('admin_access_token')
  const clientToken = localStorage.getItem('client_access_token')
  const requiresAuth = to.meta.requiresAuth !== false

  // 判断是否访问管理员路径
  const isAdminPath = to.path.startsWith('/admin')
  const hasAdminToken = !!adminToken
  const hasClientToken = !!clientToken

  console.log('[Router Guard] 路由检查:', {
    path: to.path,
    isAdminPath,
    hasAdminToken,
    hasClientToken,
    requiresAuth,
  })

  // 1. 需要登录但没有相应的 token
  // 允许跨身份认证：用户可以访问另一个身份的登录页面来切换认证
  if (requiresAuth) {
    if (isAdminPath && !hasAdminToken) {
      // 管理员路径需要 admin token，重定向到管理员登录页面
      // 允许客户端用户访问 /admin-login 来登录为管理员
      console.log('[Router Guard] 管理员路径需要 admin token，重定向到管理员登录页')
      next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
      return
    }
    if (!isAdminPath && !hasClientToken) {
      // 客户端路径需要 client token，重定向到客户端登录页面
      // 允许管理员用户访问 /login 来登录为客户端
      console.log('[Router Guard] 客户端路径需要 client token，重定向到登录页')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  // 2. 已登录访问登录页，重定向到对应的首页
  // 允许跨身份认证：客户端用户可以访问 /admin-login 来登录为管理员，反之亦然
  if (to.name === 'Login' && hasClientToken) {
    // 客户端用户访问 /login，已有客户端登录，重定向到主页
    console.log('[Router Guard] Client user 已登录，重定向到 /')
    next({ path: '/' })
    return
  }

  if (to.name === 'AdminLogin' && hasAdminToken) {
    // 管理员用户访问 /admin-login，已有管理员登录，重定向到管理员页面
    console.log('[Router Guard] Admin user 已登录，重定向到 /admin')
    next({ path: '/admin' })
    return
  }

  // 否则允许访问登录页（用户可以通过登录来切换身份）

  // 3. 角色权限检查和强化登出逻辑
  const requiredRole = to.meta.requiredRole as string | undefined
  const requiresSubscription = to.meta.requiresSubscription as boolean | undefined

  // 特殊处理：'customer' 角色表示"需要 client token 的任何客户用户"（VIP或NORMAL）
  const isRequiredRoleCustomer = requiredRole === 'customer'

  if (requiredRole && (hasAdminToken || hasClientToken)) {
    // 对于 'customer' 角色，检查是否有 client token（不检查具体的 role 值）
    if (isRequiredRoleCustomer && hasClientToken) {
      console.log('[Router Guard] 客户端用户已验证，继续检查订阅状态...')
      // 确保用户信息已加载
      if (!authStore.clientUser) {
        authStore.fetchClientUser().then(() => {
          if (requiresSubscription && !authStore.hasValidSubscription) {
            console.warn('User subscription expired or invalid')
            next({ name: 'SubscriptionExpired', query: { redirect: to.fullPath } })
          } else {
            next()
          }
        }).catch(() => {
          localStorage.removeItem('client_access_token')
          localStorage.removeItem('client_refresh_token')
          next({ name: 'Login', query: { redirect: to.fullPath } })
        })
      } else {
        if (requiresSubscription && !authStore.hasValidSubscription) {
          console.warn('User subscription expired or invalid')
          next({ name: 'SubscriptionExpired', query: { redirect: to.fullPath } })
        } else {
          next()
        }
      }
      return
    }

    // 对于其他角色（如 'admin'），使用 hasRole 检查
    if (!isRequiredRoleCustomer && (hasAdminToken || hasClientToken)) {
      // 确保用户信息已加载
      const currentUser = isAdminPath ? authStore.adminUser : authStore.clientUser

      if (!currentUser) {
        console.log('[Router Guard] 用户信息未加载，正在获取...')
        const fetchPromise = isAdminPath ? authStore.fetchAdminUser() : authStore.fetchClientUser()

        fetchPromise
          .then(() => {
            const user = isAdminPath ? authStore.adminUser : authStore.clientUser
            if (!user || !authStore.hasRole(requiredRole)) {
              console.warn(`User does not have required role: ${requiredRole}`)
              // 角色不匹配，强制登出并重定向到合适的登录页
              if (isAdminPath) {
                authStore.logout('admin')
                next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
              } else {
                authStore.logout('client')
                next({ name: 'Login', query: { redirect: to.fullPath } })
              }
            } else {
              next()
            }
          })
          .catch(() => {
            // token 无效，清除并重定向到登录页
            console.error('[Router Guard] 获取用户信息失败，token 可能无效')
            if (isAdminPath) {
              localStorage.removeItem('admin_access_token')
              localStorage.removeItem('admin_refresh_token')
              next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
            } else {
              localStorage.removeItem('client_access_token')
              localStorage.removeItem('client_refresh_token')
              next({ name: 'Login', query: { redirect: to.fullPath } })
            }
          })
        return
      }

      if (!authStore.hasRole(requiredRole)) {
        console.warn(`User does not have required role: ${requiredRole}`)
        // 角色不匹配，强制登出并重定向到合适的登录页
        if (isAdminPath) {
          authStore.logout('admin')
          next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
        } else {
          authStore.logout('client')
          next({ name: 'Login', query: { redirect: to.fullPath } })
        }
        return
      }

      next()
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