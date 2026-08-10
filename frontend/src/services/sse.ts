/** SSE 事件中心（§6.6）：事件类型注册 handler，新事件零改动核心逻辑。 */

export type SseEventName = 'article.ready' | 'task.progress'

type SseHandler = (payload: unknown) => void

export function createEventSource(): EventSource {
  return new EventSource(import.meta.env.VITE_SSE_URL ?? '/api/v1/stream')
}

// TODO(MVP)：接入后端 /stream 后，在此按事件类型注册 handler 分发
export function attachSseHandlers(source: EventSource, handlers: Partial<Record<SseEventName, SseHandler>>): void {
  source.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as { type?: SseEventName; payload?: unknown }
      const handler = data.type ? handlers[data.type] : undefined
      handler?.(data.payload)
    } catch {
      // 忽略非 JSON 消息
    }
  }
}
