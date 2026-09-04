import { defineStore } from 'pinia'

import http from '@/services/http'
import type { SourceItem, SourceUpdatePayload } from '@/types/source'

/** 数据源状态（M1 管理页）：列表 + 启停 + 手动触发。 */
export const useSourceStore = defineStore('source', {
  state: () => ({
    sources: [] as SourceItem[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchSources() {
      this.loading = true
      this.error = null
      try {
        const res = await http.get<SourceItem[]>('/sources')
        this.sources = res.data
      } catch (e) {
        this.error = e instanceof Error ? e.message : String(e)
      } finally {
        this.loading = false
      }
    },
    async updateSource(id: string, payload: SourceUpdatePayload) {
      const res = await http.patch<SourceItem>(`/sources/${id}`, payload)
      const idx = this.sources.findIndex((s) => s.id === id)
      if (idx >= 0) this.sources[idx] = res.data
      return res.data
    },
    async triggerCrawl(id: string) {
      const res = await http.post(`/sources/${id}/crawl`)
      return res.data as { id: string; status: string }
    },
  },
})
