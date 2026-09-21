/** 数据源契约（对应后端 core/models.Source）。 */

export interface SourceChannel {
  channel_id: number
  name: string
  alias?: string
}

export interface SourceConfig {
  base_url?: string
  max_pages_per_channel?: number
  page_size?: number
  channels?: SourceChannel[]
  [key: string]: unknown
}

export interface SourceItem {
  id: string
  name: string
  country: string | null
  type: string
  adapter_key: string
  weight: number
  enabled: boolean
  health: Record<string, unknown>
  config?: SourceConfig
}

export interface SourceUpdatePayload {
  enabled?: boolean
  weight?: number
}
