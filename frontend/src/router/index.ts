import { createRouter, createWebHistory } from 'vue-router'

import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 页面级权限：meta.role 预留（§6.6）。
// 当前规则：带 meta.role 且非 guest 的页面未登录 → 跳登录页。
// TODO(RBAC)：拉取 /auth/me 后按 meta.role（如 'admin'）对比 store.user.role。
router.beforeEach((to) => {
  document.title = to.meta.title ? `${String(to.meta.title)} · info-harbor` : 'info-harbor'

  const token = localStorage.getItem('harbor_token')
  const requiresAuth = to.meta.role && to.meta.role !== 'guest'
  if (requiresAuth && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  // 已登录访问登录页 → 回首页
  if (to.path === '/login' && token) {
    return '/'
  }
  return true
})

export default router
