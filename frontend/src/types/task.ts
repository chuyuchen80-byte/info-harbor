/** 抓取任务契约（对应后端 core/models.TaskOut）。 */

export type CrawlTaskStatus = 'queued' | 'running' | 'succeeded' | 'failed'

export interface CrawlTaskItem {
  id: string
  source_id: string
  status: CrawlTaskStatus
  task_type: 'manual' | 'scheduled'
  arq_job_id: string | null
  result_count: number
  error: string | null
  created_at: string | null
  started_at: string | null
  finished_at: string | null
}

export interface TaskPage {
  items: CrawlTaskItem[]
  total: number
  page: number
  page_size: number
}
