<script setup lang="ts">
import { h, onMounted, onUnmounted, ref } from 'vue'
import {
  NCard,
  NDataTable,
  NSelect,
  NTag,
  type DataTableColumns,
} from 'naive-ui'

import { useSourceStore } from '@/stores/source'
import { useTaskStore } from '@/stores/task'
import type { CrawlTaskItem } from '@/types/task'
import { dateTime, durationSeconds } from '@/utils/format'

const sourceStore = useSourceStore()
const taskStore = useTaskStore()

const sourceId = ref('')
const taskStatus = ref('')
const timer = window.setInterval(() => refresh(), 5000) // 任务进行中自动刷新

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
const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '排队中', value: 'queued' },
  { label: '抓取中', value: 'running' },
  { label: '成功', value: 'succeeded' },
  { label: '失败', value: 'failed' },
]

const columns: DataTableColumns<CrawlTaskItem> = [
  { title: '任务', key: 'id', render: (row) => h('span', { class: 'mono' }, row.id.slice(0, 8)) },
  {
    title: '数据源',
    key: 'source_id',
    render: (row) =>
      h('span', null, sourceStore.sources.find((s) => s.id === row.source_id)?.name ?? row.source_id),
  },
  {
    title: '类型',
    key: 'task_type',
    render: (row) => h(NTag, { size: 'small', bordered: false }, { default: () => (row.task_type === 'manual' ? '手动' : '定时') }),
  },
  {
    title: '状态',
    key: 'status',
    render: (row) =>
      h(NTag, { size: 'small', bordered: false, type: statusType[row.status] }, { default: () => statusLabel[row.status] }),
  },
  { title: '新增条数', key: 'result_count' },
  {
    title: '耗时',
    key: 'duration',
    render: (row) => h('span', { class: 'mono' }, durationSeconds(row.started_at, row.finished_at)),
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row) => h('span', { class: 'mono' }, dateTime(row.created_at)),
  },
  {
    title: '错误',
    key: 'error',
    ellipsis: { tooltip: true },
    render: (row) => h('span', { class: row.error ? 'err' : '' }, row.error ?? '—'),
  },
]

async function refresh() {
  await taskStore.fetchTasks({
    source_id: sourceId.value || undefined,
    task_status: taskStatus.value || undefined,
    page: 1,
    page_size: 50,
  })
}

function sourceOptions() {
  return [
    { label: '全部来源', value: '' },
    ...sourceStore.sources.map((s) => ({ label: s.name, value: s.id })),
  ]
}

onMounted(async () => {
  await sourceStore.fetchSources()
  await refresh()
})
onUnmounted(() => window.clearInterval(timer))
</script>

<template>
  <NCard :bordered="false" class="admin-card">
    <div class="head-row">
      <span class="head-desc">最近任务 · 每 5 秒自动刷新（页面停留期间）</span>
      <div class="filters">
        <NSelect
          v-model:value="sourceId"
          :options="sourceOptions()"
          size="small"
          style="width: 160px"
          @update:value="refresh"
        />
        <NSelect
          v-model:value="taskStatus"
          :options="statusOptions"
          size="small"
          style="width: 140px"
          @update:value="refresh"
        />
      </div>
    </div>
    <NDataTable
      :columns="columns"
      :data="taskStore.tasks"
      :bordered="false"
      size="small"
      :loading="taskStore.loading"
      :row-key="(row: CrawlTaskItem) => row.id"
    />
  </NCard>
</template>

<style scoped>
.head-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.head-desc { font-size: 13px; color: var(--text-2); }
.filters { display: flex; gap: 8px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: var(--text-2); }
.err { color: var(--danger-text); font-size: 12px; }
.admin-card { border-radius: 12px; }
</style>
