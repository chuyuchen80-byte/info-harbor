import type { RouteRecordRaw } from 'vue-router'

export const sourceRoutes: RouteRecordRaw[] = [
  {
    path: '/sources',
    name: 'sources',
    component: () => import('@/views/SourceView.vue'),
    meta: { title: '来源', role: 'guest' },
  },
]
