import type { RouteRecordRaw } from 'vue-router'

export const articleRoutes: RouteRecordRaw[] = [
  {
    path: '/articles',
    name: 'article-list',
    component: () => import('@/views/ArticleListView.vue'),
    meta: { title: '文章列表', role: 'guest' },
  },
  {
    path: '/articles/:id',
    name: 'article-detail',
    component: () => import('@/views/ArticleDetailView.vue'),
    meta: { title: '文章详情', role: 'guest' },
  },
]
