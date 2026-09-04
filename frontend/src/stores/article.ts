import { defineStore } from 'pinia'

import http from '@/services/http'
import type { Article, PageResult, SourceOverviewItem } from '@/types/article'

export interface ArticleFilters {
  country: string | null
  sourceId: string | null
}

/** 文章状态：真实分页列表 + 来源概况（筛选维度 M1 仅国家/来源，评分/时间待管道就绪）。 */
export const useArticleStore = defineStore('article', {
  state: () => ({
    articles: [] as Article[],
    total: 0,
    page: 1,
    pageSize: 20,
    sort: 'published_at' as 'published_at' | 'created_at',
    filters: { country: null, sourceId: null } as ArticleFilters,
    overview: [] as SourceOverviewItem[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchList() {
      this.loading = true
      this.error = null
      try {
        const res = await http.get<PageResult<Article>>('/articles', {
          params: {
            page: this.page,
            page_size: this.pageSize,
            sort: this.sort,
            ...(this.filters.country ? { country: this.filters.country } : {}),
            ...(this.filters.sourceId ? { source_id: this.filters.sourceId } : {}),
          },
        })
        this.articles = res.data.items
        this.total = res.data.total
      } catch (e) {
        this.error = e instanceof Error ? e.message : String(e)
      } finally {
        this.loading = false
      }
    },
    async fetchDetail(id: string): Promise<Article | null> {
      try {
        const res = await http.get<Article>(`/articles/${id}`)
        return res.data
      } catch {
        return null
      }
    },
    async fetchOverview() {
      try {
        const res = await http.get<SourceOverviewItem[]>('/sources/overview')
        this.overview = res.data
      } catch {
        this.overview = []
      }
    },
    setFilter(key: keyof ArticleFilters, value: string | null) {
      this.filters[key] = value
      this.page = 1
      void this.fetchList()
    },
    setSort(sort: string) {
      this.sort = sort === 'created_at' ? 'created_at' : 'published_at'
      this.page = 1
      void this.fetchList()
    },
    setPage(page: number) {
      this.page = page
      void this.fetchList()
    },
    resetFilters() {
      this.filters = { country: null, sourceId: null }
      this.sort = 'published_at'
      this.page = 1
      void this.fetchList()
    },
  },
})
