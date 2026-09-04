<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import {
  NButton,
  NCard,
  NDataTable,
  NSwitch,
  NTag,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'

import { useSourceStore } from '@/stores/source'
import { useTaskStore } from '@/stores/task'
import type { SourceItem } from '@/types/source'

const message = useMessage()
const sourceStore = useSourceStore()
const taskStore = useTaskStore()
const triggering = ref<string | null>(null)

const typeLabel: Record<string, string> = {
  media: '媒体',
  api: 'API',
  rss: 'RSS',
  arxiv: 'arXiv',
  github: 'GitHub',
}

const columns: DataTableColumns<SourceItem> = [
  {
    title: '来源名称',
    key: 'name',
    render: (row) =>
      h('span', [
        h('span', { class: 'src-name' }, row.name),
        h('span', { class: 'src-id mono' }, row.id),
      ]),
  },
  {
    title: '国家',
    key: 'country',
    render: (row) => h(NTag, { size: 'small', bordered: false }, { default: () => row.country ?? '—' }),
  },
  {
    title: '类型',
    key: 'type',
    render: (row) =>
      h(
        NTag,
        { size: 'small', bordered: false, type: row.type === 'api' ? 'info' : 'default' },
        { default: () => typeLabel[row.type] ?? row.type },
      ),
  },
  {
    title: '适配器',
    key: 'adapter_key',
    render: (row) => h('span', { class: 'mono' }, row.adapter_key),
  },
  {
    title: '频道',
    key: 'channels',
    render: (row) => String(row.config?.channels?.length ?? '—'),
  },
  { title: '权重', key: 'weight' },
  {
    title: '启用',
    key: 'enabled',
    render: (row) =>
      h(NSwitch, {
        value: row.enabled,
        size: 'small',
        'onUpdate:value': async (v: boolean) => {
          try {
            await sourceStore.updateSource(row.id, { enabled: v })
            message.success(`「${row.name}」已${v ? '启用' : '停用'}`)
          } catch (e) {
            message.error(`更新失败：${(e as Error).message}`)
          }
        },
      }),
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(
        NButton,
        {
          size: 'small',
          type: 'primary',
          loading: triggering.value === row.id,
          onClick: () => trigger(row),
        },
        { default: () => '立即抓取' },
      ),
  },
]

async function trigger(row: SourceItem) {
  triggering.value = row.id
  try {
    await sourceStore.triggerCrawl(row.id)
    message.success(`已触发「${row.name}」抓取，任务入队成功`)
    await taskStore.fetchTasks({ page: 1 })
  } catch (e) {
    message.error(`触发失败：${(e as Error).message}`)
  } finally {
    triggering.value = null
  }
}

onMounted(() => sourceStore.fetchSources())
</script>

<template>
  <NCard :bordered="false" class="admin-card">
    <div class="head-row">
      <span class="head-desc">
        共 {{ sourceStore.sources.length }} 个源 · 启用 {{ sourceStore.sources.filter((s) => s.enabled).length }} 个 ·
        定时抓取间隔由服务端 HARBOR_CRAWL_INTERVAL_HOURS 配置
      </span>
      <NButton size="small" :loading="sourceStore.loading" @click="sourceStore.fetchSources()">刷新</NButton>
    </div>
    <NDataTable
      :columns="columns"
      :data="sourceStore.sources"
      :bordered="false"
      size="small"
      :row-key="(row: SourceItem) => row.id"
    />
  </NCard>
</template>

<style scoped>
.head-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.head-desc { font-size: 13px; color: var(--text-2); }
.src-name { font-weight: 600; margin-right: 8px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: var(--text-2); }
.admin-card { border-radius: 12px; }
</style>
