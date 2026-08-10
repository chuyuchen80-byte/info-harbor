import { createRouter, createWebHistory } from 'vue-router'

import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 页面级权限从第一天预留（§6.6）：meta.role 后期接入 JWT 校验
router.beforeEach((to) => {
  document.title = to.meta.title ? `${String(to.meta.title)} · info-harbor` : 'info-harbor'
  return true
})

export default router
