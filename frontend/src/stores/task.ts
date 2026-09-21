import { defineStore } from 'pinia'

import http from '@/services/http'
import type { TaskPage } from '@/types/task'

/** 抓取任务状态（M1 任务监控）：筛选 + 分页，轮询由组件层定时调用。 */
export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [] as TaskPage['items'],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchTasks(params?: { source_id?: string; task_status?: string; page?: number; page_size?: number }) {
      this.loading = true
      this.error = null
      try {
        const res = await http.get<TaskPage>('/tasks', { params })
        this.tasks = res.data.items
        this.total = res.data.total
        this.page = res.data.page
        this.pageSize = res.data.page_size
      } catch (e) {
        this.error = e instanceof Error ? e.message : String(e)
      } finally {
        this.loading = false
      }
    },
  },
})
