/** 统一文章契约的前端映射（对应后端 core/models，§7）。 */

export interface Entity {
  type: string
  name: string
  confidence: number | null
}

export interface Article {
  id: string
  sourceId: string
  title: string
  url: string
  rawUrl?: string | null
  content?: string | null
  summary?: string | null
  author?: string | null
  publishedAt?: string | null
  detectedLang?: string | null
  country?: string | null
  sourceType: string
  tags: string[]
  entities?: Entity[]
  categories: string[]
  clusterId?: string | null
  status: string
  score?: Score | null
}

export interface Score {
  articleId: string
  ruleScore?: number | null
  relevance?: number | null
  timeliness?: number | null
  impact?: number | null
  credibility?: number | null
  llmModel?: string | null
  confidence?: number | null
  valueScore?: number | null
}

export interface Source {
  id: string
  name: string
  country?: string | null
  type: string
  adapterKey: string
  enabled: boolean
  health?: Record<string, unknown>
}

export interface PageResult<T> {
  items: T[]
  page: number
  pageSize: number
  total: number
}
