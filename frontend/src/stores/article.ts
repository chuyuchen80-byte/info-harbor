import { defineStore } from 'pinia'

import http from '@/services/http'
import type { Article, PageResult } from '@/types/article'

export const useArticleStore = defineStore('article', {
  state: () => ({
    articles: [] as Article[],
    total: 0,
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchArticles(params?: Record<string, unknown>) {
      this.loading = true
      this.error = null
      try {
        const res = await http.get<PageResult<Article>>('/articles', { params })
        this.articles = res.data.items
        this.total = res.data.total
      } catch (e) {
        this.error = e instanceof Error ? e.message : String(e)
      } finally {
        this.loading = false
      }
    },
  },
})
