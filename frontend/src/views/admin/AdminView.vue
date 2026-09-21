<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NTag, useMessage } from 'naive-ui'

import LinearSliderTabs from '@/components/LinearSliderTabs.vue'
import { MOCK_SOURCES } from '@/config/mockSources'
import { useAuthStore } from '@/stores/auth'
import { useSourceStore } from '@/stores/source'
import CrawlerOverviewPane from './components/CrawlerOverviewPane.vue'
import SourceManagePane from './components/SourceManagePane.vue'
import TaskMonitorPane from './components/TaskMonitorPane.vue'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const sourceStore = useSourceStore()

const activeTab = ref('crawler')

/** 源选择器层（infoq 真实 + 4 mock 占位）。 */
const selectedSource = ref('infoq')
const realInfoq = computed(() =>
  sourceStore.sources.find((s) => s.adapter_key === 'infoq'),
)
const sourceOptions = computed(() => [
  { key: 'infoq', label: 'infoq' },
  ...MOCK_SOURCES.map((m) => ({ key: m.id, label: m.name })),
])
const activeMock = computed(() =>
  MOCK_SOURCES.find((m) => m.id === selectedSource.value),
)

onMounted(() => {
  // 页面级 RBAC 兜底（服务端才是权威：管理接口已 require_roles('admin')）
  if (authStore.user && authStore.user.role !== 'admin') {
    message.error('该页面仅管理员可见')
    router.replace('/')
  }
  void sourceStore.fetchSources()
})

watch(selectedSource, (v) => {
  if (v === 'infoq' && sourceStore.sources.length === 0) void sourceStore.fetchSources()
})
</script>

<template>
  <div class="admin-page">
    <div class="page-head">
      <h1 class="page-title">管理后台</h1>
      <span class="page-desc">数据源接入 · 抓取任务编排与监控（M1）</span>
    </div>

    <NCard class="source-selector" :bordered="false">
      <div class="selector-head">
        <span class="selector-title">数据源</span>
        <span class="selector-hint">选中查看详情（mock 为占位）</span>
      </div>
      <LinearSliderTabs v-model="selectedSource" :options="sourceOptions" />
      <div class="source-card" v-if="selectedSource === 'infoq'">
        <div class="sc-head">
          <span class="sc-name">{{ realInfoq?.name ?? 'InfoQ 中文站' }}</span>
          <NTag v-if="realInfoq" size="small" type="success" :bordered="false">真实</NTag>
          <NTag v-else size="small" type="warning" :bordered="false">加载中</NTag>
        </div>
        <div class="sc-meta">
          <span>ID {{ realInfoq?.id ?? '—' }}</span>
          <span>地区 {{ realInfoq?.country ?? 'CN' }}</span>
          <span>适配器 {{ realInfoq?.adapter_key ?? 'infoq' }}</span>
          <span>权重 {{ realInfoq?.weight ?? '—' }}</span>
        </div>
      </div>
      <div class="source-card mock" v-else-if="activeMock">
        <div class="sc-head">
          <span class="sc-name">{{ activeMock.name }}</span>
          <NTag size="small" type="default" :bordered="false">占位</NTag>
        </div>
        <div class="sc-meta">
          <span>地区 {{ activeMock.country }}</span>
          <span>类型 {{ activeMock.type }}</span>
        </div>
        <p class="sc-note">{{ activeMock.note }}</p>
      </div>
    </NCard>

    <NTabs v-model:value="activeTab" type="line" animated>
      <NTabPane name="crawler" tab="爬虫管理">
        <CrawlerOverviewPane />
      </NTabPane>
      <NTabPane name="sources" tab="源管理">
        <SourceManagePane />
      </NTabPane>
      <NTabPane name="tasks" tab="任务监控">
        <TaskMonitorPane />
      </NTabPane>
      <NTabPane name="scoring" tab="评分调试">
        <div class="pane-placeholder">LLM 评分管道 V2 接入后开放（权重滑条 / 评分雷达）</div>
      </NTabPane>
      <NTabPane name="rules" tab="筛选规则">
        <div class="pane-placeholder">规则初筛 V2 接入后开放（关键词黑白名单 / 阈值配置）</div>
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 8px; }
.page-head { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-1); }
.page-desc { font-size: 13px; color: var(--text-2); }
.pane-placeholder {
  padding: 48px 0;
  text-align: center;
  color: var(--text-3);
  font-size: 13px;
}
.source-selector {
  border-radius: 12px;
}
.selector-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 10px;
}
.selector-title { font-size: 14px; font-weight: 700; color: var(--text-1); }
.selector-hint { font-size: 12px; color: var(--text-3); }
.source-card {
  margin-top: 16px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
}
.source-card.mock { background: var(--bg-soft); }
.sc-head { display: flex; align-items: center; gap: 8px; }
.sc-name { font-size: 15px; font-weight: 700; color: var(--text-1); }
.sc-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-3);
}
.sc-note { margin: 8px 0 0; font-size: 12px; color: var(--text-2); }
</style>
