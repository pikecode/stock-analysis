import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/stocks',
      },
      {
        path: 'stocks',
        name: 'Stocks',
        component: () => import('@/views/stocks/StockList.vue'),
        meta: { title: '股票列表' },
      },
      {
        path: 'stocks/:code',
        name: 'StockDetail',
        component: () => import('@/views/stocks/StockDetail.vue'),
        meta: { title: '股票详情' },
      },
      {
        path: 'concepts',
        name: 'Concepts',
        component: () => import('@/views/concepts/ConceptList.vue'),
        meta: { title: '概念列表' },
      },
      {
        path: 'concepts/:id',
        name: 'ConceptDetail',
        component: () => import('@/views/concepts/ConceptDetail.vue'),
        meta: { title: '概念详情' },
      },
      {
        path: 'rankings',
        name: 'Rankings',
        component: () => import('@/views/rankings/RankingView.vue'),
        meta: { title: '排名查询' },
      },
      {
        path: 'import',
        name: 'Import',
        component: () => import('@/views/import/ImportView.vue'),
        meta: { title: '数据导入' },
      },
      {
        path: 'import/batches',
        name: 'ImportBatches',
        component: () => import('@/views/import/BatchList.vue'),
        meta: { title: '导入记录' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
