/** 格式化工具：时间 / 相对时间 / 分数（对齐原型 utils/format，供全部页面使用）。 */

const MIN = 60_000
const HOUR = 3_600_000
const DAY = 24 * HOUR

/** 宽松解析：后端无时区后缀的字符串按本地时间处理（统一时区治理见 TECH_DEBT T10）。 */
function parse(value: string | null | undefined): number | null {
  if (!value) return null
  const t = new Date(value).getTime()
  return Number.isNaN(t) ? null : t
}

export function timeAgo(iso: string | null | undefined): string {
  const t = parse(iso)
  if (t == null) return '—'
  const diff = Date.now() - t
  if (diff < MIN) return '刚刚'
  if (diff < HOUR) return `${Math.floor(diff / MIN)} 分钟前`
  if (diff < DAY) return `${Math.floor(diff / HOUR)} 小时前`
  if (diff < 7 * DAY) return `${Math.floor(diff / DAY)} 天前`
  return dateShort(iso)
}

export function dateShort(iso: string | null | undefined): string {
  const t = parse(iso)
  if (t == null) return '—'
  const d = new Date(t)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

export function dateTime(value: string | null | undefined): string {
  const t = parse(value)
  if (t == null) return '—'
  const d = new Date(t)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

export function durationSeconds(startedAt: string | null, finishedAt: string | null): string {
  const start = parse(startedAt)
  if (start == null) return '—'
  const end = parse(finishedAt) ?? Date.now()
  const seconds = Math.max(0, Math.round((end - start) / 1000))
  if (seconds < 60) return `${seconds}s`
  return `${Math.floor(seconds / 60)}m${seconds % 60}s`
}

export function formatScore(n: number | null | undefined): string {
  if (n == null) return '—'
  return Number.isInteger(n) ? String(n) : n.toFixed(1)
}

export type ScoreTone = 'great' | 'good' | 'fair' | 'poor'

export function scoreTone(score: number | null | undefined): ScoreTone {
  if (score == null) return 'poor'
  if (score >= 80) return 'great'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}
