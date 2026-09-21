/** 文章/来源/任务契约（snake_case，与后端 core/models 响应字段一一对应）。 */

export interface Entity {
  type: string
  name: string
  confidence: number | null
}

export interface Article {
  id: string
  source_id: string
  title: string
  url: string
  raw_url?: string | null
  content?: string | null
  summary?: string | null
  author?: string | null
  published_at?: string | null
  detected_lang?: string | null
  translated_lang?: string | null
  content_translated?: string | null
  country?: string | null
  source_type: string
  tags: string[]
  entities?: Entity[]
  categories: string[]
  cluster_id?: string | null
  raw_snapshot_key?: string | null
  status: string
  ext_json?: Record<string, unknown>
}

export interface SourceOverviewItem {
  id: string
  name: string
  country: string | null
  type: string
  adapter_key: string
  enabled: boolean
  article_count: number
  last_published_at: string | null
}

export interface PageResult<T> {
  items: T[]
  page: number
  page_size: number
  total: number
}
