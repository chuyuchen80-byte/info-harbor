import type { RouteRecordRaw } from 'vue-router'

export const countryRoutes: RouteRecordRaw[] = [
  {
    path: '/countries',
    name: 'countries',
    component: () => import('@/views/CountryView.vue'),
    meta: { title: '国家/地区', role: 'guest' },
  },
]
