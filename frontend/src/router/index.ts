import { createRouter, createWebHistory } from 'vue-router'

import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 页面级权限：/admin 需登录（meta.role=admin）且角色匹配才放行。
// 角色以 authStore.user.role（/auth/me 实时拉取）为准；路由守卫 + 页面内兜底双保险。
router.beforeEach(async (to) => {
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
