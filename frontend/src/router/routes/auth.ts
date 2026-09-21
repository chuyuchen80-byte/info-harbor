import type { RouteRecordRaw } from 'vue-router'

export const authRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    // fullscreen：登录页脱离全局壳（不渲染导航/页脚），左右分屏布局
    meta: { title: '登录', role: 'guest', fullscreen: true },
  },
]
