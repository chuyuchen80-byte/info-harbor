<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { NCard, NTag } from 'naive-ui'

import { useSourceStore } from '@/stores/source'
import { useTaskStore } from '@/stores/task'
import { dateTime, durationSeconds } from '@/utils/format'
import type { CrawlTaskItem } from '@/types/task'

const sourceStore = useSourceStore()
const taskStore = useTaskStore()

const statusType: Record<string, 'default' | 'info' | 'success' | 'error'> = {
  queued: 'default',
  running: 'info',
  succeeded: 'success',
  failed: 'error',
}
const statusLabel: Record<string, string> = {
  queued: '排队中',
  running: '抓取中',
  succeeded: '成功',
  failed: '失败',
}

const stats = computed(() => {
  const tasks = taskStore.tasks
  const finished = tasks.filter((t) => t.status === 'succeeded' || t.status === 'failed')
  return {
    sources: sourceStore.sources.length,
    enabled: sourceStore.sources.filter((s) => s.enabled).length,
    succeeded: tasks.filter((t) => t.status === 'succeeded').length,
    failed: tasks.filter((t) => t.status === 'failed').length,
    running: tasks.filter((t) => t.status === 'running' || t.status === 'queued').length,
    totalArticles: tasks.reduce((sum, t) => sum + t.result_count, 0),
    successRate: finished.length ? Math.round((finished.filter((t) => t.status === 'succeeded').length / finished.length) * 100) : null,
  }
})

/** 每个源最近一次任务（按 source_id 取最新）。 */
const latestBySource = computed<CrawlTaskItem[]>(() => {
  const map = new Map<string, CrawlTaskItem>()
  for (const t of taskStore.tasks) {
    if (!map.has(t.source_id)) map.set(t.source_id, t)
  }
  return [...map.values()]
})

function sourceName(id: string): string {
  return sourceStore.sources.find((s) => s.id === id)?.name ?? id
}

onMounted(async () => {
  await Promise.all([sourceStore.fetchSources(), taskStore.fetchTasks({ page: 1 })])
})
</script>

<template>
  <div class="crawler-overview">
    <div class="stat-row">
      <NCard :bordered="false" class="stat-card">
        <div class="stat-value">{{ stats.sources }}</div>
        <div class="stat-label">数据源</div>
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <div class="stat-value">{{ stats.enabled }}</div>
        <div class="stat-label">启用中</div>
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <div class="stat-value running">{{ stats.running }}</div>
        <div class="stat-label">进行中任务</div>
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <div class="stat-value ok">{{ stats.succeeded }}</div>
        <div class="stat-label">成功 / 失败 {{ stats.failed }}</div>
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <div class="stat-value">{{ stats.totalArticles }}</div>
        <div class="stat-label">累计入库条数</div>
      </NCard>
    </div>

    <div class="latest-title">各源最近一次抓取</div>
    <div class="latest-grid">
      <NCard v-for="t in latestBySource" :key="t.id" :bordered="false" class="latest-card">
        <div class="latest-head">
          <span class="latest-name">{{ sourceName(t.source_id) }}</span>
          <NTag size="small" :bordered="false" :type="statusType[t.status]">
            {{ statusLabel[t.status] }}
          </NTag>
        </div>
        <div class="latest-meta mono">
          任务 {{ t.id.slice(0, 8) }} · {{ t.task_type === 'manual' ? '手动' : '定时' }} ·
          新增 {{ t.result_count }} 条 · 耗时 {{ durationSeconds(t.started_at, t.finished_at) }}
        </div>
        <div class="latest-meta">开始：{{ dateTime(t.started_at) }} · 结束：{{ dateTime(t.finished_at) }}</div>
        <div v-if="t.error" class="latest-error">{{ t.error }}</div>
      </NCard>
      <div v-if="latestBySource.length === 0" class="empty">暂无运行记录 —— 在「源管理」里点「立即抓取」试试</div>
    </div>
  </div>
</template>

<style scoped>
.crawler-overview { display: flex; flex-direction: column; gap: 16px; }
.stat-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
.stat-card { border-radius: 12px; text-align: center; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--brand); }
.stat-value.running { color: var(--info); }
.stat-value.ok { color: var(--ok); }
.stat-label { font-size: 12px; color: var(--text-2); margin-top: 2px; }
.latest-title { font-weight: 600; font-size: 14px; }
.latest-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }
.latest-card { border-radius: 12px; }
.latest-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.latest-name { font-weight: 600; }
.latest-meta { font-size: 12px; color: var(--text-2); line-height: 1.8; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
.latest-error {
  margin-top: 6px; font-size: 12px; color: var(--danger-text); background: var(--danger-soft);
  border-radius: 6px; padding: 6px 8px; word-break: break-all;
}
.empty { font-size: 13px; color: var(--text-3); }
</style>
