import type { RouteRecordRaw } from 'vue-router'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/admin/AdminView.vue'),
    // 权限从第一天预留（§6.6）：路由 meta 携带 role/permission
    meta: { title: '管理后台', role: 'admin' },
  },
]
