import type { RouteRecordRaw } from 'vue-router'

export const searchRoutes: RouteRecordRaw[] = [
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchView.vue'),
    meta: { title: '搜索', role: 'guest' },
  },
]
